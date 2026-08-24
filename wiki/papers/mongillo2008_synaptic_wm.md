---
id: mongillo2008_synaptic_wm
title: "Synaptic theory of working memory"
authors:
  - "Mongillo, Gianluigi"
  - "Barak, Omri"
  - "Tsodyks, Misha"
year: 2008
venue: "Science"
doi: "10.1126/science.1150769"
arxiv: ""
url: "https://doi.org/10.1126/science.1150769"
tags:
  - theoretical-essay
  - working-memory
  - prefrontal-cortex
concepts:
  - cortical-microcircuit-model
  - recurrence-for-temporal-dynamics
related:
  - masse2019_circuit_wm
  - riley_constantinidis2016_pfc_persistent
  - constantinidis2018_persistent_activity
  - funahashi1989_mnemonic_dlpfc
  - goldman_rakic1995_cellular_wm
  - miller_cohen2001_pfc_function
  - bays2024_wm_representation
  - beck2024_xlstm
  - attwell_laughlin2001_brain_energy_budget
  - laughlin1998_metabolic_cost
  - mujika2017_fast_slow_rnn
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

# Synaptic theory of working memory

> **Taxonomy note.** The natural concept tags for this paper — `synaptic-working-memory` and `activity-silent` — do not exist in TAXONOMY.md. The closest available concepts are `cortical-microcircuit-model` (the paper *is* a microcircuit model of recurrent PFC dynamics) and `recurrence-for-temporal-dynamics` (the mechanism is recurrent-network-mediated temporal maintenance). The persistent-activity counterpart concept (`working-memory-persistent-activity`) does exist; its absence here is *not* an oversight — Mongillo et al.'s contribution is precisely the claim that WM does *not* require persistent activity. Two new concepts should be added to the taxonomy in a future pass: `synaptic-working-memory` (WM held in short-term synaptic facilitation/depression) and `activity-silent-memory` (decodable WM content with near-baseline firing rates).

## 1. Abstract

Mongillo, Barak & Tsodyks propose that working memory (WM) is implemented not by persistent neural firing — the canonical Funahashi–Goldman-Rakic substrate — but by calcium-mediated short-term synaptic facilitation in the recurrent connections of neocortical networks. In their account, the residual presynaptic calcium left in the terminal of a spike serves as a slowly-decaying buffer that can be loaded by a brief burst of spiking activity, sustained passively by its own kinetics for hundreds of milliseconds to seconds, and read out by a subsequent probe of network activity. Because the facilitation lives in the synapse rather than in the neuron, the network can be metabolically quiet during the delay — firing rates can return to baseline while the memory persists in the dynamic state of the synaptic efficacies. The model further shows that the duration and stability of the memory are controlled by network spontaneous activity, with the spontaneous rate acting as a "refresh" signal that periodically reinjects spikes into the cortical recurrent loop, replenishing the facilitated efficacies before they decay. The proposal offers a thermodynamically cheap, biophysically grounded alternative to persistent activity and is the foundational citation for the *activity-silent* family of WM theories (Stokes 2013, 2015; Wolff et al. 2017) that has dominated the modern WM debate.

## 2. Why this matters for us

Mongillo et al. 2008 is the foundational reference for the *activity-silent* / synaptic-WM hypothesis — the principled challenger to the persistent-activity orthodoxy that the user's architectural program builds on (Funahashi 1989; Goldman-Rakic 1995; Riley & Constantinidis 2016; Constantinidis 2018). For the user's research program, this paper supplies the biological rationale for a second, *slow synaptic-like* memory channel coexisting with a *fast activation-like* channel — exactly the architectural commitment made explicit in PRISM v2's slow/fast memory split (`PRISM_V2_PROPOSAL.md` §3.3), implicit in the Recurrent ViT's hidden state $H^{(t-1)}$ vs accumulated weight updates, and central to the xLSTM matrix memory and Mujika 2017 fast-slow RNN that the user's program cites. Mongillo et al. is also load-bearing for the user's `competition-emergent-predictive-coding` thesis: the activity-silent framing implies that competition between neural coalitions need not be encoded in instantaneous firing rates but can also live in slowly-varying synaptic state — which dramatically expands the architectural space in which "competition" could be implemented.

## 3. Key claims

1. **Short-term synaptic facilitation (STSF) can sustain WM-like content without persistent spiking.** A recurrent network with calcium-mediated presynaptic facilitation can store stimulus-selective information in its synaptic efficacies through a delay during which firing rates return to spontaneous baseline.
2. **Residual presynaptic calcium is the physical substrate of the silent memory.** Each spike leaves a small amount of $\text{Ca}^{2+}$ in the terminal; this calcium decays on a timescale of $\tau_F \sim 1.5$ s and enhances release probability for subsequent spikes. The slow kinetics give the memory its long-time-constant.
3. **The memory is "loaded, refreshed, and read out by spiking activity."** A brief burst of selective spiking at encoding loads the calcium buffer; subsequent spontaneous activity periodically refreshes the buffer (preventing decay); a probe input triggers a population response that decodes the stored content.
4. **Spontaneous activity controls memory duration and stability.** The model exhibits regimes in which the spontaneous firing rate sets the effective decay time of the synaptic memory: too low and the calcium decays before readout; too high and the memory becomes diffuse. There is an intermediate "refreshing" regime that maximizes maintenance.
5. **The mechanism is metabolically efficient.** Because firing rates during the delay can approach baseline, the network avoids the metabolic cost of persistent spiking (Laughlin et al. 1998; Attwell & Laughlin 2001) — a substantial energetic saving relative to bump-attractor / line-attractor persistent-activity models.
6. **The mechanism is robust to perturbations of the firing-rate state.** Distractors and transient firing-rate perturbations during the delay leave the synaptic memory largely intact, because the synaptic state changes on a slower timescale than the firing-rate state.
7. **Multiple items can be stored simultaneously without crosstalk.** Because each stored item occupies its own subset of synapses (those connecting the neurons selective for that item), capacity is set by the number of separable synaptic subpopulations rather than by firing-rate interference.
8. **Population-Up states and oscillations can emerge naturally from STSF.** Network spontaneous activity in the model exhibits transient population bursts ("PSs") whose frequency and amplitude are gated by the stored synaptic facilitation — a falsifiable prediction that subsequent work (Lundqvist et al. 2016, 2018) has partially confirmed via beta/gamma burst dynamics in PFC.

## 4. Methods

**Network architecture.** A randomly-connected recurrent network of leaky integrate-and-fire (LIF) excitatory and inhibitory neurons; sparse connectivity; conductance-based synapses. Selective subpopulations encode stimulus identity via stronger-than-random intra-population recurrent connections (Hebbian-imprint of training stimuli, in the spirit of Amit-Brunel attractor networks).

**Short-term synaptic plasticity.** Following the Markram–Tsodyks tradition, each recurrent excitatory synapse has two dynamic variables:
- $u(t)$ — fraction of resources released per spike, equivalent to presynaptic calcium-controlled release probability. Facilitates with each spike: $u \to u + U(1 - u)$. Decays back to baseline with time constant $\tau_F \sim 1.5$ s.
- $x(t)$ — fraction of available resources (vesicles). Depletes with each release: $x \to x(1 - u)$. Recovers with time constant $\tau_D \sim 200$ ms.

Synaptic efficacy is the product $u \cdot x$. In the facilitation-dominated regime ($\tau_F \gg \tau_D$), each spike incrementally raises $u$, and a stimulus-loaded burst leaves $u$ elevated on the engaged subpopulation for $\sim 1.5$ s — the substrate of the silent memory.

**Memory protocol.** (i) Encoding: a brief external input drives the selective subpopulation, causing a burst of firing that elevates $u$ on the intra-population synapses. (ii) Delay: the external input is removed; firing rates return toward spontaneous baseline; the elevated $u$ persists. (iii) Readout: a non-specific "probe" input is delivered to the whole network; the previously-loaded subpopulation responds disproportionately because of its elevated synaptic efficacies, revealing the stored identity.

**Refreshing dynamics.** Spontaneous spikes in the loaded subpopulation periodically replenish $u$, preventing decay below the readout threshold. This is the central role of network spontaneous activity in the model — it is not noise to be suppressed but a functional refresh mechanism. The authors derive a mean-field expression for the steady-state $u$ as a function of the spontaneous rate $\nu$ and identify the regime of robust maintenance.

**Analyses.** Simulations of the LIF network supplemented by mean-field reductions in which the synaptic state is replaced by its population average. The mean-field analysis identifies bifurcation parameters that govern transitions between (i) no maintenance, (ii) silent maintenance with intermittent refresh, and (iii) full persistent activity.

## 5. Results

- **Silent maintenance during the delay.** After encoding, the firing rate of the loaded subpopulation returns to within a few Hz of the spontaneous rate (typically $\sim 3$ Hz) while $u$ remains elevated at $\sim 0.4$–$0.6$ versus a baseline $U \sim 0.15$. Memory content is decodable from the synaptic state but not (or only weakly) from firing rates.
- **Memory lifetime.** Without spontaneous activity, the calcium-mediated facilitation decays with $\tau_F \sim 1.5$ s — long enough for typical WM delays but not indefinitely sustainable. With spontaneous activity in the refreshing regime, the effective lifetime extends to many seconds and is limited by the depression timescale $\tau_D$ rather than by $\tau_F$.
- **Distractor robustness.** Transient strong inputs to non-selective neurons during the delay perturb firing rates but leave the synaptic memory of the loaded population largely intact; the network re-converges to the loaded state once the distractor is removed.
- **Multi-item capacity.** The model successfully stores 2–3 items simultaneously, with capacity limited by synaptic-subpopulation interference and by overall network dynamics rather than by firing-rate interference. Capacity scales differently from persistent-activity models, which is a distinguishing empirical prediction.
- **Population-spike dynamics.** During the silent maintenance phase, the network exhibits transient "population spikes" — synchronized bursts in the loaded subpopulation — whose frequency increases with stored content. This is a directly testable prediction; subsequent PFC recordings (Lundqvist et al. 2016) have observed gamma/beta bursts whose statistics match aspects of this prediction.
- **Metabolic efficiency.** The mean firing rate during the delay is $\sim 1/10$th to $\sim 1/3$ that of equivalent persistent-activity models (Compte et al. 2000; Wang 1999), implying a comparable reduction in metabolic cost (since spiking dominates cortical energy consumption per Attwell & Laughlin 2001).

## 6. Critique / limitations

The model's success in pure-maintenance scenarios is genuine and important, but several limitations have been catalogued by the subsequent decade of work:

The mechanism is specifically tailored to *recognition-style* maintenance — hold a representation, compare it to a probe. It does not support graded recall (drift-diffusion-style continuous decoding from synaptic state has not been demonstrated), prospective recoding (transforming the stored stimulus into the upcoming response, à la DMRS), or active manipulation. Masse et al. 2019 ([masse2019_circuit_wm](masse2019_circuit_wm.md)) shows that as soon as the task demands manipulation rather than pure maintenance, persistent activity re-emerges; Mongillo's silent mechanism alone is insufficient.

The model assumes that stimulus-selective recurrent subpopulations have been pre-wired by Hebbian learning before the WM protocol begins. The plasticity that learns these subpopulations operates on a slower timescale (synaptic LTP/LTD) and is outside the scope of the model. For arbitrary novel stimuli — including the random patterns used in many human WM experiments — the silent-maintenance mechanism cannot operate without first having Hebbian-imprinted the relevant subpopulations. Bays 2024 ([bays2024_wm_representation](bays2024_wm_representation.md)) and the broader human WM literature put pressure on this assumption.

The model's "silent" delay is silent only on average; transient population spikes occur sporadically. Whether these bursts are the same phenomenon as the gamma/beta bursts observed empirically (Lundqvist et al. 2016, 2018) is unclear; the model's bursts arise from depression-recovery dynamics in the loaded subpopulation, while the empirical bursts may have additional oscillatory machinery (E-I rhythm, thalamocortical pacing). Riley & Constantinidis 2016 ([riley_constantinidis2016_pfc_persistent](riley_constantinidis2016_pfc_persistent.md)) note that even when mean rates are near baseline, *single-cell* persistent firing in a small subset is often present — i.e., the empirical evidence for genuine silence is weaker than the model assumes.

The calcium timescale $\tau_F \sim 1.5$ s is at the upper end of presynaptic calcium decay constants measured in cortical synapses. Some preparations show $\tau_F \sim 200$–500 ms, which would shorten the silent-maintenance window substantially. The model's predictions are timescale-dependent in ways that empirical refinement of $\tau_F$ measurements directly stress-tests.

The model does not address how the silent synaptic state interfaces with downstream readout — i.e., how a motor or decision circuit can convert the elevated $u$ back into the kind of firing-rate response that drives behavior. The "probe" input is exogenous and unexplained; in a real WM task, the analog of the probe is itself a recurrent network signal whose origin and timing the model leaves underspecified.

Finally, the model is *complementary* to persistent activity, not a replacement. The modern synthesis — Masse 2019 ([masse2019_circuit_wm](masse2019_circuit_wm.md)) — is that both substrates coexist in a hybrid code whose mix is set by task demand. Mongillo's most important contribution is to have established that the synaptic substrate is *possible*; the empirical question of when it is *actual* is what the post-2008 literature has been working out.

## 7. Connection to our work

Mongillo, Barak & Tsodyks 2008 is the foundational citation for the slow synaptic-like memory channel in the user's architectural program, and the principled challenger to the active-recurrent commitment that the program also makes. Its role is therefore complementary to that of Riley & Constantinidis 2016 ([riley_constantinidis2016_pfc_persistent](riley_constantinidis2016_pfc_persistent.md)) and Constantinidis 2018 ([constantinidis2018_persistent_activity](constantinidis2018_persistent_activity.md)): both sides of the persistent-vs-silent debate are load-bearing for the program because the program commits to *both* substrates simultaneously rather than picking a side.

**PRISM v2's slow/fast memory split.** PRISM v2 (`PRISM_V2_PROPOSAL.md` §3.3) commits to two coupled recurrent states: a fast memory $M^{\text{fast}}$ that updates every step (analog of persistent firing-rate dynamics, à la Riley-Constantinidis) and a slow memory $M^{\text{slow}}$ with a low per-step update probability $\sim 0.05$ (analog of Mongillo's synaptic facilitation). Mongillo provides the biological justification for the slow channel: its timescale ($\tau_F \sim 1.5$ s), its metabolic motivation (avoid persistent spiking cost), and its functional role (distractor-resistant maintenance through delay periods) all map directly onto the architectural commitments PRISM v2 makes. The dual-timescale Mujika 2017 / Tallec & Ollivier 2018 citations that motivate the PRISM v2 slow/fast structure on the ML side find their cortical analog in Mongillo's synaptic vs. persistent dichotomy.

**The recurrent ViT's hidden state vs accumulated weight updates.** The Recurrent ViT (2502.10955, §6.7) maintains a per-token hidden state $H^{(t-1)}$ that is the analog of the *persistent-activity* substrate — instantaneous, gradient-trainable, firing-rate-like. The model's frozen weights are *not* updated during inference. Mongillo's contribution motivates a future architectural extension: introduce a fast-Hebbian or fast-modifying weight layer (e.g., the Schmidhuber 1992 fast weights, the Schlag/Irie/Schmidhuber 2021 linear-transformer-as-fast-weights, or the xLSTM matrix memory mentioned in the user's notes) that acts as the synaptic-facilitation analog. The pairing of a slow plastic weight channel and a fast activation channel is exactly the architectural prescription Mongillo's biology supports.

**Connection to xLSTM matrix memory (beck2024_xlstm).** The xLSTM mLSTM variant introduces a matrix-valued memory state that is updated via outer products of key and value vectors — a learned fast-Hebbian rule that lives in a memory matrix rather than in the hidden activations. This is the cleanest ML analog of Mongillo's synaptic-facilitation memory: the outer-product update is structurally identical to the Hebbian increment to $u$ that occurs whenever a presynaptic spike co-occurs with elevated postsynaptic activity. The user's program should track xLSTM (and the broader linear-transformer / fast-weights literature) as the engineering counterpart to Mongillo's biological proposal.

**Connection to Mujika 2017 fast-slow RNN.** The Mujika et al. 2017 fast-slow LSTM (cited in `PRISM_V2_PROPOSAL.md` §3.3) explicitly maintains two coupled recurrent units with different timescales of update. This is the ML-side citation for the same architectural commitment that Mongillo motivates on the biology side. Mongillo's contribution to this connection is to assert that the slow channel is properly synaptic — i.e., it should be implemented as a plastic-weight update rather than as a slow gated hidden state. PRISM v2's slow $M^{\text{slow}}$ takes a *gated hidden-state* form rather than a *plastic-weight* form; whether the latter would yield qualitatively different behavior is an open architectural question that Mongillo's framing invites.

**Connection to Masse 2019.** Masse et al. 2019 ([masse2019_circuit_wm](masse2019_circuit_wm.md)) directly closes the persistent-vs-silent debate node by training a recurrent network with Mongillo-style STSP and demonstrating that maintenance tasks self-organize into the silent regime while manipulation tasks recruit persistent activity. Mongillo provides the synaptic-kinetics substrate that Masse builds on (the $u \cdot x$ formulation is from the Markram–Tsodyks–Mongillo tradition), and Masse provides the empirical demonstration that Mongillo's silent regime is what a trained network naturally discovers for pure-maintenance tasks. The user's program inherits both: PRISM v2's slow memory is the silent regime; PRISM v2's fast memory is the persistent regime; the task selects the operating regime.

**Implication for the competition-emergent-PC thesis.** The user's `competition-emergent-predictive-coding` concept (`the_user_architectural_program` §5) currently frames inter-coalition competition as a firing-rate phenomenon: hubs compete for control of the self-attention map by modulating Q/K projections of the sensory pathway. Mongillo's activity-silent framing opens an alternative: competition could also be encoded in the *synaptic state* of recurrent connections — slow plastic updates that bias the network's attractor landscape toward one coalition's preferred outcomes without changing instantaneous firing rates. This is a substantive architectural variant the program has not yet explored. It would imply that the predictive-error signals modulating top-down feedback should drive *fast plastic updates* to recurrent weights, not just gating of recurrent activations. xLSTM's mLSTM, Schmidhuber's fast weights, and the Mongillo synaptic substrate are all candidates for the mechanism.

**Implication for the change-detection task.** The change-detection benchmark used by the Recurrent ViT and PRISM is a maintenance-and-comparison task — hold a representation of frame $t-1$, compare to frame $t$. By Mongillo's taxonomy this is a recognition-style task and should be amenable to silent synaptic maintenance. The empirical observation that PRISM v1 (`THESIS.md` §2.4) succeeds with a single ConvGRU memory operating in a slow-update regime is consistent with this prediction. The further prediction — that adding a fast-Hebbian / fast-weights layer to PRISM v1's slow channel should *not* impair, and may improve, change-detection performance — is testable.

**Implication for the Feedback Transformer.** The Feedback Transformer (§1 of the user's program) integrates multiple recurrent states via per-state Q/K/V projections into the attention computation. Mongillo's contribution suggests that at least one of those feedback sources should be a *slow plastic weight* rather than a *fast hidden activation* — i.e., the Q/K projection for one of the feedback sources should be parameterized as a fast-Hebbian-updated matrix rather than as a fixed projection of a recurrent state. Whether this is architecturally tractable (gradient flow through a fast-plastic projection is subtle) is an engineering question; the biological motivation is clear.

**Counterpoint structure.** The architectural choice to commit to *both* fast-firing-rate-like and slow-synaptic-like memory channels is the user's program's resolution of the persistent-vs-silent debate. Mongillo 2008 is the slow-synaptic anchor; Riley-Constantinidis 2016 and Constantinidis 2018 are the fast-firing-rate anchor; Masse 2019 is the synthesis showing that both substrates emerge from a single trained network depending on task demand. The user's program inherits this synthesis directly: the multi-compartmental memory commitment is the architectural acknowledgement that the substrate question is not a binary choice but a hybrid-code question, and that the engineering work is in *how the two substrates are coupled* rather than in *which one wins*.

## 8. Citations to follow

- `stokes2013_activity_silent_wm` — Stokes et al. 2013, the canonical activity-silent WM challenger to persistent activity. The conceptual descendant of Mongillo 2008 that frames silent maintenance as a *dynamic coding* phenomenon; the natural pair to this entry in the user's database. Not in seed; should be added.
- `markram_tsodyks1996_synaptic_dynamics` — The original short-term plasticity formulation behind Mongillo's $u \cdot x$ kinetics. Foundational for any synaptic-facilitation modeling in the database.
- `tsodyks_markram1997_neural_code` — Tsodyks & Markram on the role of synaptic depression in coding; the companion to the 1996 paper.
- `wolff2017_pinging_silent_wm` — Wolff et al. 2017, TMS "pinging" reveals activity-silent WM traces. The strongest empirical evidence for Mongillo-style silent maintenance in human cortex.
- `lundqvist2016_gamma_bursts_wm` — Lundqvist et al. 2016, gamma/beta bursts during WM delays in PFC. The empirical phenomenon that partially confirms Mongillo's population-spike prediction.
- `lundqvist2018_pfc_burst_wm` — Lundqvist et al. 2018, *J Neurosci* counterpoint to Constantinidis 2018; the modern Lundqvist statement of burst-coding WM.
- `compte2000_bump_attractor` — Compte, Brunel, Goldman-Rakic & Wang 2000, the bump-attractor model that Mongillo's mechanism is the silent alternative to. Essential for the debate.
- `wang1999_nmda_bistability` — Wang 1999, NMDA-receptor-dependent bistability supporting persistent firing. The cellular-mechanism alternative to Mongillo's synaptic mechanism.
- `laughlin1998_metabolic_cost` — The metabolic-cost-of-neural-information argument that justifies Mongillo's claim of efficiency advantage for silent over persistent maintenance. Also load-bearing for the user's `coalition-resource-competition` thesis.
- `attwell_laughlin2001_brain_energy_budget` — The quantitative budget that establishes spiking as the dominant cortical energy cost; the empirical underpinning of Mongillo's efficiency claim.
- `barak_tsodyks2014_working_models` — Barak & Tsodyks follow-up review on working models of WM. Updates Mongillo 2008 with subsequent developments and reconciles it with persistent-activity findings.
- `schlag_irie_schmidhuber2021_linear_transformers_fast_weights` — Linear transformers as fast-weight programmers; the ML-side incarnation of Mongillo's synaptic-facilitation memory.
- `beck2024_xlstm` — The xLSTM matrix-memory architecture; the most recent ML analog of Mongillo's synaptic-state memory and the natural engineering target for the user's program's slow-plastic channel.
- `mujika2017_fast_slow_rnn` — The fast-slow LSTM that PRISM v2's slow/fast memory commitment cites; the ML pair to the Mongillo-vs-persistent biological debate.
