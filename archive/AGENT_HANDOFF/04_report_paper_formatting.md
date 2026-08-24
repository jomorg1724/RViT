# 04 — Report / Paper Formatting Guide

**WHAT THIS IS:** The rules for writing the LaTeX manuscripts and research_db notes for this project — the two deliverable formats, the exact LaTeX scaffolding, the HARD RULES (each with its WHY), and how to add research_db notes. Read this before writing any `.tex` or any `research_db/` page.

**Sibling handoff docs (read the ones you need):** [`01_reference_paper.md`](01_reference_paper.md) · [`02_model_4stim.md`](02_model_4stim.md) · [`03_model_9stim.md`](03_model_9stim.md) · `04_report_paper_formatting.md` (this file) · [`05_research_reading.md`](05_research_reading.md) · [`README.md`](README.md) (index — **start here**)

> **Terminology used throughout this doc (and mandatory in every deliverable):** the two feedback streams are **PRIORITY** (the stimulus-grounded, image-residual stream that drives the **decision / policy → actor**) and **VALUE** (the memory-anchored stream that drives **valuation → critic**). Never write "salience" / "top-down" in user-facing text or figures. See HARD RULE 3.

---

## 0. Orientation: where things live

```
AttentionManuscript/
├── AGENT_HANDOFF/                         ← internal agent docs (this dir; the deliberate no-meta EXCEPTION — see §6)
├── reports/                               ← standalone multi-file manuscripts
│   ├── setsize_invalid_manuscript/        ← main.tex + sections/*.tex + figures/*.png + refs.bib
│   ├── loop_routing_manuscript/           ← same split-file layout (+ tikz for the loop diagram)
│   ├── crosstalk_manuscript/
│   ├── thesis/
│   └── publication_plan.md
├── RViT_plus_paper_jepa_conv/
│   ├── repro/                             ← FIGURE-REPRODUCTION papers (paper_*.tex) + repro_fig*.py
│   └── deepdive_affine/                   ← DEEP-DIVE paper (affine_ew_deepdive.tex) + dda_*.py
├── RViT_plus_v11_part5/analysis/          ← the CANONICAL figure-builder pattern: ddstyle.py + make_figures.py
├── research_db/                           ← the vault (papers/, concepts/, notes/, threads/, briefs/, _conventions/)
└── .venv/                                 ← the ONE venv at repo root
```

Run convention (from [feedback: run-command convention]): activate the repo-root venv and invoke plain `python -m <module>`. Two accepted forms:
```bash
source /Users/jonathanmorgan/AttentionManuscript/.venv/bin/activate && python -m RViT_plus_v11_part5.analysis.make_figures
# or directly:
/Users/jonathanmorgan/AttentionManuscript/.venv/bin/python -m RViT_plus_v11_part5.analysis.make_figures
```
Do NOT invent `VENV=` vars or `_curr` dirs. Start from the README/module command and change only what's needed. `torch.set_num_threads(3)` and an `OMP`/torch cap of 3 are already set in the analysis cores — keep them; one compute job at a time (see [feedback: cap CPU on the laptop]).

---

## 1. The TWO deliverable formats — and when each is used

There are exactly two manuscript shapes in this project. Pick by what the deliverable must *do*.

### (a) FIGURE-REPRODUCTION paper — "does this variant reproduce the reference paper?"
**What it IS:** a single-`.tex` paper that reproduces **every** figure (main **and** supplement) of the Morgan/Albanna/Herman reference paper for **one model variant**, panel-for-panel, from that variant's own data — and states where the variant *agrees* and where it *diverges*.

- **Canonical example:** `/Users/jonathanmorgan/AttentionManuscript/RViT_plus_paper_jepa_conv/repro/paper_affine_ew.tex` (and its twin `paper_crossattn1.tex`).
- **Section spine (one `\section` per reference-figure block):** Introduction · Task and model · Behaviour (psychometrics/chronometrics) · Attention allocation dynamics · Feedback mechanism · Causal attention manipulations · Decoding the mnemonic percept · Actor-logit geometry · Value/TD/entropy · Signal detection (criterion & sensitivity) · Supervised vs RL · Discussion · Methods (variant). One figure = one reference figure; caption header names the reference figure it maps to (`\textbf{Fig 8 --- decode change LOCATION from $H$.}`).
- **Figure count:** ~17 figures (Figs 1–17 of the reference, main + supplement). This is a *coverage* deliverable — omitting a reference figure is a defect. Where the variant is RL-only and a reference column (e.g. supervised) doesn't apply, reproduce the applicable column and mark the rest "out-of-scope baselines for this RL-only variant" (see the Fig-17 analog).
- **Data → figure pipeline:** each `repro/repro_figN.py` loads the checkpoint via `repro_core.load(snap, feedback)`, runs the analysis, caches to `repro/data_figN_<variant>.npz`, and emits `repro/figs/figN_<variant>.png`. `\graphicspath{{figs/}}` picks them up. The variant is threaded by the `feedback` arg (`"affine_ew"` vs `"crossattn1"`) so the same scripts produce both papers.

### (b) DEEP-DIVE paper — "what is this ONE variant actually doing, at reference depth?"
**What it IS:** a Lisman-Grace-style deep interrogation of a **single variant**, ~3000 words / **20–30 pp**, that reaches the **four-pillar reference depth** (HARD RULE 4). Not a reproduction of the reference figure set — an *original mechanistic dissection*.

- **Structural template:** `/Users/jonathanmorgan/AttentionManuscript/RViT_plus_paper_jepa_conv/deepdive_affine/affine_ew_deepdive.tex` — the single-file preamble, the block-math box, the positive abstract, the maps→decoding→behaviour Results spine (note: this particular file is ~12 pp / 7 figs and centres on the maps + decoding pillars, so it is the *layout* exemplar, not a full four-pillar one). **Full-depth exemplar of the four pillars:** `RViT_plus_v11_part5/analysis/deepdive/` (the `RViT_plus_v11_part5_distractor_deepdive` rebuild, ~20 pp / 12 figs, built from `paper/paper.md` + `build.sh`), whose `exp3_latent_decoding.py` / `exp4_causal_attention.py` / `exp5_value_entropy.py` supply the decoding, causal-battery, and value pillars.
- **The four pillars a deep dive MUST hit** (all four, or it is "slop" — the user's word for a thin one):
  1. **Spatial attention MAPS** — the signature figure. Per-condition × per-timepoint heatmaps of the raw attention (e.g. the `4×4` `A[query→key]` maps across all cue×change conditions and every frame, or `10×10` for the distractor task). **Not** line-plot summaries standing in for maps.
  2. **Causal-perturbation BATTERY** — per-region bias sweeps, the decision-vs-value dissociation, a d′ shift. **Not** one sweep.
  3. **Psychometric / chronometric 4-param logistic FITS** — valid-vs-invalid × reliability, `P(Δ)=A+(1−A−B)/(1+e^{−(Δ−D)/C})`.
  4. **TEMPORAL decoding** — every task variable, every frame (position, value, validity/proportion, change location/occurrence), showing what the recurrence *retains vs discards*.
- **Section spine:** Model and task (with the exact block equations) · Results (attention schedule → maps → causal battery → decoding → behaviour/psychometrics → value) · Discussion · (Methods folded in or separate). Abstract states the headline mechanism positively.
- **Data → figure pipeline:** the `dda_*.py` scripts. `dda_core.py` = load + attention/press/decode primitives; `dda_maps.py`, `dda_proportion_attn.py`, `dda_response.py`, `dda_value.py` each SAVE a `summary_*.npz` / `data_*.npz`; a light builder plots from the npz. Same compute/plot split as the repro papers.

**Which one to write?** New variant, "does it reproduce the paper?" → (a). "What is variant X *doing*, mechanistically, at depth?" → (b). A standalone scientific claim about a manipulation (set-size, loop-routing) that isn't the full reference figure set → a `reports/<name>_manuscript/` multi-file paper (same LaTeX conventions as below, split into `sections/`).

---

## 2. Concrete LaTeX scaffolding

Two established preambles. Match the one closest to your deliverable.

### 2a. Single-file paper (repro + deep-dive) — compact preamble
From `paper_affine_ew.tex` / `affine_ew_deepdive.tex`:
```latex
\documentclass[11pt]{article}
\usepackage[margin=1in]{geometry}
\usepackage{amsmath,amssymb,bm,graphicx,booktabs,caption,subcaption}
\usepackage[table]{xcolor}\usepackage{hyperref}
\hypersetup{colorlinks=true,linkcolor=blue!50!black}
\graphicspath{{figs/}}\captionsetup{font=small}
\title{\textbf{ ... }}
\author{ ... }            % descriptive line, NOT a build note — see HARD RULE 1
\date{ ... }              % a checkpoint identifier is OK; a "progress" claim is NOT — HARD RULE 2
\begin{document}\maketitle
\begin{abstract}\noindent ... \end{abstract}
% \section per reference-figure block; one \begin{figure}[h] per figure
\end{document}
```

### 2b. Multi-file manuscript (`reports/*_manuscript/`) — full preamble with bib
From `reports/loop_routing_manuscript/main.tex` and `reports/setsize_invalid_manuscript/main.tex`:
```latex
\documentclass[11pt]{article}
\usepackage[utf8]{inputenc}\usepackage[T1]{fontenc}\usepackage{lmodern}
\usepackage[a4paper,margin=1in]{geometry}
\usepackage{amsmath,amssymb,amsthm,mathtools}
\usepackage{graphicx}\graphicspath{{figures/}}
\usepackage{tikz}\usetikzlibrary{arrows.meta,positioning,fit,backgrounds}  % only if you draw a circuit/loop
\usepackage{booktabs}\usepackage{xcolor}
\usepackage{caption}\captionsetup{labelfont=bf,textfont=small,labelsep=period}
\usepackage[round]{natbib}\bibliographystyle{plainnat}
\usepackage[colorlinks=true,allcolors=blue!50!black]{hyperref}
\title{\bfseries ...}
\author{Jonathan Morgan$^{1}$ \and Badr Albanna$^{2,3}$ \and James P.\ Herman$^{1}$ \\[4pt]
  {\small $^{1}$Department of Ophthalmology, University of Pittsburgh, Pittsburgh, PA 15219}\\
  {\small $^{2}$Department of Otolaryngology, University of Pittsburgh, Pittsburgh, PA 15219}\\
  {\small $^{3}$Duolingo, AI Organization}}
\date{Preprint --- draft}
\begin{document}\maketitle
\input{sections/abstract}\input{sections/intro}\input{sections/task_models}
\input{sections/results}\input{sections/discussion}\input{sections/methods}
\bibliography{refs}
\end{document}
```
- **Author block is fixed** for the submittable manuscripts: Morgan / Albanna / Herman with the Pittsburgh + Duolingo affiliations exactly as above.
- **Split into `sections/*.tex`** for multi-file papers (`abstract, intro, task_models/architectures, results, mechanism, neural_loop, predictions, discussion, methods`). One `\input` per section in `main.tex`.
- **Notation shorthands** go in the preamble as `\newcommand`s, and their *comment* should carry the priority/value meaning, e.g. from loop_routing: `\newcommand{\Zpri}{\mathbf{Z}_{\text{pri}}} % priority-pathway output (-> actor)`.
- **Build:** `pdflatex main ; bibtex main ; pdflatex main ; pdflatex main` (the build line is in a comment at the top of each `main.tex`). Single-file papers: `pdflatex paper_affine_ew` (twice if refs).

### 2c. Figure & caption conventions
- Every figure: `\begin{figure}[h]\centering\includegraphics[width=...]{figN_variant.png}\caption{\textbf{Fig N --- <title>.} <what each panel is, verbatim panel letters A/B/C...>}\label{fig:...}\end{figure}`.
- **Caption header is bold and names the figure/its reference analog**; body walks panels A, B, C… concretely (what's plotted, `n`, what the lines/points are, fit type). Captions carry the numbers-in-context so a skim of captions alone conveys the result.
- **Widths:** full-page `\textwidth`; two-up `0.47\textwidth ... \hfill ...`; single-panel `0.5–0.9\textwidth`. Don't clip.
- **Figures are generated by scripts, never hand-drawn or eyeballed.** The heavy analysis script SAVES an `.npz`; a light builder plots from it (compute/plot separation). This is load-bearing: it lets figures regenerate with no torch and keeps the style consistent.

### 2d. The figure-builder pattern (REUSE THIS)
Canonical files: `/Users/jonathanmorgan/AttentionManuscript/RViT_plus_v11_part5/analysis/ddstyle.py` (+ `make_figures.py`).
- `ddstyle.apply()` sets publication rcParams: `font.size=15`, `axes.titlesize=16` bold, tick labels ≥13, `constrained_layout=True`, spines off, `savefig.dpi=200`, `bbox="tight"`. Fonts **≥13–16** — the user rejected earlier figures for tiny fonts / overlaps / clipping.
- **Fixed palette** in `ddstyle`: `PRIORITY="#1f6fb2"`, `VALUE="#8e44ad"`, `TARGET="#2ca02c"`, `DISTRACT="#e6194b"`. The source comments already record `# priority pathway — drives the decision (was "salience")` / `# value pathway — drives the valuation (was "top-down")`. Use these colours consistently across every figure of a paper.
- `make_figures.py` runs `matplotlib.use("Agg")`, loads each cached `*_summary.npz`, and writes both `.png` and `.pdf`. **No torch import** in the builder.

---

## 3. The HARD RULES (imperatives + WHY)

These are strong, repeated user corrections. Violating them has burned trust before. Obey exactly.

### RULE 1 — Deliverables expose NO build process, source, scaffolding, iteration history, or "we found" meta.
**Do:** write the manuscript as the final, original, standalone artifact in the target venue's voice (Nature Neuroscience). State findings **positively**, at the strength the evidence supports.
**Do NOT:** describe the work as a *reconstruction / rebuild / revision / draft*; name, cite, or allude to any *prior / original / source / internal* paper it derives from; use internal tooling vocabulary (ledgers, claim ids, verdicts, critique, provenance, "defensible strength"); or frame a finding as a *correction/hedge* of some absent statement ("rather than asserting…", "not a categorical floor", "more honestly than…").
**WHY:** the user reacted very strongly (profanity, caps) when an agent's paper called itself a "reconstruction," named the source paper in the title/footnote, exposed the rebuild pipeline, and hedged findings as corrections — *"WRITE A PAPER WE WILL SUBMIT TO NATURE NEUROSCIENCE!"* The deliverable is submission-ready original science, full stop. Keep all provenance in private scaffolding files (or these handoff docs — §6), never in the `.tex`.
*(Note: reproduction papers legitimately compare a variant against "the original model" as a scientific referent — that's allowed and expected in the repro genre. What's forbidden is meta about **our own** build/rebuild/iteration process, and framing the manuscript itself as a reconstruction of a prior write-up.)*

### RULE 2 — Judge model maturity by BEHAVIOR, never by an iteration number.
**Do:** characterize a model by the accuracy/return you measure or the user states (e.g. "reaches ≈0.83 correct", "hit rate 0.794"). Treat a loaded model as matured unless told otherwise.
**Do NOT:** call a checkpoint "early / iter-X / undertrained / preliminary" based on its recorded `iter` field.
**WHY:** the same model is reloaded and trained cumulatively across many sessions, so the per-run `iter` counter **resets on each reload** and badly understates true training — a checkpoint reading `iter=1199` had ~10k+ cumulative iters and 90%+ accuracy. Framing a matured model as "early" is simply wrong and undersells the result. The per-run `iter` may appear only as a checkpoint *identifier* in `\date{}` (as `paper_affine_ew.tex` does: "Model checkpoint iteration 6,599"), never as a progress claim. *(Grep note: the existing `affine_ew_deepdive.tex` still contains the phrase "this checkpoint is early" — that predates this rule; do not copy it.)*

### RULE 3 — Terminology: PRIORITY stream (→ decision) and VALUE stream (→ valuation). Disambiguate overloaded terms.
**Do:** name the grounded, image-residual stream (Q=X, K=V=[H1‖H2], res=X → actor) the **PRIORITY stream** (controls the DECISION); name the memory-anchored stream (Q=X, K=V=H2, res=H2 → critic) the **VALUE stream** (controls VALUE). Keep "stream" as the noun. Use the fixed `ddstyle` PRIORITY/VALUE colours in figures.
**Do NOT:** write "salience" or "top-down" in user-facing text/figures.
**WHY:** in the neuroscience literature "salience/top-down" names the *bottom-up vs goal-directed* dichotomy, but in our model the ex-"salience" stream carries the cue's goal-directed bias + the decision and the ex-"top-down" stream carries value — roughly backwards. The biased-competition framing (priority/value) tells a clean, correct neuroscientific story. **Code-internal names stay as-is** (`sal_block`/`td_block`/`Z_sal`/`Z_td`/`sal_tag`) so checkpoint state-dict keys don't break — only USER-FACING text/figures use priority/value. **Disambiguate overloaded terms:** name the exact referent of "heads" (memory-cell heads vs attention heads vs JEPA-distillation-head heads), "stream", "validity" (displayed ring proportion vs empirical change-probability), etc.
*(Heads-up: `reports/setsize_invalid_manuscript/` still says "top-down read-out" in places — it predates this rule. Follow the rule going forward; that manuscript is a candidate for a terminology pass, not a template for the wording.)*

### RULE 4 — Deep dives MUST reach reference depth (the four pillars of §1b).
**Do:** include (1) spatial attention MAPS, (2) a causal-perturbation BATTERY, (3) psychometric/chronometric 4-param logistic FITS, (4) temporal decoding of every variable/frame. Target 20–30 pp.
**Do NOT:** ship a thin ~6 pp / 5-fig line-plot summary and call it a deep dive.
**WHY:** the user rejected a first thin v11_part5 deep-dive as "slop / lazy." A deep dive is calibrated to the Morgan-Albanna-Herman reference paper's depth; the attention maps are the *signature* figure and cannot be replaced by line-plot summaries.

### RULE 5 — Lead every build/write with a plain one-line "what it IS", and flag every default / judgment-call / load-bearing fork up front.
**Do:** open with one plain sentence of the actual dataflow/architecture (e.g. "conv front-end + element-wise affine self-attention + JEPA, 7-step vda4; memory modulates visual features element-wise before self-attention"). Then explicitly list every default and arbitrary choice ("I chose X; alternatives were Y/Z; defaulted to X because …"). Surface load-bearing forks *before* building.
**Do NOT:** bury implicit choices in prose where the user can't tell what was actually built vs asked for.
**WHY:** the user repeatedly got surprised by implicit choices (JEPA uses a CONTINUOUS xLSTM memory not the softmax-head categorical memory; "4 heads" = the JEPA head's heads; the JEPA softmax is over 256 prototype dims in a *projection* of the memory) — each a real default made without flagging, surfacing late after multi-hour runs. In a manuscript this shows up as the Methods/Task section stating the exact block equations (as `affine_ew_deepdive.tex` §1 does) and the abstract naming the three ways the variant differs from the reference.

### RULE 6 — Prove, don't guess: never assert a mechanism / collapse / ceiling without a measurement; trust the live log over a stale checkpoint.
**Do:** produce the measurement that proves the claim, or explicitly say "I don't know — here's the experiment that would tell us." When a run trains live, trust the live metrics/log over any on-disk `*_latest.pt`. When loading a checkpoint, build the **exact** trained arch and assert **0 missing / 0 unexpected** keys (`load_state_dict(strict=False)` then `assert not r.missing_keys and not r.unexpected_keys` — see `repro_core.load`).
**Do NOT:** call a flat RL plateau a "collapse / dead-end / ceiling"; report an argmax "peak" without its magnitude/spread; read behavior from a `*_latest.pt` being overwritten mid-write; or generalize an attention finding from the change frame alone.
**WHY:** a flat plateau in sparse-reward RL is NOT a ceiling — these runs sit in degenerate local optima for thousands of iters then break out; asserting a mechanism without a measurement is guessing dressed as analysis, and doing it repeatedly burned trust ("where is your proof?"). Attention-map gotchas the critic caught: the change response appears the frame AFTER the change (inspect the cue frame AND the frame after change); an argmax on a near-uniform read is pure noise (print peak vs uniform Σ/4 and spread); the cue read is per-query (inspect the cued query's own row, not the query-mean); run the cue≠change dissociation BOTH ways.

---

## 4. Verbatim examples of the rules in the templates

- **Positive framing (RULE 1):** `paper_affine_ew.tex` abstract states signatures positively and reports divergence as a scientific finding ("its behaviour and attention are largely *invariant to displayed cue validity*"), never as a correction of a prior write-up.
- **Checkpoint as identifier not progress (RULE 2):** `\date{Model checkpoint iteration 6{,}599 (task: 4-stimulus \texttt{vda4}, $50\times50$)}`.
- **Priority/Value in code comments (RULE 3):** `ddstyle.py` — `PRIORITY = "#1f6fb2"  # priority pathway — drives the decision (was "salience")`.
- **Plain "what it IS" + exact block math (RULE 5):** `affine_ew_deepdive.tex` §1 "Element-wise affine self-attention" box: `X' = γ⊙X + β`, `A=softmax(QKᵀ/√140)`, `Z=X+AV`, with the explicit note "no `1+` identity term, `γ→1,β→0` at init".
- **0-missing/0-unexpected load assert (RULE 6):** `repro_core.load` and `dda_core.load` both `assert not r.missing_keys and not r.unexpected_keys`.

---

## 5. research_db notes (when you add research notes)

The manuscripts are the deliverables; the `research_db/` vault is the internal knowledge base. When work surfaces a finding worth keeping, add a page. The `_conventions/` files are canon — agents read them but do NOT edit them.

- **Pick the smallest page type that fits** (`PAGE_TYPES.md`): external paper summary → `paper` (`papers/`, 8-section Lisman-Grace card); single mechanism/term → `concept`; chronological engineering log → `thread`; multi-concept synthesis → `brief`; a finding about OUR work → `note` (`notes/`, the agent write-target); a dated Q&A/run-log → `conversation`. Rule of thumb: *concept > brief > note*, promote upward only when a real audience appears.
- **Frontmatter (`FRONTMATTER.md`), required on every page:** `type` (enum incl. `paper`/`thread`), `status` (`stub|draft|stable|archived`; new agent writes default `draft`), `created: YYYY-MM-DD`, `tags` (namespaced: `topic/attention`, `mechanism/recurrence`). Slug = file basename, `^[a-z0-9][a-z0-9_-]*$`, underscore-native (do NOT dasherize — 1,777 `related:` edges depend on it), equals `id`. `note` provenance fields satisfy the Reproduction dimension cheaply: `source_project`, `source_code`, `source_commit`, `source_run_id`.
- **Layered disclosure (`LAYERED_DISCLOSURE.md`), every substantive page:** open with `## TL;DR` (2–4 sentences, plain, no bare acronyms/run-labels/Greek loss terms), then `## Plain explanation` (defines every term inline or wikilinks it), then the technical L3. Math in the first paragraph of L1 is a write failure.
- **Reproducible findings (`REPRODUCIBLE_FINDINGS.md`), every `note`/`brief`/finding:** after L1+L2, the six sections **in order** — `## Research goal · ## Method` (name code paths/config/commit) `· ## Finding · ## Evidence` (numbers, seeds, run-ids, where plots live) `· ## Reproduction` (script + exact flags + commit + expected runtime/hardware) `· ## Caveats` (real limitations — single-seed, narrow regime, confounds). A finding without Method + Reproduction is "a rumour, and the wiki does not store rumours." If evidence isn't collected yet, use the explicit stub pattern: `status: stub`, `*Hypothesis*` in TL;DR, `*Not yet collected.*` in Evidence.
- **Edges (`EDGES.md`):** cross-links go in frontmatter `see_also` as `{slug, rel, summary?}`. `rel` ∈ the controlled vocab (`applies, grounded-in, informs, depends-on, extends, refines, refutes, corroborates, replicates, ablates, benchmarks, motivates, explains`, …). Hand-authored edges add a specific one-sentence `summary` (not a restatement of the slug). Every `see_also[].slug` must resolve to a real page.
- These conventions **compose**: layered-disclosure check AND reproducible-findings check must both pass before `write_page`.

---

## 6. The no-meta rule governs DELIVERABLES — the handoff docs are the deliberate EXCEPTION

**Explicitly:** the positive-framing / no-meta / no-scaffolding rules of §3 (RULES 1–2 especially) govern **DELIVERABLE manuscripts** — the `.tex` files in `reports/`, `repro/`, `deepdive_*/` that the user will present or submit. They do **not** govern these `AGENT_HANDOFF/` docs.

The `AGENT_HANDOFF/` docs exist precisely **to expose process, state, and provenance to the next agent** — build steps, file paths, exact run commands, gotchas, current state of work, iteration history, "what's built vs not," failed variants. That transparency is their whole job. So:
- In a **manuscript**: never write "reconstruction", never name the source paper as ours, never say "early checkpoint", never expose the pipeline.
- In an **`AGENT_HANDOFF/` doc** (like this one) or a `research_db` `note`: DO expose all of it — that's how the next agent picks up the work.

Do not let the two contexts bleed. A phrase that is mandatory here ("this deep dive was rebuilt from 6 pp to 20 pp after the user called it slop") is forbidden in the `.tex`.

---

## Checklist before a manuscript ships

Format / structure:
- [ ] Correct format chosen: figure-reproduction (§1a, every reference fig, main+supp) vs deep-dive (§1b, four pillars, 20–30 pp) vs `reports/` multi-file standalone.
- [ ] Preamble matches the established one (§2a single-file, or §2b multi-file with natbib + fixed author block).
- [ ] Every figure generated by a script from a cached `.npz` (compute/plot split), not hand-made; `ddstyle` fonts ≥13–16, no clipping/overlap, PRIORITY/VALUE fixed palette.
- [ ] Every caption header bold + names its figure/reference analog; panels walked A/B/C with `n`, fit type, numbers-in-context.
- [ ] Builds clean: `pdflatex ; bibtex ; pdflatex ; pdflatex` (multi-file) or `pdflatex ×2` (single-file); no undefined refs/citations in the `.log`.

HARD RULES:
- [ ] **RULE 1** — no "reconstruction/rebuild/revision", no naming our own source/prior paper, no internal tooling vocab, no hedging findings as corrections; all findings stated positively at evidence strength.
- [ ] **RULE 2** — no "early/iter-X/undertrained"; maturity described by measured behavior; `iter` appears only as a checkpoint identifier if at all.
- [ ] **RULE 3** — PRIORITY/VALUE everywhere in user-facing text + figures; zero "salience"/"top-down"; overloaded terms ("heads", "validity", "stream") disambiguated at first use.
- [ ] **RULE 4** (deep dives) — all four pillars present: attention MAPS, causal BATTERY, 4-param logistic FITS, temporal DECODING.
- [ ] **RULE 5** — abstract/Methods state plainly WHAT the variant IS and every load-bearing choice/default (exact block equations, the three ways it differs from the reference).
- [ ] **RULE 6** — every mechanistic claim backed by a measurement (or explicitly flagged as an untested prediction); no plateau called a collapse; checkpoint loaded with 0 missing / 0 unexpected keys; attention claims checked on the cue frame AND the frame after change, per-query, both dissociation directions.

Provenance hygiene:
- [ ] All build/process/iteration notes live in scaffolding or `AGENT_HANDOFF/` — zero of it leaked into the `.tex`.
- [ ] If a `research_db` note was added: correct type + namespaced frontmatter + underscore slug; `## TL;DR`/`## Plain explanation` opener; six reproducible-findings sections non-empty (or explicit `status: stub` markers); `see_also` edges typed and resolving.
