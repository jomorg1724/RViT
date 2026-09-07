# KimiDecayVDAConvRecurrentTF

## Corrected supervised protocol: `blank_first_v1`

The old reset-discarding supervised collector and its results are invalid. Do not restore its weights, analyses, baselines, launchers, or takeoff claims from historical commits or backups.

The model processes **seven images**, not seven calls to `step()`:

| Model input | Environment time | Image | Label on a changed trial |
|---|---:|---|---:|
| 0 | 0 | Initial blank returned by reset | 0 |
| 1 | 1 | Cue | 0 |
| 2 | 2 | Blank | 0 |
| 3 | 3 | Sample | 0 |
| 4 | 4 | Sample | 0 |
| 5 | 5 | Changed test | 1 |
| 6 | 6 | Changed test | 1 |

Unchanged-trial labels are all zero. The terminal observation at t7 is not an input. Collection and frame endpoint indexing live in `envs/sequences.py`. Checkpoints record the protocol and physical/model time indices; resume rejects missing or incompatible sequence metadata before loading weights.

## Fresh no-memory launcher

```bash
python launch.py --root /workspace/runs/nomem_blank_first_v1_seed3
```

The launcher refuses an occupied output directory, does not accept a resume path, and records `parent_checkpoint: null`. It uses VDA16, C128, token attention, H1=Z, H2 as the raw weighted X/H attention sum, independently normalized split softmax, sampled straight-through attention, and an H2 convolutional classifier. Dedicated memory is removed; visual accumulation and recurrent H1 still exist. Training is fp32 without AMP, with JEPA coefficient zero. See `launch.py` for the complete explicit argv and `corrected_contract.json` for the tested sequence contract.

The scoped verification suite is:

```bash
python -m pytest tests/test_supervised_sequence.py tests/test_raw_nomem.py tests/test_sample_attention.py tests/test_sample_attention_trainer.py tests/test_vision_qk_norm.py tests/test_attention_entropy.py tests/test_launch.py -q --rootdir=.
```

These tests include actual trainer-to-model input and label capture, incompatible-resume rejection, split normalization, and sampled-attention/readout behavior. Tests and GPU canaries validate plumbing, not scientific competence.

Reset-correct RL training is a separate, preserved lineage. Do not use its results as the supervised same-architecture baseline.
