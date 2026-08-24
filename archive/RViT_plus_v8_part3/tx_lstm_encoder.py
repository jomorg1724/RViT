"""
Encoder for RViT+ v8_part3: v8's H1-residual cross-attention block + stacked
per-token LSTMs, re-engineered so the per-frame-rewritten memory store becomes an
EXPLICIT PREDICTIVE COMPARATOR. v8's attention topology is kept verbatim; three
changes are layered on:

  1. PREDICTIVE-COMPARATOR WRITE GATE (the headline). A tiny per-token forward
     model predicts the current attention output from the carried deep memory:
         p_t = W_pred · H2_{t-1}                     (predictor, side-car)
         e_t = Z_t − p_t                             (per-token "surprise")
     A self-supervised loss ‖Z_t.detach() − p_t‖² (returned as `last_aux`) trains
     W_pred to be an honest forward model — reward-independent, so it learns even
     when RL is saturated. The DETACHED surprise magnitude drives a learnable
     write-gate that modulates ONLY the deep-memory (LSTM2) input:
         g_t = σ(gate_scale · mean‖e_t‖² + gate_bias)        # per token, in (0,1)
         inp_to_LSTM2 = (1 + g_t) · H1_t
     gate_scale init 0 + gate_bias init −4 ⇒ g≈0 ⇒ EXACTLY v8 at init (the (1+g)
     strict-generalization pattern). When a grating tilts, e_t spikes at the
     changed quadrant, opens g_t, and rewrites the evolving codebook H2 harder
     there — making "change = a localized rewrite of the evolving store" a built-in,
     observable circuit instead of an emergent LSTM-gate side-effect. The predictor
     reads a DETACHED H2 and the gate uses a DETACHED surprise, so the comparator
     is a pure side-car: it cannot corrupt the main pathway; RL only tunes how
     strongly surprise opens the gate. The evolving codebook is LEVERAGED, never
     frozen (no VQ, no fixed codebook).

  2. LEARNABLE-GAIN H1 RESIDUAL. v8's block-0 residual `Z = H1_prev + attn` carries
     the carried memory at a FIXED amplitude (≈1/7 of the attention output) the
     model cannot tune. Here `Z = h1_res_gain · H1_prev + attn`, h1_res_gain init
     1.0 ⇒ exact v8 at init, but training can now weight the top-down memory prior.

  3. (readout, in decoder.py / model.py) the heads read H1 ‖ H2, not just H2.

Everything else is v8 verbatim: Q = W_q·X; K = V = [X ++ H1 ++ H2] (memory tagged +
shared positional embedding); the 2 stacked per-token LSTMs; the (Hs, Cs)
State/forward_step contract (so PER state storage / burn-in / carry are untouched).
Requires d_model == d_mem and exactly n_lstm == 2 (H1 = sensory, H2 = deep/codebook).
"""
from __future__ import annotations

from typing import List, Optional, Tuple

import torch
import torch.nn as nn

# A recurrent state: (Hs, Cs) with Hs/Cs per-LSTM lists of (B, n_tokens, d_mem).
State = Tuple[List[torch.Tensor], List[torch.Tensor]]


class _CrossAttnBlock(nn.Module):
    """Pre-norm cross-attention block (v8's): queries are the patch tokens X;
    keys/values are [X ++ memory]; the residual tensor is supplied by the caller
    (block 0: the gained prev-frame H1), so X's content reaches the output only
    through the attention values."""

    def __init__(self, d_model: int, n_heads: int, drop: float) -> None:
        super().__init__()
        self.attn = nn.MultiheadAttention(d_model, n_heads, dropout=drop, batch_first=True)
        self.norm_q = nn.LayerNorm(d_model)
        self.norm_kv = nn.LayerNorm(d_model)
        self.norm_ff = nn.LayerNorm(d_model)
        self.ffn = nn.Sequential(
            nn.Linear(d_model, 4 * d_model), nn.GELU(), nn.Dropout(drop),
            nn.Linear(4 * d_model, d_model),
        )
        self.drop = nn.Dropout(drop)

    def forward(self, X: torch.Tensor, mem_kv: torch.Tensor,
                residual: torch.Tensor, return_attn: bool = False):
        kv = self.norm_kv(torch.cat([X, mem_kv], dim=1))        # (B, (1+n_lstm)·N, d)
        a, aw = self.attn(self.norm_q(X), kv, kv,
                          need_weights=return_attn, average_attn_weights=False)
        Z = residual + self.drop(a)
        Z = Z + self.ffn(self.norm_ff(Z))
        return Z, aw                                            # aw: (B, heads, N, (1+n_lstm)·N) or None


class ComparatorEncoder(nn.Module):
    """v8 cross-attention-over-memory + 2 per-token LSTMs + a predictive-comparator
    write gate on the deep memory and a learnable-gain H1 residual.

    Args
    ----
    n_tokens : number of patch tokens (e.g. 100 for a 10×10 grid).
    d_model  : transformer / token width (MUST equal d_mem).
    d_mem    : LSTM hidden width (= one recurrent-state's width).
    n_heads  : attention heads (default 8).
    tx_layers: cross-attention blocks (default 1).
    n_lstm   : MUST be 2 (H1 = sensory memory, H2 = deep/codebook memory).
    drop     : dropout.

    forward_step returns (new_state, rec[, attn]); rec = [H1, H2]. The per-step
    self-supervised predictor loss (B,) is stashed on ``self.last_aux`` (and the
    detached gate / surprise on ``self.last_gate`` / ``self.last_surprise``) so the
    trainer/probes can read them without changing the return contract.
    """

    def __init__(
        self,
        n_tokens: int,
        d_model: int = 128,
        d_mem: int = 128,
        n_heads: int = 8,
        tx_layers: int = 1,
        n_lstm: int = 2,
        drop: float = 0.1,
    ) -> None:
        super().__init__()
        if d_model != d_mem:
            raise ValueError(
                f"d_model ({d_model}) must equal d_mem ({d_mem}): memory is concatenated "
                f"into the d_model token stream as keys/values."
            )
        if int(n_lstm) != 2:
            raise ValueError("v8_part3 comparator needs exactly n_lstm=2 (H1 sensory, H2 deep).")
        self.n_tokens = n_tokens
        self.d_model, self.d_mem = d_model, d_mem
        self.n_heads, self.tx_layers, self.n_lstm = n_heads, max(1, int(tx_layers)), 2

        self.blocks = nn.ModuleList(
            [_CrossAttnBlock(d_model, n_heads, drop) for _ in range(self.tx_layers)]
        )
        self.mem_tag = nn.Parameter(torch.zeros(self.n_lstm, 1, d_model))
        nn.init.normal_(self.mem_tag, std=0.02)
        self.mem_pos_emb = nn.Parameter(torch.zeros(1, n_tokens, d_model))
        nn.init.normal_(self.mem_pos_emb, std=0.02)

        self.cells = nn.ModuleList(
            [nn.LSTMCell(d_model if i == 0 else d_mem, d_mem) for i in range(self.n_lstm)]
        )
        self.H0 = nn.ParameterList(
            [nn.Parameter(torch.zeros(1, n_tokens, d_mem)) for _ in range(self.n_lstm)]
        )
        self.C0 = nn.ParameterList(
            [nn.Parameter(torch.zeros(1, n_tokens, d_mem)) for _ in range(self.n_lstm)]
        )

        # ── (1) predictive-comparator write gate (side-car) ──────────────────
        self.predictor = nn.Linear(d_mem, d_model)            # p_t = W_pred · H2_{t-1}
        self.gate_scale = nn.Parameter(torch.zeros(1))        # init 0  → g≈0 → exact v8
        self.gate_bias = nn.Parameter(torch.full((1,), -4.0))  # σ(−4)≈0.018
        # ── (2) learnable-gain H1 residual (init 1.0 = exact v8) ─────────────
        self.h1_res_gain = nn.Parameter(torch.ones(1))

        # per-step diagnostics (set each forward_step; not parameters)
        self.last_aux: Optional[torch.Tensor] = None          # (B,) predictor MSE
        self.last_gate: Optional[torch.Tensor] = None         # (B,N,1) detached
        self.last_surprise: Optional[torch.Tensor] = None     # (B,N,1) detached

    def init_states(self, batch_size: int, device=None, dtype=torch.float32) -> State:
        Hs = [h.to(device=device, dtype=dtype).expand(batch_size, -1, -1).contiguous() for h in self.H0]
        Cs = [c.to(device=device, dtype=dtype).expand(batch_size, -1, -1).contiguous() for c in self.C0]
        return Hs, Cs

    def forward_step(self, tokens: torch.Tensor, prev_state: State, return_attn: bool = False):
        """Consume ONE frame; cross-attend over [X ++ carried memories]; predict the
        attention output from the carried deep memory; gate the deep-memory write by
        the prediction-error 'surprise'; advance both per-token LSTMs."""
        Hs, Cs = list(prev_state[0]), list(prev_state[1])
        B, N = tokens.shape[0], self.n_tokens

        mem_kv = torch.cat(
            [Hs[k] + self.mem_pos_emb + self.mem_tag[k] for k in range(self.n_lstm)], dim=1
        )                                                       # (B, n_lstm·N, d_model)

        X = tokens
        attn_per_layer: List[Optional[torch.Tensor]] = []
        for bi, blk in enumerate(self.blocks):
            # block 0: residual = learnable-gain carried H1 (the only path for
            # current-frame visual content is still the attention values).
            res = self.h1_res_gain * Hs[0] if bi == 0 else X
            X, aw = blk(X, mem_kv, residual=res, return_attn=return_attn)
            attn_per_layer.append(aw)
        Z = X                                                   # (B, N, d_model) attention output

        # ── predictive comparator (side-car: predictor reads DETACHED H2) ─────
        p_t = self.predictor(Hs[1].detach())                    # (B, N, d_model) prediction of Z
        aux = (Z.detach() - p_t).pow(2).mean(dim=(1, 2))        # (B,) self-supervised forward-model loss
        surprise = (Z - p_t).detach().pow(2).mean(dim=-1, keepdim=True)   # (B,N,1) detached → no graph leak
        g_t = torch.sigmoid(self.gate_scale * surprise + self.gate_bias)  # (B,N,1) in (0,1)
        self.last_aux, self.last_gate, self.last_surprise = aux, g_t.detach(), surprise

        # ── advance the LSTMs; the DEEP cell's input is comparator-gated ──────
        inp = Z
        for li, cell in enumerate(self.cells):
            if li == self.n_lstm - 1:                           # deep memory (LSTM2): (1+g)·H1
                inp = (1.0 + g_t) * inp
            h, c = cell(
                inp.reshape(B * N, inp.shape[-1]),
                (Hs[li].reshape(B * N, self.d_mem), Cs[li].reshape(B * N, self.d_mem)),
            )
            Hs[li] = h.view(B, N, self.d_mem)
            Cs[li] = c.view(B, N, self.d_mem)
            inp = Hs[li]
        rec = [Hs[li] for li in range(self.n_lstm)]
        if return_attn:
            return (Hs, Cs), rec, attn_per_layer
        return (Hs, Cs), rec
