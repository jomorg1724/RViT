"""
Encoder for RViT+ v12_part2 — an ADAPTIVE codebook with an energetic maintenance
cost. Builds on v12 (a static learnable value codebook read by soft attention)
by letting the agent SPEND ENERGY to deform the codebook toward the current
environment — but the codebook always DECAYS back to the static learned table,
and maintaining a deformation is penalized, so the default behaviour is to fall
back on the static codebook.

Two coupled mechanisms per frame, with the carried key-memory H2 and the carried
codebook deviation D (D_0 = 0 → the codebook starts exactly static):

  (1) ENERGY MODULATION (a transformer that EDITS the codebook).
      The current codebook is the residual stream; the energy is what the
      self-attention block ADDS to it.

          C_in   = C_base + D_{t-1}                  # current codebook = "H1"
          Q      = W_q^E · C_in                      # queries  = the codebook slots
          K = V  = [ X ‖ H2_{t-1} ]                  # keys/values = image ++ key-memory (2N)
          attn   = softmax(QKᵀ/√d) · V
          h      = C_in + W_o^E · attn               # RESIDUAL = the codebook
          h      = h + FFN^E(h)
          energy = h − C_in                          # net energy the block injected
          D_t    = decay · D_{t-1} + energy          # leaky integrator (→ decays to 0)
          C_t    = C_base + D_t                       # the ADAPTED codebook

      With no energy injected, D decays geometrically and C_t → C_base (static).
      The per-step MAINTENANCE cost mean‖D_t‖² is exposed (last_energy_cost) and
      added to the TRAINING OBJECTIVE with weight energy_coef. This is a penalty
      on the encoder dynamics, NOT a cost in the agent's reward/return: the task
      gradient (which reaches the codebook through the readout output Z) must
      OVERCOME this penalty to justify deforming the codebook, so the model holds
      a deformation only where it improves task performance more than it costs.
      (It is deliberately not folded into the return — the deformation D is an
      internal computation the wait/press action cannot control, so a return cost
      would only push the policy to end episodes early rather than to adapt less.)

  (2) CODEBOOK READOUT (the v12 mechanism, now reading the ADAPTED codebook).

          Q = W_q · X ;  K = W_k · H2_{t-1} ;  V = C_t   (the adapted codebook)
          weights = softmax(QKᵀ/√d) ;  Z = W_o·(weights @ C_t) + FFN
          H2_t = LSTM(X + Z)                          # the only LSTM (keys ← image+readout)
          Z → actor AND critic (rec = [Z])

The image enters by exactly three routes: as the readout queries, as energy
keys/values, and into the H2 update — never as a key/value of the codebook
readout itself. Requires d_model == d_mem and n_lstm == 1.

State note: (Hs, Cs) carries TWO entries — Hs=[H2, D], Cs=[C2, 0]. Only H2 is a
true LSTM state (with cell C2); D is the codebook-deviation integrator (its Cs
slot is an unused zero placeholder kept so len(Hs)==len(Cs)).
"""
from __future__ import annotations

from typing import List, Optional, Tuple

import torch
import torch.nn as nn

# (Hs, Cs): Hs = [H2 (B,N,d_mem), D (B,N,d_mem)]; Cs = [C2 (B,N,d_mem), 0 placeholder].
State = Tuple[List[torch.Tensor], List[torch.Tensor]]


class VQAttnEncoder(nn.Module):
    """Adaptive-codebook encoder: an energy-modulation transformer deforms a
    static learnable codebook (decaying back to it), which a soft-attention
    readout then reads.

    Args
    ----
    n_tokens       : patch tokens AND codebook slots (e.g. 100).
    d_model        : transformer / token width (MUST equal d_mem).
    d_mem          : key-memory / codebook width.
    n_heads        : attention heads in BOTH the energy and readout blocks (default 1).
    tx_layers      : accepted for config parity; fixed at one block each.
    n_lstm         : must be 1 (only the key-memory H2 is a true LSTM state).
    drop           : dropout.
    codebook_decay : λ for the deviation leaky integrator D_t = λ·D_{t-1}+energy.
                     <1 ⇒ the codebook relaxes to the static table without energy.
    temperature    : softmax temperature τ for the readout attention.
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
        codebook_decay: float = 0.9,
        temperature: float = 1.0,
    ) -> None:
        super().__init__()
        if d_model != d_mem:
            raise ValueError(f"d_model ({d_model}) must equal d_mem ({d_mem}).")
        if int(n_lstm) != 1:
            raise ValueError("v12_part2 needs n_lstm=1 (only the key-memory H2 is a true LSTM state).")
        if d_model % n_heads != 0:
            raise ValueError(f"d_model ({d_model}) must be divisible by n_heads ({n_heads}).")
        if not (0.0 <= codebook_decay < 1.0):
            raise ValueError(
                f"codebook_decay must be in [0,1) — the codebook MUST decay back to static; "
                f"got {codebook_decay}. (1.0 = no leak: D never relaxes and ‖D‖² can blow up.)")
        self.n_tokens = n_tokens
        self.d_model, self.d_mem = d_model, d_mem
        self.n_heads = int(n_heads)
        self.head_dim = d_model // self.n_heads
        self.scale = self.head_dim ** -0.5
        self.n_lstm = 1
        self.codebook_decay = float(codebook_decay)
        self.temperature = float(temperature)

        # The STATIC learnable codebook the system decays toward (the resting table).
        self.codebook = nn.Parameter(torch.randn(1, n_tokens, d_mem))

        # Shared spatial identity (codebook slot n ↔ patch n ↔ H2 token n) + a
        # modality tag distinguishing codebook-query / X-key / H2-key.
        self.mem_pos_emb = nn.Parameter(torch.zeros(1, n_tokens, d_model))
        nn.init.normal_(self.mem_pos_emb, std=0.02)
        self.src_emb = nn.Parameter(torch.zeros(3, d_model))   # 0=cb-query, 1=X, 2=H2
        nn.init.normal_(self.src_emb, std=0.02)

        # ── (1) Energy-modulation transformer: Q=codebook, K=V=[X‖H2] ──────────
        self.E_norm_q = nn.LayerNorm(d_model)
        self.E_norm_kv = nn.LayerNorm(d_model)
        self.E_norm_ff = nn.LayerNorm(d_model)
        self.E_W_q = nn.Linear(d_model, d_model)
        self.E_W_k = nn.Linear(d_model, d_model)
        self.E_W_v = nn.Linear(d_model, d_model)
        self.E_W_o = nn.Linear(d_model, d_model)
        self.E_ffn = nn.Sequential(
            nn.Linear(d_model, 4 * d_model), nn.GELU(), nn.Dropout(drop),
            nn.Linear(4 * d_model, d_model),
        )
        self.E_drop = nn.Dropout(drop)
        # Zero-init the energy branch's OUTPUT (W_o + the FFN's last layer) so the
        # block injects NOTHING at init: energy ≡ 0 ⇒ the deviation D starts and
        # STAYS at 0 until the task gradient grows these weights. The model thus
        # begins as the plain static-codebook readout (v12) and deforms the codebook
        # only if adapting earns more reward than the ‖D‖² penalty costs — instead of
        # swamping the codebook with large random deformations at initialization
        # (the standard "residual branch starts as identity" trick).
        nn.init.zeros_(self.E_W_o.weight); nn.init.zeros_(self.E_W_o.bias)
        nn.init.zeros_(self.E_ffn[-1].weight); nn.init.zeros_(self.E_ffn[-1].bias)

        # ── (2) Codebook readout (v12): Q=X, K=H2, V=adapted codebook ─────────
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

        # The single LSTM state: the key-memory H2 ← LSTM(X + Z).
        self.cell = nn.LSTMCell(d_model, d_mem)
        self.cells = nn.ModuleList([self.cell])     # alias for generic grad checks
        self.H0 = nn.ParameterList([nn.Parameter(torch.zeros(1, n_tokens, d_mem))])
        self.C0 = nn.ParameterList([nn.Parameter(torch.zeros(1, n_tokens, d_mem))])

        # Diagnostics (set each forward_step).
        self.last_soft: Optional[torch.Tensor] = None           # readout attention (B,H,N,N)
        self.last_deviation: Optional[torch.Tensor] = None      # D_t (B,N,d)
        self.last_energy_inject: Optional[torch.Tensor] = None  # mean‖energy‖² per item (B,)
        self.last_energy_cost: Optional[torch.Tensor] = None    # mean‖D_t‖² per item (B,) — DIFFERENTIABLE

    def init_states(self, batch_size: int, device=None, dtype=torch.float32) -> State:
        H2 = self.H0[0].to(device=device, dtype=dtype).expand(batch_size, -1, -1).contiguous()
        C2 = self.C0[0].to(device=device, dtype=dtype).expand(batch_size, -1, -1).contiguous()
        D = torch.zeros(batch_size, self.n_tokens, self.d_mem, device=device, dtype=dtype)  # start static
        return [H2, D], [C2, torch.zeros_like(D)]

    def _heads(self, x: torch.Tensor) -> torch.Tensor:
        B, L, _ = x.shape
        return x.view(B, L, self.n_heads, self.head_dim).transpose(1, 2)   # (B,H,L,dh)

    def forward_step(self, tokens: torch.Tensor, prev_state: State, return_attn: bool = False):
        """One frame X: (1) spend energy to deform the codebook (decaying toward
        the static table), then (2) read the adapted codebook to form Z, then
        H2 ← LSTM(X + Z). Returns (new_state, rec[, attn]); rec = [Z]."""
        Hs, Cs = list(prev_state[0]), list(prev_state[1])
        B, N = tokens.shape[0], self.n_tokens
        H2, C2, D_prev = Hs[0], Cs[0], Hs[1]
        X = tokens
        Hh, dh = self.n_heads, self.head_dim
        C_base = self.codebook.expand(B, -1, -1)            # (B,N,d) static table (LIVE)

        # ── (1) Energy modulation — codebook is the residual stream ───────────
        # The energy block treats the static table as a FIXED resting reference
        # (C_base.detach()): the maintenance penalty mean‖D_t‖² must shrink the
        # DEVIATION, not edit the table it decays toward. C_base is learned only
        # through the readout below (the task shapes the resting codebook).
        C_in = C_base.detach() + D_prev                     # current codebook ("H1")
        kv = torch.cat(
            [self.E_norm_kv(X) + self.mem_pos_emb + self.src_emb[1],
             self.E_norm_kv(H2) + self.mem_pos_emb + self.src_emb[2]], dim=1)   # (B,2N,d)
        qE = self.E_W_q(self.E_norm_q(C_in) + self.mem_pos_emb + self.src_emb[0])   # (B,N,d)
        kE, vE = self.E_W_k(kv), self.E_W_v(kv)
        qE, kE, vE = self._heads(qE), self._heads(kE), self._heads(vE)             # (B,H,·,dh)
        aE = torch.softmax(torch.matmul(qE, kE.transpose(-2, -1)) * self.scale, dim=-1)
        eatt = torch.matmul(aE, vE).transpose(1, 2).reshape(B, N, self.d_model)    # (B,N,d)
        h = C_in + self.E_drop(self.E_W_o(eatt))            # residual 1 = the codebook
        h = h + self.E_ffn(self.E_norm_ff(h))               # residual 2
        energy = h - C_in                                   # net energy injected this step
        D_t = self.codebook_decay * D_prev + energy         # leaky integrator (decays to 0)
        C_t = C_base + D_t                                  # the ADAPTED codebook (readout values)

        # ── (2) Codebook readout — soft attention over the ADAPTED codebook ───
        q = self.W_q(self.norm_q(X)) + self.mem_pos_emb     # (B,N,d) queries from X
        k = self.W_k(self.norm_k(H2)) + self.mem_pos_emb    # (B,N,d) keys from H2
        q, k = self._heads(q), self._heads(k)
        v = C_t.view(B, N, Hh, dh).transpose(1, 2)          # (B,H,N,dh) adapted codebook values
        logits = torch.matmul(q, k.transpose(-2, -1)) * self.scale / max(self.temperature, 1e-6)
        soft = torch.softmax(logits, dim=-1)                # (B,H,N,N)
        attn_out = torch.matmul(soft, v).transpose(1, 2).reshape(B, N, self.d_mem)
        a = self.drop(self.W_o(attn_out))                   # (B,N,d) — NO X residual
        Z = a + self.ffn(self.norm_ff(a))

        # ── the only LSTM update: keys H2 ← X + Z ─────────────────────────────
        h2, c2 = self.cell((X + Z).reshape(B * N, self.d_model),
                           (H2.reshape(B * N, self.d_mem), C2.reshape(B * N, self.d_mem)))
        new_H2 = h2.view(B, N, self.d_mem)
        new_C2 = c2.view(B, N, self.d_mem)

        # Diagnostics + the differentiable maintenance cost mean‖D_t‖² per item.
        self.last_soft = soft.detach()
        self.last_deviation = D_t.detach()
        self.last_energy_inject = energy.detach().pow(2).mean(dim=(1, 2))
        self.last_energy_cost = D_t.pow(2).mean(dim=(1, 2))            # (B,) — KEEP grad

        new_state = ([new_H2, D_t], [new_C2, torch.zeros_like(D_t)])
        rec = [Z]                                           # actor AND critic read Z
        if return_attn:
            return new_state, rec, [soft]
        return new_state, rec
