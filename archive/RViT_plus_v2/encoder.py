"""
RViTPlusEncoder — three-layer GridCell-RNN stack with cross-layer feedback,
retinotectal-analog skips, and per-cell microstim plumbing.

Architecture (per `../RVIT_PLUS_DESIGN.md` §3.1, revised 2026-05-20):

    Layer | Pairing | Grid       | Channels | n_external_feedback
    -----------------------------------------------------------
    C₁    | V1      | 12 × 12    |     64   |  2 (C₂, C₃)
    C₂    | V4      |  6 ×  6    |     96   |  1 (C₃)
    C₃    | IT      |  3 ×  3    |    128   |  0

Proper hierarchical capacity trade-off per the architectural-program spec
(`threads/the_user_architectural_program.md` §3): each layer **decreases
spatial resolution and increases channel capacity**, matching the V1→V4→IT
progression. Total memory footprint per cell: 9216 / 3456 / 1152 features
— a real hierarchy in which the deeper layers are forced to abstract
rather than store position-by-position copies of the input.

(Run-6 had departed from this with C₁/C₂ both at 12×12, citing an HRA
empirical finding that aggressive stride-2 froze deeper layers. That
finding was specific to HRA's optimization setup — sparse-reward PPO
without skip connections. With the retinotectal-analog V→C₂, V→C₃ skips
in place and the spatial-latent + content-weighted loss in train.py, the
proper hierarchical reduction is what the program calls for.)

Cell input flow per iteration k:
    z₁ = V  (stem output, 64ch @ 12×12 — same channel count as C₁)
    z₂ = descend_1to2(C₁_{k-1}) + skip_scale · skip_V_to_C2(V)
    z₃ = descend_2to3(C₂_{k-1}) + skip_scale · skip_V_to_C3(V)
where descend_1to2 is stride-2 (12→6), descend_2to3 is stride-2 (6→3),
skip_V_to_C2 is stride-2 (12→6), skip_V_to_C3 is two stride-2's (12→3).

Cross-layer feedback (into each cell's FeedbackTransformer):
    cell₁.FT receives [self, ascend_2to1(C₂), ascend_3to1(C₃)]
    cell₂.FT receives [self, ascend_3to2(C₃)]
    cell₃.FT receives [self]
"""
from __future__ import annotations

from typing import Dict, List, Optional, Sequence, Tuple

import torch
import torch.nn as nn
import torch.nn.functional as F

from .memory import GridCellRNN_LSTM


def _gn_groups(channels: int) -> int:
    for g in (8, 4, 2, 1):
        if channels % g == 0:
            return g
    return 1


def _channel_adapter(in_ch: int, out_ch: int) -> nn.Sequential:
    """1×1 conv + GN + GELU; channel change, no spatial reshape."""
    return nn.Sequential(
        nn.Conv2d(in_ch, out_ch, kernel_size=1),
        nn.GroupNorm(_gn_groups(out_ch), out_ch),
        nn.GELU(),
    )


def _descend(in_ch: int, out_ch: int) -> nn.Sequential:
    """Stride-2 conv block: spatial reduction × 2 + channel expansion."""
    return nn.Sequential(
        nn.Conv2d(in_ch, out_ch, kernel_size=3, stride=2, padding=1),
        nn.GroupNorm(_gn_groups(out_ch), out_ch),
        nn.GELU(),
    )


def _ascend(in_ch: int, out_ch: int, scale_factor: int) -> nn.Sequential:
    """Bilinear upsample + 1×1 conv: spatial expansion + channel adapt.
    Bilinear avoids checkerboard artifacts; cheaper than transpose-conv."""
    return nn.Sequential(
        nn.Upsample(scale_factor=scale_factor, mode="bilinear", align_corners=False),
        nn.Conv2d(in_ch, out_ch, kernel_size=1),
        nn.GroupNorm(_gn_groups(out_ch), out_ch),
        nn.GELU(),
    )


class RViTPlusEncoder(nn.Module):
    """Three-layer GridCell-RNN encoder with n_FR inner iterations per env step.

    Args
    ----
    stem_out_channels : channels of the V1-stem output (default 64)
    state_channels    : (c1, c2, c3) per-layer channel counts. Default (64,96,128).
    n_FR              : forward-reasoning inner iterations per env step (default 4).
    n_heads           : attention heads in every FeedbackTransformer (default 4).
    enable_skips      : whether V→C₂, V→C₃ retinotectal-analog skips fire (default True).
    skip_scale        : scalar multiplier on skip contributions (default 0.3) — HRA
                        random-init probe found unscaled skips over-drive C₂.

    Forward (see __call__)
    ----------------------
    V          : (B, stem_out_channels, 12, 12) — stem output, constant across n_FR iters
    prev_states: tuple (C₁, C₂, C₃) from previous env step (or init_states())
    attn_biases: optional dict mapping (layer_idx, iter_idx) → bias tensor
                 for microstim experiments. layer_idx ∈ {0,1,2}, iter_idx ∈ {0..n_FR-1}.
                 None entries become 0 bias.

    Returns dict:
        layer_states_new : tuple (C₁, C₂, C₃) after n_FR iterations
        attn_per_iter    : list of [attn₁, attn₂, attn₃] per iteration (B, n_heads, N_ℓ, N_ℓ)
        state_per_iter   : list of [C₁_k, C₂_k, C₃_k] per iteration (full tensors)
        feedback_per_iter: list of dicts with named cross-layer projections per iter
    """

    GRID_HW = ((12, 12), (6, 6), (3, 3))

    # The supported task-specific specializations of the deepest layer. When
    # split_c3=True, the encoder maintains one C₃ cell per heading in this
    # tuple.
    C3_HEADS = ("ae", "actor", "critic")

    def __init__(
        self,
        stem_out_channels: int = 64,
        state_channels: Tuple[int, int, int] = (64, 96, 128),
        n_FR: int = 4,
        n_heads: int = 4,
        enable_skips: bool = True,
        skip_scale: float = 0.3,
        split_c3: bool = False,
    ) -> None:
        super().__init__()
        c1, c2, c3 = state_channels
        (h1, w1), (h2, w2), (h3, w3) = self.GRID_HW

        self.state_channels = state_channels
        self.n_FR = int(n_FR)
        self.n_heads = int(n_heads)
        self.enable_skips = bool(enable_skips)
        self.skip_scale = float(skip_scale)
        self.stem_out_channels = stem_out_channels
        self.split_c3 = bool(split_c3)

        # Stem→C₁ channel adapter. Identity if stem_out_channels == c1.
        if stem_out_channels == c1:
            self.stem_to_c1 = nn.Identity()
        else:
            self.stem_to_c1 = _channel_adapter(stem_out_channels, c1)

        # Descending driving projections — proper hierarchical reduction.
        # 12×12, c1 → 6×6, c2: stride-2 + channel expand.
        self.descend_1to2 = _descend(c1, c2)
        # 6×6, c2 → 3×3, c3: stride-2 + channel expand.
        self.descend_2to3 = _descend(c2, c3)

        # Retinotectal-analog skips (V → C₂, V → C₃). V is at (12,12) c=stem_out;
        # need to project to C₂'s (6,6) and C₃'s (3,3).
        if enable_skips:
            self.skip_V_to_C2 = _descend(stem_out_channels, c2)  # 12→6
            # 12→3 via two stride-2 descends.
            self.skip_V_to_C3 = nn.Sequential(
                _descend(stem_out_channels, c2),  # 12→6, stem_out→c2
                _descend(c2, c3),                  # 6→3, c2→c3
            )
        else:
            self.skip_V_to_C2 = None
            self.skip_V_to_C3 = None

        # Ascending feedback projections (deeper-layer states → shallower-layer FT).
        # C₂ (6×6) → C₁ (12×12): ×2 up. C₃ (3×3) → C₁ (12×12): ×4 up. C₃ → C₂: ×2 up.
        self.ascend_2to1 = _ascend(c2, c1, scale_factor=2)
        self.ascend_3to1 = _ascend(c3, c1, scale_factor=4)
        self.ascend_3to2 = _ascend(c3, c2, scale_factor=2)

        # GridCell-RNN cells.
        # in_channels = state_channels for each cell (the descend/skip blocks
        # output in the destination cell's channel count).
        self.cell1 = GridCellRNN_LSTM(
            in_channels=c1, state_channels=c1, grid_h=h1, grid_w=w1,
            n_heads=n_heads, n_feedback=2,  # ascend_2to1, ascend_3to1
        )
        self.cell2 = GridCellRNN_LSTM(
            in_channels=c2, state_channels=c2, grid_h=h2, grid_w=w2,
            n_heads=n_heads, n_feedback=1,  # ascend_3to2
        )
        # The "canonical" C₃ cell — used as the autoencoder's deep state when
        # split_c3=True, and as the shared C₃ when split_c3=False. Kept under
        # the legacy name `cell3` so existing checkpoints load cleanly.
        self.cell3 = GridCellRNN_LSTM(
            in_channels=c3, state_channels=c3, grid_h=h3, grid_w=w3,
            n_heads=n_heads, n_feedback=0,
        )

        # When split_c3=True: two ADDITIONAL deep cells, one per RL head
        # (actor and critic). They read the same z₃ = descend_2to3(C₂) + skip
        # that `cell3` reads, but are SILENT SPECIALISTS: they do not feed
        # back into C₁ or C₂ via the ascend pathways. Only `cell3` (the
        # autoencoder's deep state) participates in the encoder's upward
        # feedback dynamics. This keeps C₁/C₂'s shared perceptual pyramid
        # unchanged while letting each task-specific head specialize in its
        # own abstract representation, reducing competition for channels in
        # the smallest, most-compressed level of the hierarchy.
        if self.split_c3:
            self.cell3_actor = GridCellRNN_LSTM(
                in_channels=c3, state_channels=c3, grid_h=h3, grid_w=w3,
                n_heads=n_heads, n_feedback=0,
            )
            self.cell3_critic = GridCellRNN_LSTM(
                in_channels=c3, state_channels=c3, grid_h=h3, grid_w=w3,
                n_heads=n_heads, n_feedback=0,
            )

    def init_states(
        self, batch_size: int, device=None, dtype=torch.float32
    ) -> Tuple[torch.Tensor, ...]:
        """Zero-initialised hidden states for the three layers.

        Returns a 3-tuple `(C₁, C₂, C₃)` when split_c3=False. When split_c3=True,
        the returned C₃ is the autoencoder's variant; use `init_c3_specialists`
        for the actor/critic variants.
        """
        device = device or next(self.parameters()).device
        states = []
        for (h, w), c in zip(self.GRID_HW, self.state_channels):
            states.append(torch.zeros(batch_size, c, h, w, device=device, dtype=dtype))
        return tuple(states)

    def init_c3_specialists(
        self, batch_size: int, device=None, dtype=torch.float32
    ) -> Dict[str, torch.Tensor]:
        """Zero-init the task-specific C₃ specialists (actor + critic) when
        split_c3=True. Returns an empty dict when split_c3=False.
        """
        if not self.split_c3:
            return {}
        device = device or next(self.parameters()).device
        c3 = self.state_channels[2]
        h3, w3 = self.GRID_HW[2]
        return {
            "actor":  torch.zeros(batch_size, c3, h3, w3, device=device, dtype=dtype),
            "critic": torch.zeros(batch_size, c3, h3, w3, device=device, dtype=dtype),
        }

    def forward_step(
        self,
        V: torch.Tensor,
        prev_states: Tuple[torch.Tensor, torch.Tensor, torch.Tensor],
        attn_biases: Optional[dict] = None,
        prev_c3_specialists: Optional[Dict[str, torch.Tensor]] = None,
    ) -> dict:
        """One env-step's worth of recurrent updates (n_FR inner iterations).

        Args
        ----
        V : (B, stem_out, 12, 12) stem features for this frame.
        prev_states : (C₁, C₂, C₃) from the previous timestep. When split_c3=True,
                      `C₃` is the autoencoder variant (cell3.ae).
        prev_c3_specialists : when split_c3=True, dict {"actor": C₃_actor,
                              "critic": C₃_critic} from previous timestep. Pass
                              `init_c3_specialists(B)` on the first frame.

        Returns dict with:
            layer_states_new   : (C₁, C₂, C₃_ae)
            c3_specialists_new : when split_c3=True, dict of the updated
                                 specialist C₃ states. Empty dict otherwise.
            attn_per_iter      : list of [attn₁, attn₂, attn₃_ae] per iter
            attn_specialists_per_iter : list of dicts {"actor": attn3_actor,
                                        "critic": attn3_critic} per iter
                                        (empty when split_c3=False)
            state_per_iter, feedback_per_iter — diagnostics.
        """
        C1, C2, C3 = prev_states
        V_for_c1 = self.stem_to_c1(V)

        if self.split_c3:
            if prev_c3_specialists is None:
                prev_c3_specialists = self.init_c3_specialists(
                    batch_size=V.shape[0], device=V.device, dtype=V.dtype
                )
            C3_actor = prev_c3_specialists["actor"]
            C3_critic = prev_c3_specialists["critic"]
        else:
            C3_actor = C3_critic = None  # unused

        # ── Single bottom-up pass per timestep (no inner FR loop). ──
        # Connectivity is strictly sequential:
        #     z1 ── cell1 ── C1_new ──┐
        #     (V skip) ────────────▶ cell2 ── C2_new ──┐
        #     (V skip) ──────────────────────────────▶ cell3 ── C3_new
        # Each layer's driving input is the NEW state of the layer below
        # (descended to its grid size), plus a skip from the initial visual
        # representation V (resized via skip_V_to_C2 / skip_V_to_C3).
        #
        # Top-down feedback uses the PREVIOUS timestep's deep states
        # (C2, C3 as passed in via prev_states) — bottom-up at this timestep,
        # top-down at one-timestep lag.

        # Ascending feedback from PREVIOUS timestep's states.
        fb_2to1 = self.ascend_2to1(C2)
        fb_3to1 = self.ascend_3to1(C3)
        fb_3to2 = self.ascend_3to2(C3)

        def _bias(layer_idx):
            if attn_biases is None:
                return None
            # Accept either (layer,) or (layer, 0) keys for back-compat.
            return attn_biases.get(layer_idx, attn_biases.get((layer_idx, 0), None))

        # ── Layer 1: driven by the initial visual representation. ──
        z1 = V_for_c1
        out1 = self.cell1(z1, C1, feedback_list=[fb_2to1, fb_3to1],
                          attn_bias=_bias(0))
        C1_new = out1["C_new"]

        # ── Layer 2: driven by C1_new (descended) + V skip. ──
        z2 = self.descend_1to2(C1_new)
        if self.enable_skips:
            z2 = z2 + self.skip_scale * self.skip_V_to_C2(V)
        out2 = self.cell2(z2, C2, feedback_list=[fb_3to2],
                          attn_bias=_bias(1))
        C2_new = out2["C_new"]

        # ── Layer 3: driven by C2_new (descended) + V skip. ──
        z3 = self.descend_2to3(C2_new)
        if self.enable_skips:
            z3 = z3 + self.skip_scale * self.skip_V_to_C3(V)
        out3 = self.cell3(z3, C3, feedback_list=None,
                          attn_bias=_bias(2))
        C3_new = out3["C_new"]

        # Specialist C₃ cells (split_c3): same z3 driving input, own recurrent
        # state and FT, no external feedback into C₁ / C₂.
        spec_attn: Dict[str, torch.Tensor] = {}
        if self.split_c3:
            out3_actor = self.cell3_actor(z3, C3_actor, feedback_list=None)
            out3_critic = self.cell3_critic(z3, C3_critic, feedback_list=None)
            C3_actor = out3_actor["C_new"]
            C3_critic = out3_critic["C_new"]
            spec_attn = {
                "actor": out3_actor["attn"],
                "critic": out3_critic["attn"],
                "actor_spatial": out3_actor["attn_spatial"],
                "critic_spatial": out3_critic["attn_spatial"],
            }

        C1, C2, C3 = C1_new, C2_new, C3_new

        # Diagnostics are wrapped in length-1 lists so downstream code that
        # previously iterated over inner-iter outputs still works unchanged.
        attn_per_iter              = [[out1["attn"], out2["attn"], out3["attn"]]]
        # Spatial attention residuals (per-layer (B, C_ℓ, H_ℓ, W_ℓ)). These are
        # the "look-here" maps — the actual tensors added to the residual in
        # each layer's attention block. Empirically these are the most
        # attention-map-like signal in the architecture.
        attn_spatial_per_iter      = [[out1["attn_spatial"], out2["attn_spatial"], out3["attn_spatial"]]]
        # Z↔H gating maps per layer (B, C_ℓ, H_ℓ, W_ℓ) for {Q, K, V}.
        gates_per_iter             = [{
            "q": [out1["q_gate"], out2["q_gate"], out3["q_gate"]],
            "k": [out1["k_gate"], out2["k_gate"], out3["k_gate"]],
            "v": [out1["v_gate"], out2["v_gate"], out3["v_gate"]],
        }]
        attn_specialists_per_iter  = [spec_attn]
        state_per_iter             = [[C1, C2, C3]]
        feedback_per_iter          = [{
            "descend_1to2": z2,
            "descend_2to3": z3,
            "ascend_2to1": fb_2to1,
            "ascend_3to1": fb_3to1,
            "ascend_3to2": fb_3to2,
        }]

        if self.split_c3:
            c3_specialists_new: Dict[str, torch.Tensor] = {
                "actor": C3_actor, "critic": C3_critic,
            }
        else:
            c3_specialists_new = {}

        return {
            "layer_states_new": (C1, C2, C3),
            "c3_specialists_new": c3_specialists_new,
            "attn_per_iter": attn_per_iter,
            "attn_spatial_per_iter": attn_spatial_per_iter,
            "gates_per_iter": gates_per_iter,
            "attn_specialists_per_iter": attn_specialists_per_iter,
            "state_per_iter": state_per_iter,
            "feedback_per_iter": feedback_per_iter,
        }
