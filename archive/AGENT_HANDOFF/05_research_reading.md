# 05 — Essential-research reading guide

WHAT THIS IS: a curated, theme-grouped reading list into `research_db/` (the flat-file paper-note wiki, ~261 notes) so the next agent lands with the load-bearing literature already triaged — what to read, in what order, and *why it matters to THIS attention-model program*.

Sibling handoff docs: [01_reference_paper.md](01_reference_paper.md) · [02_model_4stim.md](02_model_4stim.md) · [03_model_9stim.md](03_model_9stim.md) · [04_report_paper_formatting.md](04_report_paper_formatting.md) · **05_research_reading.md** (this file) · [README.md](README.md)

> Note for the next agent: as of this writing `01`–`05` all exist in `AGENT_HANDOFF/`; only `README.md` is not yet written (treat it as a forward reference and create it if missing). `04_report_paper_formatting.md` owns the note-authoring template — this doc points at it (see the last section).

---

## 1. What `research_db` IS and how to query it

`research_db/` is a **flat-file research wiki** rooted at `/Users/jonathanmorgan/AttentionManuscript/research_db/`. It grounds the program's manuscripts and models (the Recurrent ViT — Morgan, Albanna & Herman 2025, arXiv:2502.10955 — and the PRISM / RViT+ lineage). Layout:

```
research_db/
├── README.md            # scope, seed sources, depth tiers
├── SCHEMA.md            # frontmatter spec + body sections + file-naming
├── TAXONOMY.md          # controlled vocab for tags/concepts
├── INDEX.md             # master ledger (papers × depth × seed source)
├── _conventions/        # PAGE_TYPES.md, FRONTMATTER.md, EDGES.md, LAYERED_DISCLOSURE.md, REPRODUCIBLE_FINDINGS.md
├── papers/              # ~261 paper-notes, one .md per work  <-- THE CORPUS
├── concepts/            # 16 atomic mechanism/term pages (e.g. gridcell_rnn.md)
├── threads/             # narrative through-lines / engineering logs
├── tools/               # query.py, audit.py, build_graph.py, ...
└── graph/               # graph.json dump consumed by tools/query.py
```

**Filename convention** (this is your primary index): each paper-note is `papers/{firstauthor}{year}_{keyword}.md`, e.g. `herman_krauzlis2017_sc_change_detection.md`, `assran2023_ijepa.md`, `beck2024_xlstm.md`. The slug (basename) equals the note's `id` and is what every cross-reference (`related:`, `see_also[].slug`, `[[wikilinks]]`) resolves to. Slug regex `^[a-z0-9][a-z0-9_-]*$`; underscores are canonical — **do not dasherize**.

**Note anatomy** (from `_conventions/PAGE_TYPES.md` §`paper` and `FRONTMATTER.md`): YAML frontmatter (`id, title, authors, year, venue, doi, arxiv, url, tags, concepts, related, relevance_to, seed_source, status, depth`) + an eight-section body: `## 1. Abstract`, `## 2. Why this matters for us`, `## 3. Key claims`, `## 4. Methods`, `## 5. Results`, `## 6. Critique / limitations`, `## 7. Connection to our work`, `## 8. Citations to follow`. **`## 2` and `## 7` are the load-bearing sections for you** — they state, per note, exactly how the paper wires into the model program. When skimming, read `## 2` first; read `## 7` when you need the concrete architectural mapping.

`depth` ∈ `metadata|abstract|summary|full`; `status` ∈ `stub|draft|stable|archived` (lifecycle, orthogonal to depth). Most cited exemplars are `depth: full`; some (e.g. `dabney2020_distributional_dopamine`, `stanisor2013_v1_value_attention`) are `depth: abstract` stubs — the frontmatter `related:` graph is still complete on stubs, so they remain navigable.

### How to query it

Prefer the graph tool over blind `grep`; fall back to filename + `grep` for full-text:

```bash
cd /Users/jonathanmorgan/AttentionManuscript/research_db
python tools/query.py search <terms>...        # keyword search over titles/ids/tags/concepts, ranked
python tools/query.py paper <paper-id>          # one card: frontmatter + out/in citations + concepts + threads
python tools/query.py concept <concept-id>      # papers anchored by a concept
python tools/query.py thread <thread-id>        # papers/concepts a thread spans
python tools/query.py work <work-id>            # papers relevant to a work node: recurrent_vit|prism_v1|prism_v2, by depth (rvit_plus is a valid relevance_to tag but NOT a work node — query.py errors on it)
python tools/query.py neighbors <node-id> [--depth N]   # local neighborhood + edge types
python tools/query.py path <id-1> <id-2>        # shortest citation path between two nodes
python tools/query.py stats                     # node/edge counts, top-cited, most-anchored concepts
```

`tools/query.py` reads `graph/graph.json`; if you edit/add notes, regenerate with `python tools/build_graph.py` first. Validate any note you write with `python tools/audit.py` (schema/frontmatter check; the engineering-thread note in memory says "run `python3 research_db/tools/audit.py` after each batch of edits").

Raw filename discovery when you just want the list:
```bash
ls -1 research_db/papers/ | grep -i <topic>     # e.g. grep -i jepa | grep -i wm | grep -i sc_
```

---

## 2. Curated reading list, grouped by theme

Each entry is a `research_db/papers/` filename + a one-to-two-line "why it matters to THIS project". Terminology reminder for this program: the two feedback streams are **PRIORITY** (drives the decision/policy) and **VALUE** (drives valuation) — do NOT call them salience/top-down. (Some older notes still say "salience/top-down"; read those through the PRIORITY/VALUE lens.)

### (a) Target phenomenon — primate visual attention · cued change-detection · value-directed attention · SDT criterion

- **`herman_krauzlis2017_sc_change_detection.md`** — THE precursor. Establishes the exact color-change-detection-with-manual-response paradigm the models replicate; SC activity is behaviorally relevant (hit>miss), precedes response ~200 ms, accounts for 67% of RT variance. Co-author Herman is on the reference paper.
- **`krauzlis2013_sc_attention.md`** — Canonical modern review: SC is a *covert-attention* substrate (not just a saccade generator), partly independent of cortex. Grounds treating the model's attention map as an SC/priority-map homolog.
- **`posner1980_orienting.md`** — The cueing paradigm itself. Every valid/invalid trial and the 25/50/75/100% validity conditions are Posner cues; the validity effect is the headline behavioral signature the models must reproduce.
- **`luo_maunsell2018_criterion_sensitivity.md`** — Localizes the *criterion* vs *sensitivity* SDT components to LPFC vs visual cortex. Motivates the architectural split: PRIORITY/gain → sensitivity; central memory/valuation → criterion.
- **`muller_findlay1987_sensitivity_criterion.md`** — Founding SDT decomposition of cueing into d′ vs β. The methodological contract for reporting the model's cueing effects (don't report RT/accuracy without partitioning sensitivity from criterion).
- **`stanisor2013_v1_value_attention.md`** — Reward value and top-down attention share one selection signal down in V1 (relative value predicts V1 activity). The empirical anchor for the VALUE stream reaching early sensory levels. (stub/abstract depth.)
- **`bisley_goldberg2010_parietal_priority.md`** — The priority-map framework (LIP): a shared map of behavioral importance fed by bottom-up + top-down, read out by both attention and action. The biological template for the model's central self-attention substrate.
- **`sridharan2017_sc_sensitivity_bias.md`** — SC's causal, dissociable roles in sensitivity vs bias; the causal-perturbation companion to Luo & Maunsell for the SDT story.

### (b) JEPA & self-supervised learning

- **`assran2023_ijepa.md`** — I-JEPA: predict *latent* target-block embeddings from context, EMA target encoder as the anti-collapse mechanism. The image-domain template for the program's latent-prediction (discrete-JEPA) loss.
- **`bardes2023_vjepa.md`** — V-JEPA: the video extension; explicitly the contrast architecture cited in 2502.10955 (continuous access to past, no working-memory bottleneck) — i.e. what the recurrent bottleneck models define themselves *against*.
- **`lecun2022_path_to_agi.md`** — LeCun's JEPA position paper; the "predict in representation space, not pixels" commitment the whole lineage inherits.
- **`hafner2023_dreamerv3.md`** — DreamerV3 discrete latents; the program's current loss stack borrows DreamerV3 discrete latents + V-JEPA-style latent prediction (see `project_rvit_plus_findings` memory, 2026-06-01 loss-stack update).
- **`higgins2017_factorized_representations.md`** — β-VAE / factorized latents; background on the disentanglement pressures relevant to whether the encoder "sees" the task variable.
- **`zhuang2021_unsupervised_ventral.md`** — Unsupervised learning that predicts ventral-stream representations; the neuro-grounding argument that SSL objectives recover brain-like features.

### (c) Predictive coding & the Bayesian brain

- **`rao_ballard1999_predictive_coding.md`** — The foundation. Hierarchical generative model, ascending pathway carries *prediction error*; PRISM is by construction a Rao-Ballard model. Read this before any PC-flavored architecture decision.
- **`friston2010_fep_unified_theory.md`** — Free-energy principle; the variational objective under which perception = prediction-error minimization and attention = precision-weighting. The overarching framework for the "single loss for any temporal environment" claim.
- **`feldman_friston2010_attention_free_energy.md`** — Attention *as precision-weighting* specifically; the bridge from FEP to an explicit attention/gain mechanism. Directly relevant to interpreting the model's attention map.
- **`bastos2012_canonical_microcircuits.md`** — Maps Rao-Ballard/Friston onto specific cortical layers + a gamma-feedforward/alpha-beta-feedback frequency signature. The microcircuit template for a two-level PC hierarchy (V1/V2, fast/slow memory).
- **`keller_mrsic_flogel2018_pc_review.md`** — Modern empirical review of predictive processing in cortex; the up-to-date evidence anchor (mouse V1 prediction-error neurons) versus the 1999/2012 theory.
- **`spratling2008_pc_biased_competition.md`** — Derives biased-competition attention from PC *without* explicit error neurons; the important alternative account (don't over-claim the Rao-Ballard mapping is unique).
- **`shipp2024_visual_pc_computational.md`** — Recent computational synthesis of visual PC; useful for situating the program against the current state of PC modeling.

### (d) Attention & working memory

- **`luck_vogel1997_wm_capacity.md`** — The ~4-item, *object-based* visual-WM capacity limit. The capacity constraint the model's fixed-dimensional recurrent memory should respect.
- **`desimone_duncan1995_biased_competition.md`** — Biased-competition theory: attention as competitive resolution among stimuli. The conceptual backbone for the priority map and for coalition/competition framing.
- **`reynolds_heeger2009_normalization.md`** — The normalization model of attention; explains gain vs contrast-gain effects. The mechanistic account of *how* attention multiplicatively modulates responses (why gain, not a spotlight gate).
- **`carrasco2011_visual_attention_25y.md`** — 25-year retrospective; documents the shift from spotlight to graded-gain. Read to avoid the spotlight/winner-take-all framing the program explicitly rejects.
- **`awh2006_attention_wm.md`** — Overlapping mechanisms of attention and WM; grounds the idea that the same substrate maintains and selects.
- **`stokes2015_activity_silent_wm.md`** — Activity-silent WM (synaptic/latent maintenance); relevant to whether the recurrent state must show persistent activity or can hold information "silently."
- **`constantinidis2018_persistent_activity.md`** — The persistent-activity account of WM; the counterpoint to activity-silent, and the classic delay-period-firing target for the model's delay dynamics.

### (e) Dopamine / RL / basal ganglia

- **`hikosaka2006_bg_reward_eyes.md`** — Basal ganglia (caudate→SNr→SC), dopamine-trained, orient the eyes to reward. The neuroanatomical + physiological substrate for an RL/VALUE loop that reweights the priority map; direct/indirect pathway ↔ facilitative/suppressive attention contributions.
- **`dabney2020_distributional_dopamine.md`** — Distributional RL in VTA dopamine neurons (heterogeneous optimism = quantile code). The neuro-grounding for the program's distributional (QR-DQN-style) critic. (stub/abstract depth.)
- **`dabney2018_qr_dqn.md`** — QR-DQN: the quantile-regression distributional critic the models actually use (`critic_kind`, quantile-huber loss). The algorithmic side of the above.
- **`schulman2017_ppo.md`** — PPO; the on-policy actor loss the RL phase is built on. Read alongside the PAC/MPO actor-loss notes in the engineering thread.
- **`glimcher2011_dopamine_rpe.md`** — The canonical reward-prediction-error hypothesis; the scalar-RPE baseline the distributional account refines.
- **`herman_arcizet2020_caudate_sc.md`** — Caudate–SC interaction in attention (Herman co-author); attention-related caudate modulation requires intact SC. Ties the RL/BG loop back to the SC change-detection substrate.
- **`sutton_barto2018_rl_intro.md`** — The RL textbook reference (TD, eligibility traces, actor-critic); the formal frame the whole RL phase instantiates.

### (f) Transformers, recurrence, xLSTM & ViT

- **`vaswani2017_attention.md`** — The Transformer / scaled-dot-product + multi-head attention. The primitive the Recurrent ViT augments with recurrent feedback; also the foil for PRISM's "prediction error replaces softmax attention" claim.
- **`dosovitskiy2020_vit.md`** — ViT: Transformer on image patches. The direct backbone the Recurrent ViT and the 4-patch/9-patch models are built on.
- **`beck2024_xlstm.md`** — xLSTM (sLSTM scalar + mLSTM matrix memory, exponential gating). The contemporary gated-recurrence competitor and a drop-in candidate for the GridCell-RNN SIP stage / slow memory; note the memory index calls the memory transformer an xLSTM analog.
- **`hochreiter_schmidhuber1997_lstm.md`** — The foundational LSTM; the recurrence primitive the program's cells inherit gating from.
- **`mnih2014_recurrent_attention.md`** — Recurrent models of visual attention (hard-attention glimpse policy trained by RL); the direct ancestor of "attention as an RL-controlled action over the image."
- **`kietzmann2019_recurrence_required.md`** — Evidence that recurrence is required to match the ventral stream's temporal dynamics; the neuro-argument for why the models are recurrent at all (vs feedforward ViT).
- **`wang2025_hierarchical_reasoning_model.md`** — Hierarchical/multi-timescale reasoning recurrence; contemporary support for the fast/slow, multi-compartment memory commitment.

### (g) Neural microcircuits / laminar cortex

- **`bastos2015_laminar_macaque.md`** — Laminar macaque recordings confirming the feedforward-gamma / feedback-alpha-beta asymmetry predicted by canonical PC microcircuits. The empirical payoff of `bastos2012`.
- **`larkum2013_apical_basal.md`** — Apical/basal dendritic integration in pyramidal cells; the single-cell mechanism for combining bottom-up drive with top-down prediction — the biological basis for FiLM-affine / multiplicative feedback in the model.
- **`felleman_vanessen1991_hierarchical_cortex.md`** — The canonical hierarchical-cortex wiring diagram (feedforward/feedback laminar rules). The anatomical scaffold for the V1→V4→IT stack.
- **`sherman2022_ctc_loop.md`** — Cortico-thalamo-cortical (transthalamic) loops; motivates thalamic-relay / cross-area routing beyond direct cortico-cortical feedback.
- **`weiler2025_l6_corticocortical.md`** — L6 corticocortical / feedback specifics; fine-grained laminar-origin detail for the feedback pathway the model's PRIORITY/VALUE streams stand in for.
- **`miller_cohen2001_pfc_function.md`** — PFC as the source of top-down control / task rules; the functional account of the central controller the memory transformer approximates.

---

## 3. Lineage: this program is a follow-up to arXiv:2502.10955

**arXiv:2502.10955 = the Recurrent ViT paper (Morgan, Albanna & Herman, 2025).** This is the published anchor of the whole program and the primary seed of the corpus. Its 126 numbered references are the first seed source of `research_db` (see `README.md` "Three sources seed the database"); many notes carry `seed_source: vit_paper_ref_NN`, and the `## 7. Connection to our work` sections repeatedly cite it by reference number (e.g. Posner is `ref_11`, Luck & Vogel `ref_33`, V-JEPA `ref_32`, xLSTM `ref_41`, Müller & Findlay `ref_52`, Herman & Krauzlis is `ref_58`).

What 2502.10955 established, and how the current work extends it:
- **Paradigm:** a Recurrent ViT trained on Posner-cued color-change detection (adapted from `herman_krauzlis2017_sc_change_detection`), producing primate-like attention signatures — cueing/validity effects, attention-map dynamics over recurrent iterations, and FEF/SC-microstimulation-analog perturbation effects (`moore_armstrong2003_fef_microstim`, `cavanaugh_wurtz2004_sc_change_blindness`).
- **Architecture:** a ViT (`dosovitskiy2020_vit`) self-attention encoder (`vaswani2017_attention`) with an LSTM-style recurrent memory bottleneck feeding back into attention — deliberately *the opposite* of V-JEPA's "continuous access to the past" (`bardes2023_vjepa`).
- **The follow-up (this repo's program):** builds novel, small (~1–10M param), recurrent, biologically-grounded, *interpretable* attention models that keep the 2502.10955 interpretability standard (attention-map dynamics, ablations mapped to primate microstimulation, SDT decomposition) while pushing the architecture — multi-compartment memory, PRIORITY/VALUE dual feedback streams, PC/JEPA self-supervision, a distributional RL critic, and an SC/BG/dopamine-analog action loop. Working-model lineage: **HRA (abandoned 2026-05-19) → RViT+ / PRISM v1/v2 → the RViT_plus_* variant family** (see the memory hub files `project_rvit_plus_findings.md`, `project_visual_attention_model.md`, and `project_manuscript_publication_plan.md`).

Practical consequence for you: when a note's `## 2`/`## 7` says "the Recurrent ViT" or cites "2502.10955," it means this paper. `relevance_to:` tags (`recurrent_vit`, `prism_v1`, `prism_v2`, `rvit_plus`) tell you which arm of the lineage a note was filed against; `python tools/query.py work recurrent_vit` (or `prism_v1`/`prism_v2`) enumerates the arm. Note: only those three are graph *work nodes* the `work` subcommand accepts — `rvit_plus` is a `relevance_to` value but has no work node yet, so filter for it with `grep -l "rvit_plus" papers/*.md` (20 notes) rather than `query.py work rvit_plus`.

---

## 4. If you only read 5 notes, read these

1. **`herman_krauzlis2017_sc_change_detection.md`** — the exact task the whole program models, from a co-author of the reference paper.
2. **`rao_ballard1999_predictive_coding.md`** — the predictive-coding foundation the architectures are built on.
3. **`assran2023_ijepa.md`** — the latent-prediction (JEPA) template the current self-supervised loss inherits.
4. **`luo_maunsell2018_criterion_sensitivity.md`** — the SDT criterion/sensitivity split that structures both the behavior analysis and the architecture (VALUE→criterion, PRIORITY→sensitivity).
5. **`hikosaka2006_bg_reward_eyes.md`** — the dopamine/basal-ganglia RL loop that grounds the VALUE stream and the action policy.

(Runner-up if you get a sixth: **`vaswani2017_attention.md`** for the primitive, or **`beck2024_xlstm.md`** for the recurrence competitor.)

---

## How to add a new research note

1. **Format contract:** the note-authoring template + house style live in [04_report_paper_formatting.md](04_report_paper_formatting.md) (create it if absent) and in the canonical conventions under `research_db/_conventions/` — read `PAGE_TYPES.md` (§`paper`), `FRONTMATTER.md` (frontmatter schema + validation rules), `EDGES.md` (typed `see_also` cross-links), `LAYERED_DISCLOSURE.md` (TL;DR opener), and `REPRODUCIBLE_FINDINGS.md` (for notes asserting our own findings). `SCHEMA.md` and `TAXONOMY.md` at the `research_db/` root give the body-section spec and the controlled tag/concept vocabulary.
2. **File + name:** create `research_db/papers/{firstauthor}{year}_{keyword}.md`. Slug = basename, `^[a-z0-9][a-z0-9_-]*$`, underscores not dashes; `id` in frontmatter must equal the slug.
3. **Frontmatter:** required `type: paper`, `status` (new writes default `draft`), `created`, `tags`; plus the paper block `id, title, authors, year, venue, doi, arxiv, url, concepts, related, relevance_to, seed_source, depth`. Every `related:`/`see_also[].slug` must resolve to an existing page (dead links surface in `wiki_stats().dead_links` / `audit.py`).
4. **Body:** the eight sections `## 1. Abstract` … `## 8. Citations to follow`, with a `## TL;DR` opener per layered disclosure. Write `## 2. Why this matters for us` and `## 7. Connection to our work` in the program's own terms (PRIORITY/VALUE, the lineage, the specific model files) — those two sections are what future agents actually read.
5. **Validate + wire the graph:** `python tools/audit.py` (schema check), then `python tools/build_graph.py` to regenerate `graph/graph.json` so `tools/query.py` sees the new node. Add the paper to `INDEX.md` if you maintain the master ledger.
6. **Do not edit** `_conventions/*` or `_adr/` — those are human/curator canon (server write-allowlist excludes them).
