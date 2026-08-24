---
id: mujika2017_fast_slow_rnn
title: "Fast-Slow Recurrent Neural Networks"
authors:
  - "Mujika, Asier"
  - "Meier, Florian"
  - "Steger, Angelika"
year: 2017
venue: "NeurIPS"
doi: ""
arxiv: "1705.08639"
url: "https://arxiv.org/abs/1705.08639"
tags:
  - recurrent-networks
  - deep-learning
concepts:
  - slow-fast-recurrence
  - lstm-cell
  - parallel-recurrent-units
  - multi-compartmental-memory
  - coupled-rnn-world-models
related:
  - wang2025_hierarchical_reasoning_model
  - tallec_ollivier2018_chrono_init
  - hochreiter_schmidhuber1997_lstm
  - beck2024_xlstm
  - schmidhuber2015_learn_to_think
  - ha_schmidhuber2018_world_models
  - graves2016_act
relevance_to:
  - prism_v2
seed_source:
  - prism_v2_proposal
status: full
depth: full
last_updated: "2026-05-18"
---

# Fast-Slow Recurrent Neural Networks

## 1. Abstract

Processing sequential data of variable length is a major challenge in a wide range of applications, such as speech recognition, language modeling, generative image modeling and machine translation. The authors propose the Fast-Slow RNN (FS-RNN), which "incorporates the strengths of both multiscale RNNs and deep transition RNNs as it processes sequential data on different timescales and learns complex transition functions from one time step to the next." The FS-RNN is evaluated on two character-level language modeling data sets, Penn Treebank and Hutter Prize Wikipedia (enwik8), improving state-of-the-art results to 1.19 and 1.25 BPC respectively. An ensemble of two FS-RNNs achieves 1.20 BPC on Hutter Prize Wikipedia, outperforming the best known compression algorithm (cmix v13, 1.225 BPC) with respect to the BPC measure. The authors also present an empirical investigation of the learning and network dynamics, demonstrating that the architecture is general: any kind of RNN cell can serve as a building block.

## 2. Why this matters for us

Mujika et al. 2017 is the foundational ML reference for the slow/fast RNN family that PRISM v2's dual-memory design ([PrismV2/docs/PRISM_V2_PROPOSAL.md](PrismV2/docs/PRISM_V2_PROPOSAL.md) §3.3) and the user's multi-compartmental-memory program ([threads/the_user_architectural_program.md](research_db/threads/the_user_architectural_program.md) §3) both descend from. The paper is cited explicitly in the PRISM v2 proposal as the architectural-ML precedent for pairing a fast-updating module (V1-paired $M^{\text{fast}}$) with a slow-updating module (V2-paired $M^{\text{slow}}$). FS-RNN provides three things our program needs: (i) the explicit *coupling* equations between Slow and Fast modules (a template our equations should look like); (ii) empirical evidence that the Slow module preferentially stores long-term information while the Fast module rapidly absorbs novel input — directly supporting the design rationale for diminishing feedback into deeper layers in the user's program; (iii) a working competitive baseline on a small, well-defined sequence task (character-level LM), which is exactly the regime where PRISM v2 should first beat or match published numbers.

## 3. Key claims

1. The FS-RNN unifies two prior architectural traditions — multiscale RNNs (hierarchical update-rate separation, e.g., Clockwork RNN, HM-RNN) and deep transition RNNs (intermediate sequential layers between consecutive hidden states, e.g., Pascanu et al. 2013 deep transition, Recurrent Highway Networks) — in a single design.
2. **Architecture.** In its simplest form: $k$ sequentially-connected Fast cells $F_1, \dots, F_k$ at the lower hierarchical layer plus one Slow cell $S$ at the higher layer. $F_1$ reads input $x_t$ and the previous-step output of $F_k$; $S$ takes the new $h^{F_1}_t$ and produces $h^S_t$ in *the same wall-clock step*; $F_2$ then takes $(h^{F_1}_t, h^S_t)$; subsequent Fast cells $F_3, \dots, F_k$ run in sequence with no further input.
3. The Fast cells learn complex transition functions from one input step to the next (the "deep transition" advantage), while the Slow cell shortens gradient paths between distant inputs (the "multiscale" long-term-dependency advantage).
4. **Empirical SOTA.** FS-LSTM-2 achieves 1.190 BPC on Penn Treebank (7.2M params) and FS-LSTM-4 achieves 1.193 BPC (6.5M params), beating prior best NASCell (1.214 BPC, 16.3M) and HyperLSTM (1.219 BPC, 14.4M) with significantly fewer parameters. On enwik8, Large FS-LSTM-4 reaches 1.245 BPC (47M); a 2-model ensemble reaches 1.198 BPC, exceeding the best text compressor cmix v13 (1.225 BPC).
5. **Mechanistic claim 1 (long-term dependencies).** The gradient $\|\partial L_t / \partial c_{t-k}\|$ is largest for the Slow cell and decays slowly with $k$; for the Fast cell it is small and decays steeply. The Slow cell carries long-range information; the Fast cell does not.
6. **Mechanistic claim 2 (different update rates).** Mean squared change of cell-state values per timestep, $\frac{1}{n}\sum_i (c_{t,i} - c_{t-1,i})^2$, is smallest for the Slow cell among all layers of three compared architectures (FS-LSTM, stacked, sequential). The Slow cell is empirically slow even though no hard update-frequency rule is imposed — the slow timescale emerges from the architecture.
7. **Mechanistic claim 3 (adaptation to unexpected input).** Character-position-conditioned BPC plots show that all three architectures predict the first letter of a word roughly equally well, but FS-LSTM is significantly better on subsequent positions. The Fast layer rapidly absorbs the new high-entropy input and exploits it for the next characters.
8. **Generality.** Any RNN cell can serve as $F_i$ or $S$. The authors use LSTMs (Fast-Slow LSTM) but note EURNNs and NARX RNNs as plausible alternative Slow cells with better long-term memory.
9. **Code availability.** Reference implementation released at `https://github.com/amujika/Fast-Slow-LSTM`.
10. **Negative ablation on deeper hierarchy.** Stacking *additional* Slow-style cells above $S$ — i.e., a 3-tier or 4-tier hierarchy where each higher tier runs on a still slower timescale, à la Clockwork RNN — caused overfitting and worse test performance on PTB and enwik8 even with regularization. The two-tier (one Slow + one Fast chain) structure is the empirical sweet spot at this scale.

## 4. Methods

**Architecture.** Let $f^Q(h, x)$ denote a generic RNN cell mapping state $h$ and optional input $x$ to a new state. The FS-RNN with $k$ Fast cells obeys the per-step equations
$$
h^{F_1}_t = f^{F_1}(h^{F_k}_{t-1}, x_t), \qquad h^S_t = f^S(h^S_{t-1}, h^{F_1}_t),
$$
$$
h^{F_2}_t = f^{F_2}(h^{F_1}_t, h^S_t), \qquad h^{F_i}_t = f^{F_i}(h^{F_{i-1}}_t) \text{ for } 3 \le i \le k.
$$
Output is an affine transform of $h^{F_k}_t$. The Slow cell's state $h^S$ persists across the input timeline and receives input only from $F_1$; it is updated *every input step* (not every $T$ steps as in Clockwork or HRM). The "slow" character of $S$ is not enforced by gating but is an emergent property of the architecture (verified in §5 of the paper). The Fast chain $F_1 \to F_2 \to \dots \to F_k$ constitutes a deep transition function within one input step: $F_2, \dots, F_k$ are "shallow networks sharing hidden state," i.e., a sequential composition that gives the input-to-output map exponentially greater expressive depth without adding cross-timestep recurrence.

**LSTM building block.** When each cell is an LSTM with state $(h, c)$:
$$
\begin{pmatrix} f_t \\ i_t \\ o_t \\ g_t \end{pmatrix} = W^Q_h h_{t-1} + W^Q_x x_t + b^Q, \quad c_t = \sigma(f_t) \odot c_{t-1} + \sigma(i_t) \odot \tanh(g_t), \quad h_t = \sigma(o_t) \odot \tanh(c_t).
$$
Forget bias initialized to 1; orthogonal weight initialization; layer normalization is applied to the cell state and each gate separately.

**Training.** Cross-entropy loss $L = -\frac{1}{n}\sum_i \log p_\theta(x_i | x_1, \dots, x_{i-1})$, evaluated in BPC. Adam optimizer; gradient norm clipped to 1; truncated BPTT with TBPTT length 150 (100 for the Large variant); minibatch size 128; learning rate 0.002 (PTB) / 0.001 (enwik8) with stepwise decay. Regularization: non-recurrent dropout 0.2–0.35; Zoneout on recurrent connections (cell zoneout 0.3–0.5, hidden zoneout 0.05–0.1). Final hidden state is carried to the next sequence segment.

**Datasets and splits.** Penn Treebank: 5.1M / 400K / 450K characters (train/val/test) following Mikolov 2012. enwik8 (Hutter Prize Wikipedia, 100M chars, 205 unique tokens): 90M / 5M / 5M following Chung et al. 2015.

**Ablation: stacking deeper.** Adding additional hierarchical layers each operating on a slower timescale (Clockwork-style stacking above the Slow cell) led to overfitting and worse test performance on these data sets, even with regularization. The authors keep the two-layer structure (one Slow + chain of Fast).

**Dynamics analysis (§4.2).** Three roughly parameter-matched models on enwik8 trained for 20 epochs without dropout/zoneout (only layer norm): FS-LSTM (1 Slow + 4 Fast, 450 units each); stacked-LSTM (5 layers × 375 units); sequential-LSTM (5 sequentially connected cells × 500 units). Per-timestep wall-clock cost roughly matched. Three measurements: long-range gradient norm $\|\partial L_t/\partial c_{t-k}\|$ vs $k$ (Fig. 3); rate of cell-state change $\frac{1}{n}\sum_i (c_{t,i}-c_{t-1,i})^2$ (Fig. 4); per-character-position BPC inside words (Fig. 5).

**Coupling asymmetry.** Only $F_2$ — not $F_1$ — receives input from $S$. $F_1$ depends on the previous step's $h^{F_k}_{t-1}$ and the current input $x_t$, computing the "first guess" $h^{F_1}_t$ purely from local context. $S$ then refines its slow context with this guess, and the refined $h^S_t$ enters the Fast chain at $F_2$. This is structurally similar to a Kalman-filter "predict then correct" sequence: $F_1$ predicts, $S$ updates its slow estimate, $F_2$ onwards corrects using the updated slow context. The asymmetry is load-bearing — feeding $S$'s state to $F_1$ would create an immediate cycle through the slow module on every step, defeating the timescale separation.

**Hyperparameter ranges.** Fast-cell size sweeps from 500 (PTB FS-LSTM-4) to 1200 (Large enwik8 FS-LSTM-4); Slow-cell size from 400 (PTB) to 1500 (enwik8). Slow cell is *larger* than each Fast cell on enwik8 — consistent with the design intent that the Slow cell carries the long-range context and benefits more from capacity.

## 5. Results

**Penn Treebank (Table 1).** FS-LSTM-2 1.190 BPC at 7.2M params; FS-LSTM-4 1.193 BPC at 6.5M params. Beats Zoneout LSTM (1.27), 2-layer LSTM (1.243), HM-LSTM (1.24), HyperLSTM-small (1.233), HyperLSTM (1.219, 14.4M), NASCell-small (1.228), NASCell (1.214, 16.3M). Increasing FS-LSTM size further did not improve test BPC (overfitting). FS-LSTM-4's per-step processing is 25% slower than FS-LSTM-2's due to sequential Fast chain.

**enwik8 (Table 2).** FS-LSTM-2 1.290 BPC (27M); FS-LSTM-4 1.277 BPC (27M); Large FS-LSTM-4 1.245 BPC (47M); 2× Large FS-LSTM-4 ensemble 1.198 BPC. Compared to: LSTM (1.461 / 18M), Layer-Norm LSTM (1.402 / 14M), HyperLSTM (1.340 / 27M), HM-LSTM (1.32 / 35M), Surprisal-driven Zoneout (1.31 / 64M), RHN depth-5 (1.31 / 23M), RHN depth-10 (1.30 / 21M), Large RHN depth-10 (1.27 / 46M). The ensemble (1.198) beats cmix v13 (1.225), the leading text compressor.

**Dynamics (small models, no regularization).** FS-LSTM 1.49 BPC vs stacked 1.61 vs sequential 1.58. Gradient curves (Fig. 3): Slow cell's $\|\partial L_t / \partial c_{t-k}\|$ stays elevated out to $k = 100$; Fast cell's is small and steeply decays; stacked-LSTM's bottom layer has very small gradients (vanishing-gradient signature); sequential-LSTM has small steeply-decaying gradients overall. Rate of change (Fig. 4): Slow cell shows the smallest mean-squared change per step among all 7 layers/cells compared; sequential-LSTM the largest; Fast cell next-largest. Per-character BPC inside words (Fig. 5): All architectures equivalent at position 1; FS-LSTM achieves 0.86–0.88× the stacked-LSTM's loss at positions 4–8 (~12–14% relative reduction).

**Scaling within the family.** Going from $k=2$ to $k=4$ Fast cells improves enwik8 BPC from 1.290 to 1.277 at fixed 27M params, demonstrating that the deep-transition chain pays for itself at constant parameter count. Going from 27M to 47M params at $k=4$ further improves BPC from 1.277 to 1.245. On Penn Treebank the FS-LSTM-4 (6.5M params) actually performs slightly *worse* than FS-LSTM-2 (7.2M) — 1.193 vs 1.190 — at smaller scale; the chain depth and model scale interact non-monotonically. The 25%-per-step compute penalty for $k=4$ over $k=2$ is real and limits how far the chain can be extended.

**Wall-clock cost.** The FS-LSTM, stacked-LSTM, and sequential-LSTM in the §4.2 comparison were sized to be wall-clock-equivalent per step (FS: 1 Slow + 4 Fast × 450; Stacked: 5 × 375; Sequential: 5 × 500). On equal compute budget the FS-LSTM achieves the lowest BPC, which is a stronger result than the headline parameter-matched comparison.

## 6. Critique / limitations

The Slow-vs-Fast separation is not a *guaranteed* timescale separation: nothing in the equations forces $h^S$ to update less than $h^F$. The empirical Fig. 4 result that $h^S$ does change less is an *emergent* property of the architecture under the chosen losses and regularization. Under different objectives or different data, the same architecture might not exhibit the same timescale separation. Subsequent work (HRM, chrono-init) imposes the separation explicitly to remove this dependence on emergence.

The architecture's "deep transition" property comes entirely from the Fast chain $F_2 \to \dots \to F_k$. With $k = 2$, the deep-transition gain is marginal (one extra LSTM step). The paper does not isolate the multiscale contribution from the deep-transition contribution: the authors do not run an ablation that removes $S$ and keeps the Fast chain, or vice versa, on the main benchmarks. The §4.2 dynamics analysis comes closest, but does not directly attribute BPC improvement to one mechanism or the other.

The "outperforms cmix" claim is real on BPC but not on the cmix benchmark's own terms: cmix is scored on the size of the compressed file *including the decompressor*. The FS-LSTM model has 47M (or 2 × 47M for the ensemble) parameters that would have to be transmitted, vs cmix's compact code, so the practical-compression claim is overstated.

The architecture is evaluated only on character-level language modeling. No results on word-level LM, machine translation, speech recognition, or vision tasks are reported. The "general" claim in the abstract — that any RNN cell type can be used — is illustrated only with LSTMs.

The Slow cell receives input only from $F_1$, and sends its state only to $F_2$. The cycle through the Slow cell is therefore: input → $F_1$ → $S$ → $F_2$ → … → $F_k$ → output, and $S$'s only feedback is via the next step's $F_1$ → $S$ path. This is a much simpler coupling than later work (HRM's nested fixed-point, the Feedback Transformer's per-state Q/K/V) and limits how much top-down control the Slow cell can exert.

The Penn Treebank result does not improve with more parameters (the authors attribute this to overfitting on a small corpus), suggesting the design is well-suited to small-data regimes but its scaling behavior on larger corpora was not fully characterized at publication time.

The paper's "best compressor" framing implicitly assumes BPC on a held-out test set transfers to compression of unseen English text. Since the model is trained directly on the first 90M characters of enwik8 and evaluated on the last 5M characters of the same corpus, the test distribution is statistically very close to the train distribution (consecutive sections of the same Wikipedia dump). The "should achieve similar performance on any part of the English Wikipedia" remark in §4.1 is plausible but not directly tested.

No measurement of training stability across seeds is reported. Given that the Slow / Fast separation is *emergent* rather than imposed, run-to-run variability in whether the separation actually develops would be informative; the paper reports single numbers without error bars.

The contemporary Transformer (Vaswani et al. 2017, same NeurIPS) is not a baseline. By 2018–2019 character-level Transformers (Al-Rfou et al., Transformer-XL) had surpassed all the RNN baselines in this paper on enwik8. FS-RNN's empirical SOTA claim is therefore correctly read as "best RNN at NeurIPS 2017," not as a stable architectural winner.

## 7. Connection to our work

FS-RNN is the foundational ML paper on fast-slow RNN architectures and is cited in this role in PRISM v2's proposal ([PrismV2/docs/PRISM_V2_PROPOSAL.md](PrismV2/docs/PRISM_V2_PROPOSAL.md) §3.3, motivating the dual-memory $M^{\text{fast}} / M^{\text{slow}}$ design). The mapping:

| FS-RNN | PRISM v2 / user's program |
|---|---|
| Slow cell $S$, one per layer | $M^{\text{slow}} \in \mathbb{R}^{B \times C_M^{\text{slow}} \times 6 \times 6}$ (V2-paired) |
| Fast chain $F_1 \dots F_k$, $k=2$ or $4$ | $M^{\text{fast}} \in \mathbb{R}^{B \times C_M^{\text{fast}} \times 12 \times 12}$ (V1-paired); single fast cell, not a chain |
| Both update every step | Both update every step (no hard $T$-step gating, unlike HRM) |
| Timescale separation is *emergent* | Soft separation enforced by chrono-init gate biases ($b_u^{\text{fast}} = -1$, $b_u^{\text{slow}} = -3$) |
| $F_1 \to S$ coupling: $F_1$'s output is $S$'s input | Pooled V1 prediction error $E_{V_1}$ drives slow GRU ([PrismV2/docs/PRISM_V2_PROPOSAL.md](PrismV2/docs/PRISM_V2_PROPOSAL.md) §3.7) |
| $S \to F_2$ coupling: $S$'s state input to next Fast cell | Slow-FiLM: $M^{\text{slow}}_{t-1}$ upsampled and modulates V1 features (§3.4) |
| Deep transition chain $F_2 \to F_3 \to \dots \to F_k$ | No deep transition chain in PRISM v2 |

**Three implications for the user's program:**

1. **The "emergent slow timescale" is empirical evidence that PRISM v2's softer mechanism can work.** FS-RNN imposes *no* explicit slow-update rule and the Slow cell still ends up being slow (Fig. 4). This is direct empirical support for PRISM v2's chrono-init soft-bias approach over HRM's hard-$T$-cycle approach — at least in the regime of small character-LM tasks. The corresponding sentence in `concepts/slow_fast_recurrence.md` ("the slow module still consumes per-step compute even though most updates are no-ops") is a feature, not a bug: it's exactly what FS-RNN does, and FS-RNN works.

2. **The deep-transition Fast chain is a primitive the user's program does not currently use.** In FS-RNN, the chain $F_2 \to F_3 \to \dots \to F_k$ gives the input-to-output map up to $k$-layer effective depth *within one input step*, distinct from cross-step recurrence. The user's GridCell RNN ([threads/the_user_architectural_program.md](research_db/threads/the_user_architectural_program.md) §2) currently has one SIP + one FT integration per step. Inserting a depth-$k$ chain of Fast updates before the FT integration is an architectural variant worth considering — particularly if PRISM v2 underperforms on tasks (like character LM) where deep-transition models excel.

3. **Per-character-position adaptation is a missing benchmark for the user's program.** Fig. 5's per-character-position BPC plot is exactly the kind of fine-grained dynamic-adaptation measurement that would distinguish the user's program from baseline RViT / PRISM models. For the change-detection or video-VAE tasks, the analogous measurement would be per-event-onset prediction error: does the architecture absorb the new event faster than a baseline? PRISM v2's slow-FiLM modulation gives the slow memory a way to bias the fast module's next prediction — but does this actually translate to faster post-onset recovery? This is testable and underspecified.

4. **The diagnostic methodology travels cleanly.** The three Fig. 3–5 diagnostics — long-range gradient norm $\|\partial L_t / \partial c_{t-k}\|$ as a probe of effective memory horizon, mean-squared per-step state change as a probe of empirical timescale, and per-position loss as a probe of dynamic adaptation — are exactly the right diagnostics to apply to the user's three-memory stack to verify that the program's claimed timescale ordering actually obtains. They cost very little to implement on top of an already-trained model. This is a concrete recommendation for any v2 ablation: report these three figures alongside the change-detection F1 number.

**Relation to HRM (`papers/wang2025_hierarchical_reasoning_model.md`).** FS-RNN and HRM are the bookends of a design spectrum. FS-RNN imposes no hard timescale separation but achieves an emergent one; HRM imposes a hard $T$-step cycle and forces $L$ to converge between $H$ updates. PRISM v2 sits between them with soft gate-bias separation (chrono-init). The two papers together delimit the space the user's program has to choose within. The empirical question — emergent vs imposed timescale separation — is one of the open questions in `concepts/slow_fast_recurrence.md` and FS-RNN's positive result is an existence proof for the emergent-only end of the spectrum.

**Direct line to PRISM v2 §3.3 wording.** The proposal says the slow/fast memory design is motivated by "Mujika et al. 2017 and Tallec & Ollivier 2018." This entry is the verified-from-PDF anchor for the Mujika half of that claim. The other half is captured in `papers/tallec_ollivier2018_chrono_init.md` (stub).

## 8. Citations to follow

- `chung2016_hierarchical_multiscale_rnn` — HM-RNN, the closest multiscale-RNN predecessor; baseline in Tables 1 and 2 (HM-LSTM 1.24 / 1.32 BPC). Add to seed.
- `koutnik2014_clockwork_rnn` — Clockwork RNN, the canonical hard-update-rate multiscale baseline; FS-RNN cites it as a multiscale ancestor. Add to seed.
- `pascanu2013_deep_recurrent` — deep-transition RNN, the deep-transition ancestor; cites the empirical analysis FS-RNN follows. Add to seed.
- `zilly2016_recurrent_highway_networks` — RHN, the strongest deep-transition baseline; RHN depth-10 1.30 BPC on enwik8. Add to seed.
- `el_hihi_bengio1995_hierarchical_rnn` — early hierarchical-RNN with frequency separation; one of the program's intellectual roots. Add to seed.
- `schmidhuber1992_history_compression` — early multiscale architecture (higher layer updates only on prediction errors of lower layer); a clear ancestor of error-gated update concepts the user's program uses. Add to seed.
- `ha2016_hypernetworks` — HyperLSTM baseline (1.219 / 1.340 BPC); the second-strongest prior result. Add to seed.
- `krueger2016_zoneout` — Zoneout regularization, used in FS-RNN's training recipe; methodologically relevant. Add to seed.
- `ba2016_layer_normalization` — layer norm, used throughout; in seed via other papers.
- `graves2016_act` — adaptive computation time; referenced as a deep-transition analog. In seed.
- `lin1996_narx_rnn` and `dipietro2017_narx_revisited` — NARX RNNs suggested as plausible Slow-cell substitutes; would inform a long-term-memory variant of PRISM v2's slow module.
- `jing2016_eunn` — tunable unitary RNN, the other plausible Slow-cell substitute the authors call out.
- `rocki2016_surprisal_zoneout` — Surprisal-driven Zoneout, a methodological cousin (1.31 BPC on enwik8 / 64M).
- `mikolov2012_subword_lm` — establishes the PTB character-level split FS-RNN follows. Methodologically load-bearing for reproducibility.
