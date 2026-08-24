---
id: pleines2022_recurrent_ppo
title: "Generalization, Mayhems and Limits in Recurrent Proximal Policy Optimization"
authors:
  - "Pleines, Marco"
  - "Pallasch, Matthias"
  - "Zimmer, Frank"
  - "Preuss, Mike"
year: 2022
venue: "arXiv:2205.11104"
doi: "10.48550/arXiv.2205.11104"
arxiv: "2205.11104"
url: "https://arxiv.org/abs/2205.11104"
tags:
  - reinforcement-learning
  - recurrent-networks
  - deep-learning
  - methodology
concepts:
  - ppo
  - actor-critic
  - gae
  - lstm-cell
  - gru-cell
  - recurrent-attention
related:
  - schulman2017_ppo
  - schulman2016_gae
  - mnih2014_recurrent_attention
  - hochreiter_schmidhuber1997_lstm
  - vaswani2017_attention
  - sutton_barto2018_rl_intro
  - cho2014_gru
relevance_to:
  - recurrent_vit
  - prism_v1
  - prism_v2
seed_source:
  - thesis_md
status: full
depth: full
last_updated: "2026-05-16"
---

# Generalization, Mayhems and Limits in Recurrent Proximal Policy Optimization

## 1. Abstract

At first sight it may seem straightforward to use recurrent layers in Deep Reinforcement Learning (DRL) algorithms to give agents memory in partially observable settings. Starting from Proximal Policy Optimization (PPO), the authors highlight four implementation details that must be gotten right when adding recurrence: (i) properly shaping the neural net's forward pass, (ii) arranging the training data into fixed-length sequences from variable-length episodes, (iii) selecting the correct hidden state at the beginning of each sequence, and (iv) masking padding positions when computing the loss. They contribute a documented baseline implementation (`recurrent-ppo-truncated-bptt`) and two novel POMDP environments — Mortar Mayhem and Searing Spotlights — that stress memory beyond simple capacity / distraction. Empirically they show that on Mortar Mayhem a strong-generalization regime is reached, but only by scaling the number of training seeds to 1000; on Searing Spotlights, recurrent PPO fails entirely. Refreshing stale hidden states and advantages between epochs does not provide a gain that justifies its compute cost.

## 2. Why this matters for us

The published Recurrent ViT (2502.10955) and PRISM v1 are trained with recurrent PPO. Pleines et al. are the most careful published account of *what specifically goes wrong* when one drops a recurrent layer into a vanilla PPO loop and trains on a partially observable visual task — i.e., the exact training regime our published change-detection results were obtained in. The four "fundamental implementation details" they isolate (forward-pass shaping, episode-to-sequence splitting, hidden-state selection for sequence starts, padding masking) are load-bearing for whether a recurrent PPO run learns anything at all, and Figure 1 of the paper shows that *failing to mask paddings* still yields a curve that looks plausible — a silent correctness failure. This is directly relevant to (a) interpreting our PRISM v1 / Recurrent ViT training curves, (b) the architectural-stability question for PRISM v2 (which adds more recurrent state), and (c) any future scaling effort.

## 3. Key claims

1. Adding a recurrent layer to PPO is not plug-and-play: four implementation issues must be resolved — efficient forward-pass organization, splitting collected trajectories into fixed-length sequences with zero-padding, correctly sampling the initial hidden state of each sequence (the output hidden state of the previous sequence is the input hidden state of its consecutive one), and masking the padded positions in the loss.
2. Low-scale debugging environments (e.g., CartPole with velocity removed) can give misleadingly "good" curves even with bugs — Figure 1 shows un-masked-padding training reaches ~190 IQM return while the correct masked-padding training reaches the same plateau, hiding the bug at low scale.
3. The authors release a fully-documented baseline implementation with truncated BPTT support (Algorithm 1; code at `github.com/MarcoMeter/recurrent-ppo-truncated-bptt`).
4. Two new POMDP environments — Mortar Mayhem and Searing Spotlights — stress memory beyond simple cue retention. Mortar Mayhem requires *continuously modifying* memory to track which commands have already been executed; Searing Spotlights requires the agent to infer its own location from past observations because the lights go out.
5. **Generalization on Mortar Mayhem requires 1000 training seeds.** With 200 seeds the IQM return on novel seeds collapses to ≤ 0.2; with 500 seeds it reaches ≈ 0.6; with 1000 seeds it reaches ≈ 1.0. This is a "transition to strong generalization" effect with respect to seed count.
6. **The ballet environment (Lampinen et al. 2021) does *not* show this transition.** Training-seed scaling from 500 → 1000 yields no improvement; performance on novel seeds remains near chance even though training-seed performance is near perfect. Generalization-via-seed-scaling is task-dependent, not universal.
7. **Recurrent PPO fails on Searing Spotlights.** Even after ablating spotlight penalties, limiting coins to one, scaling up the agent and coin sizes, freezing spotlights, or making the agent permanently visible, none of the configurations except heavily simplified ones (stationary lights with a scaled-up agent) yield successful training. The authors hypothesize a transformer-style episodic memory (like Lampinen et al.'s Hierarchical Chunk Attention Memory) is required.
8. Refreshing stale hidden states and advantages between optimization epochs gives at most a marginal improvement on Mortar Mayhem and ballet, not enough to justify the extra forward pass on the entire data. This contradicts Ndousse (2020)'s claim of benefit and partially contradicts Andrychowicz et al. (2021) for advantage recomputation under on-policy training.
9. GRU was slightly more effective than LSTM in the trained environments (per the grid search reported in Appendix D); this is a small effect and probably environment-dependent.

## 4. Methods

**Recurrent PPO.** The agent is trained with the standard PPO clipped surrogate objective $L^{C}_t(\theta) = \mathbb{E}_t [\min(q_t(\theta)\hat A_t, \text{clip}(q_t(\theta), 1-\epsilon, 1+\epsilon)\hat A_t)]$ where $q_t(\theta) = \pi_\theta(a_t \mid o_t, h_t) / \pi_{\theta_\text{old}}(a_t \mid o_t, h_t)$. Advantages are computed via GAE. The combined loss is $L^{CVH}_t = L^C_t - c_1 L^V_t + c_2 \mathcal{H}[\pi_\theta](o_t)$ with $L^V_t = (V_\theta(o_t, h_t) - V^{\text{targ}}_t)^2$.

**The four implementation issues (§3.1 of the paper).**

1. *Data preprocessing pipeline* (Figure 2). Sampled trajectories of shape `[W workers, T steps]` are split into episodes of varying length, then split again into sequences of *fixed length* (`sequence_length` hyperparameter), and finally zero-padded so all sequences have the same length `max(#T)`. Minibatches sample multiple sequences from the resulting tensor.
2. *Forward-pass shaping* (Figure 3). Non-recurrent layers operate on the full flat batch `batch_size = workers × steps` for efficiency. Before the recurrent layer the batch is reshaped to `[#sequences, sequence_length]`; after the recurrent layer it is reshaped back. For trajectory sampling (acting in the environment) the sequence length is 1.
3. *Hidden state initialization at sequence starts.* The output hidden state of one sequence is fed in as the input hidden state of its consecutive sequence — this is the truncated-BPTT approach. This requires keeping track, for each sequence, of *which* prior sequence it followed (since episodes have been split into multiple sequences and possibly extended across worker steps).
4. *Padding masking in the loss.* Padded positions must not contribute to gradient. Define $\text{mask}_t = 1$ where padding is not used and 0 where padding is used; the masked loss is $L^{\text{mask}}(\theta) = (\sum_t \text{mask}_t \cdot L^{CVH}_t) / \sum_t \text{mask}_t$.

**Optional refreshing of stale hidden states and advantages (§3.2 of the paper).** Once the parameters have been updated by at least one minibatch, subsequent minibatch updates of the current iteration operate on stale data. Andrychowicz et al. (2021) found that recomputing advantages each epoch helps in continuous-control PPO. Pleines et al. extend this to also recompute hidden states. Algorithm 1 includes an optional `if epoch > 0` step that recomputes both with respect to the current θ. Empirically (Figures 9, 10) this is at most marginally helpful and is not worth the compute.

**Network architecture (Figure 3).** Visual observation `o_t` (84 × 84 × 3 pixels for Mortar Mayhem / Searing Spotlights) goes through three conv layers (32 filters/size 8/stride 4 → 64 filters/size 4/stride 2 → 64 filters/size 3/stride 1). Flattened conv features are concatenated with a vector-observation encoding (FC-128) that includes `o_t`, last action `a_{t-1}` (one-hot), and last reward `r_{t-1}`. The concatenated feature is reshaped to sequences for the GRU/LSTM (hidden size 512), then reshaped back to batch. Two FC-512 heads emit value and policy logits (one head per action dimension for multi-discrete spaces).

**Truncated BPTT (Algorithm 1).** For each iteration: each of W workers runs π_{θ_old} for T steps; advantages are computed; trajectories are split into episodes and into fixed-length sequences (or kept as episodes if `fixed_sequence_length = False`); short sequences are zero-padded; initial hidden states for each sequence are selected from the previous sequence's terminal hidden state. Then for each epoch and minibatch (M ≤ W·T), the masked loss $L^{\text{mask}}(\theta)$ is optimized.

**Training hyperparameters (Table 1, Mortar Mayhem column).** Seeds: 1000; visual obs 84 × 84 × 3; vector obs dim 490+4+1 (one-hot grid + last-action + last-reward); 4 actions; vector encoder size 256; 32 workers; batch size 16384; 4 epochs; LR initial 3e-4 decaying to 3e-5; entropy coefficient initial 0.1 decaying to 1e-4; sequence length = full episode (Max); discount γ = 0.99; GAE λ = 0.95; worker steps 512; 8 minibatches; value-loss coeff c_1 = 0.25; max grad norm 0.5; clip range 0.2; hidden state size 512; recurrent layer GRU; ReLU; AdamW.

## 5. Results

**CartPole-POMDP sanity check (Figure 1).** Both "Loss Padding Masked" and "Loss Padding Not Masked" reach IQM ≈ 195 at 800K steps; "No Recurrence" plateaus at ≈ 50. The point is that the bug (un-masked paddings) is *not* detectable from training curves on this scale — a methodological warning, not a quantitative result.

**Mortar Mayhem Act Only Task (Figure 6).** With recurrence: IQM = 1.0 by ~20M steps. Without recurrence (six different ablations of which inputs to use, including last action, last reward, both, plus visual variants): all plateau at IQM ≈ 0.2–0.3 by 40M steps. *Recurrence is necessary*; supplying last action / last reward as inputs to a non-recurrent net is not a substitute.

**Mortar Mayhem generalization (Figure 8).** Trained on 200 seeds: 200-Seeds(Train) IQM ≈ 0.2 by 50M steps, novel = ~0.15. Trained on 500 seeds: train IQM = 1.0, novel IQM = ~0.55. Trained on 1000 seeds: train and novel IQM ≈ 1.0. *Transition to strong generalization at 1000 seeds.*

**Mortar Mayhem command-count scaling (Figure 11).** Training on 10, 20, 30 commands: 10 commands → train IQM 1.0 / novel ≈ 0.95 by ~40M steps; 20 commands → train ≈ 0.95 / novel ≈ 0.65 by ~80M steps; 30 commands → train ≈ 0.85 / novel ≈ 0.55 by ~80M steps. Highest possible returns for 20 and 30 commands are 2.0 and 3.0 respectively; neither is reached. The limit appears to be model scale and compute time, not the algorithm.

**Ballet environment (Figure 7).** 2 dances: train IQM ≈ 1.0 / novel ≈ 0.95. 4 dances: train ≈ 0.95 / novel ≈ 0.55. 8 dances: train ≈ 0.95 / novel ≈ 0.1. *No "transition to strong generalization" effect with seed scaling 500 → 1000.*

**Stale hidden-state and advantage refreshing (Figures 9, 10).** On Mortar Mayhem novel seeds, refreshing every other epoch (4 epochs, refresh modulo 2 == 0) reaches IQM ≈ 1.0 slightly faster than no refresh, but no refresh also reaches 1.0; 8 epochs degrades performance to IQM ≈ 0.4. On ballet 8 dances, "no refresh" reaches train IQM ≈ 1.0 while "3 epochs % 1 == 0" achieves ≈ 0.6. *Refreshing is at best marginal and at worst harmful.*

**Searing Spotlights.** Recurrent PPO fails completely. Only after removing spotlight penalties, limiting coins to one, freezing spotlights, *and* scaling the agent / coin up by 2-3× does any learning occur; moving spotlights at original scale remain unsolved across all configurations tried.

## 6. Critique / limitations

The paper's central methodological contribution — the four implementation details — is presented without an explicit ablation of each detail in isolation. The Figure 1 CartPole comparison demonstrates that padding-masking matters, but the other three (forward-pass reshape, episode-to-sequence splitting, hidden-state carry-over) are described rather than ablated separately. The reader has to trust that all four are independently necessary.

The Searing Spotlights failure analysis is qualitative. The authors hypothesize a transformer-based episodic memory would solve it but do not test this. Given that PRISM v1 / v2 explicitly add memory architectures more elaborate than a single GRU, this is precisely the regime the user's program targets — but the paper does not provide a quantitative target to beat.

The "transition to strong generalization at 1000 seeds" claim on Mortar Mayhem is established with five training runs per condition (per the paper's IQM/CI methodology citing Agarwal et al. 2021). The transition is sharp in the reported figure but the statistical reliability of the *transition point* itself (200 vs 500 vs 1000) is not separately characterized; intermediate seed counts (e.g., 700) are not reported.

GRU > LSTM is stated as a result of grid search in Appendix D, but the effect size is described as "slightly." The conclusion does not generalize to other environments or other recurrent units (e.g., xLSTM, Transformer attention, or the user's GridCell RNN).

The recommendation to *not* refresh stale hidden states contradicts Ndousse (2020) directly, with the difference attributed to environment-space complexity. This contradiction is acknowledged but not fully resolved; it may matter for very long episodes or off-policy regimes the paper does not test.

The treatment of hidden-state *initialization at the start of an episode* (zero init vs learned init vs Kapturowski-style burn-in) is acknowledged as open in §6.4: "Making the initial states learnable parameters as part of θ is non-trivial, because gradients are truncated and therefore cannot be backpropagated to the hidden states' origin." This is a methodologically relevant gap: PRISM v1/v2 currently use zero initialization, and the paper does not provide guidance on alternatives.

The paper does not discuss reward-shaping or curriculum-learning interactions with recurrence. In the user's published work on change detection, reward sparsity and episode length are likely interacting with whatever staleness or truncated-BPTT effects this paper identifies; the bridge between the two settings is not made by the paper.

## 7. Connection to our work

This paper is the single most direct piece of methodological prior art for the *training* component of both the Recurrent ViT (2502.10955) and the PRISM family (`Prism/docs/THESIS.md`, `PrismV2/docs/PRISM_V2_PROPOSAL.md`). Specific connections:

| Pleines et al. recommendation | Our training setup |
|---|---|
| Mask padded positions in the loss (§3.1, Eq. 3) | Recurrent ViT and PRISM v1 must use the same masking when episodes are split into fixed-length sequences. If either implementation skipped this, training curves would still appear plausible (per the paper's Figure 1) but gradients would be biased. This warrants verification in our codebase. |
| Carry hidden state from sequence to consecutive sequence within an episode | Truncated BPTT in our setup must respect episode boundaries. PRISM v1's inner-loop inference (`THESIS.md` §2.8) operates within an episode; the outer recurrent-PPO loop is the relevant boundary. |
| Reshape batch before/after the recurrent layer; act with sequence length 1 | The Recurrent ViT's published forward pass is single-step at acting time, multi-step at training time. This is the same pattern. |
| GRU ≥ LSTM in their environments | Our published work uses LSTM-style memory. Pleines's GRU preference is small and environment-dependent; not a strong signal to switch, but a data point. |
| Refreshing stale hidden states / advantages not worth the compute | PRISM v1 and v2 currently do not refresh. The paper's result supports this choice. PRISM v2 with three memory compartments would be especially expensive to refresh and should not adopt this. |
| 1000 training seeds for generalization on Mortar Mayhem | Change detection benchmarks in 2502.10955 are evaluated on held-out video clips, not seed-scaled procedural environments. The relevant analog is held-out scene/clip count. If our generalization curves flatten with seed count, the analog of Pleines's 200-seed failure is relevant. |

**Specific implications for PRISM v2.** PRISM v2 (`PRISM_V2_PROPOSAL.md` §3.3) introduces a slow/fast dual memory with chrono-init (slow-bias $b_u^{\text{slow}} = -3$, fast-bias $b_u^{\text{fast}} = -1$). The training pipeline is still recurrent PPO. Pleines et al.'s four-issue checklist therefore applies to PRISM v2 verbatim, with one new wrinkle: the slow update happens stochastically and infrequently. Truncated BPTT must therefore carry *both* memory states across sequence boundaries; mis-handling either is the same class of silent correctness failure as the unmasked-padding bug. Algorithm 1 of the paper is the right starting template; PRISM v2 needs an analogous explicit algorithm that lists which states must be carried through which boundaries.

**Specific implications for the Feedback Transformer training.** The user's architectural program (`threads/the_user_architectural_program.md` §1) defines the Feedback Transformer to integrate many recurrent states at the attention layer. When this is trained with PPO, every one of those states is hidden state that must be carried correctly across sequence boundaries. Pleines's complexity-vs-correctness argument compounds linearly with the number of feedback sources. The user has reported up to twelve feedback sources used successfully in the Video VAE — that work was *not* trained with PPO, but if the Feedback Transformer is ever inserted into the PRISM family's PPO loop, Pleines's checklist becomes critical.

**Specific implications for the Searing Spotlights failure.** Pleines's hypothesis that a transformer episodic memory (Lampinen et al. 2021's Hierarchical Chunk Attention Memory) is required for Searing Spotlights is interesting because the user's program already commits to attention-based recurrent memory at every level. PRISM v2's slow memory state coupled with the Feedback Transformer is, in expressive terms, a closer fit to Lampinen's architecture than vanilla GRU PPO. *Searing Spotlights is therefore a candidate benchmark on which PRISM v2 (or its eventual three-compartment successor) should outperform single-GRU recurrent PPO.* This would be a methodologically clean comparison: identical PPO loop, identical observation space, identical reward — only the recurrent architecture varies.

**Implementation audit recommendation.** The PRISM v1, PRISM v2, and Recurrent ViT codebases should each be checked against Pleines's four-issue list as a one-time audit. The paper's Figure 1 makes clear that a passing training curve is *not* sufficient evidence of correctness for at least one of the four issues. A short audit task is in order.

## 8. Citations to follow

- `schulman2017_ppo` — the underlying PPO algorithm. In seed; should be deepened.
- `schulman2016_gae` — GAE for advantage estimation, used here. In seed; should be deepened.
- `hochreiter_schmidhuber1997_lstm` — LSTM cell, one of two recurrent units compared. In seed.
- `cho2014_gru` — GRU cell, the unit the authors found slightly preferable. Add to seed.
- `andrychowicz2021_what_matters_ppo` — large-scale ablation of PPO design choices; Pleines compares his refreshing results to theirs. Add to seed.
- `engstrom2020_ppo_trpo_implementation_matters` — implementation-details-in-RL ancestor study. Add to seed.
- `hsu2020_ppo_design_choices` — revisits PPO design choices including advantage normalization. Add to seed.
- `kapturowski2019_r2d2` — Recurrent Replay Distributed DQN; introduces burn-in for hidden states. Add to seed.
- `ndousse2020_stale_hidden_states_ppo_lstm` — the blog post Pleines partially contradicts on refreshing. Add to seed as `ndousse2020_ppo_lstm_stale_states` (informal source).
- `lampinen2021_mental_time_travel` — hierarchical chunk attention memory; the architecture Pleines hypothesizes would solve Searing Spotlights; also supplies the ballet benchmark. Add to seed.
- `hausknecht_stone2015_drqn` — Deep Recurrent Q-Network; classic prior work on recurrence + value-based RL. Add to seed.
- `chevalier_boisvert2018_minigrid` — MiniGrid environments, used to implement Mortar Mayhem. Useful for our own benchmarking. Add to seed.
- `fortunato2019_generalization_recurrent_drl` — Memory Task Suite, including ballet. Add to seed.
- `agarwal2021_rliable` — IQM / CI methodology. Add to seed.
- `juliani2018_unity_ml_agents` — ml-agents toolkit, used to implement Searing Spotlights. Add to seed.
