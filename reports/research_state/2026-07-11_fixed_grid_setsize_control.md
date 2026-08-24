# Controlled fixed-grid VDA set-size family

**Producer:** `RViT_plus_paper_jepa_grid9/`  
**Status:** environment and registration implemented; no training run is authorized or represented by this document.

## Condition table

| Task ID | Active items (K) | Grid | Image | Model tokens (N) | Inactive cells |
|---|---:|---:|---:|---:|---|
| `vda_fixed1` | 1 | 4×4 | 100×100 RGB | 16 | blank |
| `vda_fixed2` | 2 | 4×4 | 100×100 RGB | 16 | blank |
| `vda_fixed4` | 4 | 4×4 | 100×100 RGB | 16 | blank |
| `vda_fixed9` | 9 | 4×4 | 100×100 RGB | 16 | blank |
| `vda_fixed16` | 16 | 4×4 | 100×100 RGB | 16 | none |

Active locations are sampled without replacement through the project's existing NumPy RNG convention. The cue is sampled from the active set, and a realized change target is always active.

## Controlled factors

These defaults are identical for all five task IDs; a controlled training program must keep them identical unless it declares a different experiment family.

| Factor | Fixed value / rule |
|---|---|
| Geometry | 4 rows × 4 columns; row-major token/stimulus correspondence |
| Image and observation | 100×100×3 `float32` |
| Model-facing dimensions | 16 visual tokens; shared convolutional front end (`--conv-frontend` is required for training); token width `128 + 16 + 8 = 152` |
| Logical timing | 7 logical frames; cue at frame 1; blank frames 0 and 2; stimuli from frame 3 |
| Change timing | frame 5 by default (`min_change_time=max_change_time=5`) |
| Frame repeat | 1 by default |
| Renderer | shared Gabor and cue renderer; inactive cells skipped and left zero |
| Sensory noise | `noise_multiplier=5.0` by default |
| Change magnitude / curriculum interface | same `theta` and curriculum controls |
| Validity support | `(0.25, 0.5, 0.75, 1.0)` by default |
| Validity sampling, K≥2 | exact Bernoulli validity; invalid branch excludes the cue |
| K=1 validity caveat | no uncued active target exists, so every realized change is cued; metadata reports `effective_validity=1.0`, `validity_mode=degenerate_singleton`, and a caveat even if the displayed ring encodes another value |
| Value cue and reward | same red/green/blue cue values (5/3/1), reward scale, action space, and reward logic |
| Variable factor | active item count only: 1, 2, 4, 9, or 16 |

## Future-run immutability rule

Future training must create **immutable child runs**, one unique child for every `(task ID, training seed, frozen config, source snapshot)` tuple.

- Never resume one set-size condition into another condition's directory.
- Never overwrite a completed child's metrics, config, manifest, or checkpoints.
- A continuation must be recorded as a new child linked to its parent checkpoint, not as an in-place rewrite.
- Each child must record the exact command, task ID, seed, resolved config, source-tree hash, parent checkpoint identity (if any), and output/checkpoint hashes.
- Replicates must use distinct child IDs/directories so between-training-seed uncertainty remains recoverable.

The legacy `vda1`, `vda2`, `vda4`, `vda9`, and `vda16` tasks remain available for historical compatibility but are not substitutes for this controlled family because their geometries and model-facing dimensions are not all matched.
