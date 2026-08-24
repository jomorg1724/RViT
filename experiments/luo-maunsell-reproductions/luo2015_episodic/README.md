# Paired episodic Luo–Maunsell optimization experiment

## Decision

A continuously learning agent is **not required** to test the paper's reward-optimization prediction. This experiment estimates the fixed-condition policy optima. It does not claim to reproduce online adaptation when a biological session switches reward blocks.

For each training seed:

1. Train one neutral perceptual parent with equal hit and correct-rejection rewards and the existing VDA xLSTM/affine-feedback/conv/JEPA optimizer.
2. Require the parent to reach the target orientation difference and pass a deterministic, balanced held-out gate at that exact difficulty: at least 75% accuracy and 90% valid engagement separately for change/no-change trials at locations 0 and 3.
3. Fork the exact parent checkpoint into four independent episodic agents:
   - sensitivity rewards, favored location 0;
   - sensitivity rewards, favored location 3;
   - criterion rewards, low-criterion location 0;
   - criterion rewards, low-criterion location 3.
4. Keep the condition, reward table, session orientations, and difficulty fixed within every child run. There is no reward-condition cue.
5. Evaluate all four policies on the same deterministic, balanced stimulus bank.

This is a paired optimization design: the four children for a seed have identical inherited weights, architecture, and training budget. Only the fixed reward objective differs. The trainer strictly loads all parent tensors, verifies the launcher's expected SHA-256, and embeds the original parent hash and iteration in every child checkpoint. Resumes preserve that immutable initialization root; neither the launcher nor analyzer accepts a stale child relabeled against a replacement parent.

## Reward scaling

The environment preserves the paper-supported within-session reward ratios. A single positive multiplier normalizes the average correct-outcome reward to approximately one in each session:

- sensitivity: `(1 / 3)` because the two location means are 5 and 1;
- criterion: `(1 / 0.95)` because the two location means are 0.9 and 1.0.

This does not change an unregularized policy optimum, and it limits an avoidable optimizer-scale confound from the fixed entropy/value coefficients.

All parent and child runs use `gamma=1.0`. Because hit/false-alarm rewards can occur at the first test while correct-rejection rewards occur at the second test, discounting would otherwise change the intended hit:CR objective rather than merely rescale it.

## Primary estimands

For metric `m`, define the counterphased location contrast

`DID(m) = 0.5 * [(m_loc0 - m_loc3)_condition0 - (m_loc0 - m_loc3)_condition3]`.

Preregistered directional predictions:

- sensitivity session: `DID(d-prime) > 0`;
- criterion session: `DID(c) < 0`.

Specificity estimates are `DID(c)` in sensitivity sessions and `DID(d-prime)` in criterion sessions. A nonsignificant result is not evidence of no cross-effect; declare equivalence bounds before using the word “selective.”

## Commands

The matrix launcher supports the two VDA feedback families with the same xLSTM
carry-decay intervention. Use `--memory-decay 0.5` for heavy decay and
`--noise 0.5` for small orientation jitter. Keep the affine and cross-attention
matrices in separate run roots and run them one at a time on MPS. From this
repository root, use `../.venv/bin/python`; do not substitute `python3`, which
may resolve to a uv interpreter without Torch.

Dry-run the full matrix without creating files:

```bash
../.venv/bin/python experiments/luo2015_episodic/run_matrix.py \
  --run-root runs/luo2015_episodic_full \
  --seeds 0 1 2 3 4 \
  --parent-iters 20000 --child-iters 20000 \
  --theta 18 --device mps
```

Execute or safely resume it:

```bash
../.venv/bin/python experiments/luo2015_episodic/run_matrix.py \
  --run-root runs/luo2015_episodic_full \
  --seeds 0 1 2 3 4 \
  --parent-iters 20000 --child-iters 20000 \
  --theta 18 --device mps --execute
```

The only child-launch gate is neutral-parent competence. The parent must first reach target theta, then pass 100 held-out change and 100 held-out no-change trials at each of locations 0 and 3. Every location/status cell must have accuracy at least 0.75 and valid engagement at least 0.90. The bank is deterministic and generated at target theta, not inferred from aggregate curriculum performance. If any cell fails, no reward-condition child is launched. Gate thresholds and trial counts can be changed explicitly with `--parent-min-accuracy`, `--parent-min-valid-fraction`, and `--parent-gate-trials`; doing so creates a different manifest contract.

At child launch, the orchestrator computes the completed parent's SHA-256 and injects it as `--expected-parent-sha256`. This runtime value is intentionally absent from dry-run commands because the parent does not exist yet. Existing final checkpoints are reused only after their complete embedded task, reward table, theta, curriculum, iteration, discount, and initialization contracts pass.

Evaluate completed children on a common balanced trial bank:

```bash
../.venv/bin/python experiments/luo2015_episodic/analyze_matrix.py \
  runs/luo2015_episodic_full \
  --magnitudes 18 --trials-per-location 200 --batch-size 64
```

The output is `runs/luo2015_episodic_full/episodic_evaluation.json`.

## Canary versus evidence

`--canary` explicitly bypasses only the behavioral competence gate and is only for plumbing verification. It still enforces neutral-parent protocol identity, strict parent loading, embedded lineage, reward-table identity, fixed theta, and `gamma=1.0`. Canary checkpoints and their SDT output are not scientific evidence; the analyzer rejects canary manifests. A full run omits `--canary`, passes the hard gate, trains all paired children, and supports the specified contrasts.

## Claim boundary

This design can test whether different reward functions produce the predicted criterion/sensitivity optima under the existing episodic VDA training procedure. A continuously stateful agent would be needed only for a separate hypothesis about adaptation speed, inference of hidden block switches, or trial-history effects.
