"""
RViTPlusModel — video-compression encoder-decoder.

Per the owner's design intent (clarified after the per-frame-autoencoding
failure mode): the model is a *video compressor*. It encodes the entire input
video into a compressed final state, then decodes the entire video from that
single point. Both phases are explicit:

    final_states, encoder_aux = model.encode_sequence(x_video)
    # ... sample latent from final_states ...
    decoder_out                = model.decode_sequence(final_states, latent, T)

The two phases are separable, which is important for:
 * the microstim experiment (perturb encoder attention during a chosen frame
   and iteration, then run decode unchanged — see analysis/microstim.py)
 * the Stage-4 RL bridge (encoder used as a feature extractor; decoder not
   used during PPO rollouts)

Per-frame `forward_step` is retained as a thin convenience that does encode
only (no decoder), useful for interpretability probes.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

import torch
import torch.nn as nn

try:
    from .decoder import RViTPlusVideoDecoder
    from .encoder import RViTPlusEncoder
    from .latent import VAELatentSampler
    from .rl_heads import ActorHead, CriticHead, PredictiveCodingHead
    from .stem import V1Stem
except ImportError:  # pragma: no cover
    from decoder import RViTPlusVideoDecoder  # type: ignore[no-redef]
    from encoder import RViTPlusEncoder  # type: ignore[no-redef]
    from latent import VAELatentSampler  # type: ignore[no-redef]
    from rl_heads import ActorHead, CriticHead, PredictiveCodingHead  # type: ignore[no-redef]
    from stem import V1Stem  # type: ignore[no-redef]


@dataclass
class EncoderStepOutput:
    """One encode-step's worth of outputs (one input frame)."""
    layer_states_new: Tuple[torch.Tensor, ...] = ()
    attn_per_iter: List[List[torch.Tensor]] = field(default_factory=list)
    state_per_iter: List[List[torch.Tensor]] = field(default_factory=list)
    feedback_per_iter: List[Dict[str, torch.Tensor]] = field(default_factory=list)


@dataclass
class CompressionOutput:
    """One full video-compression forward pass: encode → latent → decode."""
    # Primary output
    recons: List[torch.Tensor] = field(default_factory=list)  # list of T recons
    final_encoder_states: Tuple[torch.Tensor, ...] = ()
    final_decoder_states: Tuple[torch.Tensor, ...] = ()

    # VAE latent
    latent_sample: Optional[torch.Tensor] = None
    latent_mu: Optional[torch.Tensor] = None
    latent_logvar: Optional[torch.Tensor] = None
    kl: Optional[torch.Tensor] = None
    kl_per_dim: Optional[torch.Tensor] = None  # (B, latent_c, h3, w3) — for free-bits / diagnostics

    # Aggregate losses (filled if targets supplied)
    pixel_recon: Optional[torch.Tensor] = None

    # Interpretability hooks — per-encoder-frame and per-decoder-step
    encoder_attn_per_frame: List[List[List[torch.Tensor]]] = field(default_factory=list)
    encoder_state_per_frame: List[List[List[torch.Tensor]]] = field(default_factory=list)
    decoder_attn_per_step: List[List[List[torch.Tensor]]] = field(default_factory=list)
    decoder_state_per_step: List[Tuple[torch.Tensor, torch.Tensor, torch.Tensor]] = field(default_factory=list)

    # RL heads (populated when actor / critic heads are enabled)
    actor_logits: Optional[torch.Tensor] = None     # (B, n_actions) — pre-softmax policy logits
    # Distributional, action-conditional Q (QR-DQN-style — Q_CRITIC.md).
    critic_q_dist: Optional[torch.Tensor] = None    # (B, n_actions, n_quantiles)
    critic_V_dist: Optional[torch.Tensor] = None    # (B, n_quantiles) — V_dist = Σ_a sg[π(a)]·Q(s,a,:)
    critic_V_scalar: Optional[torch.Tensor] = None  # (B,)              — V_scalar = mean(V_dist)


class RViTPlusModel(nn.Module):
    """Video-compression encoder-decoder.

    Args (defaults from RVIT_PLUS_DESIGN.md §3):
    in_channels        : 3 (RGB)
    image_h, image_w   : 50, 50
    stem_out_channels  : 64
    state_channels     : (64, 96, 128) for C₁ / C₂ / C₃
    n_FR               : encoder/decoder inner iterations per step (default 4)
    n_heads            : FT heads per layer (default 4)
    latent_dim         : VAE latent dim (default 128)
    enable_skips       : retinotectal-analog V→C₂, V→C₃ encoder skips
    skip_scale         : scaling on skip contributions (default 0.3)
    max_T              : maximum video length the decoder's temporal
                         embedding covers (default 32).
    """

    def __init__(
        self,
        in_channels: int = 3,
        image_h: int = 50,
        image_w: int = 50,
        stem_out_channels: int = 64,
        state_channels: Tuple[int, int, int] = (64, 96, 128),
        n_FR: int = 4,
        n_BR: int = 4,                       # kept for API back-compat; ignored
        n_heads: int = 4,
        seq_len: int = 10,                   # run-13: T frames the decoder predicts in one pass
        upsample_out_channels: int = 32,     # per-memory-state channels after upsampling to image res
        cnn_hidden: int = 64,                # decoder CNN hidden channels
        latent_channels: Optional[int] = None,  # legacy kwarg — VAE is skipped in run-13
        latent_dim: Optional[int] = None,    # legacy kwarg — VAE is skipped in run-13
        enable_skips: bool = True,
        skip_scale: float = 0.3,
        max_T: int = 32,                     # kept for API back-compat
        # RL heads (added run-18). Construction is optional — pure autoencoder
        # users keep enable_actor=False and enable_critic=False.
        enable_actor: bool = False,
        enable_critic: bool = False,
        n_actions: int = 2,                  # Posner press/wait default
        n_quantiles: int = 51,               # QR-DQN-style distributional critic — default 51
        rl_per_state_channels: int = 32,     # channels per memory state after downsample pyramid
        rl_cnn_hidden: int = 64,             # CNN hidden channels in the actor/critic reducer
        init_action_bias: Optional[list] = None,   # actor's per-action initial logit bias
        split_c3: bool = False,              # if True: separate C3 cells for AE / actor / critic
    ) -> None:
        super().__init__()
        # Run-13: VAE bottleneck deferred per user directive — encoder final
        # states pass directly into the decoder. `latent_channels` and
        # `latent_dim` kwargs are accepted (so old checkpoints' model_kwargs
        # don't break the constructor) but ignored.
        self.in_channels = in_channels
        self.image_h, self.image_w = image_h, image_w
        self.state_channels = state_channels
        self.n_FR = n_FR
        self.n_BR = n_BR  # informational only
        self.seq_len = seq_len
        self.max_T = max_T

        self.stem = V1Stem(
            in_channels=in_channels,
            mid_channels=32,
            out_channels=stem_out_channels,
        )

        self.encoder = RViTPlusEncoder(
            stem_out_channels=stem_out_channels,
            state_channels=state_channels,
            n_FR=n_FR,
            n_heads=n_heads,
            enable_skips=enable_skips,
            skip_scale=skip_scale,
            split_c3=split_c3,
        )
        self.split_c3 = bool(split_c3)

        # No latent_sampler in run-13. Encoder final states pass directly to decoder.
        self.latent_sampler = None

        self.decoder = RViTPlusVideoDecoder(
            state_channels=state_channels,
            grid_hw=self.encoder.GRID_HW,
            seq_len=seq_len,
            image_h=image_h,
            image_w=image_w,
            image_channels=in_channels,
            upsample_out_channels=upsample_out_channels,
            cnn_hidden=cnn_hidden,
        )

        # ── RL heads (optional) ─────────────────────────────────────────────
        # The actor and critic are independent modules with the same structural
        # pattern: per-memory-state downsample pyramids → concat → CNN reducer
        # → output (action logits or value). See rl_heads.py.
        self.enable_actor = bool(enable_actor)
        self.enable_critic = bool(enable_critic)
        self.n_actions = int(n_actions)
        self.n_quantiles = int(n_quantiles)

        # Target spatial size for both heads = deepest encoder level (default 3×3).
        rl_target_hw = self.encoder.GRID_HW[-1]

        if self.enable_actor:
            self.actor_head: Optional[ActorHead] = ActorHead(
                state_channels=state_channels,
                grid_hw=self.encoder.GRID_HW,
                target_hw=rl_target_hw,
                per_state_channels=rl_per_state_channels,
                cnn_hidden=rl_cnn_hidden,
                n_actions=n_actions,
                init_action_bias=init_action_bias,
            )
        else:
            self.actor_head = None

        if self.enable_critic:
            self.critic_head: Optional[CriticHead] = CriticHead(
                state_channels=state_channels,
                grid_hw=self.encoder.GRID_HW,
                target_hw=rl_target_hw,
                per_state_channels=rl_per_state_channels,
                cnn_hidden=rl_cnn_hidden,
                n_actions=n_actions,
                n_quantiles=n_quantiles,
            )
        else:
            self.critic_head = None

        c3 = state_channels[2]
        # ── Predictive-coding heads ─────────────────────────────────────
        # For each branch X ∈ {actor, critic}: a small upsample+refine
        # network that maps C_{3, X} (B, c3, h3, w3) → a tensor matching
        # C_2's shape (B, c2, h2, w2). Used by the PC auxiliary loss to
        # enforce C_{3, X, t-1} predicting C_{2, t} via cosine similarity.
        # PC's training signal is a temporal-consistency constraint on the
        # encoder that doesn't depend on actor / reward labels — useful
        # specifically when the actor has collapsed and the contrastive
        # losses lose their pair-label diversity.
        c2 = state_channels[1]
        h2, w2 = self.encoder.GRID_HW[1]
        h3, w3 = self.encoder.GRID_HW[2]
        self.pc_actor_head: Optional[PredictiveCodingHead] = None
        self.pc_critic_head: Optional[PredictiveCodingHead] = None
        if self.enable_actor:
            self.pc_actor_head = PredictiveCodingHead(
                c_in=c3, c_out=c2, spatial_in=(h3, w3), spatial_out=(h2, w2),
            )
        if self.enable_critic:
            self.pc_critic_head = PredictiveCodingHead(
                c_in=c3, c_out=c2, spatial_in=(h3, w3), spatial_out=(h2, w2),
            )

    # ── Initialization helpers ─────────────────────────────────────────────

    def init_states(
        self, batch_size: int, device=None, dtype=torch.float32
    ) -> Tuple[torch.Tensor, ...]:
        return self.encoder.init_states(batch_size, device=device, dtype=dtype)

    # ── Encoder-only convenience for per-frame analysis / microstim ──────

    def forward_step(
        self,
        x_t: torch.Tensor,
        prev_states: Tuple[torch.Tensor, torch.Tensor, torch.Tensor],
        attn_biases: Optional[dict] = None,
    ) -> EncoderStepOutput:
        """One frame's encode step (no decoder). Used for microstim probes
        and interpretability tools that work per-frame."""
        V = self.stem(x_t)
        enc_out = self.encoder.forward_step(V, prev_states, attn_biases=attn_biases)
        return EncoderStepOutput(
            layer_states_new=enc_out["layer_states_new"],
            attn_per_iter=enc_out["attn_per_iter"],
            state_per_iter=enc_out["state_per_iter"],
            feedback_per_iter=enc_out["feedback_per_iter"],
        )

    # ── Online RL inference (single step, recurrent state in/out) ──────────

    def rl_step(
        self,
        x_t: torch.Tensor,
        prev_states: Tuple[torch.Tensor, torch.Tensor, torch.Tensor],
        attn_biases: Optional[dict] = None,
        prev_c3_specialists: Optional[Dict[str, torch.Tensor]] = None,
    ) -> dict:
        """One frame's encode step + actor + distributional critic + V.

        Used for online rollout collection: feed one frame at a time, propagate
        the recurrent state across env steps. When `split_c3=True`, the
        `prev_c3_specialists` dict carries the per-task C₃ states between
        steps; on the first frame, pass `init_c3_specialists(B)` (or omit —
        the encoder will zero-init).

        Returns dict with:
            new_states         : (C₁, C₂, C₃_ae) — for next-step encoder input
            new_c3_specialists : dict {"actor": ..., "critic": ...} when split_c3
            actor_logits       : (B, n_actions)
            critic_q_dist      : (B, n_actions, n_quantiles)
            V_dist, V_scalar
        """
        if self.actor_head is None or self.critic_head is None:
            raise RuntimeError(
                "rl_step requires both actor_head and critic_head. "
                "Construct the model with enable_actor=True, enable_critic=True."
            )
        # Run the encoder. Pass C₃ specialists if we have them.
        V = self.stem(x_t)
        enc_out = self.encoder.forward_step(
            V, prev_states, attn_biases=attn_biases,
            prev_c3_specialists=prev_c3_specialists,
        )
        new_states = enc_out["layer_states_new"]   # (C1, C2, C3_ae)
        c3_spec = enc_out["c3_specialists_new"]    # {} or {"actor":..., "critic":...}

        # Route the right C₃ to each head.
        states_for_actor, states_for_critic = self._route_states_to_heads(new_states, c3_spec)

        actor_logits = self.actor_head(states_for_actor)
        q_dist = self.critic_head(states_for_critic)
        V_dist, V_scalar = self.critic_head.derive_V(q_dist, actor_logits)
        return {
            "new_states": new_states,
            "new_c3_specialists": c3_spec,
            "actor_logits": actor_logits,
            "critic_q_dist": q_dist,
            "V_dist": V_dist,
            "V_scalar": V_scalar,
        }

    # ── Full-video encode + decode (training path) ────────────────────────

    def encode_sequence(
        self,
        x_video: torch.Tensor,
        attn_biases_per_frame: Optional[List[dict]] = None,
    ) -> dict:
        """Encode an entire video x_video : (B, T, 3, H, W).

        Returns dict with:
            final_states         : tuple (C₁,C₂,C₃) at end of encoding
            attn_per_frame       : list of T (each = list of n_FR per-iter [a₁,a₂,a₃])
            state_per_frame      : analogously
            feedback_per_frame   : list of T per-iter dicts of cross-layer projections
        """
        B, T = x_video.shape[:2]
        states = self.init_states(B, device=x_video.device, dtype=x_video.dtype)
        c3_spec = self.encoder.init_c3_specialists(
            B, device=x_video.device, dtype=x_video.dtype
        )
        attn_per_frame = []
        attn_spatial_per_frame = []   # per-frame [[L1, L2, L3]] spatial residuals
        gates_per_frame = []          # per-frame [{q, k, v}] gates
        state_per_frame = []
        feedback_per_frame = []
        attn_specialists_per_frame = []
        for t in range(T):
            bias = None if attn_biases_per_frame is None else attn_biases_per_frame[t]
            V = self.stem(x_video[:, t])
            enc_out = self.encoder.forward_step(
                V, states, attn_biases=bias,
                prev_c3_specialists=c3_spec if self.split_c3 else None,
            )
            states = enc_out["layer_states_new"]
            c3_spec = enc_out["c3_specialists_new"]
            attn_per_frame.append(enc_out["attn_per_iter"])
            attn_spatial_per_frame.append(enc_out.get("attn_spatial_per_iter", []))
            gates_per_frame.append(enc_out.get("gates_per_iter", []))
            state_per_frame.append(enc_out["state_per_iter"])
            feedback_per_frame.append(enc_out["feedback_per_iter"])
            attn_specialists_per_frame.append(enc_out.get("attn_specialists_per_iter", []))
        return {
            "final_states": states,
            "final_c3_specialists": c3_spec,
            "attn_per_frame": attn_per_frame,
            "attn_spatial_per_frame": attn_spatial_per_frame,
            "gates_per_frame": gates_per_frame,
            "attn_specialists_per_frame": attn_specialists_per_frame,
            "state_per_frame": state_per_frame,
            "feedback_per_frame": feedback_per_frame,
        }

    def decode_sequence(
        self,
        final_states: Tuple[torch.Tensor, torch.Tensor, torch.Tensor],
    ) -> dict:
        """Decode the full video (seq_len frames) from encoder final states.
        Returns the dict from RViTPlusVideoDecoder.forward."""
        return self.decoder(final_states)

    def compress_and_reconstruct(
        self,
        x_video: torch.Tensor,
        attn_biases_per_frame: Optional[List[dict]] = None,
    ) -> CompressionOutput:
        """Full video-compression forward pass: encode → decode (no VAE in run-13).
        Also runs actor / critic heads if they are enabled (run-18 RL path).

        x_video : (B, T, 3, H, W) input video. T must equal self.seq_len because
                  the feedforward decoder predicts a fixed number of frames.
        """
        B, T = x_video.shape[:2]
        if T != self.seq_len:
            raise ValueError(
                f"x_video has T={T} but decoder is configured for seq_len={self.seq_len}. "
                f"The run-13 feedforward decoder predicts a fixed number of frames."
            )

        enc = self.encode_sequence(x_video, attn_biases_per_frame=attn_biases_per_frame)
        final_states = enc["final_states"]                # (C1, C2, C3_ae)
        final_c3_spec = enc.get("final_c3_specialists", {})

        # Decoder reads the canonical (C1, C2, C3_ae).
        dec = self.decode_sequence(final_states)

        # Actor/critic read C1, C2, and their OWN specialist C3 when split_c3,
        # else the same shared C3 as the decoder.
        states_for_actor, states_for_critic = self._route_states_to_heads(
            final_states, final_c3_spec
        )
        actor_logits = self.actor_head(states_for_actor) if self.actor_head is not None else None
        critic_q_dist, critic_V_dist, critic_V_scalar = self._run_critic(
            states_for_critic, actor_logits
        )

        return CompressionOutput(
            recons=dec["recons"],
            final_encoder_states=final_states,
            final_decoder_states=dec["final_dec_states"],
            latent_sample=None,
            latent_mu=None,
            latent_logvar=None,
            kl=None,
            kl_per_dim=None,
            pixel_recon=None,
            encoder_attn_per_frame=enc["attn_per_frame"],
            encoder_state_per_frame=enc["state_per_frame"],
            decoder_attn_per_step=dec["attn_per_step"],
            decoder_state_per_step=dec["state_per_step"],
            actor_logits=actor_logits,
            critic_q_dist=critic_q_dist,
            critic_V_dist=critic_V_dist,
            critic_V_scalar=critic_V_scalar,
        )

    # ── RL forward path (encoder + actor + critic, no decoder) ────────────

    def _route_states_to_heads(
        self,
        final_states: Tuple[torch.Tensor, ...],
        c3_specialists: Dict[str, torch.Tensor],
    ) -> Tuple[Tuple[torch.Tensor, ...], Tuple[torch.Tensor, ...]]:
        """Return `(states_for_actor, states_for_critic)`.

        With split_c3=False: actor/critic both read the same (C1, C2, C3).
        With split_c3=True:  each head reads (C1, C2, C3_<task>) where
                              C3_<task> is its dedicated specialist deep state.
        """
        if not self.split_c3:
            return final_states, final_states
        C1, C2, _ = final_states
        return (
            (C1, C2, c3_specialists["actor"]),
            (C1, C2, c3_specialists["critic"]),
        )

    def _run_critic(
        self,
        final_states: Tuple[torch.Tensor, ...],
        actor_logits: Optional[torch.Tensor],
    ) -> Tuple[Optional[torch.Tensor], Optional[torch.Tensor], Optional[torch.Tensor]]:
        """Run the distributional critic and derive V from Q + π.

        Returns (q_dist, V_dist, V_scalar) — all None if critic disabled.
        """
        if self.critic_head is None:
            return None, None, None
        q_dist = self.critic_head(final_states)
        if actor_logits is None:
            return q_dist, None, None
        V_dist, V_scalar = self.critic_head.derive_V(q_dist, actor_logits)
        return q_dist, V_dist, V_scalar

    def forward_rl_sequence(
        self,
        x_video: torch.Tensor,
        return_decoder: bool = False,
        attn_biases_per_frame: Optional[List[dict]] = None,
    ) -> dict:
        """Run encoder + actor + critic AT EVERY TIMESTEP of x_video.

        Used during PPO update: re-encode the rollout trajectory and recompute
        actor logits + critic Q distribution at every step (because the encoder
        has changed since rollout collection). Optionally also runs the decoder
        on the FINAL encoder state for the reconstruction auxiliary loss.

        Args
        ----
        x_video        : (B, T, 3, H, W) — episodes padded to T_max.
        return_decoder : if True, also runs the decoder for the recon aux loss.
        attn_biases_per_frame : optional microstim biases.

        Returns dict with:
            actor_logits_seq : (B, T, n_actions)
            q_dist_seq       : (B, T, n_actions, n_quantiles)
            V_dist_seq       : (B, T, n_quantiles)
            V_scalar_seq     : (B, T)
            states_seq       : list of T tuples of (C₁, C₂, C₃) — post-step states
            final_states     : (C₁, C₂, C₃) at end of sequence
            recons           : list of T recons (B, 3, H, W) if return_decoder else []
            encoder_attn_per_frame, encoder_state_per_frame for diagnostics.
        """
        if self.actor_head is None or self.critic_head is None:
            raise RuntimeError("forward_rl_sequence requires actor+critic enabled")
        B, T = x_video.shape[:2]
        device = x_video.device
        states = self.init_states(B, device=device, dtype=x_video.dtype)
        c3_spec = self.encoder.init_c3_specialists(B, device=device, dtype=x_video.dtype)

        actor_logits_seq = []
        q_dist_seq = []
        V_dist_seq = []
        V_scalar_seq = []
        states_seq: List[Tuple[torch.Tensor, ...]] = []
        actor_states_seq: List[Tuple[torch.Tensor, ...]] = []   # per-step (C₁, C₂, C₃_actor)
        critic_states_seq: List[Tuple[torch.Tensor, ...]] = []  # per-step (C₁, C₂, C₃_critic)
        attn_per_frame = []
        state_per_frame = []

        for t in range(T):
            bias = None if attn_biases_per_frame is None else attn_biases_per_frame[t]
            V = self.stem(x_video[:, t].contiguous())
            enc_out = self.encoder.forward_step(
                V, states, attn_biases=bias,
                prev_c3_specialists=c3_spec if self.split_c3 else None,
            )
            states = enc_out["layer_states_new"]
            c3_spec = enc_out["c3_specialists_new"]
            states_seq.append(states)
            attn_per_frame.append(enc_out["attn_per_iter"])
            state_per_frame.append(enc_out["state_per_iter"])

            # Per-step routing: each head sees its OWN C3 specialist (or the
            # shared C3 when split_c3=False).
            states_for_actor, states_for_critic = self._route_states_to_heads(states, c3_spec)
            actor_states_seq.append(states_for_actor)
            critic_states_seq.append(states_for_critic)

            actor_logits = self.actor_head(states_for_actor)
            q_dist = self.critic_head(states_for_critic)
            V_dist, V_scalar = self.critic_head.derive_V(q_dist, actor_logits)

            actor_logits_seq.append(actor_logits)
            q_dist_seq.append(q_dist)
            V_dist_seq.append(V_dist)
            V_scalar_seq.append(V_scalar)

        out: dict = {
            "actor_logits_seq": torch.stack(actor_logits_seq, dim=1),           # (B, T, A)
            "q_dist_seq":      torch.stack(q_dist_seq, dim=1),                  # (B, T, A, N)
            "V_dist_seq":      torch.stack(V_dist_seq, dim=1),                  # (B, T, N)
            "V_scalar_seq":    torch.stack(V_scalar_seq, dim=1),                # (B, T)
            "states_seq":      states_seq,
            # Per-step routed state triplets — the contrastive heads read these.
            "actor_states_seq":  actor_states_seq,
            "critic_states_seq": critic_states_seq,
            "final_states":    states,
            "encoder_attn_per_frame": attn_per_frame,
            "encoder_state_per_frame": state_per_frame,
            "recons": [],
        }

        if return_decoder:
            # The decoder reconstructs the full video from the FINAL encoder state.
            # Auxiliary self-supervised signal — gradient flows into the encoder.
            dec = self.decode_sequence(states)
            out["recons"] = dec["recons"]

        return out

    def forward_rl(
        self,
        x_video: torch.Tensor,
        attn_biases_per_frame: Optional[List[dict]] = None,
    ) -> CompressionOutput:
        """Encoder → actor/critic. Skips the decoder for speed when only the
        RL outputs are needed (e.g. environment rollouts during PPO collection).
        The reconstruction-loss training pass should use `compress_and_reconstruct`
        which runs decoder + actor + critic together so all three gradient
        sources flow back into the shared encoder.

        Returns a CompressionOutput with `recons` empty and the RL fields
        (actor_logits, critic_q_dist, critic_V_dist, critic_V_scalar) populated.
        """
        if self.actor_head is None and self.critic_head is None:
            raise RuntimeError(
                "forward_rl called but neither actor_head nor critic_head is enabled. "
                "Construct the model with enable_actor=True and/or enable_critic=True."
            )
        enc = self.encode_sequence(x_video, attn_biases_per_frame=attn_biases_per_frame)
        final_states = enc["final_states"]
        final_c3_spec = enc.get("final_c3_specialists", {})
        states_for_actor, states_for_critic = self._route_states_to_heads(
            final_states, final_c3_spec
        )
        actor_logits = self.actor_head(states_for_actor) if self.actor_head is not None else None
        critic_q_dist, critic_V_dist, critic_V_scalar = self._run_critic(
            states_for_critic, actor_logits
        )

        return CompressionOutput(
            recons=[],
            final_encoder_states=final_states,
            final_decoder_states=(),
            encoder_attn_per_frame=enc["attn_per_frame"],
            encoder_state_per_frame=enc["state_per_frame"],
            decoder_attn_per_step=[],
            decoder_state_per_step=[],
            actor_logits=actor_logits,
            critic_q_dist=critic_q_dist,
            critic_V_dist=critic_V_dist,
            critic_V_scalar=critic_V_scalar,
        )


# Back-compat alias for analysis scripts that imported StepOutput.
StepOutput = CompressionOutput
