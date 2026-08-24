"""
Actor and critic heads — read the FLATTENED memory readout H' ∈ ℝ^{4096} (the paper
drops the 4-patch structure at the RL agent: "this 4-patch structure is retained
throughout the attention and working memory modules but not in the RL agent").

Actor (paper Eq 713–718): H' → ELU → ELU → ELU → softmax over the 2 actions.

Critic: our harness's distributional QR-DQN critic (per the locked spec) reading H'
through the same 3-ELU trunk, outputting `n_quantiles` quantiles PER action,
(B, A, N). V is the policy-weighted quantile mixture (derive_V). The paper's own
critic is an action-conditioned categorical critic; here we use our QR-DQN objective
with `n_quantiles` particles (=5).
"""
from __future__ import annotations

from typing import Optional, List

import torch
import torch.nn as nn

HIDDEN = 256


class FFActor(nn.Module):
    def __init__(self, in_dim: int, n_actions: int = 2, hidden: int = HIDDEN,
                 init_action_bias: Optional[List[float]] = None) -> None:
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(in_dim, hidden), nn.ELU(),
            nn.Linear(hidden, hidden), nn.ELU(),
            nn.Linear(hidden, hidden), nn.ELU(),
        )
        self.out = nn.Linear(hidden, n_actions)
        if init_action_bias is not None:
            with torch.no_grad():
                self.out.bias.copy_(torch.tensor(init_action_bias, dtype=self.out.bias.dtype))

    def forward(self, h_flat: torch.Tensor) -> torch.Tensor:
        return self.out(self.net(h_flat))                       # (B, n_actions) logits


class QRCritic(nn.Module):
    def __init__(self, in_dim: int, n_actions: int = 2, n_quantiles: int = 5,
                 hidden: int = HIDDEN) -> None:
        super().__init__()
        self.n_actions, self.n_quantiles = n_actions, n_quantiles
        # quantile midpoints τ_i = (i+0.5)/N for the quantile-Huber loss (QR-DQN)
        self.register_buffer("taus", (torch.arange(n_quantiles, dtype=torch.float32) + 0.5) / n_quantiles)
        self.net = nn.Sequential(
            nn.Linear(in_dim, hidden), nn.ELU(),
            nn.Linear(hidden, hidden), nn.ELU(),
            nn.Linear(hidden, hidden), nn.ELU(),
        )
        self.out = nn.Linear(hidden, n_actions * n_quantiles)

    def forward(self, h_flat: torch.Tensor) -> torch.Tensor:
        q = self.out(self.net(h_flat))                          # (B, A*N)
        return q.view(q.shape[0], self.n_actions, self.n_quantiles)   # (B, A, N)

    def derive_V(self, q_dist: torch.Tensor, actor_logits: torch.Tensor):
        """V_dist = Σ_a π(a)·Q_dist(a)  (policy-weighted quantile mixture); V = mean(V_dist)."""
        pi = torch.softmax(actor_logits, dim=-1).unsqueeze(-1)  # (B, A, 1)
        V_dist = (pi * q_dist).sum(dim=-2)                      # (B, N)
        V_scalar = V_dist.mean(dim=-1)                          # (B,)
        return V_dist, V_scalar


class ImageVAEHead(nn.Module):
    """Bottom-up image-VAE head reading the transformer output Z (per patch token).

    Pipeline (per timestep): Z (B,N,d_token) → 1-layer reducer to `reduce_dim` per patch →
    flatten patches → project to a VAE latent (mean/log-var) → sample → MLP decoder →
    full-frame reconstruction (img_ch × img_hw × img_hw), tanh-squashed to the [-1,1] obs range.

    This head is meant to be trained on a SEPARATE backward pass whose input Z has the
    recurrent memory DETACHED, so its gradient shapes the bottom-up perception path (conv
    front-end + attention projections) and never the LSTM."""
    def __init__(self, d_token: int = 140, n_patch: int = 4, reduce_dim: int = 32,
                 latent_dim: int = 64, img_ch: int = 3, img_hw: int = 50, hidden: int = 512) -> None:
        super().__init__()
        self.latent_dim, self.img_ch, self.img_hw = int(latent_dim), int(img_ch), int(img_hw)
        self.reduce = nn.Linear(d_token, reduce_dim)                 # 1-layer per-patch reducer d_token→32
        self.to_latent = nn.Linear(n_patch * reduce_dim, 2 * latent_dim)   # → (mean ‖ log-var)
        self.decode = nn.Sequential(
            nn.Linear(latent_dim, hidden), nn.GELU(),
            nn.Linear(hidden, hidden), nn.GELU(),
            nn.Linear(hidden, img_ch * img_hw * img_hw),
        )

    def forward(self, Z: torch.Tensor):
        """Z: (B,T,N,d_token) → recon (B,T,img_ch,img_hw,img_hw), mu (B,T,L), logvar (B,T,L)."""
        B, T = Z.shape[:2]
        h = torch.nn.functional.gelu(self.reduce(Z))                # (B,T,N,reduce_dim)
        h = h.reshape(B, T, -1)                                     # flatten patches → (B,T,N*reduce_dim)
        mu, logvar = self.to_latent(h).chunk(2, dim=-1)            # each (B,T,L)
        logvar = logvar.clamp(-8.0, 8.0)                           # numerical safety
        z = mu + torch.exp(0.5 * logvar) * torch.randn_like(mu)    # reparameterisation
        recon = torch.tanh(self.decode(z))                        # (B,T,ch*hw*hw) → [-1,1]
        recon = recon.reshape(B, T, self.img_ch, self.img_hw, self.img_hw)
        return recon, mu, logvar


class JEPAStructuredHead(nn.Module):
    """STRUCTURED DINO/V-JEPA head on the recurrent cell output (per patch token). Instead of one
    flat softmax over all prototypes, it produces `n_heads` separate embeddings each of `proto_dim`,
    and EACH embedding is softmaxed independently (over proto_dim). So per token there are n_heads
    distributions; across the 4 patch tokens that's (4 × n_heads) independent softmaxes, mirroring
    the softmax-head cell's per-(patch,head) structure. The loss softmaxes the LAST dim per group."""
    def __init__(self, d_mem: int = 1024, hidden: int = 512, n_heads: int = 4,
                 proto_dim: int = 256) -> None:
        super().__init__()
        self.n_heads, self.proto_dim = int(n_heads), int(proto_dim)
        self.norm = nn.LayerNorm(d_mem)
        self.mlp = nn.Sequential(nn.Linear(d_mem, hidden), nn.GELU(),
                                 nn.Linear(hidden, hidden), nn.GELU())
        self.out = nn.Linear(hidden, self.n_heads * self.proto_dim)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """x: (..., d_mem) → (..., n_heads, proto_dim) logits (softmax over proto_dim per head)."""
        h = self.out(self.mlp(self.norm(x)))
        return h.unflatten(-1, (self.n_heads, self.proto_dim))   # (..., n_heads, proto_dim)
