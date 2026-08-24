# TRACE.md — section -> artifact provenance spine

This table makes the synthesizer's **assemble-only** mandate auditable
(mission §5.2, §6.1). One block per integrated manuscript section; every
scientific assertion lists the artifact that licenses it. A section is
not "done" until every claim in it has a row. Editorial connective
tissue (transitions, signposting) is not a claim and is not listed.

Artifact keys:
- **ORIG** = `Critique/source/main.pdf` (the original; structure +
  framing only, read-only).
- **LEDGER:Cn / LEDGER:An** = a row of `Rebuild/CLAIM_LEDGER.md` (the
  strength ceiling).
- **SIM:<dir>** = a simulation under `Rebuild/sims/`.
- **DERIV:<file>** = a derivation under `Rebuild/derivations/`.
- **RB:<file>** = a rebuilder draft section under
  `Rebuild/manuscript/sections/`.
- **BIB:<key>** = an entry in `Reconstruction/manuscript/refs.bib`.

---

> **SY-015 de-meta scrub (2026-05-30, run F2C7A9E1).** Content-preserving
> firewall pass over the whole manuscript: removed build-machinery framing
> from prose, comments, captions, and `refs.bib`. **No assertion below was
> added, removed, or changed in strength** — every existing grounding row
> still holds. The scrub only changed how findings are phrased (positive,
> standalone), not what they assert.

> **SY-005 coherence pass (2026-05-30, run 2F9C61B4).** Content-preserving
> consistency pass over Intro + Model + Results §4.1–§4.2. **No assertion,
> number, equation, or figure was added, removed, or changed in strength**
> — every grounding row below still holds. The pass only: (i) standardised
> the standard-normal density glyph to $\varphi$ in the Results gradient
> coefficients $K_c, K_u$ to match the Model's boxed integral (M9);
> (ii) identified the Results baseline symbol $\dprime_b \equiv
> \dprime_{\mathrm{base}}$ with the Model definition (M4) and removed the
> redundant `:=`, so the quantity is defined once (Model §2.3); (iii) made
> the two Model cross-references to the supplementary section say
> "Supplementary material" (matching Results and the section heading);
> (iv) fixed the one overfull `\hbox` (Results §4.2) and reworded two
> "trace"→"curve" plot mentions. Notation now consistent against the
> `\newcommand` block; no duplicated definitions; 0 dangling refs.

---

## Introduction (`sections/intro.tex`) — integrated SY-001 (2026-05-30)

| # | Assertion (paraphrase) | Strength | Artifact(s) |
| --- | --- | --- | --- |
| I1 | Observer can adapt to value cues in more than one way; mechanisms differ in cost | framing | ORIG §1 |
| I2 | Mechanism 1 = criterion adjustment; "free", no perceptual reallocation, leaves sensitivity elsewhere untouched | framing | ORIG §1; BIB:MullerFindlay1987, BIB:posner1980_orienting |
| I3 | Mechanism 2 = VDA: re-allocates attention, raises $\dprime$ at cued location at a cost elsewhere; reward can capture attention | framing | ORIG §1; BIB:CohenMaunsell2009, BIB:failing_theeuwes2018_selection_history, BIB:hickey2010_reward_salience_acc |
| I4 | Third lever = decorrelation; $\corr$ promoted to a model parameter; three-lever decomposition (criterion/sensitivity/decorrelation); $\corr=0$ recovers the two-mechanism picture; attention reduces interneuronal correlations | three levers, not two | LEDGER:A1; RB:model.tex (Definition of three levers, `def:three-levers`); BIB:CohenMaunsell2009, BIB:RuffCohen2016, BIB:Srinath2021 |
| I5 | Benefit and cost are not necessarily symmetric; enhancement vs suppression dissociable; asymmetry ratio $\Rsens>0$ introduced | framing | ORIG §1 (p.2) + §2.3; BIB:reynolds_heeger2009_normalization, BIB:treue_martinez_trujillo1999_feature_attention, BIB:mcadams_maunsell1999_v4_tuning |
| I6 | Normative question: when does VDA gain over optimal criterion + validity-driven attention; null-result / experimental-design motivation | framing | ORIG §1 |
| I7 | Finding 1 preview: criterion *typically* dominant; CF median $\approx0.76$, concentrated $[0.30,1.00]$; central tendency w/ tail, not a floor; $\corr>0$ shifts mass toward attention | distributional / central-tendency | LEDGER:C1; SIM:C1--cf-distribution |
| I8 | Finding 2 preview: VDA advantage non-monotonic in $\Rsens$, peaks cost-dominant; closed-form $\rdagger(\val)$ lower edge | confirmed + closed form | LEDGER:C2; SIM:C2--vda-vs-r-vfamily |
| I9 | Finding 3 preview: VDA concentrated in a graded regime (low $\valid$, high $\val$, moderate/cost-dominant $\Rsens$, low $f_0$); contour band, not "negligible regardless" | graded / quantitative | LEDGER:C3; SIM:C3--iso-vda-Vv |
| I10 | Finding 4 preview: no inversion under predictive cues, conditional on $\valid\ge 1/\Nloc$; anti-cue inversion ($\valid<1/\Nloc$) a new falsifiable prediction | conditional theorem + new prediction | LEDGER:C4; SIM:C4--anti-cue-inversion |
| I11 | Outside the graded VDA regime (incl. many standard cueing paradigms), optimal-criterion observer loses little treating attention as value-blind | bounded restatement of ORIG §6/§5.2 | ORIG §6; LEDGER:C1, LEDGER:C3 |

**Strength check.** I7 states the C1 result as a distribution (median
0.76, $[0.30,1.00]$), never the retracted categorical $[0.60,0.96]$
floor. I9 states C3 as a graded contour band, explicitly correcting the
original's "negligible regardless of other parameters". I10 states C4 as
conditional on $\valid\ge1/\Nloc$ with the anti-cue inversion as a *new*
prediction, never the original's unconditional "never". No assertion
exceeds its ledger row. Provenance verified.

---

## Model (`sections/model.tex`) — integrated SY-002 (2026-05-30)

| # | Assertion (paraphrase) | Strength | Artifact(s) |
| --- | --- | --- | --- |
| M1 | Task: $\Nloc\ge2$ locations, one cued; cue conveys value $\val\ge1$ (uncued worth 1) and validity $\valid\in[1/\Nloc,1]$ (uncued each $(1-\valid)/(\Nloc-1)$); change trial w.p. 0.5 | framing | ORIG §2.1 |
| M2 | Per-location SDT: $\HR_i=\Phinorm(\dprime_i/2-c_i)$, $\FAR_i=\Phinorm(-\dprime_i/2-c_i)$ (Eq. sdt-marginal) | framing | ORIG §2.1 (Eqs.1–2); RB:model.tex Eq. eq:sdt-marginal; BIB:MullerFindlay1987, BIB:posner1980_orienting |
| M3 | Allocation: $\alphacued\in[0,1]$ to cued, $\alphauncued=(1-\alphacued)/(\Nloc-1)$ each uncued; $\alphacued+(\Nloc-1)\alphauncued=1$; uniform $=1/\Nloc$ | framing | ORIG §2.2 |
| M4 | Transfer $f(a)=f_0+(1-f_0)h(a)$, $h\in\{a,\sqrt a,a^{0.3},a^2\}$, $h(0)=0,h(1)=1$; $\dprime_{\mathrm{base}}=\dprimemax f(1/\Nloc)$ | framing | ORIG §2.3 (Eqs.3–4); RB:model.tex Eq. eq:transfer |
| M5 | Asymmetry: $\benefit(\Rsens)=2\Rsens/(\Rsens+1)$, $\cost(\Rsens)=2/(\Rsens+1)$; $\benefit+\cost=2$, $\benefit/\cost=\Rsens$; benefit-/cost-dominant interpretation | framing | ORIG §2.3 (Eqs.5–6); RB:model.tex Eq. eq:beta-gamma; BIB:reynolds_heeger2009_normalization, BIB:treue_martinez_trujillo1999_feature_attention, BIB:mcadams_maunsell1999_v4_tuning |
| M6 | $\dprime_c,\dprime_u$ map (Eqs. dprime-cued/uncued); $\alphacued<1/\Nloc$ role-reversal + clamp $\ge0$; $\Rsens=1$ symmetric smooth centre | framing | ORIG §2.3 (Eqs.7–8); RB:model.tex Eqs. eq:dprime-cued/uncued; LEDGER:C5 (smooth-centre wording) |
| M7 | Two reward variants: A ($\CR=\valid\val+(1-\valid)$), B ($\CR=1$); expected reward Eq. expected-reward; $\PnoFA$ no-FA prob | framing | ORIG §2.4 (Eq.9); RB:model.tex Eq. eq:expected-reward |
| M8 | Independence enters (\ref{eq:expected-reward}) only through $\PnoFA$; under independence $\PnoFA^{\mathrm{indep}}=\Phinorm(b_c)\Phinorm(b_u)^{\Nloc-1}$, $b_i=c_i+\dprime_i/2$ | framing + locus | ORIG §2.4 ($\PnoFA$ defn); RB:model.tex Eq. eq:pnofa-indep; DERIV:A1--rho-channel.md §1 |
| M9 | Promote A1 to equicorrelation $\corr\in[0,1)$ (Eq. equicorr-cov); one-factor rep; exact 1-D integral $\PnoFA(\corr)$ (Eq. pnofa-rho, boxed); GH-64 quadrature, err $\le10^{-15}$ | three levers, not two (mechanism) | LEDGER:A1; RB:model.tex Eq. eq:pnofa-rho; DERIV:A1--rho-channel.md §2; `Rebuild/model/core.py:p_no_fa_point/_grid` |
| M10 | Recovery contract $\PnoFA(0)$ = product (Eq. rho-zero-recovery); $\corr=0$ reproduces inherited reward/VDA/CF to FP identity (7/7 pass); empirical band $\corr\in[0,0.4]$ brackets V4 $\corr\approx0.2$ | confirmed (recovery) | LEDGER:A1; RB:model.tex Eq. eq:rho-zero-recovery; `Rebuild/model/tests/test_recovery.py` (sha256 d3c62215…); BIB:CohenMaunsell2009 |
| M11 | Equicorrelation a deliberate 1-param simplification; structured covariances break the 1-D reduction (scoped limitation); Slepian monotonicity $\PnoFA(\corr)\ge\PnoFA(0)$ | bounded / scoped | LEDGER:A1; RB:model.tex; DERIV:A1--rho-channel.md Prop.3.1; BIB:RuffCohen2016, BIB:Srinath2021, BIB:Slepian1962 |
| M12 | Four nested policies P1 (joint optimum), P2 (value-blind attention), P3 (uniform attention, criteria optimised), P4 (floor) | framing | ORIG §2.5; RB:model.tex |
| M13 | Reward-gain decomposition: criterion gain $=\Rpthree-\Rpfour$, validity-attention gain $=\Rptwo-\Rpthree$, $\VDA=\Rpone-\Rptwo$ (Eqs.10–12); $\CF=(\Rpthree-\Rpfour)/(\Rpone-\Rpfour)$ | framing | ORIG §2.5 (Eqs.10–12); RB:model.tex Eqs. eq:vda-def, eq:cf-def |
| M14 | Three-lever Definition (criterion / sensitivity / decorrelation); decorrelation is the lever the inherited model held at $\corr=0$; the §5.5 upper-bound claim is an empirical $\partial\VDA/\partial\corr$ question deferred to Results/Discussion | three levers, not two | LEDGER:A1 (Definition def:three-levers, RB:model.tex); BIB:CohenMaunsell2009, BIB:RuffCohen2016, BIB:Srinath2021, BIB:Slepian1962 |

**Strength check.** The Model carries machinery only. The CF metric is
*defined* (M13) and its distribution is explicitly deferred to Results
(no "$[0.60,0.96]$" floor appears here). The §5.5 "upper bound on VDA"
claim is named but *not asserted* — M14 frames it as an open empirical
question routed to Results/Discussion, so the categorical inherited
claim is neither restated nor rebutted prematurely. The decorrelation
lever (M9–M11, M14) is stated at LEDGER:A1 strength as a model parameter
with a FP-identity recovery contract, not as a result. Gap G-001 marks
the one missing artifact (original Figure 1). Provenance verified.


## Results §4.1 — criterion typically dominates (`sections/results.tex`, `sec:results-criterion`) — integrated SY-003 (2026-05-30)

Results header + four-finding orienting paragraph + §4.1 (the original's
"Criterion Adjustment Dominates Value Encoding", finding C1). Subsequent
findings (4.2–4.6) appended by SY-004/006/007.

| # | Assertion (paraphrase) | Strength | Artifact(s) |
| --- | --- | --- | --- |
| R0 | Results = four findings developing one argument (criterion typically dominant → VDA non-monotonic in $\Rsens$ → graded VDA regime → no inversion except anti-cue corner); $\corr$ reported alongside each as a sensitivity | framing / signposting | ORIG §4 (section structure); LEDGER:C1–C4; RB:model.tex `def:three-levers` |
| R1 | $\CF$ = share of value-related gain captured by the criterion lever alone (defined in Model, Eq. eq:cf-def); criterion *typically* dominant | distributional / central-tendency | ORIG §4.1; RB:model.tex Eq. eq:cf-def |
| R2 | Original reports $\CF\in[60\%,96\%]$ categorically, "always single largest contributor"; reconstruction corrects to central tendency with a tail | correction (ledger-bound) | ORIG §4.1 (the corrected wording); LEDGER:C1 |
| R3 | CF distribution over the 4,410-cell sweep at $(\Nloc,\dprimemax,f_0,h)=(4,2,0.5,\sqrt{})$, $\corr=0$: median 0.7552 (A) / 0.7682 (B); strict min 0.5587 (A) / 0.3040 (B); both reach 1.00; 8% of var-B cells < 0.50 (Table cf-distribution, Fig cf-histogram) | distributional | LEDGER:C1; SIM:C1--cf-distribution (sha256 91fc4692…); RB:results.tex tab:cf-distribution, fig:cf-histogram |
| R4 | Categorical $[0.60,0.96]$ floor fails at both ends (min below 0.60/0.50; max = 1.00 above 0.96) | correction (ledger-bound) | LEDGER:C1; SIM:C1--cf-distribution |
| R5 | Regime structure: $\CF$ monotone-decreasing along $\Rsens$ (cost-dom. median ≥0.90 → benefit-dom. low-$\valid$ corner median 0.61 A / 0.51 B, min 0.30; frac<0.6 = 37% A / 78% B) (Table cf-quadrants, Figs cf-heatmap, cf-curves) | distributional / regime | LEDGER:C1; SIM:C1--cf-distribution (block quadrant_breakdown); RB:results.tex tab:cf-quadrants, fig:cf-heatmap, fig:cf-curves |
| R6 | Original's r-axis ordering (96% cost-dom / 73% symmetric / 64% benefit-dom) reproduced as quadrant medians; the "$\CF\to1$ small-$\Rsens$, declines large-$\Rsens$" intuition survives, the categorical bound does not | framing + correction | ORIG §4.1; LEDGER:C1; SIM:C1--cf-distribution |
| R7 | $\corr$ sensitivity (the §5.5 retraction along the CF axis): independence upper-bounds the *criterion fraction* (var A only), not VDA. $\corr{:}0\to0.2$ triples var-A frac<0.6 (0.07→0.22), min crosses below 0.50, $\CF$ decreases in 84% of var-A cells (median $\Delta\CF=-0.035$); var B mixed (64% dec / 24% inc) → not an upper bound there | distributional / variant-dependent (LEDGER:A1, C1) | LEDGER:C1, LEDGER:A1; SIM:C1--cf-distribution ($\corr=0.2$, blocks cf-rho-sensitivity, delta_distribution); RB:results.tex tab:cf-rho-sensitivity, tab:cf-delta-distribution; BIB:CohenMaunsell2009 |
| R8 | Conservation-family band: median robust (A $-0.0012$ / B $-0.0042$) but tail rule-dependent — additive→multiplicative doubles frac<0.5 (4.0%→8.3% combined), 191 cells flip $\CF{\ge}0.5\to{<}0.5$ with 0 reverse, var-B min deepens 0.304→0.231 | distributional band | LEDGER:C1; SIM:A3--conservation-band (sha256 055bf4ec…) |

**Strength check.** §4.1 states C1 only as a distribution/central
tendency: the median (≈0.76) carries the "criterion typically dominates"
reading and the categorical $[0.60,0.96]$ floor is explicitly retracted
at both ends (R2, R4). "Always the single largest contributor regardless
of $\Rsens$" is corrected to "typically dominant", with the explicit
benefit-dominant low-validity corner where it cedes the lead (R5). The
§5.5 "upper bound on VDA" claim is corrected to "upper-bounds the
criterion fraction, variant A only" (R7) — the carried-over A1 retraction
from SY-002, kept at LEDGER:A1 strength (variant B reported as a
sensitivity, not a uniform claim). No assertion exceeds its ledger row.
Provenance verified.

**Original wording corrected (auditable).**
- ORIG §4.1 "the criterion fraction ranges from 60% to 96% across all
  $(r,V,v)$ combinations tested" → "median $\CF\approx0.76$; concentrated
  in $[0.30,1.00]$; categorical $[0.60,0.96]$ retracted at both ends".
- ORIG §4.1 "Criterion adjustment is always the single largest
  contributor to value-related reward" → "criterion adjustment is
  *typically* the dominant lever; in the benefit-dominant, low-validity
  corner it cedes the lead to attention re-allocation (variant-B median
  0.51, min 0.30)".
- ORIG §5.5 (folded in here along the CF axis) "independent-noise results
  are an upper bound on the VDA benefit" → "independence upper-bounds the
  *criterion fraction*, and only in variant A (one-sided, 84% of cells);
  variant B is mixed".

**Re-narrativisation / figure decision (logged).** The original §4.1
leads with Figure 2 (reward-decomposition stacked bars at $v{=}5$,
$V{\approx}0.5$). No rebuilder artifact regenerates that bar chart, but
the reward-gain decomposition it depicts is the criterion/validity/VDA
split already typeset in the Model (Eqs. eq:gain-criterion,
eq:gain-validity, eq:vda-def). The rebuild deliberately *replaces* the
categorical bar chart with the distributional figure cf-histogram
("the figure that replaces the inherited categorical-floor language",
RB:results.tex). §4.1 therefore leads with cf-histogram rather than a
reconstructed Figure 2 — a supersession, not a gap. **No new gap opened.**

## Results §4.2 — VDA non-monotonic in $\Rsens$, closed-form escape threshold (`sections/results.tex`, `sec:results-vda-nonmonotonic`) — integrated SY-004 (2026-05-30)

The confident centerpiece (finding C2): $\VDA(\Rsens)$ rises out of zero,
peaks, decays; closed-form escape threshold $\rdagger(\val)$ marks the
lower edge of the active band; decorrelation effect is $\val$-signed.
Reported under additive conservation at $\valid=0.5$. No assertion
exceeds its ledger row; the non-monotonicity is stated plainly (its
licensed ceiling is the confident centerpiece per LEDGER:C2 / mission §3).

| # | Assertion (paraphrase) | Strength | Artifact(s) |
| --- | --- | --- | --- |
| V0 | $\VDA(\Rsens)=\Rpone-\Rptwo$ is non-monotonic in the benefit/cost ratio: rises from 0, interior peak, decays to 0 | confident centerpiece | LEDGER:C2 (CONFIRMED-UNDER-ATTACK); RB:model.tex eq:vda-def; SIM:C2--vda-vs-r-vfamily (sha256 09ecef3c…) |
| V1 | Closed-form escape threshold $\rdagger(\val)=K_u(\val)/[(\Nloc-1)K_c(\val)]$ from $\partial_\alpha\Rpone\|_{1/\Nloc}=0$, with $K_c,K_u$ as displayed (Eqs eq:r-dagger, eq:K-c, eq:K-u); theorem of model defs, derivation deferred to Supplementary | analytic (theorem) | LEDGER:C2; RB:results.tex eq:r-dagger/eq:K-c/eq:K-u; derivation Rebuild/derivations/C2--non-monotonic-vda-rho.md (Prop 2.1) |
| V2 | $\val$-family numerics at $(4,2,0.5,\sqrt{},0.5)$ var A: $\rdagger$ falls 0.343 ($\val{=}1$) → 0.016 ($\val{=}10$); $c_c^\star,c_u^\star,K_c,K_u$ per Table r-dagger-family | numerical | LEDGER:C2; SIM:C2--vda-vs-r-vfamily (sha256 09ecef3c…); RB:results.tex tab:r-dagger-family |
| V3 | Peak $r^\star>\rdagger(\val)$ for every $\val$ (margin +0.28..+0.35), clusters below $\rdagger(1)\approx0.343$; 84-pt log-grid; VDA supported on $(\rdagger(\val),\rdagger(1))$ | numerical + mechanism | LEDGER:C2; SIM:C2 (84-pt grid); RB:results.tex tab:peak-vs-threshold |
| V4 | Peak height grows monotonically with $\val$: $\VDA\approx0.012$ ($\val{=}2$) → 0.183 ($\val{=}10$); Fig vda-curves-vfamily | numerical | LEDGER:C2; SIM:C2--vda-vs-r-vfamily; RB:results.tex fig:vda-curves-vfamily |
| V5 | Decorrelation $\corr:0\to0.2$ suppresses peak for $\val\le8$ ($\Delta\VDA^\star$ down to $-0.004$ at $\val{=}3$), amplifies at $\val{=}10$ ($+0.001$); $r^\star$ drifts up (0.501→0.631 at $\val{=}2$); Table rho-sensitivity | distributional/signed | LEDGER:C2 + LEDGER:A1 ($\val$-dependent sign-flip); SIM:C2 ($\corr\in\{0,0.2\}$); RB:results.tex tab:rho-sensitivity |
| V6 | $\corr$-aware $\rdagger(\val;\corr)$ via 1-D GH gradients gives $\rdagger(\val;0.2)>\rdagger(\val;0)$ at every $\val$ (+3% at $\val{=}1$ to +30% at $\val{=}8$); sign matches empirical peak drift at all $\val\neq1$; decorrelation not a uniform attenuator — enhances VDA in benefit-dominant high-value corner | directional (ledger-bound) | LEDGER:C2 + LEDGER:A1; derivation Rebuild/derivations/C2--non-monotonic-vda-rho.md (Prop 4.1); SIM:C2 drift sign-match 5/5 |
| V7 | $\corr$ effect signed by value structure = operational content of the third lever (Def def:three-levers) | framing | RB:model.tex def:three-levers; LEDGER:A1 |

**Provenance verified.** Every number in Tables r-dagger-family,
peak-vs-threshold, rho-sensitivity and both figures comes from
SIM:C2--vda-vs-r-vfamily (output sha256 09ecef3c…); the closed-form
$\rdagger$ and its $\corr$-aware extension from the C2 derivation file.
The §5.5 "upper bound on VDA" reframing (folded along the VDA axis here:
decorrelation does not uniformly attenuate VDA) is kept at LEDGER:A1
strength, stated positively as a model property. No floors; the
non-monotonicity stated at its confident-centerpiece ceiling. Figures
r_dagger_vs_v.png and vda_curves_vfamily.png copied from
SIM:C2--vda-vs-r-vfamily/output/figures/. No new gap.

**Forward references (resolve now, content lands later).** The
$\corr$-aware threshold derivation and its drift table are referenced as
Supplementary (`sec:appendix`, exists as a stub) — content to be written
under SY-011. Ref resolves; no dangling \ref.

## Results §4.3 — graded regime (`sections/results.tex`, `sec:results-graded`)

| id | assertion | strength | backing |
| --- | --- | --- | --- |
| G0 | VDA is materially large only in a concentrated corner of $(\valid,\val)$ — low validity, high value contrast, moderate-low $\Rsens$ — with a graded boundary | graded/quantitative | LEDGER:C3 (graded/quantitative; categorical high-$\valid$ claim replaced by contour band); RB:results.tex sec:results-c3 |
| G1 | Grid: $(4,2,0.5,\sqrt{})$ var A, $\valid\in[0.25,1]$ (31 pts), $\val\in[1,10]$ (19 pts), $\Rsens\in\{0.3,1,3\}$, $\corr\in\{0,0.2\}$ = 3,534 cells; Fig iso-vda-contours | numerical (sweep design) | LEDGER:C3; SIM:C3--iso-vda-Vv (sha256 72820559…); RB:results.tex fig:iso-vda-contours |
| G2 | Median $\VDA\le0.007$ in every panel; peak 0.173 ($\Rsens{=}0.3,\corr{=}0$) → 0.062 ($\Rsens{=}3$); frac$\ge$0.05 falls 28.7%→1.2%; Table graded-marginals | distributional | LEDGER:C3; SIM:C3; RB:results.tex tab:c3-marginals |
| G3 | Corner flattens along $\Rsens$: $\VDA\approx0.17$ ($\Rsens{=}0.3$) → 0.16 ($\Rsens{=}1$) → $\le0.06$ ($\Rsens{=}3$) | numerical | LEDGER:C3; SIM:C3; RB:results.tex fig:iso-vda-contours |
| G4 | High-$\valid$ probe (Table graded-highV): $\valid\ge0.95$ floor for all; $\valid\ge0.80$ floor at $\corr{=}0$, $\corr$-conditional max 0.0032 at $\Rsens{=}3$; $\valid\ge0.60$ peak 0.1432 ($\corr{=}0$) / 0.1639 ($\corr{=}0.2$) at $\Rsens{=}0.3$ | conditional/quantitative | LEDGER:C3; SIM:C3 (high_V_probe block); RB:results.tex tab:c3-highV-probe |
| G5 | Design guidance: $\valid\gtrsim0.95$ unconditional, or $\gtrsim0.8$ if $r_{SC}\lesssim0.2$; $\valid\ge0.75$ too permissive; $\valid\in[0.6,0.8)$ cost-dominant admits peak $\VDA\approx0.16$ | quantitative recommendation | LEDGER:C3 (graded contour-band design statement); RB:results.tex §5.2-replacement blockquote; CohenMaunsell2009 ($r_{SC}\approx0.2$) |
| G6 | Sign of $\partial\VDA/\partial\corr$ varies over plane: $\Rsens{=}0.3$ suppression-dominated (37.2%), $\Rsens\in\{1,3\}$ amplification-dominated (52.8%/54.0%); Fig iso-vda-drho, Table graded-signflip | distributional/signed | LEDGER:C3 + LEDGER:A1 (sign-flip generalisation, cross-axis); SIM:C3 (rho_sensitivity block); RB:results.tex tab:c3-sign-flip |
| G7 | Dormant-cell amplification: $(\valid,\val,\Rsens)=(0.7,10,0.3)$ lifts $\VDA$ 0.0007→0.0676 at $\corr{=}0.2$ ($\approx96\times$); flagged falsifiable, deferred to Discussion | numerical observation (positive prediction) | LEDGER:C3 + LEDGER:A1 (strongest single amplification in sweep); SIM:C3 |

**Provenance verified.** Every number in Tables graded-marginals,
graded-highV, graded-signflip and all three figures
(iso\_vda\_contours, vda\_at\_high\_V, iso\_vda\_drho) comes from
SIM:C3--iso-vda-Vv (output sha256 72820559…), recovery vs the C2 anchor
$(\valid,\val,\Rsens,\corr)=(0.5,5,1,0)$ at $|\Delta\VDA|=1.27\text{e-}7$.
The concentrated-regime finding stated at LEDGER:C3 graded ceiling: a
contour band, not a categorical floor; the high-validity design
guidance stated positively as the model's own prediction, with the
$\corr$-conditional caveat and the $\valid\ge0.75$ permissiveness as
quantitative facts of the sweep. The $\val=1$ value-blind identity
($\VDA\equiv0$) is a model theorem (consistency check). Three figures
copied from SIM:C3/output/figures/. No floors. No new gap (all three
figures existed).

**Drift watch.** $\valid=0.95$/$0.80$ thresholds bracketed by the
$\valid$-grid step 0.025; a finer grid (not yet run) would sharpen
"$\gtrsim$" to a second decimal — stated as scope, not claimed. variant-B
and conservation-family bands forward-referenced to Discussion
(`sec:discussion`); ref resolves (stub exists; content lands SY-008).

## Results — no inversion under predictive cues (`sec:results-noninversion`, SY-007)

Grounding map (assertion → evidence). Source: the C4 anti-cue-inversion
simulation output (results.json: step_A tally, step_B rows, step_C
incidence, step_D map) and the C4 formal derivation; strength ceiling =
LEDGER:C4 (CONFIRMED-CONDITIONAL). All stated positively; no
comparison/correction framing reaches the page.

- **N0** Under a predictive cue ($\val\ge1$) the optimum never falls
  below uniform $1/\Nloc$ across the primary range → LEDGER:C4
  "$\alpha^\star_{global}\ge1/N$ at every cell of the 4,410-cell sweep";
  step_B 0/12 inversions.
- **N1** Value-weight inequality eq:value-weight $w_c\ge w_u \iff
  \valid\ge1/[(\Nloc-1)\val+1]$; universal worst-case $\valid\ge1/\Nloc$
  at $\val=1$ → LEDGER:C4 value-weight inequality + derivation §6 (Eq 6.2).
- **N2** Closed-form boundary left-derivative eq:boundary-derivative and
  threshold eq:r-inv $\rstarinv=(\Nloc-1)A_0/B_0$ → LEDGER:C4 closed-form
  local threshold; derivation §2–§3 (Eqs 2.4–2.5, 3.3).
- **N3** Symmetric-corner identity eq:r-inv-corner
  $\rstarinv(1/\Nloc,1,\Nloc,\CR,\corr)=1$ exactly, $\Nloc/\CR/\corr$-
  independent → LEDGER:C4 Proposition 5.1; recovered to FP identity in
  all 4 panels (min_r_inv=1.0000).
- **N4** Table noninv-tally (closed-form $\rstarinv$ tally, 4 panels;
  48.6% in [0.1,10] at $\corr=0$ → 51.9% at $\corr=0.2$; median falls
  13% var-A / 21% var-B) → step_A.tally block keys; numbers verbatim
  from LEDGER:C4 + source results table.
- **N5** Zero global inversions, 12-probe sweep, Table noninv-sweep
  (numbers $\alpha^\star\in[0.95,0.98]$, $R_{global}>R_{left}$) →
  step_B.rows; LEDGER:C4 "Step B 0/12".
- **N6** Counter-predictive inversion as new falsifiable prediction:
  36.1% ($\corr=0$) / 34.7% ($\corr=0.2$) on the $\valid<1/\Nloc$
  sub-grid; Table anticue stratifiers (75% at $\val=1$, 12.5% at
  $\val=5$; boundary $1/16$ at $\val=5$) → LEDGER:C4 anti-cue block,
  step_C.incidence; stated as a positive new prediction (LEDGER licenses
  "added as a new falsifiable prediction").
- **N7** Fig r-inv-map / er-alpha-anticue / alpha-star-map copied from
  the C4 sim output figures; captions describe content + parameters only.
  alpha-star-map: 2.21% incidence, 0 in predictive regime → step_D.
- **N8** Behavioural alignment (Wang-Theeuwes 2018, Wang-Samara-Theeuwes
  2019, Kong et al 2020, Failing-Theeuwes 2018, Hickey 2010, Posner 1980)
  → LEDGER:C4 behavioural-literature paragraph; all 6 bib keys pre-exist.
- **Robustness** (the SY-007 robustness element): no-inversion holds in
  both conservation variants; decorrelation shifts $\rstarinv$ median
  13–21% but leaves 0 predictive-cue inversions and ±1 cell counter-
  predictive → LEDGER:C4 A1 cross-axis (25 vs 26).

**Drift watch.** Counter-predictive sweep is variant-A only; variant-B
higher-incidence band forward-referenced to Discussion (`sec:discussion`,
SY-008) — ref resolves (stub exists). Full derivation of
eq:boundary-derivative–eq:r-inv-corner forward-referenced to Supplementary
(`sec:appendix`, SY-011) — ref resolves (stub exists). $\valid$-grid step
0.05 brackets the inversion-onset validity to $\pm0.05$ at $\val=1$;
stated as scope. No floors; no "regardless of"; the LEDGER:C4
"regardless of $\Rsens$" wording is NOT reproduced — replaced by the
closed-form bimodality + conditional theorem, positive.

## Discussion (`sections/discussion.tex`) — DONE (SY-008, 2026-05-30)

Every scientific assertion in the Discussion maps to an internal artifact
(used silently; none named in the manuscript). Editorial connective tissue
(synthesis sentences, signposting) asserts nothing beyond the rows below.

- **D0** Opening synthesis (four findings recapped: criterion typically
  dominant ~3/4 of reward gain; VDA non-monotonic in $\Rsens$ with edge
  $\rdagger(\val)$; graded corner; conditional no-inversion theorem
  $\valid\ge1/\Nloc$) → LEDGER:C1/C2/C3/C4; restates established results,
  no new claim.
- **D1** Why criterion dominates: criterion is "free" (no perceptual
  reallocation), VDA pays a trade-off; residual value most economically
  booked into thresholds under predictive cues. CF median 0.7552 (var A)
  / 0.7682 (var B), concentrated $[0.30,1.00]$ → LEDGER:C1 +
  `sec:results-criterion`. Mechanism reading is interpretation of the
  model structure (model.tex), not a new number.
- **D2** Criterion cedes in benefit-dominant low-validity corner (CF
  falls, VDA material) → LEDGER:C1 (contested low-validity corner) +
  `sec:results-criterion`.
- **D3** $\Rsens$ = benefit/cost asymmetry = relative efficacy of
  enhancement vs suppression; biological reading via normalization/gain
  literature → cites reynolds_heeger2009, mcadams_maunsell1999,
  treue_martinez_trujillo1999, carrasco2011 (all pre-existing bib keys);
  grounded in model.tex asymmetry definition + intro framing. Hedged as
  interpretation; NO neural-implementation claim (per LEDGER non-claim).
- **D4** Non-monotonicity reading (peak in cost-dominant window; large
  $\Rsens$→value-blind already attends; small $\Rsens$→nobody
  re-allocates; edge $\rdagger(\val)$, `eq:r-dagger`) → LEDGER:C2
  (confident centerpiece) + `sec:results-vda-nonmonotonic`.
- **D5** Design guidance: $\valid\ge0.95$ floor unconditional;
  $\valid\ge0.80$ survives at $\corr=0$, small $\corr$-conditional
  signal otherwise; $\valid\ge0.75$ too permissive (peak ~0.16 in
  $[0.60,0.80)$ cost-dominant) → LEDGER:C3 boxed design recommendation +
  `sec:results-graded`. Standard cueing paradigms in dormant regime →
  intro framing (already stated) + C3.
- **D6 (new prediction 1)** Anti-cue inversion: $\valid<1/\Nloc$ → inverted
  allocation optimal in substantial cell fraction; sharp boundary
  $\valid<1/[(\Nloc-1)\val+1]$; absent in predictive regime; falsifiable
  signature distinguishing re-allocation from criterion shifts →
  LEDGER:C4 (anti-cue 36.1% / 34.7%; sharp v-boundary) +
  `sec:results-noninversion`.
- **D7 (new prediction 2)** Decorrelation an active lever, sign of
  $\partial\VDA/\partial\corr$ set by $\Rsens$ (suppress at small $\Rsens$,
  amplify at $\Rsens\gtrsim1$); dormant-cell amplification $0.0007\to0.0676$
  (~100×) at the empirical $\corr=0.2$ anchor → LEDGER:C3 (iso_vda_drho
  sign-flip; dormant-cell 96× at (0.7,10,0.3)) + `sec:results-graded`;
  cites CohenMaunsell2009, RuffCohen2016, Srinath2021.
- **D8 (new prediction 3)** Conservation-form sensitivity of the split:
  additive→multiplicative leaves median fixed (<0.005) but ~doubles
  frac $\CF<0.5$ (4.0%→8.3%), 191 cells flip with 0 reverse; tail size a
  structural observable. Equal-reward (variant-B) deeper tail + lower
  median $\rstarinv$ → larger attention-favourable region + higher anti-cue
  incidence → LEDGER:C1 (conservation band) + LEDGER:C4 (variant-B
  median drop) + `sec:results-criterion` robustness paragraph +
  `tab:noninv-tally`. Resolves the §4.1/§4.3/§4.4 forward-refs to
  `sec:discussion`.
- **D9** Limitations (all positive-voiced scope statements): conservation
  rule a one-parameter family (`eq:beta-gamma`, additive/multiplicative
  endpoints); heterogeneity (per-location $\Rsens$, $\Nloc$-simplex) leaves
  optima ~intact, closed-form spread-dependence not derived; decision-noise
  channel $\sigma_i(\alpha)$ a natural further axis alongside $\corr$, not
  included; transfer-function family (mechanism stmts generic in $f$,
  `def:three-levers`/`eq:r-dagger`); equicorrelation only (structured
  covariance out of scope); normative + stationary, no learning, no neural
  implementation claim beyond the $\Rsens$↔gain-control correspondence →
  all grounded in `Rebuild/manuscript/sections/limitations.tex` scope
  content (lifted as positive scope, meta-framing stripped) + LEDGER
  non-claims row.

**Strength check.** Nothing exceeds the ledger: C1 stated distributionally
(median + tail, no floor); C2 as the confident centerpiece; C3 graded /
contour-band; C4 as a conditional theorem + anti-cue prediction; the
decorrelation sign as a model property; conservation/variant sensitivity
as bands. Biological reading is explicitly hedged ("a natural reading",
"consistent with") and paired with the explicit no-neural-claim limitation.

**Firewall.** Zero meta. The limitations content was lifted from internal
source prose with all "rebuilt/inherited/live verdict/reviewer" framing
removed and restated as the model's own scope. No comparison-hedges; the
conservation/variant findings are stated as positive structural properties,
not as corrections of an absent statement.

## Methods (`sections/methods.tex`) — DONE (SY-010)

Operational documentation of the model and its simulation protocol. Every
number is a procedural fact (grid sizes, node counts, tolerances), not a
finding; the findings themselves are stated and traced in Results. Each
assertion is backed by the written Model section (equations lifted by
`\ref`), the validated sim grids, and the model code base.

- **ME1** Task/decision recap (change prob 0.5; validity split; per-location
  criteria; rewards $\val$/$1$/$\CR$; `eq:expected-reward`) + headline cell
  $(\Nloc,\dprimemax,f_0,h)=(4,2,0.5,\sqrt\cdot)$ and the four `eq:h-forms`
  for transfer-function robustness → `sections/model.tex` (§2.1–2.3);
  `Rebuild/model/core.py` module-level cell constants (`N=4, D_MAX=2.0,
  F0=0.5, H_NAME="sqrt"`).
- **ME2** Benefit/cost via additive conservation `eq:beta-gamma`
  ($\benefit+\cost=2$); conservation-form sensitivity as a one-parameter
  power-mean family deferred to Supplementary; variant A ($\CR=\valid\val
  +(1-\valid)$) vs variant B ($\CR=1$) → `sections/model.tex` §2.4;
  `Rebuild/derivations/A3--power-mean-conservation.md`; `core.py`
  `beta_gamma(r, p=1.0)`.
- **ME3** Correlated channel: `eq:equicorr-cov`/`eq:pnofa-rho`; GH-64
  quadrature, ≤$10^{-15}$ vs 128-node across $\corr\in\{0,.05,.1,.2,.3,.4\}$;
  headline $\corr\in\{0,0.2\}$ anchored to V4 $r_{SC}\approx0.2$
  (`CohenMaunsell2009`) → `sections/model.tex` §2.4; C2 README (GH64-vs-GH128
  ~1e-16); `core.py` `gauss_hermite(64)`, `p_no_fa_point`.
- **ME4** Policy optimisation: criterion grid 121 pts, $c\in[-3,3]$,
  $\Delta c=0.05$; floor fixes $c=0$; attention grid $[1/\Nloc,1]$ for
  P1/P2, extended to $[0.02,1]$ for distributional/anti-cue sweeps,
  $\alphacued=1/\Nloc$ for P3/P4; exhaustive search; value-blind allocation
  cached per config → `core.py` `C_GRID=arange(-3,3,0.05)` (121),
  `default_alpha_grid` (step 0.005), C1 `run.py` `ALPHA_GRID` (0.02 step,
  50 pts), `_alpha_opt` brute force, value-blind caching comment.
- **ME5** Four sweeps with exact grid sizes:
  (1) distributional 22 $\Rsens$ (logspace $[0.1,10]$+pinned 1) × 21
  $\valid$ × 5 $\val$ × 2 variants = 4,620 nominal, 4,410 valid (2,205/var)
  → C1 `run.py` `R_GRID`(22)/`V_GRID`(21)/`V_LIST`{1..5}, README n_valid=2205;
  (2) VDA(r) 83-pt log grid, $\val\in\{2,3,5,8,10\}$ → C2 README "83-point
  +pinned"; (3) iso-VDA $31\times19\times3\times2=3{,}534$ → C3 README;
  (4) inversion: closed-form $\rstarinv$ on $21\times5\times2\times2=420$,
  197-pt $\alpha$ verification at adversarial cells, anti-cue grid
  $\{0.05,.1,.15,.2\}\times\{1,3,5\}\times\{0.1,.5,1,3,5,10\}\times\{0,.2\}$,
  $\alphacued^*$ map $17\times16\times2=544$ → C4 README Steps A–D.
- **ME6** Validation: (i) recovery contract `eq:rho-zero-recovery` —
  $\corr{=}0$ quadrature = closed-form product `eq:pnofa-indep` to FP
  (max abs diff $<10^{-6}$ across the distributional grid); (ii)
  closed-form/grid agreement — $\rdagger(\val)$ orders against peak
  $\Rsens^*$ (Results §4.2), symmetric-corner identity
  $\rstarinv(1/\Nloc,1,\Nloc,\CR,\corr)=1$ `eq:r-inv-corner`; (iii) Slepian
  monotonicity sign check (`Slepian1962`) → C1 README recovery (FP-scale
  agreement), C2/C4 README recovery tables, `sections/results.tex`
  `eq:r-inv-corner`. NOTE: README cross-substrate numbers (1.47e-6, 48.6%
  vs 49.0%) are external comparisons — NOT cited; the FP-identity recovery
  is stated as an internal limit check only (`<1e-6`), the C4 percentages
  live in Results as model facts, not re-reported here.
- **ME7** Reproducibility: deterministic, no Monte-Carlo; fixed grids +
  quadrature nodes → bitwise-reproducible output; <2 min full sweep; Python
  + standard numerical/special-function libraries → C1 README ("Deterministic
  (no RNG; all grids fixed); re-running produces identical results.json",
  "~67 s"); `core.py` (no RNG).

**Strength check.** Methods asserts no finding; it documents procedure.
All grid sizes, node counts, and tolerances match the sim READMEs / code
to the digits stated. The recovery tolerance is stated conservatively
($<10^{-6}$) and as an internal limit check, never as agreement with an
external substrate.

**Firewall.** Zero meta. No reviewer/substrate/inherited/published framing;
the external recovery comparisons in the READMEs (vs "reviewer's
results.json") are deliberately not surfaced — validation is framed as the
model's internal $\corr\to0$ limit and closed-form/grid self-consistency.
No file paths, sha256, or sim ids in the prose. "Supplementary" not
"Appendix".

> **SY-009 coherence pass (2026-05-31, run C3D9A1F7).** Second
> interleaved consistency pass, over Results (§4.1–§4.4) + Discussion.
> **No assertion was added, removed, or changed in strength, and no number
> changed.** The pass corrected a cross-section terminology conflation
> between two orthogonal axes that the validated source keeps distinct:
> the **reward variant** (variant~A = value-coupled correct rejection
> $\CR=\valid\val+(1-\valid)$; variant~B = fixed $\CR=1$) and the
> **conservation rule** (additive $\benefit+\cost=2$ vs multiplicative
> $\benefit\cdot\cost=1$, a separate one-parameter family). Authority:
> Model §2.4 (`sections/model.tex`) and Methods §"Benefit, cost, and
> reward variants", both of which already define A/B as the reward
> variant; corroborated by the upstream source `model.tex` ("variant~A …
> $\CR=\valid\val+(1-\valid)$ … variant~B … $\CR=1$; the additive
> conservation rule is varied [separately]") and `extensions.tex`
> ($0.7552\to0.7540$ var-A, $0.7682\to0.7640$ var-B as additive→
> multiplicative — i.e. A/B persist across the conservation move, so they
> are orthogonal to it). Fixes: (1) "conservation variant"→"reward
> variant" wherever it labels A/B (7 spots in Results, incl. the
> `tab:cf-distribution`/`fig:cf-histogram` captions); (2) Results §4.1
> robustness paragraph reworded so additive/multiplicative are the
> conservation-family **endpoints** (swept within each reward variant),
> not "the two variants above"; (3) Results §4.2 "$\CR(\val)$ encodes the
> conservation rule"→"$\CR(\val)$ is the correct-rejection reward scaling
> set by the reward variant", with $\CR(\val)=1$ kept as the value-blind
> computational setting and additive conservation named as the (separate)
> weight rule; (4) Discussion opening: medians $0.7552$/$0.7682$
> re-attributed to the value-coupled / equal-reward **variants** (both at
> additive conservation), not to "additive rule"/"equal-reward
> convention"; (5) Discussion "New predictions": "the additive,
> value-weighted convention"→"the value-coupled reward variant". All other
> cross-checks passed without edits (cross-ref graph resolves; intro
> four-finding previews match body strength; dormant-cell ~96×↔
> "hundredfold", anti-cue boundary $\valid<1/[(\Nloc-1)\val+1]$, and the
> $\valid\ge0.95/0.80/0.75$ design thresholds all consistent across
> Results and Discussion; density glyph uniformly $\varphi$). Clean
> 3-pass build, 26 pages, 0 undefined refs/citations, 0 overfull boxes.

## Supplementary (`sections/appendix.tex`) — SY-011 (2026-05-31, run E8F1A0D4)

Four subsections, each assertion grounded in validated model material
(derivation files + reference implementation + the model write-up for
notation). Lifted to ledger strength; every meta tag stripped.

| # | Assertion | Backing |
|---|-----------|---------|
| P1 | One-factor representation `eq:one-factor` reproduces the equicorrelated covariance and makes locations conditionally independent given $Z$; integrating $Z$ out gives the exact 1-D integral `eq:pnofa-rho` | A1 decorrelation-channel derivation §2.1–2.3 (one-factor construction, conditional no-FA, exact orthant reduction); model write-up notation |
| P2 | 64-node Gauss–Hermite agrees with 128-node to $\le 10^{-15}$ across $\corr\in\{0,0.05,0.1,0.2,0.3,0.4\}$ | A1 derivation §2.5 (quadrature realisation); Model §reward (already states the same band, `eq:pnofa-rho`) |
| P3 | Orthant monotonicity Prop `prop:orthant-monotone` ($\PnoFA(\corr)\ge\PnoFA(0)$) | A1 derivation §3.1 Prop 3.1 (Slepian 1962 equicorrelated specialisation); cites `Slepian1962`, `Tong1990` |
| P4 | Per-policy reward monotone in $\corr$ Cor `cor:policy-monotone` | A1 derivation §3.2 Cor 3.2 (pointwise bound survives sup) |
| P5 | Two-channel sign of $\partial\VDA/\partial\corr$ (criterion-devaluation vs concentration-relaxation), flips with $\Rsens$ | A1 derivation §4.2–4.3; LEDGER:A1 (sign-flip in $r$, two competing channels) |
| P6 | Boundary collapse $\dprime_c=\dprime_u=\dprime_{\mathrm{base}}$; criterion optimum `eq:boundary-crit`; headline $(c_c^\star,c_u^\star)=(0.10,1.75)\to(0.05,1.80)$ at $\corr=0.2$ | C2 escape-threshold derivation §1.2, §3.2 (boundary config, $\corr$-aware P3 criterion shift) |
| P7 | $\corr$-aware gradient integrals `eq:gh-grad-c`/`eq:gh-grad-u`; reduce to $I_c^0,I_u^0$ at $\corr=0$ | C2 derivation §3.1 (differentiation under the integral, GH quadrature) |
| P8 | Boundary FOC `eq:boundary-foc-rho` with $K_c(\val;\corr),K_u(\val;\corr)$ `eq:Kc-rho`/`eq:Ku-rho` | C2 derivation §3.3; consistent with Results `eq:K-c`/`eq:K-u` at $\corr=0$ |
| P9 | Escape threshold Prop `prop:escape-rho` (boxed `eq:r-dagger-rho`); FD sign-flip 6/6 at $(\val,\corr)\in\{1,2,3\}\times\{0,0.2\}$ | C2 derivation §4 Prop 4.1 + §5.3 boundary-FD; LEDGER:C2 |
| P10 | Structural $\corr\to0$ recovery to `eq:r-dagger`; reproduces `tab:r-dagger-family` to $\le 5\times10^{-4}$ | C2 derivation §4.1, §5.1; cross-checked against the Results table values (0.343…0.016, exact match) |
| P11 | Drift `tab:r-dagger-rho-drift` ($\Delta\rdagger>0$ every $\val$; 5/5 sign-match vs `tab:rho-sensitivity`; abs drift $\le0.014$) | C2 derivation §5.2 (drift table, two findings) |
| P12 | Symmetric collapse at $\Rsens=1$; real-number identity Prop `prop:symmetric-recovery` | C5 symmetric-recovery material (real-number identity, universal claim); LEDGER:C5 |
| P13 | Bit-exact identity Prop `prop:bitexact-recovery` via Sterbenz lemma; off-band threshold `eq:sterbenz-threshold` ($f_0<1/3$) | C5 material (Sterbenz band $a=1.5$, $x\in[1.0,2.0]\subset[0.75,3.0]$); cites `Sterbenz1974`, `Goldberg1991`; LEDGER:C5 |
| P14 | $\Rsens=1$ is the smooth centre (slopes $\pm1/2$; reward diff $\approx0.084$/unit); conservation-form invariant | C5 material (smooth-centre continuity probe; conservation invariance) |
| P15 | Power-mean family `eq:power-mean`; closed-form weights `eq:power-mean-weights`; $p=1$ additive, $p=0$ multiplicative | A3 power-mean derivation §2 (closed-form weights); LEDGER:A3 |
| P16 | HLP monotonicity as KL closed form `eq:hlp-kl`; sign `eq:mono-sign`; FD cross-check $\le1.5\times10^{-10}$ | A3 derivation §3 (HLP–KL identity, Corollary, $p\to0$ limit) |
| P17 | Symmetric-corner identity Prop `prop:symmetric-corner` + recovery corollary `cor:symmetric-invariance` | A3 derivation §4 (full proofs) |
| P18 | Escape-threshold $p$-invariance Prop `prop:escape-invariance` (3-step proof) | A3 derivation §5 (full three-step proof; vanishing-bracket collapse); LEDGER:C2 ("free theorem", verified to FP identity) |
| P19 | CF chain rule `eq:cf-chain-rule`/`eq:dprime-of-p`; P3 invariance Prop `prop:p3-invariance`; empirical $\Delta\CF\le0$ over 4,410 cells (0 reverse flips; frac$<0.5$ $4.0\%\to8.3\%$; median moves $<0.005$); closed form open | A3 derivation §6 (chain-rule sign analysis, Prop, open status); LEDGER:A3/C1 (conservation band) |

**Grounding verified** — every assertion in the Supplementary has a row
above. **No figures** placed (the section is pure derivation); no new
gap opened. New real citation `Tong1990` added to `refs.bib`
(Springer, 1990) to back Prop `prop:orthant-monotone`.

> **Cross-section firewall fix (SY-011, content-preserving).** While
> sweeping, one pre-existing comparison-hedge in `sections/discussion.tex`
> ("…a substantial tail, not a categorical split") was rewritten to the
> positive "…a substantial tail across the parameter space." No number or
> claim strength changed.

## Coherence pass (SY-012) — whole paper, pre-abstract

Third interleaved coherence pass, end to end before the abstract. No new
scientific assertions; two cross-section parameter-grid descriptions were
brought onto the validated source and made mutually consistent. Both
fixes are content-preserving (no headline number, distribution, or claim
strength changed).

| ref | what was reconciled | source ground truth |
|---|---|---|
| X1 | Results §4.1 distributional-sweep $\Rsens$ grid: "$21$ log-spaced points" (which lands directly on $4{,}410$ with no drop) → "$22$ values ($21$ log-spaced plus a pinned $\Rsens=1$)", with the $4{,}620$-nominal / $4{,}410$-valid ($2{,}205$/variant) distinction now stated, matching Methods §sweeps. | `Rebuild/sims/C1--cf-distribution/run.py`: `R_GRID = np.unique(concat([logspace(log10(0.1),log10(10),21),[1.0]]))` → 22 r-values; `n_total = 22·21·5·2 = 4620`; `n_valid = 2205`/variant (one degenerate $\Rsens$-slice dropped). README "n_valid 2205". |
| X2 | VDA$(\Rsens)$ grid count harmonised: Results said "$84$ log-spaced points", Methods said "$83$ log-spaced ratios (… pinned)". Both → "$84$ (83 log-spaced + pinned escape/peak neighbourhoods)". | `Rebuild/sims/C2--vda-vs-r-vfamily/README.md`: "83-point + pinned log-spaced r-grid" (line 13) **and** "84-pt r-grid" (line 103) — i.e. 83 log-spaced ∪ pinned set = 84 total. |

**Grounding verified** — both reconciliations resolve to the C1/C2 sim
`run.py`/README, the authoritative grids. The valid-cell counts the prose
already reports ($4{,}410$; $2{,}205$/variant; peak located on the
84-point grid) are unchanged.

**Coherence checks passed without edits:** cross-reference graph fully
resolves (98 labels, 236 `\ref`/`\eqref` calls, 0 undefined on a 3-pass
build); all 11 `\includegraphics` targets present in `figures/` and each
referenced exactly once; notation consistent vs the `\newcommand` block
($\varphi$ density glyph, $\dprime_{\mathrm{base}}\!\equiv\!\dprime_b$,
three-lever symbols); intro four-finding previews match body strength;
the $4{,}410$ / $2{,}205$ / $3{,}534$ / $420$ / $544$ / $72$ sweep sizes
are now consistent across Results ↔ Methods; iso-VDA $31{\times}19{\times}3{\times}2$,
anti-cue $4{\times}3{\times}6$, and $\alpha^\star$ $17{\times}16$ grids agree.

**Placeholders (deliberate, not coherence defects):** GAP G-001 (model
attention-to-$\dprime$ illustration figure — open, owner-mediated) and
the abstract stub (written last, SY-013).

## Abstract (`sections/abstract.tex`) — SY-013, written last

Single unstructured paragraph (~205 words), no citations, no meta, written
from the finished body. Every sentence is a positive restatement of an
already-grounded body result, at its body / CLAIM_LEDGER strength.

| ref | abstract sentence | grounded in (body) | ledger |
|---|---|---|---|
| AB1 | Cued task; observer can adapt by criterion shift, attention re-allocation, or decorrelating the population code when noise is correlated across locations. | `sec:intro` ¶1–4; `sec:model` three-lever Defn `def:three-levers` | framing (C1/C2/C3/C4) |
| AB2 | Three levers within one optimisation; cross-location correlation a free parameter whose zero limit recovers the independent-noise case. | `sec:model` $\corr$ channel + `eq:rho-zero-recovery` (FP-identity recovery at $\corr\to0$) | model setup |
| AB3 | Criterion adjustment typically dominant, median ≈ three-quarters of the reward gain, with a substantial tail where attention contributes materially. | `sec:results-criterion`: median $\CF$ 0.7552 (A) / 0.7682 (B); `tab:cf-distribution`; left tail | C1 (distributional) |
| AB4 | Attention benefit non-monotonic in the benefit/cost ratio of enhancement to suppression; lower edge of the active band given in closed form. | `sec:results-vda-nonmonotonic`: $\VDA(\Rsens)$ non-monotonic; `eq:r-dagger` $\rdagger(\val)$ | C2 |
| AB5 | Concentrated in a graded regime — low validity, high value contrast, cost-dominant asymmetry — mapped quantitatively and turned into validity thresholds for cueing designs. | `sec:results-graded`: iso-VDA contour band; `tab:graded-highV`; $\valid\gtrsim0.95$ / $0.8$ design guidance | C3 (graded) |
| AB6 | Optimal attention never turns away from the high-value location under a predictive cue — a conditional theorem; under a counter-predictive cue inverted allocation becomes optimal, a new falsifiable prediction. | `sec:results-noninversion`: `eq:value-weight` condition $\valid\ge1/\Nloc$; anti-cue inversion 36.1% at $\Nloc=4$ | C4 (conditional) |

**Grounding verified** — every abstract clause maps to a body result
already traced above; the abstract introduces no number, mechanism, or
claim not present (and grounded) in the body. **Firewall clean** —
banned-vocabulary grep on `abstract.tex`: zero hits; no comparison/hedge
framing, no version tag, no build-process language; written positively as
this paper's own result. **Compile verified** — `pdflatex`×2 + `bibtex` +
`pdflatex`×2, exit 0, 33 pages, 0 undefined references/citations, 0 bibtex
warnings, single pre-existing 3.0pt overfull hbox (Supplementary
Corollary 2, not abstract).
