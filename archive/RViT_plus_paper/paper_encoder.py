"""
Recurrent ViT core — EXACTLY the paper's equations (Methods §ViT, §Spatial LSTM).

ViT (multiplicative self-attention over the 4 patch tokens), Eqs (610)–(620):
    Q = (X·W_XQ) ⊙ (H^{t-1}·W_HQ)        K = (X·W_XK) ⊙ (H^{t-1}·W_HK)
    V = (X·W_XV) ⊙ (H^{t-1}·W_HV)
    V_filtered = softmax(Q Kᵀ) · V        (no 1/√d scaling — as written)
    Z = X + V_filtered ∈ ℝ^{4×140}
  W_X· ∈ ℝ^{140×140}, W_H· ∈ ℝ^{1024×140}.  Pure Hadamard gate (no "1+"): with H^0=0
  the gate is 0 ⇒ Z=X at the first frame, and the multiplicative feedback engages as
  memory builds and W_H· train. Projections are bias-free (the paper writes X·W, H·W).

Spatial LSTM — the xLSTM update (Table eq:recurrent_updates), per patch, independent:
    Ĩ = Z·W_i + H·R_i      F̃ = Z·W_f + H·R_f      Õ = Z·W_o + H·R_o      Ũ = Z·W_u + H·R_z
    M = max(F̃ + M_prev, Ĩ)         I = exp(Ĩ − M)         F = exp(F̃ + M_prev − M)
    O = σ(Õ)               U = tanh(Ũ)
    N = F⊙N_prev + I       C = C_prev⊙F + U⊙I             H = O ⊙ (C / N)
  W_x ∈ ℝ^{140×1024}, R_x ∈ ℝ^{1024×1024} (the paper's R∈ℝ^{140×1024} is a typo — H is
  1024-wide, so the recurrent map must be 1024×1024). Gate inputs carry a bias on the
  W_x term (standard LSTM convention; the paper drops biases in notation), R_x bias-free.
  H,C,N,M are each (B,4,1024); pre-initial C,N,M = 0 (⇒ H_0 = O⊙U, well-defined).
"""
from __future__ import annotations

from typing import List, Tuple

import torch
import torch.nn as nn

# State = (H, C, N, M), each (B, n_patch, d_mem)
State = Tuple[torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor]

N_PATCH = 4
D_TOKEN = 140
D_MEM = 1024


class MultiplicativeSelfAttention(nn.Module):
    """feedback ∈ {"multiplicative", "film"} — the ONLY thing that differs between the
    paper's mechanism and the FiLM variant (how the memory feedback is broadcast):
      "multiplicative" (paper): Q = (X·W_XQ) ⊙ (H·W_HQ)        — H=0 ⇒ Q=0 ⇒ Z=X
      "film":                   Q = (X·W_XQ) ⊙ (1 + H·W_HQ)    — feedback-off ⇒ plain
        self-attention over X. W_H· are ZERO-init so (1+0)=1 at init (identity start),
        and the memory learns to MODULATE the sensory attention rather than gate it from 0.
    """
    def __init__(self, d_token: int = D_TOKEN, d_mem: int = D_MEM,
                 feedback: str = "multiplicative") -> None:
        super().__init__()
        if feedback not in ("multiplicative", "film"):
            raise ValueError(f"feedback must be 'multiplicative' or 'film', got {feedback!r}")
        self.feedback = feedback
        self.W_XQ = nn.Linear(d_token, d_token, bias=False)
        self.W_XK = nn.Linear(d_token, d_token, bias=False)
        self.W_XV = nn.Linear(d_token, d_token, bias=False)
        self.W_HQ = nn.Linear(d_mem, d_token, bias=False)
        self.W_HK = nn.Linear(d_mem, d_token, bias=False)
        self.W_HV = nn.Linear(d_mem, d_token, bias=False)
        if feedback == "film":
            # identity-init: (1 + W_H·H) = 1 at init ⇒ block starts as plain self-attention
            for m in (self.W_HQ, self.W_HK, self.W_HV):
                nn.init.zeros_(m.weight)

    def forward(self, X: torch.Tensor, H_prev: torch.Tensor, return_attn: bool = False,
                attn_clamp=None):
        if self.feedback == "film":
            Q = self.W_XQ(X) * (1.0 + self.W_HQ(H_prev))    # FiLM: modulate sensory attention
            K = self.W_XK(X) * (1.0 + self.W_HK(H_prev))
            V = self.W_XV(X) * (1.0 + self.W_HV(H_prev))
        else:
            Q = self.W_XQ(X) * self.W_HQ(H_prev)            # paper: pure Hadamard gate
            K = self.W_XK(X) * self.W_HK(H_prev)
            V = self.W_XV(X) * self.W_HV(H_prev)
        scores = torch.matmul(Q, K.transpose(-1, -2))   # (B,4,4) — no 1/√d (paper)
        if attn_clamp:                                  # causal manipulation: bias attention to patch j
            scores = scores.clone()
            for j, bias in attn_clamp.items():
                scores[..., int(j)] = scores[..., int(j)] + float(bias)
        attn = torch.softmax(scores, dim=-1)
        V_filtered = torch.matmul(attn, V)              # (B,4,140)
        Z = X + V_filtered                              # Eq (620), residual = X
        return (Z, attn) if return_attn else (Z, None)


class DualMemAttention(nn.Module):
    """The 'crazy' dual-memory variant:
        Q = W_q([H1 ‖ H2])                         (2N queries — the MEMORIES do the querying)
        K = [W_kx(X) ‖ W_kh1(H1) ‖ W_kh2(H2)]      V likewise                     (3N keys/values)
        residual = [W_h1(H1)+X ‖ W_h2(H2)+X]       (2N tokens, concat along patch axis)
        Z = residual + softmax(Q Kᵀ/√d)·V          → split into Z1 (first N) and Z2 (last N)
    Z1 updates H1, Z2 updates H2. (H1,H2 are projected to the token dim where they meet X.)"""
    def __init__(self, d_token: int = D_TOKEN, d_mem: int = D_MEM) -> None:
        super().__init__()
        d = d_token
        self.W_q = nn.Linear(d_mem, d, bias=False)
        self.W_kx = nn.Linear(d_token, d, bias=False)
        self.W_kh1 = nn.Linear(d_mem, d, bias=False)
        self.W_kh2 = nn.Linear(d_mem, d, bias=False)
        self.W_vx = nn.Linear(d_token, d, bias=False)
        self.W_vh1 = nn.Linear(d_mem, d, bias=False)
        self.W_vh2 = nn.Linear(d_mem, d, bias=False)
        self.W_h1r = nn.Linear(d_mem, d_token, bias=False)     # H1 → token dim for the residual
        self.W_h2r = nn.Linear(d_mem, d_token, bias=False)
        self.scale = d ** -0.5

    def forward(self, X, H1, H2, return_attn: bool = False):
        Q = self.W_q(torch.cat([H1, H2], dim=1))                            # (B,2N,d)
        K = torch.cat([self.W_kx(X), self.W_kh1(H1), self.W_kh2(H2)], dim=1)  # (B,3N,d)
        V = torch.cat([self.W_vx(X), self.W_vh1(H1), self.W_vh2(H2)], dim=1)  # (B,3N,d)
        aw = torch.softmax(torch.matmul(Q, K.transpose(-1, -2)) * self.scale, dim=-1)  # (B,2N,3N)
        residual = torch.cat([self.W_h1r(H1) + X, self.W_h2r(H2) + X], dim=1)  # (B,2N,d)
        Z = residual + torch.matmul(aw, V)                                  # (B,2N,d)
        N = X.shape[1]
        return Z[:, :N], Z[:, N:], (aw if return_attn else None)            # Z1, Z2


class CrossAttentionXH(nn.Module):
    """Cross-attention (v11_part2 cross-talk): the image queries BOTH itself and feedback memory.
        Q = W_q(X)
        K = [W_kx(X) ‖ W_kh(H1)]        V = [W_vx(X) ‖ W_vh(H1)]      (concatenated along tokens)
        Z = X + softmax(Q Kᵀ/√d) · V                                  (residual = X)
    Q is from X only; K and V draw on both the image X and the feedback memory H1 (2N keys)."""
    def __init__(self, d_token: int = D_TOKEN, d_mem: int = D_MEM) -> None:
        super().__init__()
        self.W_q = nn.Linear(d_token, d_token, bias=False)
        self.W_kx = nn.Linear(d_token, d_token, bias=False)
        self.W_kh = nn.Linear(d_mem, d_token, bias=False)
        self.W_vx = nn.Linear(d_token, d_token, bias=False)
        self.W_vh = nn.Linear(d_mem, d_token, bias=False)
        self.scale = d_token ** -0.5

    def forward(self, X, H1_prev, return_attn: bool = False, attn_clamp=None):
        Q = self.W_q(X)                                                  # (B,N,d)
        K = torch.cat([self.W_kx(X), self.W_kh(H1_prev)], dim=1)         # (B,2N,d)
        V = torch.cat([self.W_vx(X), self.W_vh(H1_prev)], dim=1)         # (B,2N,d)
        aw = torch.softmax(torch.matmul(Q, K.transpose(-1, -2)) * self.scale, dim=-1)   # (B,N,2N)
        Z = X + torch.matmul(aw, V)                                      # (B,N,d), residual X
        return (Z, aw) if return_attn else (Z, None)


class DualHeadSelfAttention(nn.Module):
    """Two parallel heads with DIFFERENT forms, to keep memory from hijacking attention:
       Head A (SENSORY): Q,K,V = W(X) — pure self-attention over the image, NO memory.
                         Can attend the salient cue regardless of memory state.
       Head B (FEEDBACK): Q,K,V = W_X(X) ⊙ W_H(H) — the broadcasting multiplicative form (paper).
       Z = X + W_o([out_A ‖ out_B]).   Returns both maps [aw_sensory, aw_feedback]."""
    def __init__(self, d_token: int = D_TOKEN, d_mem: int = D_MEM) -> None:
        super().__init__()
        self.A_q = nn.Linear(d_token, d_token, bias=False)   # sensory head (X only)
        self.A_k = nn.Linear(d_token, d_token, bias=False)
        self.A_v = nn.Linear(d_token, d_token, bias=False)
        self.B_xq = nn.Linear(d_token, d_token, bias=False)  # feedback head (X ⊙ H)
        self.B_xk = nn.Linear(d_token, d_token, bias=False)
        self.B_xv = nn.Linear(d_token, d_token, bias=False)
        self.B_hq = nn.Linear(d_mem, d_token, bias=False)
        self.B_hk = nn.Linear(d_mem, d_token, bias=False)
        self.B_hv = nn.Linear(d_mem, d_token, bias=False)
        self.W_o = nn.Linear(2 * d_token, d_token)

    def forward(self, X, H_prev, return_attn: bool = False, attn_clamp=None):
        # head A — pure sensory self-attention over X
        aw_a = torch.softmax(torch.matmul(self.A_q(X), self.A_k(X).transpose(-1, -2)), dim=-1)
        out_a = torch.matmul(aw_a, self.A_v(X))
        # head B — multiplicative memory-gated (broadcasting feedback)
        Qb = self.B_xq(X) * self.B_hq(H_prev)
        Kb = self.B_xk(X) * self.B_hk(H_prev)
        Vb = self.B_xv(X) * self.B_hv(H_prev)
        aw_b = torch.softmax(torch.matmul(Qb, Kb.transpose(-1, -2)), dim=-1)
        out_b = torch.matmul(aw_b, Vb)
        Z = X + self.W_o(torch.cat([out_a, out_b], dim=-1))
        return (Z, [aw_a, aw_b]) if return_attn else (Z, None)


class HyperWeightSelfAttention(nn.Module):
    """FAST-WEIGHT / hypernetwork feedback: the memory H GENERATES the Q/K/V projection
    weights that process the visual input, rather than gating its activations.

        W_P^(i) = reshape( G_P( bottleneck(H_i) ) ) ∈ ℝ^{d×d}        (per patch i, P∈{Q,K,V})
        P_i = X_i · W_P^(i)
        V_filtered = softmax(QKᵀ/√d)·V ,   Z = X + V_filtered        (paper's ViT structure)

    "H becomes W_Q, W_K, W_V." A full d×d weight straight from 1024-d H is ~20M params per
    projection, so H passes through a small bottleneck (d_hyper) before being reshaped into
    each weight matrix — the only departure from generating the weights directly from H.
    Generators are small-init so the generated weights (and thus the attention) start near
    zero ⇒ Z≈X at init, then the memory learns the synaptic weights as it trains.
    """
    def __init__(self, d_token: int = D_TOKEN, d_mem: int = D_MEM, d_hyper: int = 64) -> None:
        super().__init__()
        self.d_token = d_token
        self.bottleneck = nn.Linear(d_mem, d_hyper)
        self.gen_q = nn.Linear(d_hyper, d_token * d_token)
        self.gen_k = nn.Linear(d_hyper, d_token * d_token)
        self.gen_v = nn.Linear(d_hyper, d_token * d_token)
        for g in (self.gen_q, self.gen_k, self.gen_v):
            nn.init.normal_(g.weight, std=0.01); nn.init.zeros_(g.bias)
        self.scale = d_token ** -0.5

    def _proj(self, gen, b, X):
        B, N, d = X.shape
        W = gen(b).view(B, N, d, d)                          # per-patch generated weight (B,N,d,d)
        return torch.einsum("bnd,bnde->bne", X, W)           # X_i · W_i → (B,N,d)

    def forward(self, X: torch.Tensor, H_prev: torch.Tensor, return_attn: bool = False):
        b = torch.tanh(self.bottleneck(H_prev))              # (B,N,d_hyper)
        Q, K, V = self._proj(self.gen_q, b, X), self._proj(self.gen_k, b, X), self._proj(self.gen_v, b, X)
        scores = torch.matmul(Q, K.transpose(-1, -2)) * self.scale   # (B,N,N)
        attn = torch.softmax(scores, dim=-1)
        Z = X + torch.matmul(attn, V)                        # residual = X
        return (Z, attn) if return_attn else (Z, None)


class AffineModulatedSelfAttention(nn.Module):
    """Feedback derives a SCALE MATRIX + SHIFT that affinely transform the visual features
    before a standard self-attention — matrix-valued FiLM:

        b      = tanh(bottleneck(H))
        Γ(H)   = I + reshape(G_Γ(b)) ∈ ℝ^{d×d}        (scale matrix; zero-init ⇒ Γ=I at start)
        β(H)   = G_β(b) ∈ ℝ^{d}                       (shift; zero-init ⇒ 0 at start)
        X'     = Γ(H)·X + β(H)                        (per patch — the affine modulation)
        Q,K,V  = W_XQ/K/V(X') ;  Z = X + softmax(QKᵀ/√d)·V

    Generalizes diagonal FiLM (a scale VECTOR) to a full scale MATRIX + shift, derived from
    the recurrent memory. Identity/zero init ⇒ plain self-attention over X at init; the
    memory learns to rotate/scale/shift the visual representation as it trains.
    """
    def __init__(self, d_token: int = D_TOKEN, d_mem: int = D_MEM, d_hyper: int = 64) -> None:
        super().__init__()
        self.d_token = d_token
        self.bottleneck = nn.Linear(d_mem, d_hyper)
        self.gen_scale = nn.Linear(d_hyper, d_token * d_token)    # ΔΓ
        self.gen_shift = nn.Linear(d_hyper, d_token)             # β
        for g in (self.gen_scale, self.gen_shift):               # identity/zero init
            nn.init.zeros_(g.weight); nn.init.zeros_(g.bias)
        self.W_XQ = nn.Linear(d_token, d_token, bias=False)
        self.W_XK = nn.Linear(d_token, d_token, bias=False)
        self.W_XV = nn.Linear(d_token, d_token, bias=False)
        self.attn_scale = d_token ** -0.5
        self.register_buffer("eye", torch.eye(d_token).view(1, 1, d_token, d_token))

    def forward(self, X: torch.Tensor, H_prev: torch.Tensor, return_attn: bool = False,
                return_modulation: bool = False, attn_clamp=None):
        B, N, d = X.shape
        b = torch.tanh(self.bottleneck(H_prev))
        delta_gamma = self.gen_scale(b).view(B, N, d, d)
        beta = self.gen_shift(b)
        Gamma = self.eye + delta_gamma                             # I + ΔΓ (near-identity at init)
        Xp = torch.einsum("bned,bnd->bne", Gamma, X) + beta        # Γ·X + β
        Q, K, V = self.W_XQ(Xp), self.W_XK(Xp), self.W_XV(Xp)
        scores = torch.matmul(Q, K.transpose(-1, -2)) * self.attn_scale
        if attn_clamp:                                            # causal: bias attention to patch j
            scores = scores.clone()
            for j, bias in attn_clamp.items():
                scores[..., int(j)] = scores[..., int(j)] + float(bias)
        aw = torch.softmax(scores, dim=-1)
        Z = X + torch.matmul(aw, V)                              # X-residual (paper structure)
        if return_modulation:
            mod = dict(Xp=Xp, beta=beta, delta_gamma=delta_gamma,
                       gamma_dev=(delta_gamma ** 2).sum(dim=(-2, -1)).sqrt())
            if return_attn:
                return Z, aw, mod
            return Z, None, mod
        return (Z, aw) if return_attn else (Z, None)

    def attention_on(self, tokens: torch.Tensor):
        """Self-attention on arbitrary tokens (counterfactual: unmodulated X)."""
        Q, K, V = self.W_XQ(tokens), self.W_XK(tokens), self.W_XV(tokens)
        aw = torch.softmax(torch.matmul(Q, K.transpose(-1, -2)) * self.attn_scale, dim=-1)
        return aw


class HyperCodebookSelfAttention(nn.Module):
    """Fast-weight feedback (H generates W_Q, W_K) + a CODEBOOK value (V = H_CB), with
    codebook_v12's downstream:

        b   = tanh(bottleneck(H))
        Q_i = X_i · reshape(G_Q(b_i)) ,  K_i = X_i · reshape(G_K(b_i))     (memory IS the weights)
        V   = codebook                       (learnable table, one entry per patch — H_CB)
        aw  = softmax(QKᵀ/√d) ;  av = aw · codebook                        (blend of codes)
        a   = W_o(av) ;  Z = a + FFN(LN(a))                                (NO X-residual, v12-style)

    Memory generates the synaptic weights that read the image and route it onto codebook
    entries; the codebook supplies the values. No W_V — the value comes from the codebook.
    """
    def __init__(self, d_token: int = D_TOKEN, d_mem: int = D_MEM, n_patch: int = N_PATCH,
                 d_hyper: int = 64, drop: float = 0.1) -> None:
        super().__init__()
        self.d_token = d_token
        self.bottleneck = nn.Linear(d_mem, d_hyper)
        self.gen_q = nn.Linear(d_hyper, d_token * d_token)
        self.gen_k = nn.Linear(d_hyper, d_token * d_token)
        for g in (self.gen_q, self.gen_k):
            nn.init.normal_(g.weight, std=0.01); nn.init.zeros_(g.bias)
        self.codebook = nn.Parameter(torch.randn(1, n_patch, d_token) * 0.02)   # V = H_CB
        self.W_o = nn.Linear(d_token, d_token)
        self.norm_ff = nn.LayerNorm(d_token)
        self.ffn = nn.Sequential(
            nn.Linear(d_token, 4 * d_token), nn.GELU(), nn.Dropout(drop),
            nn.Linear(4 * d_token, d_token),
        )
        self.drop = nn.Dropout(drop)
        self.scale = d_token ** -0.5

    def _proj(self, gen, b, X):
        B, N, d = X.shape
        W = gen(b).view(B, N, d, d)
        return torch.einsum("bnd,bnde->bne", X, W)

    def forward(self, X: torch.Tensor, H_prev: torch.Tensor, return_attn: bool = False):
        b = torch.tanh(self.bottleneck(H_prev))
        Q = self._proj(self.gen_q, b, X)
        K = self._proj(self.gen_k, b, X)
        aw = torch.softmax(torch.matmul(Q, K.transpose(-1, -2)) * self.scale, dim=-1)   # (B,N,N)
        V = self.codebook.expand(X.shape[0], -1, -1)                  # (B,N,d) codebook values
        a = self.drop(self.W_o(torch.matmul(aw, V)))                  # codebook blend, no X-residual
        Z = a + self.ffn(self.norm_ff(a))
        return (Z, aw) if return_attn else (Z, None)


class SpatialXLSTM(nn.Module):
    def __init__(self, input_dim: int = D_TOKEN, d_mem: int = D_MEM) -> None:
        super().__init__()
        self.W_i = nn.Linear(input_dim, d_mem, bias=True)
        self.W_f = nn.Linear(input_dim, d_mem, bias=True)
        self.W_o = nn.Linear(input_dim, d_mem, bias=True)
        self.W_u = nn.Linear(input_dim, d_mem, bias=True)
        self.R_i = nn.Linear(d_mem, d_mem, bias=False)
        self.R_f = nn.Linear(d_mem, d_mem, bias=False)
        self.R_o = nn.Linear(d_mem, d_mem, bias=False)
        self.R_z = nn.Linear(d_mem, d_mem, bias=False)

    def forward(self, Z, H_prev, C_prev, N_prev, M_prev):
        I_tilde = self.W_i(Z) + self.R_i(H_prev)
        F_tilde = self.W_f(Z) + self.R_f(H_prev)
        O_tilde = self.W_o(Z) + self.R_o(H_prev)
        U_tilde = self.W_u(Z) + self.R_z(H_prev)

        M = torch.maximum(F_tilde + M_prev, I_tilde)             # stabilizer
        I = torch.exp(I_tilde - M)
        F = torch.exp(F_tilde + M_prev - M)
        O = torch.sigmoid(O_tilde)
        U = torch.tanh(U_tilde)

        N = F * N_prev + I
        C = C_prev * F + U * I
        H = O * (C / (N + 1e-8))                                 # eps for numerical safety
        return H, C, N, M


class RecurrentViTxLSTM(nn.Module):
    """Multiplicative-SA ViT + spatial xLSTM. forward_step carries (H,C,N,M) and returns
    the new memory readout H (B,4,1024); the heads read H flattened to 4096."""

    def __init__(self, d_token: int = D_TOKEN, d_mem: int = D_MEM, n_patch: int = N_PATCH,
                 feedback: str = "multiplicative", two_lstm: bool = False) -> None:
        super().__init__()
        self.n_patch, self.d_token, self.d_mem = n_patch, d_token, d_mem
        self.feedback = feedback
        cross = (feedback == "crossattn")
        dualmem = (feedback == "dualmem")
        cascade = (feedback == "affine_cascade")
        self.two_lstm = two_lstm or cross or dualmem or cascade  # these imply two LSTMs
        self.lstm2_from = "Z" if (cross or dualmem or cascade) else "H1"  # LSTM2 reads Z (140) vs H1 (1024)
        if feedback == "crossattn":
            self.attn = CrossAttentionXH(d_token, d_mem)         # Q(X), K=V=[X‖H1]
        elif feedback == "dualmem":
            self.attn = DualMemAttention(d_token, d_mem)         # Q([H1‖H2]), K=V=[X‖H1‖H2] → Z1,Z2
        elif feedback == "hyper":
            self.attn = HyperWeightSelfAttention(d_token, d_mem)
        elif feedback == "hyper_codebook":
            self.attn = HyperCodebookSelfAttention(d_token, d_mem, n_patch=n_patch)
        elif feedback == "affine":
            self.attn = AffineModulatedSelfAttention(d_token, d_mem)
        elif feedback == "dualhead":
            self.attn = DualHeadSelfAttention(d_token, d_mem)
        elif feedback == "affine_cascade":
            # two stacked affine-modulated transformers (T1 input X / feedback H1;
            # T2 input Z1 / feedback H2), split readout (actor←H2, critic←H1).
            self.attn = AffineModulatedSelfAttention(d_token, d_mem)    # T1
            self.attn2 = AffineModulatedSelfAttention(d_token, d_mem)   # T2
        else:
            self.attn = MultiplicativeSelfAttention(d_token, d_mem, feedback=feedback)
        self.lstm = SpatialXLSTM(d_token, d_mem)                  # LSTM1: Z → H1 (feeds the attention)
        if self.two_lstm:
            in2 = d_token if self.lstm2_from == "Z" else d_mem   # LSTM2 reads Z (crossattn) or H1
            self.lstm2 = SpatialXLSTM(in2, d_mem)                # → H2 (feeds the heads)
        self.readout_dim = n_patch * d_mem                       # 4096 (flattened readout)

    def _z(self, B, device, dtype):
        return torch.zeros(B, self.n_patch, self.d_mem, device=device, dtype=dtype)

    def init_states(self, batch_size: int, device=None, dtype=torch.float32) -> State:
        z = lambda: self._z(batch_size, device, dtype)
        s1 = (z(), z(), z(), z())                                # H1, C1, N1, M1
        if self.two_lstm:
            return (s1, (z(), z(), z(), z()))                    # (LSTM1 state, LSTM2 state)
        return s1

    def forward_step(self, X: torch.Tensor, state: State, return_attn: bool = False,
                     attn_clamp=None):
        # dualmem: Q from [H1‖H2], K/V from [X‖H1‖H2], output split Z1/Z2 → update H1/H2 separately
        if self.feedback == "dualmem":
            s1, s2 = state
            Z1, Z2, attn = self.attn(X, s1[0], s2[0], return_attn=return_attn)
            H1, C1, N1, M1 = self.lstm(Z1, *s1)                              # Z1 → H1
            H2, C2, N2, M2 = self.lstm2(Z2, *s2)                             # Z2 → H2
            return ((H1, C1, N1, M1), (H2, C2, N2, M2)), H2, attn            # heads read H2
        # affine_cascade: T1(X, fb=H1)→Z1→H1 ; T2(Z1, fb=H2)→Z2→H2 ; actor←H2, critic←H1
        if self.feedback == "affine_cascade":
            s1, s2 = state
            H1p, C1, N1, M1 = s1
            H2p, C2, N2, M2 = s2
            c1 = attn_clamp.get("t1") if isinstance(attn_clamp, dict) else None   # causal levers
            c2 = attn_clamp.get("t2") if isinstance(attn_clamp, dict) else None
            Z1, aw1 = self.attn(X, H1p, return_attn=return_attn, attn_clamp=c1)   # T1: input X, feedback H1
            H1, C1, N1, M1 = self.lstm(Z1, H1p, C1, N1, M1)                  # H1 ← LSTM1(Z1)
            Z2, aw2 = self.attn2(Z1, H2p, return_attn=return_attn, attn_clamp=c2) # T2: input Z1, feedback H2
            H2, C2, N2, M2 = self.lstm2(Z2, H2p, C2, N2, M2)                 # H2 ← LSTM2(Z2)
            attn = [aw1, aw2] if return_attn else None
            return ((H1, C1, N1, M1), (H2, C2, N2, M2)), (H2, H1), attn      # actor←H2, critic←H1
        # the attention is fed by LSTM1's H1 (the feedback memory); the heads read the readout
        if self.two_lstm:
            s1, s2 = state
            H_prev, C_prev, N_prev, M_prev = s1
        else:
            H_prev, C_prev, N_prev, M_prev = state
        if isinstance(self.attn, MultiplicativeSelfAttention):                # only this one clamps
            Z, attn = self.attn(X, H_prev, return_attn=return_attn, attn_clamp=attn_clamp)
        else:
            Z, attn = self.attn(X, H_prev, return_attn=return_attn)
        H1, C1, N1, M1 = self.lstm(Z, H_prev, C_prev, N_prev, M_prev)        # LSTM1: Z → H1
        if self.two_lstm:
            lstm2_in = Z if self.lstm2_from == "Z" else H1                   # crossattn: Z; two_lstm: H1
            H2, C2, N2, M2 = self.lstm2(lstm2_in, *s2)                       # LSTM2 → H2
            return ((H1, C1, N1, M1), (H2, C2, N2, M2)), H2, attn            # heads read H2
        return (H1, C1, N1, M1), H1, attn                                    # heads read H1
