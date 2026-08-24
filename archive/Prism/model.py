"""
PrismModel — wires the six components into a single nn.Module.

Architecture writeup: see `../docs/THESIS.md` §3 (Methods).

Two callable interfaces:

    forward_step(x_t, M_prev) -> StepOutput
        Single-step forward used during rollout (and inside forward_episode).

    forward_episode(x_seq, M_init=None) -> EpisodeOutput
        Convenience: iterate forward_step over a (B, T, C, H, W) sequence.

Both return dataclass-style namedtuples so logging code can grab whatever
diagnostic it wants without dict-key fishing.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

import torch
import torch.nn as nn

try:
    from .decoder import GenerativeDecoder, PixelDecoder, pixel_saliency_map, prediction_error_map
    from .film import FiLM
    from .losses import predictive_coding_loss
    from .memory import ErrorGatedConvGRU, InnerWMLoop
    from .readout import ActorHead, CriticHead, DecisionReadout
    from .stem import V1Stem
except ImportError:
    from decoder import GenerativeDecoder, PixelDecoder, pixel_saliency_map, prediction_error_map  # type: ignore[no-redef]
    from film import FiLM  # type: ignore[no-redef]
    from losses import predictive_coding_loss  # type: ignore[no-redef]
    from memory import ErrorGatedConvGRU, InnerWMLoop  # type: ignore[no-redef]
    from readout import ActorHead, CriticHead, DecisionReadout  # type: ignore[no-redef]
    from stem import V1Stem  # type: ignore[no-redef]


# --- Output containers --------------------------------------------------------


@dataclass
class StepOutput:
    """One env step's worth of model outputs."""

    action_logits: torch.Tensor  # (B, n_actions)
    value: torch.Tensor  # (B,)
    M_next: torch.Tensor  # (B, C_M, H, W)
    saliency: torch.Tensor  # (B, 1, H, W) — the interpretable map S_t
    pc_loss: torch.Tensor  # scalar — L_PC at this step
    aux: dict = field(default_factory=dict)  # diagnostic intermediates


@dataclass
class EpisodeOutput:
    """A whole-episode unrolled forward pass."""

    action_logits: torch.Tensor  # (B, T, n_actions)
    values: torch.Tensor  # (B, T)
    M_seq: torch.Tensor  # (B, T+1, C_M, H, W)  — includes initial M_0
    saliency_seq: torch.Tensor  # (B, T, 1, H, W)
    pc_loss_seq: torch.Tensor  # (B, T) — per-step L_PC, averaged across batch later


# --- The model ---------------------------------------------------------------


class PrismModel(nn.Module):
    """
    PRISM: Predictive Recurrent Inference via Self-Modulation.

    Args
    ----
    in_channels              : C_in for x_t (default 3 for RGB)
    image_h, image_w         : pixel resolution of x_t (default 50, 50)
    feature_channels         : C_V — V1 stem output channels (default 32)
    memory_channels          : C_M — recurrent memory channels (default 16)
    n_actions                : discrete actions (default 2)
    inner_K                  : iterations of variational inference per env step (default 2)
    inner_eps                : step size of the inner WM loop (default 0.1)
    actor_hidden             : actor MLP hidden width (default 64)
    critic_hidden            : critic MLP hidden width (default 64)
    decision_channels        : evidence channels in the decision projection (default 4)
    init_action_logit_bias   : optional bias on policy logits at init (see ActorHead docs).
                                Default None. For ChangeDetectionEnv: pass [0.0, -4.0] so
                                the initial policy strongly prefers action 0 ("wait") and
                                episodes don't terminate at t=0 with a false alarm.
    pc_pixel_coef            : weight of the *forward* pixel PC loss ‖x_t − g(M_{t-1})‖²
                                in pc_loss. Default 1.0. This is the term whose error map
                                is used as the saliency signal — it predicts the next frame
                                from prior memory.
    pc_feature_coef          : weight of the feature-level PC loss (V vs g(M_prev)). Default
                                0.1 — small but nonzero so the feature decoder g still gets
                                an explicit training signal beyond what flows back through
                                the GRU/inner-loop usage.
    pc_autoenc_coef          : weight of the autoencoding PC term ‖x_t − g(M_t)‖² (i.e.
                                predict the *current* frame from the *post-GRU* memory).
                                Default 1.0. Necessary to break the cold-start zero-attractor:
                                because M_t is computed from x_t, the decoder can extract
                                some info from M_t for any input — so this term has nontrivial
                                gradient even when the decoder starts at zero-init. Once the
                                decoder is non-trivial, the forward term (pc_pixel) can also
                                start learning. Cost: one extra ~7K-param decoder pass per
                                env step. Set to 0 to disable.
    """

    # Spatial dims after the V1 stem. With image_size=50 these are 12×12.
    # If we ever change input image size we'll need to recompute these.
    SPATIAL_H: int = 12
    SPATIAL_W: int = 12

    def __init__(
        self,
        in_channels: int = 3,
        image_h: int = 50,
        image_w: int = 50,
        feature_channels: int = 32,
        memory_channels: int = 16,
        n_actions: int = 2,
        inner_K: int = 2,
        inner_eps: float = 0.1,
        actor_hidden: int = 64,
        critic_hidden: int = 64,
        decision_channels: int = 4,
        decision_coarse_grid: int = 2,
        init_action_logit_bias: list[float] | None = None,
        pc_pixel_coef: float = 1.0,
        pc_feature_coef: float = 0.1,
        pc_autoenc_coef: float = 1.0,
    ) -> None:
        super().__init__()
        self.feature_channels = feature_channels
        self.memory_channels = memory_channels
        self.n_actions = n_actions
        self.image_h = image_h
        self.image_w = image_w
        self.pc_pixel_coef = float(pc_pixel_coef)
        self.pc_feature_coef = float(pc_feature_coef)
        self.pc_autoenc_coef = float(pc_autoenc_coef)

        # Components.
        self.stem = V1Stem(
            in_channels=in_channels,
            mid_channels=max(16, feature_channels // 2),
            out_channels=feature_channels,
        )
        self.film = FiLM(
            memory_channels=memory_channels,
            feature_channels=feature_channels,
        )
        # Feature decoder g — used internally for the feature-space error map and
        # the inner WM loop. Trained both by gradient flowing back through the
        # GRU/inner-loop usage AND by the (small-weighted) feature PC term.
        self.decoder = GenerativeDecoder(
            memory_channels=memory_channels,
            feature_channels=feature_channels,
        )
        # Pixel decoder \tilde g — the collapse-proof generative model of the input.
        # Trained by the (large-weighted) pixel PC term. See decoder.PixelDecoder
        # for why predicting raw pixels (not learned features) prevents the
        # representation-collapse hazard of pure self-prediction.
        self.pixel_decoder = PixelDecoder(
            memory_channels=memory_channels,
            out_channels=in_channels,
            out_h=image_h,
            out_w=image_w,
        )
        self.gru = ErrorGatedConvGRU(
            memory_channels=memory_channels,
            feature_channels=feature_channels,
        )
        self.inner = InnerWMLoop(
            memory_channels=memory_channels,
            feature_channels=feature_channels,
            K=inner_K,
            epsilon=inner_eps,
        )
        self.readout = DecisionReadout(
            memory_channels=memory_channels,
            decision_channels=decision_channels,
            coarse_grid=decision_coarse_grid,
        )
        self.actor = ActorHead(
            input_dim=self.readout.output_dim,
            hidden_dim=actor_hidden,
            n_actions=n_actions,
            init_action_logit_bias=init_action_logit_bias,
        )
        self.critic = CriticHead(
            input_dim=self.readout.output_dim,
            hidden_dim=critic_hidden,
        )

    # ------------------------------------------------------------------
    #  Memory init
    # ------------------------------------------------------------------

    def init_memory(
        self,
        batch_size: int,
        device: Optional[torch.device] = None,
        dtype: torch.dtype = torch.float32,
    ) -> torch.Tensor:
        """
        Zero-initialise M_0 ∈ ℝ^(B, C_M, H, W).

        Why zero? The decoder is zero-init'd (see decoder.py), so g(0) ≈ 0,
        E_0 ≈ V_0, and L_PC ≈ ‖V_0‖² at the first step. The network starts
        maximally surprised — the right initial condition for a system about
        to learn its generative model.
        """
        device = device if device is not None else next(self.parameters()).device
        return torch.zeros(
            batch_size,
            self.memory_channels,
            self.SPATIAL_H,
            self.SPATIAL_W,
            device=device,
            dtype=dtype,
        )

    # ------------------------------------------------------------------
    #  Single step
    # ------------------------------------------------------------------

    def forward_step(
        self,
        x_t: torch.Tensor,
        M_prev: torch.Tensor,
        return_aux: bool = False,
    ) -> StepOutput:
        """
        One env step's worth of computation.

        x_t    : (B, 3, 50, 50)
        M_prev : (B, C_M, 12, 12)

        Returns StepOutput. See dataclass above.
        """
        # 4.1 Bottom-up perception.
        # V_t : (B, C_V, 12, 12)
        V_t = self.stem(x_t)

        # 4.2 Top-down FiLM modulation: distributed multiplicative gain.
        # P_t : (B, C_V, 12, 12)
        P_t = self.film(M_prev, V_t)

        # 4.3a Top-down generative predictions.
        #   - x_hat_t : pixel-space prediction (B, 3, 50, 50). The collapse-proof PC target.
        #   - V_hat_t : feature-space prediction (B, C_V, 12, 12). Used for the internal
        #               feature-error E_t that feeds the GRU candidate.
        x_hat_t = self.pixel_decoder(M_prev)
        V_hat_t = self.decoder(M_prev)

        # 4.3b Two error signals.
        #   E_t : feature-space sign-preserving error      (B, C_V, 12, 12)
        #         — used by the GRU's candidate so the candidate is informed by the
        #           direction (per-channel sign) of the prediction error.
        #   S_t : pixel-derived saliency on the feature grid (B, 1, 12, 12)
        #         — used by the GRU's update-gate amplifier and by the decision pool.
        #           Derived from PIXEL error so it cannot be cheated by stem collapse:
        #           even if the V1 stem zeroed itself out, S_t would still react to
        #           novelty in the raw input.
        E_t, _ = prediction_error_map(V_t, V_hat_t)
        _E_pix, S_t = pixel_saliency_map(x_t, x_hat_t, target_h=self.SPATIAL_H, target_w=self.SPATIAL_W)

        # 5.2 PC aux loss — combination of forward, feature, and autoencoding terms.
        #
        # FORWARD term (pc_pixel): predict x_t from M_{t-1}.
        #   This is the term whose error map drives the saliency S_t.
        #   PROBLEM: most of this env's per-frame information is unpredictable from
        #   prior memory alone (cue color/position/proportion are random per episode;
        #   initial Gabor orientations are random per episode). The decoder can
        #   converge to "predict zero everywhere" — which yields L_PC ≈ mean(x²) ≈ 0.025
        #   — and then ∂g/∂M ≈ 0, so no gradient flows back to the GRU and M never
        #   becomes useful. Stable but useless equilibrium. This is exactly what we
        #   observed empirically before adding the autoencoding term below.
        #
        # AUTOENCODING term (pc_autoenc): predict x_t from M_t (post-GRU memory).
        #   M_t was computed FROM x_t (via stem → FiLM → GRU), so the decoder can
        #   always extract some info from M_t about x_t. Gradient is non-trivial from
        #   step 1, breaking the cold-start zero-attractor. Once the decoder has
        #   non-trivial outputs, the forward term can also start learning because
        #   ∂g/∂M is no longer ≈ 0.
        #
        # FEATURE term (pc_feature): small-weighted feature-PC term ‖V_t − g(M_{t-1})‖².
        #   Provides explicit gradient to the (separate) feature decoder used by the
        #   inner WM loop and the GRU candidate.
        pc_pixel = predictive_coding_loss(x_t, x_hat_t)        # forward, drives saliency
        pc_feature = predictive_coding_loss(V_t, V_hat_t)      # feature regulariser

        # 4.4 Error-gated ConvGRU memory update.
        # M_t : (B, C_M, 12, 12)
        # u_t : (B, C_M, 12, 12)  (used for diagnostics only)
        M_t, u_t = self.gru(M_prev, P_t, E_t, S_t)

        # 4.5 Inner WM = K-step variational inference.
        # We pass the decoder explicitly so the inner loop shares its parameters.
        # Gradient flows back through decoder K+1 times in total per env step.
        M_t = self.inner(M_t, V_t, decoder=self.decoder)

        # 5.3 AUTOENCODING term: predict x_t from M_t (computed AFTER the GRU + inner
        # loop saw x_t). M_t depends on x_t, so this term is trivially trainable —
        # which breaks the cold-start zero-attractor of the forward term.
        # Skip the extra decoder pass entirely if the coef is 0.
        if self.pc_autoenc_coef > 0.0:
            x_hat_auto_t = self.pixel_decoder(M_t)
            pc_autoenc = predictive_coding_loss(x_t, x_hat_auto_t)
        else:
            pc_autoenc = pc_pixel.detach() * 0.0  # zero scalar with the right device/dtype/grad

        pc_loss = (
            self.pc_pixel_coef * pc_pixel
            + self.pc_autoenc_coef * pc_autoenc
            + self.pc_feature_coef * pc_feature
        )

        # 4.6 Decision readout: 8-d state vector.
        # Note that this uses the *outer* S_t — the saliency from BEFORE the
        # inner loop refined M. This matches §4.6 spec; using the post-inner-
        # loop saliency would be a one-line change but adds another forward
        # pass through the decoder, which is unnecessary for the actor/critic.
        s_t = self.readout(M_t, S_t)  # (B, 8)

        # 4.7 Heads.
        action_logits = self.actor(s_t)  # (B, n_actions)
        value = self.critic(s_t)  # (B,)

        aux: dict = {}
        if return_aux:
            aux = {
                "V_t": V_t,
                "V_hat_t": V_hat_t,
                "x_hat_t": x_hat_t,
                "E_t": E_t,
                "E_pix": _E_pix,
                "P_t": P_t,
                "u_t": u_t,
                "s_t": s_t,
                "pc_pixel": pc_pixel.detach(),
                "pc_feature": pc_feature.detach(),
                "pc_autoenc": pc_autoenc.detach(),
            }

        return StepOutput(
            action_logits=action_logits,
            value=value,
            M_next=M_t,
            saliency=S_t,
            pc_loss=pc_loss,
            aux=aux,
        )

    # ------------------------------------------------------------------
    #  Whole episode (convenience, used by PPO update)
    # ------------------------------------------------------------------

    def forward_episode(
        self,
        x_seq: torch.Tensor,
        M_init: Optional[torch.Tensor] = None,
    ) -> EpisodeOutput:
        """
        Iterate forward_step over a (B, T, C, H, W) sequence.

        Returns the full per-step outputs stacked along T. Used by the PPO
        update during the truncated-BPTT pass.

        x_seq : (B, T, 3, 50, 50)
        M_init: (B, C_M, 12, 12) or None (zero-init)

        Returns EpisodeOutput.

        Memory note
        -----------
        This holds the whole episode's intermediate tensors in memory at once.
        For the default sizes (B=8, T=30, C_V=32, H=W=12) this is well under
        a megabyte. If we scale up, switch to truncated BPTT in the trainer
        (which is what `ppo.py` does).
        """
        if x_seq.dim() != 5:
            raise ValueError(f"forward_episode expects 5D input (B,T,C,H,W); got {x_seq.dim()}D")
        B, T = x_seq.shape[0], x_seq.shape[1]

        if M_init is None:
            M_init = self.init_memory(B, device=x_seq.device, dtype=x_seq.dtype)

        # Storage for the per-step outputs.
        action_logits = []
        values = []
        saliencies = []
        pc_losses = []
        M_seq = [M_init]

        M_prev = M_init
        for t in range(T):
            out = self.forward_step(x_seq[:, t], M_prev, return_aux=False)
            action_logits.append(out.action_logits)
            values.append(out.value)
            saliencies.append(out.saliency)
            pc_losses.append(out.pc_loss)
            M_seq.append(out.M_next)
            M_prev = out.M_next

        return EpisodeOutput(
            action_logits=torch.stack(action_logits, dim=1),  # (B, T, n_actions)
            values=torch.stack(values, dim=1),  # (B, T)
            M_seq=torch.stack(M_seq, dim=1),  # (B, T+1, C_M, H, W)
            saliency_seq=torch.stack(saliencies, dim=1),  # (B, T, 1, H, W)
            pc_loss_seq=torch.stack(pc_losses, dim=0),  # (T,) — per-step scalars
        )

    # ------------------------------------------------------------------
    #  Convenience: count parameters
    # ------------------------------------------------------------------

    def count_parameters(self) -> dict[str, int]:
        """Per-module parameter count, for the budget table in §7 of the proposal."""
        return {
            "stem": sum(p.numel() for p in self.stem.parameters()),
            "film": sum(p.numel() for p in self.film.parameters()),
            "decoder_feat": sum(p.numel() for p in self.decoder.parameters()),
            "decoder_pix": sum(p.numel() for p in self.pixel_decoder.parameters()),
            "gru": sum(p.numel() for p in self.gru.parameters()),
            "inner": sum(p.numel() for p in self.inner.parameters()),
            "readout": sum(p.numel() for p in self.readout.parameters()),
            "actor": sum(p.numel() for p in self.actor.parameters()),
            "critic": sum(p.numel() for p in self.critic.parameters()),
            "total": sum(p.numel() for p in self.parameters()),
        }
