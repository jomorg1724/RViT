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
