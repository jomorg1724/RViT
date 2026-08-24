# Signal-coherence framing and PDF QA — 2026-08-02

## Scope

This pass reoriented the manuscript around the falsifiable functional hypothesis that attention increases signal coherence: cue- and target-consistent visual-routing and recurrent-memory signals should become more spatially aligned, more representationally stable and separable, more behaviorally useful, and more causally actionable relative to competing locations.

The revision explicitly separates four quantities that earlier prose risked conflating:

- `K`: active items / object-level competition.
- `N`: native patches / eligible spatial-key competition.
- `V`: effective visual streams on the fixed carrier.
- `M`: effective recurrent-memory streams on the fixed carrier.

The registered `V x M` factorial therefore tests signal rank and binding, not native key cardinality. A decisive discretization test still requires a parameter-matched manipulation of eligible or independently varying spatial competitors at fixed `K`; a complementary fixed-carrier `K` series is required to isolate active-item competition.

## Attention-measure clarification

All native grids are compared on a common physical `2 x 2` partition. The manuscript separately defines and visualizes:

- total target-quadrant mass;
- requested raw peak-patch score after query-column averaging;
- uniform-normalized peak strength;
- peak-quadrant share;
- target peak share minus the mean of the other quadrants;
- within-quadrant focality.

Exact uniform routing gives normalized peak strength 1, but maxima retain an `N`-dependent extreme-value expectation under noisy or heterogeneous patch weights. Peak measures are therefore descriptive complements; equal-area target mass and preregistered target-minus-distractor contrasts remain the primary cross-grid quantities. Frame 5 (change onset) and frame 6 (open-loop continuation) remain separate.

## Evidence-boundary corrections

- The VDA16 cross-attention lesion/rescue is described as a producer-bound, single-checkpoint, finite-trial intervention result pending independent semantic verification and seed replication.
- The manuscript no longer calls that result architecturally necessary or seed-generally sufficient.
- Checkpoint-local causal control is distinguished from population generality, biological equivalence, and a universal scaling law.
- Response-rate cueing gaps are not treated as signal coherence without sensitivity/criterion, representation, routing, and causal convergence.
- Current discretization directions are reported as mixed and routing-family/estimand dependent, not as a proven monotonic law.
- Explicit falsifiers include raw-peak-only effects, disappearance after equal-area or uniform normalization, criterion-only changes, sharper maps without behavioral/representational gains, nonspecific interventions, frame-6-only effects, and adequately replicated seed reversals.

## Build and automated checks

- Source: `main.tex`
- Source SHA-256: `658a961814dee1255bcae831862e7106165ff3ca01cbea31d14b4b6cfc7fd9e8`
- Final PDF: `VDA_Set_Size.pdf`
- Final PDF SHA-256: `ecc606995d1001387072f994a4d03ba2cd7443b2cea706e7dfef95295d2b773c`
- Final PDF bytes: `3,589,200`
- Page count: `36`
- Tectonic: exit `0`
- Log scan: no LaTeX errors, undefined control sequences, undefined references, overfull boxes, or missing characters.
- Claim scan: none of the retired overclaim phrases remained.
- Tests: `26 passed in 8.62s` for the spatial-scaling evaluation, endpoint replication, independent endpoint verifier, and attention-measure suites.
- Promotion: `main.pdf` and `VDA_Set_Size.pdf` were byte-identical by SHA-256.

## Visual QA

All 36 pages were rendered at 120 dpi into the unique directory:

`tmp/pdfs/vda_signal_coherence_20260802_qa2/`

Six contact sheets covering pages 1–36 were inspected. Full-size inspection additionally covered the title/abstract (page 1), the `K/N/V/M` theory table (page 3), attention definitions and caveats (page 8), common-grid and endpoint figures (pages 11–14), causal-intervention framing (pages 19–22), discussion/methods/conclusion (pages 23–25), and the appendices through page 36. No clipping, overlap, missing glyphs, corrupt figures, or unreadable revised content was found.

The compiler retained non-fatal underfull-box warnings and local Windows Times-font portability warnings; neither produced a visible defect in the rendered artifact.
