# AGENT_HANDOFF — start here

**WHAT THIS IS:** an agent-to-agent handoff so the next Claude/coding-agent is caught up on the **JEPA-variant recurrent-ViT attention models** (4-stimulus and 9-stimulus, each in `affine_ew` and `crossattn1` feedback flavors), the **reference paper** they model, how to **write the reports/manuscripts**, and the **relevant literature**. Unlike the deliverable `.tex` manuscripts, these docs deliberately expose process, file paths, run commands, and current state — that is their job.

Read order: **this file → the doc you need.** If you only have five minutes, read **"State of play"** and **"Critical operational facts"** just below.

---

## State of play — how far we got (as of 2026-07-04)

- **All four models exist and are trained/working.** On **SS4** (`RViT_plus_paper_jepa_conv/`): `affine_ew` is at curriculum **θ≈50**, `crossattn1` at **θ≈62** (both ~0.80–0.85 correct at their current difficulty). On **SS9** (`RViT_plus_paper_jepa_grid9/`): both variants are built and documented. **Trust each checkpoint dir's `metrics.csv` for live θ / correct-rate over any number quoted in these docs** — the live runs keep advancing.
- **Deliverables done:** the four figure-reproduction papers (`repro/paper_{affine_ew,crossattn1}.tex`, `repro9/paper9_{affine_ew,crossattn1}.tex`) and the deep-dives (`deepdive/`, `deepdive_affine/`, `deepdive9/`) are built and adversarially reviewed; findings are distilled in `02_model_4stim.md` / `03_model_9stim.md` and the memory files.
- **The memory-leak investigation is CLOSED.** Root cause = a known, open PyTorch **Apple-MPS backend** leak (graphCache/allocator; pytorch #164299/#16445) — **not our code, not a torch version, no env-var or in-loop fix** (all tested). Every attempted fix (batched-patch, auto-resume wrapper, in-loop `empty_cache`/`gc`, `PYTORCH_MPS_*` knobs) was tried, didn't address the cause, and was **reverted** — the code is intentionally back to its plain, leaky form. Only leak-free path = `--device cpu`; otherwise reload-after-OOM (~10k iters/session). Full write-up: memory `reference_torch212_conv_backward_leak.md` + "Critical operational facts" below.
- **What's open / next:** walk the curriculum θ down toward the floor on both SS4 variants (reload after each OOM, or run on CPU unattended); some SS9 set-size×validity results in `03_model_9stim.md` are still **predictions** awaiting more trained-and-measured confirmation.

---

## The five docs

| Doc | What it covers |
|---|---|
| [01_reference_paper.md](01_reference_paper.md) | The Herman-Lab reference paper **"When Does Value-Directed Attention Matter?"** (Morgan, Albanna & Herman) + supplement/appendix: the task, every main & supplementary figure, the SDT (criterion/d′), decoding, actor-logit, TD/value, "stimulation"/criterion-shift, and supervised-vs-RL analyses, and the paper's predictions. Says which manuscript dir is canonical. |
| [02_model_4stim.md](02_model_4stim.md) | The **set-size-4** model (`RViT_plus_paper_jepa_conv/`, the 2×2 `vda4` task): full architecture with file:line pointers, `affine_ew` vs `crossattn1`, training recipe + curriculum, per-variant findings, run commands, checkpoints, and the current MPS-leak operational state. |
| [03_model_9stim.md](03_model_9stim.md) | The **set-size-9** model (`RViT_plus_paper_jepa_grid9/`, the 3×3 `vda9` task): same structure, emphasizing what diverges at SS9 — the set-size × validity result (invalid-cue "change-lock" recovers at SS4 but is abolished at SS9; grid9 `crossattn1` uses validity). Flags which SS9 results are trained-and-measured vs predictions. |
| [04_report_paper_formatting.md](04_report_paper_formatting.md) | How to write the outputs: the two formats (full **figure-reproduction paper** vs **deep-dive** 8-section Lisman-Grace card), the LaTeX scaffolding, and the **HARD RULES** (no-meta/positive framing for deliverables, PRIORITY/VALUE terminology, judge-by-behavior, prove-don't-guess), plus how to add `research_db` notes. |
| [05_research_reading.md](05_research_reading.md) | Curated, theme-grouped reading list into `research_db/` (~261 paper-notes): the target phenomenon, JEPA/SSL, predictive coding, attention/WM, dopamine/RL, transformers/xLSTM, cortical microcircuits — each with "why it matters here." Explains the arXiv:2502.10955 lineage. |

---

## The one-paragraph mental model

Each model is a **recurrent vision-transformer trained by RL** to do a **covert-attention change-detection task** taken from the reference paper. Pipeline: a **conv SE-ResNet front-end** encodes image patches → a **recurrent-ViT self-attention encoder** with a **feedback mechanism** (this is the variable that names the variant) → a **spatial xLSTM** working memory → **distributional actor-critic (QR-DQN) heads** plus a **JEPA self-distillation head**. Two task sizes: **SS4** (four Gabors, 2×2) and **SS9** (nine Gabors, 3×3). Two feedback flavors per size: **`affine_ew`** (FiLM-style element-wise affine modulation) and **`crossattn1`** (memory-as-tokens cross-attention). Call the two functional streams **PRIORITY** (drives the decision/policy) and **VALUE** (drives valuation) — never "salience/top-down." The whole program is a follow-up to **arXiv:2502.10955** and models the Herman-Lab paper's empirical signatures.

The four models, concretely:

| | `affine_ew` | `crossattn1` |
|---|---|---|
| **SS4** (`RViT_plus_paper_jepa_conv/`) | `repro/paper_affine_ew.tex`, `deepdive_affine/` | `repro/paper_crossattn1.tex`, `deepdive/` |
| **SS9** (`RViT_plus_paper_jepa_grid9/`) | `repro9/paper9_affine_ew.tex` | `repro9/paper9_crossattn1.tex` |

---

## Critical operational facts (read before you train anything)

1. **There is a real, unfixable-by-us memory leak when training on MPS.** It is a **known, open PyTorch bug in Apple's MPS backend** (graphCache/allocator; pytorch/pytorch #164299, #16445). It reproduces with a *stock* `Conv2d`+`GroupNorm` stack — **not our code**. MPS leaks (~1.5–4 MB/iter for the full model); **CPU is flat**. It is version-independent (2.8→2.12.1) and **not fixed by `empty_cache()`/`gc`**. Full write-up: memory file `reference_torch212_conv_backward_leak.md`.
   - **Consequence:** an MPS run OOMs (`zsh: killed`) at ~iter 10–12k / ~3–4 h. The accepted workflow is **run → OOM → rerun the same command to resume from the latest checkpoint.** (CPU trains leak-free but ~2.5–3× slower.)
   - **Do NOT** re-introduce a batched-patch, an auto-resume wrapper, or in-loop cache-flushing — those were tried, don't fix the cause, and were explicitly reverted on 2026-07-03. The code is intentionally the plain, leaky version.

2. **The curriculum** (paper's difficulty ramp): `theta` (max orientation change magnitude, Δ ~ U(−θ,θ)) starts at **65**, drops by **3** each time the agent averages **≥85% over a non-overlapping 1000-trial window**, floored at `theta_floor`. Logic lives in `envs/base.py:_update_curriculum`. It is **correct and unchanged**.
   - **Gotcha A:** the 1000-trial success window (`_recent_correct`) is **not saved in the checkpoint** — only `theta` is. Every reload restarts the window empty. Over a full session many windows complete, so this only matters at the margins, but if θ appears "stuck," this is why.
   - **Gotcha B:** the `crossattn1` checkpoint predates θ-saving — its `*_latest.pt` has **no `theta` key**, so a `--curriculum` resume falls back to `--theta-start` (65) and **loses θ progress**. Pass **`--theta-start 62`** (its last known θ) when resuming crossattn1. The `affine_ew` checkpoint does carry `theta` (=50) and restores correctly. Details in `02_model_4stim.md §7–8`.

3. **The displayed `correct=` in the training log is a rolling display average**, not the curriculum's 1000-trial block statistic. Don't conclude "it's above 85%" from the log line.

4. **Resume-training command** (SS4 `affine_ew`, the plain leaky MPS path — the current default):
   ```
   source .venv/bin/activate && python RViT_plus_paper_jepa_conv/train_rl.py --device mps --init-mode resume --T 7 --min-change-time 5 --max-change-time 5 --cell xlstm --feedback affine_ew --conv-frontend --jepa-coef 0.5 --d-mem 128 --curriculum --theta-start 65 --iters 20000 --save-every 200 --checkpoint-dir ~/rvit_plus_checkpoints/paper_jepa_conv_affine_ew
   ```
   For `crossattn1`: swap `--feedback crossattn1`, its checkpoint dir, and add `--theta-start 62` (see Gotcha B). For the grid9/SS9 models see `03_model_9stim.md`. To train leak-free, swap `--device mps` → `--device cpu`.

---

## Where the durable knowledge lives

- **These handoff docs** — the models, paper, formatting, research (this dir).
- **Memory files** (`/Users/jonathanmorgan/.claude/projects/-Users-jonathanmorgan-AttentionManuscript/memory/`, indexed in `MEMORY.md`) — distilled, cross-linked facts and hard-won corrections. Especially: `reference_torch212_conv_backward_leak.md`, `project_full_figure_reproductions.md`, `project_setsize_invalid_manuscript.md`, and the `feedback_*` working-principle notes. **Verify a memory's file/symbol references still exist before acting on them.**
- **`research_db/`** — the literature (see `05_research_reading.md`).
- **The manuscripts themselves** — `RViT_plus_paper_jepa_conv/{repro,deepdive,deepdive_affine}/*.tex` and `RViT_plus_paper_jepa_grid9/{repro9,deepdive9}/*.tex`.

## Scope of this handoff

Covers the **two JEPA repos** named by the user — `RViT_plus_paper_jepa_conv` (SS4) and `RViT_plus_paper_jepa_grid9` (SS9), each with both feedback variants. It deliberately does **not** document the many sibling `RViT_plus_*` experiments (`_jepa_fr`, `_jepa_smem`, `v5`–`v15`, `setsize9*`, ViZDoom, etc.); those have their own memory notes if needed.
