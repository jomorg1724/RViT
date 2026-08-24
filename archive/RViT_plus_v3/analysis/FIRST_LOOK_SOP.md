# SOP — "First Look" at a trained RViT+ model

Standardized first-pass inspection of any freshly-trained RViT+ checkpoint.
One command, one output folder, one digest. Run this before any deeper analysis.

## Run it

```bash
# From the repo root. Defaults to <pkg>/checkpoints/rvit_plus_rl_final.pt.
.venv/bin/python RViT_plus_v3/analysis/first_look.py --open
```

Useful flags:
- `--checkpoint <path>` — analyze a specific checkpoint (default: `final.pt`, fallback `latest.pt`).
- `--device mps|cpu|cuda` — default `cpu` (reliable; `mps` is faster if no training is competing).
- `--n-trials N` — trials per condition cell (default 200).
- `--thorough` — 384 trials + finer |Δθ| bins (smoother curves, slower).
- `--skip-psychometric` / `--skip-attention` — run only one half.
- `--out-dir <dir>` — default `analysis/figures/first_look/`.

**Checkpoint discipline.** The script prints the exact file + `iter` it loaded.
`final.pt` is the completed run; `latest.pt` is whatever a *currently-running*
training last saved (often undertrained). Analyze `final.pt` unless you
deliberately want a mid-training snapshot. A running job won't overwrite
`final.pt` until it completes.

## What it produces (in `analysis/figures/first_look/`)

**Behavior — psychometric / chronometric** (`psychometric_chronometric.py`):
| File | Content |
|---|---|
| `psychometric_chronometric_signal.png` | EXP1: P(hit) & RT vs `|Δθ|`, valid vs invalid — the spatial **cueing/validity effect** |
| `psychometric_chronometric_validity.png` | EXP2: cued accuracy & RT vs displayed ring validity {0.25…1.0} |
| `psychometric_chronometric_value.png` | EXP3: cued accuracy & RT vs cue value {blue=1, green=3, red=5} |
| `psychometric_*.csv` | raw numbers + SEMs for each experiment |

**Attention — channel/head-summed heatmaps** (`avg_attention_maps.py`):
| File | Content |
|---|---|
| `avg_attn_L{1,2,3}_<cond>_chg0_t15.png` | per-timestep summed-attention heatmap strip, per layer, per cue condition |
| `avg_attn_alpha_L{1,2,3}_chg0_t15.png` | per-quadrant aggregate attention over time, all conditions overlaid |
| `avg_attn_chg0_t15.npz` | raw arrays for re-plotting |

Conditions: cue **left/right** × ring **1.0/0.25**, with the change fixed
(top-left, t=15, large `|Δθ|`). cue-left = **valid**, cue-right = **invalid**.

## How to read the digest

The script prints a text digest at the end:
- **Psychometric**: per-`|Δθ|` valid/invalid hit rates, the 50%-threshold for each
  (the leftward shift = attention benefit), the max P(hit) gap, and a verdict
  (`cueing effect PRESENT` if the gap exceeds 0.05).
- **Validity scaling**: accuracy trend from validity 0.25→1.0 (`scales` vs `flat/null`).
- **Value scaling**: accuracy spread across colors (`value modulation` vs `flat/null`).

The published target signature (Morgan, Albanna & Herman 2025): cued stimuli
show **higher accuracy and faster RT, scaling with cue validity**. The first-look
digest tells you at a glance whether a new model reproduces it.

## Architecture portability

The two underlying scripts are architecture-agnostic:
- **Psychometric/chronometric** only reads behavior (actions/rewards) — works on any model.
- **Averaged attention** sums the attention tensor over `dim=1`, so it adapts to
  whatever the attention map is: V2's per-channel softmaxes `(B,C,H,W)` or V3's
  per-head sigmoid gates `(B,n_heads,H,W)`. "Sum all heads" is the same operation.

To stand this up for another package (e.g. `RViT_plus_v2`), copy `first_look.py`,
`psychometric_chronometric.py`, `avg_attention_maps.py`, and `_behav_utils.py`
into that package's `analysis/` (they use package-relative imports), then run
`<pkg>/analysis/first_look.py`.
