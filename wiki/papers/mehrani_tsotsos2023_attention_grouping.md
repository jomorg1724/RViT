---
id: mehrani_tsotsos2023_attention_grouping
title: "Self-attention in vision transformers performs perceptual grouping, not attention"
authors:
  - "Mehrani, Paria"
  - "Tsotsos, John K."
year: 2023
venue: "arXiv:2303.01542"
doi: ""
arxiv: "2303.01542"
url: "https://arxiv.org/abs/2303.01542"
tags:
  - vision-transformers
  - visual-attention
  - theoretical-essay
  - biased-competition
concepts:
  - self-attention-over-tokens
  - scaled-dot-product-attention
  - figure-ground-segmentation
  - top-down-feedback
  - attention-as-prediction-error
related:
  - vaswani2017_attention
  - dosovitskiy2020_vit
  - desimone_duncan1995_biased_competition
  - koch_ullman1984_winner_takes_all
  - hassanin2024_attention_dl_survey
  - tsotsos1988_complexity_vision
  - rao_ballard1999_predictive_coding
relevance_to:
  - recurrent_vit
seed_source:
  - vit_paper_ref_30
status: full
depth: full
last_updated: "2026-05-16"
---

# Self-attention in vision transformers performs perceptual grouping, not attention

## 1. Abstract

Recently, a considerable number of studies in computer vision involves deep neural architectures called vision transformers. Visual processing in these models incorporates computational models that are claimed to implement attention mechanisms. Despite an increasing body of work that attempts to understand the role of attention mechanisms in vision transformers, their effect is largely unknown. Here, we asked if the attention mechanisms in vision transformers exhibit similar effects as those known in human visual attention. To answer this question, we revisited the attention formulation in these models and found that despite the name, computationally, these models perform a special class of relaxation labeling with similarity grouping effects. Additionally, whereas modern experimental findings reveal that human visual attention involves both feed-forward and feedback mechanisms, the purely feed-forward architecture of vision transformers suggests that attention in these models will not have the same effects as those known in humans. To quantify these observations, we evaluated grouping performance in a family of vision transformers. Our results suggest that self-attention modules group figures in the stimuli based on similarity in visual features such as color. Also, in a singleton detection experiment as an instance of saliency detection, we studied if these models exhibit similar effects as those of feed-forward visual salience mechanisms utilized in human visual attention. We found that generally, the transformer-based attention modules assign more salience either to distractors or the ground. Together, our study suggests that the attention mechanisms in vision transformers perform similarity grouping and not attention.

## 2. Why this matters for us

The user's published Recurrent ViT (2502.10955) and the entire Feedback-Transformer program rest on the claim that softmax self-attention is a *competition-grouping* operation over patch tokens, and that the human-attention-like phenomena observed in the Recurrent ViT (attention maps focusing, defocusing, and reactivating across recurrent passes) come from *closing the feedback loop*, not from the feedforward attention layer alone. Mehrani & Tsotsos provide the cleanest published statement of the negative half of this claim: a single feedforward self-attention layer over patch tokens implements similarity-based perceptual grouping (a form of relaxation labeling), not attention in the human-vision sense. Their conclusion directly motivates the architectural commitment in `the_user_architectural_program` §1: to get genuine attention dynamics, you must augment self-attention with recurrent feedback from competing memory hubs.

## 3. Key claims

1. The scaled-dot-product self-attention formulation in vision transformers, despite its name, computationally implements *relaxation labeling* with a similarity-grouping objective rather than attention in the cognitive-neuroscience sense.
2. Human visual attention is not purely feedforward: it involves descending feedback from higher cortical areas and from working memory. A feedforward stack of self-attention layers therefore cannot, in principle, reproduce the feedback-dependent phenomena of human attention.
3. Empirically, when ViT self-attention maps are evaluated on figure-grouping stimuli, the maps group patches together by similarity in low-level visual features (especially color), behaving like a perceptual-grouping operator over the patch grid.
4. In a feature-singleton detection task (a canonical test of bottom-up saliency in human attention), ViT self-attention assigns higher salience to distractors or to the background than to the singleton target — the opposite of human saliency-driven attention behavior.
5. The mislabeling of self-attention as "attention" obscures these mechanistic distinctions and inflates claims that ViTs implement biologically-plausible attention. The mechanism is better described as similarity grouping; calling it attention is at best a metaphor.

## 4. Methods

The paper proceeds in two parts: a theoretical reanalysis of the self-attention computation and an empirical evaluation on attention-relevant stimuli.

**Theoretical reanalysis.** Starting from the standard scaled-dot-product attention $A = \mathrm{softmax}(QK^\top / \sqrt{d_k}) V$, the authors recast the attention-weight matrix as a relaxation-labeling update over the set of patch tokens. Relaxation labeling (Rosenfeld, Hummel & Zucker 1976) is a parallel iterative procedure in which each site holds a probability distribution over labels and updates that distribution based on the *compatibility* between its current labeling and the labelings of neighboring sites. The authors show that the softmax-normalized inner product of query and key vectors plays the role of the compatibility coefficient, the value matrix supplies the labels being propagated, and a single attention layer is one relaxation step. Iterating multiple attention layers therefore implements a relaxation-labeling cascade that drives patches with similar Q/K projections toward shared V representations — i.e., similarity grouping.

**Empirical setup.** A family of pretrained vision transformers is evaluated on two stimulus families. The first is a figure-grouping stimulus set in which simple geometric shapes (squares, circles, etc.) are placed against a contrasting background; the question is whether the model's attention map groups the patches belonging to the figure together. The second is a singleton-search paradigm: an array of identical distractor items contains one feature singleton (e.g., a uniquely colored item), and the question is whether the model's attention map highlights the singleton (as human bottom-up saliency would). Self-attention maps from various heads and layers are extracted and compared against ground-truth figure masks and singleton locations.

The architectures evaluated span the standard ViT family — patch-tokenizing transformers with multi-layer multi-head self-attention pretrained on ImageNet-scale data — and include attention-rollout / attention-aggregation visualizations of the form pioneered by Abnar & Zuidema (2020).

## 5. Results

On the figure-grouping stimuli, the attention maps reliably group patches by similarity in low-level visual features. When the figure is defined by a distinctive color, the attention map highlights the figure patches; when the figure is defined by shape but matched in color to the background, the grouping fails. This is the predicted behavior of a similarity-grouping operator over patch tokens, not of an attention mechanism that selects the behaviorally relevant figure independent of low-level features.

On the singleton-detection task, the self-attention maps fail the test of feedforward saliency: across the tested ViT family, attention is assigned predominantly to distractors or to the background rather than to the singleton target. Quantitatively, the singleton receives lower mean attention than the distractor set, an inversion of the human pattern in which the singleton is the most salient location in the display.

The combination of these two results is the paper's empirical case: ViT self-attention groups by similarity (positive result on the grouping task) but does not implement saliency-driven attentional selection (negative result on the singleton task). The two are dissociable, and ViTs implement only the former.

## 6. Critique / limitations

The paper does not formally prove the equivalence between scaled-dot-product attention and relaxation labeling; it argues by analogy and by demonstration. The mapping is suggestive but leaves several details — the role of the residual connection, the role of layer normalization, the role of multi-head concatenation — outside the scope of the analogy. A more rigorous treatment would derive the relaxation-labeling objective as the variational fixed point of stacked attention layers, which the paper does not attempt.

The empirical evaluation uses static, artificial stimuli (geometric shapes and singleton displays) and asks whether the *raw* attention maps from a feedforward ViT match human attention behavior. This is a stacked test: it conflates (a) whether self-attention is grouping rather than attention, with (b) whether a feedforward pretrained ViT, with no recurrent feedback and no task-specific objective, should be expected to do attention. Mehrani & Tsotsos read the negative result as evidence for (a), but a critic could read it equally well as evidence for (b) — i.e., that the right architecture is a *recurrent* ViT with feedback, in which the same self-attention primitive does implement attention once embedded in the right computational loop. The Recurrent ViT (2502.10955) is exactly this critic's position.

The paper does not engage in depth with the literature on transformer interpretability (e.g., the rollout-attention work of Abnar & Zuidema, the attribution work of Chefer et al.) which has shown that attention maps are an unreliable surrogate for the network's actual decision attribution. If attention maps mostly highlight grouping rather than the network's decision-relevant tokens, the paper's negative result on singleton detection may say less about self-attention as a mechanism than about the limitations of attention-map visualization as a probe.

Finally, the paper's positive proposal — that the right model of attention is one that closes the loop with feedback — is asserted rather than constructed. Tsotsos has the most developed positive proposal in the field (Selective Tuning; STAR), and the paper would be stronger if it traced an explicit bridge from the relaxation-labeling grouping operation to the selective-tuning architecture as the missing feedback piece.

## 7. Connection to our work

This paper is the single most useful published anchor for the central architectural claim of the user's program: that *softmax self-attention over patch tokens is a competition-grouping primitive, not an attention mechanism*. The user's framing in `the_user_architectural_program` §5 — predictive coding as a strategy emerging from inter-coalition competition for representational bandwidth — treats the self-attention map as the substrate on which coalitions compete, with the softmax enforcing a soft winner-take-all over patches. Mehrani & Tsotsos arrive at the same architectural conclusion from a different angle: relaxation labeling is, under the hood, an iterative competitive-grouping procedure, and a single attention layer is one such step.

The connection sharpens three commitments in the user's published and unpublished work:

- **Recurrent ViT (arXiv:2502.10955) §6.7.** The published paper distinguishes three variants of memory integration — tokens, additive, multiplicative. Mehrani & Tsotsos's argument predicts that the *tokens* variant (which leaves the feedforward attention layer unmodified and simply prepends memory tokens) should behave most like pure similarity grouping, while the *multiplicative* variant (which Hadamard-broadcasts memory into the Q and K projections before softmax) is precisely the move that converts grouping into attention by injecting top-down feedback into the competition. The empirical superiority of multiplicative feedback in the published Recurrent ViT results is exactly what Mehrani & Tsotsos's framework predicts.
- **Feedback Transformer (`the_user_architectural_program` §1).** The element-wise broadcasting of $C_i$-derived $Q_{C_i}, K_{C_i}$ into the bottom-up $Q_S, K_S$ prior to softmax is the architectural realization of "close the feedback loop so the grouping operator becomes attention." Mehrani & Tsotsos's relaxation-labeling reading clarifies what is being modulated: not the values being grouped, but the compatibility coefficients themselves. Top-down feedback edits the compatibility between sites, which is what selective tuning does at the level of receptive-field competition.
- **Competition-emergent predictive coding (`the_user_architectural_program` §5).** The user's account is that prediction errors are signals of strategic surprise about competing coalitions. Mehrani & Tsotsos's reading makes the competition concrete: the soft winner-take-all in the attention softmax is the competition; the hubs that successfully predict each other's contributions to Q and K win attention bandwidth. This grounds the user's coalition-competition story in a published mechanistic interpretation of self-attention rather than leaving it at the level of metaphor.

The link to Tsotsos's broader program is also load-bearing. Selective Tuning (Tsotsos et al. 1995) explicitly models attention as a *competitive grouping* operation in a multi-layer feedforward-plus-feedback network: a feedforward pass identifies candidate coalitions, then a top-down "winner-take-all" gating pass suppresses non-selected units to sharpen the winner. The Recurrent ViT's iterative attention dynamics — focusing, defocusing, reactivating across recurrent passes (`the_user_architectural_program` §6, Food-101 classifier experiment) — are the transformer analog of selective tuning's iterative WTA refinement. Mehrani & Tsotsos's paper is the bridge: it identifies softmax self-attention as the *first half* of selective tuning (the feedforward grouping pass) and implicitly licenses the addition of feedback (the second half) as the architectural prescription.

For PRISM v1 the connection is weaker but still real. PRISM v1 replaces softmax attention with a prediction-error map (Rao-Ballard residual; see `papers/rao_ballard1999_predictive_coding.md`). Under Mehrani & Tsotsos's reading, PRISM v1 trades a similarity-grouping primitive for a prediction-error primitive — two different mechanisms by which one could in principle drive selective processing of behaviorally relevant content. The user's open empirical question (which of these wins on change-detection benchmarks) is meaningful precisely because the two mechanisms are *not* the same operation.

## 8. Citations to follow

- `tsotsos1995_selective_tuning` — the canonical positive model of attention as feedforward grouping plus top-down WTA gating; the architectural complement to this paper's negative result.
- `rosenfeld_hummel_zucker1976_relaxation_labeling` — the formal grounding of the relaxation-labeling reinterpretation; foundational reference for the theoretical argument.
- `abnar_zuidema2020_attention_rollout` — the methodological tool for aggregating attention across ViT layers; relevant to the empirical methodology and to the caveat that raw attention maps are unreliable probes.
- `chefer2021_transformer_attribution` — alternative attribution methods for transformers; relevant to whether the singleton-detection negative result reflects the mechanism or the probe.
- `caron2021_dino` — DINO and self-supervised ViTs; produces qualitatively different attention maps from supervised ViTs and is a likely test case for the family of models evaluated.
- `desimone_duncan1995_biased_competition` — already in seed; biased-competition is the cognitive-neuroscience analog of the user's coalition-competition framing and the natural bridge between Mehrani & Tsotsos's grouping interpretation and the broader attention literature.
- `koch_ullman1984_winner_takes_all` — already in seed; the WTA primitive underlying selective-tuning and the softmax competition.
- `bruce_tsotsos2009_saliency_information` — Tsotsos lab's bottom-up saliency model (AIM); the alternative against which the singleton-detection failures of ViTs are being compared.
