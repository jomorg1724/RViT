# Attention Manuscript — Predictive-Coding Architectures for Cued Change Detection

Two convolutional-recurrent neural architectures and the Posner-style cued
change-detection environment they train on. Both architectures use a single
auxiliary objective family — variational free energy / predictive-coding error
— and avoid any softmax-over-locations "spotlight" primitive. They differ in
size, hierarchy depth, and critic structure.

**Status (May 2026):** PRISM v1 (in `Prism/`) is the best-performing model on
the change-detection task in this repo. PRISM v2 (in `PrismV2/`) is a heavier
follow-up that explored hierarchical PC + slow/fast memory + multi-head
saliency + an action-value critic; despite multiple architectural iterations,
v2 has not yet matched v1.

## Layout

```
AttentionManuscript/
├── README.md             this file
├── requirements.txt      pandas, numpy, scipy, matplotlib (PyTorch installed separately)
├── Prism/                PRISM v1 — small (~250 K params), single-level, scalar critic
│   ├── README.md
│   ├── docs/             THESIS.md, PRISM_V2_PROPOSAL.md, PROJECT_PLAN.md, PRISM_V2/Q_CRITIC.md
│   ├── env.py            ChangeDetectionEnv — the Posner-cuing task
│   ├── *.py              stem, film, decoder, memory, readout, losses, model, ppo, train
│   ├── config/           default hyperparameters
│   ├── checkpoints/      saved weights
│   └── tests/            shape, identity, smoke
└── PrismV2/              PRISM v2 — heavier (~1.48 M params), V1+V2 hierarchy,
    ├── README.md         dual-timescale memory, multi-head saliency,
    ├── env.py            action-conditional distributional Q critic
    ├── *.py              stem, film, decoder, memory, readout, losses, model, ppo, train
    ├── config/           default hyperparameters
    ├── checkpoints/      saved weights
    ├── analysis/         gradient_audit.py — per-module gradient-norm diagnostic
    └── tests/            shape, identity, gradient routing
```

## The task

`ChangeDetectionEnv` (defined identically in `Prism/env.py` and
`PrismV2/env.py`) is a Posner-style cued change-detection paradigm. Each
episode shows four oriented Gabor patches at the corners of a 50×50 RGB
image; a cue at $t = 0$ probabilistically indicates which patch will undergo
an orientation change. The change occurs at a uniformly-sampled
$t_{\text{change}} \in [11, 25]$. The agent must press at the moment of the
change (immediately after, within the response window) and not before. The
env terminates on press or at $t_{\text{max}}$. Reward is sparse: positive
for a press at the right moment, zero otherwise.

Behavioral baselines (from internal env audits):

- **Oracle** policy (knows $t_{\text{change}}$ from env state): reward ≈ 2.98
- **Never-press** policy: reward ≈ 1.47
- **Always-press-at-t=0**: reward ≈ 0

So the env is solvable; the gap between never-press and oracle is the
learnable signal.

## Quick start

Install Python deps (PyTorch is installed separately for your platform; the
`requirements.txt` covers the rest):

```bash
pip install -r requirements.txt
# + install torch from https://pytorch.org/get-started/locally/ for your platform
```

Train PRISM v1 (the recommended model):

```bash
cd Prism
python3 tests/test_shapes.py        # ~5 s sanity check
python3 train.py                    # full training run
```

Train PRISM v2:

```bash
cd PrismV2
python3 tests/test_shapes.py
python3 train.py
```

Both `train.py` scripts auto-select CUDA → MPS → CPU and write checkpoints
to `<model>/checkpoints/`.

## Reading order for documentation

1. **`Prism/README.md`** — what v1 is, how to run it, what's in each file.
2. **`Prism/docs/THESIS.md`** — full v1 manuscript draft: introduction,
   methods, math, references. The architecture spec for v1 lives in §3.
3. **`Prism/docs/PRISM_V2_PROPOSAL.md`** — design doc for v2 with full math
   derivations of hierarchical PC, slow/fast memory, multi-head saliency,
   cross-level Rao-Ballard coupling.
4. **`PrismV2/README.md`** — what v2 is, what changed from v1, current
   training status, how to interpret the new diagnostic columns
   (`Zstd`, `dQ`).
5. **`Prism/docs/PRISM_V2/Q_CRITIC.md`** — derivation of the action-
   conditional distributional Q critic added during v2 development;
   gradient-routing argument for why the value loss does not contaminate
   the actor.
6. **`Prism/docs/PROJECT_PLAN.md`** — 99-task experimental roadmap covering
   training stability, ablations, baselines, neuroscientific cross-
   validation, and writeup.
