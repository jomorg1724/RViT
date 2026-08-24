# RViT — Recurrent Vision Transformer Attention Research

Unified repository for the RViT / RViT+ research program: recurrent Vision
Transformer architectures with biologically-plausible memory→attention
feedback, trained with RL (PPO) and self-supervised objectives (JEPA,
reconstruction, association) on Posner-style cued change-detection tasks.

This repository consolidates two previously separate workspaces:

- **`RViT_plus_paper_jepa_grid9/`** — the live codebase (Windows workstation)
- **`AttentionManuscript/`** — the Mac-era manuscript workspace, wiki
  (`research_db`), ongoing experiment programs, and the deprecated project
  archive

Consolidated on 2026-08-23. See `wiki/MIGRATION_2026-08-23.md` for the full
path mapping and link-maintenance record, and `docs/provenance/` for the
original reorganization manifest and move logs.

## Repository map

```
RViT/
├── code/                       # Live RViT+ codebase (was RViT_plus_paper_jepa_grid9/)
│   ├── model.py                #   core recurrent-ViT model
│   ├── paper_encoder.py        #   paper architecture encoder
│   ├── conv_frontend.py        #   SE-ResNet conv front-end
│   ├── conv_memory_model.py    #   conv-memory variant
│   ├── vae.py / vae_frontend.py / patch_embed.py / paper_heads.py
│   ├── train_rl.py / ppo.py    #   PPO RL training
│   ├── pretrain_*.py           #   JEPA / recon / trial-recon / association / conv-memory / VAE pretraining
│   ├── probe_*.py              #   memory / MLP / T5 probing
│   ├── envs/                   #   change-detection environments (base, luo2015, tasks)
│   ├── config/                 #   default hyperparameters + loader
│   ├── experiments/            #   code-coupled experiment contracts (FSQ, transformer memory)
│   ├── analysis/               #   analysis pipelines (attention, behavior, psychometrics)
│   ├── scripts/                #   launch / figure / recovery scripts
│   ├── tests/                  #   pytest suite (shapes, contracts, run configs)
│   ├── vda_series/             #   VDA manuscript figure code
│   ├── repro9/ deepdive9/      #   reproduction & deep-dive figure data + code
│   └── runs/                   #   run artifacts (GIT-IGNORED)
├── docs/                       # Design & theory documents
│   ├── ATTENTION_MANUSCRIPT.md #   original manuscript-project overview (task, baselines)
│   ├── MODEL_DESIGN.md
│   ├── RVIT_PLUS_DESIGN.md
│   ├── RVIT_PLUS_NOTES.md
│   ├── THEORY_unified_percept_attention.md
│   └── provenance/             #   reorganization manifest + move/verify logs
├── wiki/                       # Research knowledge base (was research_db/)
│   ├── INDEX.md                #   bibliographic ledger (~265 paper cards)
│   ├── TAXONOMY.md             #   controlled vocabulary for tags/concepts
│   ├── SCHEMA.md HANDOFF.md README.md
│   ├── mocs/                   #   maps of content (attention program, RViT+, PRISM, …)
│   ├── papers/ concepts/ threads/ notes/ briefs/
│   ├── registry/               #   canonical run index
│   └── graph/                  #   generated concept-graph snapshots
├── experiments/                # Experiment designs, by research program
│   ├── vda-set-size-and-memory/
│   ├── luo-maunsell-reproductions/
│   └── memory-stability-and-percepts/
├── reports/                    # Reports & manuscripts, by research program
│   ├── vda-set-size-and-memory/
│   ├── luo-maunsell-reproductions/
│   ├── memory-stability-and-percepts/
│   └── research_state/         #   dated research-state briefings (referenced by the wiki)
├── analysis/
│   └── luo2015/                #   cross-program Luo–Maunsell analysis core
├── archive/                    # Deprecated Mac-era projects (kept for lineage)
│   ├── Prism/ PrismV2/         #   predictive-coding change-detection architectures
│   ├── Critique/ Rebuild/ Reconstruction/   # normative-paper audit/repair lineage
│   ├── RViT_plus*/             #   full RViT+ version history (v2 … paper_jepa_grid9)
│   ├── HRA/ agents/ VDA4_memory_decay/ analysis_t29/
│   ├── v6_VizdoomArena/ v10_VizdoomArena/
│   ├── reports/                #   archived manuscript trees (crosstalk, loop-routing, thesis, …)
│   └── archive_manifest.txt    #   original archival record (2026-08-20)
├── runs/                       # Lightweight run artifacts by program (GIT-IGNORED)
└── rescues/                    # RunPod rescue artifacts (GIT-IGNORED)
```

## What is tracked in git — and what is not

Tracked: all source code, tests, configs, experiment designs, reports,
manuscripts, the wiki, and small figure data.

**Not tracked** (see `.gitignore`): model weights/checkpoints (`*.pt`,
`*.pth`, `*.ckpt`, …), datasets and archives (`*.zip`, `*.tar`, …), run
output directories (`runs/`, `rescues/`), virtual environments, and caches.
Lightweight run artifacts (logs/configs/plots ≤ 2 MB) were copied locally
under `runs/` and `rescues/` for reference; the full-fidelity heavy data
remains at the original storage locations documented in
`docs/provenance/MANIFEST.md`.

## Quick start

```bash
cd code
pip install torch  # plus pandas/numpy/scipy/matplotlib per archive/requirements.txt
python -m pytest tests/ -k shape        # smoke-test the model shapes
```

Canonical training invocations and architecture notes are in
`code/README.md`; task definition and behavioral baselines are in
`docs/ATTENTION_MANUSCRIPT.md`.

## Research programs

| Program | Focus | Designs | Reports |
|---|---|---|---|
| VDA set size & memory | VDA4/9/16 set-size scaling, attention validity | `experiments/vda-set-size-and-memory/` | `reports/vda-set-size-and-memory/` |
| Luo–Maunsell reproductions | `luo2015` grid attention reproductions, RunPod deployments | `experiments/luo-maunsell-reproductions/` | `reports/luo-maunsell-reproductions/` |
| Memory stability & percepts | transformer/JEPA memory, memory noise, FSQ | `experiments/memory-stability-and-percepts/` | `reports/memory-stability-and-percepts/` |
