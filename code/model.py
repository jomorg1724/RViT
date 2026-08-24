"""
Recurrent ViT — the paper network (Morgan, Albanna, Herman), assembled:

    frame → VAEPatchFrontEnd (4 patches → 140-d tokens)
          → RecurrentViTxLSTM (multiplicative self-attention + spatial xLSTM)
          → flattened memory readout H' ∈ ℝ^{4096}
          → FFActor (policy)  +  QRCritic (distributional value)

The optional dual actor/critic mode instantiates two independent copies of the
front-end → Transformer-feedback → recurrent-memory path. The actor reads only
the actor memory and the critic reads only the critic memory.

The model exposes the interface our PAC/QR-DQN/PER harness (ppo.py) expects:
init_states / rl_step / forward_rl_sequence, and the attributes n_actions,
n_quantiles, seq_len. The recurrent state is ((H,C,N,M), t) — the xLSTM memory plus
an integer timestep used for the token's temporal one-hot. State is fully internal:
the harness only carries it opaquely (and re-encodes whole sequences from frames).
"""
from __future__ import annotations

from typing import Optional, List

import torch
import torch.nn as nn

try:
    from .vae_frontend import VAEPatchFrontEnd
    from .conv_frontend import ConvPatchFrontEnd
    from .paper_encoder import RecurrentViTxLSTM
    from .paper_heads import FFActor, QRCritic, JEPAStructuredHead
except ImportError:  # script / flat import
    from vae_frontend import VAEPatchFrontEnd        # type: ignore[no-redef]
    from conv_frontend import ConvPatchFrontEnd      # type: ignore[no-redef]
    from paper_encoder import RecurrentViTxLSTM       # type: ignore[no-redef]
    from paper_heads import FFActor, QRCritic, JEPAStructuredHead   # type: ignore[no-redef]


class RViTPaperModel(nn.Module):
    def __init__(self, n_actions: int = 2, n_quantiles: int = 5,
                 init_action_bias: Optional[List[float]] = None, seq_len: int = 7,
                 feedback: str = "multiplicative", two_lstm: bool = False,
                 cell: str = "xlstm", mem_heads: int = 4, vae_in_channels: int = 1,
                 jepa_n_heads: int = 0, jepa_proto_dim: int = 256, frame_repeat: int = 1,
                 d_mem: int = 1024, conv_frontend: bool = False,
                 grid_rows: int = 2, grid_cols: int = 2, image_size: int = 50,
                 memory_decay: float = 1.0, memory_noise_std: float = 0.0,
                 memory_output_noise_std: float = 0.0,
                 dual_actor_critic_streams: bool = False,
                 **_ignore) -> None:
        super().__init__()
        self.frame_repeat = int(frame_repeat)   # front-end time one-hot uses the LOGICAL frame = t // frame_repeat
        if init_action_bias is None:
            init_action_bias = [0.0, -1.5]
        self.n_actions = int(n_actions)
        self.n_quantiles = int(n_quantiles)
        self.seq_len = int(seq_len)
        self.feedback = feedback
        self.cell = cell
        self.dual_actor_critic_streams = bool(dual_actor_critic_streams)
        if self.dual_actor_critic_streams and cell in (
            "transformer_memory_2layer", "transformer_memory_2layer_softmax",
            "transformer_memory_2layer_softmax_modern"
        ):
            raise ValueError(
                "dual actor/critic streams currently require one memory level per stream"
            )
        if cell == "softmax_head":
            two_lstm = False
        self.two_lstm = two_lstm
        self.enc_layers = 2 if two_lstm else 1                    # parity field for the harness

        # Front-end: CONV (capable SE-ResNet, 3ch colour, trained end-to-end) or the paper VAE encoder.
        # The front-end fixes n_patch (grid_rows*grid_cols) and the token width (128+n_patch+8); the
        # encoder is then built to match, so 2x2/4-stim and 3x3/9-stim share one code path.
        self.conv_frontend = bool(conv_frontend)
        self.memory_output_noise_std = float(memory_output_noise_std)
        if not self.conv_frontend and ((grid_rows, grid_cols) != (2, 2) or image_size != 50):
            raise ValueError("the VAE front-end is fixed to a 2x2/50px layout; use --conv-frontend "
                             f"for grid {grid_rows}x{grid_cols} @ {image_size}px (e.g. vda9 = 3x3/75px).")
        self.vae_in_channels = 3 if self.conv_frontend else int(vae_in_channels)   # conv is always colour
        def make_front():
            return (
                ConvPatchFrontEnd(
                    in_channels=3,
                    grid_rows=grid_rows,
                    grid_cols=grid_cols,
                    image_size=image_size,
                )
                if self.conv_frontend
                else VAEPatchFrontEnd(in_channels=self.vae_in_channels)
            )

        def make_encoder(front):
            return RecurrentViTxLSTM(
                feedback=feedback,
                two_lstm=two_lstm,
                cell=cell,
                mem_heads=mem_heads,
                d_mem=int(d_mem),
                n_patch=int(front.n_tokens),
                d_token=int(front.token_dim),
                memory_decay=memory_decay,
                memory_noise_std=memory_noise_std,
                memory_output_noise_std=memory_output_noise_std,
            )

        self.front = make_front()
        n_patch = int(self.front.n_tokens); d_token = int(self.front.token_dim)
        self.encoder = make_encoder(self.front)
        if self.dual_actor_critic_streams:
            self.critic_front = make_front()
            self.critic_encoder = make_encoder(self.critic_front)
        self.n_tokens = self.encoder.n_patch
        rd = self.encoder.readout_dim                            # 4096
        self.actor_head = FFActor(rd, n_actions, init_action_bias=init_action_bias)
        self.critic_head = QRCritic(rd, n_actions, n_quantiles)
        # JEPA self-distillation head (built only when enabled). Per patch token it emits n_heads
        # embeddings of proto_dim, each softmaxed independently. jepa_center is the DINO
        # teacher-centering buffer, shaped (n_tokens, n_heads, proto_dim) — one centre per softmax group.
        self.jepa_n_heads, self.jepa_proto_dim = int(jepa_n_heads), int(jepa_proto_dim)
        self.jepa_n_memory_layers = 2 if cell in (
            "transformer_memory_2layer", "transformer_memory_2layer_softmax",
            "transformer_memory_2layer_softmax_modern"
        ) else 1
        # structured_jepa_loss averages its structured axis. In dual-stream mode
        # multiply that mean by two so each independent branch retains the stated
        # per-branch JEPA coefficient instead of silently receiving half of it.
        self.jepa_loss_multiplier = 2.0 if self.dual_actor_critic_streams else 1.0
        if self.jepa_n_heads > 0:
            if self.dual_actor_critic_streams:
                self.jepa_branch_names = ("actor", "critic")
                self.jepa_branch_heads = nn.ModuleList([
                    JEPAStructuredHead(
                        encoder.d_mem,
                        n_heads=self.jepa_n_heads,
                        proto_dim=self.jepa_proto_dim,
                    )
                    for encoder in (self.encoder, self.critic_encoder)
                ])
                self.register_buffer(
                    "jepa_center",
                    torch.zeros(2, self.n_tokens, self.jepa_n_heads, self.jepa_proto_dim),
                )
            elif self.jepa_n_memory_layers == 2:
                # H1 and H2 have different roles, so each gets its own student/EMA-teacher
                # projection head and DINO center rather than forcing a shared prototype map.
                self.jepa_layer_heads = nn.ModuleList([
                    JEPAStructuredHead(
                        self.encoder.d_mem,
                        n_heads=self.jepa_n_heads,
                        proto_dim=self.jepa_proto_dim,
                    )
                    for _ in range(2)
                ])
                self.register_buffer(
                    "jepa_center",
                    torch.zeros(2, self.n_tokens, self.jepa_n_heads, self.jepa_proto_dim),
                )
            else:
                self.jepa_head = JEPAStructuredHead(self.encoder.d_mem, n_heads=self.jepa_n_heads,
                                                    proto_dim=self.jepa_proto_dim)
                self.register_buffer("jepa_center",
                                     torch.zeros(self.n_tokens, self.jepa_n_heads, self.jepa_proto_dim))

    # ── recurrent state: (cell-dependent encoder state, timestep) ────────────
    def init_states(self, batch_size: int, device=None, dtype=torch.float32):
        if self.dual_actor_critic_streams:
            return ((
                self.encoder.init_states(batch_size, device=device, dtype=dtype),
                self.critic_encoder.init_states(batch_size, device=device, dtype=dtype),
            ), 0)
        return (self.encoder.init_states(batch_size, device=device, dtype=dtype), 0)

    @staticmethod
    def _to_bchw(x: torch.Tensor) -> torch.Tensor:
        """Accept (B,3,50,50) or (B,50,50,3); return (B,3,50,50)."""
        if x.dim() == 4 and x.shape[-1] == 3 and x.shape[1] != 3:
            x = x.permute(0, 3, 1, 2)
        return x.contiguous()

    def _run_heads(self, H_flat: torch.Tensor):
        actor_logits = self.actor_head(H_flat)
        q_dist = self.critic_head(H_flat)
        V_dist, V_scalar = self.critic_head.derive_V(q_dist, actor_logits)
        return actor_logits, q_dist, V_dist, V_scalar

    def heads_from_memory_sequence(self, memory_seq: torch.Tensor) -> dict[str, torch.Tensor]:
        """Decode ``(B,T,tokens,d_mem)`` memory through the online actor/critic heads."""
        if memory_seq.dim() != 4:
            raise ValueError(
                "actor/critic memory sequence must be (B,T,tokens,d_mem); "
                f"got {tuple(memory_seq.shape)}"
            )
        B, T = memory_seq.shape[:2]
        actor_logits, q_dist, V_dist, V_scalar = self._run_heads(
            memory_seq.flatten(2).flatten(0, 1)
        )
        return {
            "actor_logits_seq": actor_logits.unflatten(0, (B, T)),
            "q_dist_seq": q_dist.unflatten(0, (B, T)),
            "V_dist_seq": V_dist.unflatten(0, (B, T)),
            "V_scalar_seq": V_scalar.unflatten(0, (B, T)),
        }

    def _decode_readout(self, H_new):
        """H_new is either a single (B,4,1024) readout (both heads read it) or a tuple
        (actor_H, critic_H) for split-readout variants (e.g. affine_cascade: actor←H2,
        critic←H1). Returns (actor_logits, q_dist, V_dist, V_scalar, rec_flat)."""
        if isinstance(H_new, (tuple, list)):
            a_flat, c_flat = H_new[0].flatten(1), H_new[1].flatten(1)
            actor_logits = self.actor_head(a_flat)
            q_dist = self.critic_head(c_flat)
            V_dist, V_scalar = self.critic_head.derive_V(q_dist, actor_logits)
            return actor_logits, q_dist, V_dist, V_scalar, a_flat
        H_flat = H_new.flatten(1)
        a, q, vd, vs = self._run_heads(H_flat)
        return a, q, vd, vs, H_flat

    # ── one online step ──────────────────────────────────────────────────────
    def rl_step(self, x_t: torch.Tensor, prev_states, return_attn: bool = False,
                attn_clamp=None, inject_memory_noise: bool = False, **_ignore) -> dict:
        enc_state, t = prev_states
        frame = self._to_bchw(x_t)
        X = self.front(frame, t // self.frame_repeat)
        if self.dual_actor_critic_streams:
            actor_state, critic_state = enc_state
            new_actor, actor_H, attn = self.encoder.forward_step(
                X, actor_state, return_attn=return_attn, attn_clamp=attn_clamp,
                inject_memory_noise=inject_memory_noise,
            )
            critic_X = self.critic_front(frame, t // self.frame_repeat)
            new_critic, critic_H, critic_attn = self.critic_encoder.forward_step(
                critic_X, critic_state, return_attn=return_attn,
                inject_memory_noise=inject_memory_noise,
            )
            new_enc, H_new = (new_actor, new_critic), (actor_H, critic_H)
        else:
            new_enc, H_new, attn = self.encoder.forward_step(
                X, enc_state, return_attn=return_attn, attn_clamp=attn_clamp,
                inject_memory_noise=inject_memory_noise,
            )
            critic_attn = None
        actor_logits, q_dist, V_dist, V_scalar, H_flat = self._decode_readout(H_new)
        return {
            "new_states": (new_enc, t + 1),
            "new_c3_specialists": {},
            "actor_logits": actor_logits,
            "critic_q_dist": q_dist,
            "V_dist": V_dist,
            "V_scalar": V_scalar,
            "attn": [attn] if attn is not None else None,
            "critic_attn": [critic_attn] if critic_attn is not None else None,
            "rec": H_flat,
        }

    # ── re-encode a whole trajectory (PAC update / analysis) ──────────────────
    def forward_rl_sequence(self, x_video: torch.Tensor, return_attn: bool = False,
                            return_cell: bool = False, inject_memory_noise: bool = False,
                            return_raw_memory: bool = False,
                            return_prediction: bool = False,
                            **_ignore) -> dict:
        B, T = x_video.shape[:2]
        enc_state = self.encoder.init_states(B, device=x_video.device, dtype=x_video.dtype)
        if self.dual_actor_critic_streams:
            critic_state = self.critic_encoder.init_states(
                B, device=x_video.device, dtype=x_video.dtype
            )
        a_seq, q_seq, vd_seq, vs_seq, attn_seq, critic_attn_seq, cell_seq = [], [], [], [], [], [], []
        raw_memory_seq = []
        prediction_seq = []
        memory_attn_seq, memory_gate_seq, memory_source_contribution_seq = [], [], []
        for t in range(T):
            frame = self._to_bchw(x_video[:, t])
            X = self.front(frame, t // self.frame_repeat)
            enc_state, actor_H, attn = self.encoder.forward_step(
                X,
                enc_state,
                return_attn=return_attn,
                inject_memory_noise=inject_memory_noise,
            )
            if self.dual_actor_critic_streams:
                critic_X = self.critic_front(frame, t // self.frame_repeat)
                critic_state, critic_H, critic_attn = self.critic_encoder.forward_step(
                    critic_X, critic_state, return_attn=return_attn,
                    inject_memory_noise=inject_memory_noise,
                )
                H_new = (actor_H, critic_H)
                if return_attn and critic_attn is not None:
                    critic_attn_seq.append(critic_attn)
            else:
                H_new = actor_H
            if return_attn and attn is not None:
                attn_seq.append(attn)
                if self.encoder.cell == "transformer_memory_2layer_softmax_modern":
                    memory_attn_seq.append(self.encoder.last_memory_attn)
                    memory_gate_seq.append(self.encoder.last_memory_gate)
                    memory_source_contribution_seq.append(
                        self.encoder.last_memory_source_contribution
                    )
            if return_raw_memory and not self.dual_actor_critic_streams:
                raw_H1, raw_H2 = self.encoder._last_raw_memory
                raw_memory_seq.append(torch.stack((raw_H1, raw_H2), dim=1))  # (B,2,tokens,d_mem)
            if return_prediction and not self.dual_actor_critic_streams:
                H1_hat, H2_hat = self.encoder._last_prediction
                prediction_seq.append(torch.stack((H1_hat, H2_hat), dim=1))  # (B,2,tokens,d_mem)
            if return_cell:
                if self.dual_actor_critic_streams:
                    cell_seq.append(torch.stack((actor_H, critic_H), dim=1))
                elif self.encoder.cell in (
                    "transformer_memory_2layer",
                    "transformer_memory_2layer_softmax",
                    "transformer_memory_2layer_softmax_modern",
                ):
                    # Keep both recurrent levels for independent temporal JEPA targets.
                    cell_seq.append(torch.stack((enc_state[0], enc_state[1]), dim=1))  # (B,2,4,d_mem)
                else:
                    cell_seq.append(H_new[0] if isinstance(H_new, (tuple, list)) else H_new)
            a, q, vd, vs, _ = self._decode_readout(H_new)
            a_seq.append(a); q_seq.append(q); vd_seq.append(vd); vs_seq.append(vs)
        out = {
            "actor_logits_seq": torch.stack(a_seq, dim=1),       # (B,T,A)
            "q_dist_seq": torch.stack(q_seq, dim=1),             # (B,T,A,N)
            "V_dist_seq": torch.stack(vd_seq, dim=1),            # (B,T,N)
            "V_scalar_seq": torch.stack(vs_seq, dim=1),          # (B,T)
            "recons": [],
        }
        if return_attn and attn_seq:
            out["attn_seq"] = torch.stack(attn_seq, dim=1)       # (B,T,4,4)
        if return_attn and critic_attn_seq:
            out["critic_attn_seq"] = torch.stack(critic_attn_seq, dim=1)
        if return_attn and memory_attn_seq:
            out["memory_attn_seq"] = torch.stack(memory_attn_seq, dim=1)
            out["memory_gate_seq"] = torch.stack(memory_gate_seq, dim=1)
            out["memory_source_contribution_seq"] = torch.stack(
                memory_source_contribution_seq, dim=1
            )
        if return_cell:
            out["cell_seq"] = torch.stack(cell_seq, dim=1)       # single: (B,T,4,D); stacked: (B,T,2,4,D)
        if return_raw_memory and raw_memory_seq:
            out["raw_memory_seq"] = torch.stack(raw_memory_seq, dim=1)  # (B,T,2,4,D) pre-nonlinearity
        if return_prediction and prediction_seq:
            out["prediction_seq"] = torch.stack(prediction_seq, dim=1)  # (B,T,2,4,D) next-state predictions
        return out

    def jepa_logits(self, cell_seq: torch.Tensor) -> torch.Tensor:
        """Map one or both memory-level sequences to structured prototype logits."""
        if self.dual_actor_critic_streams:
            if cell_seq.dim() != 5 or cell_seq.shape[2] != 2:
                raise ValueError(
                    "dual-stream JEPA expects cell_seq shaped (B,T,2,tokens,d_mem); "
                    f"got {tuple(cell_seq.shape)}"
                )
            return torch.stack(
                [head(cell_seq[:, :, branch])
                 for branch, head in enumerate(self.jepa_branch_heads)],
                dim=2,
            )
        if self.jepa_n_memory_layers == 2:
            if cell_seq.dim() != 5 or cell_seq.shape[2] != 2:
                raise ValueError(
                    "two-layer JEPA expects cell_seq shaped (B,T,2,tokens,d_mem); "
                    f"got {tuple(cell_seq.shape)}"
                )
            return torch.stack(
                [head(cell_seq[:, :, layer]) for layer, head in enumerate(self.jepa_layer_heads)],
                dim=2,
            )
        return self.jepa_head(cell_seq)

    def jepa_features(self, cell_seq: torch.Tensor) -> torch.Tensor:
        """Return pre-prototype student features for variance/covariance regularization."""
        if self.dual_actor_critic_streams:
            if cell_seq.dim() != 5 or cell_seq.shape[2] != 2:
                raise ValueError("dual-stream JEPA features require (B,T,2,tokens,d_mem)")
            return torch.stack(
                [head.features(cell_seq[:, :, branch])
                 for branch, head in enumerate(self.jepa_branch_heads)],
                dim=2,
            )
        if self.jepa_n_memory_layers == 2:
            if cell_seq.dim() != 5 or cell_seq.shape[2] != 2:
                raise ValueError("two-layer JEPA features require (B,T,2,tokens,d_mem)")
            return torch.stack(
                [head.features(cell_seq[:, :, layer])
                 for layer, head in enumerate(self.jepa_layer_heads)],
                dim=2,
            )
        return self.jepa_head.features(cell_seq)
