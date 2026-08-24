---
id: wm_vwm_hippocampus_world_models_deep_dive
type: thread
title: "Working memory, visual working memory, hippocampus, and world models — a deep-dive synthesis"
papers:
  - baddeley_hitch1974_working_memory
  - desposito_postle2015_wm_neuroscience
  - stokes2015_activity_silent_wm
  - christophel2017_distributed_wm
  - bays_husain2008_dynamic_resources
  - soto2008_automatic_attention_wm
  - foster2017_alpha_vwm
  - postle2006_wm_emergent
  - sreenivasan_desposito2019_delay_activity
  - awh_jonides2001_overlapping_attention_wm
  - okeefe_dostrovsky1971_hippocampal_map
  - hafting2005_grid_cells
  - whittington2020_tem
  - stachenfeld2017_predictive_map
  - behrens2018_cognitive_map
  - hafner2023_dreamerv3
  - wayne2018_merlin
  - schrittwieser2020_muzero
  - banino2018_vector_navigation
  - assran2023_ijepa
  - lisman_grace2005_hippocampal_vta
  - panichello_buschman2021_shared_mechanisms
  - lecun2022_path_to_agi
  - bardes2023_vjepa
  - hafner2020_dreamer
  - ha_schmidhuber2018_world_models
  - gazzaley_nobre2012_topdown
  - kiyonaga_egner2013_wm_internal_attention
concepts:
  - multi_compartmental_memory
  - slow_fast_recurrence
  - gridcell_rnn
  - coalition_resource_competition
  - world_model_emergence
  - coupled_rnn_world_models
  - hierarchical_predictive_coding
  - bidirectional_hierarchical_feedback
last_updated: "2026-05-23"
---

# Working memory, visual working memory, hippocampus, and world models — a deep-dive synthesis

This thread is the cross-paper synthesis of the 20-paper deep-dive batch added on 2026-05-23 spanning four target domains: *working memory* (5 papers), *visual working memory with attention bridges* (5 papers), *hippocampus / place-grid cells / cognitive maps* (5 papers), and *modern world-model RL architectures* (5 papers). The dive was motivated by gaps in the user's database (hippocampus had only 1 prior paper, world models had only 3, neural WM substrate was sparse) and by the user's program-level commitment to architectures grounded in the biological mechanisms of memory and attention.

---

## 1. The convergent architectural thesis across the four domains

The four target domains, on the surface, address different scales of biological cognition (cognitive psychology of WM, neural substrate of VWM, single-neuron biology of hippocampus, AI engineering of world models). At the *architectural* level, the 20 papers converge on a small number of load-bearing commitments that the user's program inherits:

**Thesis 1 — memory and attention share substrate.** [postle2006_wm_emergent](../papers/postle2006_wm_emergent.md), [awh_jonides2001_overlapping_attention_wm](../papers/awh_jonides2001_overlapping_attention_wm.md), [desposito_postle2015_wm_neuroscience](../papers/desposito_postle2015_wm_neuroscience.md), [soto2008_automatic_attention_wm](../papers/soto2008_automatic_attention_wm.md), and the already-in-seed [panichello_buschman2021_shared_mechanisms](../papers/panichello_buschman2021_shared_mechanisms.md) all converge on the same architectural claim: working memory and selective attention are not separable subsystems; they operate on shared substrate. The user's program-level commitment to *no separate "memory module" and "attention module"* (instead, the central self-attention substrate of the Feedback Transformer plays both roles simultaneously) is biologically licensed across multiple lines of evidence in this batch.

**Thesis 2 — memory is distributed, multi-compartmental, content-paired.** [christophel2017_distributed_wm](../papers/christophel2017_distributed_wm.md) and [sreenivasan_desposito2019_delay_activity](../papers/sreenivasan_desposito2019_delay_activity.md) consolidate the empirical case: WM contents are simultaneously represented across V1-V4, IPS, premotor, MTL, PFC, basal ganglia, and thalamus, with each region storing the same memorandum at a different level of abstraction. This is the modern biological warrant for the user's [multi_compartmental_memory](../concepts/multi_compartmental_memory.md) commitment: multiple recurrent compartments paired with cortical-hierarchy levels, with each compartment storing content at its appropriate abstraction.

**Thesis 3 — spatial-grid organization is the substrate of biological memory.** [okeefe_dostrovsky1971_hippocampal_map](../papers/okeefe_dostrovsky1971_hippocampal_map.md), [hafting2005_grid_cells](../papers/hafting2005_grid_cells.md), and [foster2017_alpha_vwm](../papers/foster2017_alpha_vwm.md) jointly establish that the brain's memory architecture is fundamentally *spatially organized* — place cells in hippocampus and grid cells in MEC for explicit spatial coding, alpha-band scalp signatures for spontaneous spatial coding even of task-irrelevant location. The user's [gridcell_rnn](../concepts/gridcell_rnn.md) architectural commitment — one state vector per spatial position — is biologically licensed by this convergent evidence.

**Thesis 4 — memory is predictive, not just retrospective.** [stachenfeld2017_predictive_map](../papers/stachenfeld2017_predictive_map.md) (SR theory) and [stokes2015_activity_silent_wm](../papers/stokes2015_activity_silent_wm.md) (dynamic coding) jointly argue that biological memory is *forward-looking* — encoding what is likely to happen next, not just logging what has happened. The user's [world_model_emergence](../concepts/world_model_emergence.md) and [hierarchical_predictive_coding](../concepts/hierarchical_predictive_coding.md) commitments are licensed by this thesis.

**Thesis 5 — capacity is a continuous resource, allocated by attention.** [bays_husain2008_dynamic_resources](../papers/bays_husain2008_dynamic_resources.md), in conjunction with the prior [emrich2017_attention_wm_resources](../papers/emrich2017_attention_wm_resources.md) and [bays2024_wm_representation](../papers/bays2024_wm_representation.md), establishes the cognitive-psychology source of the user's [coalition_resource_competition](../concepts/coalition_resource_competition.md) commitment: a fixed-budget resource is allocated across items via attention-mediated competition.

**Thesis 6 — structural-content factorization enables generalization.** [whittington2020_tem](../papers/whittington2020_tem.md) and [behrens2018_cognitive_map](../papers/behrens2018_cognitive_map.md) jointly articulate the *structure / content factorization* principle: re-usable abstract structural codes (graph relations, spatial maps) are paired with content bindings (sensory observations) that vary across environments. The user's program inherits this as the long-horizon architectural target: the deepest memory compartment should hold structural codes that generalize across tasks, while shallower compartments hold content bindings.

**Thesis 7 — world models can be explicit (Dreamer/MERLIN/MuZero) or emergent (the user's thesis).** [hafner2023_dreamerv3](../papers/hafner2023_dreamerv3.md), [wayne2018_merlin](../papers/wayne2018_merlin.md), and [schrittwieser2020_muzero](../papers/schrittwieser2020_muzero.md) instantiate the *explicit-world-model* training paradigm; the user's [world_model_emergence](../concepts/world_model_emergence.md) thesis predicts that a world model should emerge from inter-hub competition without an explicit world-model objective. The deep-dive papers provide both the baselines to beat (Dreamer, MERLIN, MuZero) and the architectural references for what a "world model" should look like at internal-state level.

---

## 2. Cross-paper convergences and tensions

### Convergences

**(a) Attention-WM shared substrate — five-paper convergence.** Awh & Jonides 2001 (cognitive-psychology), Postle 2006 (broader emergent-property), Soto et al. 2008 (WM-to-attention guidance), D'Esposito & Postle 2015 (modern neural synthesis), and the already-in-seed Panichello & Buschman 2021 (PFC empirical demonstration) all converge on the architectural claim that attention and WM share substrate. This is the strongest cross-paper convergence in the batch.

**(b) Distributed delay activity — three-paper convergence.** D'Esposito & Postle 2015, Christophel et al. 2017, and Sreenivasan & D'Esposito 2019 jointly canonize the distributed-storage finding: WM lives across many cortical regions simultaneously, not in PFC alone. This is the empirical anchor for the user's multi-compartmental memory commitment.

**(c) Spatial organization of memory — four-paper convergence.** O'Keefe & Dostrovsky 1971 (place cells), Hafting et al. 2005 (grid cells), Foster et al. 2017 (alpha-band spatial WM), and Banino et al. 2018 (grid cells emerge in deep RL) converge on the architectural claim that *memory is fundamentally spatially organized*. The convergence spans biology (hippocampus, EC, scalp EEG) and AI (deep RL agents), strongly supporting the architectural choice.

**(d) Predictive substrate — five-paper convergence.** Stokes 2015 (dynamic coding), Stachenfeld et al. 2017 (SR), Behrens et al. 2018 (cognitive map as predictive), Whittington et al. 2020 (TEM as next-observation prediction), and the world-model lineage (Dreamer, MERLIN, MuZero) all converge on the architectural claim that memory should be *predictive*. The user's program inherits this commitment.

**(e) Multi-scale spatial hierarchy — three-paper convergence.** Hafting et al. 2005 (multi-scale grid spacings, dorsoventral gradient), Stachenfeld et al. 2017 (grid cells as SR eigenvectors at different frequencies), Banino et al. 2018 (multi-scale grid emergence in deep RL) jointly support the architectural commitment to *multiple parallel spatial resolutions* in the memory hierarchy.

### Tensions

**(a) Persistent activity vs activity-silent vs dynamic codes.** Constantinidis et al. 2018 (already in seed) defends classical persistent activity as the WM mechanism; Stokes 2015 argues for activity-silent storage via synaptic facilitation; Sreenivasan & D'Esposito 2019 takes a both/and position (all forms coexist). The user's program is licensed by all three positions because the architecture supports continuous updates (persistent), gated silent storage (activity-silent), and dynamic morphing (dynamic coding) simultaneously.

**(b) Sensory recruitment vs PFC-as-content-storage.** Postle 2006 and Christophel et al. 2017 push hard on the sensory-recruitment view; the Constantinidis tradition and content-selective PFC findings (Mendoza-Halliday & Martinez-Trujillo 2017, Freedman & Miller) push back. The user's program is licensed by the integrated view: shallow compartments are sensory-paired (Postle/Christophel), the deepest compartment is content-and-control-paired (a softer version of the Constantinidis position).

**(c) Slot vs resource for VWM capacity.** Bays & Husain 2008 (resource); Luck & Vogel tradition + Adam, Vogel & Awh 2017 (slot, possibly with continuous precision within slot). The user's program is closer to the resource view via the [coalition_resource_competition](../concepts/coalition_resource_competition.md) commitment, but the architecture does not commit definitively — capacity emerges from network dynamics rather than from a hard-coded slot count.

**(d) Explicit vs emergent world models.** Dreamer / MERLIN / MuZero explicitly train world models; the user's [world_model_emergence](../concepts/world_model_emergence.md) thesis predicts emergence without explicit training. The tension is empirical: can the user's competition-based architecture match the world-model quality of explicit training? This is the central empirical question the user's program targets.

**(e) Reconstruction-based vs latent-prediction self-supervision.** DreamerV3 / MERLIN use pixel reconstruction; I-JEPA / V-JEPA / TEM use latent prediction. The user's [iterative_variational_encoder_decoder](../concepts/iterative_variational_encoder_decoder.md) should be configured for latent prediction (in the JEPA lineage) to avoid the pixel-reconstruction limitations DreamerV3 demonstrates.

---

## 3. Architectural recommendations for the user's program

Based on the cross-paper synthesis, the deep-dive batch supplies the following concrete architectural recommendations:

1. **Continue committing to shared-substrate attention-WM.** Multiple cognitive-psychology lines (Awh-Jonides, Postle, Soto, Gazzaley-Nobre, Panichello-Buschman) and modern neural evidence (D'Esposito-Postle, Sreenivasan-D'Esposito) all converge on this commitment. The Feedback Transformer central self-attention as the joint attention-and-WM substrate is biologically licensed.

2. **Strengthen the multi-compartmental memory commitment.** Distributed-WM evidence (Christophel et al., D'Esposito-Postle, Sreenivasan-D'Esposito) is the most-replicated finding in modern WM neuroscience; the user's multi-compartmental design directly recapitulates it. Continue to commit to V1/V2/V4-paired compartments with distinct abstraction levels.

3. **Validate the gridcell_rnn architecture against emerging-grid-cells empirical evidence.** Banino et al. 2018 demonstrates that grid cells emerge in deep RL agents; the user's gridcell_rnn architecture should be probed for similar emergent properties. Train the user's models on path-integration or navigation tasks and check for grid-like, place-like, border-like representations in the grid cells.

4. **Adopt latent-prediction over pixel reconstruction.** I-JEPA, V-JEPA, and TEM all demonstrate that latent prediction produces more semantic representations than pixel reconstruction. The user's iterative VAE should be configured for latent prediction at the encoder level, not pixel-level reconstruction. DreamerV3's pixel-reconstruction limitation is a cautionary tale.

5. **Add an offline-replay / consolidation mechanism.** The cognitive-map literature (Behrens et al., Kurth-Nelson 2016 MEG replay, Tse et al. 2007 schema-consistent learning) supports the architectural extension of an offline-consolidation phase. The user's program does not currently have one; adding a "dream phase" in which the multi-hub system runs forward in imagination without external input could substantially improve structural learning.

6. **Empirical validation on long-horizon partial-observability benchmarks.** MERLIN's principal advantage over LSTM-A3C is in severe partial-observability; the user's program is engineered for this regime. Evaluate the user's models on MERLIN-style benchmarks (DM Lab Memory Suite or analogs) to demonstrate the multi-compartment memory hierarchy outperforms standard recurrent baselines.

7. **Adopt DreamerV3 engineering robustness lessons.** Symlog, free bits, LayerNorm, two-hot critic regression — these are low-cost engineering improvements that improve training stability. The user's recent RViT+ runs (run 5 collapse, run 6 surgical fix) demonstrate that engineering robustness matters; DreamerV3's lessons are directly applicable.

8. **Probe the user's models for predicted empirical signatures.** The deep-dive papers supply concrete signatures the user's architecture should reproduce:
   - Dual-task selective interference (Baddeley-Hitch) — perturbing one hub should selectively degrade tasks that depend on that hub.
   - Activity-silent storage (Stokes) — perturbation pinging should re-evoke content from low-activity memory states.
   - Resource-precision power law (Bays-Husain) — recall precision should follow $\propto (\text{resource share})^{-1}$.
   - Alpha-band spatial code (Foster et al.) — the attention map at each spatial position should track an IEM-derived spatial code.
   - WM-to-attention bias (Soto) — the attention map should show enhanced weight on patches matching previously-stored content.
   - Structured remapping (Whittington TEM) — structural codes should persist across environments while content bindings change.
   - Community-structure detection (Stachenfeld) — memory representations should fragment at relational boundaries in structured tasks.

---

## 4. Coverage gaps remaining after the deep-dive

Even with the 20-paper addition, several coverage gaps remain.

**(a) Hippocampal replay / consolidation.** The deep-dive added foundational papers (place cells, grid cells, TEM, SR, cognitive map review) but did not add the *replay* literature (Skaggs & McNaughton 1996, Foster & Wilson 2006, Ji & Wilson 2007, Lewis & Durrant 2011). The user's program would benefit from explicitly engaging with the offline-consolidation mechanism.

**(b) CA3/DG circuit dynamics.** Pattern separation (Yassa & Stark 2011) and pattern completion (McClelland & O'Reilly 1995) are foundational hippocampal-circuit concepts the user's program touches only via [lisman_grace2005_hippocampal_vta](../papers/lisman_grace2005_hippocampal_vta.md). A dedicated CA3/DG paper or two would round out the hippocampal coverage.

**(c) Schema and semantic memory.** The cognitive-map framework engages with schemas (Tse et al. 2007) but the user's database lacks systematic coverage of semantic-memory-and-schema literature (Ghosh & Gilboa 2014; van Kesteren et al. 2012).

**(d) Stochastic-world-model extensions.** The deep-dive added DreamerV3 (deterministic+stochastic) and MuZero (deterministic) but did not add Stochastic MuZero (Antonoglou et al. 2022) or other stochastic-dynamics extensions.

**(e) Transformer-based world models.** IRIS (Micheli et al. 2023), STORM (Zhang et al. 2023), TD-MPC2 (Hansen et al. 2024) — the modern transformer-based world-model alternatives to RSSM-based Dreamer were noted in citations-to-follow but not added.

**(f) Diffusion world models.** DIAMOND (Alonso et al. 2024), Genie (Bruce et al. 2024) — the modern diffusion-based world-model frontier was noted but not added.

These gaps are candidates for future deep-dive batches; the current batch's 20-paper allocation prioritized cross-domain coverage over exhaustive within-domain coverage.

---

## 5. Connection to other threads

- [coupled_rnn_architectures](coupled_rnn_architectures.md) — the world-model papers (Dreamer, MERLIN, MuZero) extend the coupled-RNN lineage this thread maintains.
- [predictive_coding_as_canonical_computation](predictive_coding_as_canonical_computation.md) — the predictive-memory thesis (Stachenfeld, Stokes, TEM) is the modern instantiation of predictive coding in the memory domain.
- [feedback_substrates](feedback_substrates.md) — the distributed-WM literature (Christophel, Sreenivasan-D'Esposito) supplies modern empirical evidence for the bidirectional feedback substrate.
- [the_user_architectural_program](the_user_architectural_program.md) — the deep-dive batch's 20 papers substantially expand the biological warrant for the user's program-level commitments.
- [rvit_plus_engineering](rvit_plus_engineering.md) — the DreamerV3 engineering-robustness lessons are directly applicable to RViT+ training; the deep-dive batch supplies a richer biological context for the architectural choices RViT+ commits to.
