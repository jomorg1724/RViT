"""
RViTPlusModel — the CANONICAL recurrent ViT of the paper, rebuilt with a stable
FiLM memory-feedback block and a conv (end-to-end) per-patch front-end, wired to the
reused PER + PAC + QR-DQN harness.

Pipeline (one frame), two LSTMs — H1 FiLM-gates Q/K, H2 supplies values, Z is the readout:
    x_t (B,3,50,50)
      │  front_end           → tokens X (B, N=grid, d_model)   [one token per stimulus]
      │  SingleStreamFiLMEncoder.forward_step:
      │     Q,K = X-proj ⊙ (1 + H1-proj)       (FiLM-gated by feedback memory H1)
      │     V   = W_V(H2)                       (values from the deep memory H2)
      │     Z   = W_reduce(concat[X, softmax(QKᵀ/√d)·V]) + FFN     (X = concat-residual)
      │     H1  = LSTM1(Z) ; H2 = LSTM2(Z)      (both memories updated from Z)
      │                                        → rec = [Z]  (shared readout)
      ├─► ActorDecoder([Z])  → logits (B, n_actions)
      └─► CriticDecoder([Z]) → Q (B, n_actions, n_quantiles) → V via derive_V

Single-stream / single readout — both heads read Z. H1 gain-modulates the query/key
matching, H2 supplies the attended content, X is the residual. The dual-stream split and
cross-attention are out-of-scope and not used here. Interface matches the harness.
"""
from __future__ import annotations

from typing import Dict, List, Optional, Tuple

import torch
import torch.nn as nn

try:
    from .decoder import ActorDecoder, CriticDecoder
    from .encoder import SingleStreamFiLMEncoder, State
    from .codebook_encoder import CodebookFiLMEncoder, CodebookV12Encoder
    from .twolayer_encoder import TwoLayerCodebookEncoder
    from .crosstalk_encoder import CrossTalkEncoder
    from .broadcast_encoder import BroadcastEncoder
    from .front_end import build_front_end
except ImportError:  # pragma: no cover
    from decoder import ActorDecoder, CriticDecoder       # type: ignore[no-redef]
    from encoder import SingleStreamFiLMEncoder, State     # type: ignore[no-redef]
    from codebook_encoder import CodebookFiLMEncoder, CodebookV12Encoder  # type: ignore[no-redef]
    from twolayer_encoder import TwoLayerCodebookEncoder   # type: ignore[no-redef]
    from crosstalk_encoder import CrossTalkEncoder         # type: ignore[no-redef]
    from broadcast_encoder import BroadcastEncoder         # type: ignore[no-redef]
    from front_end import build_front_end                  # type: ignore[no-redef]


class RViTPlusModel(nn.Module):
    def __init__(
        self,
        in_channels: int = 3,
        image_h: int = 50,
        image_w: int = 50,
        grid_rows: int = 2,
        grid_cols: int = 2,
        front_end: str = "pixel",          # raw pixels → linear, no conv
        patch_hidden: int = 128,           # used by mlp / patches front-ends
        patch_size: int = 5,               # used by `patches` front-end (5 → 100 tokens)
        d_model: int = 128,
        d_mem: int = 128,
        tx_heads: int = 1,
        tx_layers: int = 1,
        n_lstm: int = 2,
        readout: str = "Z",                # heads read: Z (default) | H1 | H2
        encoder: str = "crosstalk",        # crosstalk (default, cross-attention μ/q) | filmblock | codebook ...
        conv_channels: int = 64,
        n_conv_layers: int = 3,
        conv_kernel: int = 5,
        n_actions: int = 2,
        n_quantiles: int = 51,
        init_action_bias: Optional[list] = None,
        seq_len: int = 29,
        drop: float = 0.1,
    ) -> None:
        super().__init__()
        self.n_actions = int(n_actions)
        self.n_quantiles = int(n_quantiles)
        self.seq_len = int(seq_len)
        self.enc_layers = int(max(1, n_lstm))             # # recurrent states the harness stores
        self.split_c3 = False

        self.front = build_front_end(
            kind=front_end, in_channels=in_channels, image_h=image_h, image_w=image_w,
            grid_rows=grid_rows, grid_cols=grid_cols, d_model=d_model, patch_hidden=patch_hidden,
            patch_size=patch_size,
        )
        n_tokens = self.front.n_tokens
        self.n_tokens = n_tokens

        if encoder == "crosstalk":
            self.encoder = CrossTalkEncoder(
                n_tokens=n_tokens, d_model=d_model, d_mem=d_mem, n_heads=tx_heads,
                tx_layers=tx_layers, n_lstm=2, drop=drop,
            )
        elif encoder in ("broadcast_film", "broadcast"):
            # broadcast SELF-attention (Herman/Morgan multiplicative-feedback) in place of
            # cross-attention; same v11_part2 split + cross-talk. film=FiLM gate, add=straight.
            self.encoder = BroadcastEncoder(
                n_tokens=n_tokens, d_model=d_model, d_mem=d_mem, n_heads=tx_heads,
                tx_layers=tx_layers, n_lstm=2, drop=drop,
                mode=("film" if encoder == "broadcast_film" else "add"),
            )
        elif encoder == "twolayer":
            self.encoder = TwoLayerCodebookEncoder(
                n_tokens=n_tokens, d_model=d_model, d_mem=d_mem,
                t1_heads=1, t2_heads=2, tx_layers=tx_layers, drop=drop,
                readout=("Z2" if readout == "Z" else readout),
            )
        elif encoder == "codebook_v12":
            self.encoder = CodebookV12Encoder(
                n_tokens=n_tokens, d_model=d_model, d_mem=d_mem, n_heads=tx_heads,
                tx_layers=tx_layers, drop=drop, readout=readout,
            )
        elif encoder == "codebook":
            self.encoder = CodebookFiLMEncoder(
                n_tokens=n_tokens, d_model=d_model, d_mem=d_mem, n_heads=tx_heads,
                tx_layers=tx_layers, drop=drop, readout=readout,
            )
        else:
            self.encoder = SingleStreamFiLMEncoder(
                n_tokens=n_tokens, d_model=d_model, d_mem=d_mem, n_heads=tx_heads,
                tx_layers=tx_layers, n_lstm=n_lstm, drop=drop, readout=readout,
            )
        self.enc_layers = int(self.encoder.n_lstm)        # # recurrent states (codebook=1)

        dec_in = self.encoder.stream_dim                  # = d_model (single stream)
        self.actor_head = ActorDecoder(
            d_mem=dec_in, n_tokens=n_tokens, n_actions=n_actions,
            conv_channels=conv_channels, n_conv_layers=n_conv_layers,
            conv_kernel=conv_kernel, drop=drop, init_action_bias=init_action_bias,
        )
        self.critic_head = CriticDecoder(
            d_mem=dec_in, n_tokens=n_tokens, n_actions=n_actions, n_quantiles=n_quantiles,
            conv_channels=conv_channels, n_conv_layers=n_conv_layers,
            conv_kernel=conv_kernel, drop=drop,
        )

    # ── recurrent state ─────────────────────────────────────────────────────
    def init_states(self, batch_size: int, device=None, dtype=torch.float32) -> State:
        return self.encoder.init_states(batch_size, device=device, dtype=dtype)

    # ── one-frame head evaluation (both heads read the shared Z) ─────────────
    def _run_heads(self, rec: List[torch.Tensor]):
        # SPLIT readout when the encoder returns two streams (crosstalk: actor←Z_μ,
        # critic←Z_q); otherwise both heads read the single shared stream.
        z_actor = rec[0]
        z_critic = rec[1] if len(rec) > 1 else rec[0]
        actor_logits = self.actor_head([z_actor])
        q_dist = self.critic_head([z_critic])
        V_dist, V_scalar = self.critic_head.derive_V(q_dist, actor_logits)
        return actor_logits, q_dist, V_dist, V_scalar

    # ── online RL inference (single step) ───────────────────────────────────
    def rl_step(
        self,
        x_t: torch.Tensor,
        prev_states: State,
        attn_biases: Optional[dict] = None,               # parity; unused
        prev_c3_specialists: Optional[dict] = None,        # parity; unused
        return_attn: bool = False,
        attn_clamp: Optional[Dict[int, float]] = None,
    ) -> dict:
        tokens = self.front(x_t)
        step = self.encoder.forward_step(tokens, prev_states, return_attn=return_attn,
                                         attn_clamp=attn_clamp)
        if return_attn:
            new_states, rec, attn = step
        else:
            new_states, rec = step
            attn = None
        actor_logits, q_dist, V_dist, V_scalar = self._run_heads(rec)
        return {
            "new_states": new_states,
            "new_c3_specialists": {},
            "actor_logits": actor_logits,
            "critic_q_dist": q_dist,
            "V_dist": V_dist,
            "V_scalar": V_scalar,
            "attn": attn,                                  # [aw] or None — for analysis
            "rec": rec,                                    # stream output(s): [Z_μ, Z_q] for crosstalk
        }

    # ── re-encode a whole trajectory (PAC update path / analysis) ────────────
    def forward_rl_sequence(
        self,
        x_video: torch.Tensor,
        return_decoder: bool = False,                      # parity
        attn_biases_per_frame: Optional[list] = None,
        return_attn: bool = False,
        attn_clamp_per_frame: Optional[list] = None,
    ) -> dict:
        B, T = x_video.shape[:2]
        states = self.init_states(B, device=x_video.device, dtype=x_video.dtype)
        actor_logits_seq, q_dist_seq, V_dist_seq, V_scalar_seq, attn_seq = [], [], [], [], []
        states_seq: List[State] = []
        for t in range(T):
            tokens = self.front(x_video[:, t].contiguous())
            clamp = attn_clamp_per_frame[t] if attn_clamp_per_frame else None
            step = self.encoder.forward_step(tokens, states, return_attn=return_attn, attn_clamp=clamp)
            if return_attn:
                states, rec, aw = step
                attn_seq.append(aw[0])
            else:
                states, rec = step
            states_seq.append(states)
            a, q, vd, vs = self._run_heads(rec)
            actor_logits_seq.append(a); q_dist_seq.append(q)
            V_dist_seq.append(vd); V_scalar_seq.append(vs)
        out = {
            "actor_logits_seq": torch.stack(actor_logits_seq, dim=1),
            "q_dist_seq": torch.stack(q_dist_seq, dim=1),
            "V_dist_seq": torch.stack(V_dist_seq, dim=1),
            "V_scalar_seq": torch.stack(V_scalar_seq, dim=1),
            "states_seq": states_seq,
            "final_states": states,
            "recons": [],
        }
        if return_attn:
            out["attn_seq"] = torch.stack(attn_seq, dim=1)  # (B, T, n_heads, N, N)
        return out
