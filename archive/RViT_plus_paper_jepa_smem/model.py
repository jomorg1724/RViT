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

try:
    from .vae_frontend import VAEPatchFrontEnd
    from .paper_encoder import RecurrentViTxLSTM
    from .paper_heads import FFActor, QRCritic, JEPAStructuredHead
except ImportError:  # script / flat import
    from vae_frontend import VAEPatchFrontEnd        # type: ignore[no-redef]
    from paper_encoder import RecurrentViTxLSTM       # type: ignore[no-redef]
    from paper_heads import FFActor, QRCritic, JEPAStructuredHead   # type: ignore[no-redef]


class RViTPaperModel(nn.Module):
    def __init__(self, n_actions: int = 2, n_quantiles: int = 5,
                 init_action_bias: Optional[List[float]] = None, seq_len: int = 7,
                 feedback: str = "multiplicative", two_lstm: bool = False,
                 cell: str = "xlstm", mem_heads: int = 4, vae_in_channels: int = 1,
                 jepa_n_heads: int = 0, jepa_proto_dim: int = 256, frame_repeat: int = 1,
                 d_mem: int = 1024, softmax_memory: bool = False, **_ignore) -> None:
        super().__init__()
        self.frame_repeat = int(frame_repeat)   # front-end time one-hot uses the LOGICAL frame = t // frame_repeat
        if init_action_bias is None:
            init_action_bias = [0.0, -1.5]
        self.n_actions = int(n_actions)
        self.n_quantiles = int(n_quantiles)
        self.seq_len = int(seq_len)
        self.feedback = feedback
        # softmax-memory carries the CONTINUOUS xLSTM cell internally, so it REQUIRES cell='xlstm'
        # (the smem forward calls self.lstm with the 5-arg xLSTM signature). Force it here so a
        # leftover --cell default can't build a SoftmaxHeadCell and crash mid-forward.
        if softmax_memory:
            cell = "xlstm"
        self.cell = cell
        if cell == "softmax_head":
            two_lstm = False
        self.two_lstm = two_lstm
        self.enc_layers = 2 if two_lstm else 1                    # parity field for the harness

        # SOFTMAX-MEMORY: the JEPA student's per-head softmax IS the recurrent memory (fed back into
        # the cross-attention + read out). The structured head then has a SINGLE owner — the encoder's
        # mem_head — and jepa_logits routes to it; we do NOT build a separate self.jepa_head (that would
        # double-register and break the deepcopy'd teacher). Requires the structured head, so n_heads≥1.
        self.softmax_memory = bool(softmax_memory)
        if self.softmax_memory and jepa_n_heads <= 0:
            jepa_n_heads = 4                                      # softmax memory REQUIRES the structured head
        self.jepa_n_heads, self.jepa_proto_dim = int(jepa_n_heads), int(jepa_proto_dim)

        self.vae_in_channels = int(vae_in_channels)              # 1 grayscale / 3 COLOUR (value-aware)
        self.front = VAEPatchFrontEnd(in_channels=self.vae_in_channels)
        self.encoder = RecurrentViTxLSTM(feedback=feedback, two_lstm=two_lstm,
                                         cell=cell, mem_heads=mem_heads, d_mem=int(d_mem),
                                         softmax_memory=self.softmax_memory,
                                         mem_softmax_heads=self.jepa_n_heads,
                                         mem_softmax_dim=self.jepa_proto_dim)
        self.n_tokens = self.encoder.n_patch
        rd = self.encoder.readout_dim                            # n_patch * mem_dim (4096 at 4 heads×256)
        self.actor_head = FFActor(rd, n_actions, init_action_bias=init_action_bias)
        self.critic_head = QRCritic(rd, n_actions, n_quantiles)
        # JEPA self-distillation head (built only when enabled). Per patch token it emits n_heads
        # embeddings of proto_dim, each softmaxed independently. jepa_center is the DINO
        # teacher-centering buffer, shaped (n_tokens, n_heads, proto_dim) — one centre per softmax group.
        if self.jepa_n_heads > 0:
            if not self.softmax_memory:                          # normal JEPA: head owned by the model
                self.jepa_head = JEPAStructuredHead(self.encoder.d_mem, n_heads=self.jepa_n_heads,
                                                    proto_dim=self.jepa_proto_dim)
            self.register_buffer("jepa_center",
                                 torch.zeros(self.n_tokens, self.jepa_n_heads, self.jepa_proto_dim))

    # ── recurrent state: (xLSTM (H,C,N,M), timestep) ─────────────────────────
    def init_states(self, batch_size: int, device=None, dtype=torch.float32):
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
        enc_state, t = prev_states
        X = self.front(self._to_bchw(x_t), t // self.frame_repeat)
        new_enc, H_new, attn = self.encoder.forward_step(X, enc_state, return_attn=return_attn,
                                                         attn_clamp=attn_clamp)
        actor_logits, q_dist, V_dist, V_scalar, H_flat = self._decode_readout(H_new)
        return {
            "new_states": (new_enc, t + 1),
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
        a_seq, q_seq, vd_seq, vs_seq, attn_seq, cell_seq = [], [], [], [], [], []
        for t in range(T):
            X = self.front(self._to_bchw(x_video[:, t]), t // self.frame_repeat)
            enc_state, H_new, attn = self.encoder.forward_step(X, enc_state, return_attn=return_attn)
            if return_attn and attn is not None:
                attn_seq.append(attn)
            if return_cell:
                cell_seq.append(self.encoder.cont_cell(enc_state))   # CONTINUOUS cell (B,4,d_mem) for the JEPA head
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
            out["cell_seq"] = torch.stack(cell_seq, dim=1)       # (B,T,4,d_mem) — the recurrent cell output
        return out

    def jepa_logits(self, cell_seq: torch.Tensor) -> torch.Tensor:
        """cell_seq (B,T,4,d_mem) → prototype logits (B,T,4,n_heads,proto_dim) via the structured head.
        In softmax_memory mode the head lives in the encoder (single owner = the memory head)."""
        head = self.encoder.mem_head if self.softmax_memory else self.jepa_head
        return head(cell_seq)
