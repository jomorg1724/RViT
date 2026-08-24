"""
Decision readout + actor / critic heads.

Architecture writeup: see `../docs/THESIS.md` §3 (Methods).

The decision readout is the only place in PRISM where a non-conv reduction
across the spatial axis happens. The reduction is constrained to be:
    1. A uniform global pool (parameter-free), AND
    2. A pool whose weights are the prediction-error magnitude (parameter-free).
Both are derived; neither is a learned spatial softmax. This is the minimum
commitment to a non-conv operation that any decision-emitting architecture
must make — cortical decision areas (LIP, FEF, area 5) are widely thought to
do exactly this kind of pooling over topographic input.

Mathematical formulation
------------------------
Given M_t ∈ ℝ^(B,C_M,H,W) and the saliency map S_t ∈ ℝ^(B,1,H,W) ≥ 0:

    d_t = Conv_{1×1}^{C_M → 4}( M_t )                             # (B, 4, H, W)

    g_t = mean_{H,W} d_t                                          # (B, 4)
    e_t = Σ_{H,W} S_t · d_t  /  (Σ_{H,W} S_t + eps)               # (B, 4)

    s_t = [g_t, e_t]                                              # (B, 8)

The actor and critic are tiny 2-layer MLPs over s_t.
"""
from __future__ import annotations

from typing import Tuple

import torch
import torch.nn as nn
import torch.nn.functional as F


class DecisionReadout(nn.Module):
    """
    Project memory to an evidence volume, then pool three ways:
      (1) global mean   over (H,W)        → (B, decision_channels)
      (2) global saliency-weighted mean   → (B, decision_channels)
      (3) per-cell pooled saliency*evidence on a (G,G) coarse grid
                                          → (B, decision_channels * G * G)

    The third pool gives the actor *spatial localisation* of where surprise
    is concentrated, without committing to a hand-coded "4 patches" assumption
    (G=2 → 4 cells, G=3 → 9 cells, etc. — pick by `coarse_grid`).

    Why this exists
    ---------------
    The original two-pool readout collapses spatial info to scalars, so the
    actor cannot distinguish "high saliency at the cued patch" from "high
    saliency at an uncued patch." Without that distinction, the actor cannot
    represent the optimal policy "press when surprise is at the cued location."
    The (G,G) grid is the minimum amount of spatial structure that enables
    cued-vs-uncued discrimination on a 2×2-quadrant scene, and is generic for
    any spatially-organised observation.

    Returns the (B, output_dim)-shaped state vector consumed by actor / critic.

    Args
    ----
    memory_channels   : C_M (default 16)
    decision_channels : number of evidence channels (default 4)
    coarse_grid       : G — spatial resolution of the per-cell pool.
                        Default 2 (i.e. 2×2 = 4 cells). Set to 1 to disable
                        the spatial pool (recovers the previous 2-pool readout).
    """

    def __init__(
        self,
        memory_channels: int = 16,
        decision_channels: int = 4,
        coarse_grid: int = 2,
        eps: float = 1e-6,
    ) -> None:
        super().__init__()
        self.memory_channels = memory_channels
        self.decision_channels = decision_channels
        self.coarse_grid = int(coarse_grid)
        if self.coarse_grid < 1:
            raise ValueError(f"coarse_grid must be >= 1; got {coarse_grid}")
        self.eps = eps

        # 1×1 projection: per-location, per-channel re-weighting only — no
        # spatial mixing here, the pooling step does that.
        self.d_proj = nn.Conv2d(memory_channels, decision_channels, kernel_size=1, bias=True)
        nn.init.kaiming_uniform_(self.d_proj.weight, a=0, mode="fan_in", nonlinearity="relu")
        nn.init.zeros_(self.d_proj.bias)

    @property
    def output_dim(self) -> int:
        """Dimensionality of the s_t vector: global mean + global saliency mean + (G×G) cells × channels."""
        return self.decision_channels * (2 + self.coarse_grid ** 2)

    def forward(self, M_t: torch.Tensor, S_t: torch.Tensor) -> torch.Tensor:
        """
        M_t : (B, C_M, H, W)  memory state
        S_t : (B, 1, H, W)    saliency map ≥ 0 (from prediction_error_map)

        Returns
        -------
        s_t : (B, output_dim)  decision vector
        """
        if M_t.shape[1] != self.memory_channels:
            raise ValueError(
                f"DecisionReadout expects {self.memory_channels} memory channels; "
                f"got {M_t.shape[1]}"
            )
        if S_t.shape[1] != 1:
            raise ValueError(f"DecisionReadout expects S_t with 1 channel; got {S_t.shape[1]}")
        if S_t.shape[-2:] != M_t.shape[-2:]:
            raise ValueError(
                f"DecisionReadout: S_t and M_t must share spatial dims; "
                f"got {tuple(S_t.shape[-2:])} vs {tuple(M_t.shape[-2:])}"
            )

        # d_t: 1×1 projection of memory → 4 evidence channels.
        # (B, C_M, H, W) → (B, 4, H, W).
        d_t = self.d_proj(M_t)

        # ── Pool 1: global mean (uniform spatial average) ────────────────────
        g_t = F.adaptive_avg_pool2d(d_t, 1).flatten(start_dim=1)  # (B, 4)

        # ── Pool 2: global saliency-weighted mean ────────────────────────────
        # Weights = S_t / sum(S_t). Stable via +eps in denominator.
        s_weighted_d = (S_t * d_t).sum(dim=(-1, -2))  # (B, 4)
        s_norm = S_t.sum(dim=(-1, -2)) + self.eps     # (B, 1)
        e_t = s_weighted_d / s_norm                    # (B, 4)

        # ── Pool 3: per-cell saliency-weighted features on a (G,G) grid ─────
        # We adaptively-avg-pool both the numerator (S·d) and denominator (S)
        # to (G, G), then divide. This gives a per-cell saliency-weighted mean
        # of d. With G=2 the actor sees 4 cells × 4 channels = 16 numbers
        # describing "how much surprise-relevant evidence is in each quadrant."
        # adaptive_avg_pool with stride=ceil(H/G), kernel ≈ ceil(H/G) — handles
        # any input H,W gracefully.
        if self.coarse_grid > 1:
            sd_grid = F.adaptive_avg_pool2d(S_t * d_t, self.coarse_grid)   # (B, 4, G, G)
            s_grid = F.adaptive_avg_pool2d(S_t, self.coarse_grid)           # (B, 1, G, G)
            cell_t = sd_grid / (s_grid + self.eps)                          # (B, 4, G, G)
            cell_t = cell_t.flatten(start_dim=1)                            # (B, 4*G*G)
            s_t = torch.cat([g_t, e_t, cell_t], dim=-1)                     # (B, 4*(2+G²))
        else:
            s_t = torch.cat([g_t, e_t], dim=-1)                             # (B, 4*2)
        return s_t


class ActorHead(nn.Module):
    """
    Policy head: 2-layer MLP over the decision vector → action logits.

    Output is *logits*, not probabilities — the PPO update consumes logits
    directly via Categorical(logits=...). Use F.softmax(logits, dim=-1) only
    for diagnostic display.

    Args
    ----
    input_dim                : dimensionality of s_t (default 8 for DecisionReadout default)
    hidden_dim               : MLP hidden width (default 64)
    n_actions                : number of discrete actions (default 2 for ChangeDetectionEnv)
    init_action_logit_bias   : optional initial bias on the output logits, length n_actions.
        Defaults to None (zeros). For environments where one action immediately terminates
        the episode with zero reward (e.g. ChangeDetectionEnv's "press change-detected" at
        action=1), a negative bias on that action is essential at init: a near-uniform
        initial policy would otherwise terminate ~50% of episodes at t=0, starving the
        learner of any post-cue experience. With bias[1] = -4 the initial probability of
        the terminating action is σ(-4) ≈ 0.018, so episodes survive ~25 steps in
        expectation. This is a generic "conservative-policy" prior, not task-specific aux:
        it's the policy analogue of the +1 forget-gate-bias trick for LSTMs (Jozefowicz
        et al., 2015) — a generic recipe for breaking pathological initial dynamics.
    """

    def __init__(
        self,
        input_dim: int = 8,
        hidden_dim: int = 64,
        n_actions: int = 2,
        init_action_logit_bias: list[float] | None = None,
    ) -> None:
        super().__init__()
        self.fc1 = nn.Linear(input_dim, hidden_dim)
        self.fc2 = nn.Linear(hidden_dim, n_actions)

        # Standard small-init for policy outputs (Andrychowicz et al., 2020 — orthogonal
        # init with gain 0.01 keeps the initial policy near-uniform in logit space).
        nn.init.orthogonal_(self.fc1.weight, gain=2.0**0.5)  # √2 for ReLU/GELU layers
        nn.init.zeros_(self.fc1.bias)
        nn.init.orthogonal_(self.fc2.weight, gain=0.01)  # near-uniform initial policy
        nn.init.zeros_(self.fc2.bias)

        # Optional: bias the initial policy toward "safe" actions to avoid bootstrapping
        # collapse on environments with terminate-on-action dynamics. See class docstring.
        if init_action_logit_bias is not None:
            if len(init_action_logit_bias) != n_actions:
                raise ValueError(
                    f"init_action_logit_bias has length {len(init_action_logit_bias)}, "
                    f"expected n_actions={n_actions}"
                )
            with torch.no_grad():
                self.fc2.bias.copy_(torch.tensor(init_action_logit_bias, dtype=torch.float32))

        self.n_actions = n_actions

    def forward(self, s_t: torch.Tensor) -> torch.Tensor:
        """
        s_t : (B, input_dim)

        Returns
        -------
        logits : (B, n_actions)
        """
        h = F.gelu(self.fc1(s_t))
        return self.fc2(h)


class CriticHead(nn.Module):
    """
    Value head: 2-layer MLP over the decision vector → scalar V(s).

    Args
    ----
    input_dim  : dimensionality of s_t (default 8)
    hidden_dim : MLP hidden width (default 64)
    """

    def __init__(self, input_dim: int = 8, hidden_dim: int = 64) -> None:
        super().__init__()
        self.fc1 = nn.Linear(input_dim, hidden_dim)
        self.fc2 = nn.Linear(hidden_dim, 1)

        # Andrychowicz et al. recommend gain=1.0 on the value-output linear layer.
        nn.init.orthogonal_(self.fc1.weight, gain=2.0**0.5)
        nn.init.zeros_(self.fc1.bias)
        nn.init.orthogonal_(self.fc2.weight, gain=1.0)
        nn.init.zeros_(self.fc2.bias)

    def forward(self, s_t: torch.Tensor) -> torch.Tensor:
        """
        s_t : (B, input_dim)

        Returns
        -------
        value : (B,)  scalar value estimate
        """
        h = F.gelu(self.fc1(s_t))
        return self.fc2(h).squeeze(-1)
