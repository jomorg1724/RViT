---
id: cho2014_gru
title: "Learning Phrase Representations using RNN Encoder–Decoder for Statistical Machine Translation"
authors:
  - "Cho, Kyunghyun"
  - "van Merriënboer, Bart"
  - "Gulcehre, Caglar"
  - "Bahdanau, Dzmitry"
  - "Bougares, Fethi"
  - "Schwenk, Holger"
  - "Bengio, Yoshua"
year: 2014
venue: "EMNLP 2014"
doi: ""
arxiv: "1406.1078"
url: "https://arxiv.org/abs/1406.1078"
tags:
  - recurrent-networks
  - deep-learning
  - representation-learning
concepts:
  - gru-cell
  - recurrence-for-temporal-dynamics
  - gain-modulation
related:
  - bahdanau2014_neural_translation
  - ballas2016_convgru
  - hochreiter_schmidhuber1997_lstm
  - jozefowicz2015_rnn_exploration
  - vaswani2017_attention
relevance_to:
  - recurrent_vit
  - prism_v1
  - prism_v2
seed_source:
  - manual
status: full
depth: full
last_updated: "2026-05-15"
---

# Learning Phrase Representations using RNN Encoder–Decoder for Statistical Machine Translation

## 1. Abstract

The paper introduces the **RNN Encoder–Decoder**, a novel neural architecture consisting of two recurrent networks: an encoder RNN that maps a variable-length source sequence into a fixed-length vector representation, and a decoder RNN that maps this representation back to a variable-length target sequence. The two networks are trained jointly to maximize the conditional probability of a target sequence given a source sequence. Trained on aligned phrase pairs from the WMT'14 English–French corpus, the model's learned phrase-pair scores are incorporated as an additional feature in a log-linear phrase-based statistical machine translation (SMT) pipeline (Moses), yielding measurable BLEU improvements over the baseline. The paper also introduces a new "hidden unit that includes a reset gate and an update gate" — what subsequently became known as the **Gated Recurrent Unit (GRU)** — designed as a simpler alternative to the LSTM cell, with comparable empirical performance but fewer parameters and gates. Qualitative analysis shows that the learned continuous-space phrase representations cluster semantically and syntactically meaningful phrases together, suggesting that the encoder–decoder learns useful linguistic structure end-to-end from the translation objective.

## 2. Why this matters for us

This is **the original GRU paper** — the source of the gated recurrent cell that the user's program depends on throughout its memory layers. The GRU is the direct ancestor of the ConvGRU (Ballas et al. 2016) used as PRISM v1's memory cell, the slow/fast dual memory in PRISM v2, and the spatially-independent-processing stage of the GridCell RNN. The reset-gate / update-gate decomposition introduced here is the conceptual basis for FiLM-style multiplicative modulation: a sigmoid-bounded gate that elementwise multiplies a candidate state. Equally important, the **encoder–decoder framing** introduced in this paper — a forward-reasoning RNN building a representation that a backward-reasoning RNN unpacks — prefigures the user's iterative variational encoder–decoder ($n_{FR}$ forward passes building a guide, $n_{BR}$ backward passes producing reconstruction proposals). Without this paper, none of the recurrent commitments in the user's architectural program have a citable foundation.

## 3. Key claims

1. A neural network can learn a joint conditional distribution $p(y_1, \ldots, y_{T_y} \mid x_1, \ldots, x_{T_x})$ over variable-length sequence pairs by factoring it through a fixed-length intermediate representation $c$ produced by an encoder RNN.
2. The same architecture, trained on aligned phrase pairs, produces a useful **phrase-pair scoring function** that augments — but does not replace — classical phrase-based SMT.
3. A new hidden unit (the GRU) with a **reset gate** $r$ and an **update gate** $z$ achieves performance comparable to LSTM on this task while using fewer parameters and gates.
4. The reset gate controls how much of the previous hidden state contributes to the candidate update; the update gate controls how much of the candidate vs. the previous state survives to the next time step. Together they let the unit *learn to forget* on a per-dimension basis.
5. The continuous-space phrase representations the encoder produces are **semantically and syntactically organized** — qualitatively visible in 2D projections where semantically related phrases form local clusters and short syntactic variants align along systematic directions.
6. Augmenting a state-of-the-art phrase-based SMT system (Moses) with the RNN Encoder–Decoder's phrase-pair score as an additional log-linear feature yields measurable BLEU improvements on WMT'14 English–French.

## 4. Methods

**Encoder–decoder architecture.** Given a source sequence $\mathbf{x} = (x_1, \ldots, x_{T_x})$, the encoder RNN reads it left-to-right, updating its hidden state $h_t = f(x_t, h_{t-1})$. After processing the full sequence, the final hidden state $c = h_{T_x}$ serves as a fixed-length summary. The decoder RNN is trained to generate the target sequence $\mathbf{y} = (y_1, \ldots, y_{T_y})$ conditioned on $c$: its hidden state evolves as $h'_t = f(h'_{t-1}, y_{t-1}, c)$, and the conditional probability factorizes as

$$
p(\mathbf{y} \mid \mathbf{x}) = \prod_{t=1}^{T_y} p(y_t \mid y_{<t}, c) = \prod_{t=1}^{T_y} g(h'_t, y_{t-1}, c)
$$

where $g$ is a softmax output layer over the target vocabulary. The encoder and decoder share no weights but are trained jointly to maximize $\log p(\mathbf{y} \mid \mathbf{x})$ over the training corpus.

**The Gated Recurrent Unit (GRU).** Where a vanilla RNN computes $h_t = \tanh(W x_t + U h_{t-1})$, the GRU introduces two sigmoid gates:

$$
r_t = \sigma(W_r x_t + U_r h_{t-1}) \quad \text{(reset gate)}
$$
$$
z_t = \sigma(W_z x_t + U_z h_{t-1}) \quad \text{(update gate)}
$$
$$
\tilde h_t = \tanh(W x_t + U(r_t \odot h_{t-1})) \quad \text{(candidate update)}
$$
$$
h_t = (1 - z_t) \odot h_{t-1} + z_t \odot \tilde h_t \quad \text{(final update)}.
$$

The reset gate $r_t$ controls how much of $h_{t-1}$ feeds into the candidate $\tilde h_t$: if $r_t \approx 0$, the unit "forgets" its past and treats $x_t$ as a fresh start. The update gate $z_t$ controls how much of the candidate replaces the previous state: if $z_t \approx 0$, $h_t \approx h_{t-1}$ (information preserved); if $z_t \approx 1$, $h_t \approx \tilde h_t$ (full update). The two gates jointly play the role of the LSTM's input, forget, and output gates — collapsing three multiplicative controls into two — without an explicit cell state separate from the hidden state.

**Integration with phrase-based SMT.** The Moses system represents translation as a log-linear combination of feature functions over phrase pairs $(\bar f, \bar e)$. The RNN Encoder–Decoder is trained on phrase pairs from the WMT'14 phrase table and produces a score $\log p_{\text{RNN}}(\bar e \mid \bar f)$ that is added as a new feature alongside the standard SMT features (translation probability, language model, reordering, etc.). Feature weights are tuned on the development set using MERT.

**Training.** SGD with Adadelta on minibatches of phrase pairs. Source and target vocabularies restricted to the 15,000 most frequent words; OOV tokens map to `[UNK]`. Hidden state dimension is 1000. No alignment supervision beyond the bilingual phrase table.

## 5. Results

**BLEU on WMT'14 English–French (newstest2014).** The baseline Moses phrase-based system achieves a BLEU score in the low-30s. Adding the RNN Encoder–Decoder phrase-pair score as a log-linear feature yields a consistent improvement of roughly **+1 BLEU point** over the baseline. The improvement is comparable to that obtained by adding a separate continuous-space language model (CSLM) feature, and the two improvements are partially additive — combining both features gives the best reported result.

**Phrase-representation quality.** 2D projections (Barnes-Hut t-SNE) of the encoder's final-state vectors $c$ for phrases in the test set show clear semantic clustering: temporal expressions ("for several years," "for many years," "for a long time") form a tight neighborhood; syntactically parallel phrases ("the United States," "the European Union") align along systematic directions. Crucially, the clustering reflects **semantic and syntactic** structure simultaneously — the model is not just memorizing surface forms.

**GRU vs. LSTM (qualitative).** The paper reports that the GRU and LSTM achieve comparable performance on this task, but does not perform an exhaustive comparison. The empirical claim is "competitive," not "superior" — the parameter savings and architectural simplicity are presented as the GRU's main advantage. (A more thorough head-to-head comparison would not arrive until Jozefowicz et al. 2015, which broadly confirms parity across tasks with task-specific minor differences.)

## 6. Critique / limitations

**The fixed-length bottleneck.** The single context vector $c$ summarizing an arbitrarily long source sequence is the architectural failure mode that Bahdanau, Cho & Bengio (2014, `bahdanau2014_neural_translation`) — co-authored by Cho and Bahdanau, four months later — explicitly identified and remedied with attention. The 1406.1078 paper itself shows performance degrading on longer phrases, and the discussion implicitly anticipates the bottleneck argument. Read in the timeline, this paper sets up the problem that the additive-attention paper solves: same group, same encoder–decoder framing, plus a soft-alignment mechanism that removes the fixed-vector constraint.

**SMT-augmentation framing, not end-to-end NMT.** This paper does *not* report a fully neural translation system. The RNN Encoder–Decoder is a *feature* in a classical phrase-based SMT pipeline. The end-to-end neural-translation case is made by Sutskever et al. (2014, sequence-to-sequence) and Bahdanau et al. (2014). The GRU contribution stands on its own, but the translation claim is more modest than later seq2seq work made it appear in retrospect.

**No ablation of the gate structure.** The paper proposes the GRU but does not systematically ablate the reset vs. update gate. Are both necessary? Is the asymmetric coupling $(1-z) h + z \tilde h$ critical, or would two independent sigmoids work? These questions were left for subsequent work (Jozefowicz et al. 2015; Chung et al. 2014 "Empirical Evaluation of Gated Recurrent Neural Networks on Sequence Modeling").

**No theoretical analysis of vanishing gradients.** The LSTM paper (Hochreiter & Schmidhuber 1997) explicitly motivated the cell-state / gate structure via the constant-error-carousel argument. The GRU paper provides no analogous derivation; the gate structure is presented as a design choice justified empirically rather than theoretically. Why this particular gate decomposition succeeds is left for later analyses (e.g., Tallec & Ollivier's chrono-initialization work).

**No public framework for inter-cell communication.** The model is a single recurrent encoder and a single recurrent decoder. There is no notion of multiple recurrent units operating in parallel, no hierarchical stacking with cross-level feedback. The multi-compartmental, hierarchical-feedback architecture of the user's program requires extensions far beyond what this paper supplies.

**Vocabulary restriction.** All experiments use a 15K-word vocabulary; rare-word handling is brittle. This is a property of the era's training infrastructure, not a substantive limitation of the GRU itself.

## 7. Connection to our work

The GRU defined in this paper is the **substrate of every recurrent state in the user's architectural program**. The specific load-bearing connections:

**ConvGRU and PRISM v1.** Ballas et al. (2016, `ballas2016_convgru`) construct the convolutional GRU by replacing the fully-connected weight matrices $W_z, U_z, W_r, U_r, W, U$ in *this paper's equations* with 2D convolutions. PRISM v1's working memory $M_t$ is a ConvGRU cell — i.e., directly an instance of this paper's recurrent unit, lifted to a spatial feature map (`THESIS.md` §2.4–§2.5). Every architectural argument PRISM v1 makes about "the memory remembers *where* things are" stands on the GRU update rule $h_t = (1 - z_t) \odot h_{t-1} + z_t \odot \tilde h_t$ — applied per-position, with $z_t$ a spatial map of update probabilities.

**The reset / update gate as the conceptual basis for FiLM.** PRISM v1's FiLM modulation (`THESIS.md` §2.4; Perez et al. 2018) applies featurewise affine transforms $\gamma \odot x + \beta$ to a feature stack. The GRU's update rule $h_t = (1 - z_t) \odot h_{t-1} + z_t \odot \tilde h_t$ is structurally the same operation: a sigmoid-bounded multiplicative gate $z_t$ controlling a convex combination. FiLM is the un-bounded, unconstrained generalization of the GRU's gating. The Feedback Transformer's multiplicative-feedback variant (`concepts/feedback_transformer.md`) — element-wise multiplication of sensory Q/K by recurrent-state Q/K — is the same primitive applied inside attention. The lineage **GRU gate → FiLM → multiplicative feedback transformer** runs through this paper.

**Encoder–decoder framing prefigures the iterative VAE.** The user's iterative variational encoder–decoder (`the_user_architectural_program.md` §4) consists of an encoder running $n_{FR}$ forward-reasoning passes to build a guide $H_{n_{FR}}$, and a decoder running $n_{BR}$ backward-reasoning passes producing reconstruction proposals $\tilde X_\tau$ initialized from that guide. The structural template — encoder builds a representation, decoder unpacks it, both trained jointly under a single objective — is the framing introduced in this paper, generalized along three axes: (i) iteration (the encoder runs multiple times over the *same* input rather than once over a sequence), (ii) variational regularization (KL on the guide), and (iii) hierarchical decoder structure (decoder is a multi-compartmental memory stack, not a single RNN). But the foundation — *the same architecture acts as both feature extractor and generator, jointly trained* — is here.

**Bidirectional information flow.** This paper's encoder–decoder is unidirectional (left-to-right). Bahdanau et al. (`bahdanau2014_neural_translation`) introduced the bidirectional encoder. The Feedback Transformer takes the bidirectional commitment further: every recurrent state can both send and receive feedback from every other, via the per-state Q/K/V projection structure. The 2014 GRU paper is the unidirectional baseline against which the Feedback Transformer's bidirectional hierarchical feedback is the generalization.

**Slow/fast dual memory in PRISM v2.** PRISM v2 (`PRISM_V2_PROPOSAL.md` §3.3) maintains two ConvGRU memories operating at different effective timescales. The mechanism by which a recurrent cell can be made "slow" is to bias the update gate $z_t$ toward zero — preserving $h_{t-1}$ across many time steps. Chrono-initialization (Tallec & Ollivier 2018) is precisely an initialization scheme for the update gate's bias that controls the cell's effective timescale. This entire family of techniques operates on the gate parameter introduced in this paper.

**Why not LSTM?** The user's program uses LSTM-style gating (GridCell RNN, `the_user_architectural_program.md` §2) but the ConvGRU substrate of PRISM v1 / v2 uses GRU-style gating. The parameter-efficiency argument that justifies ConvGRU over ConvLSTM — fewer gates, fewer matrices, fewer parameters per spatial position — is *this paper's argument*, lifted to the convolutional setting. The decision to commit to GRU rather than LSTM as the recurrent primitive in PRISM is supported by Cho et al. 2014's parameter-count claim and confirmed empirically by Jozefowicz et al. 2015's broad comparison.

## 8. Citations to follow

- `sutskever2014_seq2seq` — Sutskever, Vinyals, Le. The contemporary fully-neural seq2seq baseline (LSTM-based). The natural companion paper to read alongside this one. **Not yet in seed; high priority.**
- `chung2014_empirical_gated_rnn` — Chung, Gulcehre, Cho, Bengio. "Empirical Evaluation of Gated Recurrent Neural Networks on Sequence Modeling." The systematic GRU-vs-LSTM ablation the present paper does not provide. **Not yet in seed; high priority for the gate-structure justification.**
- `hochreiter_schmidhuber1997_lstm` — The LSTM cell. In seed, full depth. The architectural foil this paper simplifies.
- `bahdanau2014_neural_translation` — The attention paper, by overlapping authors. In seed, full depth. The follow-up that removes this paper's fixed-vector bottleneck.
- `tallec_ollivier2018_chrono` — Chrono-initialization of recurrent gates. The principled timescale-control method that operates on the gate this paper introduces. **Not yet in seed.**
- `mujika2017_fast_slow` — Fast-slow RNNs. The hierarchical-timescale construction PRISM v2 builds on. **Not yet in seed.**
- `graves2013_speech_lstm` — Graves' speech-recognition LSTM work. The pre-existing benchmark for gated RNN performance. **Not yet in seed.**
- `pascanu2013_exploding_gradients` — Pascanu, Mikolov, Bengio. The vanishing/exploding-gradient analysis that motivated the gated-RNN era. **Not yet in seed.**
