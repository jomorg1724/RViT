"""
PrismV2Model — wires the v2 components into a single nn.Module.

Spec: end-to-end of §2 + §3 + §4 + §5 of ../Prism/docs/PRISM_V2_PROPOSAL.md.

Per-step computation (forward_step):

    x_t  ─►  V1Stem  ─►  V_1^t                                (B, C_V1, 12, 12)
                          │
                          ▼
                   V2Stem  ─►  V_2^t                          (B, C_V2, 6, 6)

    M_fast_{t-1}, M_slow_{t-1}                                (carried recurrent state)

    HierarchicalFiLM(M_fast, M_slow)  modulates V_1 → P_1     (B, C_V1, 12, 12)

    PixelDecoder(M_fast_{t-1})  →  x̂_t                       (B, 3, 50, 50)
        S_V1_pix from pixel error
    MultiHeadFeatureDecoder_V1(M_fast_{t-1})  →  V̂_1 per head
        E_V1, S_V1 from feature error (per-head)
    MultiHeadFeatureDecoder_V2(M_slow_{t-1})  →  V̂_2 per head
        E_V2, S_V2 from feature error (per-head)

    L_PC = α_pix · ‖x − x̂_fwd‖² + α_auto · ‖x − x̂(M_fast_t)‖²
         + α_V1_feat · L_V1_feat
         + α_V2_feat · L_V2_feat + α_V2_auto · L_V2_feat_auto

    M_fast_t = FastConvGRU(M_fast_{t-1}, P_1, E_V1, S_V1)
    M_slow_t = SlowConvGRU(M_slow_{t-1}, V_2, E_V2, S_V2,
                           E_V1_pooled = pool(E_V1, target=6))

    M_fast_t = InnerWMLoop_fast(M_fast_t, V_1, decoder_V1)    K_fast iterations
    M_slow_t = InnerWMLoop_slow(M_slow_t, V_2, decoder_V2)    K_slow iterations

    s_t = HierarchicalDecisionReadout(M_fast_t, S_V1, M_slow_t, S_V2)
    π(a|s) = softmax(ActorHead(s_t))
    V(s)   = CriticHead(s_t)

Two callable interfaces (mirroring PRISM v1):
    forward_step(x_t, M_fast_prev, M_slow_prev) -> StepOutput
    forward_episode(x_seq, M_fast_init=None, M_slow_init=None) -> EpisodeOutput
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional, Tuple

import torch
import torch.nn as nn
import torch.nn.functional as F

try:
    from .decoder import (
        MultiHeadFeatureDecoder, PixelDecoder, multi_head_saliency, pixel_saliency_map,
    )
    from .film import HierarchicalFiLM
    from .losses import multi_head_pc_loss, predictive_coding_loss
    from .memory import CrossLevelErrorPool, FastConvGRU, InnerWMLoop, SlowConvGRU
    from .readout import ActorHead, CriticHead, HeadCompressionBackbone, HierarchicalDecisionReadout
    from .stem import V1Stem, V2Stem
except ImportError:
    from decoder import MultiHeadFeatureDecoder, PixelDecoder, multi_head_saliency, pixel_saliency_map  # type: ignore[no-redef]
    from film import HierarchicalFiLM  # type: ignore[no-redef]
    from losses import multi_head_pc_loss, predictive_coding_loss  # type: ignore[no-redef]
    from memory import CrossLevelErrorPool, FastConvGRU, InnerWMLoop, SlowConvGRU  # type: ignore[no-redef]
    from readout import ActorHead, CriticHead, HeadCompressionBackbone, HierarchicalDecisionReadout  # type: ignore[no-redef]
    from stem import V1Stem, V2Stem  # type: ignore[no-redef]


# --- Output containers --------------------------------------------------------


@dataclass
class StepOutput:
    """One env step's outputs from PrismV2Model.

    Critic outputs (action-conditional, distributional Q):
      q_dist     : full distributional Q,  shape (B, n_actions, N_quantiles)
      q_values   : mean-over-quantiles Q,  shape (B, n_actions)
      value      : V(s) = Σ_a sg[π(a|s)] · Q(s,a),  shape (B,)
                   — used as the GAE bootstrap. The stop-gradient on π
                   keeps the value loss from propagating into the actor.

    See readout.CriticHead and the design discussion in
    docs/PRISM_V2/Q_CRITIC.md for the gradient-routing rationale.
    """
    action_logits: torch.Tensor      # (B, n_actions)
    value: torch.Tensor              # (B,)                  V(s)  — scalar GAE bootstrap
    q_values: torch.Tensor           # (B, n_actions)        Q(s, a) (mean over quantiles)
    q_dist: torch.Tensor             # (B, n_actions, N)     distributional Q (for QR loss)
    M_fast_next: torch.Tensor        # (B, C_M^fast, 12, 12)
    M_slow_next: torch.Tensor        # (B, C_M^slow, 6, 6)
    S_V1_per_head: torch.Tensor      # (B, K_fast, 12, 12)
    S_V2_per_head: torch.Tensor      # (B, K_slow, 6, 6)
    S_V1_pix: torch.Tensor           # (B, 1, 12, 12)  — pixel-derived, kept for analyses
    pc_loss: torch.Tensor            # scalar
    aux: dict = field(default_factory=dict)


@dataclass
class EpisodeOutput:
    action_logits: torch.Tensor      # (B, T, n_actions)
    values: torch.Tensor             # (B, T)                V(s_t) sequence
    q_values_seq: torch.Tensor       # (B, T, n_actions)     Q(s_t, ·) sequence
    q_dist_seq: torch.Tensor         # (B, T, n_actions, N)  distributional Q sequence
    M_fast_seq: torch.Tensor         # (B, T+1, C_M^fast, 12, 12)
    M_slow_seq: torch.Tensor         # (B, T+1, C_M^slow, 6, 6)
    S_V1_per_head_seq: torch.Tensor  # (B, T, K_fast, 12, 12)
    S_V2_per_head_seq: torch.Tensor  # (B, T, K_slow, 6, 6)
    S_V1_pix_seq: torch.Tensor       # (B, T, 1, 12, 12)
    pc_loss_seq: torch.Tensor        # (T,)


# --- The model ---------------------------------------------------------------


class PrismV2Model(nn.Module):
    """
    PRISM v2.4: hierarchical predictive coding + slow/fast memory + multi-head
    saliency + cross-level Rao-Ballard coupling.
    """

    # Spatial dims set by the V1/V2 stems for the default 50-px input.
    SPATIAL_FAST_H: int = 12
    SPATIAL_FAST_W: int = 12
    SPATIAL_SLOW_H: int = 6
    SPATIAL_SLOW_W: int = 6

    def __init__(
        self,
        in_channels: int = 3,
        image_h: int = 50,
        image_w: int = 50,
        # Channels
        feature_channels_V1: int = 64,
        feature_channels_V2: int = 128,
        memory_channels_fast: int = 32,
        memory_channels_slow: int = 64,
        # Multi-head saliency
        n_heads_fast: int = 4,
        n_heads_slow: int = 4,
        # Inner WM loops
        inner_K_fast: int = 2,
        inner_K_slow: int = 4,
        inner_eps: float = 0.1,
        # Memory gate biases
        update_gate_bias_fast: float = -1.0,
        update_gate_bias_slow: float = -3.0,
        # Decision readout + heads
        decision_channels: int = 8,
        decision_coarse_grid_fast: int = 2,
        head_compression_hidden: int = 32,
        head_compression_output: int = 256,
        actor_hidden: int = 128,
        critic_hidden: int = 128,
        n_quantiles: int = 51,
        n_actions: int = 2,
        init_action_logit_bias: list[float] | None = None,
        # PC loss coefficients
        pc_pixel_coef: float = 1.0,
        pc_pixel_autoenc_coef: float = 1.0,
        pc_pixel_grid_coef: float = 0.1,
        pc_pixel_grid_autoenc_coef: float = 0.1,
        pc_V1_feat_coef: float = 0.1,
        pc_V2_feat_coef: float = 0.5,
        pc_V2_feat_autoenc_coef: float = 0.5,
    ) -> None:
        super().__init__()

        # Stash hyperparameters.
        self.in_channels = in_channels
        self.feature_channels_V1 = feature_channels_V1
        self.feature_channels_V2 = feature_channels_V2
        self.memory_channels_fast = memory_channels_fast
        self.memory_channels_slow = memory_channels_slow
        self.n_heads_fast = n_heads_fast
        self.n_heads_slow = n_heads_slow
        self.image_h = image_h
        self.image_w = image_w

        self.pc_pixel_coef = float(pc_pixel_coef)
        self.pc_pixel_autoenc_coef = float(pc_pixel_autoenc_coef)
        self.pc_pixel_grid_coef = float(pc_pixel_grid_coef)
        self.pc_pixel_grid_autoenc_coef = float(pc_pixel_grid_autoenc_coef)
        self.pc_V1_feat_coef = float(pc_V1_feat_coef)
        self.pc_V2_feat_coef = float(pc_V2_feat_coef)
        self.pc_V2_feat_autoenc_coef = float(pc_V2_feat_autoenc_coef)

        # ── Perceptual hierarchy ─────────────────────────────────────────────
        self.stem_V1 = V1Stem(
            in_channels=in_channels,
            mid_channels=max(8, feature_channels_V1 // 2),
            out_channels=feature_channels_V1,
        )
        self.stem_V2 = V2Stem(
            in_channels=feature_channels_V1,
            out_channels=feature_channels_V2,
        )

        # ── Hierarchical FiLM (within-level fast + cross-level slow) ─────────
        self.film = HierarchicalFiLM(
            fast_memory_channels=memory_channels_fast,
            slow_memory_channels=memory_channels_slow,
            feature_channels=feature_channels_V1,
            fast_h=self.SPATIAL_FAST_H, fast_w=self.SPATIAL_FAST_W,
            slow_h=self.SPATIAL_SLOW_H, slow_w=self.SPATIAL_SLOW_W,
        )

        # ── Generative decoders ──────────────────────────────────────────────
        # Pixel decoder (collapse-proof anchor; V1-level only).
        self.pixel_decoder = PixelDecoder(
            memory_channels=memory_channels_fast,
            out_channels=in_channels,
            out_h=image_h, out_w=image_w,
        )
        # Multi-head feature decoders, one per level.
        self.feature_decoder_V1 = MultiHeadFeatureDecoder(
            memory_channels=memory_channels_fast,
            feature_channels=feature_channels_V1,
            n_heads=n_heads_fast,
            spatial_h=self.SPATIAL_FAST_H, spatial_w=self.SPATIAL_FAST_W,
        )
        self.feature_decoder_V2 = MultiHeadFeatureDecoder(
            memory_channels=memory_channels_slow,
            feature_channels=feature_channels_V2,
            n_heads=n_heads_slow,
            spatial_h=self.SPATIAL_SLOW_H, spatial_w=self.SPATIAL_SLOW_W,
        )

        # ── Recurrent memories ───────────────────────────────────────────────
        self.gru_fast = FastConvGRU(
            memory_channels=memory_channels_fast,
            feature_channels=feature_channels_V1,
            pixel_channels=in_channels,
            n_heads=n_heads_fast,
            update_gate_bias=update_gate_bias_fast,
        )
        self.gru_slow = SlowConvGRU(
            memory_channels=memory_channels_slow,
            feature_channels=feature_channels_V2,
            cross_in_channels=feature_channels_V1,
            n_heads=n_heads_slow,
            update_gate_bias=update_gate_bias_slow,
        )

        # ── Inner variational-inference loops ────────────────────────────────
        self.inner_fast = InnerWMLoop(
            memory_channels=memory_channels_fast,
            feature_channels=feature_channels_V1,
            n_heads=n_heads_fast,
            K=inner_K_fast,
            epsilon=inner_eps,
        )
        self.inner_slow = InnerWMLoop(
            memory_channels=memory_channels_slow,
            feature_channels=feature_channels_V2,
            n_heads=n_heads_slow,
            K=inner_K_slow,
            epsilon=inner_eps,
        )

        # ── Cross-level error pool (LEARNED) ─────────────────────────────────
        self.cross_pool = CrossLevelErrorPool(cross_in_channels=feature_channels_V1)

        # ── Decision readout + head-compression backbone + heads ─────────────
        self.readout = HierarchicalDecisionReadout(
            fast_memory_channels=memory_channels_fast,
            slow_memory_channels=memory_channels_slow,
            decision_channels=decision_channels,
            n_heads_fast=n_heads_fast,
            n_heads_slow=n_heads_slow,
            coarse_grid_fast=decision_coarse_grid_fast,
            fast_h=self.SPATIAL_FAST_H, fast_w=self.SPATIAL_FAST_W,
            slow_h=self.SPATIAL_SLOW_H, slow_w=self.SPATIAL_SLOW_W,
        )
        # Head-compression backbone: takes raw memory states + readout vector,
        # produces a compact embedding for the actor/critic. Replaces the
        # previous "small actor MLP over readout vector" with a richer learned
        # compression that has direct access to the full memory state.
        self.head_backbone = HeadCompressionBackbone(
            fast_memory_channels=memory_channels_fast,
            slow_memory_channels=memory_channels_slow,
            readout_dim=self.readout.output_dim,
            hidden_channels=head_compression_hidden,
            output_dim=head_compression_output,
        )
        self.actor = ActorHead(
            input_dim=self.head_backbone.output_dim,
            hidden_dim=actor_hidden,
            n_actions=n_actions,
            init_action_logit_bias=init_action_logit_bias,
        )
        # Action-conditional distributional Q critic.
        # Output shape (B, n_actions, n_quantiles); see readout.CriticHead.
        self.critic = CriticHead(
            input_dim=self.head_backbone.output_dim,
            hidden_dim=critic_hidden,
            n_actions=n_actions,
            n_quantiles=n_quantiles,
        )
        self.n_actions = n_actions
        self.n_quantiles = n_quantiles

    # ------------------------------------------------------------------
    #  Memory init
    # ------------------------------------------------------------------

    def init_memory(
        self,
        batch_size: int,
        device: Optional[torch.device] = None,
        dtype: torch.dtype = torch.float32,
    ) -> Tuple[torch.Tensor, torch.Tensor]:
        """Initialize both memory states to zero. Returns (M_fast_0, M_slow_0)."""
        device = device if device is not None else next(self.parameters()).device
        M_fast = torch.zeros(
            batch_size, self.memory_channels_fast,
            self.SPATIAL_FAST_H, self.SPATIAL_FAST_W,
            device=device, dtype=dtype,
        )
        M_slow = torch.zeros(
            batch_size, self.memory_channels_slow,
            self.SPATIAL_SLOW_H, self.SPATIAL_SLOW_W,
            device=device, dtype=dtype,
        )
        return M_fast, M_slow

    # ------------------------------------------------------------------
    #  Single step
    # ------------------------------------------------------------------

    def forward_step(
        self,
        x_t: torch.Tensor,
        M_fast_prev: torch.Tensor,
        M_slow_prev: torch.Tensor,
        return_aux: bool = False,
    ) -> StepOutput:
        """One env step. See class docstring for the operation sequence."""
        # 3.1, 3.2  Feedforward perceptual hierarchy.
        V1 = self.stem_V1(x_t)            # (B, C_V1, 12, 12)
        V2 = self.stem_V2(V1)             # (B, C_V2, 6, 6)

        # 3.4  Hierarchical FiLM modulation of V_1.
        P1 = self.film(M_fast_prev, M_slow_prev, V1)  # (B, C_V1, 12, 12)

        # 3.5, 3.6  Generative decoders + per-head saliency.
        # Pixel decoder: full-res prediction (50×50) for the collapse-proof PC anchor,
        # plus a grid-scale prediction (12×12) for native-resolution pixel saliency.
        x_hat, x_hat_grid = self.pixel_decoder(M_fast_prev)       # (B,3,50,50), (B,3,12,12)
        x_t_12 = F.interpolate(
            x_t, (self.SPATIAL_FAST_H, self.SPATIAL_FAST_W),
            mode="bilinear", align_corners=False,
        )                                                          # (B, 3, 12, 12)
        E_pix_12, S_V1_pix = pixel_saliency_map(x_t_12, x_hat_grid)

        # Multi-head feature decoders + per-head error/saliency at each level.
        V1_hat_per_head = self.feature_decoder_V1(M_fast_prev)     # (B, K_f, C_V1/K_f, 12, 12)
        V2_hat_per_head = self.feature_decoder_V2(M_slow_prev)     # (B, K_s, C_V2/K_s, 6, 6)
        E_V1_per_head, S_V1_per_head = multi_head_saliency(V1, V1_hat_per_head)
        E_V2_per_head, S_V2_per_head = multi_head_saliency(V2, V2_hat_per_head)

        # 5  Forward PC loss components (computed before GRU update).
        pc_pixel = predictive_coding_loss(x_t, x_hat)
        pc_pixel_grid = predictive_coding_loss(x_t_12, x_hat_grid)
        pc_V1_feat = multi_head_pc_loss(V1, V1_hat_per_head)
        pc_V2_feat = multi_head_pc_loss(V2, V2_hat_per_head)

        # 3.7  Per-level error-gated GRU updates.
        # Fast GRU receives both feature-domain and pixel-domain errors at 12×12.
        M_fast_t, _u_fast = self.gru_fast(M_fast_prev, P1, E_V1_per_head, S_V1_per_head, E_pix_12)

        # 3.10  LEARNED cross-level error pooling (V1 → V2 grid).
        E_V1_pooled = self.cross_pool(E_V1_per_head)  # (B, C_V1, 6, 6)
        M_slow_t, _u_slow = self.gru_slow(
            M_slow_prev, V2, E_V2_per_head, S_V2_per_head, E_V1_pooled,
        )

        # 3.8  Per-level inner variational-inference loops.
        M_fast_t = self.inner_fast(M_fast_t, V1, decoder=self.feature_decoder_V1)
        M_slow_t = self.inner_slow(M_slow_t, V2, decoder=self.feature_decoder_V2)

        # 5  Autoencoding PC terms (uses post-update memory).
        x_hat_auto, x_hat_grid_auto = self.pixel_decoder(M_fast_t)
        pc_pixel_auto = predictive_coding_loss(x_t, x_hat_auto)
        pc_pixel_grid_auto = predictive_coding_loss(x_t_12, x_hat_grid_auto)
        V2_hat_auto_per_head = self.feature_decoder_V2(M_slow_t)
        pc_V2_feat_auto = multi_head_pc_loss(V2, V2_hat_auto_per_head)

        pc_loss = (
            self.pc_pixel_coef * pc_pixel
            + self.pc_pixel_autoenc_coef * pc_pixel_auto
            + self.pc_pixel_grid_coef * pc_pixel_grid
            + self.pc_pixel_grid_autoenc_coef * pc_pixel_grid_auto
            + self.pc_V1_feat_coef * pc_V1_feat
            + self.pc_V2_feat_coef * pc_V2_feat
            + self.pc_V2_feat_autoenc_coef * pc_V2_feat_auto
        )

        # 3.9  Hierarchical decision readout (saliency-weighted feature pools).
        s_readout = self.readout(M_fast_t, S_V1_per_head, M_slow_t, S_V2_per_head)

        # 3.9b Head-compression backbone: takes raw memories + readout vector,
        # produces a compact embedding for the actor/critic. Lets the heads see
        # full spatial structure of the memory states with their own learned
        # compression, in addition to the saliency-weighted pools.
        s_t = self.head_backbone(M_fast_t, M_slow_t, s_readout)

        # 3.10  Heads.
        # Actor: π(a | s) logits.
        action_logits = self.actor(s_t)

        # Critic: action-conditional distributional Q.
        # Shapes:
        #   q_dist   : (B, n_actions, N_quantiles)  full distributional Q
        #   q_values : (B, n_actions)               mean over quantiles
        #   value    : (B,)                         V(s) = Σ sg[π(a|s)] Q(s,a)
        # The stop-gradient inside CriticHead.state_value ensures the value
        # baseline cannot leak gradient into the actor — the actor is updated
        # ONLY by the PPO surrogate. The critic is updated only by the
        # quantile-Huber on Q(s, a_t) (and the implicit shared-feature
        # gradient through the rest of the network).
        q_dist = self.critic(s_t)                                      # (B, |A|, N)
        q_values = q_dist.mean(dim=-1)                                 # (B, |A|)
        value = CriticHead.state_value(q_values, action_logits)        # (B,)

        aux: dict = {}
        if return_aux:
            aux = {
                "V1": V1, "V2": V2,
                "P1": P1,
                "x_hat": x_hat, "x_hat_grid": x_hat_grid,
                "x_hat_auto": x_hat_auto, "x_hat_grid_auto": x_hat_grid_auto,
                "V1_hat_per_head": V1_hat_per_head,
                "V2_hat_per_head": V2_hat_per_head,
                "E_V1_per_head": E_V1_per_head, "E_V2_per_head": E_V2_per_head,
                "E_pix_12": E_pix_12,
                "E_V1_pooled": E_V1_pooled,
                "S_V1_pix": S_V1_pix,
                "pc_pixel": pc_pixel.detach(),
                "pc_pixel_auto": pc_pixel_auto.detach(),
                "pc_pixel_grid": pc_pixel_grid.detach(),
                "pc_pixel_grid_auto": pc_pixel_grid_auto.detach(),
                "pc_V1_feat": pc_V1_feat.detach(),
                "pc_V2_feat": pc_V2_feat.detach(),
                "pc_V2_feat_auto": pc_V2_feat_auto.detach(),
                "s_t": s_t,
            }

        return StepOutput(
            action_logits=action_logits,
            value=value,
            q_values=q_values,
            q_dist=q_dist,
            M_fast_next=M_fast_t,
            M_slow_next=M_slow_t,
            S_V1_per_head=S_V1_per_head,
            S_V2_per_head=S_V2_per_head,
            S_V1_pix=S_V1_pix,
            pc_loss=pc_loss,
            aux=aux,
        )

    # ------------------------------------------------------------------
    #  Whole episode
    # ------------------------------------------------------------------

    def forward_episode(
        self,
        x_seq: torch.Tensor,
        M_fast_init: Optional[torch.Tensor] = None,
        M_slow_init: Optional[torch.Tensor] = None,
    ) -> EpisodeOutput:
        if x_seq.dim() != 5:
            raise ValueError(f"forward_episode expects (B,T,C,H,W); got {x_seq.dim()}D")
        B, T = x_seq.shape[0], x_seq.shape[1]

        if M_fast_init is None or M_slow_init is None:
            mf0, ms0 = self.init_memory(B, device=x_seq.device, dtype=x_seq.dtype)
            M_fast_init = M_fast_init if M_fast_init is not None else mf0
            M_slow_init = M_slow_init if M_slow_init is not None else ms0

        action_logits, values, q_values_l, q_dist_l = [], [], [], []
        S_V1_ph, S_V2_ph, S_V1_pix_seq = [], [], []
        pc_losses = []
        M_fast_seq = [M_fast_init]
        M_slow_seq = [M_slow_init]

        Mf, Ms = M_fast_init, M_slow_init
        for t in range(T):
            out = self.forward_step(x_seq[:, t], Mf, Ms, return_aux=False)
            action_logits.append(out.action_logits)
            values.append(out.value)
            q_values_l.append(out.q_values)
            q_dist_l.append(out.q_dist)
            S_V1_ph.append(out.S_V1_per_head)
            S_V2_ph.append(out.S_V2_per_head)
            S_V1_pix_seq.append(out.S_V1_pix)
            pc_losses.append(out.pc_loss)
            Mf, Ms = out.M_fast_next, out.M_slow_next
            M_fast_seq.append(Mf)
            M_slow_seq.append(Ms)

        return EpisodeOutput(
            action_logits=torch.stack(action_logits, dim=1),
            values=torch.stack(values, dim=1),
            q_values_seq=torch.stack(q_values_l, dim=1),
            q_dist_seq=torch.stack(q_dist_l, dim=1),
            M_fast_seq=torch.stack(M_fast_seq, dim=1),
            M_slow_seq=torch.stack(M_slow_seq, dim=1),
            S_V1_per_head_seq=torch.stack(S_V1_ph, dim=1),
            S_V2_per_head_seq=torch.stack(S_V2_ph, dim=1),
            S_V1_pix_seq=torch.stack(S_V1_pix_seq, dim=1),
            pc_loss_seq=torch.stack(pc_losses, dim=0),
        )

    # ------------------------------------------------------------------
    #  Parameter accounting
    # ------------------------------------------------------------------

    def count_parameters(self) -> dict[str, int]:
        return {
            "stem_V1": sum(p.numel() for p in self.stem_V1.parameters()),
            "stem_V2": sum(p.numel() for p in self.stem_V2.parameters()),
            "film": sum(p.numel() for p in self.film.parameters()),
            "decoder_pix": sum(p.numel() for p in self.pixel_decoder.parameters()),
            "decoder_V1_feat": sum(p.numel() for p in self.feature_decoder_V1.parameters()),
            "decoder_V2_feat": sum(p.numel() for p in self.feature_decoder_V2.parameters()),
            "gru_fast": sum(p.numel() for p in self.gru_fast.parameters()),
            "gru_slow": sum(p.numel() for p in self.gru_slow.parameters()),
            "inner_fast": sum(p.numel() for p in self.inner_fast.parameters()),
            "inner_slow": sum(p.numel() for p in self.inner_slow.parameters()),
            "cross_pool": sum(p.numel() for p in self.cross_pool.parameters()),
            "readout": sum(p.numel() for p in self.readout.parameters()),
            "head_backbone": sum(p.numel() for p in self.head_backbone.parameters()),
            "actor": sum(p.numel() for p in self.actor.parameters()),
            "critic": sum(p.numel() for p in self.critic.parameters()),
            "total": sum(p.numel() for p in self.parameters()),
        }
