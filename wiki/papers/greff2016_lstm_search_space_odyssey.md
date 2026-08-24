---
id: greff2016_lstm_search_space_odyssey
title: "LSTM: A Search Space Odyssey"
authors:
  - "Greff, Klaus"
  - "Srivastava, Rupesh K."
  - "Koutník, Jan"
  - "Steunebrink, Bas R."
  - "Schmidhuber, Jürgen"
year: 2017
venue: "IEEE TNNLS"
doi: "10.1109/TNNLS.2016.2582924"
arxiv: "1503.04069"
url: "https://arxiv.org/abs/1503.04069"
tags:
  - recurrent-networks
  - deep-learning
  - ablation-study
  - methodology
concepts:
  - lstm-cell
related:
  - hochreiter_schmidhuber1997_lstm
  - jozefowicz2015_rnn_exploration
  - beck2024_xlstm
  - ballas2016_convgru
  - mujika2017_fast_slow_rnn
  - cho2014_gru
  - shi2015_convlstm
  - tallec_ollivier2018_chrono_init
relevance_to:
  - recurrent_vit
  - prism_v1
  - prism_v2
seed_source:
  - manual
status: full
depth: full
last_updated: "2026-05-16"
---

# LSTM: A Search Space Odyssey

## 1. Abstract

Several variants of the Long Short-Term Memory (LSTM) network have been proposed over the years, but it has never been clear which architectural choices are essential and which are interchangeable. Greff, Srivastava, Koutník, Steunebrink & Schmidhuber present the first large-scale, controlled comparison of eight LSTM variants on three representative sequence-learning tasks — speech recognition (TIMIT), handwriting recognition (IAM Online), and polyphonic music modelling (JSB Chorales). Across approximately 5,400 experimental runs (about 15 CPU years), they evaluate each variant under random-search-tuned hyperparameters and analyse hyperparameter importance with the fANOVA framework. None of the eight variants improves significantly on the standard LSTM, but the ablations identify the forget gate and the output activation function as the two most critical components. Coupling the input and forget gates (CIFG, equivalent to the GRU's update gate) and removing peephole connections (NP) cause no significant degradation and simplify the architecture. fANOVA further finds the studied hyperparameters to be approximately independent of one another, and learning rate to dominate by a wide margin — followed by hidden-layer size and input noise — with momentum essentially irrelevant. The authors derive practical guidelines for efficient LSTM tuning.

## 2. Why this matters for us

This is the companion paper to Jozefowicz et al. 2015 and is the second pillar of the empirical case that the vanilla gated-additive LSTM cell is hard to beat. Where Jozefowicz et al. mutate the LSTM equations to search nearby architectures, Greff et al. perform a tightly-controlled ablation of named LSTM components on standardized sequence tasks. The two together cover the LSTM design space and converge on the same conclusion: the forget gate is load-bearing, the rest of the architecture is mostly fungible, and the per-cell innovation budget is small. For the user's program this validates building memory from off-the-shelf gated cells (LSTM in the Recurrent ViT memory update, ConvGRU in PRISM v1's $M_t$, LSTM-derived gating in the GridCell RNN) and spending architectural effort on between-cell structure (Feedback Transformer, multi-compartmental memory, hierarchical bidirectional feedback) instead. The fANOVA result that learning rate dominates is a direct hyperparameter-prioritization prescription for every recurrent training run in our stack.

## 3. Key claims

1. None of eight LSTM variants significantly improves on the standard (vanilla) LSTM across speech, handwriting, and music modelling tasks.
2. The forget gate is essential: removing it (NFG) causes large, consistent performance loss on all three tasks.
3. The output activation function ($\tanh$ on the cell output) is essential: removing it (NOAF) is similarly catastrophic.
4. Peephole connections from the cell state to the gates can be removed (NP) without significant cost and simplify the architecture.
5. Coupling the input and forget gates ($i_t = 1 - f_t$, the CIFG variant — equivalent to the GRU's update gate) is competitive with the full LSTM and saves parameters.
6. The input gate (NIG) and output gate (NOG) can be individually removed with smaller but still non-trivial losses; the output gate is the more dispensable of the two.
7. Full gate recurrence (FGR — making every gate depend on every other gate's previous activation) substantially increases parameter count without improving performance.
8. fANOVA hyperparameter analysis: learning rate is by far the most important hyperparameter, followed by hidden-layer size, and then input noise; momentum is essentially uninformative.
9. The three studied hyperparameters (learning rate, hidden size, input noise) act approximately independently — they can be tuned one at a time without large interaction effects, justifying coordinate-wise random search.
10. Learning rate can be tuned on a small network first and the optimum carries over to larger networks of the same architecture, enabling cheap hyperparameter transfer.

## 4. Methods

**Vanilla LSTM baseline.** The reference cell uses input gate $i_t$, forget gate $f_t$, output gate $o_t$, cell candidate $z_t = \tanh(W_z x_t + R_z h_{t-1} + b_z)$, cell state $c_t = i_t \odot z_t + f_t \odot c_{t-1}$, and hidden output $h_t = o_t \odot \tanh(c_t)$. Each gate is a sigmoid of its own linear combination of $x_t$, $h_{t-1}$, and (via peephole connections) $c_{t-1}$ (for $i, f$) or $c_t$ (for $o$).

**Eight variants.** Each variant removes or modifies one component:
- **NIG** — No Input Gate: $i_t = 1$, removing input gating entirely.
- **NFG** — No Forget Gate: $f_t = 1$, removing forget gating.
- **NOG** — No Output Gate: $o_t = 1$, exposing $\tanh(c_t)$ directly.
- **NIAF** — No Input Activation Function: replace $\tanh$ on the cell candidate with the identity.
- **NOAF** — No Output Activation Function: replace $\tanh$ on the cell output with the identity.
- **NP** — No Peepholes: drop the $c$-to-gate peephole connections.
- **CIFG** — Coupled Input and Forget Gate: $i_t = 1 - f_t$ (the GRU-style update gate).
- **FGR** — Full Gate Recurrence: every gate at time $t$ receives recurrent connections from every gate at time $t-1$ (adds $\sim 9 \times$ the gate-recurrence parameters of the vanilla LSTM).

**Tasks and architectures.**
- *TIMIT* — framewise phoneme classification on the standard speech corpus; 12 MFCC features per frame; bidirectional LSTM with two hidden layers.
- *IAM Online* — online handwriting recognition (pen-trajectory data); CTC loss on character output; bidirectional LSTM with two hidden layers.
- *JSB Chorales* — next-step polyphonic note prediction on Bach chorales; unidirectional LSTM with one hidden layer.

**Random-search hyperparameter tuning.** For each (variant, task) pair, 200 hyperparameter samples are drawn uniformly at log-scale over learning rate, hidden-layer size, momentum, and input Gaussian noise standard deviation. Each sample is trained until validation-set performance stops improving. The best 10 trials per (variant, task) pair are reported. Total: $8 \text{ variants} \times 3 \text{ tasks} \times 200 \text{ trials} + \text{baseline runs} \approx 5{,}400$ experiments.

**fANOVA analysis.** The functional ANOVA decomposition of Hutter, Hoos & Leyton-Brown attributes performance variance to individual hyperparameters and their interactions. This identifies which hyperparameters dominate and how strongly they interact.

## 5. Results

- **TIMIT framewise classification error (lower is better, vanilla LSTM ≈ 29.6%).** NFG: significantly worse ($\Delta \approx +6$ points). NOAF: significantly worse ($\Delta \approx +4$ points). NP, CIFG, NIG, NOG, FGR, NIAF: within ~1 point of vanilla, differences not statistically significant.
- **IAM Online character error rate (lower is better, vanilla LSTM ≈ 9.3%).** NFG: catastrophic ($\Delta \approx +30$ points). NOAF: catastrophic ($\Delta \approx +30$ points). NIAF: small but significant loss. CIFG and NP: indistinguishable from vanilla.
- **JSB Chorales negative log-likelihood (lower is better, vanilla LSTM ≈ 8.4).** NFG: significantly worse. NOAF and NIAF: significantly worse. All other variants within noise.
- **fANOVA marginal importance.** Learning rate accounts for the largest fraction of performance variance on all three tasks (typically >50%). Hidden-layer size is second (10–20%). Input noise is third on TIMIT (helpful) but negligible or harmful on IAM/JSB. Momentum is essentially uninformative.
- **Hyperparameter interactions.** fANOVA pairwise terms are small relative to marginals: hyperparameters can be tuned approximately independently.
- **Transfer of learning rate across hidden sizes.** The optimal learning rate is roughly invariant to hidden-layer size, so tuning learning rate on small networks transfers to large ones.
- **Parameter cost.** FGR roughly triples the parameter count vs vanilla LSTM with no performance gain — a pure cost. CIFG and NP modestly reduce parameter count with no performance loss — pure simplifications.

## 6. Critique / limitations

The variant set is one-at-a-time ablations of named components; the search does not explore compound modifications (e.g., CIFG + NP simultaneously, which would be the GRU-without-reset-gate). Jozefowicz et al. 2015's mutation-based search complements this by exploring compound variants, and reaches the same broad null conclusion.

Tasks are moderate-length sequence modelling (TIMIT frames, online handwriting strokes, music notes). The conclusions speak only weakly to very long sequences (where state-space models and xLSTM operate), to convolutional recurrent units operating over spatial grids (ConvLSTM, ConvGRU), or to deeply hierarchical recurrent stacks with multi-timescale updates (HRM, Mujika fast-slow). For these regimes the ablation has not been re-run, and the within-cell architecture may matter more.

The fANOVA importance result is conditional on the chosen random-search ranges. Learning rate dominates partly because its log-range is wide ($10^{-5}$ to $10^{-1}$), which guarantees a large performance spread; a narrower well-chosen range would shrink its apparent importance. The qualitative ordering (LR > size > noise > momentum) is nonetheless robust to range choice in published replications.

The "no architecture beats vanilla LSTM" conclusion is genuinely true within the LSTM design space as defined here, but does not establish that the LSTM design space is the right design space. The transformer (Vaswani 2017, two years later), state-space models, and Beck et al. 2024 xLSTM all step outside the space studied here and obtain qualitatively different gains. The right reading is "you cannot squeeze more out of the LSTM by rearranging its gates," not "no sequence model can beat the LSTM."

The forget gate's importance is consistent with Gers, Schmidhuber & Cummins 2000 ("Learning to Forget"), which originally introduced it. This paper's contribution is to quantify its necessity on standardized benchmarks rather than to discover it.

## 7. Connection to our work

This paper is one of the two empirical pillars (with Jozefowicz et al. 2015) that licence the user's architectural program to treat the gated LSTM cell as a primitive and spend innovation budget on between-cell topology. The relevance is concrete at four levels.

**Validation of the gated-cell substrate.** The user's GridCell RNN (described in `Private & Shared/Encoder-Decoder Architecture` as "LSTM-derived gating") is built on top of a gated additive recurrent unit. Greff et al.'s null-result ablation across 8 variants on 3 tasks plus Jozefowicz et al.'s parallel null result over a much wider mutation space jointly establish that this substrate is genuinely near-optimal among recurrent units of comparable size. The decision in PRISM v1 (`THESIS.md` §2.3) to implement the slow memory $M_t$ as Ballas et al.'s ConvGRU rather than as a bespoke recurrent unit is supported by exactly this evidence — ConvGRU inherits the load-bearing properties Greff et al. identify (the GRU is effectively CIFG + NP applied jointly, both of which Greff et al. show are free simplifications).

**Concrete component prescriptions.** Greff et al.'s ablation directly prescribes which LSTM components must be present and which can be dropped. For every recurrent module in our stack:
- The **forget gate must be present** and (per Jozefowicz et al.) initialised with bias $\geq 1$. NFG is catastrophic on all three tasks tested here.
- The **output activation $\tanh(c_t)$ must be present**. NOAF is catastrophic. This is non-obvious — removing the output nonlinearity might seem like a clean simplification, but Greff et al. show it is not. The GridCell RNN's SIP proposal should therefore preserve a $\tanh$-style cell-output nonlinearity.
- **Peephole connections can be omitted**. The ConvGRU we use in PRISM v1 already omits them; the LSTM variants we consider for the Recurrent ViT memory should follow suit.
- **Coupling input and forget gates is free**. The GRU's update gate (which is CIFG) loses nothing relative to a full LSTM. This further supports the ConvGRU choice in PRISM v1.
- **The output gate is the most dispensable LSTM gate**. If a parameter-budget squeeze arises in any of our recurrent modules, removing the output gate (NOG) is the safest place to cut. This is consistent with the GRU's design, which has no output gate.

**fANOVA hyperparameter-priority prescription.** Greff et al.'s most actionable single result is that learning rate dominates other hyperparameters by a wide margin, and the optimal learning rate transfers across hidden sizes. For our training pipelines this means: (i) spend the bulk of hyperparameter-search compute on learning rate (broad log-scale random search), not on momentum or noise; (ii) tune learning rate on a small model first and use it for larger models; (iii) since hyperparameters are approximately independent, coordinate-wise search is essentially as good as joint search, which we have implicitly assumed in PRISM training runs.

**Strategic alignment with the user's between-cell program.** As with Jozefowicz et al., the larger strategic message is that within-cell architecture is a closed frontier and between-cell architecture is the open one. The Feedback Transformer integrates state from many cells; the multi-compartmental memory stack arranges many cells hierarchically; the iterative variational encoder-decoder runs many cells in two coupled loops. Each of these scales an existing gated-cell substrate rather than replacing it. Greff et al. supply the evidence that this is the right division of architectural labour.

**Connection to the published Recurrent ViT.** §6.7 of 2502.10955 reports three memory-integration ablations (tokens, additive, multiplicative). The methodology that Greff et al. embody — fix the task, vary one architectural component, report random-search-tuned best results — is the methodology §6.7 should aspire to. In a future expansion, §6.7 should additionally ablate (i) whether the recurrent state $H^{(t)}$ uses an LSTM, GRU, or simplified-output-gate-removed cell, and (ii) whether peephole connections (if present) matter. Greff et al.'s priors predict (i) does not matter much and (ii) does not matter at all.

**Open tension with xLSTM.** Beck et al. 2024 explicitly reopens the within-cell design space with exponential gating and matrix memory and reports gains at large scale. If those gains are reproducible, Greff et al.'s 2017 conclusion is bounded by their compute scale and task length, not universal. The user's program is compatible with either outcome — Feedback Transformer routes between cells of any internal architecture — but the xLSTM line should be tracked as a potential drop-in replacement for the GridCell RNN's inner unit if and when its scaling story holds up.

## 8. Citations to follow

- `hochreiter_schmidhuber1997_lstm` — the LSTM itself; already in seed at full depth.
- `gers2000_learning_to_forget` — Gers, Schmidhuber & Cummins introduced the forget gate; not yet in seed. Greff et al. quantify on standardized tasks the importance Gers et al. first argued.
- `gers2002_peephole_lstm` — Gers, Schraudolph & Schmidhuber introduced peephole connections; not in seed. Greff et al. show they can be dropped without cost — directly contradicting the original peephole motivation for the variants tested.
- `cho2014_gru` — the GRU paper; In seed, full depth. Greff et al.'s CIFG variant is effectively the GRU's update gate, so the GRU literature should be added in the next expansion.
- `hutter2014_fanova` — the functional-ANOVA hyperparameter-importance framework Greff et al. use; not in seed but a methodologically important reference for our own hyperparameter-tuning pipelines.
- `bergstra2012_random_search` — Bergstra & Bengio's random-search foundations; not in seed. The methodological basis for Greff et al.'s search strategy and for ours.
- `klambauer2017_selu` — self-normalizing networks; not in seed. A more recent attempt to remove gating altogether; an interesting contrast point.
- `tallec_ollivier2018_chrono_init` — chrono initialisation of forget-gate bias; already in seed. The natural extension of Greff et al.'s forget-gate-importance finding to long-horizon tasks.
- `shi2015_convlstm` — the original ConvLSTM; In seed, full depth. The convolutional generalisation of the cell Greff et al. ablate; a natural companion paper for our PRISM v1 ConvGRU choice.
