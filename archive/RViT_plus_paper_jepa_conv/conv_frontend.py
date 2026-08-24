"""
Conv patch front-end — a CAPABLE-but-small SE-ResNet replacing the paper VAE encoder.

Each 50×50 RGB frame is split into FOUR 25×25 patches in the env's cell order
[TL, TR, BL, BR] (so patch index == cue_index/change_index; S1=TL=0 … S4=BR=3).
A SHARED small CNN encodes each patch to a 128-d embedding ô_i; the token is then
x_i = [ô_i ‖ ρ_i(4) ‖ τ(8)] = 140-d, X = (x_1..x_4) ∈ ℝ^{4×140} — IDENTICAL token
layout to VAEPatchFrontEnd, so it is a drop-in front-end.

CNN (standard small-visual-encoder best practice; NOT a naive conv stack):
  stem 3×3 conv → 3 SE-residual stages (progressive downsample + channel growth)
  → global average pool → RMSNorm (scale-match, colour-DC-preserving) → 128-d. Each stage:
  Conv3×3-GN-SiLU → Conv3×3-GN → Squeeze-Excite (channel attention) → +residual → SiLU.

CHOICES (flagged):
  • 3-channel COLOUR input — the value cue (red/green/blue) must be visible.
  • GroupNorm, NOT BatchNorm: the front-end runs at batch=1 during the recurrent online
    rollout (rl_step), where BN running-stats are fragile; GroupNorm is batch-independent
    and train/eval-identical.
  • Squeeze-Excitation + residual on every stage (per the user's spec).
  • Trained END-TO-END with RL+JEPA (no pretrain, no reconstruction). It replaces the
    from-scratch VAE-shaped encoder that was the perception bottleneck.
"""
from __future__ import annotations

import math

import torch
import torch.nn as nn
import torch.nn.functional as F

N_PATCH = 4
O_FLAT2 = 128                 # per-patch embedding width (matches the paper's o_flat,2)
POS_DIM = 4                   # one-hot over the 4 patch positions
TEMP_DIM = 8                  # one-hot over timestep (T=7 task; 8 slots, t clamped)
TOKEN_DIM = O_FLAT2 + POS_DIM + TEMP_DIM   # = 140 (matches VAEPatchFrontEnd / the paper 4×140)


def _gn(c: int, max_groups: int = 8) -> nn.GroupNorm:
    for cand in (max_groups, 4, 2, 1):
        if c % cand == 0:
            return nn.GroupNorm(cand, c)
    return nn.GroupNorm(1, c)


class RMSNorm(nn.Module):
    """Scale-normalise the embedding WITHOUT mean-subtraction. Used on the pooled patch vector to
    match its scale to the pos/temporal one-hots feeding the ViT, while preserving any constant
    (DC) component — important because the value cue is COLOUR; a mean-subtracting LayerNorm here
    could attenuate a uniform colour offset."""
    def __init__(self, d: int, eps: float = 1e-6) -> None:
        super().__init__()
        self.weight = nn.Parameter(torch.ones(d))
        self.eps = eps

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return x * torch.rsqrt(x.pow(2).mean(-1, keepdim=True) + self.eps) * self.weight


class SqueezeExcite(nn.Module):
    """Channel attention: global-avg-pool (squeeze) → FC↓ → SiLU → FC↑ → sigmoid (excite) → rescale."""
    def __init__(self, c: int, reduction: int = 8) -> None:
        super().__init__()
        h = max(4, c // reduction)
        self.fc1 = nn.Conv2d(c, h, 1)
        self.fc2 = nn.Conv2d(h, c, 1)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        s = x.mean(dim=(2, 3), keepdim=True)          # squeeze
        s = F.silu(self.fc1(s))
        s = torch.sigmoid(self.fc2(s))
        return x * s                                  # excite


class SEResBlock(nn.Module):
    """Conv3×3-GN-SiLU → Conv3×3-GN → SE → + (projected) residual → SiLU."""
    def __init__(self, in_c: int, out_c: int, stride: int = 1, reduction: int = 8) -> None:
        super().__init__()
        self.conv1 = nn.Conv2d(in_c, out_c, 3, stride=stride, padding=1, bias=False)
        self.gn1 = _gn(out_c)
        self.conv2 = nn.Conv2d(out_c, out_c, 3, stride=1, padding=1, bias=False)
        self.gn2 = _gn(out_c)
        self.se = SqueezeExcite(out_c, reduction)
        if stride != 1 or in_c != out_c:
            self.short = nn.Sequential(nn.Conv2d(in_c, out_c, 1, stride=stride, bias=False), _gn(out_c))
        else:
            self.short = nn.Identity()

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        h = F.silu(self.gn1(self.conv1(x)))
        h = self.gn2(self.conv2(h))
        h = self.se(h)
        return F.silu(h + self.short(x))


class ConvMGU(nn.Module):
    """Conv Minimal-Gated-Unit — a SHORT-timescale recurrent cell for the conv front-end ("recurrence
    in the visual cortex"). Simpler than a ConvLSTM/ConvGRU: ONE gate f (retention) that also gates the
    recurrent candidate path, on a conv feature map (C,H,W).

        f    = σ( W_f * x + U_f * H_prev )                 # retention gate (fraction of PAST kept)
        cand = tanh( GN( W_h * x + U_h * (f ⊙ H_prev) ) )  # bounded candidate (|cand|≤1 ⇒ |H|≤1, stable)
        H    = f ⊙ H_prev + (1 - f) ⊙ cand                # leaky integrate

    BIASED DECAY: W_f.bias = logit(retain) (default retain=0.30 ⇒ bias=−0.8473), and the gate CONV
    WEIGHTS are zero-init, so at t=0 f ≡ σ(bias) = retain data-independently — the state is dominated by
    the CURRENT frame with ~one past step integrated (e-fold τ≈0.83 frames at 0.30). The weights leave that
    init the instant gradients arrive, so the cell can LEARN a longer time-constant if the task rewards it."""

    def __init__(self, ch: int, retain: float = 0.3, k: int = 3) -> None:
        super().__init__()
        p = k // 2
        self.W_f = nn.Conv2d(ch, ch, k, padding=p, bias=True)      # gate ← current frame (biased)
        self.U_f = nn.Conv2d(ch, ch, k, padding=p, bias=False)     # gate ← recurrent state
        self.W_h = nn.Conv2d(ch, ch, k, padding=p, bias=True)      # candidate ← current frame
        self.U_h = nn.Conv2d(ch, ch, k, padding=p, bias=False)     # candidate ← reset-gated state
        self.gn = _gn(ch)                                          # GroupNorm on candidate only (batch-1 safe)
        retain = min(max(float(retain), 1e-3), 1 - 1e-3)
        nn.init.constant_(self.W_f.bias, math.log(retain / (1 - retain)))   # f→retain at init
        nn.init.zeros_(self.W_f.weight); nn.init.zeros_(self.U_f.weight)    # pin f=σ(bias) data-independently at t=0
        nn.init.zeros_(self.U_h.weight)                                     # recurrent candidate path silent at t=0

    def forward(self, x: torch.Tensor, h_prev: torch.Tensor) -> torch.Tensor:
        f = torch.sigmoid(self.W_f(x) + self.U_f(h_prev))                  # retention (past kept)
        cand = torch.tanh(self.gn(self.W_h(x) + self.U_h(f * h_prev)))     # bounded candidate
        return f * h_prev + (1.0 - f) * cand


class ConvPatchFrontEnd(nn.Module):
    def __init__(self, in_channels: int = 3, conv_recurrent: bool = False,
                 conv_rec_stage: int = 1, conv_rec_retain: float = 0.3) -> None:
        super().__init__()
        self.in_channels = int(in_channels)
        c0, c1, c2, c3 = 32, 64, 128, 128
        self.stem = nn.Sequential(
            nn.Conv2d(self.in_channels, c0, 3, stride=1, padding=1, bias=False), _gn(c0), nn.SiLU())
        self.stage1 = SEResBlock(c0, c1, stride=2)    # 25→13
        self.stage2 = SEResBlock(c1, c2, stride=2)    # 13→7
        self.stage3 = SEResBlock(c2, c3, stride=1)    # 7→7 (extra depth, no further downsample)
        self.pool = nn.AdaptiveAvgPool2d(1)
        self.out_norm = RMSNorm(O_FLAT2)              # scale-match into the ViT; PRESERVES colour DC (no mean-subtract)
        assert c3 == O_FLAT2
        self.n_tokens = N_PATCH
        self.token_dim = TOKEN_DIM
        self.frozen = False
        # ── perceptual recurrence: a ConvMGU wrapping ONE conv stage's output (shared across patches,
        #    per-patch STATE). stage1 = 64ch/13×13 (early, cheap, keeps motion-relevant spatial resolution);
        #    stage2 = 128ch/7×7. concat[feat‖H] → 1×1 reduce back to C → continue the stack.
        self.conv_recurrent = bool(conv_recurrent)
        if self.conv_recurrent:
            assert conv_rec_stage in (1, 2), "conv_rec_stage must be 1 (after stage1) or 2 (after stage2)"
            self.conv_rec_stage = int(conv_rec_stage)
            cs = {1: c1, 2: c2}[self.conv_rec_stage]
            self.conv_mgu = ConvMGU(cs, retain=float(conv_rec_retain))
            self.conv_reduce = nn.Sequential(nn.Conv2d(2 * cs, cs, 1, bias=False), _gn(cs), nn.SiLU())

    def _encode_patch(self, o: torch.Tensor) -> torch.Tensor:
        """STATELESS path (unchanged): o: (B,C,25,25) → ô (B,128)."""
        z = self.stem(o)
        z = self.stage1(z); z = self.stage2(z); z = self.stage3(z)
        z = self.pool(z).flatten(1)                   # (B,128)
        return self.out_norm(z)

    def _fuse(self, feat: torch.Tensor, h_prev):
        """Run the ConvMGU on `feat` (h_prev None → zeros), concat, 1×1-reduce back to C. Returns (fused, h_new)."""
        if h_prev is None:
            h_prev = torch.zeros_like(feat)
        h_new = self.conv_mgu(feat, h_prev)
        fused = self.conv_reduce(torch.cat([feat, h_new], dim=1))
        return fused, h_new

    def _encode_patch_rec(self, o: torch.Tensor, h_prev):
        """RECURRENT path: o batched (B*4,C,25,25); insert the ConvMGU after stage{conv_rec_stage}.
        Returns (ô (B*4,128), h_new (B*4,Cs,Hs,Ws))."""
        z = self.stem(o)
        z = self.stage1(z)
        if self.conv_rec_stage == 1:
            z, h_new = self._fuse(z, h_prev)
            z = self.stage2(z); z = self.stage3(z)
        else:                                          # stage 2
            z = self.stage2(z)
            z, h_new = self._fuse(z, h_prev)
            z = self.stage3(z)
        z = self.pool(z).flatten(1)
        return self.out_norm(z), h_new

    def forward(self, x: torch.Tensor, t: int, conv_state=None):
        """x: (B,3,50,50) RGB frame, t: integer timestep.
        Stateless (conv_recurrent=False): returns X: (B,4,140) — byte-identical to before.
        Recurrent: returns (X: (B,4,140), new_conv_state: (B*4,Cs,Hs,Ws)), state carried across frames."""
        B = x.shape[0]
        g = x if self.in_channels == 3 else x.mean(dim=1, keepdim=True)
        # [TL, TR, BL, BR] in the env's cell order (patch index == cue/change index).
        patches = [g[:, :, :25, :25], g[:, :, :25, 25:], g[:, :, 25:, :25], g[:, :, 25:, 25:]]
        if self.conv_recurrent:
            # fold the 4 patches into the batch (row b*4+p ↔ patch p) so the CNN runs once and each patch
            # carries its OWN conv-state; GroupNorm/SE are batch-independent so this is numerically clean.
            P = torch.stack(patches, dim=1).reshape(B * N_PATCH, self.in_channels, 25, 25)
            emb_bp, new_conv = self._encode_patch_rec(P, conv_state)
            emb = emb_bp.reshape(B, N_PATCH, O_FLAT2)
        else:
            emb = torch.stack([self._encode_patch(p) for p in patches], dim=1)    # (B,4,128)
            new_conv = None
        pos = torch.eye(POS_DIM, device=x.device, dtype=x.dtype).unsqueeze(0).expand(B, -1, -1)
        ti = max(0, min(int(t), TEMP_DIM - 1))
        tau = torch.zeros(B, N_PATCH, TEMP_DIM, device=x.device, dtype=x.dtype)
        tau[:, :, ti] = 1.0
        X = torch.cat([emb, pos, tau], dim=-1)                               # (B,4,140)
        return (X, new_conv) if self.conv_recurrent else X
