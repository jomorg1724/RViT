---
id: recurrent_vit
type: moc
status: stable
created: 2026-07-11
tags:
  - topic/attention
  - topic/recurrent-vision
  - mechanism/recurrence
scope: "Morgan–Albanna–Herman 2025 empirical Recurrent ViT baseline"
summary: "This hub covers the empirical Morgan–Albanna–Herman Recurrent ViT paper, A recurrent vision transformer shows signatures of primate visual attention (arXiv:2502.10955v1). It is the baseline extended by RViT+, not an earlier version of the separate normative VDA paper."
see_also:
  - slug: attention_program
    rel: informs
    summary: "Places the 2025 empirical baseline within the broader attention program without merging lineages."
  - slug: attention_program_lineage_boundaries
    rel: defines
    summary: "Documents why arXiv:2502.10955 and the 2026 normative VDA paper are distinct."
  - slug: rvit_plus
    rel: predecessor
    summary: "The 2025 empirical model is the baseline that the RViT+ experimental line extends."
  - slug: posner1980_orienting
    rel: grounded-in
    summary: "Supplies the spatial-cueing paradigm underlying the model's change-detection task."
  - slug: carrasco2011_visual_attention_25y
    rel: grounded-in
    summary: "Supplies behavioral and mechanistic attention distinctions used to interpret model signatures."
  - slug: feedback_transformer
    rel: informs
    summary: "Generalizes the single-source recurrent feedback variants discussed in the empirical paper."
---

# Recurrent ViT

## TL;DR

The canonical object here is the 2025 empirical paper by Morgan, Albanna, and Herman, not the 2026 normative VDA model. It establishes a recurrent neural-model baseline for cued orientation-change detection and is the predecessor of the RViT+ empirical work.

## Plain explanation

The paper trains a recurrent vision transformer on a seven-step, 50-by-50-image cued change-detection task. It reports behavioral, temporal, decoding, signal-detection, and causal-attention signatures intended to be compared with primate visual attention. The paper's authority is the external arXiv record and bundled supplement; no local PDF named for arXiv:2502.10955 was identified in the audited workspace.

## Canonical source

- Morgan, Albanna, and Herman (2025), *A recurrent vision transformer shows signatures of primate visual attention*, arXiv:2502.10955v1: <https://arxiv.org/abs/2502.10955>

## Reading order

1. The arXiv paper and supplement for claims about the published empirical baseline.
2. [[posner1980_orienting]] for the cueing paradigm.
3. [[carrasco2011_visual_attention_25y]] for the sensitivity, criterion, and attentional-gain framing.
4. [[feedback_transformer]] for the later architectural generalization of recurrent feedback.
5. [[rvit_plus]] for current empirical extensions and the upgraded manuscript.

## Boundary with later work

RViT+ changes architecture, task variants, training support, and analysis scope. Its results therefore extend or test the empirical baseline; they are not evidence that the 2025 model itself was rerun under every later condition. The normative paper in `Critique/source/main.pdf` is a stationary ideal-observer model and is neither a correction nor a successor edition of arXiv:2502.10955.
