"""
Broadcast self-attention encoders for the RViT+ battery — the Herman/Morgan
multiplicative-feedback / broadcast self-attention mechanism, as a drop-in
alternative to the cross-attention `crosstalk` encoder.

HYPOTHESIS UNDER TEST (user, 2026-06-21): broadcast SELF-attention — each stream
self-attends over its own *content* tokens while the other source is fed back as an
identity-initialised gate — makes the fast, immediate change-response easier to learn
than cross-attention (where the image *queries* memory). Cross-attention builds 2N
memory keys; broadcast builds a per-token feature gate and self-attends over N tokens.

The v11_part2 split + cross-talk are kept EXACTLY, so only the attention op changes:
    μ / priority stream (→ actor):   content = X ,   gate = [H1 ‖ H2] ,  residual = X
    q / value    stream (→ critic):  content = H2 ,  gate = X ,          residual = H2
    memory:   H1 = LSTM1(X) ,   H2 = LSTM2(Z_μ)        (the cross-talk lives in H2)

Each block self-attends over its CONTENT tokens; the GATE source modulates Q/K/V.
Two modes:

  mode="film"  (broadcast + FiLM adaptation):
        P = W_CP(content) ⊙ (1 + W_GP(gate))              for P in {Q, K, V}
      Gate projections W_GP are ZERO-init ⇒ (1+0)=1 ⇒ feedback off at init ⇒ the
      block is plain self-attention over `content` (clean baseline, no explosion).
      LayerNorm Q,K after the gate and before the softmax (reference stabilisation).

  mode="add"   (straight broadcast):
        P = W_CP(content) + W_GP(gate)                    for P in {Q, K, V}
      W_GP zero-init ⇒ feedback off at init (same clean baseline).
      NORMALIZATION PLACEMENT (the "don't blow everything up" knob): we LayerNorm
      Q, K AND V after the additive injection and before the attention. The FiLM form
      only needs Q,K because its (1+·) gate is bounded near 1; the additive form's V
      is unbounded, so it is normed too. Normalising the three attention inputs right
      after the broadcast injection is what keeps the logits and the value-path output
      bounded as the gate weights grow during training.
"""
from __future__ import annotations

from typing import Dict, List, Optional, Tuple

import torch
import torch.nn as nn

State = Tuple[List[torch.Tensor], List[torch.Tensor]]


class _BroadcastBlock(nn.Module):
    """Broadcast self-attention over `content` with a `gate`-modulated Q/K/V.

    content : (B, N, d_model)  — the tokens the attention runs over (its own residual)
    gate    : (B, N, d_gate)   — the feedback source, broadcast onto Q/K/V per token
    """

    def __init__(self, d_model: int, n_heads: int, d_gate: int, drop: float,
                 mode: str = "film") -> None:
        super().__init__()
        assert d_model % n_heads == 0, "d_model must be divisible by n_heads"
        assert mode in ("film", "add")
        self.d_model, self.n_heads, self.dh = d_model, n_heads, d_model // n_heads
        self.mode = mode

        # content (bottom-up) projections
        self.W_CQ = nn.Linear(d_model, d_model)
        self.W_CK = nn.Linear(d_model, d_model)
        self.W_CV = nn.Linear(d_model, d_model)
        # gate (feedback) projections — ZERO-init so feedback is OFF at init:
        #   film: (1 + 0) = 1  →  Q = W_CQ(content)        (plain self-attention)
        #   add : (   + 0)     →  Q = W_CQ(content)        (plain self-attention)
        self.W_GQ = nn.Linear(d_gate, d_model)
        self.W_GK = nn.Linear(d_gate, d_model)
        self.W_GV = nn.Linear(d_gate, d_model)
        for m in (self.W_GQ, self.W_GK, self.W_GV):
            nn.init.zeros_(m.weight)
            nn.init.zeros_(m.bias)

        self.W_o = nn.Linear(d_model, d_model)
        self.norm_q = nn.LayerNorm(d_model)            # Q,K normed before the softmax
        self.norm_k = nn.LayerNorm(d_model)            #   (both modes)
        # straight-broadcast: also norm V (unbounded additive injection); FiLM: identity
        self.norm_v = nn.LayerNorm(d_model) if mode == "add" else nn.Identity()
        self.norm_ff = nn.LayerNorm(d_model)
        self.ffn = nn.Sequential(
            nn.Linear(d_model, 4 * d_model), nn.GELU(), nn.Dropout(drop),
            nn.Linear(4 * d_model, d_model),
        )
        self.drop = nn.Dropout(drop)

    def _heads(self, x: torch.Tensor) -> torch.Tensor:   # (B,N,d) -> (B,H,N,dh)
        B, N, _ = x.shape
        return x.view(B, N, self.n_heads, self.dh).transpose(1, 2)

    def _gate(self, content_proj: torch.Tensor, gate_proj: torch.Tensor) -> torch.Tensor:
        if self.mode == "film":
            return content_proj * (1.0 + gate_proj)      # multiplicative FiLM feedback
        return content_proj + gate_proj                   # additive (straight) broadcast

    def forward(self, content: torch.Tensor, gate: torch.Tensor, residual: torch.Tensor,
                return_attn: bool = False):
        Q = self._gate(self.W_CQ(content), self.W_GQ(gate))
        K = self._gate(self.W_CK(content), self.W_GK(gate))
        V = self._gate(self.W_CV(content), self.W_GV(gate))
        Q = self.norm_q(Q)                                # normalize after the injection,
        K = self.norm_k(K)                                #   before the broadcast softmax
        V = self.norm_v(V)                                # add-mode only (else identity)

        qh, kh, vh = self._heads(Q), self._heads(K), self._heads(V)
        scores = torch.matmul(qh, kh.transpose(-2, -1)) / (self.dh ** 0.5)
        aw = torch.softmax(scores, dim=-1)
        out = torch.matmul(aw, vh).transpose(1, 2).contiguous().view(content.shape)
        Z = residual + self.drop(self.W_o(out))
        Z = Z + self.ffn(self.norm_ff(Z))
        return Z, (aw if return_attn else None)


class BroadcastEncoder(nn.Module):
    """v11_part2 split dual-stream + cross-talk, with broadcast self-attention in place
    of cross-attention. Same constructor / state / forward_step contract as
    `CrossTalkEncoder`, so it is a drop-in encoder. `mode` selects FiLM vs straight."""

    def __init__(self, n_tokens: int, d_model: int = 128, d_mem: int = 128,
                 n_heads: int = 1, tx_layers: int = 1, n_lstm: int = 2,
                 drop: float = 0.1, mode: str = "film") -> None:
        super().__init__()
        if d_model != d_mem:
            raise ValueError(f"d_model ({d_model}) must equal d_mem ({d_mem}).")
        if int(n_lstm) != 2:
            raise ValueError("dual-stream needs exactly n_lstm=2 (H1 sensory, H2 deep).")
        if mode not in ("film", "add"):
            raise ValueError(f"mode must be 'film' or 'add', got {mode!r}")
        self.n_tokens = n_tokens
        self.d_model, self.d_mem = d_model, d_mem
        self.n_heads = n_heads
        self.n_lstm = 2
        self.mode = mode
        self.stream_dim = d_model                          # split readout: one stream per head

        # μ: content=X (d_model), gate=[H1‖H2] (2·d_mem), residual=X → actor
        self.mu_block = _BroadcastBlock(d_model, n_heads, d_gate=2 * d_mem, drop=drop, mode=mode)
        # q: content=H2 (d_model), gate=X (d_model), residual=H2 → critic
        self.q_block = _BroadcastBlock(d_model, n_heads, d_gate=d_model, drop=drop, mode=mode)

        self.cell1 = nn.LSTMCell(d_model, d_mem)           # H1 ← X
        self.cell2 = nn.LSTMCell(d_model, d_mem)           # H2 ← Z_μ
        self.cells = nn.ModuleList([self.cell1, self.cell2])
        self.H0 = nn.ParameterList([nn.Parameter(torch.zeros(1, n_tokens, d_mem)) for _ in range(2)])
        self.C0 = nn.ParameterList([nn.Parameter(torch.zeros(1, n_tokens, d_mem)) for _ in range(2)])

    def init_states(self, batch_size: int, device=None, dtype=torch.float32) -> State:
        Hs = [h.to(device=device, dtype=dtype).expand(batch_size, -1, -1).contiguous() for h in self.H0]
        Cs = [c.to(device=device, dtype=dtype).expand(batch_size, -1, -1).contiguous() for c in self.C0]
        return Hs, Cs

    def forward_step(self, tokens: torch.Tensor, prev_state: State,
                     return_attn: bool = False, attn_clamp: Optional[Dict[int, float]] = None):
        # attn_clamp accepted for signature parity with crosstalk (unused: broadcast is
        # self-attention, so the causal-clamp analysis hook does not apply here).
        Hs, Cs = list(prev_state[0]), list(prev_state[1])
        B, N = tokens.shape[0], self.n_tokens
        H1, H2 = Hs[0], Hs[1]
        C1, C2 = Cs[0], Cs[1]
        X = tokens

        mu_gate = torch.cat([H1, H2], dim=-1)              # (B, N, 2·d_mem) — feature-concat gate
        Z_mu, aw_mu = self.mu_block(content=X, gate=mu_gate, residual=X, return_attn=return_attn)
        Z_q, aw_q = self.q_block(content=H2, gate=X, residual=H2, return_attn=return_attn)

        h1, c1 = self.cell1(X.reshape(B * N, self.d_model),
                            (H1.reshape(B * N, self.d_mem), C1.reshape(B * N, self.d_mem)))
        h2, c2 = self.cell2(Z_mu.reshape(B * N, self.d_model),
                            (H2.reshape(B * N, self.d_mem), C2.reshape(B * N, self.d_mem)))
        new_Hs = [h1.view(B, N, self.d_mem), h2.view(B, N, self.d_mem)]
        new_Cs = [c1.view(B, N, self.d_mem), c2.view(B, N, self.d_mem)]

        rec = [Z_mu, Z_q]                                  # Z_μ → actor, Z_q → critic (split)
        if return_attn:
            return (new_Hs, new_Cs), rec, [aw_mu, aw_q]
        return (new_Hs, new_Cs), rec
