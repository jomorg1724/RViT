# Constant-parameter visual-versus-memory stream factorial

Status: **production-v1 contract prepared and tested; no training has been launched.**

The registered model factory is now reachable only through the paired
`--effective-visual-streams` and `--effective-memory-streams` CLI arguments.
The launchers below fail closed on every other scientific value and bind the
design, config, launcher, model source, initialization, and environment-RNG
trace into a preflight record.  `design_manifest.json` is the authoritative
machine-readable protocol.

## Why this is the next decisive experiment

The completed VDA4 spatial-discretization battery does not isolate a stream-count
effect. Changing the grid from 2x2 to 10x10 simultaneously changes:

- visual-token count (4 to 100);
- recurrent-memory positions (4 to 100);
- positional one-hot width (4 to 100);
- flattened actor/critic input (512 to 12,800 at `d_mem=128`);
- total parameters (about 2.2M to 8.7M).

The new design fixes all physical and trainable shapes at the 10x10 carrier and
crosses the *effective rank* of visual input and recurrent memory independently.
The display remains the unchanged 50x50 VDA4 scene with four active items.

## Manipulations

The carrier always has 100 slots, token width 236, memory width 128, and a
12,800-dimensional flattened readout.

- `V=100`: identity visual projection.
- `V=4`: average the frontend tokens within each 5x5 quadrant and broadcast the
  four quadrant tokens back onto the 100-slot carrier before routing.
- `M=100`: identity recurrent-write projection.
- `M=4`: average routed writes within the same four quadrants before the xLSTM;
  the shared recurrent update then carries exactly four distinct H/C/N/M states,
  broadcast over the fixed carrier.

Both projections are fixed, idempotent, differentiable, and have no trainable
parameters. The actor and critic always receive 100x128 values. At the registered
settings, measured trainable-parameter counts are exactly:

| routing family | all four V x M cells |
|---|---:|
| `crossattn1` | 8,682,948 |
| `affine_ew` | 8,661,468 |

Within each routing family and training seed, all four cells should start from
identical trainable tensors, receive the same environment RNG stream, use the same
20,000-iteration budget, and differ only in the two projector buffers.

## Registered matrix and staging

The confirmatory matrix is `V in {4,100} x M in {4,100}`.

1. **Engineering canary (not evidence):** one 50-iteration run per cell for
   `crossattn1`; verify state rank, gradients, checkpoint schema, and common initial
   trainable-tensor hash.
2. **Immediate scientific batch:** `crossattn1`, four cells, seeds 0/1/2 (12
   terminal runs). This estimates independent visual and memory main effects and
   their interaction without mixing routing algebras.
3. **Architecture replication:** repeat the same 12 cells for `affine_ew`. This is
   required before making a routing-family-independent statement because the
   completed spatial-scaling battery already showed a strong family interaction.
4. **Population extension:** add seeds 3/4 only after the pre-registered competence
   and non-saturation gates pass. Five seeds are the minimum sensible target for an
   inferential claim; three seeds remain a directional pilot.

Existing A4000 logs put a 100-carrier cross-attention run near 3.2--3.4 GPU-hours
and an affine run near 6.6 GPU-hours. At the recent $0.17/hour A4000 rate, stage 2
is roughly 40 GPU-hours / $7 before overhead, and stage 3 roughly 80 GPU-hours /
$14. These are planning estimates, not billing guarantees.

## Primary estimands

Use held-out, common-random-number trial banks and analyze the factorial directly:

- behavioral cueing: invalid-minus-valid psychometric threshold and normalized
  response-AUC gap;
- representation: true-change minus cue-region routing mass after the change,
  plus held-out change-location decoding;
- causal use: true-change-location suppression/rescue and natural-vs-disabled
  routing, with both `d-prime` and criterion;
- factorial contrasts: visual main effect, memory main effect, and V x M synergy,
  reported separately by routing family.

Do **not** use the easy 30-degree endpoint as the primary causal probe: one completed
100-token seed was saturated under natural, uniform, shuffled, and disabled routing.
Choose a frozen per-checkpoint magnitude from a separate calibration bank that puts
invalid detection near 50--70%, then evaluate all interventions on a disjoint bank.

## Coherent/actionable percept test

Stream count alone is not the full hypothesis. After the factorial checkpoints are
trained, add an inference-only, rank-preserving *binding intervention*: cyclically
remap the four recurrent quadrant states to the wrong visual quadrants during the
cue-delay and/or change window. The number of visual streams, memory streams,
parameters, and state values is unchanged; only visual-memory correspondence is
broken. Compare aligned, cyclically shifted, and restored mappings on paired trials.

The coherent/actionable-percept account predicts that:

1. more memory streams help only when they can remain bound to distinct visual
   streams (a V x M interaction, not two independent monotonic effects);
2. breaking the binding should selectively reduce cue-localized delay routing,
   change-location decoding, and true-location rescue beyond any generic accuracy
   loss; and
3. restoring the mapping should restore those effects within the frozen model.

This binding intervention still needs a small, separately tested feedback-remapping
hook. It is deliberately not hidden inside the projector scaffold.

## Evidence gates

Every scientific cell retains the existing production contract: fresh exact seed,
20,000 contiguous finite rows (0--19,999), terminal final/latest checkpoints,
schema/config/source/launcher hashes, clean log, and held-out behavior. A run that
fails the competence gate or saturates the registered causal probe is recorded as
non-informative for that estimand, not interpreted from training accuracy.

Run the scaffold checks with:

```powershell
python -m pytest -q experiments/vda_stream_factorial/test_stream_model.py
python -m experiments.vda_stream_factorial.design_matrix
```

Run the production-contract checks with:

```powershell
python -m pytest -q experiments/vda_stream_factorial/test_stream_model.py `
  experiments/vda_stream_factorial/test_production_contract_v1.py
```

On a prepared Linux GPU worker, the four engineering canaries are queued
sequentially with:

```bash
bash experiments/vda_stream_factorial/queue_crossattn1_canaries_v1.sh
```

They are engineering checks, never attention evidence.  After all four pass the
registered canary contract, queue one complete four-cell production block for a
registered seed with:

```bash
bash experiments/vda_stream_factorial/queue_crossattn1_seed_v1.sh 0
```

Repeat for seeds 1 and 2 without inspecting effect direction between seeds.
