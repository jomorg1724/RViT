# RViT+ Design Notes (working file)

Synthesis pad for designing the next visual-attention model.
Inputs: research_db threads + concepts + PRISM/HRA failure record + targeted papers.
Output: `RVIT_PLUS_DESIGN.md` once notes converge.

## Sections will fill in as I read

- §1 Core Video AE design (from threads, as I infer it)
- §2 Architectural primitives I'd keep
- §3 Architectural primitives I'd modify or drop
- §4 New architectural choices (and the papers that justify them)
- §5 Interpretability protocol — microstim analog as the central commitment
- §6 Training curriculum (recon → RL bridge)
- §7 Failure modes from HRA, prevented by design
- §8 Open questions

---

## Thread-level synthesis (Phase 1)

**Video AE design philosophy (inferred from `the_user_architectural_program.md`):**

- A stack of GridCell RNN cells (ConvGRU-flavored recurrent cells with per-cell spatial state) coupled via the Feedback Transformer at each level. Up to 12 feedback sources mentioned in §1 for the Video VAE case.
- Multi-compartmental memory: 3-layer reference design with descending (V1→V2→V4) driving convs that reduce spatial resolution + expand channel count, and ascending (V4→V1) transpose-conv feedback.
- Iterative encoder-decoder protocol: $n_{FR}$ forward passes on same input followed by $n_{BR}$ backward decoder passes. Reconstruction loss is exponentially-weighted across the $n_{BR}$ outputs. KL on the initial latent $\tilde H_0$ provides VAE structure.
- Matrix-normal latents: $\tilde H_0 \in \mathbb{R}^{n_\text{patch} \times d_\text{guide}}$ with row-whitening enforced via off-diagonal penalty.
- Empirical: works on UCF101 reconstruction. Food-101 classification works at training but overfits aggressively.

**What I learned from each thread:**

1. **`feedback_substrates`** — multi-source feedback is well-motivated. Real cortex has TWO parallel substrates (direct L6 CC + transthalamic) that are NOT redundant; they carry different information with different gating characteristics. The Feedback Transformer is the unified AI analog. Multiplicative integration at the cellular AND-gate level is the biophysical norm (Larkum 2013, Jordan 2023).

2. **`coupled_rnn_architectures`** — the dual-timescale (Mujika 2017 / Tallec-Ollivier 2018) and controller-world-model (Schmidhuber 2015, Ha-Schmidhuber 2018, Dreamer 2020) lineages are well-established. **V-JEPA 2023 is a major lesson**: latent-space prediction beats pixel reconstruction in the modern world-modeling literature. HRM 2025 demonstrates that brain-inspired coupled RNNs at 27M params can match much larger transformers on reasoning — strong evidence that the small-recurrent direction is viable.

3. **`predictive_coding_as_canonical_computation`** — PC framework is empirically well-supported (mouse V1, macaque laminar) but **scaling PC to deep learning has failed so far** (Wen 2018, Pinchetti 2024). This is a warning: don't bet the architecture on PC being the magic ingredient. PC as an *auxiliary* objective is fine; PC as the *only* objective is not yet validated at scale.

**Key insight that reframes the whole HRA failure:**

The HRA's attention collapsed to uniform partly because the Posner task *can be solved by global pooling* (PRISM v1 demonstrates this). The FT sat at a flat minimum with no differentiating gradient. **Video reconstruction can't be solved by global pooling** — patch-level spatial structure is required to reconstruct local pixels. So the recon task itself is the attention-shaping mechanism. This is why the Video AE works and HRA didn't, and it's the strongest argument for "recon first, RL second."

**Architectural commitments I now think are non-negotiable:**

1. Multi-layer recurrent cell stack — biologically grounded, empirically validated (Video AE)
2. Feedback Transformer as the cross-layer integration primitive — uniquely captures multi-source multiplicative feedback (no other AI primitive does this)
3. Per-layer spatial state preserved (not aggressively pooled) — interpretability + biological accuracy
4. Pixel-reconstruction objective for pretraining — densely-gradient-shaping for attention

**Architectural commitments I'd revisit:**

1. **Full $n_{FR}\to n_{BR}$ iterative VAE.** May be overkill. V-JEPA's latent prediction may be a better fit. Or stick with iterative VAE for the recon phase and switch to JEPA-style for representation use.
2. **Pixel reconstruction.** Modern wisdom (LeCun 2022 JEPA) says latent-space prediction is computationally cheaper and produces better representations. Worth testing.
3. **The 3-layer architecture's aggressive spatial compression (12→6→3).** HRA failed partly because of this. Could the layers preserve resolution and only differ in channel/feature dimension? Cortical hierarchy DOES preserve retinotopy at all levels through V4 — only IT becomes spatially invariant.
4. **Update gates at σ(-1).** PRISM v1's default is too sticky for stacks. HRA's σ(0) fix is the right direction.

---

## Concept-level synthesis (Phase 2 concept reading)

**FT open question 4 is the most important finding for me:** HRA's FT spatial-attention collapsed to uniform because the Posner task can be solved without spatial focus (PRISM v1 demonstrates this). The FT sat at a flat minimum of the policy loss. The recommended fix is **attention supervision** (KL against a cue-derived prior during cue/change windows). **Video reconstruction cannot be solved by global pooling** — the recon task itself supplies the gradient pressure to develop spatial structure. This is the *primary* argument for recon-first.

**GridCell RNN open question 3:** SIP+FT can collapse to ConvGRU-like behavior if FT learns only local attention. To prevent this, the recon task is the gradient-shaping mechanism — long-range dependencies in video force non-local attention.

**Multi-compartmental memory thinking:** PRISM v2 has 2 compartments (12×12, 6×6); HRA tried 3 with aggressive compression (12→6→3) and it killed signal. Cortical reality: V1/V2/V4 preserve retinotopy; IT does not. So a "spatial-preserving for the first two levels, abstract at the third" is the bio-faithful + computationally-tractable middle ground.

**Distributional RL is required for biological plausibility AND for escaping the dominant-action bootstrapping trap.** Action-conditional QR-DQN with V = Σ sg[π]·Q is the right pattern.

**PRISM v2 architectural detail check:** v2 had V1 stem (64ch @ 12×12) + V2 stem (128ch @ 6×6), top-down FiLM V2→V1, per-level error-gated GRU, multi-head saliency via partitioned feature decoders, inner variational-inference loops, decision readout. Despite all this, v2 didn't match v1. **Lesson: complexity without a strong objective just adds places for things to go wrong.** Recon objective gives every piece a job; sparse-RL didn't.
