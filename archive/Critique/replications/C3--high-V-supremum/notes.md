# CR-026 notes

## Sanity / validation

- The model code reproduces CR-001's V=0.5 reference points: at
  $(V=0.5, v=5, r=0.1)$, VDA = 0.0155 (matches CR-001 table); at
  $(V=0.5, v=5, r=0.398)$, VDA = 0.0774 (matches CR-001 peak).
  So the implementation is correct, and the V=0.75 finding is not an
  artefact of a bug.

- The defensive `np.clip(alpha, 0.0, 1.0)` in `d_prime_cued_uncued`
  is a fix for a bug that surfaced only in the refinement pass:
  `np.arange(0.02, 1.0 + 1e-9, 0.005)` can produce a final value
  $1.0 + \epsilon$ due to floating-point rounding, which makes
  $(1 - \alpha)/(N-1)$ slightly negative, and `sqrt(neg) = NaN` then
  propagates through everything. The coarse pass at
  `np.arange(0.02, 1.0 + 1e-9, 0.01)` happens to land cleanly on
  $1.0$ in this build but is also affected on other builds; the
  clamp is correct in both regimes.

## What the result depends on

- **Variant A vs B.** CR-026 ran Variant A only ($\mathrm{CR} = V v +
  (1-V)$). Variant B ($\mathrm{CR} = 1$) was not tested; spawn as a
  follow-up. Per CR-002's variant-B sweep, the V=0.75 boundary in
  variant B is expected to sit slightly differently because the
  no-FA payoff does not scale with $v$, which dampens the cued-side
  gain in (8) of the derivation. Provisional prediction: sup VDA at
  V=0.75 in variant B is smaller than in variant A but likely still
  $> 0.005$.

- **Transfer function $h$.** Only $h = \sqrt{\cdot}$ was tested. The
  closed-form (5) depends on $\kappa$ which depends on the optimal
  criteria, which in turn depend on $d'_b = d'_{\max}\cdot f(1/N)$,
  which depends on $h(1/N)$. For $h = a$ (linear): $f(1/N) = 0.5 +
  0.5\cdot 0.25 = 0.625$, $d'_b = 1.25$. For $h = a^{0.3}$: $f(1/N) =
  0.5 + 0.5\cdot 0.617 = 0.808$, $d'_b = 1.62$. For $h = a^2$:
  $f(1/N) = 0.5 + 0.5\cdot 0.0625 = 0.531$, $d'_b = 1.06$. Higher
  $d'_b$ → criteria closer to zero → $\kappa$ closer to 1 →
  $V_{\text{critical}}$ slightly lower. Worth spawning a sensitivity
  follow-up.

- **Reference parameters.** $(N=4, d'_{\max}=2, f_0=0.5)$ is the
  paper's headline regime. The closed-form (5) explicitly depends on
  $N$ and (implicitly through $\kappa$) on $d'_{\max}$ and $f_0$. A
  cleaner statement of the refutation: §4.4's wording fails at the
  *headline reference regime*, which is the strongest version of the
  refutation.

## What this run did NOT do

- Did not test alternative reward structures (A7). Variant A only.
- Did not test alternative transfer functions (A5). $h = \sqrt{}$ only.
- Did not test cross-location response correlations (A1). Independence
  assumed throughout — but this is the paper's own assumption, so the
  refutation is internal-to-model.
- Did not compute the closed-form $V_{\text{critical}}$ including the
  FAR-side correction (derivation §5.1 noted the simple approximation
  underestimates by $\sim 4$pp; a full correction would shift the
  predicted boundary from 0.74 to 0.78, matching empirics).
- Did not test the proposed §4.4 reformulation against any other
  $(N, d'_{\max}, f_0, h)$ combination — the reformulation predicts
  $V_{\text{critical}}$ as a closed form in those parameters, but
  empirical validation across the full secondary-sweep grid is a
  separate task (would be a CR-031-class follow-up).

## Spawned tasks (for the agent backlog)

- **CR-027** (re-derivation, medium): full FAR-corrected
  $V_{\text{critical}}(r, N, d'_{\max}, f_0, h)$ closed form. Resolves
  the 4-percentage-point gap between the simple-approximation
  prediction (§2 (5) ≈ 0.74) and the empirical boundary (≈ 0.78).

- **CR-028** (replication, medium): Variant B sup at V=0.75.
  Confirms whether the §4.4 wording is wrong in both variants or
  only variant A.

- **CR-029** (sensitivity, low): $V_{\text{critical}}$ across the
  paper's secondary sweep grid $(f_0 \in \{0.1, 0.3, 0.5, 0.7\}, h
  \in \{a, \sqrt{a}, a^{0.3}, a^2\}, N \in \{2, 4\})$. Predicts the
  shape of the "negligible-VDA-regardless-of-r" region across the
  full parameter space.

- **CR-030** (literature, low): given the new closed-form
  $V_{\text{critical}}$, search the literature for cueing experiments
  with high $V$ AND high $v$ AND cost-dominant $r$ (the predicted
  residual high-V VDA window). The Stănișor 2013 paradigm
  (high V curve-tracing with reward magnitude variation) is a
  candidate; a behavioural-d′ probe in that experiment would directly
  test the §7 reformulation.
