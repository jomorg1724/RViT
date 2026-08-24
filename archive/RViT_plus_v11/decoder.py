"""
Actor and critic decoders for RViT+ v5_part2 — 1D-CONV style.

Replaces the (failed) mean-pool + FF heads. The pooled variant collapsed the
100-token spatial layout of H2 before decoding, which is the suspected reason it
did not learn a spatial task. Here each head instead PRESERVES that layout:

    h2  = recurrent_states[-1]              # (B, N, d_mem)  top LSTM hidden
    x   = h2.transpose(1, 2)                # (B, d_mem, N)  features = CHANNELS,
                                            #                tokens   = CONV AXIS
    h   = conv_trunk(x)                     # strided Conv1d stack, downsamples N
    out = Linear(flatten(h))               # → outputs

So the 128 LSTM features are conv channels and the 100 token positions (the
10×10 patch grid, row-major) are the convolution axis; each strided Conv1d mixes
local spatial neighbourhoods while shrinking the token axis. The final small
feature map is flattened and linearly projected to the outputs.

  • ActorDecoder  → logits (B, n_actions)
  • CriticDecoder → (B, n_actions, n_quantiles); V via derive_V (expected SARSA,
                    stop-grad on π) — unchanged so ppo.py is untouched.
"""
from __future__ import annotations

from typing import List, Optional, Tuple

import torch
import torch.nn as nn


def _conv_trunk(d_mem: int, conv_channels: int, n_conv_layers: int, kernel: int, drop: float) -> nn.Sequential:
    """A stack of stride-2 Conv1d → GELU → Dropout layers over the token axis.
    First layer ingests d_mem channels; the rest keep conv_channels."""
    layers: list[nn.Module] = []
    in_ch = d_mem
    pad = kernel // 2
    for _ in range(max(1, int(n_conv_layers))):
        layers += [
            nn.Conv1d(in_ch, conv_channels, kernel_size=kernel, stride=2, padding=pad),
            nn.GELU(), nn.Dropout(drop),
        ]
        in_ch = conv_channels
    return nn.Sequential(*layers)


def _flat_dim(trunk: nn.Sequential, d_mem: int, n_tokens: int) -> int:
    """Flattened size of the conv trunk output for a (B, d_mem, n_tokens) input."""
    with torch.no_grad():
        y = trunk(torch.zeros(1, d_mem, n_tokens))
    return int(y.shape[1] * y.shape[2])


def _to_conv_input(recurrent_states: List[torch.Tensor]) -> torch.Tensor:
    """Concatenate the provided readout streams on the FEATURE axis and lay them
    out as (B, Σfeatures, N): features = conv channels, tokens = the conv axis.

    v11 passes the two transformer outputs [Z_sal, Z_td] → 2·d_model channels, so
    at every token position the conv sees both the salience and the top-down
    feature. A single-element list (e.g. just H2) recovers the v8/v9 behaviour."""
    x = torch.cat(recurrent_states, dim=-1)                 # (B, N, Σfeatures)
    return x.transpose(1, 2).contiguous()                   # (B, Σfeatures, N)


class ActorDecoder(nn.Module):
    """Conv1d-over-tokens trunk on H2 → flatten → Linear → action logits (B, n_actions)."""

    def __init__(
        self,
        d_mem: int = 128,
        n_tokens: int = 100,
        n_actions: int = 2,
        conv_channels: int = 64,
        n_conv_layers: int = 3,
        conv_kernel: int = 5,
        drop: float = 0.1,
        init_action_bias: Optional[list] = None,
        final_init_std: float = 0.02,
    ) -> None:
        super().__init__()
        self.n_actions = n_actions
        self.trunk = _conv_trunk(d_mem, conv_channels, n_conv_layers, conv_kernel, drop)
        self.out = nn.Linear(_flat_dim(self.trunk, d_mem, n_tokens), n_actions)
        nn.init.normal_(self.out.weight, std=final_init_std)
        nn.init.zeros_(self.out.bias)
        if init_action_bias is not None:
            if len(init_action_bias) != n_actions:
                raise ValueError(
                    f"init_action_bias has length {len(init_action_bias)} but n_actions = {n_actions}"
                )
            with torch.no_grad():
                self.out.bias.copy_(torch.tensor(init_action_bias, dtype=torch.float32))

    def forward(self, recurrent_states: List[torch.Tensor]) -> torch.Tensor:
        h = self.trunk(_to_conv_input(recurrent_states))        # (B, conv_ch, L')
        return self.out(h.flatten(1))                           # (B, n_actions)


class CriticDecoder(nn.Module):
    """Conv1d-over-tokens trunk on H2 → flatten → Linear → action-conditional
    quantile distribution (B, n_actions, n_quantiles)."""

    def __init__(
        self,
        d_mem: int = 128,
        n_tokens: int = 100,
        n_actions: int = 2,
        n_quantiles: int = 51,
        conv_channels: int = 64,
        n_conv_layers: int = 3,
        conv_kernel: int = 5,
        drop: float = 0.1,
        final_init_std: float = 0.02,
    ) -> None:
        super().__init__()
        self.n_actions = n_actions
        self.n_quantiles = n_quantiles
        self.trunk = _conv_trunk(d_mem, conv_channels, n_conv_layers, conv_kernel, drop)
        self.out = nn.Linear(_flat_dim(self.trunk, d_mem, n_tokens), n_actions * n_quantiles)
        nn.init.normal_(self.out.weight, std=final_init_std)
        nn.init.zeros_(self.out.bias)
        taus = (torch.arange(n_quantiles, dtype=torch.float32) + 0.5) / n_quantiles
        self.register_buffer("taus", taus)

    def forward(self, recurrent_states: List[torch.Tensor]) -> torch.Tensor:
        h = self.trunk(_to_conv_input(recurrent_states))        # (B, conv_ch, L')
        q = self.out(h.flatten(1))                              # (B, n_actions*n_quantiles)
        return q.view(q.shape[0], self.n_actions, self.n_quantiles)

    def derive_V(
        self, q_dist: torch.Tensor, actor_logits: torch.Tensor
    ) -> Tuple[torch.Tensor, torch.Tensor]:
        """Expected-SARSA V from Q and π, stop-grad on π (unchanged from v5).
            V_dist(s)   = Σ_a sg[π(a|s)] · Q(s, a, :)   → (B, n_quantiles)
            V_scalar(s) = mean over quantiles of V_dist → (B,)
        """
        if q_dist.dim() != 3:
            raise ValueError(f"q_dist must be (B, n_actions, n_quantiles); got {tuple(q_dist.shape)}")
        if actor_logits.dim() != 2:
            raise ValueError(f"actor_logits must be (B, n_actions); got {tuple(actor_logits.shape)}")
        pi = torch.softmax(actor_logits, dim=-1)
        pi_sg = pi.detach()
        V_dist = (pi_sg.unsqueeze(-1) * q_dist).sum(dim=1)       # (B, n_quantiles)
        V_scalar = V_dist.mean(dim=-1)                           # (B,)
        return V_dist, V_scalar
