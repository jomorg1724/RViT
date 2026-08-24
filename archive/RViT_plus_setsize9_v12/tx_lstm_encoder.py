"""
Encoder for RViT+ setsize9_v12 — a VQ-VAE-style DISCRETE CODEBOOK bottleneck built out of
attention, SIMPLIFIED: the value codebook is now a STATIC LEARNABLE LOOKUP TABLE
(a plain nn.Parameter), not the self-referential recurrent H1 of the first setsize9_v12.

Per frame, with the carried key-memory H2 and the learned codebook table:

    Q = W_q · X                      # queries = the patch tokens
    K = W_k · H2                     # keys derived from the carried key-memory H2
    V = codebook                     # values = a STATIC learnable table (1, N, d)
    logits  = Q Kᵀ / (√d · τ)        # per head
    weights = softmax(logits)        # DEFAULT: plain soft attention over the N slots
    a       = W_o · ( weights @ codebook )          # a convex blend of codebook entries
    Z       = a + FFN(a)             # transformer output — NO X-residual

Recurrent update (only ONE recurrent state remains — the keys):
    H2 = LSTM(X + Z)                 # keys grounded in image + readout

Readout: the actor AND critic read Z (rec = [Z]).

vs the first setsize9_v12: H1 (the values) was a recurrent state updated by LSTM(Z); here it
is a fixed learned codebook table addressed by the evolving keys H2. The image still
enters ONLY as queries (which codebook slots to read) and into the H2 update — never
as a key or a value.

Default is SOFT attention (vq_mode='soft'): the readout is a smooth softmax-weighted
blend of the whole codebook — no sampling, fully differentiable. The hard VQ-VAE-style
variants stay available behind a knob: vq_mode='sample' (multinomial) or 'argmax', each
applied through a straight-through estimator
    onehot  = hard − soft.detach() + soft
so the forward pass reads ONE slot while gradients flow through the softmax. Other
knob: temperature τ. Requires d_model == d_mem and n_lstm == 1 (only H2 is recurrent).
"""
from __future__ import annotations

from typing import List, Optional, Tuple

import torch
import torch.nn as nn

# A recurrent state: (Hs, Cs), each a list with the single key-memory (B, n_tokens, d_mem).
State = Tuple[List[torch.Tensor], List[torch.Tensor]]


class VQAttnEncoder(nn.Module):
    """Sampled / straight-through codebook attention with a STATIC learnable value
    table (Q=X, K=H2, V=codebook) + one LSTM (the keys H2).

    Args
    ----
    n_tokens    : patch tokens AND codebook slots (e.g. 100).
    d_model     : transformer / token width (MUST equal d_mem).
    d_mem       : key-memory / codebook width.
    n_heads     : attention heads (each reads its own blend/slot; default 1).
    tx_layers   : accepted for config parity; fixed at one block.
    n_lstm      : must be 1 (only the key-memory H2 is recurrent; values are static).
    drop        : dropout.
    vq_mode     : 'soft' (default; plain softmax blend, no sampling/STE) |
                  'sample' (multinomial, straight-through) | 'argmax' (straight-through).
    temperature : softmax temperature τ.
    """

    def __init__(
        self,
        n_tokens: int,
        d_model: int = 128,
        d_mem: int = 128,
        n_heads: int = 1,
        tx_layers: int = 1,
        n_lstm: int = 1,
        drop: float = 0.1,
        vq_mode: str = "soft",
        temperature: float = 1.0,
    ) -> None:
        super().__init__()
        if d_model != d_mem:
            raise ValueError(f"d_model ({d_model}) must equal d_mem ({d_mem}).")
        if int(n_lstm) != 1:
            raise ValueError("setsize9_v12 (static codebook) needs n_lstm=1 (only the key-memory H2 is recurrent).")
        if d_model % n_heads != 0:
            raise ValueError(f"d_model ({d_model}) must be divisible by n_heads ({n_heads}).")
        if vq_mode not in ("soft", "sample", "argmax"):
            raise ValueError(f"vq_mode must be 'soft' | 'sample' | 'argmax'; got {vq_mode!r}.")
        self.n_tokens = n_tokens
        self.d_model, self.d_mem = d_model, d_mem
        self.n_heads = int(n_heads)
        self.head_dim = d_model // self.n_heads
        self.scale = self.head_dim ** -0.5
        self.n_lstm = 1
        self.vq_mode = vq_mode               # 'soft' = plain soft attention (no sampling/STE)
        self.temperature = float(temperature)

        # Attention projections: queries from X, keys from H2, NO value projection;
        # output projection recombines heads.
        self.W_q = nn.Linear(d_model, d_model)
        self.W_k = nn.Linear(d_mem, d_model)
        self.W_o = nn.Linear(d_mem, d_model)
        self.norm_q = nn.LayerNorm(d_model)
        self.norm_k = nn.LayerNorm(d_mem)
        self.norm_ff = nn.LayerNorm(d_model)
        self.ffn = nn.Sequential(
            nn.Linear(d_model, 4 * d_model), nn.GELU(), nn.Dropout(drop),
            nn.Linear(4 * d_model, d_model),
        )
        self.drop = nn.Dropout(drop)
        self.mem_pos_emb = nn.Parameter(torch.zeros(1, n_tokens, d_model))
        nn.init.normal_(self.mem_pos_emb, std=0.02)

        # The VALUE CODEBOOK: a static learnable lookup table of N slots (was H1).
        self.codebook = nn.Parameter(torch.randn(1, n_tokens, d_mem))

        # The single recurrent state: the key-memory H2 ← LSTM(X + Z).
        self.cell = nn.LSTMCell(d_model, d_mem)
        self.cells = nn.ModuleList([self.cell])     # alias for generic grad checks
        self.H0 = nn.ParameterList([nn.Parameter(torch.zeros(1, n_tokens, d_mem))])
        self.C0 = nn.ParameterList([nn.Parameter(torch.zeros(1, n_tokens, d_mem))])

        self.last_soft: Optional[torch.Tensor] = None
        self.last_weights: Optional[torch.Tensor] = None   # the attention weights actually applied
        self.last_hard: Optional[torch.Tensor] = None      # the one-hot (None in 'soft' mode)

    def init_states(self, batch_size: int, device=None, dtype=torch.float32) -> State:
        Hs = [h.to(device=device, dtype=dtype).expand(batch_size, -1, -1).contiguous() for h in self.H0]
        Cs = [c.to(device=device, dtype=dtype).expand(batch_size, -1, -1).contiguous() for c in self.C0]
        return Hs, Cs

    def _select(self, soft: torch.Tensor) -> torch.Tensor:
        B, H, Nq, Nk = soft.shape
        if self.vq_mode == "sample":
            idx = torch.multinomial(soft.reshape(-1, Nk), 1).reshape(B, H, Nq, 1)
        else:   # "argmax"
            idx = soft.argmax(dim=-1, keepdim=True)
        return torch.zeros_like(soft).scatter_(-1, idx, 1.0)

    def forward_step(self, tokens: torch.Tensor, prev_state: State, return_attn: bool = False):
        """Consume ONE frame X: address the static codebook (keys from H2), read it
        (soft softmax blend by default, or a sampled/argmax entry via STE), form Z,
        then H2 ← LSTM(X + Z).

        Returns (new_state, rec[, attn]); rec = [Z] (read by actor AND critic).
        """
        Hs, Cs = list(prev_state[0]), list(prev_state[1])
        B, N = tokens.shape[0], self.n_tokens
        H2 = Hs[0]                       # the only recurrent state: the key-memory
        C2 = Cs[0]
        X = tokens
        Hh, dh = self.n_heads, self.head_dim

        q = self.W_q(self.norm_q(X)) + self.mem_pos_emb       # (B,N,d)
        k = self.W_k(self.norm_k(H2)) + self.mem_pos_emb      # (B,N,d) keys from H2
        q = q.view(B, N, Hh, dh).transpose(1, 2)              # (B,H,N,dh)
        k = k.view(B, N, Hh, dh).transpose(1, 2)
        v = self.codebook.view(1, N, Hh, dh).transpose(1, 2)  # (1,H,N,dh) static table

        logits = torch.matmul(q, k.transpose(-2, -1)) * self.scale / max(self.temperature, 1e-6)
        soft = torch.softmax(logits, dim=-1)                  # (B,H,N,N)
        if self.vq_mode == "soft":
            weights = soft                                    # plain soft attention — NO sampling, NO STE
            hard = None
        else:
            hard = self._select(soft)                         # one-hot (sample / argmax)
            weights = hard - soft.detach() + soft             # straight-through
        attn_out = torch.matmul(weights, v)                   # (B,H,N,dh) — codebook readout (v broadcasts over B)
        attn_out = attn_out.transpose(1, 2).reshape(B, N, self.d_mem)
        a = self.drop(self.W_o(attn_out))                     # (B,N,d) — NO X residual
        Z = a + self.ffn(self.norm_ff(a))
        self.last_soft = soft.detach()
        self.last_weights = weights.detach()
        self.last_hard = None if hard is None else hard.detach()

        # the only recurrent update: keys H2 ← X + Z
        h2, c2 = self.cell((X + Z).reshape(B * N, self.d_model),
                           (H2.reshape(B * N, self.d_mem), C2.reshape(B * N, self.d_mem)))
        new_Hs = [h2.view(B, N, self.d_mem)]
        new_Cs = [c2.view(B, N, self.d_mem)]

        rec = [Z]                                             # actor AND critic read Z
        if return_attn:
            return (new_Hs, new_Cs), rec, [soft]
        return (new_Hs, new_Cs), rec
