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
    N = F⊙N_prev + I       C = λ(C_prev⊙F) + U⊙I           H = O ⊙ (C / N)
  λ is the explicit carried-cell retention factor (`memory_decay`, default 1.0). It leaks only
  content carried from the prior frame; the current write U⊙I is not immediately attenuated.
  W_x ∈ ℝ^{140×1024}, R_x ∈ ℝ^{1024×1024} (the paper's R∈ℝ^{140×1024} is a typo — H is
  1024-wide, so the recurrent map must be 1024×1024). Gate inputs carry a bias on the
  W_x term (standard LSTM convention; the paper drops biases in notation), R_x bias-free.
  H,C,N,M are each (B,4,1024); pre-initial C,N,M = 0 (⇒ H_0 = O⊙U, well-defined).
"""
from __future__ import annotations

from typing import List, Tuple

import torch
import torch.nn as nn

# Recurrent state is cell-dependent: xLSTM carries (H,C,N,M), while the
# layer-normalized decay cell carries only (H,C).
State = Tuple[torch.Tensor, ...]

N_PATCH = 4
D_TOKEN = 140
D_MEM = 1024


def fsq_quantize(x: torch.Tensor, levels: int = 2) -> torch.Tensor:
    """Finite Scalar Quantization with straight-through estimator.

    Each coordinate is clamped to [0, 1], scaled to [0, L-1], rounded to the
    nearest integer level, and scaled back.  The rounding is non-differentiable,
    so the gradient is replaced by the identity (straight-through estimator):

        forward:  q(x) = round(clamp(x) * (L-1)) / (L-1)
        backward: dq/dx = I  (identity for ALL x)

    NOTE: the standard FSQ STE passes identity gradient everywhere, including
    saturated values (x outside [0,1]), so a saturated unit can still receive
    gradient and move back toward a quantization boundary. The previous
    clamp-aware variant zeroed the gradient for ~91% of units, which blocked
    the memory from learning subtle content like the orientation change.

    With ``levels=1`` the function is a no-op passthrough.
    """
    if levels < 1:
        raise ValueError(f"fsq levels must be >= 1, got {levels}")
    if levels == 1:
        return x
    scale = float(levels - 1)
    quantized = torch.round(x.clamp(0.0, 1.0) * scale) / scale
    # Standard STE: forward = quantized, backward = identity for ALL x.
    return x + (quantized - x).detach()


class RMSNorm(nn.Module):
    """Feature-wise RMS normalization for PyTorch versions without nn.RMSNorm."""

    def __init__(self, d: int, eps: float = 1e-6) -> None:
        super().__init__()
        self.weight = nn.Parameter(torch.ones(d))
        self.eps = float(eps)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        scale = torch.rsqrt(x.float().square().mean(dim=-1, keepdim=True) + self.eps)
        return (x.float() * scale).to(dtype=x.dtype) * self.weight


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
        K = torch.cat([self.W_kx(X), self.W_kh(H1_prev)], dim=1)         # (B,2N,d): keys 0..N-1 IMAGE, N..2N-1 MEMORY
        V = torch.cat([self.W_vx(X), self.W_vh(H1_prev)], dim=1)         # (B,2N,d)
        scores = torch.matmul(Q, K.transpose(-1, -2)) * self.scale       # (B,N,2N)
        if attn_clamp:                                                   # causal: additively bias key j (0..3 image, 4..7 memory)
            scores = scores.clone()
            for j, bias in attn_clamp.items():
                scores[..., int(j)] = scores[..., int(j)] + float(bias)
        aw = torch.softmax(scores, dim=-1)                               # (B,N,2N) over the 8 keys
        Z = X + torch.matmul(aw, V)                                      # (B,N,d), residual X
        return (Z, aw) if return_attn else (Z, None)


class ModernCrossAttentionXH(CrossAttentionXH):
    """Source-normalized QK-normalized visual-to-memory cross-attention."""

    def __init__(self, d_token: int = D_TOKEN, d_mem: int = D_MEM) -> None:
        super().__init__(d_token=d_token, d_mem=d_mem)
        self.visual_norm = RMSNorm(d_token)
        self.memory_norm = RMSNorm(d_mem)
        self.query_key_norm = True

    @staticmethod
    def _rms_norm(x: torch.Tensor, eps: float = 1e-6) -> torch.Tensor:
        return x * torch.rsqrt(x.square().mean(dim=-1, keepdim=True) + eps)

    def forward(self, X, H1_prev, return_attn: bool = False, attn_clamp=None):
        X_norm = self.visual_norm(X)
        H_norm = self.memory_norm(H1_prev)
        Q = self._rms_norm(self.W_q(X_norm))
        K = self._rms_norm(torch.cat([self.W_kx(X_norm), self.W_kh(H_norm)], dim=1))
        V = torch.cat([self.W_vx(X_norm), self.W_vh(H_norm)], dim=1)
        scores = torch.matmul(Q, K.transpose(-1, -2)) * self.scale
        if attn_clamp:
            scores = scores.clone()
            for j, bias in attn_clamp.items():
                scores[..., int(j)] = scores[..., int(j)] + float(bias)
        aw = torch.softmax(scores, dim=-1)
        Z = X + torch.matmul(aw, V)
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


class ElementwiseAffineSelfAttention(nn.Module):
    """ELEMENT-WISE affine modulation by the feedback memory, then standard self-attention.
    Two VECTORS per patch, both computed from H (NO identity / no `1+` term — the scale is
    parameterised directly, per the user's spec):

        b   = tanh(bottleneck(H))
        γ   = scale(b)      ∈ ℝ^{d}      (element-wise SCALE; bias-init 1 ⇒ γ=1 at start)
        β   = broadcast(b)  ∈ ℝ^{d}      (element-wise SHIFT/broadcast; zero-init ⇒ β=0 at start)
        X'  = γ ⊙ X + β                  (element-wise affine — NO matrix, NO identity residual)
        Q,K,V = W_XQ/K/V(X') ;  Z = X + softmax(QKᵀ/√d)·V

    Differs from FiLM (scale-only, `(1+γ)`) by adding an element-wise shift β AND dropping the
    `1+` identity; differs from `affine` (a full d×d scale MATRIX) by being diagonal/element-wise.
    INIT: γ→1, β→0 ⇒ X'=X ⇒ plain self-attention at start (alive). A zero-init scale would give
    X'≈0 → dead attention (the multiplicative-death mode); γ is free to learn toward 0 thereafter."""
    def __init__(self, d_token: int = D_TOKEN, d_mem: int = D_MEM, d_hyper: int = 64) -> None:
        super().__init__()
        self.bottleneck = nn.Linear(d_mem, d_hyper)
        self.gen_scale = nn.Linear(d_hyper, d_token)             # γ (element-wise scale)
        self.gen_shift = nn.Linear(d_hyper, d_token)             # β (element-wise broadcast/shift)
        nn.init.zeros_(self.gen_scale.weight); nn.init.ones_(self.gen_scale.bias)   # γ=1 at init (no `1+` term)
        nn.init.zeros_(self.gen_shift.weight); nn.init.zeros_(self.gen_shift.bias)  # β=0 at init
        self.W_XQ = nn.Linear(d_token, d_token, bias=False)
        self.W_XK = nn.Linear(d_token, d_token, bias=False)
        self.W_XV = nn.Linear(d_token, d_token, bias=False)
        self.attn_scale = d_token ** -0.5

    def forward(self, X: torch.Tensor, H_prev: torch.Tensor, return_attn: bool = False,
                attn_clamp=None):
        b = torch.tanh(self.bottleneck(H_prev))
        gamma = self.gen_scale(b)                                # (B,N,d) element-wise scale
        beta = self.gen_shift(b)                                 # (B,N,d) element-wise shift
        Xp = gamma * X + beta                                    # γ⊙X + β  (NO identity)
        Q, K, V = self.W_XQ(Xp), self.W_XK(Xp), self.W_XV(Xp)
        scores = torch.matmul(Q, K.transpose(-1, -2)) * self.attn_scale
        if attn_clamp:                                           # causal: bias attention to patch j
            scores = scores.clone()
            for j, bias in attn_clamp.items():
                scores[..., int(j)] = scores[..., int(j)] + float(bias)
        aw = torch.softmax(scores, dim=-1)
        Z = X + torch.matmul(aw, V)                             # X-residual (paper structure)
        return (Z, aw) if return_attn else (Z, None)


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


class CrossAttentionTransformerMemory(nn.Module):
    """One H-only transformer memory block with joint memory/visual cross-attention.

    For each memory slot, queries come only from the previous hidden state while
    keys and values share one softmax over the previous memory followed by the
    current visual-transformer output::

        Q = W_q(H_prev)
        K = [W_kh(H_prev) | W_kz(Z)]
        V = [W_vh(H_prev) | W_vz(Z)]
        H = TransformerBlock(H_prev, attention(Q, K, V))

    The first N key columns are memory and the last N are visual. Because both
    sources compete under one normalization, the block can route entirely through
    memory and ignore the current visual input when that is useful.
    """

    def __init__(self, d_token: int = D_TOKEN, d_mem: int = D_MEM,
                 n_heads: int = 4, dropout: float = 0.0) -> None:
        super().__init__()
        if n_heads <= 0 or d_mem % n_heads != 0:
            raise ValueError(
                f"d_mem must be divisible by a positive n_heads, got {d_mem} and {n_heads}"
            )
        self.d_mem = int(d_mem)
        self.n_heads = int(n_heads)
        self.head_dim = self.d_mem // self.n_heads
        self.scale = self.head_dim ** -0.5

        self.W_q = nn.Linear(d_mem, d_mem, bias=False)
        self.W_kh = nn.Linear(d_mem, d_mem, bias=False)
        self.W_kz = nn.Linear(d_token, d_mem, bias=False)
        self.W_vh = nn.Linear(d_mem, d_mem, bias=False)
        self.W_vz = nn.Linear(d_token, d_mem, bias=False)
        self.W_o = nn.Linear(d_mem, d_mem, bias=False)
        self.attn_dropout = nn.Dropout(dropout)
        self.resid_dropout = nn.Dropout(dropout)
        self.norm1 = nn.LayerNorm(d_mem)
        self.norm2 = nn.LayerNorm(d_mem)
        self.ffn = nn.Sequential(
            nn.Linear(d_mem, 4 * d_mem),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(4 * d_mem, d_mem),
        )

    def _split_heads(self, x: torch.Tensor) -> torch.Tensor:
        B, L, _ = x.shape
        return x.reshape(B, L, self.n_heads, self.head_dim).transpose(1, 2)

    def _merge_heads(self, x: torch.Tensor) -> torch.Tensor:
        B, _heads, L, _dim = x.shape
        return x.transpose(1, 2).contiguous().reshape(B, L, self.d_mem)

    def forward(self, Z: torch.Tensor, H_prev: torch.Tensor,
                return_attn: bool = False):
        Q = self._split_heads(self.W_q(H_prev))
        K = self._split_heads(torch.cat([self.W_kh(H_prev), self.W_kz(Z)], dim=1))
        V = self._split_heads(torch.cat([self.W_vh(H_prev), self.W_vz(Z)], dim=1))
        attention = torch.softmax(torch.matmul(Q, K.transpose(-1, -2)) * self.scale, dim=-1)
        context = torch.matmul(self.attn_dropout(attention), V)
        attended = self.W_o(self._merge_heads(context))
        H_attn = self.norm1(H_prev + self.resid_dropout(attended))
        H_new = self.norm2(H_attn + self.resid_dropout(self.ffn(H_attn)))
        return H_new, (attention if return_attn else None)


class ModernCrossAttentionTransformerMemory(CrossAttentionTransformerMemory):
    """Normalized, gated variant that preserves the joint memory/source softmax.

    Source-specific RMSNorms put simplex memory and dense incoming tokens on
    comparable scales before all projections. Q/K are additionally normalized
    per head. A query-dependent elementwise sigmoid gate modulates each SDPA
    head output before head merging, without changing the inspectable attention
    probabilities.
    """

    def __init__(self, d_token: int = D_TOKEN, d_mem: int = D_MEM,
                 n_heads: int = 4, dropout: float = 0.0) -> None:
        super().__init__(d_token=d_token, d_mem=d_mem, n_heads=n_heads, dropout=dropout)
        self.query_norm = RMSNorm(d_mem)
        self.source_norm = RMSNorm(d_token)
        self.query_key_norm = True
        self.W_g = nn.Linear(d_mem, d_mem, bias=False)
        self.last_gate: torch.Tensor | None = None
        self.last_source_contribution: torch.Tensor | None = None

    @staticmethod
    def _head_rms_norm(x: torch.Tensor, eps: float = 1e-6) -> torch.Tensor:
        return x * torch.rsqrt(x.square().mean(dim=-1, keepdim=True) + eps)

    def forward(self, Z: torch.Tensor, H_prev: torch.Tensor,
                return_attn: bool = False):
        H_norm = self.query_norm(H_prev)
        Z_norm = self.source_norm(Z)
        Q = self._head_rms_norm(self._split_heads(self.W_q(H_norm)))
        K_h = self._split_heads(self.W_kh(H_norm))
        K_z = self._split_heads(self.W_kz(Z_norm))
        K = self._head_rms_norm(torch.cat([K_h, K_z], dim=2))
        V_h = self._split_heads(self.W_vh(H_norm))
        V_z = self._split_heads(self.W_vz(Z_norm))
        V = torch.cat([V_h, V_z], dim=2)

        attention = torch.softmax(torch.matmul(Q, K.transpose(-1, -2)) * self.scale, dim=-1)
        context = torch.matmul(self.attn_dropout(attention), V)
        gate = torch.sigmoid(self._split_heads(self.W_g(H_norm)))
        gated_context = gate * context
        attended = self.W_o(self._merge_heads(gated_context))
        H_attn = self.norm1(H_prev + self.resid_dropout(attended))
        H_new = self.norm2(H_attn + self.resid_dropout(self.ffn(H_attn)))

        if return_attn:
            n_memory = H_prev.shape[1]
            memory_context = torch.matmul(attention[..., :n_memory], V_h)
            source_context = torch.matmul(attention[..., n_memory:], V_z)
            self.last_gate = gate
            self.last_source_contribution = torch.stack(
                ((gate * memory_context).norm(dim=-1),
                 (gate * source_context).norm(dim=-1)),
                dim=-1,
            )
        else:
            self.last_gate = None
            self.last_source_contribution = None
        return H_new, (attention if return_attn else None)


class PredictiveMemoryTransformer(nn.Module):
    """Third memory layer: self-attention over the concatenated [H1, H2] memory that
    predicts the NEXT [H1_hat, H2_hat].

    This is the association/predictive layer: it learns the memory's transition
    dynamics directly (Q=K=V=[H1,H2] -> [H1_hat,H2_hat]). It has NO JEPA
    (softmax-distillation) targets — it is trained by direct next-state prediction,
    so a change naturally shows up as a break in predictability. Pre-LN with residuals.
    """

    def __init__(self, d_mem: int = D_MEM, n_heads: int = 4, dropout: float = 0.0) -> None:
        super().__init__()
        if n_heads <= 0 or d_mem % n_heads != 0:
            raise ValueError(f"d_mem must be divisible by a positive n_heads, got {d_mem} and {n_heads}")
        self.d_mem = int(d_mem)
        self.n_heads = int(n_heads)
        self.head_dim = self.d_mem // self.n_heads
        self.scale = self.head_dim ** -0.5
        self.W_q = nn.Linear(d_mem, d_mem, bias=False)
        self.W_k = nn.Linear(d_mem, d_mem, bias=False)
        self.W_v = nn.Linear(d_mem, d_mem, bias=False)
        self.W_o = nn.Linear(d_mem, d_mem, bias=False)
        self.attn_dropout = nn.Dropout(dropout)
        self.resid_dropout = nn.Dropout(dropout)
        self.norm1 = nn.LayerNorm(d_mem)
        self.norm2 = nn.LayerNorm(d_mem)
        self.ffn = nn.Sequential(
            nn.Linear(d_mem, 4 * d_mem), nn.GELU(), nn.Dropout(dropout),
            nn.Linear(4 * d_mem, d_mem),
        )

    def _split_heads(self, x: torch.Tensor) -> torch.Tensor:
        B, L, _ = x.shape
        return x.reshape(B, L, self.n_heads, self.head_dim).transpose(1, 2)

    def _merge_heads(self, x: torch.Tensor) -> torch.Tensor:
        B, _h, L, _d = x.shape
        return x.transpose(1, 2).contiguous().reshape(B, L, self.d_mem)

    def forward(self, H1: torch.Tensor, H2: torch.Tensor):
        x = torch.cat([H1, H2], dim=1)                       # (B, 2N, d_mem)
        Q = self._split_heads(self.W_q(x))
        K = self._split_heads(self.W_k(x))
        V = self._split_heads(self.W_v(x))
        attention = torch.softmax(torch.matmul(Q, K.transpose(-1, -2)) * self.scale, dim=-1)
        context = torch.matmul(self.attn_dropout(attention), V)
        attended = self.W_o(self._merge_heads(context))
        x_attn = self.norm1(x + self.resid_dropout(attended))
        x_new = self.norm2(x_attn + self.resid_dropout(self.ffn(x_attn)))
        n_tokens = H1.shape[1]
        return x_new[:, :n_tokens], x_new[:, n_tokens:]       # (H1_hat, H2_hat)


class SpatialXLSTM(nn.Module):
    def __init__(self, input_dim: int = D_TOKEN, d_mem: int = D_MEM,
                 memory_decay: float = 1.0, memory_noise_std: float = 0.0) -> None:
        super().__init__()
        if not 0.0 <= float(memory_decay) <= 1.0:
            raise ValueError(f"memory_decay must be in [0, 1], got {memory_decay}")
        if not 0.0 <= float(memory_noise_std) < float("inf"):
            raise ValueError(
                f"memory_noise_std must be finite and non-negative, got {memory_noise_std}"
            )
        self.memory_decay = float(memory_decay)
        self.memory_noise_std = float(memory_noise_std)
        self.W_i = nn.Linear(input_dim, d_mem, bias=True)
        self.W_f = nn.Linear(input_dim, d_mem, bias=True)
        self.W_o = nn.Linear(input_dim, d_mem, bias=True)
        self.W_u = nn.Linear(input_dim, d_mem, bias=True)
        self.R_i = nn.Linear(d_mem, d_mem, bias=False)
        self.R_f = nn.Linear(d_mem, d_mem, bias=False)
        self.R_o = nn.Linear(d_mem, d_mem, bias=False)
        self.R_z = nn.Linear(d_mem, d_mem, bias=False)

    def forward(self, Z, H_prev, C_prev, N_prev, M_prev,
                inject_memory_noise: bool = False):
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
        # Leak only previously stored cell content; a representation written at this step is
        # not attenuated immediately. memory_decay=1 preserves the original xLSTM equation.
        C = self.memory_decay * (C_prev * F) + U * I
        # Scale noise by the same normalizer used in H so memory_noise_std is expressed in
        # normalized C/N units and cannot explode when N is close to zero. The perturbed C is
        # carried to the next step.
        if inject_memory_noise and self.memory_noise_std > 0.0:
            C = C + self.memory_noise_std * (N + 1e-8) * torch.randn_like(C)
        H = O * (C / (N + 1e-8))                                 # eps for numerical safety
        return H, C, N, M


class LayerNormDecayLSTM(nn.Module):
    """An H/C-only recurrent cell with explicit carried-memory decay.

    This variant deliberately removes the xLSTM normalizer and stabilizer states
    ``N`` and ``M``.  It uses bounded LSTM gates, applies the requested decay only
    to content carried from the previous physical step, and exposes a
    layer-normalized cell state to the recurrent hidden state::

        I = sigmoid(W_i Z + R_i H_prev)
        F = sigmoid(W_f Z + R_f H_prev)
        O = sigmoid(W_o Z + R_o H_prev)
        U = tanh(W_u Z + R_z H_prev)
        C = memory_decay * (F * C_prev) + I * U
        H = O * tanh(LayerNorm(C))

    Memory noise, when enabled, is scaled by C's instantaneous LayerNorm
    denominator before being carried.  Thus ``memory_noise_std`` remains in
    normalized-state units without introducing a recurrent normalization state.
    """

    def __init__(self, input_dim: int = D_TOKEN, d_mem: int = D_MEM,
                 memory_decay: float = 1.0, memory_noise_std: float = 0.0) -> None:
        super().__init__()
        if not 0.0 <= float(memory_decay) <= 1.0:
            raise ValueError(f"memory_decay must be in [0, 1], got {memory_decay}")
        if not 0.0 <= float(memory_noise_std) < float("inf"):
            raise ValueError(
                f"memory_noise_std must be finite and non-negative, got {memory_noise_std}"
            )
        self.memory_decay = float(memory_decay)
        self.memory_noise_std = float(memory_noise_std)
        self.W_i = nn.Linear(input_dim, d_mem, bias=True)
        self.W_f = nn.Linear(input_dim, d_mem, bias=True)
        self.W_o = nn.Linear(input_dim, d_mem, bias=True)
        self.W_u = nn.Linear(input_dim, d_mem, bias=True)
        self.R_i = nn.Linear(d_mem, d_mem, bias=False)
        self.R_f = nn.Linear(d_mem, d_mem, bias=False)
        self.R_o = nn.Linear(d_mem, d_mem, bias=False)
        self.R_z = nn.Linear(d_mem, d_mem, bias=False)
        self.state_norm = nn.LayerNorm(d_mem)

    def forward(self, Z, H_prev, C_prev, inject_memory_noise: bool = False):
        I = torch.sigmoid(self.W_i(Z) + self.R_i(H_prev))
        F = torch.sigmoid(self.W_f(Z) + self.R_f(H_prev))
        O = torch.sigmoid(self.W_o(Z) + self.R_o(H_prev))
        U = torch.tanh(self.W_u(Z) + self.R_z(H_prev))

        C = self.memory_decay * (C_prev * F) + U * I
        if inject_memory_noise and self.memory_noise_std > 0.0:
            state_scale = torch.sqrt(
                C.var(dim=-1, keepdim=True, unbiased=False) + self.state_norm.eps
            )
            C = C + self.memory_noise_std * state_scale * torch.randn_like(C)
        H = O * torch.tanh(self.state_norm(C))
        return H, C


class SoftmaxHeadCell(nn.Module):
    """A stripped LSTM cell that keeps ONLY the cell state C (no H / N / M), splits each patch's
    C into `n_heads` heads, and SOFTMAX-normalises every (patch, head) independently — so C per
    (patch, head) is a categorical distribution over head_dim features. In the extreme case the
    four patches × four heads become 4×4 one-hot vectors (a discrete, structured memory).

    Gates come from the ViT output Z and the prior C (the only recurrence — there is no hidden
    state). Integration is in LOGIT space:  the forget gate scales the prior's log-probabilities
    and the input gate adds a tanh candidate, then a per-head softmax renormalises:

        C ← softmax_head( f ⊙ log(C_prev) + i ⊙ tanh(U) )      (per patch, per head)

    The log(C_prev) is what makes it a real memory: a value-space `f·C_prev + i·U` would be
    swamped by the write (simplex values are ~1/head_dim), so the softmax would be near-memoryless.
    The softmax is the ONLY boundedness — C is always a set of distributions, it cannot explode."""
    def __init__(self, input_dim: int = D_TOKEN, d_mem: int = D_MEM, n_heads: int = 4) -> None:
        super().__init__()
        assert d_mem % n_heads == 0, "d_mem must be divisible by n_heads"
        self.n_heads, self.head_dim, self.d_mem = n_heads, d_mem // n_heads, d_mem
        self.W_i = nn.Linear(input_dim, d_mem, bias=True)        # input gate   ← Z
        self.W_f = nn.Linear(input_dim, d_mem, bias=True)        # forget gate  ← Z
        self.W_u = nn.Linear(input_dim, d_mem, bias=True)        # cell input   ← Z
        self.R_i = nn.Linear(d_mem, d_mem, bias=False)           # recurrence ← prior C (no H)
        self.R_f = nn.Linear(d_mem, d_mem, bias=False)
        self.R_u = nn.Linear(d_mem, d_mem, bias=False)
        nn.init.constant_(self.W_f.bias, 1.0)                    # forget-bias toward RETENTION (f≈0.73 at start)

    def forward(self, Z: torch.Tensor, C_prev: torch.Tensor) -> torch.Tensor:
        B, P, _ = C_prev.shape
        H, D = self.n_heads, self.head_dim
        i = torch.sigmoid(self.W_i(Z) + self.R_i(C_prev))       # input gate   (B,4,1024)
        f = torch.sigmoid(self.W_f(Z) + self.R_f(C_prev))       # forget gate  (B,4,1024)
        u = torch.tanh(self.W_u(Z) + self.R_u(C_prev))          # candidate cell content
        # prior LOGITS = log C_prev, CENTRED per head (removes the log-partition constant). At zero
        # init this term is exactly 0 → the first step is a clean uniform prior driven by i·u, not a
        # forget-gate artifact of the −log(eps) clamp. The forget gate f scales the prior logits.
        lp = torch.log(C_prev.clamp_min(1e-9)).view(B, P, H, D)
        lp = lp - lp.mean(dim=-1, keepdim=True)
        logit = f.view(B, P, H, D) * lp + (i * u).view(B, P, H, D)
        return torch.softmax(logit, dim=-1).reshape(B, P, self.d_mem)   # per-(patch,head) softmax


class RecurrentViTxLSTM(nn.Module):
    """Multiplicative/FiLM-SA ViT plus a selectable recurrent cell.

    ``xlstm`` carries the paper state ``(H,C,N,M)``;
    ``layernorm_lstm`` carries only ``(H,C)`` and normalizes C with
    LayerNorm; ``softmax_head`` carries only its categorical C state.
    """

    def __init__(self, d_token: int = D_TOKEN, d_mem: int = D_MEM, n_patch: int = N_PATCH,
                 feedback: str = "multiplicative", two_lstm: bool = False,
                 cell: str = "xlstm", mem_heads: int = 4,
                 memory_decay: float = 1.0, memory_noise_std: float = 0.0,
                 memory_output_noise_std: float = 0.0) -> None:
        super().__init__()
        self.n_patch, self.d_token, self.d_mem = n_patch, d_token, d_mem
        self.feedback = feedback
        transformer_cells = (
            "transformer_memory",
            "transformer_memory_2layer",
            "transformer_memory_2layer_softmax",
            "transformer_memory_2layer_softmax_modern",
        )
        if cell not in ("xlstm", "layernorm_lstm", "softmax_head", *transformer_cells):
            raise ValueError(
                "cell must be 'xlstm', 'layernorm_lstm', 'softmax_head', or "
                "a transformer-memory variant; "
                f"got {cell!r}"
            )
        self.cell = cell
        self.memory_decay = float(memory_decay)
        self.memory_noise_std = float(memory_noise_std)
        # Independent Gaussian noise on the H1/H2 memory OUTPUTS (post-nonlinearity),
        # injected only when forward_step is called with inject_memory_noise=True.
        # Used for the JEPA-pretrain phase (denoising temporal self-distillation).
        self.memory_output_noise_std = float(memory_output_noise_std)
        self.fsq_levels: int = 1   # 1 = softmax (default); >=2 = FSQ quantization
        if cell in transformer_cells:
            if feedback != "crossattn1":
                raise ValueError(f"{cell} requires feedback='crossattn1'")
            if two_lstm:
                state_description = "single H-only state" if cell == "transformer_memory" else "stacked H-only states"
                raise ValueError(f"{cell} has {state_description}; two_lstm is invalid")
            if self.memory_decay != 1.0:
                raise ValueError(f"{cell} requires memory_decay=1.0")
            if self.memory_noise_std != 0.0:
                raise ValueError(f"{cell} requires memory_noise_std=0.0")
        if cell == "softmax_head" and self.memory_decay != 1.0:
            raise ValueError("memory_decay applies only to cell='xlstm'")
        if cell == "softmax_head" and self.memory_noise_std != 0.0:
            raise ValueError("memory_noise_std applies only to cell='xlstm'")
        if cell in ("softmax_head", *transformer_cells):
            two_lstm = False                                      # this variant uses a single C-only cell
        cross = (feedback == "crossattn")
        dualmem = (feedback == "dualmem")
        cascade = (feedback == "affine_cascade")
        self.two_lstm = two_lstm or cross or dualmem or cascade  # these imply two LSTMs
        self.lstm2_from = "Z" if (cross or dualmem or cascade) else "H1"  # LSTM2 reads Z (140) vs H1 (1024)
        if feedback in ("crossattn", "crossattn1"):
            # SINGLE-LSTM cross-attention (crossattn1): Q=W_q(X), K=[W_kx(X)‖W_kh(H)], V=[W_vx(X)‖W_vh(H)];
            # unlike "crossattn" it does NOT force a 2nd LSTM (cross above stays False) — the one cell's
            # H both feeds the cross-attention AND the readout. Matches the JEPA single-cell instance.
            attn_cls = (
                ModernCrossAttentionXH
                if cell == "transformer_memory_2layer_softmax_modern"
                else CrossAttentionXH
            )
            self.attn = attn_cls(d_token, d_mem)              # Q(X), K=K(X,H), V=V(X,H)
        elif feedback == "dualmem":
            self.attn = DualMemAttention(d_token, d_mem)         # Q([H1‖H2]), K=V=[X‖H1‖H2] → Z1,Z2
        elif feedback == "hyper":
            self.attn = HyperWeightSelfAttention(d_token, d_mem)
        elif feedback == "hyper_codebook":
            self.attn = HyperCodebookSelfAttention(d_token, d_mem, n_patch=n_patch)
        elif feedback == "affine":
            self.attn = AffineModulatedSelfAttention(d_token, d_mem)
        elif feedback == "affine_ew":
            self.attn = ElementwiseAffineSelfAttention(d_token, d_mem)   # γ⊙X+β, element-wise, no identity
        elif feedback == "dualhead":
            self.attn = DualHeadSelfAttention(d_token, d_mem)
        elif feedback == "affine_cascade":
            # two stacked affine-modulated transformers (T1 input X / feedback H1;
            # T2 input Z1 / feedback H2), split readout (actor←H2, critic←H1).
            self.attn = AffineModulatedSelfAttention(d_token, d_mem)    # T1
            self.attn2 = AffineModulatedSelfAttention(d_token, d_mem)   # T2
        else:
            self.attn = MultiplicativeSelfAttention(d_token, d_mem, feedback=feedback)
        if cell == "transformer_memory":
            self.initial_memory = nn.Parameter(torch.empty(1, n_patch, d_mem))
            nn.init.normal_(self.initial_memory, std=0.02)
            self.memory_transformer = CrossAttentionTransformerMemory(
                d_token, d_mem, n_heads=mem_heads
            )
        elif cell in (
            "transformer_memory_2layer",
            "transformer_memory_2layer_softmax",
            "transformer_memory_2layer_softmax_modern",
        ):
            # Slot-distinct learned priors break the otherwise permanent permutation symmetry
            # caused by querying from identical zero memories at the first physical step.
            self.initial_memory1 = nn.Parameter(torch.empty(1, n_patch, d_mem))
            self.initial_memory2 = nn.Parameter(torch.empty(1, n_patch, d_mem))
            nn.init.normal_(self.initial_memory1, std=0.02)
            nn.init.normal_(self.initial_memory2, std=0.02)
            memory_cls = (
                ModernCrossAttentionTransformerMemory
                if cell == "transformer_memory_2layer_softmax_modern"
                else CrossAttentionTransformerMemory
            )
            self.memory_transformer1 = memory_cls(
                d_token, d_mem, n_heads=mem_heads
            )
            self.memory_transformer2 = memory_cls(
                d_mem, d_mem, n_heads=mem_heads
            )
            # Third layer: association/predictive memory (Q=K=V=[H1,H2] -> next [H1_hat,H2_hat]).
            self.predictor = PredictiveMemoryTransformer(d_mem, n_heads=mem_heads)
        elif cell == "softmax_head":
            self.lstm = SoftmaxHeadCell(d_token, d_mem, n_heads=mem_heads)   # C-only, per-head softmax
        elif cell == "layernorm_lstm":
            self.lstm = LayerNormDecayLSTM(
                d_token,
                d_mem,
                memory_decay=self.memory_decay,
                memory_noise_std=self.memory_noise_std,
            )
        else:
            self.lstm = SpatialXLSTM(
                d_token,
                d_mem,
                memory_decay=self.memory_decay,
                memory_noise_std=self.memory_noise_std,
            )  # Z → H1
        if self.two_lstm:
            in2 = d_token if self.lstm2_from == "Z" else d_mem   # LSTM2 reads Z (crossattn) or H1
            cell_cls = LayerNormDecayLSTM if cell == "layernorm_lstm" else SpatialXLSTM
            self.lstm2 = cell_cls(
                in2,
                d_mem,
                memory_decay=self.memory_decay,
                memory_noise_std=self.memory_noise_std,
            )  # → H2
        self.readout_dim = n_patch * d_mem                       # 4096 (flattened readout)

    def _z(self, B, device, dtype):
        return torch.zeros(B, self.n_patch, self.d_mem, device=device, dtype=dtype)

    def init_states(self, batch_size: int, device=None, dtype=torch.float32) -> State:
        z = lambda: self._z(batch_size, device, dtype)
        if self.cell == "transformer_memory":
            H0 = self.initial_memory.to(device=device, dtype=dtype).expand(batch_size, -1, -1)
            return (H0,)                                         # learned, slot-distinct H only
        if self.cell in (
            "transformer_memory_2layer",
            "transformer_memory_2layer_softmax",
            "transformer_memory_2layer_softmax_modern",
        ):
            H10 = self.initial_memory1.to(device=device, dtype=dtype).expand(batch_size, -1, -1)
            H20 = self.initial_memory2.to(device=device, dtype=dtype).expand(batch_size, -1, -1)
            if self.cell in (
                "transformer_memory_2layer_softmax",
                "transformer_memory_2layer_softmax_modern",
            ):
                # Initial-memory parameters are logits in this variant. Every memory token
                # entering a downstream module therefore lies on the feature simplex,
                # including the first physical timestep.
                H10 = torch.softmax(H10, dim=-1)
                H20 = torch.softmax(H20, dim=-1)
            return (H10, H20)                                    # learned, slot-distinct H1/H2
        if self.cell == "softmax_head":
            return (z(),)                                        # C only (zeros → uniform prior via log clamp)
        if self.cell == "layernorm_lstm":
            s1 = (z(), z())                                      # H1, C1; no N/M state
        else:
            s1 = (z(), z(), z(), z())                            # H1, C1, N1, M1
        if self.two_lstm:
            s2 = (z(), z()) if self.cell == "layernorm_lstm" else (z(), z(), z(), z())
            return (s1, s2)                                      # (LSTM1 state, LSTM2 state)
        return s1

    def _run_recurrent_cell(self, module, X, state, *, inject_memory_noise: bool):
        if self.cell == "layernorm_lstm":
            H, C = module(X, *state, inject_memory_noise=inject_memory_noise)
            return (H, C), H
        H, C, N, M = module(X, *state, inject_memory_noise=inject_memory_noise)
        return (H, C, N, M), H

    def forward_step(self, X: torch.Tensor, state, return_attn: bool = False,
                     attn_clamp=None, inject_memory_noise: bool = False):
        # transformer_memory: standard visual crossattn1 produces Z using H_prev feedback;
        # one H-only transformer then queries from H_prev and reads joint [H_prev,Z] keys/values.
        if self.cell == "transformer_memory":
            (H_prev,) = state
            Z, visual_attn = self.attn(
                X, H_prev, return_attn=return_attn, attn_clamp=attn_clamp
            )
            H_new, _memory_attn = self.memory_transformer(
                Z, H_prev, return_attn=return_attn
            )
            return (H_new,), H_new, visual_attn
        # Two-layer transformer memory:
        #   vision Q=X, K/V=[X,H1_prev] -> Z
        #   memory1 Q=H1_prev, K/V=[H1_prev,Z] -> H1
        #   memory2 Q=H2_prev, K/V=[H2_prev,H1] -> H2
        # H1 is the recurrent visual-feedback state; actor and critic read H2.
        if self.cell in (
            "transformer_memory_2layer",
            "transformer_memory_2layer_softmax",
            "transformer_memory_2layer_softmax_modern",
        ):
            H1_prev, H2_prev = state
            Z, visual_attn = self.attn(
                X, H1_prev, return_attn=return_attn, attn_clamp=attn_clamp
            )
            H1, _memory1_attn = self.memory_transformer1(
                Z, H1_prev, return_attn=return_attn
            )
            raw_H1 = H1
            if self.cell in (
                "transformer_memory_2layer_softmax",
                "transformer_memory_2layer_softmax_modern",
            ):
                if self.fsq_levels >= 2:
                    H1 = fsq_quantize(H1, levels=self.fsq_levels)
                else:
                    H1 = torch.softmax(H1, dim=-1)
            if inject_memory_noise and self.memory_output_noise_std > 0.0:
                H1 = H1 + self.memory_output_noise_std * torch.randn_like(H1)
            H2, _memory2_attn = self.memory_transformer2(
                H1, H2_prev, return_attn=return_attn
            )
            raw_H2 = H2
            if self.cell in (
                "transformer_memory_2layer_softmax",
                "transformer_memory_2layer_softmax_modern",
            ):
                if self.fsq_levels >= 2:
                    H2 = fsq_quantize(H2, levels=self.fsq_levels)
                else:
                    H2 = torch.softmax(H2, dim=-1)
            if inject_memory_noise and self.memory_output_noise_std > 0.0:
                H2 = H2 + self.memory_output_noise_std * torch.randn_like(H2)
            self._last_raw_memory = (raw_H1, raw_H2)
            # Association/predictive layer: predict the next memory state from the current one.
            H1_hat, H2_hat = self.predictor(H1, H2)
            self._last_prediction = (H1_hat, H2_hat)
            if self.cell == "transformer_memory_2layer_softmax_modern" and return_attn:
                self.last_memory_attn = torch.stack(
                    (_memory1_attn, _memory2_attn), dim=1
                )
                self.last_memory_gate = torch.stack(
                    (self.memory_transformer1.last_gate,
                     self.memory_transformer2.last_gate),
                    dim=1,
                )
                self.last_memory_source_contribution = torch.stack(
                    (self.memory_transformer1.last_source_contribution,
                     self.memory_transformer2.last_source_contribution),
                    dim=1,
                )
            else:
                self.last_memory_attn = None
                self.last_memory_gate = None
                self.last_memory_source_contribution = None
            return (H1, H2), H2, visual_attn
        # softmax_head: a SINGLE C-only cell. The recurrent memory C (a per-head distribution)
        # both feeds the multiplicative attention AND is the readout; no H/N/M.
        if self.cell == "softmax_head":
            (C_prev,) = state
            if isinstance(self.attn, MultiplicativeSelfAttention):
                Z, attn = self.attn(X, C_prev, return_attn=return_attn, attn_clamp=attn_clamp)
            else:
                Z, attn = self.attn(X, C_prev, return_attn=return_attn)
            C1 = self.lstm(Z, C_prev)                                        # C ← softmax-head cell
            return (C1,), C1, attn                                           # heads read C
        # dualmem: Q from [H1‖H2], K/V from [X‖H1‖H2], output split Z1/Z2 → update H1/H2 separately
        if self.feedback == "dualmem":
            s1, s2 = state
            Z1, Z2, attn = self.attn(X, s1[0], s2[0], return_attn=return_attn)
            s1_next, H1 = self._run_recurrent_cell(
                self.lstm, Z1, s1, inject_memory_noise=inject_memory_noise
            )
            s2_next, H2 = self._run_recurrent_cell(
                self.lstm2, Z2, s2, inject_memory_noise=inject_memory_noise
            )
            return (s1_next, s2_next), H2, attn                               # heads read H2
        # affine_cascade: T1(X, fb=H1)→Z1→H1 ; T2(Z1, fb=H2)→Z2→H2 ; actor←H2, critic←H1
        if self.feedback == "affine_cascade":
            s1, s2 = state
            H1p, H2p = s1[0], s2[0]
            c1 = attn_clamp.get("t1") if isinstance(attn_clamp, dict) else None   # causal levers
            c2 = attn_clamp.get("t2") if isinstance(attn_clamp, dict) else None
            Z1, aw1 = self.attn(X, H1p, return_attn=return_attn, attn_clamp=c1)   # T1: input X, feedback H1
            s1_next, H1 = self._run_recurrent_cell(
                self.lstm, Z1, s1, inject_memory_noise=inject_memory_noise
            )                                                                # H1 ← LSTM1(Z1)
            Z2, aw2 = self.attn2(Z1, H2p, return_attn=return_attn, attn_clamp=c2) # T2: input Z1, feedback H2
            s2_next, H2 = self._run_recurrent_cell(
                self.lstm2, Z2, s2, inject_memory_noise=inject_memory_noise
            )                                                                # H2 ← LSTM2(Z2)
            attn = [aw1, aw2] if return_attn else None
            return (s1_next, s2_next), (H2, H1), attn                         # actor←H2, critic←H1
        # the attention is fed by LSTM1's H1 (the feedback memory); the heads read the readout
        if self.two_lstm:
            s1, s2 = state
            H_prev = s1[0]
        else:
            s1 = state
            H_prev = s1[0]
        # forward attn_clamp to every attention that ACCEPTS + APPLIES it (multiplicative/FiLM, matrix
        # affine, element-wise affine) so causal-perturbation maps actually bias the target patch and
        # never silently no-op. Modules that don't apply a clamp take the plain call.
        if isinstance(self.attn, (MultiplicativeSelfAttention, AffineModulatedSelfAttention,
                                  ElementwiseAffineSelfAttention, CrossAttentionXH)):
            Z, attn = self.attn(X, H_prev, return_attn=return_attn, attn_clamp=attn_clamp)
        else:
            Z, attn = self.attn(X, H_prev, return_attn=return_attn)
        s1_next, H1 = self._run_recurrent_cell(
            self.lstm, Z, s1, inject_memory_noise=inject_memory_noise
        )                                                                    # LSTM1: Z → H1
        if self.two_lstm:
            lstm2_in = Z if self.lstm2_from == "Z" else H1                   # crossattn: Z; two_lstm: H1
            s2_next, H2 = self._run_recurrent_cell(
                self.lstm2, lstm2_in, s2, inject_memory_noise=inject_memory_noise
            )                                                                # LSTM2 → H2
            return (s1_next, s2_next), H2, attn                               # heads read H2
        return s1_next, H1, attn                                              # heads read H1
