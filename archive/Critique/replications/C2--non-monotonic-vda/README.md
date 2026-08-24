# C2 — non-monotonic VDA: cross-check replication

Companion to:
- derivation: `../../derivations/C2--non-monotonic-vda.md`
- verdict:    `../../verdicts/C2--non-monotonic-vda.md`

## What this script computes

A minimal implementation of the policy decomposition P1/P2/P3/P4
from mission §2.5, sweeping the asymmetry ratio $r$ across the
paper's primary range $[0.1, 10.0]$ (21 log-spaced points). For each
$r$ it reports $\alpha^\star$ for P1 and P2, the optimal reward
under each, and the VDA benefit $R(P_1) - R(P_2)$.

The intent is to corroborate the analytic re-derivation in
`../../derivations/C2--non-monotonic-vda.md`, not to reproduce
Figure 4 pixel-for-pixel. A full replication is spawned as
CR-013 in the backlog.

## How it differs from the paper's implementation

- $\Delta\alpha = 0.01$ (paper: 0.005). Coarser by 2× because
  scipy was unavailable in the sandbox (disk pressure); we
  implemented the normal CDF via `math.erf` and a hand-rolled
  Phi/phi pair. Halving $\alpha$-resolution roughly doubles
  the per-r cost; we kept 0.01 to stay within the 45 s sandbox
  timeout.
- $\Delta c = 0.05$ (matches paper).
- No false-alarm cost beyond the missed-CR; matches paper.
- Variant A only (CR = $Vv + (1-V)$).
- We pre-compute Phi on a fixed $c$-grid and vectorise via numpy
  broadcasting; the paper's reported implementation is similar
  (§3.2 "vectorised grid search over a three-dimensional array").

## Headline output (run on 2026-05-17)

```
r=  0.1000  alpha_P1=0.950  alpha_P2=0.250  VDA=0.0155
r=  0.3162  alpha_P1=0.990  alpha_P2=0.250  VDA=0.0737
r=  0.3981  alpha_P1=0.990  alpha_P2=0.320  VDA=0.0774  ← peak
r=  1.0000  alpha_P1=1.000  alpha_P2=0.750  VDA=0.0395
r=  3.1623  alpha_P1=1.000  alpha_P2=0.960  VDA=0.0071
r= 10.0000  alpha_P1=1.000  alpha_P2=0.990  VDA=0.0019

Peak VDA across swept r: 0.07740 at r = 0.3981
Paper claim (C2):        ~ 0.080      at r ~ 0.3
```

The peak is one log-grid step to the right of the paper's reported
$r \approx 0.3$; magnitudes agree to within ~4 %.

## Caveats

1. Grid-resolution artefact: $\alpha^\star_{\mathrm{P2}}$ jumps
   from $0.25$ to $0.32$ between $r=0.316$ and $r=0.398$, then
   smoothly increases. The escape threshold lies in
   $(0.316, 0.398]$. A finer $\alpha$-grid would localise the
   threshold and may shift the peak one log-step leftward.
2. The criterion fraction at $r=10$ is $0.601$, *just above*
   the C1 claim's lower bound of $0.60$. This is a useful side
   corroboration of C1 but a full attack on C1 is task CR-002.
3. No replication of Figure 4's $v \in \{1,2,3,4,5\}$ envelope;
   only $v=5$ run here.

## How to run

```bash
cd Critique/replications/C2--non-monotonic-vda
python3 run.py
```

Outputs to `output/vda_vs_r.json`.
