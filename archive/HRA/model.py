"""
HRAModel — Hierarchical Recurrent Attention.

Three-layer stack of GridCell RNN cells (memory.py) with descending driving
projections (top-down in the abstraction hierarchy = downsampling in spatial
resolution) and ascending feedback projections (transpose-conv upsampling).

Per MODEL_DESIGN.md §3:

    Layer | Grid resolution | Channels | Feedback inputs
    C_1   | 12×12 (full)    | C_1=32   | self, UP(C_2), UP²(C_3)
    C_2   | 6×6  (halved)   | C_2=64   | self, UP(C_3)
    C_3   | 3×3  (quartered)| C_3=128  | self only

Update rule (parallel-within-iteration): at recurrent iteration k,
each layer updates using the iteration-(k-1) hidden states of all layers.
This is equivalent to a discrete-time differential equation where all units
step simultaneously off the prior state, which keeps the recurrent dynamics
clean and easy to analyse.

Per MODEL_DESIGN.md §7 the forward pass exposes per-layer attention maps,
hidden-state trajectories, and feedback projections as named tensors. Every
analysis under HRA/analysis/ consumes these hooks directly — interpretability
is part of the architecture spec, not a bolted-on layer.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional, Tuple

import torch
import torch.nn as nn

try:
    from .decoder import FeatureDecoder, PixelDecoder
    from .losses import predictive_coding_loss
    from .memory import GridCellRNNCell
    from .readout import ActorHead, CriticHead, DecisionReadout, DistributionalQHead
    from .stem import V1Stem
except ImportError:  # pragma: no cover — supports `python model.py` from inside HRA/
    from decoder import FeatureDecoder, PixelDecoder  # type: ignore[no-redef]
    from losses import predictive_coding_loss  # type: ignore[no-redef]
    from memory import GridCellRNNCell  # type: ignore[no-redef]
    from readout import ActorHead, CriticHead, DecisionReadout, DistributionalQHead  # type: ignore[no-redef]
    from stem import V1Stem  # type: ignore[no-redef]


# --- Output containers --------------------------------------------------------


@dataclass
class StepOutput:
    """One env step's worth of model outputs, with all interpretability hooks."""

    action_logits: torch.Tensor                   # (B, n_actions)
    value: torch.Tensor                           # (B,)                 — GAE baseline V = Σ sg[π] · Q
    q_dist: torch.Tensor                          # (B, n_actions, N)    — distributional Q (None if scalar critic)
    q_values: torch.Tensor                        # (B, n_actions)       — mean-over-quantile Q (None if scalar critic)
    layer_states_new: Tuple[torch.Tensor, ...]    # ((B, C_1, 12, 12), (B, C_2, 6, 6), (B, C_3, 3, 3))
    pc_pred: torch.Tensor                         # (B, 3, 50, 50)       pixel-space prediction from C_1
    pc_loss: torch.Tensor                         # scalar               L_PC over the batch

    # Interpretability hooks (lists indexed by iteration k = 0..n_FR-1):
    attn_per_layer: List[List[torch.Tensor]] = field(default_factory=list)
    # attn_per_layer[k][ℓ] : (B, n_heads, N_ℓ, N_ℓ)

    state_per_layer: List[List[torch.Tensor]] = field(default_factory=list)
    # state_per_layer[k][ℓ] : (B, C_ℓ, H_ℓ, W_ℓ) — hidden state after iteration k

    feedback_projections: List[dict] = field(default_factory=list)
    # feedback_projections[k] : dict with keys like 'ascend_2to1' etc.


# --- The model ---------------------------------------------------------------


class HRAModel(nn.Module):
    """
    Hierarchical Recurrent Attention with multi-layer GridCell RNN.

    Args
    ----
    in_channels      : observation channels (default 3 for RGB)
    image_h, image_w : observation HW (default 50, 50)
    stem_mid_ch      : V1 stem intermediate channels (default 16)
    stem_out_ch      : V1 stem output channels (== C_V; default 32)
    state_channels   : tuple (C_1, C_2, C_3). Default (32, 64, 128).
    n_FR             : forward-reasoning iterations per env step (default 5)
    n_heads          : attention heads in every FT (default 4)
    decision_dim     : pooled decision-vector dim (default 64)
    actor_hidden     : actor MLP hidden (default 64)
    critic_hidden    : critic MLP hidden (default 64)
    n_actions        : discrete actions (default 2 — Posner)
    init_action_logit_bias : optional bias on policy logits at init.
                       Default None.  Pass [0.0, -4.0] for ChangeDetectionEnv.
    pc_coef          : weight of the auxiliary PC loss (default 1.0)
    critic_kind      : "distributional" (default, QR-DQN action-conditional Q
                       per Q_CRITIC.md) or "scalar" (plain V head; ablation).
    n_quantiles      : N for the distributional critic (default 51). Ignored
                       if critic_kind == "scalar".
    cross_layer_via  : "input" (default) routes cross-layer ascending feedback
                       via summation with the cell's input z_t (simpler, fewer
                       parameters, no FT-residual-sign instability observed in
                       the iter-499 post-mortem). "ft" routes ascending feedback
                       into each cell's FeedbackTransformer Q/K/V — the original
                       multi-source variant; theoretically richer, empirically
                       harder to stabilise on simple tasks. Within-layer self-
                       attention is unaffected (it's the interpretability
                       primitive).
    enable_skips     : bool (default True). Adds bottom-up skip connections
                       V→C₂, V→C₃, C₁→C₃, summed into the receiving cell's
                       driving input z_t. Cortically motivated (L4 thalamic
                       drive + L5 long-range projections); added after the
                       iter-1999 post-mortem showed C₂/C₃ freezing because
                       all their input had to flow through the conv-stride-2
                       chain from C₁.
    """

    GRID_HW = ((12, 12), (6, 6), (3, 3))  # spatial dims for layers 1, 2, 3

    def __init__(
        self,
        in_channels: int = 3,
        image_h: int = 50,
        image_w: int = 50,
        stem_mid_ch: int = 16,
        stem_out_ch: int = 32,
        state_channels: Tuple[int, int, int] = (32, 64, 128),
        n_FR: int = 5,
        n_heads: int = 4,
        decision_dim: int = 64,
        actor_hidden: int = 64,
        critic_hidden: int = 64,
        n_actions: int = 2,
        init_action_logit_bias=None,
        pc_coef: float = 1.0,
        critic_kind: str = "distributional",
        n_quantiles: int = 51,
        cross_layer_via: str = "input",
        enable_skips: bool = True,
    ) -> None:
        super().__init__()
        if cross_layer_via not in ("input", "ft"):
            raise ValueError(f"cross_layer_via must be 'input' or 'ft'; got {cross_layer_via!r}")
        self.in_channels = in_channels
        self.image_h, self.image_w = image_h, image_w
        self.state_channels = state_channels
        self.n_FR = n_FR
        self.pc_coef = pc_coef
        self.critic_kind = critic_kind
        self.n_quantiles = n_quantiles if critic_kind == "distributional" else 0
        self.cross_layer_via = cross_layer_via
        self.enable_skips = enable_skips
        c1, c2, c3 = state_channels
        (h1, w1), (h2, w2), (h3, w3) = self.GRID_HW

        # --- V1 stem ---
        self.stem = V1Stem(in_channels=in_channels, mid_channels=stem_mid_ch, out_channels=stem_out_ch)

        # --- Descending driving projections (input to deeper layer) ---
        # z_2 = conv-down(C_1_prev) : (B, c1, 12, 12) → (B, c2, 6, 6)
        self.descend_1to2 = self._descend(c1, c2)
        # z_3 = conv-down(C_2_prev) : (B, c2, 6, 6) → (B, c3, 3, 3)
        # 6 → 3 is stride 2 with kernel 3, padding 1 (rounding gives 3 cleanly).
        self.descend_2to3 = self._descend(c2, c3, in_h=6)

        # The stem→C_1 projection collapses if stem_out_ch == c1; else 1×1.
        if stem_out_ch != c1:
            self.stem_to_c1 = nn.Conv2d(stem_out_ch, c1, kernel_size=1)
        else:
            self.stem_to_c1 = nn.Identity()

        # --- Ascending feedback projections ---
        # All produce tensors at the *destination* layer's (state_C, grid_H, grid_W).
        self.ascend_2to1 = self._ascend(c2, c1, scale_factor=2)            # 6→12
        self.ascend_3to1 = self._ascend(c3, c1, scale_factor=4)            # 3→12
        self.ascend_3to2 = self._ascend(c3, c2, scale_factor=2)            # 3→6

        # --- Bottom-up skip connections (NEW, biologically motivated) ---
        # Cortical analog: L4-like direct thalamic→deep-cortex inputs +
        # L5-like long-range projections that bypass intermediate areas. Added
        # to address the iter-1999 post-mortem finding that C₂ and C₃ were
        # frozen because all their input had to flow through the
        # conv-stride-2 chain from a barely-responsive C₁.
        if enable_skips:
            # Stem V (B, stem_out_ch, 12, 12) → C₂ z (B, c₂, 6, 6).
            self.skip_stem_to_c2 = self._descend(stem_out_ch, c2)
            # Stem V (B, stem_out_ch, 12, 12) → C₃ z (B, c₃, 3, 3) via two strides.
            self.skip_stem_to_c3 = nn.Sequential(
                self._descend(stem_out_ch, c2),
                self._descend(c2, c3, in_h=6),
            )
            # C₁ (B, c₁, 12, 12) → C₃ z (B, c₃, 3, 3) via two strides.
            self.skip_c1_to_c3 = nn.Sequential(
                self._descend(c1, c2),
                self._descend(c2, c3, in_h=6),
            )
        else:
            self.skip_stem_to_c2 = None
            self.skip_stem_to_c3 = None
            self.skip_c1_to_c3 = None

        # --- GridCell RNN cells ---
        # n_feedback counts the EXTERNAL feedback sources at each layer that
        # are routed into the FeedbackTransformer's Q/K/V (in addition to the
        # always-present self-recurrent feedback). In cross_layer_via='input'
        # mode, ascending feedback is summed into z_t at the cell's input
        # instead of routed via the FT, so n_feedback drops to 0 for every
        # cell and the cells' FTs do *within-layer* self-attention only.
        if cross_layer_via == "ft":
            n_fb = (2, 1, 0)  # cell 1 gets ascend_2to1 + ascend_3to1; cell 2 gets ascend_3to2
        else:  # "input"
            n_fb = (0, 0, 0)
        self.cell1 = GridCellRNNCell(
            in_channels=c1, state_channels=c1, grid_h=h1, grid_w=w1,
            n_heads=n_heads, n_feedback=n_fb[0],
        )
        self.cell2 = GridCellRNNCell(
            in_channels=c2, state_channels=c2, grid_h=h2, grid_w=w2,
            n_heads=n_heads, n_feedback=n_fb[1],
        )
        self.cell3 = GridCellRNNCell(
            in_channels=c3, state_channels=c3, grid_h=h3, grid_w=w3,
            n_heads=n_heads, n_feedback=n_fb[2],
        )

        # --- Decoders (for PC loss + per-layer interpretability) ---
        self.pixel_decoder_c1 = PixelDecoder(c1, h1, w1, image_h, image_w)
        # Per-layer decoders for interpretability (not used by primary PC loss).
        self.pixel_decoder_c2 = PixelDecoder(c2, h2, w2, image_h, image_w)
        self.pixel_decoder_c3 = PixelDecoder(c3, h3, w3, image_h, image_w)

        # --- Readout / heads ---
        # The new DecisionReadout consumes the full spatial state of every
        # layer via per-layer LayerHead (conv reduction → linear), then
        # concatenates and mixes. Both actor and critic read this output.
        layer_specs = [(c, h, w) for c, (h, w) in zip(state_channels, self.GRID_HW)]
        self.readout = DecisionReadout(layer_specs, decision_dim=decision_dim)
        self.actor = ActorHead(
            decision_dim, hidden_dim=actor_hidden, n_actions=n_actions,
            init_logit_bias=init_action_logit_bias,
        )
        if critic_kind == "distributional":
            self.critic = DistributionalQHead(
                decision_dim, hidden_dim=critic_hidden,
                n_actions=n_actions, n_quantiles=n_quantiles,
            )
        elif critic_kind == "scalar":
            self.critic = CriticHead(decision_dim, hidden_dim=critic_hidden)
        else:
            raise ValueError(
                f"critic_kind must be 'distributional' or 'scalar'; got {critic_kind!r}"
            )

    # --- Building blocks for projections ----------------------------------

    @staticmethod
    def _descend(in_ch: int, out_ch: int, in_h: Optional[int] = None) -> nn.Sequential:
        """
        Spatially-reducing, channel-expanding conv block.
        Stride-2 conv with kernel 3 + GroupNorm + GELU.
        """
        from .stem import _GN_GROUPS  # reuse stem's group-count convention

        # Pick a group count that divides out_ch.
        gn = _GN_GROUPS
        while out_ch % gn != 0 and gn > 1:
            gn //= 2

        # When in_h=6 we want 6→3 which works with stride=2, kernel=3, padding=1
        # (floor((6+2-3)/2)+1 = 3). When in_h=12 we want 12→6 which works the same.
        return nn.Sequential(
            nn.Conv2d(in_ch, out_ch, kernel_size=3, stride=2, padding=1),
            nn.GroupNorm(gn, out_ch),
            nn.GELU(),
        )

    @staticmethod
    def _ascend(in_ch: int, out_ch: int, scale_factor: int) -> nn.Sequential:
        """
        Spatially-expanding, channel-contracting projection.
        Bilinear upsample + conv + GroupNorm + GELU. Avoids the checkerboard
        artifacts that pure ConvTranspose2d can produce.
        """
        from .stem import _GN_GROUPS

        gn = _GN_GROUPS
        while out_ch % gn != 0 and gn > 1:
            gn //= 2

        return nn.Sequential(
            nn.Upsample(scale_factor=scale_factor, mode="bilinear", align_corners=False),
            nn.Conv2d(in_ch, out_ch, kernel_size=3, padding=1),
            nn.GroupNorm(gn, out_ch),
            nn.GELU(),
        )

    # --- State initialisation ---------------------------------------------

    def init_states(self, batch_size: int, device=None, dtype=torch.float32) -> Tuple[torch.Tensor, ...]:
        """Zero-initialised hidden states for all three layers."""
        device = device or next(self.parameters()).device
        states = []
        for (h, w), c in zip(self.GRID_HW, self.state_channels):
            states.append(torch.zeros(batch_size, c, h, w, device=device, dtype=dtype))
        return tuple(states)

    # --- Forward ----------------------------------------------------------

    def forward_step(
        self,
        x_t: torch.Tensor,
        prev_states: Tuple[torch.Tensor, ...],
    ) -> StepOutput:
        """
        One env step.

        x_t         : (B, 3, 50, 50) observation
        prev_states : (C_1, C_2, C_3) hidden states from the previous env step.
                      Use init_states() for the first step of an episode.
        """
        B = x_t.shape[0]

        # Bottom-up V1 features. Static across all n_FR iterations within one
        # env step (the observation doesn't change inside a step).
        V = self.stem(x_t)
        V_for_c1 = self.stem_to_c1(V)  # match channel count if needed

        # Initialise iteration-0 states from prev env step's terminal states.
        C1, C2, C3 = prev_states

        attn_per_layer: List[List[torch.Tensor]] = []
        state_per_layer: List[List[torch.Tensor]] = []
        feedback_projections: List[dict] = []

        for k in range(self.n_FR):
            # Compute the driving + feedback inputs from the PRIOR iteration's
            # states. This is the parallel-within-iteration update rule.

            # Descending driving inputs (top-down in hierarchy = down in resolution).
            z1 = V_for_c1                    # (B, c1, 12, 12)  — driven by sensory
            z2 = self.descend_1to2(C1)       # (B, c2, 6, 6)
            z3 = self.descend_2to3(C2)       # (B, c3, 3, 3)

            # Bottom-up skip connections (NEW). Cortically motivated:
            #   V → C₂   = L4-like direct thalamic drive to V4 area
            #   V → C₃   = direct projection skipping intermediate areas
            #   C₁ → C₃  = L5-like long-range projection
            # Each skip sums into the destination's driving input z_t so the
            # deeper layers cannot freeze just because C₁'s signal is weak.
            if self.enable_skips:
                z2 = z2 + self.skip_stem_to_c2(V)
                z3 = z3 + self.skip_stem_to_c3(V) + self.skip_c1_to_c3(C1)

            # Ascending feedback (bottom-up in hierarchy = up in resolution).
            fb_2to1 = self.ascend_2to1(C2)   # (B, c1, 12, 12)
            fb_3to1 = self.ascend_3to1(C3)   # (B, c1, 12, 12)
            fb_3to2 = self.ascend_3to2(C3)   # (B, c2, 6, 6)
            feedback_projections.append({
                "ascend_2to1": fb_2to1, "ascend_3to1": fb_3to1, "ascend_3to2": fb_3to2,
                "descend_1to2": z2, "descend_2to3": z3,
            })

            # Route ascending feedback per cross_layer_via mode.
            if self.cross_layer_via == "ft":
                # Original variant: ascending feedback goes into the FT's
                # external-feedback Q/K/V projections (multi-source attention).
                out1 = self.cell1(z1, C1, feedback_list=[fb_2to1, fb_3to1])
                out2 = self.cell2(z2, C2, feedback_list=[fb_3to2])
                out3 = self.cell3(z3, C3, feedback_list=None)
            else:
                # Simpler "input" variant: ascending feedback is summed into
                # the cell's bottom-up input z_t. The FT inside each cell does
                # within-layer self-attention only (over its own grid + own
                # previous state).
                z1_combined = z1 + fb_2to1 + fb_3to1
                z2_combined = z2 + fb_3to2
                out1 = self.cell1(z1_combined, C1, feedback_list=None)
                out2 = self.cell2(z2_combined, C2, feedback_list=None)
                out3 = self.cell3(z3, C3, feedback_list=None)

            C1, C2, C3 = out1["C_new"], out2["C_new"], out3["C_new"]

            attn_per_layer.append([out1["attn"], out2["attn"], out3["attn"]])
            state_per_layer.append([C1, C2, C3])

        # --- Heads ---
        h_decision = self.readout([C1, C2, C3])
        action_logits = self.actor(h_decision)

        if self.critic_kind == "distributional":
            q_out = self.critic(h_decision, action_logits)
            q_dist = q_out["q_dist"]        # (B, |A|, N)
            q_values = q_out["q_values"]    # (B, |A|)
            value = q_out["value"]          # (B,)  V = Σ sg[π] · Q
        else:
            # Scalar critic ablation — q_dist/q_values are placeholders so the
            # StepOutput contract is uniform across critic kinds.
            value = self.critic(h_decision)  # (B,)
            B = action_logits.shape[0]
            n_a = action_logits.shape[-1]
            zero = torch.zeros(B, n_a, 1, device=value.device, dtype=value.dtype)
            q_dist = zero          # (B, n_a, 1) sentinel
            q_values = zero.squeeze(-1)  # (B, n_a) sentinel

        # --- PC loss ---
        pc_pred = self.pixel_decoder_c1(C1)
        pc_loss = predictive_coding_loss(x_t, pc_pred)

        return StepOutput(
            action_logits=action_logits,
            value=value,
            q_dist=q_dist,
            q_values=q_values,
            layer_states_new=(C1, C2, C3),
            pc_pred=pc_pred,
            pc_loss=pc_loss * self.pc_coef,
            attn_per_layer=attn_per_layer,
            state_per_layer=state_per_layer,
            feedback_projections=feedback_projections,
        )

    # Default forward = forward_step (single env step). Multi-step episode roll
    # is handled by the training loop in ppo.py (to be ported in Stage 3).
    def forward(self, x_t, prev_states=None):
        if prev_states is None:
            prev_states = self.init_states(x_t.shape[0], device=x_t.device, dtype=x_t.dtype)
        return self.forward_step(x_t, prev_states)
