---
type: conversation
agent: constructive-rebuilder
prompt_version: "0.2"
run_id: rb-013-2026-05-25
started: 2026-05-25T18:00:00Z
ended: 2026-05-25T18:25:00Z
worked_on: RB-012
output_kind: manuscript
claims_touched: [C4, A1]
artifacts_written:
  - Rebuild/manuscript/sections/results.tex (§results-c4, replaced 7-line stub with ~530-line section)
  - Rebuild/manuscript/refs.bib (+6 entries: wang_theeuwes2018_statistical_learning_distractor_suppression, wang_samara_theeuwes2019, kong_li_wang_theeuwes2020, failing_theeuwes2018_selection_history, hickey2010_reward_salience_acc, posner1980_orienting)
  - Rebuild/manuscript/figures/r_inv_closed_form.png (copied from sims/C4--anti-cue-inversion/output/figures/)
  - Rebuild/manuscript/figures/er_vs_alpha_anticue.png (copied)
  - Rebuild/manuscript/figures/alpha_star_V_r_map.png (copied; headline §results-c4 figure)
  - Rebuild/manuscript/main.pdf (27 pp / 1,814,626 bytes)
  - Rebuild/CLAIM_LEDGER.md (C4 row backing column extended; rb-013 reconcile line)
  - Rebuild/REBUILD_BACKLOG.md (RB-012 status queued -> in_progress -> done; notes block expanded with full per-paragraph table-of-contents)
  - Rebuild/rebuilder_state.json (runs_completed 12 -> 13; manuscript_sections_drafted += "RB-012 (§results-C4)"; done_task_ids += RB-012; rb_013_manuscript_pdf_bytes added)
  - Rebuild/BUILD_LOG.md (rb-013 entry)
papers_added: []
spawned_tasks: []
---

# What I built

The §results-C4 manuscript section of the rebuilt VDA paper — eight
paragraphs, four numbered tables (`tab:c4-rstar-tally`,
`tab:c4-stepB`, `tab:c4-anticue`), three figures
(`fig:c4-rinv-closed-form`, `fig:c4-er-vs-alpha`,
`fig:c4-alpha-star-map`), and four numbered equations
(`eq:value-weight`, `eq:left-derivative`, `eq:r-inv`,
`eq:r-inv-corner`). The section consumes the rb-012 simulation
outputs (sha256 `6ad651d6…`) without rerunning the sim and cites
every number from the simulation's `results.json` directly.

The narrative move the section makes — the unifying reframe at the
heart of the rebuild for this claim — is to **promote C4 from a
categorical statement to a conditional theorem** with two explicit
parts:

1. **The conditional theorem** (`V ≥ 1/N`, sharp form
   `V ≥ 1/[(N-1)v+1]`): `α*_global ≥ 1/N` across the primary sweep
   and robust under A1. The mechanism is the location-count
   asymmetry combined with the value-weight inequality `w_c ≥ w_u`,
   not the local cost-vs-benefit balance argument of the inherited
   §4.5. The closed-form local threshold `r†_inv = (N-1) A_0/B_0`
   organises the bimodality of the boundary picture and lands the
   symmetric-corner identity `r†_inv(V=1/N, v=1) = 1` exactly,
   independent of N, variant, and ρ.

2. **The new falsifiable prediction**: below `V = 1/N` the value-
   weight inequality flips and the model produces global inversion
   `α* < 1/N`. The rebuild's evidence at `N = 4` (the paper's primary
   topology, which the reviewer's CR-004 only tested at `N = 2`) is
   36.1% inversion incidence across the probed anti-cue grid at
   ρ = 0, 34.7% at ρ = 0.2. The behavioural near-analog —
   statistical-learning-of-distractor-suppression — is a prediction
   match, not a contradiction.

# How it connects to the ledger

- **C4 (CONFIRMED-CONDITIONAL).** The section discharges the C4
  manuscript task at exactly the rebuilt strength the CLAIM_LEDGER
  C4 row licenses: conditional theorem with the explicit `V ≥ 1/N`
  condition, the closed-form `r†_inv`, the symmetric-corner
  identity, and the anti-cue prediction at `N = 4`. No strength
  change. The strength ceiling was already established by the
  rb-012 sim and the reviewer's V0.2 verdict; this section is the
  prose layer.

- **A1 (CONTESTED).** The cross-axis sensitivity paragraph
  documents that the A1 decorrelation channel and the C4 inversion
  lever are independent mechanisms: ρ = 0.2 quantitatively shifts
  the local threshold `r†_inv` (median by 13–21%) but leaves the
  qualitative inversion locus and incidence essentially unchanged
  (Step C: 25 vs 26 inversions; Step D: identical 2.2% incidence).
  No A1 strength change.

# Simulation evidence

All numbers in the section come directly from the rb-012 sim's
`results.json`. The simulation evidence is documented at the
rebuild's recoverability standard:

- **sha256 (content excluding wall-clock):**
  `6ad651d648ae597cdfb28c6fd19b6261e4f9d5cb96b599557e10aad47ffd6d96`.
- **Wall-clock:** 17.4 s on python 3.13 / scipy 1.17 / numpy 2.4.
- **Recovery #1** (vs reviewer derivation §4 49% in [0.1, 10]):
  48.6%, Δ = 0.4 pp. **PASS** (tol 1.0 pp).
- **Recovery #2** (vs reviewer derivation §5 Step C(i) table):
  max |Δα*| = 0, max |ΔR*| = 3 × 10⁻⁶. **PASS** both axes.
- **Symmetric-corner identity** `r†_inv(V=1/N, v=1) = 1.0000`
  exactly in every (variant, ρ) panel of `tab:c4-rstar-tally`.
- **Three figures** included from
  `Rebuild/sims/C4--anti-cue-inversion/output/figures/`:
  - `r_inv_closed_form.png` — log₁₀ r†_inv contours over (V, v)
    at variants A/B (the symmetric-corner anchor visualisation).
  - `er_vs_alpha_anticue.png` — E[R](α) at the anti-cue cell
    showing the β/γ-kink bimodality and global-inversion onset.
  - `alpha_star_V_r_map.png` — heatmap of α*(V, r) at v=5, both ρ;
    the §results-c4 headline figure with white V=1/N line and red
    α*<1/N contour.

# What the manuscript can now say

At the strength ceiling the CLAIM_LEDGER licenses (and now
discharges in §results-c4):

> Under V ≥ 1/N and v ≥ 1, the optimal allocation satisfies
> α*_global ≥ 1/N; the empirical claim survives the 4,410-cell
> primary sweep at N = 4 and is robust under A1 (Step B 0
> inversions and Step D 0 cued-region inversions at ρ ∈ {0, 0.2}).
> The mechanism is the location-count asymmetry combined with the
> value-weight inequality w_c ≥ w_u (equivalently
> V ≥ 1/[(N-1)v+1], universally bounded by V ≥ 1/N at v=1). The
> paper's `regardless of r` wording is correct as a global claim
> but incorrect as a local derivative statement: the left
> one-sided derivative at α = 1/N has a closed-form sign-flip at
> r†_inv = (N-1) A_0/B_0, which falls inside [0.1, 10] in ≈49% of
> primary-sweep cells. Below V = 1/N the model produces global
> inversion α* < 1/N — a new falsifiable prediction of the rebuilt
> normative model, verified across 36% of probed anti-cue cells at
> N = 4, with ρ = 0.2 essentially preserving both the inversion
> locus and incidence. The behavioural near-analog —
> statistical-learning-of-distractor-suppression — exhibits exactly
> the α* < 1/N allocation the model predicts at V < 1/N, a
> prediction match rather than a contradiction.

# Next increment

Natural next pick: **RB-013** (§appendix-C5 consistency result).
- Lowest-effort option: no new sim is needed because the rb-001
  ρ→0 recovery contract already exercises r = 1 symmetric recovery
  to machine precision.
- Would close out the four headline-claim results subsections + the
  C5 appendix in the same swing.
- Alternative pick: **RB-030** (C4 formal derivation in rebuild's
  voice, `Rebuild/derivations/C4--anti-cue-inversion.md`).
  Consolidates the four closed forms (eq:left-derivative, eq:r-inv,
  eq:value-weight, eq:r-inv-corner) stated in §results-c4 into a
  proper appendix derivation file. Parallels rb-008's
  `derivations/A1--rho-channel.md`. Includes the formal proof of the
  symmetric-corner identity from the FOC symmetry of A_0 and B_0
  and the ρ>0 extension of A_0, B_0 via the one-factor Gauss-Hermite
  quadrature.
- Beyond those: **RB-014** (A2 heterogeneous-r model extension) and
  **RB-015** (A3 conservation family model extension) open the
  largest remaining structural threads. RB-014 is the natural
  bridge into A8 (RB-017/RB-021) since A8 depends on A2 in the
  backlog's dependency graph.

# Wiki cross-references

§11.1 sweep performed across keywords {anti-cue, counter-predictive
cue, inverted attention, distractor suppression, statistical
learning, value-driven capture, no-inversion, priority map, signal
detection theory, location-count asymmetry, value-weight
inequality}. Hits — all already wired in `research_db/papers/` (no
new stubs added this run):

- [[wang_theeuwes2018_statistical_learning_distractor_suppression]]
  — abstract-depth wiki stub. **Cited** as the primary behavioural
  near-analog of the rebuilt model's anti-cue inversion prediction.
- [[failing_theeuwes2018_selection_history]] — full-depth. **Cited**
  for the facilitatory-capture / inhibitory-suppression
  decomposition that maps the V ≥ 1/N / V < 1/N regimes
  respectively.
- [[hickey2010_reward_salience_acc]] — full-depth. **Cited** for
  value-driven capture (V ≥ 1/N, attention pulled toward, supports
  C4 at the cued regime).
- [[posner1980_orienting]] — full-depth. **Cited** for the
  chance-validity boundary V = 1/N no-information limit (the
  rebuilt model collapses to a tied optimum there).
- [[bisley_mirpour2019_priority_map]] — full-depth. Not cited in
  this section but consistent with the inversion-as-priority-map-
  plasticity reading; the body of §results-c4 stays focused on the
  model's normative output, not its neural substrate.

Two papers cited by full bibliographic reference (not present in
`research_db/papers/`): **Wang, Samara & Theeuwes (2019)** Atten
Percept Psychophys 81(6):1813–1821, DOI 10.3758/s13414-019-01708-5;
**Kong, Li, Wang & Theeuwes (2020)** PLoS ONE 15(6):e0233544, DOI
10.1371/journal.pone.0233544. Both are listed by full bib reference
in the reviewer's C4 V0.2 verdict (`Critique/verdicts/C4--no-inversion.md`
§Evidence, V0.2) and explicitly deferred there for stub creation
under reviewer-side CR-035 / CR-037. The rebuilder follows that
scope decision — adding the wiki stubs is the reviewer's task, not
the rebuilder's, and the manuscript's bib entry suffices to anchor
the citation.

`audit.py` not re-run (no wiki writes this run).
