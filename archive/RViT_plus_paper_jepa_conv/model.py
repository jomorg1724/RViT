"""
Recurrent ViT — the EXACT paper network (Morgan, Albanna, Herman), assembled:

    frame → VAEPatchFrontEnd (4 patches → 140-d tokens)
          → RecurrentViTxLSTM (multiplicative self-attention + spatial xLSTM)
          → flattened memory readout H' ∈ ℝ^{4096}
          → FFActor (policy)  +  QRCritic (distributional value)

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
import torch.nn.functional as F

try:
    from .vae_frontend import VAEPatchFrontEnd
    from .conv_frontend import ConvPatchFrontEnd
    from .paper_encoder import RecurrentViTxLSTM
    from .paper_heads import FFActor, QRCritic, JEPAStructuredHead, ImageVAEHead
except ImportError:  # script / flat import
    from vae_frontend import VAEPatchFrontEnd        # type: ignore[no-redef]
    from conv_frontend import ConvPatchFrontEnd      # type: ignore[no-redef]
    from paper_encoder import RecurrentViTxLSTM       # type: ignore[no-redef]
    from paper_heads import FFActor, QRCritic, JEPAStructuredHead, ImageVAEHead   # type: ignore[no-redef]


class RViTPaperModel(nn.Module):
    def __init__(self, n_actions: int = 2, n_quantiles: int = 5,
                 init_action_bias: Optional[List[float]] = None, seq_len: int = 7,
                 feedback: str = "multiplicative", two_lstm: bool = False,
                 cell: str = "xlstm", mem_heads: int = 4, vae_in_channels: int = 1,
                 jepa_n_heads: int = 0, jepa_proto_dim: int = 256, frame_repeat: int = 1,
                 d_mem: int = 1024, conv_frontend: bool = False,
                 conv_recurrent: bool = False, conv_rec_stage: int = 1, conv_rec_retain: float = 0.3,
                 vae_aux: bool = False, vae_latent_dim: int = 64, vae_reduce_dim: int = 32,
                 vae_img_size: int = 50, mem_noise: float = 0.0, **_ignore) -> None:
        super().__init__()
        self.frame_repeat = int(frame_repeat)   # front-end time one-hot uses the LOGICAL frame = t // frame_repeat
        if init_action_bias is None:
            init_action_bias = [0.0, -1.5]
        self.n_actions = int(n_actions)
        self.n_quantiles = int(n_quantiles)
        self.seq_len = int(seq_len)
        self.feedback = feedback
        self.cell = cell
        if cell == "softmax_head":
            two_lstm = False
        self.two_lstm = two_lstm
        self.enc_layers = 2 if two_lstm else 1                    # parity field for the harness

        # Front-end: CONV (capable SE-ResNet, 3ch colour, trained end-to-end) or the paper VAE encoder.
        self.conv_frontend = bool(conv_frontend)
        # Perceptual recurrence ("visual-cortex" ConvMGU) — only lives in the CONV front-end.
        self.conv_recurrent = bool(conv_recurrent)
        if self.conv_recurrent and not self.conv_frontend:
            raise ValueError("conv_recurrent=True requires conv_frontend=True (the ConvMGU lives in ConvPatchFrontEnd)")
        self.vae_in_channels = 3 if self.conv_frontend else int(vae_in_channels)   # conv is always colour
        self.front = (ConvPatchFrontEnd(in_channels=3, conv_recurrent=self.conv_recurrent,
                                        conv_rec_stage=int(conv_rec_stage), conv_rec_retain=float(conv_rec_retain))
                      if self.conv_frontend else VAEPatchFrontEnd(in_channels=self.vae_in_channels))
        self.encoder = RecurrentViTxLSTM(feedback=feedback, two_lstm=two_lstm,
                                         cell=cell, mem_heads=mem_heads, d_mem=int(d_mem))
        # WORKING-MEMORY NOISE: relative Gaussian noise on the PERSISTENT xLSTM cell state C — it drifts
        # each step, so the recurrence must learn ATTRACTORS to pull it back (WM-capacity/AB bottleneck).
        self.mem_noise = float(mem_noise)
        for _c in (getattr(self.encoder, "lstm", None), getattr(self.encoder, "lstm2", None)):
            if _c is not None and hasattr(_c, "mem_noise"):
                _c.mem_noise = self.mem_noise
        self.n_tokens = self.encoder.n_patch
        rd = self.encoder.readout_dim                            # 4096
        self.actor_head = FFActor(rd, n_actions, init_action_bias=init_action_bias)
        self.critic_head = QRCritic(rd, n_actions, n_quantiles)
        # JEPA self-distillation head (built only when enabled). Per patch token it emits n_heads
        # embeddings of proto_dim, each softmaxed independently. jepa_center is the DINO
        # teacher-centering buffer, shaped (n_tokens, n_heads, proto_dim) — one centre per softmax group.
        self.jepa_n_heads, self.jepa_proto_dim = int(jepa_n_heads), int(jepa_proto_dim)
        if self.jepa_n_heads > 0:
            self.jepa_head = JEPAStructuredHead(self.encoder.d_mem, n_heads=self.jepa_n_heads,
                                                proto_dim=self.jepa_proto_dim)
            self.register_buffer("jepa_center",
                                 torch.zeros(self.n_tokens, self.jepa_n_heads, self.jepa_proto_dim))
            if self.two_lstm:                                    # DUAL JEPA: a second self-distillation head
                self.jepa_head_h1 = JEPAStructuredHead(self.encoder.d_mem, n_heads=self.jepa_n_heads,
                                                       proto_dim=self.jepa_proto_dim)   # on the feedback memory H1
                self.register_buffer("jepa_center_h1",
                                     torch.zeros(self.n_tokens, self.jepa_n_heads, self.jepa_proto_dim))

        # Bottom-up image-VAE auxiliary (separate backward pass; memory gradients detached).
        self.vae_aux = bool(vae_aux)
        if self.vae_aux:
            self.vae_head = ImageVAEHead(d_token=self.encoder.d_token, n_patch=self.n_tokens,
                                         reduce_dim=int(vae_reduce_dim), latent_dim=int(vae_latent_dim),
                                         img_ch=3, img_hw=int(vae_img_size))

    # ── recurrent state: (xLSTM (H,C,N,M), timestep) ─────────────────────────
    def init_states(self, batch_size: int, device=None, dtype=torch.float32):
        # (xLSTM enc_state, timestep, ConvMGU perceptual state). conv_state=None → zeros on the first frame.
        return (self.encoder.init_states(batch_size, device=device, dtype=dtype), 0, None)

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
                attn_clamp=None, **_ignore) -> dict:
        enc_state, t, conv_state = prev_states if len(prev_states) == 3 else (prev_states[0], prev_states[1], None)
        if self.conv_recurrent:                                  # advance perceptual recurrence every physical step
            X, conv_state = self.front(self._to_bchw(x_t), t // self.frame_repeat, conv_state)
        else:
            X = self.front(self._to_bchw(x_t), t // self.frame_repeat)
        new_enc, H_new, attn = self.encoder.forward_step(X, enc_state, return_attn=return_attn,
                                                         attn_clamp=attn_clamp)
        actor_logits, q_dist, V_dist, V_scalar, H_flat = self._decode_readout(H_new)
        return {
            "new_states": (new_enc, t + 1, conv_state),
            "new_c3_specialists": {},
            "actor_logits": actor_logits,
            "critic_q_dist": q_dist,
            "V_dist": V_dist,
            "V_scalar": V_scalar,
            "attn": [attn] if attn is not None else None,
            "rec": H_flat,
        }

    # ── re-encode a whole trajectory (PAC update / analysis) ──────────────────
    def forward_rl_sequence(self, x_video: torch.Tensor, return_attn: bool = False,
                            return_cell: bool = False, **_ignore) -> dict:
        B, T = x_video.shape[:2]
        enc_state = self.encoder.init_states(B, device=x_video.device, dtype=x_video.dtype)
        conv_state = None                                        # ConvMGU perceptual state (reset per episode; BPTT flows)
        a_seq, q_seq, vd_seq, vs_seq, attn_seq, cell_seq = [], [], [], [], [], []
        cell_seq_h1 = []                                         # DUAL JEPA: feedback memory H1 sequence
        for t in range(T):
            if self.conv_recurrent:
                X, conv_state = self.front(self._to_bchw(x_video[:, t]), t // self.frame_repeat, conv_state)
            else:
                X = self.front(self._to_bchw(x_video[:, t]), t // self.frame_repeat)
            enc_state, H_new, attn = self.encoder.forward_step(X, enc_state, return_attn=return_attn)
            if return_attn and attn is not None:
                attn_seq.append(attn)
            if return_cell:
                cell_seq.append(H_new[0] if isinstance(H_new, (tuple, list)) else H_new)   # (B,4,d_mem)=H2
                if self.two_lstm and hasattr(self, "jepa_head_h1"):
                    cell_seq_h1.append(enc_state[0][0])          # H1 (LSTM1 hidden; the feedback memory)
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
        if return_cell:
            out["cell_seq"] = torch.stack(cell_seq, dim=1)       # (B,T,4,d_mem) — H2 (readout memory)
            if cell_seq_h1:
                out["cell_seq_h1"] = torch.stack(cell_seq_h1, dim=1)   # H1 (feedback memory), dual JEPA
        return out

    def jepa_logits(self, cell_seq: torch.Tensor) -> torch.Tensor:
        """cell_seq (B,T,4,d_mem) → prototype logits (B,T,4,K) via the DINO head."""
        return self.jepa_head(cell_seq)

    def jepa_logits_h1(self, cell_seq: torch.Tensor) -> torch.Tensor:
        """DUAL JEPA: prototype logits from the feedback memory H1 via its own head."""
        return self.jepa_head_h1(cell_seq)

    @staticmethod
    def _frames_bchw(v: torch.Tensor) -> torch.Tensor:
        """(B,T,H,W,3) channels-last → (B,T,3,H,W); pass through if already channels-first."""
        if v.dim() == 5 and v.shape[-1] == 3 and v.shape[2] != 3:
            return v.permute(0, 1, 4, 2, 3).contiguous()
        return v.contiguous()

    def recon_loss(self, x_video: torch.Tensor, beta: float = 1e-3):
        """Bottom-up image-VAE auxiliary on the transformer output Z, with the recurrent MEMORY
        DETACHED at each step. Gradient flows ONLY into the bottom-up path (conv front-end +
        attention projections + VAE head), never the LSTM — this is what lets the reconstruction
        pressure sharpen the perceptual (bottom-up) layers while leaving the top-down memory to RL.

        Forward values are identical to the normal forward (detach changes only the backward graph);
        the recurrence is advanced under no_grad purely to supply each step's memory context.
        Returns (loss, mse, kl). x_video: (B,T,H,W,3) or (B,T,3,H,W)."""
        B, T = x_video.shape[:2]
        state = self.encoder.init_states(B, device=x_video.device, dtype=x_video.dtype)
        conv_state = None                                                          # ConvMGU perceptual state
        Zs = []
        for t in range(T):
            if self.conv_recurrent:
                X, conv_state = self.front(self._to_bchw(x_video[:, t]), t // self.frame_repeat, conv_state)
            else:
                X = self.front(self._to_bchw(x_video[:, t]), t // self.frame_repeat)   # grad → front-end
            H_prev = (state[0] if self.encoder.two_lstm else state)[0]             # (B,N,d_mem)
            Z, _ = self.encoder.attn(X, H_prev.detach(), return_attn=False)        # DETACH memory
            Zs.append(Z)
            with torch.no_grad():                                                  # advance recurrence, no grad
                state, _, _ = self.encoder.forward_step(X.detach(), state)
        Z_seq = torch.stack(Zs, dim=1)                                             # (B,T,N,d_token)
        recon, mu, logvar = self.vae_head(Z_seq)                                   # (B,T,3,H,W)
        target = self._frames_bchw(x_video)
        mse = F.mse_loss(recon, target)
        kl = (-0.5 * (1.0 + logvar - mu.pow(2) - logvar.exp())).mean()
        return mse + beta * kl, mse.detach(), kl.detach()
