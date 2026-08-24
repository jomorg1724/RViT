# SYNTH_BACKLOG.md — queued synthesis tasks

Ordered list. Default selection: follow the original's arc for
first-draft integration (Abstract written last), highest-priority
unblocked task first; interleave a coherence pass after every 2--3
section integrations (mission §4.1). Schema in mission §9.1.

```yaml
- id: SY-001
  output_kind: section
  target: "Introduction (original §1)"
  task: "Reconstruct the Introduction at ledger strength: two-mechanism framing + the rho decorrelation lever + four-finding preview corrected from categorical to distributional/graded/conditional."
  status: done
  priority: high
  prereqs: []
  blocking_gap: none
  notes: "Bootstrap first increment (mission §9.8). Compiles clean, 3 pages, 0 undefined refs. 0 gaps. Sets the narrative voice. Traced fully in TRACE.md (I1-I11)."
  origin: seed
  touched: 2026-05-30T21:10:00Z

- id: SY-002
  output_kind: section
  target: "Model (original §2.1-2.5) + three-lever decomposition"
  task: "Re-flow Rebuild/manuscript/sections/model.tex into the original's §2 arc (Task Structure, Attention Allocation, Attention-to-Perception Mapping incl. the rho lever, Reward Structure, Policy Decomposition P1-P4). Place Figure 1 (attention->d' mapping). State Definition of the three levers. Copy needed figures."
  status: done
  priority: high
  prereqs: [SY-001]
  blocking_gap: none
  notes: "DONE at SY-002 (2026-05-30). Re-flowed rebuilder model.tex into original §2.1-2.5: 2.1 Task Structure (SDT marginals), 2.2 Allocation, 2.3 Attention->d' mapping (transfer f, four h-forms, beta/gamma asymmetry, d'_c/d'_u map), 2.4 Reward Structure + decorrelation channel (variants A/B, expected-reward Eq, locus of A1 at P_no-fa, equicorr Eq, boxed 1-D integral Eq pnofa-rho, recovery contract), 2.5 Policy Decomposition (P1-P4, gain decomposition Eqs 10-12, CF def, three-lever Definition def:three-levers). Compiles clean, 7 pages, 0 undefined refs. DEFERRED (deliberate, 'original wins on structure'): the §5.5 upper-bound retraction + cell-wise sign-flip Table tab:a1cw-summary + 4 A1 sign-flip figures -> Results (SY-003/004) + Discussion (SY-008); named as an open empirical question in M14, not asserted. Gap G-001 opened (original Figure 1 attention->d' mapping, no artifact). Traced M1-M14 in TRACE.md."
  origin: seed
  touched: 2026-05-30T22:35:00Z

- id: SY-003
  output_kind: section
  target: "Results 4.1 — criterion typically dominant (C1)"
  task: "Re-flow §results-c1: CF distribution (median 0.76, [0.30,1.00], frac<0.6), the contested high-r corner, the rho sensitivity, the conservation-family band caveat. Place cf_histogram/cf_heatmap/cf_curves. Distributional voice only; no [0.60,0.96] floor."
  status: done
  priority: high
  prereqs: [SY-002]
  blocking_gap: none
  notes: "DONE at SY-003 (2026-05-30). Reconstructed the original's §4.1 'Criterion Adjustment Dominates Value Encoding' as a distributional finding. Results header + four-finding orienting paragraph + §4.1 (sec:results-criterion). Corrected the categorical [0.60,0.96] floor -> central tendency (median 0.7552 A / 0.7682 B, [0.30,1.00], strict min 0.5587 A / 0.3040 B, 8% of var-B < 0.50) and 'always single largest contributor regardless of r' -> 'typically dominant' with the benefit-dominant low-validity corner where it cedes (var-B median 0.51, min 0.30). Tables cf-distribution + cf-quadrants; figures cf_histogram/cf_heatmap/cf_curves copied + placed. rho sensitivity = the §5.5 retraction folded in along the CF axis (independence upper-bounds CF, var A only; var B mixed) at LEDGER:A1/C1 strength. Conservation-family band caveat (median robust, tail rule-dependent) folded as prose, forward-ref to Discussion. CARRY-IN HANDED TO SY-004: the dVDA/drho sign-flip itself (the VDA-side of the §5.5 retraction) lives with C2 (vda_curves_vfamily right panel, tab:rho-sensitivity v-dependent sign-flip) and the Discussion (SY-008). Figure 2 reward-decomposition bar chart NOT reconstructed (no artifact; superseded by cf_histogram per RB framing) -> NOT a gap, logged in TRACE. Compiles clean, 11 pages, 0 undefined refs. 0 new gaps. Traced R0-R8 in TRACE.md."
  origin: seed
  touched: 2026-05-30T23:30:00Z

- id: SY-004
  output_kind: section
  target: "Results 4.2-4.3 — asymmetry shapes allocation; VDA non-monotonic in r (C2)"
  task: "Re-flow the asymmetry-allocation narrative + §results-c2: non-monotonic VDA, closed-form rdagger(v), peak vs threshold, rho sensitivity. Place vda_curves_vfamily / r_dagger_vs_v."
  status: done
  priority: high
  prereqs: [SY-003]
  blocking_gap: none
  notes: "DONE 2026-05-30. Wrote §4.2 'The value-directed attention benefit is non-monotonic in the benefit/cost ratio' (sec:results-vda-nonmonotonic) as the confident centerpiece. Five paragraphs: (a) non-monotonic VDA(r) shape stated plainly; (b) closed-form escape threshold rdagger(v)=K_u/[(N-1)K_c] (eq:r-dagger, eq:K-c, eq:K-u) with K_c/K_u displayed, derivation deferred to Supplementary; (c) Table r-dagger-family (rdagger falls 0.343->0.016 across v=1..10) + Fig r_dagger_vs_v; (d) peak r*>rdagger(v) for every v (Table peak-vs-threshold, 84-pt grid), peak height grows 0.012->0.183 with v + Fig vda_curves_vfamily; (e) Decorrelation sensitivity: rho 0->0.2 suppresses peak for v<=8, amplifies at v=10, r* drifts up (Table rho-sensitivity); closed-form rdagger(v;rho) drifts up +3%..+30%, sign-matches empirical at v!=1 — decorrelation NOT a uniform attenuator (the §5.5 reframing folded along the VDA axis, positive voice, LEDGER:A1/C2 strength). CF/rho-recovery NOT redefined (already in Model). Both figures copied from SIM:C2. Firewall grep on results.tex: zero hits. Compiles clean, 13 pages, 0 undefined refs/citations. 0 new gaps. Traced V0-V7 in TRACE.md. Forward-refs to sec:appendix (Supplementary) resolve (stub exists; content lands SY-011)."
  origin: seed
  touched: 2026-05-30T23:30:00Z

- id: SY-005
  output_kind: coherence
  target: "Intro + Model + Results 4.1-4.3"
  task: "End-to-end coherence pass over the first integrated stretch: notation drift vs \\newcommand block, duplicated definitions, dangling \\ref, intro previews vs body strength, figure/caption consistency, transitions."
  status: done
  priority: medium
  prereqs: [SY-004]
  blocking_gap: none
  notes: "DONE 2026-05-30 (run 2F9C61B4). First interleaved coherence pass over Intro + Model + Results §4.1-§4.2. Fixes, all content-preserving: (1) standard-normal density glyph standardised to varphi in Results K_c/K_u (was \\phi) to match the Model's boxed integral; (2) Results baseline d' symbol identified with the Model's: \\dprime_b == \\dprime_{base}, redundant ':=' removed (defined once in Model §2.3); (3) two Model cross-refs to the supplementary section reworded 'Appendix' -> 'Supplementary material', matching Results + the section heading (Nature format, mission §5.5); (4) the single overfull \\hbox (54.7pt, Results §4.2 'threshold falls as cued value rises' paragraph — NOT the Model §2.4 one flagged earlier; that had cleared once SY-004 re-paginated) fixed by re-ordering the sentence so the wide config tuple is not at a tight line start; (5) two 'continuous trace' -> 'continuous curve' rewordings (plot-curve sense; also removes a borderline 'trace' substring). Verified: notation consistent vs \\newcommand block; no duplicated defs; 0 dangling \\ref; 0 undefined citations; intro four-finding previews consistent with §4.1-§4.2 body strength; all 5 referenced figures present. Firewall re-sweep: zero reader-visible hits. Clean 3-pass build, 13 pages, 0 overfull hboxes. DEFERRED to SY-009 (second coherence pass, after Discussion lands): verify §4.1/§4.2 forward-refs to sec:discussion (conservation band, rho sign) resolve to real content; check intro finding-1 'tail grows as rho admitted' against the variant-A/variant-B split once Discussion states it (currently a fair preview, variant-A dominant — drift-watch, no change)."
  origin: seed
  touched: 2026-05-30T23:59:59Z

- id: SY-006
  output_kind: section
  target: "Results 4.4 — the graded regime where VDA matters (C3)"
  task: "Re-flow §results-c3: iso-VDA contour band over (V,v,r); the high-V probe table; the re-scoped design boundary (V>=0.95 unconditional; V>=0.8 if r<=0.2; 0.75 too permissive). Place iso_vda_contours / vda_at_high_V / iso_vda_drho. Graded voice; correct 'negligible regardless'."
  status: done
  priority: high
  prereqs: [SY-004]
  blocking_gap: none
  notes: "DONE 2026-05-30 (run 7B3F1A92). Wrote Results §4.3 'The benefit is concentrated in a graded regime' (sec:results-graded) as the third finding, in clean positive venue voice — zero meta. Five paragraphs + 3 tables + 3 figures: (a) iso-VDA contour band over (V,v) on the 3,534-cell (4,2,0.5,sqrt) var-A sweep, V in [0.25,1] x v in [1,10] x r in {0.3,1,3} x rho in {0,0.2}, Fig iso-vda-contours; corner concentrated at low V / high v, flattens along r (VDA 0.17->0.16->0.06); (b) Table graded-marginals (median VDA<=0.007 every panel, peak 0.173->0.062, frac>=0.05 28.7%->1.2%); (c) high-V probe Table graded-highV + three conditional statements + boxed positive design recommendation (V>=0.95 uncond.; V>=0.8 if r_SC<=0.2; V>=0.75 too permissive, [0.6,0.8) cost-dominant admits peak ~0.16) + Fig vda-at-high-V; (d) decorrelation sign-flip across the plane: r=0.3 suppression-dominated, r in {1,3} amplification-dominated, Fig iso-vda-drho + Table graded-signflip; dormant-cell amplification (0.7,10,0.3) VDA 0.0007->0.0676 (~96x) flagged falsifiable, deferred to Discussion; (e) scope + value-blind v=1 identity consistency check. The categorical 'negligible regardless of other parameters' high-V statement is NOT reconstructed-against; stated positively as the model's contour-band guidance (firewall). Three C3 figures copied. Firewall grep on all .tex: 0 hits. Clean 3-pass build, 17 pages, 0 undefined refs/citations, 0 overfull boxes. 0 new gaps. Traced G0-G7 in TRACE.md. Forward-ref to sec:discussion (variant-B + conservation band) resolves (stub exists; content SY-008)."
  origin: seed
  touched: 2026-05-30T23:59:59Z

- id: SY-007
  output_kind: section
  target: "Results 4.5-4.6 — no inversion (C4, conditional) + robustness"
  task: "Re-flow §results-c4: conditional theorem V>=1/N, closed-form r_inv, symmetric-corner identity, anti-cue inversion as new prediction; then the robustness-across-parameters paragraph. Place r_inv_closed_form / er_vs_alpha_anticue / alpha_star_V_r_map."
  status: done
  priority: high
  prereqs: [SY-006]
  blocking_gap: none
  notes: "DONE 2026-05-30 (run 9E4D7C13). Wrote Results subsection 'Optimal allocation does not invert when the cue is predictive' (sec:results-noninversion) as the closing Results finding, clean positive venue voice — zero meta, zero comparison framing (no 'inherited paper', no 'claim restated', no reviewer/verdict/sha). Eight paragraphs + 3 tables + 3 figures: (a) positive opening: under a predictive cue the optimum never goes below uniform 1/N; the governing boundary is sharp and closed-form. (b) value-weight inequality eq:value-weight w_c>=w_u <=> V>=1/[(N-1)v+1], universal worst-case V>=1/N at v=1; location-count asymmetry mechanism. (c) closed-form boundary left-derivative eq:boundary-derivative + threshold eq:r-inv rstarinv=(N-1)A_0/B_0 + symmetric-corner identity eq:r-inv-corner rstarinv(1/N,1,N,CR,rho)=1 exactly; full derivation deferred to Supplementary (sec:appendix, lands SY-011). (d) Table noninv-tally (closed-form rstarinv on primary (V,v) grid, 4 panels; 48.6%->51.9% in [0.1,10] under rho; median drops 13%/21%) + Fig r-inv-map. (e) zero global inversions across 12-probe predictive-cue sweep, Table noninv-sweep + Fig er-alpha-anticue. (f) counter-predictive inversion as new falsifiable prediction: 36.1% at rho=0 / 34.7% at rho=0.2 on the V<1/N sub-grid, stratified Table anticue; sharp v-dependence (75% at v=1, 12.5% at v=5; boundary 1/16 at v=5) + Fig alpha-star-map (2.21% incidence, 0 in predictive regime). (g) robustness+decorrelation independence paragraph (the SY-007 'robustness-across-parameters' element). (h) behavioural-record alignment (Wang-Theeuwes 2018, Wang-Samara-Theeuwes 2019, Kong et al 2020, Failing-Theeuwes 2018, Hickey 2010, Posner 1980 — all 6 bib keys already present, 0 new entries) + scope. 3 figures copied from the C4 sim output. Firewall grep on all .tex: 0 hits. Clean 3-pass build, 21 pages (was 17), 0 undefined refs/citations, 0 overfull boxes. 0 new gaps (all 3 figures existed). Traced N0-N8 in TRACE.md. Forward-refs to sec:appendix (derivation, SY-011) and sec:discussion (variant-B inversion band, SY-008) resolve to existing stubs."
  origin: seed
  touched: 2026-05-30T23:59:59Z

- id: SY-008
  output_kind: section
  target: "Discussion (original §5.1-5.5) + new predictions"
  task: "Restate §5.1 (why criterion dominates), §5.2 (re-scoped design advice), §5.4 (biological interpretation of r), §5.5 (limitations) at ledger strength; fold in the new falsifiable predictions (anti-cue inversion, conservation-band sensitivity). Per mission §9, do NOT reconstruct the original §5.3 NN/vision-transformer self-reference."
  status: done
  priority: high
  prereqs: [SY-007]
  blocking_gap: none
  notes: "DONE 2026-05-30 (run 4A8E2D17). Wrote the Discussion (sec:discussion) in clean positive venue voice, zero meta. Replaced the red placeholder. Six descriptive subsections: (opening synthesis of the four findings); 'Why criterion adjustment is typically dominant' (criterion free vs VDA's perceptual trade-off; CF median 0.7552/0.7682 in [0.30,1.00]; cedes in benefit-dominant low-validity corner — distributional, no floor, LEDGER:C1); 'The benefit/cost asymmetry and its biological reading' (r = enhancement/suppression efficacy via reynolds_heeger2009/mcadams_maunsell1999/treue_martinez_trujillo1999/carrasco2011; non-monotonicity reading + rdagger(v) edge, LEDGER:C2); 'Guidance for experimental design' (V>=0.95 uncond / V>=0.80 at rho=0 / V>=0.75 too permissive, peak~0.16 in [0.60,0.80); standard cueing paradigms dormant, LEDGER:C3); 'New predictions' (1: anti-cue inversion V<1/N, sharp v-boundary, falsifiable signature — LEDGER:C4; 2: decorrelation an active lever, sign of dVDA/drho set by r, dormant-cell ~100x amplification at rho=0.2 — LEDGER:C3 iso_vda_drho; 3: conservation-form sensitivity — median fixed <0.005, frac CF<0.5 doubles 4.0%->8.3%, 191 flips 0 reverse; variant-B deeper tail + lower median r*_inv => higher anti-cue incidence — LEDGER:C1 conservation band + C4 variant-B); 'Scope and limitations' (conservation a 1-param family eq:beta-gamma; heterogeneity bounded; decision-noise sigma_i(alpha) a natural further axis not included; transfer-function family generic in f; equicorrelation only; normative+stationary, NO neural-implementation claim — all lifted from limitations.tex scope content with rebuilt/inherited/reviewer framing stripped, restated positively). Did NOT reconstruct the §5.3 NN/vision-transformer self-reference (mission §9; no gap needed — not a scientific element, an internal cross-link). Resolves the §4.1/§4.3/§4.4 forward-refs to sec:discussion (conservation band, variant-B, decorrelation amplification) with real content. Fixed one broken \\eqref{eq:conservation-family} (label does not exist here) -> Section~\\ref{sec:model} + \\eqref{eq:beta-gamma}, matching the §4.1 phrasing. Reworded 'little prior' -> 'weakly informative' to avoid the bare banned-cousin 'prior'. Firewall grep: only 'inVERSION'/'noninVERSION' substring false-positives remain. Clean 3-pass build, 24 pages (was 21), 0 undefined refs/citations, 0 overfull boxes, 0 LaTeX warnings. 0 new gaps. Traced D0-D9 in TRACE.md."
  origin: seed
  touched: 2026-05-30T23:59:59Z

- id: SY-009
  output_kind: coherence
  target: "Results + Discussion"
  task: "Coherence pass over the second stretch: claims stated consistently in Results and Discussion, prediction wording, figure refs, transitions into the Discussion."
  status: done
  priority: medium
  prereqs: [SY-008]
  blocking_gap: none
  notes: "DONE 2026-05-31 (run C3D9A1F7). Second interleaved coherence pass over Results §4.1-§4.4 + Discussion. Headline fix: a cross-section terminology conflation between the REWARD VARIANT (A=value-coupled CR, B=fixed CR=1) and the CONSERVATION RULE (additive vs multiplicative, a separate one-parameter family). The validated source (model.tex, extensions.tex) and the Reconstruction's own Model+Methods keep the two axes distinct; Results §4.1/§4.2 and Discussion had drifted to calling A/B 'conservation variants' and pairing median 0.7552 with 'the additive rule'. Content-preserving fixes, NO numbers changed: 'conservation variant'->'reward variant' x7 in Results (incl. tab:cf-distribution + fig:cf-histogram captions); §4.1 robustness paragraph reworded so additive/multiplicative are the conservation-family endpoints swept within each reward variant (not 'the two variants above'); §4.2 '$\\CR(\\val)$ encodes the conservation rule'->'is the correct-rejection reward scaling set by the reward variant' ($\\CR=1$ kept as the value-blind setting, additive conservation named as the separate weight rule); Discussion opening medians re-attributed to value-coupled/equal-reward variants both at additive conservation; Discussion 'New predictions' 'the additive, value-weighted convention'->'the value-coupled reward variant'. All other checks passed without edits: cross-ref graph fully resolves (51 \\ref/\\eqref targets, all defined); intro 4-finding previews match body strength; dormant-cell ~96x<->'hundredfold', anti-cue boundary, and V>=0.95/0.80/0.75 design thresholds consistent Results<->Discussion; density glyph uniformly varphi. Firewall re-sweep: zero hits. Clean 3-pass build, 26 pages, 0 undefined refs/citations, 0 overfull boxes. 0 gaps opened/closed (G-001 still open)."
  origin: seed
  touched: 2026-05-31T00:00:00Z

- id: SY-010
  output_kind: section
  target: "Methods (parameter space, optimisation, validation)"
  task: "Write the Methods: parameter space, criterion/attention grid optimisation, the correlated-noise quadrature, the four parameter sweeps, validation (rho->0 recovery, quadrature convergence), and reproducibility. Placed at end of arc."
  status: done
  priority: medium
  prereqs: [SY-007]
  blocking_gap: none
  notes: "DONE 2026-05-31 (run B7E3F0A2). Wrote the Methods (sec:methods), seven subsections: (i) Task and decision model (SDT recap, headline cell N=4/d'_max=2/f0=0.5/h=sqrt, four h-forms for robustness); (ii) Benefit, cost, and reward variants (additive conservation eq:beta-gamma, power-mean family -> Supplementary, variants A/B CR); (iii) Correlated-noise channel (GH-64 quadrature, <=1e-15 vs 128-node, headline rho in {0,0.2} anchored CohenMaunsell2009); (iv) Policy optimisation (criterion grid 121 pts Dc=0.05 over [-3,3], attention grid [1/N,1] for P1/P2 extended to [0.02,1] for distributional/anti-cue, exhaustive search, value-blind caching); (v) Parameter sweeps (4,410-valid distributional / 83-pt VDA(r) family / 3,534-cell iso-VDA / inversion 420 closed-form + 197-pt verify + anti-cue grid + 544-cell alpha* map); (vi) Validation (rho->0 recovery contract FP-identity <1e-6, closed-form/grid agreement r-dagger ordering + symmetric-corner identity, Slepian sign check); (vii) Reproducibility (deterministic, no Monte-Carlo, fixed grids -> bitwise reproducible, <2 min, Python). All equations lifted by \\ref from the written Model/Results; grids/tolerances grounded in C1/C2/C3/C4 READMEs + core.py. Firewall grep on methods.tex: ZERO hits. External recovery comparisons (1.47e-6 vs reviewer substrate, 48.6% vs 49.0%) deliberately NOT surfaced -> framed as internal limit checks. Clean 4-pass build (pdflatex x3 + bibtex), 26 pages (was 24), 0 undefined refs/citations, 0 overfull boxes (one 6.2pt box fixed by spacing the cell-parameter tuple). 0 new gaps (no figures needed). Traced ME1-ME7 in TRACE.md."
  origin: seed
  touched: 2026-05-31T00:00:00Z

- id: SY-011
  output_kind: section
  target: "Supplementary derivations and extensions"
  task: "Re-flow the formal derivations (escape-threshold rdagger closed form + rho extension; symmetric recovery at r=1; power-mean conservation family) plus the correlated no-FA integral and its Slepian monotonicity, at ledger strength."
  status: done
  priority: medium
  prereqs: [SY-007]
  blocking_gap: none
  notes: "DONE 2026-05-31 (run E8F1A0D4). Wrote the Supplementary (sec:appendix), four subsections in clean positive venue voice, zero meta. (S.1) Correlated no-false-alarm probability + monotonicity: one-factor reduction to eq:pnofa-rho (Model §reward forward-ref resolved), 64/128-node GH agreement, Prop prop:orthant-monotone (Slepian) + Cor cor:policy-monotone, two-channel sign of dVDA/drho. (S.2) Closed-form escape threshold: boundary collapse, rho-aware gradient integrals eq:gh-grad-c/eq:gh-grad-u, boundary FOC eq:boundary-foc-rho with K_c/K_u(v;rho), Prop prop:escape-rho (boxed eq:r-dagger-rho), structural rho->0 recovery to eq:r-dagger/eq:K-c/eq:K-u reproducing tab:r-dagger-family, drift Table tab:r-dagger-rho-drift (rho=0 column matches tab:r-dagger-family exactly; 5/5 sign-match vs tab:rho-sensitivity) — Results §4.2 forward-ref resolved. (S.3) Symmetric recovery at r=1: Prop prop:symmetric-recovery (real-number identity, universal) + Prop prop:bitexact-recovery (Sterbenz band) + scope threshold eq:sterbenz-threshold + smooth-centre paragraph. (S.4) Power-mean conservation family: eq:power-mean/eq:power-mean-weights, HLP-as-KL eq:hlp-kl/eq:mono-sign, Prop prop:symmetric-corner + Cor cor:symmetric-invariance, full 3-step Prop prop:escape-invariance, CF chain rule eq:cf-chain-rule/eq:dprime-of-p + Prop prop:p3-invariance + empirical DeltaCF<=0 (4,410 cells, 0 reverse flips, closed form OPEN). All labels claim-id-free; all phi->varphi. 1 new real bib entry (Tong1990, Springer — backs the Slepian Prop). Firewall grep on all .tex: ZERO hits; also fixed one pre-existing comparison-hedge in discussion.tex ('not a categorical split' -> 'across the parameter space', content-preserving). Clean 3-pass build (pdflatex x3 + bibtex), 33 pages (was 26), 0 undefined refs/citations, largest overfull box 3.0pt. 0 new gaps (no figures needed). Traced P1-P19 in TRACE.md."
  origin: seed
  touched: 2026-05-31T12:00:00Z

- id: SY-012
  output_kind: coherence
  target: "Whole paper, end to end (pre-abstract)"
  task: "Full coherence pass before the abstract: complete cross-reference graph, notation, figure list, body-vs-intro promises, all placeholders resolved or gapped."
  status: done
  priority: medium
  prereqs: [SY-008, SY-010, SY-011]
  blocking_gap: none
  notes: "DONE 2026-05-31 (run 1B2C3D4E). Third coherence pass, whole paper, pre-abstract. Firewall re-sweep first: zero hits across all .tex + refs.bib (main.tex title/author block already clean). Two cross-section parameter-grid drifts found and fixed onto the validated source, both content-preserving (NO headline number/distribution/claim-strength changed): (X1) Results §4.1 distributional-sweep r-grid said '21 log-spaced points' (landing directly on 4,410 with no drop), conflicting with Methods '22 ratios … 4,620 nominal, 4,410 valid' and with the source C1 run.py (R_GRID = unique(logspace(0.1,10,21) ∪ {1}) = 22 r-values; n_total 4,620; n_valid 2,205/variant). Rewrote §4.1 to '22 values (21 log-spaced plus a pinned r=1)' and stated the 4,620-nominal/4,410-valid distinction, matching Methods + source. (X2) VDA(r) grid count: Results said '84 log-spaced points', Methods said '83 log-spaced ratios (… pinned)'; the C2 README gives both '83-point + pinned' (l.13) and '84-pt r-grid' (l.103) = 83 log + pinned = 84 total — harmonised both sections to '84 (83 log-spaced + pinned escape/peak neighbourhoods)'. All other checks passed WITHOUT edits: cross-ref graph fully resolves (98 labels, 236 \\ref/\\eqref, 0 undefined on 3-pass build); 11/11 \\includegraphics targets present and each referenced once; notation consistent vs \\newcommand block (varphi, dprime_base≡dprime_b); intro 4-finding previews match body strength; sweep sizes (4,410/2,205/3,534/420/544/72 and the 31×19×3×2, 4×3×6, 17×16 grids) now consistent Results↔Methods. Deliberate placeholders (not defects): GAP G-001 (model attention→d' illustration figure, open, owner-mediated) and the abstract stub (SY-013, written last). Clean 3-pass build (pdflatex×2 + bibtex + pdflatex), 33 pages, 0 undefined refs/citations, largest overfull box 3.0pt. 0 gaps opened/closed. Traced X1/X2 in TRACE.md. Next: SY-013 (abstract, from the finished body) — now unblocked."
  origin: seed
  touched: 2026-05-31T13:00:00Z

- id: SY-013
  output_kind: frontmatter
  target: "Abstract (written last)"
  task: "Re-flow Rebuild/manuscript/sections/abstract.tex into the reconstruction's abstract from the finished body, at ledger strength (4-paragraph three-lever summary)."
  status: done
  priority: medium
  prereqs: [SY-012]
  blocking_gap: none
  notes: "DONE 2026-05-31 (run 2C4E6A80). Wrote the Abstract from the finished body as a single unstructured paragraph (~205 words), no citations, no meta. Did NOT re-flow the Rebuild source abstract (it is written in build-process voice — 'we rebuild', 'inherited', 'the published [0.60,0.96] interval is retracted', 'nothing stated more strongly than its CLAIM_LEDGER row licenses'); instead wrote a clean, positive, standalone abstract. States the cued task + three levers (criterion / value-directed attention / decorrelation, ρ free with ρ→0 recovery), then the four findings positively at ledger strength: C1 criterion typically dominant, median ≈3/4 of the reward gain with a material tail; C2 VDA non-monotonic in the benefit/cost ratio with a closed-form lower edge; C3 graded regime (low validity, high value contrast, cost-dominant asymmetry) mapped to validity thresholds for cueing designs; C4 no inversion under a predictive cue as a conditional theorem + anti-cue inversion as a new falsifiable prediction. Firewall grep on abstract.tex: ZERO hits. Replaced the red stub; also de-meta'd the file's lone .tex comment. Clean build (pdflatex×2 + bibtex + pdflatex×2), 33 pages, 0 undefined refs/citations, 0 bibtex warnings, single pre-existing 3.0pt overfull hbox (Supplementary, not the abstract). Traced AB1-AB6 in TRACE.md. Next: SY-014 (front/back-matter finalisation) — note G-001 still open, so the 'submission-ready' milestone is not yet reachable."
  origin: seed
  touched: 2026-05-31T14:30:00Z

- id: SY-014
  output_kind: frontmatter
  target: "Title / author block / figure list / final build"
  task: "Finalise title, author block, figure list, bibliography assembly; final compile + page count; flip README to 'draft complete' if zero open gaps."
  status: queued
  priority: low
  prereqs: [SY-013]
  blocking_gap: none
  notes: "Milestone increment."
  origin: seed
  touched: 2026-05-30T21:10:00Z

- id: SY-015
  output_kind: scrub
  target: "Whole manuscript (firewall enforcement)"
  task: "De-meta scrub under prompt v0.2: purge every firewall violation from main.tex, all section files, and refs.bib; rewrite into positive standalone statements; clean title/author block; strip meta from comments."
  status: done
  priority: high
  prereqs: []
  blocking_gap: none
  notes: "DONE 2026-05-30 (run F2C7A9E1). 38 violations fixed across all files: meta comment headers stripped; 'inherited/original/reconstruction/published' framing removed; comparison-hedges ('rather than asserting', 'categorical floor', 'sharpen') rewritten positive; Rebuild/Critique/research_db paths + sha256 + SY/rb/RB/CR ids removed from prose, captions, and refs.bib comments; GAP G-001 placeholder made terse; 'Appendix' -> 'Supplementary derivations and extensions'. No science changed; content-preserving. Final firewall grep: zero hits. Compiles clean, 10 pages, 0 undefined refs/citations. firewall_clean=true. Next: SY-004 in clean venue voice."
  origin: spawned-by-prompt-v0.2
  touched: 2026-05-30T23:59:00Z
```
