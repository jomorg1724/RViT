# VDA4 native-2x2 memory-noise paired pilot v1

Status: **frozen seed-0 pilot scaffold prepared and locally preflighted; no GPU
training or held-out evaluation has been launched.**

The authoritative protocol is `design_manifest.json`. This directory is new and
isolated; it does not modify the frozen stream-factorial source, config, queue, or
production records.

## Question

Does destructive interference in recurrent memory make selective routing more
behaviorally important? The pilot trains the same native four-patch VDA4
`crossattn1` architecture twice from the same seed and the same named trainable
initialization:

| condition | `memory_noise_std` | required |
|---|---:|---|
| `noise0p0` | 0.0 | yes |
| `noise0p5` | 0.5 | yes |

Everything else is fixed: VDA4, four active items, native 2x2 visual and memory
grid, four tokens, `xlstm`, `crossattn1`, `d_mem=128`, memory decay 1.0, learned
convolutional frontend, seed 0, and 20,000 fresh iterations.

This is one paired seed, so even a clean positive result is a directional pilot,
not a population effect.

## What "standard deviation 0.5" means here

The current `SpatialXLSTM` does not add raw fixed-scale noise directly to `C`.
Let `N_state` denote the xLSTM normalizer state (the implementation variable is
named `N`). It is unrelated to the native token count, which is written
`N_tokens=4` below. After every recurrent update for which injection is enabled,
the cell applies

```text
C <- C + sigma * (N_state + 1e-8) * randn_like(C)
```

and carries that perturbed `C` into the next update. Consequently, `sigma=0.5`
is expressed in normalized `C/N_state` units. `randn_like(C)` draws a separate
pseudorandom value for each batch element, native memory slot, memory coordinate,
and injected time step. The preflight checks that:

- the two levels have identical named trainable initialization and parameter
  count;
- noise is a no-op at 0.0;
- disabling injection makes the 0.5 model's deterministic cell update match the
  0.0 model;
- enabling 0.5 changes the carried state, repeats after an RNG reset, and changes
  with a different RNG seed.

This dose is the newly registered VDA pilot dose. It should not be described as
an exact replication of an earlier LayerNorm-cell experiment with a different
cell or dose.

### Frozen trainer asymmetry

The current training algorithm is a noisy-student/noise-off-teacher algorithm,
not an all-networks-noisy algorithm:

- online rollout collection calls `rl_step(..., inject_memory_noise=True)`;
- the optimized student/replay sequence calls
  `forward_rl_sequence(..., inject_memory_noise=True)`;
- the target actor/critic sequence omits the injection argument and is therefore
  noise-off;
- the JEPA EMA-teacher sequence also omits the injection argument and is
  noise-off.

The target and JEPA teacher model objects still carry the registered sigma, but
their deterministic forward calls do not inject it. This asymmetry is frozen and
provenance-bound for the pilot. Any later all-networks-noisy comparison would be
a different, separately registered experiment.

## Pairing boundary

The two runs have the same seed and identical initial trainable tensors. They are
also required to execute sequentially on the same physical GPU and software
runtime, enforced by a pair fingerprint.

They are **not** asserted to have identical on-policy training trial streams.
Memory noise can change sampled actions and episode lengths; environment rendering
and reset operations consume RNG, so the subsequent trajectories can diverge.
The 32-reset hash in preflight is only an initial environment-configuration
diagnostic. Actual common-random-number pairing is reserved for the frozen held-out
trial banks.

## Why behavior, routing, and intervention are all required

The hypothesis is not supported merely because the noisy model has more peaked
attention. The registered evidence chain is:

1. a larger sensitivity-corrected cueing effect;
2. stronger cue- and true-target-selective allocation in the correct visual or
   memory source and frame;
3. a larger, spatially specific behavioral cost/rescue when routing at the true
   location is suppressed/boosted;
4. no competence, floor, ceiling, or criterion-only explanation.

The primary behavioral measures are invalid-minus-valid psychometric threshold,
normalized response-AUC, d-prime with criterion reported separately, and response
frame. The primary validity analysis is the in-distribution slope/interaction
over displayed validities 0.25, 0.50, and 0.75. Forced-invalid trials at
validity 1.0 are reported separately as an out-of-distribution
expectancy-violation probe.

Causal probes use a disjoint adaptive calibration bank. Calibration selects one
common angle across all four train-noise by evaluation-noise cells, not one angle
per checkpoint. A candidate is eligible only when natural forced-invalid
response rates in all four cells are within [0.20, 0.80]; the eligible angle with
the smallest mean squared distance from 0.60 is frozen. If no angle qualifies,
the maps and interventions are retained as diagnostics but the mechanistic
interpretation gate fails.

Primary estimates must also be spatially counterbalanced: balance all four cue
locations and all 12 ordered cue-to-distinct-change pairs on forced-invalid
trials. A top-left cue to bottom-right change may be shown as an intuitive example
only; it cannot stand in for the primary spatial estimate.

## Attention display and measures

For native `N_tokens=4` `crossattn1`, the attention matrix has four query rows and eight
key columns: four visual keys followed by four recurrent-memory keys. Every report
must show visual and memory maps separately.

For source `s` and key `j`, the column-average score is

```text
p_s(j) = (1/N) * sum_i A[i,j]
```

Report raw source share, source-conditional target mass, true-target minus
distractor/cue contrasts, entropy, effective key count, top-one mass, and
target-to-distractor ratio by frame. The physical reference grid is always 2x2.
The registered temporal contrasts are cue-aligned allocation during frames 1-4
and change-target allocation during frames 5-6. Forced-invalid trials also report
target-minus-cued-wrong allocation and postchange-minus-prechange reorientation,
separately for visual and memory maps.

Because this pilot is natively 2x2, each physical region contains one patch:
regional total and regional maximum are therefore algebraically identical and
must not be presented as two independent corroborating measures.

## Fail-closed staging

On a prepared Linux CUDA worker, run both 50-iteration engineering canaries:

```bash
bash experiments/vda4_memory_noise/grid2x2_crossattn1_pilot_v1/queue_canaries_v1.sh
```

Canaries are engineering checks only. After they satisfy the engineering
contract, queue both production conditions unconditionally:

```bash
bash experiments/vda4_memory_noise/grid2x2_crossattn1_pilot_v1/queue_seed0_pair_v1.sh
```

The queue:

- preflights both conditions before launching either one;
- generates one pair id and one CUDA/GPU/runtime fingerprint;
- launches 0.0 and then 0.5 sequentially on that same fingerprint;
- creates a unique timestamp-plus-UUID output directory for every attempt;
- uses `mkdir`, not `mkdir -p`, so an existing directory cannot be overwritten;
- never reads training accuracy, theta, cueing, attention, or effect direction
  between conditions;
- stops early only if an engineering contract or trainer process fails.

If either member fails or is interrupted after its mate finishes, both unique
directories are preserved, but the registered comparison is rerun as an entire
fresh seed-0 pair under one new pair identity and one verified runtime. A
replacement condition is not spliced to an earlier mate unless the original
pair identity and runtime/GPU fingerprint are independently proven valid.

The production launcher intentionally requires `VDA_PAIR_ID` and
`VDA_PAIR_RUNTIME_SHA256` from the queue, preventing a standalone launch from
silently violating the same-GPU/runtime requirement.

## Terminal validation

Every completed condition must independently pass:

```bash
python experiments/vda4_memory_noise/grid2x2_crossattn1_pilot_v1/validate_terminal_v1.py \
  --run-dir /workspace/UNIQUE_RUN_DIRECTORY \
  --expected-memory-noise-std 0.0
```

Repeat with the 0.5 directory and `--expected-memory-noise-std 0.5`.
Validation requires exactly 20,000 finite contiguous metric rows, terminal
schema-3 final/latest checkpoints at iteration 19,999, finite semantic equality,
the complete fresh model/training contract, clean terminal log, source/config/
launcher provenance, launch-contract hashes, and runtime identity.

A terminal validation is still only training-integrity evidence. It makes no
behavioral, attention, causal, or signal-coherence claim.

## Held-out evaluation policy

No paired scientific result may be inspected until both conditions pass terminal
validation. The registered held-out sequence is:

1. adaptive nonsaturation calibration on a disjoint bank;
2. common-random-number psychometric/SDT and response-time evaluation;
3. source-separated visual and memory routing maps across all frames;
4. true-target, cued-wrong, and neutral routing interventions, separately for
   visual, memory, and both key sources;
5. paired `noise0p5 - noise0p0` contrasts.

The evaluator runs the complete 2x2 factorial: training noise 0.0 or 0.5 crossed
with evaluation noise 0.0 or 0.5. The matched trained-condition contrast compares
train0/eval0 with train0.5/eval0.5; the noise-off and crossover cells distinguish
learned compensation from acute corruption.

Each unique held-out sensory trial receives exactly one independently drawn
mnemonic-noise realization. The same sensory trial identities, sampled-action
uniforms, and standard-normal mnemonic schedules are shared across comparable
factorial cells. The same sensory realization is **not** repeated across several
mnemonic draws. Confidence intervals use a deterministic, spatially stratified
paired bootstrap over held-out trials and describe trial uncertainty conditional
on seed 0, not across-seed population uncertainty.

Interventions include a natural baseline and every combination of role
(`true_change`, `cued_wrong`, `neutral_control`), source (`visual`, `memory`,
`both`), and dose alpha in {0, 0.25, 0.5, 0.75, 1}. Beginning at frame 5, the
selected keys receive additive attention-logit bias
`b = 6 * (2 * alpha - 1)`. Therefore alpha 0 is the -6 suppress endpoint,
alpha 0.5 is zero bias, and alpha 1 is the +6 boost endpoint. This hook does not
disable routing, so no result is called `routing_disabled`. On valid and
no-change trials, where cue and target-index fields coincide, `cued_wrong` is a
deterministic non-target control location.

## Frozen identities

- design SHA-256:
  `1ae15e32b35687501554463a714074b6774e70aed524780ff14a733d832ec97b`
- config SHA-256:
  `01971fd731e030ed377f0c7db1164f0cf8c01285fbb57e7eda7381aed2414eb7`
- held-out evaluator SHA-256:
  `7f4985191c3a7feade6110109ca73eb3ab66cdc2790aebe70df46eefe1ed4e38`

The preflight also checks the exact registered hashes of `train_rl.py`, `ppo.py`,
the model/encoder/heads/frontend, the VDA environment sources, and the config
loader before a run can launch.
