# CR-026 — C3 high-V supremum replication

**Companion to:** [`../../derivations/C3--high-V-supremum.md`](../../derivations/C3--high-V-supremum.md)
**Companion verdict:** [`../../verdicts/C3--narrow-regime.md`](../../verdicts/C3--narrow-regime.md)
**Run:** run-005 (2026-05-17)

## What this computes

The supremum

$$
\sup_{r \in [0.1, 10],\; v \in \{1, 2, 3, 4, 5\}}\; \big[R^\star_{P_1}(r,v;V{=}0.75) - R^\star_{P_2}(r,v;V{=}0.75)\big]
$$

at the paper's reference parameters $(N{=}4, d'_{\max}{=}2, f_0{=}0.5,
h{=}\sqrt{\cdot}, \text{Variant A})$. The numerical answer is the
**adversarial test** of the paper's §4.4 / §5.2 categorical claim:

> "At high validity ($V \geq 0.75$), optimal $\alpha^\star$ is near
> $1.0$ and VDA is negligible ($<0.005$ reward units) regardless of $r$."
> — §4.4

## How to run

```bash
cd Critique/replications/C3--high-V-supremum
python3 run.py
```

Runs in $\sim 30$ s on the agent's sandbox (no scipy required;
$\Phi$ computed via `math.erf`). All outputs are saved to `output/`.

## Decision rule (per CR-026 task definition)

| Empirical sup | Verdict label | Interpretation |
|---:|:---|:---|
| $< 0.005$ | CONFIRMED-CONDITIONAL | §4.4 is a theorem of the model under (A1–A7). |
| $[0.005, 0.020]$ | WEAKLY-SUPPORTED | §4.4 categorical wording too strong; weaker reformulation operational. |
| $> 0.020$ | CONTESTED | §4.4 wording wrong internal to the model (crosses §4.4's own "hot zone" boundary at $V=0.75$). |

## Empirical result

**sup VDA = 0.0410** (coarse $\Delta\alpha = 0.01$) or **0.0400**
(refined $\Delta\alpha = 0.005$) at $(r, v) = (0.10, 5)$, $V = 0.75$.

This is $\mathbf{8\times}$ the paper's $0.005$ "negligible" threshold
and $\mathbf{2\times}$ the $0.02$ "hot zone" boundary that §4.4 itself
defines.

**Verdict label: CONTESTED.**

## Additional probes

The script also reports:

1. **Boundary V-grid** ($V \in \{0.75, 0.80, 0.90, 0.95\}$). Confirms
   the §4.4 "$V \geq 0.75$" threshold fails at $V = 0.75$ and holds at
   $V = 0.80$. The boundary is one V-step ($\Delta V \approx 0.025$)
   above what the paper claims.

2. **Fine V-grid in $[0.75, 0.80]$** at $(r=0.1, v=5)$. Locates the
   empirical $V_{\text{critical}} \in (0.775, 0.780)$, matching the
   closed-form analytic prediction of $V_{\text{critical}}(r, N) =
   1/(1 + r(N-1)/\kappa)$ with $\kappa \approx 0.85$ (derivation
   §2).

3. **Fine r-grid in $[0.05, 0.20]$** at $(V=0.75, v=5)$. Confirms the
   sup at $r=0.10$ is interior to a window where VDA $> 0.005$
   extends across $r \in [\approx 0.04, \approx 0.13]$, and VDA $>
   0.02$ extends across $r \in [\approx 0.06, \approx 0.13]$. The
   sup is **not** a grid-corner artefact.

4. **Comparison at $V = 0.50$ vs $V = 0.75$** at the sup location
   $(r=0.1, v=5)$. VDA at $V = 0.75$ is $2.6\times$ larger than at $V =
   0.50$, illustrating the counter-intuitive prediction (derivation
   §3) that VDA *grows* with $V$ inside the high-V VDA window before
   collapsing above $V_{\text{critical}}$.

## Files in this directory

| File | Description |
|:---|:---|
| `run.py` | The replication script. Self-contained; no scipy. |
| `output.log` | Console log from the most recent run. |
| `output/sup_vda_at_V075.json` | Full numerical results (105 (r,v) grid + refinement + boundary + r-fine + V-fine probes). |
| `README.md` | This file. |

## How this differs from CR-001/CR-002

The model code (`d_prime_cued_uncued`, `optimal_criteria_R`,
`policy_rewards`) is **identical** to
`../C2--non-monotonic-vda/run.py` (CR-001) and
`../C1--criterion-fraction-floor/run.py` (CR-002), modulo a defensive
clamp on $\alpha \in [0, 1]$ that prevents floating-point overshoot
from `np.arange` from feeding negative values to `sqrt`. The
substantive change is the *probe*: at $V = 0.75$ (CR-001 / CR-002 ran
at $V = 0.50$ or swept $V$), with finer resolution around the
boundary the paper claims is safe.

## Verdict movement

Run-005 appends a new dated version (Version 0.2) to
`../../verdicts/C3--narrow-regime.md`, moving the C3 verdict from
**WEAKLY-SUPPORTED** (run-004) to **CONTESTED** (run-005). The
proposed §4.4 / §5.2 reformulation is drafted in the derivation file
§7.
