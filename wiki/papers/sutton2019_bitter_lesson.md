---
id: sutton2019_bitter_lesson
title: "The Bitter Lesson"
authors:
  - "Sutton, Richard S."
year: 2019
venue: "Online essay (incompleteideas.net)"
doi: ""
arxiv: ""
url: "http://incompleteideas.net/IncIdeas/BitterLesson.html"
tags:
  - theoretical-essay
  - deep-learning
  - reinforcement-learning
concepts: []
related:
  - lecun2022_path_to_agi
  - hawkins2021_thousand_brains
  - marcus2025_llm_critique
  - schmidhuber2015_learn_to_think
  - schulman2016_gae
  - sutton_barto2018_rl_intro
  - sutton1988_td
  - schulman2017_ppo
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

# The Bitter Lesson

## 1. Abstract

Sutton's short essay (March 13, 2019) distills 70 years of AI research history into a single observation: general-purpose methods that scale with compute have systematically outperformed methods that bake in human knowledge of the domain. The argument is structural — Moore's-law-style exponential growth in cheap compute means that, over horizons longer than a typical research project, any short-term advantage gained from hand-crafted domain knowledge is overtaken by methods that simply use more compute. Sutton inventories four canonical episodes — computer chess (Deep Blue, 1997), computer Go (AlphaGo, 2016), speech recognition (HMM → deep learning), and computer vision (edges / SIFT → convnets) — in each of which the human-knowledge camp initially dominated, was overtaken once compute grew, and resisted the lesson on grounds that the winning method "wasn't how people think." Sutton identifies *search* and *learning* as the two general-purpose techniques that scale arbitrarily with compute, and concludes that AI builders should commit to *meta-methods* that can discover structure rather than to architectures that bake in the structure their designers think the brain or the world has. The essay is informal and contains no equations, experiments, or citations, but it has become a touchstone for arguments about scaling, inductive bias, and the role of neuroscience-inspired design in deep learning.

## 2. Why this matters for us

The Bitter Lesson is the single most cited rhetorical opponent of the user's architectural program. The user's published Recurrent ViT, PRISM v1, PRISM v2, and the broader program of multi-compartmental, biologically-aligned, feedback-rich architectures (`threads/the_user_architectural_program.md`) are *deliberately* hand-engineered around inductive biases drawn from neuroscience — feedback transformers (modeled on L6 corticocortical feedback), GridCell RNNs, V1→V2→V4→IT-style hierarchical descending and ascending projections, biased-competition–style hub competition. This is exactly the species of "building in how we think the brain works" that Sutton predicts will plateau. Engaging this essay seriously is therefore not optional: any defense of the user's program has to articulate why its inductive biases are not the kind Sutton condemns, or accept that the program is a bet against the Bitter Lesson and characterize the conditions under which that bet pays off.

## 3. Key claims

1. Over 70 years, general methods that leverage computation have outperformed methods that leverage human knowledge of the domain, by a large margin.
2. The structural cause is Moore's law (more precisely, exponentially falling cost per unit of compute), which makes any compute-bounded design obsolete on a timescale shorter than the design's research lifetime.
3. Hand-engineered domain knowledge and compute-leveraging methods are not strictly incompatible, but they compete for researcher time and tend in practice to run counter to each other; knowledge-rich methods also complicate architectures in ways that make them less able to absorb additional compute.
4. *Search* and *learning* are the two classes of techniques known to scale arbitrarily with compute; meta-methods that exploit either should be preferred to methods that hard-code structure.
5. The historical pattern has four phases: (a) researchers build domain knowledge into agents, (b) this helps in the short term and is intellectually satisfying, (c) it plateaus and eventually inhibits progress, (d) breakthrough is delivered by a compute-scaling alternative that the knowledge-builders resist.
6. Empirical evidence: computer chess (Deep Blue's deep search vs. human-chess-knowledge programs), computer Go (AlphaGo's search + self-play learning vs. Go-specific heuristics, delayed ~20 years), speech recognition (HMMs and then deep learning vs. phonetic / vocal-tract models), and computer vision (convnet features vs. edges, generalized cylinders, SIFT).
7. The contents of minds are "tremendously, irredeemably complex"; researchers should not try to bake in simple accounts of space, objects, agents, or symmetries — those belong to the world, not to the architecture.
8. The right object of design is therefore a meta-method that can *find* such structure; "we want AI agents that can discover like we can, not which contain what we have discovered."

## 4. Methods

There are none. The essay is an informal position piece — roughly 1100 words, no equations, no figures, no citations. Its method is rhetorical induction over four case studies. Each case study has the same three-act structure: (i) researchers initially commit to a human-knowledge-rich approach; (ii) a compute-rich, search- or learning-based approach overtakes them once hardware is sufficient; (iii) the knowledge-rich camp resists the lesson, sometimes for decades. The four case studies — chess, Go, speech, vision — are presented in chronological order of compute crossover.

The essay's only normative recommendation is a meta-rule: prefer methods that scale with compute (search, learning) over methods that bake in domain knowledge; prefer designing meta-methods that can discover structure over designing architectures that embed it.

## 5. Results

Not applicable — the piece reports no experiments. Its empirical content is the historical inventory of compute-crossover episodes. Some commonly-cited corroborating data points (added by readers in the years since publication, not by Sutton in the essay itself) include:

- The transition from feature-engineered computer vision pipelines to AlexNet (Krizhevsky 2012) and downstream convnets / vision transformers; modern systems use minimal hand-engineered priors beyond convolution / patch tokenization.
- The transition from HMM-GMM speech systems to end-to-end deep learning and then to large autoregressive transformers.
- The transition from MCTS-with-hand-tuned-Go-heuristics to AlphaGo (Silver et al. 2016), AlphaGo Zero (2017), and AlphaZero (2018) — each successive version stripped out more human domain knowledge.
- The post-2019 ascendancy of large language models, which use almost no linguistic or grammatical priors beyond next-token prediction at scale, and which have absorbed enormous fractions of NLP's hand-designed pipeline.

These are the data the essay invites the reader to extrapolate from; the prediction is that any future architectural commitment that does not scale with compute will be overtaken on a similar timeline.

## 6. Critique / limitations

The essay's compression is its strength but also its principal weakness. Several critiques have appeared in the years since.

**Survivorship bias in the case selection.** Sutton picks four episodes in which compute-scaling won. Cases where structured priors stuck — convolutional structure itself, transformer attention, residual connections, normalization layers, all of which are non-trivial architectural priors — are folded into the "general methods" category rather than counted against the thesis. Convolution is *exactly* a baked-in symmetry prior (translation equivariance); residual connections are an inductive bias about depth; attention is a bias about pairwise interaction. The essay does not say how to draw the line between an acceptable structural prior (convolution) and a forbidden one (SIFT features). The boundary appears to be drawn post-hoc: priors that turn out to scale with compute are "general," priors that do not are "hand-engineered."

**Compute is not free.** The essay treats compute as exogenously growing at Moore's-law rates and takes the implication as inevitable. Post-2022 frontier-model training has already encountered hard limits — energy availability, memory bandwidth, capital cost, training-data exhaustion — that were not visible in 2019. If the cost curve flattens, the case for inductive bias as a sample-efficiency multiplier strengthens substantially. The Bitter Lesson is contingent on a forecast that may no longer hold.

**Sample efficiency and out-of-distribution generalization are not addressed.** The Bitter Lesson is about asymptotic compute-scaling on training-distribution metrics. It says little about systematic generalization, OOD robustness, or sample efficiency from a human / animal point of view — exactly the regime where the human brain (which uses very little training data) outperforms current scaled models. Marcus 2025 (`marcus2025_llm_critique`) and Hawkins 2021 (`hawkins2021_thousand_brains`) make this critique explicitly.

**No notion of inductive bias as compute-multiplier.** The cleanest counterargument is that biologically-aligned inductive biases are not in opposition to compute scaling — they make a fixed compute budget go further. Convolution beats fully-connected layers at the same FLOPs; attention beats convolution at the same FLOPs on long-range tasks. If a Feedback Transformer or hierarchical-feedback prior is a similar capacity multiplier, then it is *compatible* with the Bitter Lesson rather than the kind of fragile hand-engineering it warns against.

**The essay does not engage with neuroscience.** Sutton lumps "building in how we think we think" and "building in how the brain works" together, but these are very different commitments. Neuroscience-aligned priors are constraints derived from a system (the brain) that is known to be the only general-purpose intelligence on the planet — they are not arbitrary researcher intuitions. The essay's argument is strongest against pre-1990 symbolic AI, weakest against neural architectures that recover principles known to operate in biological networks.

**No falsification condition.** The essay is unfalsifiable in its current form: any new structured prior that succeeds can be reclassified as "general purpose" after the fact (as convolution and attention have been). A stronger statement of the thesis would specify what would count as a legitimate exception — what kind of structural prior, if successful, would refute the Bitter Lesson rather than be absorbed into it.

**Conflation of "search and learning" as a single category.** Search (MCTS, minimax, gradient-based planning) and learning (SGD, self-supervised pretraining) are technically distinct mechanisms with different scaling properties. Modern LLM pretraining is almost pure learning with no explicit search at training time; AlphaZero combines them. The essay does not distinguish their compute-efficiency curves or address regimes where one dominates.

## 7. Connection to our work

This essay names, more sharply than any other piece in the database, the strategic gamble underlying the user's architectural program. The user is *deliberately* hand-engineering an architecture around biologically-derived inductive biases — Feedback Transformer integration of cortical-style feedback (program thread §1), GridCell RNNs structured as a V1→V2→V4→IT hierarchy (§3), descending conv projections and ascending conv-transpose projections that mirror the layer-6-corticocortical / pulvinar-mediated descending pathway (§3), competition-emergent predictive coding as the inter-hub dynamic (§5), an iterative variational encoder–decoder organized like cortical forward/backward reasoning (§4). Every one of these is a structural commitment of exactly the kind the Bitter Lesson predicts will be obsoleted.

**The wager.** The user's program rests on a wager that biologically-aligned inductive biases are *not* the species of fragile hand-engineering Sutton critiques. The wager has three parts.

1. *The brain is the existence proof.* Generalized cylinders, SIFT, and phonetic-tract speech models were hand-engineered descriptions of the *world*, designed without reference to any working biological system that uses them. The user's priors — hierarchical feedback, multi-compartmental memory, biased competition, free-energy regularization — are not designer intuitions about the world; they are *recovered structural facts about the brain*, the only existing system that is robustly general-purpose. The brain is the relevant out-of-sample data point that the Bitter Lesson's case studies omit.
2. *Biological priors are compute-multipliers, not compute-substitutes.* Convolution and attention are now uncontroversially "general methods" in Sutton's typology, but both started as inductive biases — translation equivariance, sparse pairwise interaction. The user's priors are claimed to be of the same character: a Feedback Transformer that admits arbitrary recurrent memory feedback is a *more general* attention primitive than vanilla self-attention, not a less general one. A multi-compartmental memory hierarchy with descending and ascending projections is a *more general* class of recurrent architecture than a flat LSTM. If this framing is correct, the priors *enable* more efficient use of compute rather than substituting for it.
3. *Sample efficiency matters as compute scaling flattens.* The Bitter Lesson assumes endless cheap compute. As that assumption weakens (data exhaustion, training-cost scaling, energy limits), inductive biases that match the structure of the data become the dominant lever. The user's program is explicitly designed for change-detection and small-video tasks where data is bounded and biological-prior sample efficiency is decisive.

**The risk.** The wager could lose. If pure scale-and-search continues to dominate — if a sufficiently large flat transformer, trained on enough video, simply matches or exceeds the user's hierarchical feedback architecture on every benchmark that matters — then neuroscience-aligned design is irrelevant in the long run, and the user's program would be remembered (at best) as an interesting failed bet. The published Recurrent ViT (2502.10955) is, in this framing, the riskiest single artifact: it is a hand-engineered recurrent attention variant competing in an era where the scaling-only camp owns the empirical lead. PRISM v1 (`THESIS.md`), which entirely replaces softmax attention with prediction-error gating, is even more exposed; it bets against attention itself, which Sutton's argument would treat as a settled general-purpose primitive.

**Conditions under which the wager pays off.** The program's defense becomes empirically decisive under any of three conditions: (a) compute scaling visibly plateaus (energy / data / capital limits), making sample efficiency the dominant competitive axis; (b) systematic OOD generalization remains out of reach for pure scaling, vindicating structural priors as the path to it; (c) the recovered biological priors prove to themselves be scaling-friendly meta-methods — that is, the Feedback Transformer, GridCell RNN, and hub-competition primitives keep improving as their parameter counts and training budgets increase, joining convolution and attention in the "general purpose" category retrospectively.

**Specific tensions with the program.**

The *Feedback Transformer* (program thread §1) integrates up to twelve hand-specified feedback sources. Sutton would predict that a less structured method — say, a deep flat transformer with arbitrary cross-attention — eventually matches its performance with more compute. The user's defense is that the FT is the *general* primitive of which flat transformers are a special case (zero feedback sources), and that the per-source Q/K/V structure is no more "hand-engineered" than multi-head attention itself. The wager is that this primitive will scale: more feedback sources, deeper hierarchies, more parameters, with the same architectural skeleton.

The *V1→V2→V4→IT hierarchical structure* with descending and ascending conv projections (program thread §3) hardcodes a specific spatial-pooling schedule. Sutton would predict that learned attention over a flat token grid eventually subsumes this. The user's defense is that the descending/ascending structure encodes capacity-allocation priors (channels grow as spatial resolution shrinks) that are about resource scaling, not domain content — closer to the convolution prior (which Sutton implicitly accepts) than to SIFT features (which Sutton rejects).

*Competition-emergent predictive coding* (program thread §5) imposes a multi-hub competition structure. Sutton would call this a hand-engineered theory of mind. The user's defense, made in the program thread itself, is that the competition mechanism is a *meta-method* — the architecture does not specify *what* the hubs compete to represent; it specifies that competition for self-attention bandwidth is the gradient-descent pressure that produces representational specialization. In Sutton's vocabulary, the user is arguing this is a meta-method that "captures arbitrary complexity," not a substantive theory of cognition baked in.

The *iterative variational encoder-decoder* (program thread §4) commits to $n_{FR}$ forward-reasoning and $n_{BR}$ backward-reasoning passes — explicit recurrent structure where a flat encoder would compute in a single pass. Sutton's critique would be that recurrence is a fragile prior absorbed by sufficiently deep feedforward networks. The user's defense is that iterative refinement is the structural commitment behind *every* successful planning system (AlphaZero's MCTS rollouts, diffusion models' denoising steps, chain-of-thought) — making it a candidate "general method" rather than a domain-specific one.

**Connections in the database.**

LeCun's *Path Towards Autonomous Machine Intelligence* (`lecun2022_path_to_agi`) is the cleanest contemporary that also rejects pure-scale orthodoxy and commits to architectural structure (H-JEPA, world models, configurator). Both LeCun's program and the user's program are bets against the Bitter Lesson, but LeCun bets on *energy-based hierarchical prediction* as the right structural prior while the user bets on *biologically-grounded multi-compartmental feedback with hub competition*. LeCun's bet is more conservative — his priors are abstract (latent prediction, hierarchy) and could plausibly be reabsorbed into the "general methods" category. The user's bet is bolder — explicit cortical anatomy is harder to retrofit as a meta-method.

Hawkins 2021 (`hawkins2021_thousand_brains`) makes a stronger neuroscience-realist version of the same bet — that cortical column structure is *the* substrate of general intelligence and must be replicated. Hawkins is the closest pole on the opposite side from Sutton: full architectural realism about biological structure. The user's program sits between Hawkins and Sutton — committed to biologically-derived primitives (cortex-style feedback, multi-compartmental memory) but trained by gradient descent on standard losses, not by replicating cortical learning rules.

Marcus 2025 (`marcus2025_llm_critique`) is the loudest external voice arguing the Bitter Lesson is misread — that scaling does not deliver compositional generalization and that hybrid neurosymbolic structure is needed. Marcus's case complements the user's neuroscience-grounded one: both argue that flat scaling will plateau on some axis (compositionality for Marcus, sample efficiency / OOD for the user) where structural priors win.

Schmidhuber 2015 (`schmidhuber2015_learn_to_think`) is Sutton's intellectual neighbor on the search-and-learning side — the coupled controller / world-model framework is exactly the kind of "meta-method that finds structure" the Bitter Lesson advocates. The user's competition-emergent predictive coding (program thread §5) is an explicit generalization of Schmidhuber's two-RNN system to many objective-specific hubs, all of which both implement and exploit predictive models of the others. This positions the user's program as continuing Schmidhuber's lineage rather than opposing it.

Sutton's own RL lineage — `sutton1988_td`, `sutton_barto2018_rl_intro`, and the policy-gradient line via `schulman2016_gae` and `schulman2017_ppo` — is where the *search and learning* commitment of the Bitter Lesson is operationalized. The PPO + GAE machinery that the user's PRISM systems use to train their RL hubs is the empirical instantiation of Sutton's preferred half of the field; in this narrow sense the user's program *adopts* the Bitter Lesson's prescription at the training-objective layer while resisting it at the architectural layer.

**Bottom-line framing.** The Bitter Lesson is not a refutation of the user's program but it is the strongest external statement of the program's principal risk. The defense the program has to make — and the defense `threads/the_user_architectural_program.md` implicitly makes — is that biologically-grounded inductive biases are meta-methods in Sutton's sense: they *enable* search and learning to operate on a richer hypothesis space (recurrent feedback, multi-compartmental memory, hub competition) rather than substituting for them. Whether that defense holds is, ultimately, an empirical question that the change-detection, video-VAE, and multi-hub-competition experiments are designed to answer.

## 8. Citations to follow

The essay itself cites no specific papers. The natural follow-ups are the empirical artifacts of the four case studies it inventories, and the principal published responses to the essay:

- `silver2016_alphago` — the search + self-play learning system that delivered the Go case study. Worth adding; the canonical empirical instance of "search and learning."
- `silver2018_alphazero` — the more general successor that strips out even more domain knowledge. Worth adding as the cleanest scaling-of-meta-methods data point.
- `krizhevsky2012_alexnet` — the compute-crossover moment in computer vision; the empirical end of the SIFT era. Worth adding.
- `kaplan2020_scaling_laws` — the post-essay empirical formalization of the compute-vs-performance curves the Bitter Lesson predicts. Worth adding as the quantitative successor to Sutton's qualitative argument.
- `hoffmann2022_chinchilla` — the compute-optimal data/parameter scaling refinement. Worth adding.
- `mitchell2021_ai_a_guide` and `marcus_davis2019_rebooting_ai` — the principal book-length critiques arguing the Bitter Lesson is misread. Background for the inductive-bias defense.
