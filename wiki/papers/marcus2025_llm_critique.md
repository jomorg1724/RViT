---
id: marcus2025_llm_critique
title: "Generative AI's crippling and widespread failure to induce robust models of the world"
authors:
  - "Marcus, Gary"
year: 2025
venue: "Substack essay (Marcus on AI)"
doi: ""
arxiv: ""
url: "https://garymarcus.substack.com/"
tags:
  - deep-learning
  - theoretical-essay
  - review
  - world-models
concepts:
  - world-model-emergence
  - causal-reasoning
  - system-1-vs-system-2
related:
  - lecun2022_path_to_agi
  - pearl2018_book_of_why
  - hawkins2021_thousand_brains
  - schmidhuber2015_learn_to_think
  - wang2025_hierarchical_reasoning_model
relevance_to:
  - prism_v2
seed_source:
  - prism_private_notes
status: full
depth: full
last_updated: "2026-05-15"
---

# Generative AI's crippling and widespread failure to induce robust models of the world

## 1. Abstract

This entry summarizes Gary Marcus's 2025 cycle of essays on the limits of large language models, anchored by the Substack piece *Generative AI's crippling and widespread failure to induce robust models of the world* and adjacent posts collected on `garymarcus.substack.com` (in the same period as his trade book *Taming Silicon Valley*, 2024). Marcus's thesis across these pieces is that current LLMs — including frontier models at the GPT-4 / Claude / Gemini generation — do not induce robust, manipulable internal models of the entities, causal structure, and physics of the world they describe in text. They produce fluent surface output that statistically tracks training distributions, but they break in characteristic ways on out-of-distribution prompts, compositional generalization, long-horizon planning, simple physical reasoning, and basic arithmetic when adversarial care is taken. Marcus's diagnosis is architectural rather than scale-limited: scaling more parameters and tokens does not by itself produce the structured, symbolic, causally indexed representations he argues are required, and the hallucination phenomenon is a symptom of the missing world model rather than a residual nuisance. The constructive corollary — left programmatic in these essays — is that AI systems need explicit world-model machinery, neurosymbolic hybridization, and grounded causal inference in the spirit of Pearl.

## 2. Why this matters for us

Marcus is the most visible articulator of the negative case that motivates the user's program: that current generative AI lacks genuine world models, and that this is an architectural, not a scaling, problem. The user's competition-emergent-PC thesis is the *constructive* answer to Marcus's critique. Marcus tells us what is missing (robust world models, causal structure, manipulable internal representations); the user proposes a concrete mechanism by which such models can emerge — implicitly, without an explicit world-model loss — from inter-hub competition for self-attention bandwidth (`the_user_architectural_program.md` §5). The empirical test plan in §5 of that thread (train a decoder to predict the global hub state at $t+1$ and check whether iterative rollouts produce coherent long-range internal-state prediction) is, in effect, a falsifiable answer to Marcus: it operationalizes "did a world model emerge?" as a measurable property of a trained multi-hub system. Marcus therefore sets the bar the program must clear.

## 3. Key claims

1. **Hallucinations are intrinsic, not residual.** LLM hallucinations reflect the absence of an internal model of what is true in the world, not bugs that fine-tuning will fix.
2. **No robust world model.** LLMs do not induce stable internal representations of entities, their properties, their relations, or how those evolve over time; coherence collapses under modest distributional shift.
3. **No genuine reasoning.** Apparent reasoning is largely template completion over training-distribution patterns; chain-of-thought traces are post-hoc rationalizations rather than evidence of inferential structure, and small perturbations to problem framing degrade performance.
4. **Scaling does not cure these failures.** Capabilities improve smoothly on benchmarks but the failure *modes* (compositional generalization, novel-combination reasoning, long-horizon planning, simple physical reasoning) recur at every model generation.
5. **Causality is missing.** LLMs operate at Pearl's first rung (association); they have no native machinery for intervention or counterfactual reasoning, which Marcus treats as a prerequisite for general intelligence.
6. **Neurosymbolic hybridization is the path forward.** Symbol-manipulating components — for entities, types, rules, constraints — must be combined with statistical pattern recognition rather than asking the latter to subsume the former.
7. **Benchmark saturation is misleading.** High scores on text benchmarks systematically overstate generalization because the benchmarks are sampled from the same training distribution they purport to test.
8. **There are policy and safety consequences.** The gap between marketed capability and actual robustness is itself a societal harm, motivating the regulatory argument of *Taming Silicon Valley* (the book companion to the essays).

## 4. Methods

Marcus's 2025 essays are non-empirical position pieces. The argumentative method is: (a) catalog publicly reported failure modes of frontier LLMs (image-generation physics errors, arithmetic on unfamiliar number ranges, counting-letter tasks, planning failures, knowledge-cutoff confabulations, reversal-curse style asymmetries); (b) argue that the *pattern* of these failures is consistent across architectures and scales and is therefore symptomatic of a shared structural deficit rather than transient implementation bugs; (c) contrast with the structured-representation desiderata derived from cognitive science (object permanence, type-token distinctions, compositional semantics, causal graphs); (d) deduce a normative architectural prescription (neurosymbolic + causal). The "data" are public failure exhibits — screenshots, transcripts, and reproduced examples Marcus collects on Substack — together with citations to academic ablations of compositional and reasoning behavior.

## 5. Results

Because the work is essayistic, there are no headline numbers in the way a benchmark paper has them. The substantive observations Marcus repeatedly invokes are:

- Frontier LLMs continue to fail on compositional generalization benchmarks (SCAN-style splits, COGS, and their successors) at rates qualitatively higher than on in-distribution evaluation.
- Reported reasoning improvements on math and code benchmarks largely track contamination, prompt engineering, and tool use rather than gains in underlying inferential robustness.
- Reversal-style and counterfactual probes (e.g., "A is B" learned but "B is A" not retrievable) persist at every scale.
- Hallucination rates on closed-domain factual QA remain non-trivial (single- to double-digit percentage points depending on domain and probe) and do not appear to vanish with scale or RLHF alone.
- Vision-language models continue to generate physically implausible images (extra fingers, intersecting solid objects, gravity violations) at rates Marcus reads as evidence that the system has no manipulable internal physics.

The intended takeaway is not a quantitative claim but a qualitative one: the *pattern* of failure is uniform across systems, scales, and modalities, and is what one would predict if the underlying machinery lacked a world model.

## 6. Critique / limitations

Marcus's case has well-known weaknesses that any use of it in our program should acknowledge.

- **Goalpost-shifting risk.** "Robust world model" and "genuine reasoning" are not operationalized with measurable criteria; each apparent counter-example can be reclassified as "still not real reasoning." Without a falsification criterion, the critique is rhetorically powerful but scientifically slippery. This is precisely the gap the user's empirical test plan (decoder rollout from hub state) can close: it gives an operational definition of "did a world model emerge."
- **Cherry-picking of failure exhibits.** Marcus's evidence base is heavily curated; the implicit base-rate is unstated. Some of the failures he cites have been substantially reduced by subsequent training; the critique is durable in *kind* but the specific exhibits age quickly.
- **Underweighting of representation-probing evidence.** A growing literature shows that LLMs do encode latent variables corresponding to entity properties, spatial layout, board states, and so on (Othello-GPT-style probes; world-state recovery in LMs). Marcus tends to discount these as superficial regularities; whether they constitute "world models" depends on the definition.
- **Neurosymbolic prescription is underspecified.** Marcus is clear about what's missing but vague about the mechanism that would supply it. The essays do not commit to a particular hybrid architecture, training signal, or empirical milestone. This is the constructive gap the user's program tries to close — though not via neurosymbolic hybridization in Marcus's sense, but via competition-emergent structure in a fully neural system.
- **Adversarial relationship to scaling.** Marcus has been wrong about specific predicted ceilings several times. The trajectory of in-context learning, instruction following, and tool-augmented reasoning has outpaced his stated expectations even where the structural critique stands.
- **Polemical register.** The essays mix scientific argument with public-discourse advocacy. Citing them in academic work requires separating the technical claims (which we use here) from the policy and personality material.

## 7. Connection to our work

Marcus's critique sets the *target* of the user's architectural program in a way no other paper in the database does, and it does so as the negative case that the user's constructive thesis answers.

**Marcus as the negative case.** The user's claim that an architecturally minimal change — multiple objective-specific hubs sharing a self-attention layer through a Feedback Transformer — can give rise to a world model is a substantive empirical conjecture *only* against the background of Marcus's argument that today's architectures cannot do this and will not do this at scale. If one believed scaling LLMs would simply produce world models, the user's program would be a more expensive way to reach the same place. Marcus is the strongest published statement of the opposing view. Adopting Marcus's diagnosis (no robust world model in current systems) is therefore load-bearing for the motivation in `the_user_architectural_program.md` §5: the program is interesting because Marcus is right that LLMs do not currently induce these models.

**Where the user departs from Marcus.** The user does not endorse Marcus's prescription (neurosymbolic hybridization). The constructive thesis is purely neural: predictive coding, and through it the implicit world model Marcus demands, arises as the strategic response of competing neural coalitions to resource scarcity (`the_user_architectural_program.md` §5, steps 1–4). The world model is not bolted on as a symbolic module; it emerges as the equilibrium structure of inter-hub prediction. This is much closer in spirit to LeCun's JEPA program (`lecun2022_path_to_agi.md`) than to Marcus's neurosymbolic prescription. The right reading is: Marcus diagnoses, LeCun proposes one architectural cure (predictive joint embeddings), the user proposes a different one (competition-emergent PC in a multi-hub system).

**Operational answer to the slipperiness of Marcus's bar.** The user's proposed empirical test — train an external decoder $D$ on $(s_t \to s_{t+1})$ over the global multi-hub state, then check whether iterative rollout $D(D(D(\ldots s_0)))$ stays semantically coherent over long horizons — directly operationalizes "robust world model." A coherent long-horizon rollout of internal state would be evidence of exactly the manipulable internal model Marcus says is missing. This connects to the Schmidhuber 2015 coupled-RNN framing (`schmidhuber2015_learn_to_think.md`), where a controller learns to query a predictive world-model RNN, and to the dual-timescale hierarchical reasoning of Wang et al. 2025 HRM (`wang2025_hierarchical_reasoning_model.md`), which the user explicitly cites as motivating the slow/fast structure of the deeper hubs.

**Causality and Pearl.** Marcus's third rung — counterfactuals — is the connection point to Pearl 2018 (`pearl2018_book_of_why.md`). The user's program does not yet claim to climb to that rung explicitly, but the multi-hub system with an RL hub provides at least the substrate for intervention (hub actions are interventions on the shared attention map, with consequences the system can observe), which is the minimum architectural commitment a Pearl-style causal account requires.

**Comparison with Hawkins.** Hawkins's *A Thousand Brains* (`hawkins2021_thousand_brains.md`) is closer to the user's positive thesis than Marcus is: Hawkins also argues for many parallel models that vote, which is structurally similar to the user's multi-hub architecture. Marcus and Hawkins agree on the diagnosis (no world model in LLMs) but diverge on the cure (neurosymbolic vs. cortical-column-style voting); the user's program is closer to Hawkins on the cure while accepting Marcus on the diagnosis.

**What the published Recurrent ViT and PRISM do not yet address.** The change-detection work (2502.10955) and PRISM v1/v2 do not directly engage Marcus's critique: they are perceptual benchmarks, not reasoning benchmarks. The Marcus connection becomes load-bearing only at the level of the full multi-hub program, especially the world-model-emergence test. This is why the entry is tagged `relevance_to: prism_v2` rather than `recurrent_vit` — PRISM v2 (and the multi-hub extension beyond it) is the artifact that takes on Marcus's challenge.

## 8. Citations to follow

- `pearl2018_book_of_why` — already a planned entry; Marcus invokes Pearl's ladder of causation as the standard against which LLM reasoning is judged inadequate.
- `lecun2022_path_to_agi` — already in seed; the JEPA position paper is the most-cited alternative architectural prescription to Marcus's neurosymbolic one.
- `hawkins2021_thousand_brains` — already in cite trail; the parallel-models voting account is closer to the user's program than Marcus's prescription.
- `marcus_davis2019_rebooting_ai` — the book-length precursor to the 2025 essays, where the neurosymbolic prescription is laid out at length.
- `mitchell2023_abstraction_reasoning` — Melanie Mitchell's complementary critique of LLM reasoning via ARC-style abstraction tasks; provides quantitative grounding for Marcus's qualitative claims.
- `vafa2024_world_models_in_transformers` — representative of the representation-probing literature that Marcus's critique should be tested against; relevant for evaluating whether implicit world models are present in trained transformers.
- `kambhampati2024_llms_cant_plan` — adjacent critique focused specifically on planning; a more empirically grounded version of part of Marcus's case.
- `mccoy2023_embers_of_autoregression` — quantifies the input-distribution sensitivity Marcus invokes informally.
- `wang2025_hierarchical_reasoning_model` — already in cite trail; the HRM is the strongest recent argument that *architectural* changes (not scaling) drive reasoning gains, consonant with Marcus's diagnosis.
- `schmidhuber2015_learn_to_think` — already in cite trail; the explicit controller + world-model framing is one of the cleanest constructive answers to Marcus's complaint.
