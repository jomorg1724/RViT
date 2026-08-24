---
id: zou2023_reading_attention
title: "Human attention during goal-directed reading comprehension relies on task optimization"
authors:
  - "Zou, Jiajie"
  - "Zhang, Yuran"
  - "Li, Jialu"
  - "Tian, Xing"
  - "Ding, Nai"
year: 2023
venue: "eLife"
doi: "10.7554/eLife.87197"
arxiv: ""
url: "https://elifesciences.org/articles/87197"
tags:
  - visual-attention
  - human-neuroimaging
  - transformers
  - deep-learning
concepts:
  - self-attention-over-tokens
  - scaled-dot-product-attention
  - multi-head-attention
  - attentional-template
  - top-down-feedback
related:
  - vaswani2017_attention
  - mehrani_tsotsos2023_attention_grouping
  - yamamoto2024_human_like_vit_attention
  - liu2024_human_attention_explainable_ai
  - cartella2024_human_attention_modeling
relevance_to:
  - recurrent_vit
seed_source:
  - vit_paper_ref_29
status: full
depth: full
last_updated: "2026-05-16"
---

# Human attention during goal-directed reading comprehension relies on task optimization

## 1. Abstract

The computational principles underlying attention allocation in complex goal-directed tasks remain elusive. Goal-directed reading, that is, reading a passage to answer a question in mind, is a common real-world task that strongly engages attention. Here, we investigate what computational models can explain attention distribution in this complex task. We show that the reading time on each word is predicted by the attention weights in transformer-based deep neural networks (DNNs) optimized to perform the same reading task. Eye tracking further reveals that readers separately attend to basic text features and question-relevant information during first-pass reading and rereading, respectively. Similarly, text features and question relevance separately modulate attention weights in shallow and deep DNN layers. Furthermore, when readers scan a passage without a question in mind, their reading time is predicted by DNNs optimized for a word prediction task. Therefore, we offer a computational account of how task optimization modulates attention distribution during real-world reading.

## 2. Why this matters for us

This paper is the cleanest published evidence that *self-attention weights in a task-optimized transformer predict human attention behavior on the same task* — in this case word-by-word reading times in goal-directed comprehension. It is the language-domain twin of yamamoto2024_human_like_vit_attention's vision result: when you optimize a transformer end-to-end on a cognitively meaningful task, the head-level attention maps look like human attention dynamics. For the user's program this is the load-bearing empirical claim: training a Recurrent ViT on change detection, or training the iterative-VAE on video reconstruction, is exactly the "task optimization" route Zou et al. validate. It also dissociates *first-pass* (bottom-up, feature-driven) from *rereading* (top-down, task-driven) attention and shows the same dissociation in shallow-vs-deep transformer layers, anchoring the hierarchical-feedback prescription of `the_user_architectural_program` §3.

## 3. Key claims

1. Word-by-word reading time in goal-directed reading is predicted by attention weights in transformer DNNs (BERT, ALBERT, RoBERTa) fine-tuned on the same reading-comprehension task, with cross-validated correlations on the order of 0.55–0.60.
2. Transformer attention weights predict reading times substantially better than an RNN-based attentive reader (Stanford Attentive Reader, SAR), better than orthographic or semantic word-matching baselines, and better than pre-trained but unoptimized transformers — task optimization is what closes the gap.
3. Eye tracking dissociates a *first-pass* reading regime (gaze duration is dominated by basic text features: word length, frequency, surprisal) from a *rereading* regime (fixation behavior is dominated by question-relevance).
4. The same dissociation appears across transformer depth: shallow layers' attention is sensitive to text features; deep layers' attention is sensitive to question relevance only after task fine-tuning.
5. When readers scan a passage without a question in mind ("free reading"), word reading times are still predicted by transformer attention — but now from a transformer optimized for next-word prediction rather than for question answering. The model that matches the human task is the model whose attention matches the human.
6. For challenging "global" questions (theme, title, purpose) that cannot be answered by word-matching strategies, transformer attention still tracks human reading time, whereas word-matching baselines fail — establishing that the result is not an artifact of surface lexical overlap.

## 4. Methods

**Behavioral paradigm.** Participants read English-language passages from the RACE reading-comprehension dataset and answered multiple-choice questions. Eye tracking recorded gaze position throughout reading. Across four experiments, N ≈ 162 readers (L2 and native English speakers) read 800 question-passage pairs, with passages of 117–456 words. Questions were categorized as *local* (factual or local-inference, 520 items) or *global* (theme, title, author intent, 280 items). Four task conditions were contrasted: blocked questions (question shown before passage), mixed questions, native-reader baseline, and general/free reading with no question in mind.

**Computational models.** The authors compared:
- *Transformer DNNs:* BERT, ALBERT, RoBERTa (each 12 layers × 12 heads = 144 attention weights per word per model), evaluated both as pre-trained (out-of-the-box) and as fine-tuned on RACE.
- *RNN baseline:* Stanford Attentive Reader (Chen et al. 2016), an attention-augmented recurrent reading-comprehension model.
- *Surface baselines:* orthographic word matching (string overlap between question and passage words) and semantic word matching (embedding similarity).
- *Free-reading model:* a transformer optimized for next-word prediction (language-model objective), used in the no-question condition.

For each model, per-word attention weights toward each passage word were extracted. These were aggregated across heads (and across question tokens for QA models) to yield a single attention-to-word scalar per passage word.

**Statistical link.** Linear regression with five-fold cross-validation related model attention weights to human gaze measures (gaze duration, total reading time, regression count). Control regressors for word length, frequency, and position were included to isolate task-driven attention effects. Layer-wise and head-wise analyses tested where in the model's depth the question-relevance signal lived.

## 5. Results

**Behavior.** Reading rates were 457 ± 142 wpm (blocked questions, Exp 1), 298 ± 123 wpm (mixed, Exp 2), 506 ± 155 wpm (native, Exp 3), and 225 ± 40 wpm (free reading, Exp 4). Human question-answering accuracy reached 77.94%; fine-tuned transformers reached ≈73%; pre-trained transformers without fine-tuning achieved only 37.08% — task optimization was necessary for the model to perform the human task.

**Model–behavior fit.** Cross-validated correlations between model attention and human reading time were approximately:
- orthographic / semantic word matching: r ≈ 0.20
- SAR (RNN-based): r ≈ 0.10
- pre-trained transformers: r ≈ 0.50
- fine-tuned transformers: r ≈ 0.55–0.60

The gap from pre-trained to fine-tuned was largest on local questions, where task fine-tuning sharpens which passage words are question-relevant.

**Hierarchical decomposition.** Shallow transformer layers' attention correlated with text-feature predictors (word length, frequency, surprisal). Deep layers of *fine-tuned* models correlated with question relevance; deep layers of *pre-trained* models did not. The human first-pass / rereading split mirrored this depth-wise split: early gaze on a word reflected text-feature attention; rereading reflected task-driven attention.

**Free reading.** With no question in mind, human reading time was no longer well predicted by question-answering transformers, but was well predicted by a transformer optimized for *next-word prediction*. The mapping from model objective to predictable attention pattern is one-to-one with the human task.

**Global vs local questions.** For local questions, all transformer models outperformed word-matching baselines. For global questions — where word matching is fundamentally inadequate because the answer is not literally in the passage — transformer attention remained predictive of human gaze, while baselines collapsed.

## 6. Critique / limitations

The paper's correlations are at the population level: the regression links model attention to *average* reading time across participants, not to individual-difference structure. Subject-level fits (which would test whether the *same* model predicts the *same* reader's idiosyncratic gaze pattern) are not reported in detail. This limits the strength of the "task-optimized model is a model of the reader" claim.

The dissociation between shallow-and-text-features vs deep-and-question-relevance is suggestive but not causally established. Without ablation or intervention on specific layers, the conclusion is correlational: nothing rules out that the depth pattern is an artifact of how the pre-training objective shapes information flow through a feedforward transformer stack. A more rigorous test would lesion deep layers and check that question-relevance regression weights collapse first.

The models tested are all *feedforward* transformers. The paper's first-pass-vs-rereading dissociation is naturally interpreted as a recurrent dynamic in the human reader (initial pass → re-fixation contingent on accumulated comprehension), but the models lack any recurrence. The comparison is therefore between a *static* model output and a *temporally extended* human process; the fact that the model still predicts gaze is consistent with the model attention being a marginal over the human's full reading trajectory rather than a true match of dynamics. This is the gap the user's Recurrent ViT closes in the vision domain.

The RNN baseline (Stanford Attentive Reader) is a 2016-era architecture and is not a strong representative of modern attention-augmented RNNs. The transformer-beats-RNN comparison is fair as a snapshot of the literature available to the authors, but it should not be read as a general claim about recurrent architectures — only as a claim about a specific weak RNN baseline.

Finally, the work is monolingual (English), uses only multiple-choice comprehension, and reads at near-newspaper-level difficulty. Whether the same task-optimization principle generalizes to longer documents, to open-ended question answering, or to non-Indo-European languages is open.

## 7. Connection to our work

This is the *reading-attention* anchor in a four-paper cluster that together validates the user's program of training models on cognitive tasks and matching the resulting neural / behavioral signatures of attention. The cluster is:

- `mehrani_tsotsos2023_attention_grouping` — the negative half: a *feedforward* ViT's self-attention performs similarity grouping, not attention, in the human-vision sense.
- `yamamoto2024_human_like_vit_attention` — the positive half in vision: a ViT trained on a sensible task (DINO self-supervision) develops attention maps that match human gaze behavior in visual scenes.
- `zou2023_reading_attention` (this paper) — the positive half in language: a transformer trained on reading comprehension develops attention weights that match human reading time word by word.
- `liu2024_human_attention_explainable_ai` — the bridge to applied XAI: human gaze can be used to supervise or evaluate model attention, treating the two as commensurable signals.
- `cartella2024_human_attention_modeling` — the survey: how the field is currently organizing the literature on computational models of human attention.

The user's published Recurrent ViT (2502.10955) sits at the intersection. The user trains a ViT-plus-LSTM on a cognitive task (change detection) and reports that, after training, the model's attention dynamics qualitatively recapitulate primate-attention phenomena — focusing, defocusing, reactivating across recurrent passes. Zou et al. supply the analogous result in the reading domain: train a transformer on the human task and the attention behavior matches the human. This is the *task-optimization-yields-human-attention* principle that motivates the program; without it, training a model on change detection and inspecting its attention is just curve fitting.

Three specific connections to the user's program are sharpened by this paper:

- **Recurrent ViT §6.7 (multiplicative feedback variant).** Zou et al. show that the same transformer stack contains *two* attentional regimes in different layers — text-features in shallow, task-relevance in deep. The user's multiplicative-feedback variant is the architectural prescription for making the deep-layer (top-down, task-driven) regime modulate the shallow-layer (bottom-up, feature-driven) regime by closing the loop. Zou et al. show that the two regimes coexist in a feedforward stack; the user's recurrent feedback is the move that lets them interact dynamically rather than only at the end of a single forward pass.
- **`the_user_architectural_program` §3 (multi-compartmental, hierarchical memory).** Zou et al.'s shallow-feature / deep-task split is precisely the V1-features / IT-task split the user's three-layer reference design targets. The human first-pass-vs-rereading dissociation is the behavioral signature of running shallow features first, then re-engaging with deep task-knowledge — exactly what bidirectional ascending / descending projections between layered GridCell RNNs are designed to produce.
- **`the_user_architectural_program` §5 (competition-emergent predictive coding).** A coalition-competition account predicts that task-relevant content wins attention only after the deep-layer (task-knowledge) hub has had time to push its predictions back into the shallow-layer competition. The first-pass-vs-rereading temporal dissociation in Zou et al. is the behavioral fingerprint of exactly that delayed-feedback dynamic. The free-reading condition — where attention follows a *language-modeling* objective in the absence of a comprehension goal — also fits: when no task-hub asserts a goal, the residual attention pattern reflects whichever objective the underlying optimization most recently committed to.

Reading-attention and visual-search-attention are complementary task domains for testing the same principle. Visual search (the natural home of saliency, biased competition, and the Recurrent ViT's change-detection benchmark) is a spatial, parallel-grouping task; reading is a sequential, syntactically-structured task. That the same architectural family (a task-optimized transformer) explains human attention in both regimes — once it is fine-tuned on the right objective — is the strongest empirical case the user has for the generality of the program.

## 8. Citations to follow

- `chen2016_stanford_attentive_reader` — the RNN-attention baseline; relevant to any claim that transformer attention specifically (not attention in general) matches human reading.
- `devlin2019_bert`, `lan2020_albert`, `liu2019_roberta` — the three transformer encoders the paper uses; foundational references for transformer-as-cognitive-model arguments.
- `hahn_keller2023_reading_task_effects` — modeling task effects in human reading with neural-network attention; the closest predecessor to this paper's main result.
- `goldstein2022_shared_computational_principles` — transformer language models share computational principles with the human brain; the canonical task-optimization-yields-brain-like-representations result in language.
- `schrimpf2021_neural_architecture_language` — neural architecture of language: integrative modeling converges on predictive processing; the brain-score-style framing for language models.
- `kell2018_task_optimized_auditory_cortex` — task-optimized DNNs as models of auditory cortex; the canonical task-optimization result in audition.
- `yamins2014_performance_optimized_models` — performance-optimized hierarchical models predict neural responses in ventral stream; the foundational task-optimization paper for vision and the upstream reference for the user's "train on a task and inspect the representations" program.
- `rayner1998_eye_movements_reading` — the canonical review on eye movements in reading; the methodological foundation for any model-vs-gaze comparison in this literature.
- `reichle2003_ez_reader` — the E-Z Reader model of eye-movement control in reading; the cognitive-model alternative to a transformer account that any task-optimization claim must be measured against.
