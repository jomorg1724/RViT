---
id: fixed_grid_controlled_design_status
type: note
status: draft
created: 2026-07-11
tags:
  - topic/value-directed-attention
  - topic/experimental-design
  - topic/reproducibility
source_project: "rvit-plus-paper-jepa-grid9"
source_code: "RViT_plus_paper_jepa_grid9/envs/tasks.py"
summary: "A five-condition fixed-grid VDA environment is implemented and tested for constant 4x4 geometry, 100x100 observations, 16 tokens, matched task settings, exact validity for K>=2, and deterministic seeding. No training run or controlled scaling result exists yet."
see_also:
  - slug: rvit_plus
    rel: informs
    summary: "Defines the prospective controlled-design branch of the current RViT+ program."
  - slug: vda_battery_state_and_provenance
    rel: refines
    summary: "Addresses geometry and semantics confounds in the archived cross-checkpoint ladder."
  - slug: archived_vda_validity_semantics
    rel: refines
    summary: "Uses exact prospective validity for K>=2 while reporting the K=1 degeneracy explicitly."
  - slug: corrected_vda_analysis_status
    rel: informs
    summary: "Pairs controlled future training with versioned, deterministic downstream analysis."
  - slug: posner1980_orienting
    rel: grounded-in
    summary: "Uses cue validity as the controlled target-location probability in the new design."
---

# Fixed-grid controlled set-size design status

## TL;DR

The controlled environment is implemented and tested, but the experiment has not been run. Five tasks vary active set size across 1, 2, 4, 9, and 16 while holding a 4-by-4 canvas, 100-by-100 observations, a 16-token model interface, timing, reward, cue values, and displayed proportions fixed; exact validity is possible only when at least two items are active.

## Plain explanation

The archived set-size ladder changed more than load: the nine-item condition also changed image geometry, token count, readout dimensions, training support, and validity semantics. The fixed-grid design places every condition on the same sixteen-cell canvas and blanks inactive cells. This removes major design confounds in principle, but only trained, replicated runs can show whether the earlier pattern survives.

## Research goal

Create a controlled active-set-size manipulation suitable for testing whether validity use changes with competition rather than with geometry, tokenization, or inconsistent target sampling.

## Method

`FixedGridVDASetSizeEnv` registers `vda_fixed1`, `vda_fixed2`, `vda_fixed4`, `vda_fixed9`, and `vda_fixed16` in `RViT_plus_paper_jepa_grid9/envs/__init__.py`. The environment fixes a 4-by-4 grid and 100-pixel image, keeps sixteen model tokens, samples only the requested number of active cells, and leaves inactive cells blank. For `K>=2`, invalid trials exclude the cue and metadata reports `validity_mode: exact_bernoulli`; for `K=1`, metadata reports the unavoidable singleton degeneracy. `train_rl.py --seed` initializes PyTorch and NumPy before environment construction.

## Finding

*Design finding only.* Tests verify constructibility, fixed geometry and task signatures, exact validity for `K>=2`, truthful singleton metadata, inactive-cell rendering, deterministic trial replay, and seeded training setup. The implementation log reports the full project suite at 117 passing tests. No metrics file, checkpoint, run ID, behavioral curve, or training-seed replication exists for any `vda_fixed*` condition.

## Evidence

- Environment implementation: `RViT_plus_paper_jepa_grid9/envs/tasks.py`
- Task registration: `RViT_plus_paper_jepa_grid9/envs/__init__.py`
- Training seeding: `RViT_plus_paper_jepa_grid9/train_rl.py`
- Controlled-design tests: `RViT_plus_paper_jepa_grid9/tests/test_fixed_grid_setsize.py`
- Audited implementation status: `reports/research_state/2026-07-11_implementation_log.md`
- Registry boundary: `research_db/registry/artifacts.jsonl` contains no `vda_fixed*` run.

The tests hold the shared signature at grid `(4,4)`, `n_stim=16`, image size `100`, observation shape `(100,100,3)`, and a sixteen-token front end. They also test realized validity near 0.25 over generated changed trials for `K=2,4,9,16` and exact replay under a fixed NumPy seed.

## Reproduction

The implementation can be rechecked by running the existing tests in `RViT_plus_paper_jepa_grid9/tests/test_fixed_grid_setsize.py` and confirming the source and task registrations above. The reviewed implementation log does not preserve the exact full-suite invocation, so this note does not invent one.

Training reproduction is *not yet defined*: before execution, each condition needs an immutable run directory and a manifest recording the exact command, source hash, seed, routing, width, reward, curriculum, planned budget, completion reason, checkpoint hashes, and expected analyses. Multiple independent training seeds are required before a scaling claim.

## Caveats

- Implementation tests are not experiment results.
- K=1 cannot realize an invalid target; its effective realized validity is 1.0 regardless of displayed `p`.
- Holding interface dimensions fixed does not guarantee equal optimization difficulty across active set sizes.
- A fixed evaluation batch from one trained model would still be within-model uncertainty, not a training replication.
- No direction or effect size is preregistered here, and no VDA16 completion is implied.

## Citations

- [[vda_battery_state_and_provenance]] — archived ladder that motivates the control.
- [[archived_vda_validity_semantics]] — historical semantic mismatch repaired prospectively for `K>=2`.
- [[posner1980_orienting]] — cue-validity construct.
- [[carrasco2011_visual_attention_25y]] — load/noise interpretation that the controlled design can test.
