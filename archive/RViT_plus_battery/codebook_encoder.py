"""
Codebook variant of the FiLM encoder (the SC-microstimulation idea): the values come
from a STATIC learnable codebook (a v12-style lookup table), the queries/keys keep OUR
FiLM gating by the feedback RNN H1, there is NO X-residual, and the single LSTM (H1) is
fed X + Z (the codebook readout), exactly as v12 fed its recurrent state.

Per frame (X = patch tokens, H1 = feedback memory from t-1, codebook = static values):

    Q = W_XQ(X) ⊙ (1 + W_HQ(H1))          # FiLM-gated queries (by H1)   — OUR mechanism
    K = W_XK(X) ⊙ (1 + W_HK(H1))          # FiLM-gated keys   (by H1)
    Q, K ← LayerNorm
    V = codebook                          # the values are the learnable codebook (H2)
    Z = W_o( softmax(QKᵀ/√d) · V ) + FFN  # NO X-residual (v12 codebook module)
    H1 = LSTM(X + Z)                       # the feedback RNN, fed X + the readout Z
    actor, critic  read  Z

TWO HEADS → TWO CODEBOOKS. With n_heads=2 the codebook Parameter (1, N, d) splits into two
per-head sub-tables (1, N, dh); each head attends and reads its own sub-table. The premise
(SC microstimulation) is that the codebook readout STIMULATES the action logits: when a
true signal is present the attention sharpens onto a codebook slot and amplifies the
response — and the two heads can specialise into a POSITIVE (respond) and a NEGATIVE
(withhold) codebook, giving a signed response signal rather than a spatial-only one.
"""
from __future__ import annotations

from typing import Dict, List, Optional, Tuple

import torch
import torch.nn as nn

State = Tuple[List[torch.Tensor], List[torch.Tensor]]


class CodebookFiLMBlock(nn.Module):
    """FiLM-gated (by H1) query/key attention whose values are a static learnable
    codebook; no X-residual."""

    def __init__(self, d_model: int, n_heads: int, d_mem: int, n_tokens: int, drop: float) -> None:
        super().__init__()
        assert d_model % n_heads == 0, "d_model must divide n_heads"
        self.d_model, self.n_heads, self.dh = d_model, n_heads, d_model // n_heads
        self.d_mem, self.n_tokens = d_mem, n_tokens
        self.scale = self.dh ** -0.5
        # queries/keys: bottom-up from X, FiLM-gated by the feedback memory H1
        self.W_XQ = nn.Linear(d_model, d_model)
        self.W_XK = nn.Linear(d_model, d_model)
        self.W_HQ = nn.Linear(d_mem, d_model)
        self.W_HK = nn.Linear(d_mem, d_model)
        for m in (self.W_HQ, self.W_HK):                 # zero-init ⇒ feedback off at init
            nn.init.zeros_(m.weight); nn.init.zeros_(m.bias)
        # the VALUE CODEBOOK: static learnable table of N slots (split across heads = "two
        # codebooks" when n_heads=2). Width d_mem; reshaped to (1, H, N, dh) at read time.
        self.codebook = nn.Parameter(torch.randn(1, n_tokens, d_mem))
        self.W_o = nn.Linear(d_mem, d_model)             # recombine head readouts (no residual)
        self.norm_q = nn.LayerNorm(d_model)
        self.norm_k = nn.LayerNorm(d_model)
        self.norm_ff = nn.LayerNorm(d_model)
        self.ffn = nn.Sequential(
            nn.Linear(d_model, 4 * d_model), nn.GELU(), nn.Dropout(drop),
            nn.Linear(4 * d_model, d_model),
        )
        self.drop = nn.Dropout(drop)

    def _heads(self, x: torch.Tensor) -> torch.Tensor:   # (B,N,d) -> (B,H,N,dh)
        B, N, _ = x.shape
        return x.view(B, N, self.n_heads, self.dh).transpose(1, 2)

    def forward(
        self,
        X: torch.Tensor,
        H1: torch.Tensor,
        return_attn: bool = False,
        attn_clamp: Optional[Dict[int, float]] = None,
    ) -> Tuple[torch.Tensor, Optional[torch.Tensor]]:
        B, N, _ = X.shape
        Q = self.W_XQ(X) * (1.0 + self.W_HQ(H1))         # FiLM gate on queries (by H1)
        K = self.W_XK(X) * (1.0 + self.W_HK(H1))         # FiLM gate on keys
        Q = self.norm_q(Q); K = self.norm_k(K)
        qh, kh = self._heads(Q), self._heads(K)
        vh = self.codebook.view(1, N, self.n_heads, self.dh).transpose(1, 2)   # (1,H,N,dh)
        logits = torch.matmul(qh, kh.transpose(-2, -1)) * self.scale           # (B,H,N,N)
        aw = torch.softmax(logits, dim=-1)
        if attn_clamp:
            aw = aw.clone()
            for j, val in attn_clamp.items():
                aw[..., j] = float(val)
            aw = aw / aw.sum(dim=-1, keepdim=True).clamp_min(1e-8)
        av = torch.matmul(aw, vh)                         # (B,H,N,dh) — codebook readout
        av = av.transpose(1, 2).contiguous().view(B, N, self.d_mem)
        a = self.drop(self.W_o(av))                       # NO X-residual
        Z = a + self.ffn(self.norm_ff(a))
        return Z, (aw if return_attn else None)


class CodebookV12Block(nn.Module):
    """v12-faithful codebook attention — NO FiLM. Q from the image X, K from the
    recurrent key-memory H2, V = a static learnable codebook; no X-residual."""

    def __init__(self, d_model: int, n_heads: int, d_mem: int, n_tokens: int, drop: float) -> None:
        super().__init__()
        assert d_model % n_heads == 0, "d_model must divide n_heads"
        self.d_model, self.n_heads, self.dh = d_model, n_heads, d_model // n_heads
        self.d_mem, self.n_tokens = d_mem, n_tokens
        self.scale = self.dh ** -0.5
        self.W_q = nn.Linear(d_model, d_model)            # queries from X
        self.W_k = nn.Linear(d_mem, d_model)              # keys from the recurrent memory H2
        self.W_o = nn.Linear(d_mem, d_model)              # recombine head readouts (no residual)
        self.codebook = nn.Parameter(torch.randn(1, n_tokens, d_mem))   # static values
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

    def _heads(self, x: torch.Tensor) -> torch.Tensor:
        B, N, _ = x.shape
        return x.view(B, N, self.n_heads, self.dh).transpose(1, 2)

    def forward(self, X, H2, return_attn=False, attn_clamp=None):
        B, N, _ = X.shape
        q = self.W_q(self.norm_q(X)) + self.mem_pos_emb   # Q = Q(X)
        k = self.W_k(self.norm_k(H2)) + self.mem_pos_emb  # K = K(H2)
        qh, kh = self._heads(q), self._heads(k)
        vh = self.codebook.view(1, N, self.n_heads, self.dh).transpose(1, 2)
        logits = torch.matmul(qh, kh.transpose(-2, -1)) * self.scale
        aw = torch.softmax(logits, dim=-1)
        if attn_clamp:
            aw = aw.clone()
            for j, val in attn_clamp.items():
                aw[..., j] = float(val)
            aw = aw / aw.sum(dim=-1, keepdim=True).clamp_min(1e-8)
        av = torch.matmul(aw, vh).transpose(1, 2).contiguous().view(B, N, self.d_mem)
        a = self.drop(self.W_o(av))                       # NO X-residual
        Z = a + self.ffn(self.norm_ff(a))
        return Z, (aw if return_attn else None)


class CodebookV12Encoder(nn.Module):
    """v12-faithful: Q(X) / K(H2) / V=codebook, no FiLM, no residual; the single LSTM is
    the KEY-memory H2 ← LSTM(X+Z). Same forward_step contract as the others."""

    def __init__(self, n_tokens, d_model=128, d_mem=128, n_heads=2, tx_layers=1,
                 n_lstm=1, drop=0.1, readout="Z") -> None:
        super().__init__()
        if d_model != d_mem:
            raise ValueError(f"d_model ({d_model}) must equal d_mem ({d_mem}).")
        if readout not in ("Z", "H2"):
            raise ValueError("readout must be 'Z' or 'H2'")
        self.n_tokens = n_tokens
        self.d_model, self.d_mem = d_model, d_mem
        self.n_heads = n_heads
        self.n_lstm = 1
        self.readout = readout
        self.stream_dim = d_model
        self.block = CodebookV12Block(d_model, n_heads, d_mem=d_mem, n_tokens=n_tokens, drop=drop)
        self.cell = nn.LSTMCell(d_model, d_mem)           # H2 (key-memory) ← LSTM(X + Z)
        self.cells = nn.ModuleList([self.cell])
        self.H0 = nn.ParameterList([nn.Parameter(torch.zeros(1, n_tokens, d_mem))])
        self.C0 = nn.ParameterList([nn.Parameter(torch.zeros(1, n_tokens, d_mem))])

    def init_states(self, batch_size, device=None, dtype=torch.float32) -> State:
        Hs = [h.to(device=device, dtype=dtype).expand(batch_size, -1, -1).contiguous() for h in self.H0]
        Cs = [c.to(device=device, dtype=dtype).expand(batch_size, -1, -1).contiguous() for c in self.C0]
        return Hs, Cs

    def forward_step(self, tokens, prev_state, return_attn=False, attn_clamp=None):
        Hs, Cs = list(prev_state[0]), list(prev_state[1])
        B, N = tokens.shape[0], self.n_tokens
        X = tokens
        H2_prev, C2 = Hs[0], Cs[0]
        Z, aw = self.block(X, H2_prev, return_attn=return_attn, attn_clamp=attn_clamp)
        h2, c2 = self.cell((X + Z).reshape(B * N, self.d_model),
                           (H2_prev.reshape(B * N, self.d_mem), C2.reshape(B * N, self.d_mem)))
        new_Hs = [h2.view(B, N, self.d_mem)]
        new_Cs = [c2.view(B, N, self.d_mem)]
        rec = [new_Hs[0]] if self.readout == "H2" else [Z]
        if return_attn:
            return (new_Hs, new_Cs), rec, [aw]
        return (new_Hs, new_Cs), rec


class CodebookFiLMEncoder(nn.Module):
    """One codebook-FiLM block + ONE feedback LSTM (H1 ← LSTM(X+Z)). Same constructor /
    state / forward_step contract as the other encoders so the harness is reused."""

    def __init__(
        self,
        n_tokens: int,
        d_model: int = 128,
        d_mem: int = 128,
        n_heads: int = 2,          # two heads → two codebooks (positive / negative)
        tx_layers: int = 1,
        n_lstm: int = 1,           # only the feedback RNN H1 is recurrent
        drop: float = 0.1,
        readout: str = "Z",        # heads read Z (codebook readout); "H1" exposes the RNN
    ) -> None:
        super().__init__()
        if d_model != d_mem:
            raise ValueError(f"d_model ({d_model}) must equal d_mem ({d_mem}).")
        if readout not in ("Z", "H1"):
            raise ValueError("readout must be 'Z' or 'H1'")
        self.n_tokens = n_tokens
        self.d_model, self.d_mem = d_model, d_mem
        self.n_heads = n_heads
        self.n_lstm = 1
        self.readout = readout
        self.stream_dim = d_model

        self.block = CodebookFiLMBlock(d_model, n_heads, d_mem=d_mem, n_tokens=n_tokens, drop=drop)
        self.cell = nn.LSTMCell(d_model, d_mem)           # H1 ← LSTM(X + Z)
        self.cells = nn.ModuleList([self.cell])
        self.H0 = nn.ParameterList([nn.Parameter(torch.zeros(1, n_tokens, d_mem))])
        self.C0 = nn.ParameterList([nn.Parameter(torch.zeros(1, n_tokens, d_mem))])

    def init_states(self, batch_size: int, device=None, dtype=torch.float32) -> State:
        Hs = [h.to(device=device, dtype=dtype).expand(batch_size, -1, -1).contiguous() for h in self.H0]
        Cs = [c.to(device=device, dtype=dtype).expand(batch_size, -1, -1).contiguous() for c in self.C0]
        return Hs, Cs

    def forward_step(
        self,
        tokens: torch.Tensor,
        prev_state: State,
        return_attn: bool = False,
        attn_clamp: Optional[Dict[int, float]] = None,
    ):
        Hs, Cs = list(prev_state[0]), list(prev_state[1])
        B, N = tokens.shape[0], self.n_tokens
        X = tokens
        H1_prev, C1 = Hs[0], Cs[0]
        Z, aw = self.block(X, H1_prev, return_attn=return_attn, attn_clamp=attn_clamp)
        # the only recurrent update: H1 ← LSTM(X + Z)  (v12-style feeding)
        h1, c1 = self.cell((X + Z).reshape(B * N, self.d_model),
                           (H1_prev.reshape(B * N, self.d_mem), C1.reshape(B * N, self.d_mem)))
        new_Hs = [h1.view(B, N, self.d_mem)]
        new_Cs = [c1.view(B, N, self.d_mem)]
        rec = [new_Hs[0]] if self.readout == "H1" else [Z]
        if return_attn:
            return (new_Hs, new_Cs), rec, [aw]
        return (new_Hs, new_Cs), rec
