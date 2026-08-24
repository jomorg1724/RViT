---
id: bahdanau2014_neural_translation
title: "Neural Machine Translation by Jointly Learning to Align and Translate"
authors:
  - "Bahdanau, Dzmitry"
  - "Cho, Kyunghyun"
  - "Bengio, Yoshua"
year: 2014
venue: "ICLR 2015"
doi: ""
arxiv: "1409.0473"
url: "https://arxiv.org/abs/1409.0473"
tags:
  - deep-learning
  - recurrent-networks
  - self-attention
concepts:
  - additive-attention
  - bahdanau-attention
  - cross-attention
  - top-down-feedback
  - feedback-transformer
related:
  - vaswani2017_attention
  - hochreiter_schmidhuber1997_lstm
  - mnih2014_recurrent_attention
  - locatello2020_slot_attention
  - cho2014_gru
relevance_to:
  - recurrent_vit
seed_source:
  - manual
status: full
depth: full
last_updated: "2026-05-16"
---

# Neural Machine Translation by Jointly Learning to Align and Translate

## 1. Abstract

Neural machine translation is a recently proposed approach to machine translation. Unlike the traditional statistical machine translation, the neural machine translation aims at building a single neural network that can be jointly tuned to maximize the translation performance. The models proposed recently for neural machine translation often belong to a family of encoder–decoders and consists of an encoder that encodes a source sentence into a fixed-length vector from which a decoder generates a translation. In this paper, we conjecture that the use of a fixed-length vector is a bottleneck in improving the performance of this basic encoder–decoder architecture, and propose to extend this by allowing a model to automatically (soft-)search for parts of a source sentence that are relevant to predicting a target word, without having to form these parts as a hard segment explicitly. With this new approach, we achieve a translation performance comparable to the existing state-of-the-art phrase-based system on the task of English-to-French translation. Furthermore, qualitative analysis reveals that the (soft-)alignments found by the model agree well with our intuition.

## 2. Why this matters for us

Bahdanau, Cho & Bengio 2014 is the **original attention paper** — the first work to formalize attention as a *learnable, differentiable, content-based, soft-selection* mechanism inside a neural network. The additive-attention scoring function introduced here is the conceptual ancestor of all subsequent attention mechanisms, including Vaswani et al.'s scaled dot-product attention, the ViT's self-attention over image patches, the Recurrent ViT's softmax attention augmented with recurrent feedback, and the Feedback Transformer's per-state Q/K/V structure. For the user's architectural program, this paper is the load-bearing citation for the move from "fixed-length bottleneck context vector" to "soft-selection over a set of source representations" — the same move that the Recurrent ViT makes within a single forward pass and that the Feedback Transformer generalizes to many parallel feedback sources.

## 3. Key claims

1. The fixed-length context vector in Cho et al. (2014)–style encoder–decoder translation is a performance bottleneck, particularly degrading on long sentences.
2. Replacing the fixed vector with a *soft alignment* — a learned, content-dependent weighted sum over all encoder hidden states — removes the bottleneck while preserving end-to-end differentiability.
3. The alignment weights are computed by a feedforward "alignment model" $a(s_{i-1}, h_j)$ jointly trained with the rest of the network; no separate alignment supervision is needed.
4. A bidirectional RNN encoder produces per-source-position annotations $h_j = [\overrightarrow{h_j}; \overleftarrow{h_j}]$ that the alignment model scores against the decoder's previous hidden state.
5. The resulting model (RNNsearch) matches the state-of-the-art conventional phrase-based statistical MT system (Moses) on English-to-French WMT14 when restricted to the same vocabulary, and substantially outperforms the fixed-vector baseline (RNNencdec).
6. Qualitative inspection of the alignment weights shows linguistically meaningful soft alignments that recover known word-order phenomena (e.g., adjective–noun inversion between English and French) without ever being told what an alignment is.

## 4. Methods

**Architecture (RNNsearch).** The encoder is a bidirectional RNN with GRU cells (Cho et al. 2014). For a source sentence $(x_1, \ldots, x_{T_x})$ it produces forward annotations $\overrightarrow{h_j}$ and backward annotations $\overleftarrow{h_j}$, concatenated as $h_j = [\overrightarrow{h_j}; \overleftarrow{h_j}] \in \mathbb{R}^{2n}$. The decoder is a GRU producing target words $y_i$ conditioned on a *context vector* $c_i$ that is recomputed at every decoding step.

**The attention mechanism.** Instead of a single fixed $c$, the decoder uses

$$
c_i = \sum_{j=1}^{T_x} \alpha_{ij}\, h_j, \qquad \alpha_{ij} = \frac{\exp(e_{ij})}{\sum_{k=1}^{T_x} \exp(e_{ik})}
$$

where the alignment energies are

$$
e_{ij} = a(s_{i-1}, h_j) = v_a^\top \tanh(W_a s_{i-1} + U_a h_j).
$$

This is the **additive (or "Bahdanau") attention** scoring function: a single-layer MLP with $\tanh$ nonlinearity applied to the sum of a projected query $W_a s_{i-1}$ and a projected key $U_a h_j$, followed by a linear projection to a scalar. The softmax over source positions $j$ yields a probability distribution interpretable as a soft alignment.

**Decoding update.** The decoder hidden state evolves as $s_i = f(s_{i-1}, y_{i-1}, c_i)$ where $f$ is a GRU and $c_i$ is the attention output. The output distribution is $p(y_i \mid y_{<i}, x) = g(y_{i-1}, s_i, c_i)$ with $g$ a maxout layer followed by softmax over the target vocabulary.

**Training.** Standard maximum-likelihood with SGD + Adadelta on bilingual sentence pairs. No alignment supervision; the attention weights emerge entirely from the translation loss. Vocabulary is the 30,000 most frequent words in each language; out-of-vocabulary tokens map to `[UNK]`.

**Data.** WMT '14 English–French. The same vocabulary-restricted setup as Cho et al. (2014) and Sutskever et al. (2014), enabling direct comparison.

## 5. Results

**BLEU on WMT'14 English–French (newstest2014).**

| Model | All sentences | No-UNK sentences |
|---|---|---|
| RNNencdec-30 (Cho 2014, 30k vocab, length-30 train) | 13.93 | 24.19 |
| RNNsearch-30 (this paper, 30k vocab, length-30 train) | 16.46 | 28.45 |
| RNNencdec-50 (length-50 train) | 17.82 | 26.71 |
| RNNsearch-50 (length-50 train) | 26.75 | 34.16 |
| RNNsearch-50* (longer training) | 28.45 | 36.15 |
| Moses (state-of-the-art phrase-based SMT) | 33.30 | 35.63 |

The headline result is that **RNNsearch-50 with longer training (36.15 BLEU on no-UNK sentences) exceeds Moses (35.63)** — the first time an end-to-end neural model is competitive with classical SMT on a major benchmark when the vocabulary mismatch is controlled.

**Length robustness.** The fixed-vector RNNencdec degrades sharply on sentences longer than its training length cutoff. RNNsearch maintains performance out to sentence lengths well beyond 50 words. The fixed-length bottleneck is the load-bearing failure mode the paper identifies.

**Qualitative alignments.** The visualized $\alpha_{ij}$ matrices show diagonal-dominant alignments with linguistically sensible local rearrangements — e.g., for "European Economic Area" → "zone économique européenne," the attention mass on "European" shifts to the French "européenne" three positions later, recovering the adjective-postposition rule without supervision.

## 6. Critique / limitations

The paper's central architectural commitment — **content-based soft alignment computed by a small MLP** — is what made it foundational, but the specific instantiation has several limitations that subsequent work has addressed.

**Quadratic compute in source length.** The alignment model is invoked $T_x$ times at every decoder step, yielding $O(T_x T_y)$ alignment evaluations per sentence. For modest sentence lengths this is fine; for document-level translation or vision (where "tokens" number in the hundreds or thousands) the cost becomes prohibitive. Vaswani et al. (2017) replaced the additive MLP with a dot product $q^\top k$, which is faster to compute on GPUs but otherwise plays the same structural role.

**MLP scoring vs. inner product.** The additive form $v_a^\top \tanh(W_a s + U_a h)$ has more parameters than necessary; the scaled dot-product $\frac{q^\top k}{\sqrt{d_k}}$ is empirically comparable on most tasks and parallelizes better. The 1409.0473 paper is silent on this — additive attention was simply the first form that worked.

**Single-head.** Each decoder step produces a single distribution $\alpha_{i,:}$. Vaswani et al.'s multi-head generalization, which lets the model attend along multiple distinct subspaces simultaneously, is a strict extension; the 2014 paper has no analog.

**Cross-attention only.** RNNsearch uses attention only at the *encoder–decoder boundary* (cross-attention from decoder to encoder). Self-attention within either stream is not considered. The 2017 Transformer's central move — replacing the recurrent encoder and decoder with stacked self-attention — is exactly what RNNsearch *does not* do.

**Recurrent backbone.** Both encoder and decoder are RNNs (GRUs). Long-range dependencies still depend on the GRU's hidden-state propagation; attention helps locate the *right* hidden state but doesn't make the encoder itself easier to train across long contexts. The "all-attention" Transformer of 2017 made this critique explicit and acted on it.

**Biological plausibility.** The alignment model is a feedforward MLP applied to every encoder–decoder pair — no obvious cortical analog. The mechanism is best understood as engineering motivated by the fixed-bottleneck observation, not as a biologically inspired primitive.

## 7. Connection to our work

This paper is the conceptual headwater of every attention mechanism downstream of it in the user's program. The connections are layered.

**The Recurrent ViT and softmax attention.** The Recurrent ViT (2502.10955) is structurally a sequence of forward passes over the *same* image, with self-attention computing soft weights over image patches at every pass. The softmax-over-positions normalization, the content-based query–key matching, and the differentiable weighted-sum readout are exactly the three primitives Bahdanau et al. introduced. The 2014 paper applied them across source positions for translation; the Recurrent ViT applies them across spatial patches for vision. The structural mapping is direct: $s_{i-1} \to$ a per-patch query computed from $H^{(t-1)}$; $h_j \to$ a per-patch key/value computed from the patch embedding; $\alpha_{ij} \to$ the patch-by-patch attention map visualized in 2502.10955 §5–6.

**The Feedback Transformer and Q/K/V structure.** The Feedback Transformer (`concepts/feedback_transformer.md`) generalizes the Q/K/V decomposition to admit *multiple feedback sources* — bottom-up sensory $S$, top-down memory $C^{(\text{deep})}$, lateral parallel hub $C^{(\text{parallel})}$, etc. — each contributing its own per-source projection that combines with sensory Q/K via Hadamard product before softmax. Bahdanau et al. introduced the Q/K split implicitly: $s_{i-1}$ is the query (the "thing doing the looking"), $h_j$ is both the key (the "thing being looked at") and the value (the "thing being read out"). Vaswani et al. (2017) split key and value explicitly. The Feedback Transformer adds *multiple* keys and *multiple* queries from heterogeneous sources, but the operation at the root — softmax over content-based similarity between a query and a set of keys — is Bahdanau et al.'s.

**Cross-attention vs. self-attention.** RNNsearch uses *cross*-attention: the decoder queries the encoder's annotations. In the user's program, the cross-attention pattern reappears whenever the Feedback Transformer integrates feedback from a *different* memory layer (top-down or parallel) into a *current* sensory stage. The within-layer self-attention is the special case where Q, K, V all come from the same source. The 2014 paper is therefore the cross-attention progenitor and the more direct ancestor of the Feedback Transformer's inter-layer integration than the 2017 Transformer's self-attention-everywhere design.

**Soft-alignment as differentiable selection.** The deeper conceptual contribution is that **selection** (which source position to read from) can be made *soft* — a weighted average rather than a hard argmax — and therefore differentiable. This is the move that makes end-to-end backprop through an attention mechanism possible. Every subsequent architecture in the program inherits this: the Recurrent ViT's attention maps are soft, the Feedback Transformer's per-position contributions are soft, the iterative VAE's decoder readout from the guide is soft. The user's competition-emergent-PC story (`the_user_architectural_program.md` §5) explicitly frames hubs as competing to control the softmax attention map — a competition that is *meaningful* only because the softmax is differentiable and learnable, the property Bahdanau et al. established.

**Length / context-window robustness.** The paper's empirical case rests on RNNsearch's *graceful degradation* with sentence length where RNNencdec collapses. The same diagnostic applies to the user's recurrent architectures: a system that bottlenecks all temporal information through a single fixed-size hidden state will fail on long sequences, while one that maintains per-position annotations and attends over them will not. PRISM v2's multi-compartmental memory (`PRISM_V2_PROPOSAL.md` §3.3) is, in part, a response to the same bottleneck argument scaled to internal state rather than external sequence.

**The bitter-lesson framing.** Bahdanau et al. demonstrated that a single end-to-end objective (translation log-likelihood) is sufficient to *induce* a useful alignment mechanism, without alignment-specific supervision. This is the same bitter-lesson commitment the Recurrent ViT and PRISM make: a single objective (change detection, reconstruction, reward) is enough to make the right internal selection mechanism emerge. The attention map should not need to be explicitly supervised.

## 8. Citations to follow

- `cho2014_gru` — the GRU cell and the original "RNNencdec" fixed-vector baseline. In seed, full depth; high priority — both the recurrent primitive and the architectural foil for this paper.
- `sutskever2014_seq2seq` — the contemporary fixed-vector seq2seq baseline (Sutskever, Vinyals, Le 2014). Not yet in seed; high priority for the same reasons as Cho 2014.
- `graves2013_handwriting_attention` — Graves' earlier mixture-density attention for handwriting generation; an alternative attention lineage. Not yet in seed.
- `kalchbrenner_blunsom2013_recurrent_convolutional_translation` — predecessor encoder–decoder translation model. Not yet in seed.
- `luong2015_effective_attention` — Luong et al.'s simplifications of additive attention (global vs. local; dot-product variant). Not yet in seed; high priority as the direct bridge from Bahdanau to Vaswani.
- `xu2015_show_attend_tell` — the application of Bahdanau-style attention to image captioning. Not yet in seed; relevant for the move from sequence to vision.
- `vaswani2017_attention` — the scaled-dot-product, multi-head generalization. In seed, full depth.
- `mnih2014_recurrent_attention` — the contemporary hard-attention RAM model. In seed.
