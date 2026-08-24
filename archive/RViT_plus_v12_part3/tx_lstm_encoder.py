"""
Encoder for RViT+ v12_part3 — an EMA codebook written by a GATED IMAGE-CONTENT
STREAM. The codebook C_base is a buffer (no gradient) consolidated by a slow
VQ-VAE-style EMA. What gets written into it comes from a dedicated transformer +
LSTM ("stream 3") that reads the image through its VALUES and gates the write so
it shuts off when no longer needed.

Per frame, three recurrent objects: the readout key-memory H2 (LSTM2), the
write-stream memory H3 (LSTM3), and the EMA codebook C_base (a buffer).

  (1) WRITE STREAM (image content → gated codebook write):
        Q3 = W_q3 · C_base                 # queries from the codebook ("H1")
        K3 = W_k3 · H3_{t-1}               # keys from the write-stream memory
        V3 = W_v3 · X                      # values from the image patches (processed)
        Z3 = W_o3 · softmax(Q3 K3ᵀ/√d) V3 + FFN3
        H3_t = LSTM3(Z3, H3_{t-1})         # the write-stream recurrent state
        gate_t = σ(W_g · H3_t)             # per-element gate (shuts the write off)
        write_t = gate_t ⊙ H3_t
        C_t = C_base + write_t             # "add (gated) H3 to the codebook H1"

  (2) READOUT (the v12 mechanism, over the written codebook C_t):
        Q = W_q · X ;  K = W_k · H2_{t-1} ;  V = C_t
        Z = W_o·(softmax(QKᵀ/√d) @ C_t) + FFN ;  H2_t = LSTM2(X+Z) ;  Z → actor & critic

  (3) CONSOLIDATION (VQ-VAE EMA, trainer-applied, no_grad):
        C_base ← (1−r)·C_base + r·mean(C_t)      = C_base + r·mean(gate⊙H3)
      The EMA target is the WRITTEN codebook C_t (NOT the write alone) — so C_base
      keeps its scale and slowly ACCUMULATES the gated write rather than decaying
      toward the near-zero write when the gate closes.

The gate is the throttle: when it closes, C_t → C_base (relaxation, replacing the
old leaky-integrator decay), so the codebook falls back to its consolidated resting
value once the write is no longer needed. A small (warmed-in) penalty on mean(gate)
is the "energy cost" of writing. The codebook is gradient-grounded through the write
(Z → C_t → write → H3 → LSTM3 → W_v3·X), so perception is reliable from the start —
the property that avoids the always-WAIT collapse. C_base inits at ZERO (built purely
by consolidating the write). Requires d_model == d_mem.

State note: (Hs, Cs) carries TWO LSTM states — Hs=[H2, H3], Cs=[C2, C3].
"""
from __future__ import annotations

from typing import List, Optional, Tuple

import torch
import torch.nn as nn

# (Hs, Cs): Hs = [H2, H3], Cs = [C2, C3], each (B, n_tokens, d_mem).
State = Tuple[List[torch.Tensor], List[torch.Tensor]]


class VQAttnEncoder(nn.Module):
    """EMA codebook (a buffer) written by a gated image-content stream (LSTM3) and
    read by the v12 soft-attention readout (LSTM2).

    Args
    ----
    n_tokens    : patch tokens AND codebook slots (e.g. 100).
    d_model     : transformer / token width (MUST equal d_mem).
    d_mem       : memory / codebook width.
    n_heads     : attention heads in BOTH the write and readout blocks (default 1).
    tx_layers   : accepted for config parity; fixed at one block each.
    n_lstm      : accepted for config parity (the architecture is fixed: LSTM2 + LSTM3).
    drop        : dropout.
    temperature : softmax temperature τ for the readout attention.
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
        temperature: float = 1.0,
    ) -> None:
        super().__init__()
        if d_model != d_mem:
            raise ValueError(f"d_model ({d_model}) must equal d_mem ({d_mem}).")
        if d_model % n_heads != 0:
            raise ValueError(f"d_model ({d_model}) must be divisible by n_heads ({n_heads}).")
        self.n_tokens = n_tokens
        self.d_model, self.d_mem = d_model, d_mem
        self.n_heads = int(n_heads)
        self.head_dim = d_model // self.n_heads
        self.scale = self.head_dim ** -0.5
        self.n_lstm = 1
        self.temperature = float(temperature)

        # The RESTING codebook: a buffer (no gradient), built ONLY by the EMA toward C_t.
        # Inits at ZERO — the codebook is the consolidated gated write, nothing else.
        self.register_buffer("codebook", torch.zeros(1, n_tokens, d_mem))

        # Shared spatial identity (slot n ↔ patch n ↔ memory token n).
        self.mem_pos_emb = nn.Parameter(torch.zeros(1, n_tokens, d_model))
        nn.init.normal_(self.mem_pos_emb, std=0.02)

        # ── (1) Write stream: Q=codebook, K=H3, V=X → Z3 → LSTM3 → gated write ──
        self.W_q3 = nn.Linear(d_model, d_model)   # Q from the codebook
        self.W_k3 = nn.Linear(d_mem, d_model)     # K from H3
        self.W_v3 = nn.Linear(d_model, d_model)   # V from the image X
        self.W_o3 = nn.Linear(d_model, d_model)
        self.norm_q3 = nn.LayerNorm(d_model)
        self.norm_k3 = nn.LayerNorm(d_mem)
        self.norm_v3 = nn.LayerNorm(d_model)
        self.norm_ff3 = nn.LayerNorm(d_model)
        self.ffn3 = nn.Sequential(
            nn.Linear(d_model, 4 * d_model), nn.GELU(), nn.Dropout(drop),
            nn.Linear(4 * d_model, d_model),
        )
        self.drop3 = nn.Dropout(drop)
        self.cell3 = nn.LSTMCell(d_model, d_mem)              # H3 ← LSTM3(Z3)
        # Per-element gate on H3 (b=0 ⇒ gate≈0.5 at init: writes flow early, then the
        # warmed-in mean(gate) penalty + task pressure close it once consolidated).
        self.W_gate = nn.Linear(d_mem, d_mem)
        nn.init.zeros_(self.W_gate.bias)

        # ── (2) Readout (v12): Q=X, K=H2, V=C_t ───────────────────────────────
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
        self.cell2 = nn.LSTMCell(d_model, d_mem)             # H2 ← LSTM2(X+Z)
        self.cells = nn.ModuleList([self.cell2, self.cell3])  # alias for generic grad checks
        self.cell = self.cell2                                # back-compat alias

        # Initial recurrent states (learnable zeros).
        self.H0_2 = nn.Parameter(torch.zeros(1, n_tokens, d_mem))
        self.C0_2 = nn.Parameter(torch.zeros(1, n_tokens, d_mem))
        self.H0_3 = nn.Parameter(torch.zeros(1, n_tokens, d_mem))
        self.C0_3 = nn.Parameter(torch.zeros(1, n_tokens, d_mem))

        # Diagnostics (set each forward_step).
        self.last_soft: Optional[torch.Tensor] = None        # readout attention (B,H,N,N)
        self.last_gate: Optional[torch.Tensor] = None        # gate (B,N,d) DETACHED
        self.last_write: Optional[torch.Tensor] = None       # gate⊙H3 (B,N,d) DETACHED
        self.last_Ct: Optional[torch.Tensor] = None          # C_t (B,N,d) DETACHED — the EMA target
        self.last_gate_cost: Optional[torch.Tensor] = None   # mean(gate) per item (B,) — DIFFERENTIABLE

    def init_states(self, batch_size: int, device=None, dtype=torch.float32) -> State:
        def _z(p):
            return p.to(device=device, dtype=dtype).expand(batch_size, -1, -1).contiguous()
        return [_z(self.H0_2), _z(self.H0_3)], [_z(self.C0_2), _z(self.C0_3)]

    @torch.no_grad()
    def ema_update_codebook(self, mean_target: torch.Tensor, rate: float) -> torch.Tensor:
        """VQ-VAE-style EMA of the codebook TOWARD the written codebook C_t (the EMA
        target is C_t = C_base + gate⊙H3, NOT the write alone):

            C_base ← (1−r)·C_base + r·mean(C_t)   = C_base + r·mean(gate⊙H3)

        Because the target includes C_base, the codebook keeps its scale and ACCUMULATES
        the gated write (rather than decaying toward the near-zero write when the gate
        closes). Returns the increment for logging. No gradient (buffer update)."""
        if rate <= 0.0:
            return torch.zeros_like(self.codebook)
        mt = mean_target
        if mt.dim() == 2:
            mt = mt.unsqueeze(0)
        mt = mt.to(self.codebook.dtype)
        increment = rate * (mt - self.codebook)              # = r·mean(gate⊙H3)
        self.codebook.add_(increment)                        # (1-r)·C_base + r·mean(C_t)
        return increment

    def _heads(self, x: torch.Tensor) -> torch.Tensor:
        B, L, _ = x.shape
        return x.view(B, L, self.n_heads, self.head_dim).transpose(1, 2)   # (B,H,L,dh)

    def forward_step(self, tokens: torch.Tensor, prev_state: State, return_attn: bool = False):
        """One frame X: (1) the write stream produces a gated write added to the
        codebook (C_t = C_base + gate⊙H3), (2) the readout attends over C_t → Z,
        (3) H2 ← LSTM2(X+Z). Returns (new_state, rec[, attn]); rec = [Z]."""
        Hs, Cs = list(prev_state[0]), list(prev_state[1])
        B, N = tokens.shape[0], self.n_tokens
        H2, C2 = Hs[0], Cs[0]
        H3, C3 = Hs[1], Cs[1]
        X = tokens
        Hh, dh = self.n_heads, self.head_dim
        C_base = self.codebook.expand(B, -1, -1)            # (B,N,d) EMA buffer (no grad)

        # ── (1) Write stream — Q=codebook, K=H3, V=X (image content) ──────────
        q3 = self.W_q3(self.norm_q3(C_base.detach())) + self.mem_pos_emb     # (B,N,d) from codebook
        k3 = self.W_k3(self.norm_k3(H3)) + self.mem_pos_emb                  # (B,N,d) from H3 memory
        v3 = self.W_v3(self.norm_v3(X)) + self.mem_pos_emb                   # (B,N,d) from image X
        q3, k3, v3 = self._heads(q3), self._heads(k3), self._heads(v3)       # (B,H,N,dh)
        a3 = torch.softmax(torch.matmul(q3, k3.transpose(-2, -1)) * self.scale, dim=-1)
        z3att = torch.matmul(a3, v3).transpose(1, 2).reshape(B, N, self.d_model)   # (B,N,d)
        o3 = self.drop3(self.W_o3(z3att))
        Z3 = o3 + self.ffn3(self.norm_ff3(o3))              # the write-stream transformer output
        h3, c3 = self.cell3(Z3.reshape(B * N, self.d_model),
                            (H3.reshape(B * N, self.d_mem), C3.reshape(B * N, self.d_mem)))
        new_H3 = h3.view(B, N, self.d_mem)
        new_C3 = c3.view(B, N, self.d_mem)
        gate = torch.sigmoid(self.W_gate(new_H3))           # (B,N,d) per-element gate
        write = gate * Z3                                # the gated write
        C_t = C_base + write                                # add (gated) H3 to the codebook

        # ── (2) Readout — soft attention over the written codebook C_t ────────
        q = self.W_q(self.norm_q(X)) + self.mem_pos_emb     # (B,N,d) queries from X
        k = self.W_k(self.norm_k(H2)) + self.mem_pos_emb    # (B,N,d) keys from H2
        q, k = self._heads(q), self._heads(k)
        v = C_t.view(B, N, Hh, dh).transpose(1, 2)          # (B,H,N,dh) written codebook values
        logits = torch.matmul(q, k.transpose(-2, -1)) * self.scale / max(self.temperature, 1e-6)
        soft = torch.softmax(logits, dim=-1)                # (B,H,N,N)
        attn_out = torch.matmul(soft, v).transpose(1, 2).reshape(B, N, self.d_mem)
        a = self.drop(self.W_o(attn_out))                   # (B,N,d) — NO X residual
        Z = a + self.ffn(self.norm_ff(a))

        # ── (3) Readout key-memory update: H2 ← LSTM2(X + Z) ──────────────────
        h2, c2 = self.cell2((X + Z).reshape(B * N, self.d_model),
                            (H2.reshape(B * N, self.d_mem), C2.reshape(B * N, self.d_mem)))
        new_H2 = h2.view(B, N, self.d_mem)
        new_C2 = c2.view(B, N, self.d_mem)

        # Diagnostics + the differentiable gate ("energy") cost.
        self.last_soft = soft.detach()
        self.last_gate = gate.detach()
        self.last_write = write.detach()
        self.last_Ct = C_t.detach()                         # (B,N,d) — the EMA target
        self.last_gate_cost = gate.mean(dim=(1, 2))         # (B,) — KEEP grad

        new_state = ([new_H2, new_H3], [new_C2, new_C3])
        rec = [Z]                                           # actor AND critic read Z
        if return_attn:
            return new_state, rec, [soft]
        return new_state, rec
