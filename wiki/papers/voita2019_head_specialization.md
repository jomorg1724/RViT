---
id: voita2019_head_specialization
title: "Analyzing multi-head self-attention: specialized heads do the heavy lifting, the rest can be pruned"
authors:
  - "Voita, Elena"
  - "Talbot, David"
  - "Moiseev, Fedor"
  - "Sennrich, Rico"
  - "Titov, Ivan"
year: 2019
venue: "ACL"
doi: "10.18653/v1/P19-1580"
arxiv: "1905.09418"
url: "https://arxiv.org/abs/1905.09418"
tags:
  - transformers
  - deep-learning
  - self-attention
  - ablation-study
concepts:
  - multi-head-attention
  - scaled-dot-product-attention
  - self-attention-over-tokens
  - feedback-transformer
related:
  - vaswani2017_attention
  - dosovitskiy2020_vit
  - khan2022_transformers_vision_survey
  - hassanin2024_attention_dl_survey
  - tay2022_efficient_transformers_survey
relevance_to:
  - prism_v2
  - recurrent_vit
seed_source:
  - prism_v2_proposal
status: full
depth: full
last_updated: "2026-05-15"
---

# Analyzing multi-head self-attention: specialized heads do the heavy lifting, the rest can be pruned

## 1. Abstract

Voita et al. analyze the individual contributions of attention heads in the encoder self-attention of a standard Transformer trained for neural machine translation. They show that only a small subset of heads is important for translation quality; the rest can be removed without measurable loss in BLEU. The important heads play consistent, linguistically interpretable roles, falling into three identifiable categories: positional heads (attending to immediate neighbors), syntactic heads (tracking specific dependency relations like subject–verb or verb–object), and a "rare words" head (attending to the lowest-frequency tokens in the sentence). Pruning is performed via a differentiable relaxation of the $L_0$ penalty using Hard-Concrete stochastic gates. Specialized heads are the ones that survive pruning longest; redundant heads are removed first. On WMT English–Russian, 38 of 48 encoder heads can be pruned with a BLEU drop of only 0.15. The paper provides the first systematic empirical evidence that the parallel multi-head structure in Transformers is grossly over-parameterized and that the learned heads decompose into functionally distinct, individually identifiable units.

## 2. Why this matters for us

This is the load-bearing reference for PRISM v2's central architectural claim that partitioning a feature decoder into $K$ heads, each predicting a disjoint subset of channels, will produce *functionally specialized* heads (`PRISM_V2_PROPOSAL.md` §3.6 "Recipe 1"). Voita et al. establish empirically — in the most studied multi-head attention setting — that specialization is real, robust, and interpretable, and that most of the per-head capacity is redundant. PRISM v2's per-head saliency maps inherit both the promise (specialization can be expected) and the warning (most heads will be pruneable). The paper also bears on the Recurrent ViT: the multi-head saliency interpretation in 2502.10955 §6 should be read against this paper's evidence that not all heads are doing equivalent work.

## 3. Key claims

1. A small minority of encoder self-attention heads is responsible for the majority of the translation quality; most heads are individually redundant and can be removed without measurable BLEU loss.
2. The important heads fall into three linguistically interpretable categories: **positional** heads (assigning ≥ 90% of their maximum attention weight to a fixed relative offset, typically −1 or +1), **syntactic** heads (tracking dependency relations such as subject→verb, verb→object, adjective→noun), and a **rare-words** head (in the first encoder layer, attending to the least-frequent tokens in the sentence > 50% of the time).
3. A two-stage importance signal — confidence (how concentrated the head's attention distribution is) plus layer-wise relevance propagation (LRP, back-propagated relevance from output to encoder neurons) — identifies the same set of "important" heads, which coincide with the linguistically interpretable ones.
4. Hard-Concrete stochastic gates with a differentiable $L_0$ relaxation make per-head pruning trainable jointly with the translation objective; the surviving heads after aggressive pruning are precisely the specialized ones (positional, syntactic, rare-words).
5. Encoder self-attention is the most prunable of the three attention mechanisms; encoder–decoder cross-attention is the most critical and tolerates the least pruning.
6. The functional roles of heads are stable across corpora (WMT En-De, WMT En-Ru, OpenSubtitles En-Ru) and across training runs: the same three categories appear with similar distributions in every setting.
7. Specialization emerges from end-to-end training on the translation objective alone — no auxiliary loss explicitly encourages positional, syntactic, or rare-word behavior. The functional partition is a property of what the unconstrained learner finds, not of what was supervised.

## 4. Methods

**Base model.** A standard 6-layer Transformer encoder–decoder (Vaswani et al. 2017) with 8 attention heads per layer, $d_\text{model}=512$, $d_k=d_v=64$. Trained on WMT 2014 English–German, WMT 2017 English–Russian, and OpenSubtitles-2018 English–Russian.

**Head importance signals.** Two complementary scores are computed on a development set. (i) *Confidence* — the average maximum attention weight assigned by the head over all query positions: $\text{conf}(h) = \mathbb{E}_i\big[\max_j \alpha_{ij}^{(h)}\big]$. A high-confidence head consistently focuses on a single key for each query. (ii) *LRP relevance* — Layer-wise Relevance Propagation back-propagates relevance from a chosen output logit down through the network to the encoder neurons, stopping there; the head's relevance is the summed contribution of its outputs to the prediction.

**Head specialization analysis.** A head is labeled *positional* if it places at least 90% of its maximum attention on a fixed relative offset (−1 or +1). A head is labeled *syntactic* if its attention distribution aligns with a specific dependency-parser-extracted relation (subject→verb, verb→object, adjective→noun, etc.) above a baseline frequency; the alignment is measured against an external dependency parser run on the source sentences. A head is labeled *rare-words* if it attends to the two least-frequent tokens of the source sentence more than 50% of the time. The thresholds are chosen post-hoc by inspection of head behavior and are deliberately conservative — a head only earns a label if its behavior is unambiguous.

**Pruning via Hard-Concrete gates.** Each head $h$ is multiplied by a scalar gate $g_h \in [0,1]$ drawn from a Hard-Concrete distribution (Louizos, Welling & Kingma 2018), a continuous relaxation of a Bernoulli that admits exact zeros and ones with non-zero probability while remaining differentiable in between. The training objective is

$$
\mathcal{L} = \mathcal{L}_\text{xent} + \lambda \sum_h P(g_h > 0)
$$

where the second term is the (differentiable) expected number of active heads — a relaxed $L_0$ penalty. $\lambda$ controls the pruning strength. After training, gates near zero indicate prunable heads; gates near one indicate retained heads. The procedure is applied separately to encoder self-attention, decoder self-attention, and encoder–decoder (cross) attention.

**Evaluation.** BLEU on standard test sets. Counts of surviving heads of each functional category at varying $\lambda$. The pruning sweep produces a Pareto curve trading number of retained heads against BLEU; the curve is reported separately for encoder self-attention, decoder self-attention, and cross-attention.

## 5. Results

**Pruning, WMT English–Russian.** With aggressive Hard-Concrete pruning, 38 of 48 encoder self-attention heads (≈79%) can be removed with a BLEU drop of only 0.15. With moderate pruning, 17 surviving heads still cover all three specialization categories.

**Pruning, OpenSubtitles English–Russian.** Only 4 of 48 encoder heads are needed to come within 0.25 BLEU of the full model (≈92% pruning), reflecting the simpler corpus.

**Pruning across attention types.** Encoder self-attention is most prunable; decoder self-attention is intermediate; encoder–decoder (cross) attention is least prunable — cross-attention heads are critical for translation quality and tolerate the smallest reduction.

**Specialization counts (WMT En-Ru, full model, 48 encoder heads).** A consistent fraction of heads are positional (most strongly +1 / −1 offsets, concentrated in the lower layers), a smaller fraction are syntactic (concentrated in middle layers, with subject→verb, verb→object, and noun-modifier relations the most reliable), and a single rare-words head appears in the first encoder layer. The positional heads are by far the most numerous of the labeled categories; the syntactic and rare-words categories together account for a smaller but non-negligible minority. The remaining heads — the bulk of the 48 — do not admit any of the three labels and are the first to be removed by the gating procedure.

**Survival under pruning.** The functional categories survive pruning in a stable order: positional heads and the rare-words head are retained first; syntactic heads are retained when pruning is less aggressive. Heads with no identifiable function are pruned first. Among the 10 surviving encoder heads in the 38-pruned En-Ru model, every one is linguistically interpretable. This ordering is the empirical core of the paper's title claim — "specialized heads do the heavy lifting, the rest can be pruned" — and it is consistent across the three corpora studied.

**Confidence vs LRP agreement.** The two importance measures agree substantially on which heads matter; their joint application gives more reliable rankings than either alone. The linguistically interpretable heads are simultaneously the high-confidence and the high-LRP heads. The agreement is non-trivial because confidence is a property of the attention distribution alone (it can be computed without any gradient information), whereas LRP propagates relevance from the output logits and therefore measures contribution to the task. The convergence of the two signals strengthens the case that "specialized" is not merely a property of how peaked the attention map is but reflects a genuine functional role.

## 6. Critique / limitations

The analysis is restricted to *encoder* self-attention in a *machine translation* model. The strong claim that "most heads can be pruned" is supported there but does not automatically transfer to other tasks, modalities, or to the decoder side, where the paper itself shows cross-attention is much less prunable.

The categorical labels (positional / syntactic / rare-words) are imposed by the authors with explicit thresholds (e.g., 90% attention on a fixed offset). A head that distributes its attention more diffusely but plays a similar functional role would be missed. The taxonomy is conservative, not exhaustive.

The LRP-based importance signal inherits all of LRP's known issues (gradient × input style attributions can be unstable across input perturbations). Confidence and LRP agreeing does not rule out the possibility that both are tracking a related artifact.

Subsequent work — most directly Michel, Levy & Neubig (2019, "Are sixteen heads really better than one?") — replicated the headline pruning finding but cautioned that the *trained* heads are interdependent: pruning iteratively is not the same as proving any single head was useless. Bian et al. (2021) and others have argued that "head specialization" may partly be an artifact of training dynamics (lottery-ticket-like) rather than an inevitable property of multi-head attention. The paper does not engage with these objections (it predates them).

Finally, the pruning rates are remarkable but the gating mechanism induces sparsity at train time; the same heads are *not* prunable post-hoc from a vanilla-trained model without retraining. The result is therefore about the existence of low-head solutions, not about the rigidity of any particular pretrained checkpoint.

## 7. Connection to our work

The connection to PRISM v2 is direct and was anticipated in the proposal. `PRISM_V2_PROPOSAL.md` §3.6 ("Recipe 1: multi-head saliency") partitions the feature decoder into $K$ heads, each responsible for predicting a disjoint subset of feature channels and each producing its own per-location prediction-error map. The architectural motivation — that the heads will *specialize* on different aspects of the scene (e.g., one head on edges, another on textures, another on objects) and that the per-head error maps will therefore be diverse rather than redundant — is the PRISM-side instantiation of Voita et al.'s finding. The paper supplies two key pieces of evidence:

1. *Specialization is real and discoverable.* In the most-studied multi-head architecture, heads spontaneously develop distinct, interpretable functions without being explicitly trained to. This is the existence proof PRISM v2 needs.

2. *Most heads are redundant under aggressive sparsification.* This is a warning. If PRISM v2's $K=8$ heads behave like Voita et al.'s 8 heads per layer, expect 2–4 to do most of the work and the rest to contribute marginally. The proposal's evaluation plan should include head-ablation experiments along these lines.

The connection to the user's larger architectural program (`threads/the_user_architectural_program.md`) is more subtle but also load-bearing. The Feedback Transformer (§1 of the thread) admits an arbitrary number of recurrent feedback sources, each entering through its own Q/K/V projections that are then *broadcast* into the sensory Q/K. The combinatorial blow-up of feedback sources is only tractable if the resulting heads/sources specialize — i.e., if not every head ends up doing the same thing. Voita et al.'s evidence that 8 standard heads spontaneously partition into 3–4 functional types is encouraging: it suggests that the Feedback Transformer's many-source structure is not doomed to degenerate redundancy. It is also a warning: the *number* of effective sources may be much smaller than the architectural count.

The connection to the Recurrent ViT (2502.10955) is more diagnostic. The published paper reports attention-map visualizations across recurrent passes and observes nontrivial dynamics. Voita et al.'s methodology (confidence + LRP + linguistic-role labeling) is the precise toolkit needed to ask whether the Recurrent ViT's heads specialize, whether their roles are stable across recurrent passes, and whether the recurrent feedback recruits or suppresses particular head functions. This is a natural follow-up analysis to the eye-tracking and Food-101 experiments described in the user's program thread.

Bitter-lesson framing: Voita et al. did not *engineer* heads to be positional or syntactic; they trained the model end-to-end on translation and observed the specialization emerge. The PRISM-v2 partition over feature channels is more constrained (each head is *assigned* a channel subset), but the per-head function within its channel subset is left to learning. The paper's lesson is that this should be enough for specialization to emerge — provided the loss provides distinct enough signals per head, which is the architectural question PRISM v2 is testing.

## 8. Citations to follow

- `michel2019_sixteen_heads` — Michel, Levy & Neubig (2019), "Are sixteen heads really better than one?" — independent replication and methodological critique of the head-pruning finding; not yet in seed.
- `louizos2018_l0_regularization` — Louizos, Welling & Kingma (2018), Hard-Concrete distribution and differentiable $L_0$; the gating mechanism Voita et al. adopt. Not yet in seed; candidate for addition.
- `bach2015_lrp` — Bach et al. (2015), original Layer-wise Relevance Propagation paper. Not yet in seed; would clarify the LRP-based importance signal.
- `clark2019_what_does_bert_look_at` — Clark, Khandelwal, Levy & Manning (2019), "What does BERT look at?" — parallel analysis of BERT attention heads with similar specialization findings; not yet in seed.
- `vaswani2017_attention` — the architecture under study; already in the database.
