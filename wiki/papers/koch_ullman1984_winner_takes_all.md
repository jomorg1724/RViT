---
id: koch_ullman1984_winner_takes_all
title: "Shifts in selective visual attention: towards the underlying neural circuitry"
authors:
  - "Koch, Christof"
  - "Ullman, Shimon"
year: 1985
venue: "Human Neurobiology"
doi: ""
arxiv: ""
url: "https://pubmed.ncbi.nlm.nih.gov/3836989/"
tags:
  - saliency-models
  - visual-attention
  - theoretical-essay
concepts:
  - attentional-spotlight
  - priority-map
  - divisive-normalization
related:
  - itti_koch2001_saliency_review
  - desimone_duncan1995_biased_competition
  - bisley_goldberg2010_parietal_priority
  - posner1980_orienting
  - treisman_gelade1980_feature_integration
  - reynolds_heeger2009_normalization
relevance_to:
  - recurrent_vit
  - prism_v1
seed_source:
  - vit_paper_ref_124
status: full
depth: full
last_updated: "2026-05-16"
---

# Shifts in selective visual attention: towards the underlying neural circuitry

## 1. Abstract

The paper proposes a neural mechanism for selective visual attention. Koch & Ullman argue that early visual processing computes a set of elementary features (color, orientation, direction of motion, binocular disparity) in parallel across retinotopic feature maps, and that selective attention operates by mapping from these multiple early representations into a single, non-topographic central representation that at any moment contains the properties of only one visual location. The selection mechanism is a **Winner-Take-All (WTA) network** operating on a combined *conspicuity* (later "saliency") map: lateral inhibition among map locations forces a single peak to dominate, designating the attended location. After selection, transient inhibition of the winning location ("inhibition of return") releases the WTA to settle on the next-most-salient location, producing automatic sequential shifts of the attentional spotlight. Proximity and similarity preferences bias which location is selected next. The authors speculate on candidate neural substrates including back-projections from cortex to LGN and the role of the pulvinar. The paper is purely theoretical; no simulation results are reported.

## 2. Why this matters for us

This is the founding computational model of visual attention. Every subsequent saliency-map architecture (Itti & Koch 2001, the entire LeMeur 2006 / 2010 fixation-prediction literature) and every learned-attention mechanism in modern vision (including the Recurrent ViT) descends from the Koch-Ullman WTA construction. The softmax used in standard self-attention is mathematically a soft, differentiable WTA over tokens; PRISM v1's saliency-gated update is functionally a WTA on the prediction-error map. The paper appears as `vit_paper_ref_124` in 2502.10955 specifically because the Recurrent ViT's attention mechanism is the modern, learned, differentiable, multi-head continuation of Koch & Ullman's selection rule.

## 3. Key claims

1. Early visual cortex computes multiple **feature maps** in parallel (color, orientation, motion direction, stereoscopic disparity), each retinotopically organized and tuned to a single elementary feature.
2. Selective attention requires a **bottleneck**: a single, non-topographic central representation that at any moment holds properties of only one spatial location, into which the contents of one feature-map location are routed.
3. Selection is performed by a **Winner-Take-All network** over a combined "conspicuity" (saliency) representation. Mutual lateral inhibition produces a single active peak corresponding to the attended location.
4. After selection, **transient suppression** (inhibition of return) of the winning location allows the WTA to converge on the next-most-conspicuous location, producing automatic sequential scanning of the scene without supervisory control.
5. Additional rules bias the WTA dynamics: **proximity preference** (the next selected location tends to be near the current one) and **similarity preference** (locations sharing features with the current focus are favored).
6. Plausible neural substrates include corticothalamic back-projections from V1 to LGN as a gating mechanism, and pulvinar / parietal cortex as candidate saliency-map sites.

## 4. Methods

This is a theoretical proposal, not an experiment or simulation. The authors lay out the architecture verbally and sketch the circuitry; the equations below are the canonical formalization of their construction (the 1985 paper itself uses prose and block diagrams).

The **feature maps** $F_k(x, y)$ are retinotopic 2D arrays, one per elementary feature $k$ (color contrast, orientation, motion direction, disparity). The values are bottom-up feature responses, each computed by parallel populations of feature-tuned neurons in early visual cortex. Koch & Ullman emphasize that these maps are computed *in parallel and without attention*; attentional selection is downstream of the feature-extraction stage.

The **conspicuity map** $C(x, y)$ is a centralized scalar map combining the feature maps into a single representation of "where in the visual field is something interesting?" The combination rule is not formally specified in the 1985 paper — the authors note only that conspicuity should reflect feature contrast (a location is conspicuous if its features differ from its neighbors). Itti, Koch & Niebur (1998) and Itti & Koch (2001) later supplied the canonical center-surround + across-scale normalization formula that operationalizes this combination.

The **WTA network** is a recurrent neural circuit over the conspicuity map. Each location $(x, y)$ has a unit with self-excitation and broad lateral inhibition obeying a continuous-time dynamics of the form

$$\tau \dot u(x, y) = -u(x, y) + C(x, y) - \alpha \sum_{(x', y') \neq (x, y)} f(u(x', y'))$$

where $f(\cdot)$ is a sigmoidal nonlinearity and $\alpha$ controls the strength of lateral inhibition. With sufficiently strong inhibition the dynamics converge to a state in which the single location with maximal input has $u > 0$ and all other locations have $u \approx 0$ — the "winner" representation of attention. The fixed-point is a one-hot indicator over locations.

**Inhibition of return** is implemented as a slow adaptation / suppression at the winning location: once $u(x^*, y^*)$ has been read out into the central representation, a suppressive signal $-I_\text{IOR}(x^*, y^*; t)$ subtracts from $C(x^*, y^*)$ for a refractory period of several hundred milliseconds, allowing the WTA to relax and rediscover a new peak elsewhere. This produces automatic sequential scanning without any supervisory routing signal.

**Proximity and similarity preferences** are imposed as additional modulations of $C$: locations near the previous winner or sharing features with it receive small additive boosts. These biases account for the empirical observation that successive fixations cluster spatially and that featurally-related distractors capture attention more often than featurally-unrelated ones.

**Candidate neural substrates** the authors propose: V1 and extrastriate cortex for the feature maps; pulvinar, posterior parietal cortex, or superior colliculus for the saliency/conspicuity map; corticothalamic back-projections from V1 to LGN as a possible gating mechanism that suppresses feature-map activity at unattended locations.

## 5. Results

The paper reports no simulation or experimental results. Its contribution is the architectural proposal — the *organization* of a candidate neural circuit. The "results" of the paper are therefore architectural commitments rather than measurements:

- a parallel-feature-map / single-saliency-map / WTA-selection / IOR-driven-shifting decomposition of the attention problem;
- a specific prediction that attention is implemented by lateral inhibition over a centralized priority representation rather than by gain modulation distributed across feature maps;
- a specific prediction that sequential fixation shifts arise from refractory dynamics rather than from explicit eye-movement control.

Subsequent computational instantiations validated the first two. Itti, Koch & Niebur (1998) and Itti & Koch (2001) showed the architecture, with explicit center-surround feature maps and Gaussian pyramids, reproduces human free-viewing fixation distributions on natural images at substantially above chance levels (typically AUC ~0.7–0.8 against eye-tracking ground truth, depending on dataset). The third prediction — IOR-driven sequential coverage — has substantial behavioral support (Klein 2000 review) but the precise neural locus of IOR remains contested. The 1985 paper itself stops at the architectural sketch; everything quantitative is downstream.

## 6. Critique / limitations

The paper is a theoretical position piece without simulation, formal proof, or neural data; almost all of its specific claims are speculative as stated. Three load-bearing assumptions deserve scrutiny.

First, the **single-saliency-map bottleneck**. Koch & Ullman assume a single, central, location-coded conspicuity map. Subsequent work has substantially complicated this picture: LIP (Bisley & Goldberg 2010), FEF, SC, and pulvinar all carry priority/saliency-like signals, and the "priority map" is now understood as distributed across these structures rather than localized. The architectural claim of a single map is wrong in detail but right in spirit.

Second, the **purely bottom-up framing**. The 1985 paper treats saliency as bottom-up feature conspicuity, with top-down influences entering only through proximity/similarity rules. Desimone & Duncan (1995) and the biased-competition literature subsequently argued the top-down contribution is far more central, and modern accounts (Bisley & Goldberg 2010) treat the priority map as integrating bottom-up salience and top-down task relevance on equal footing. The Recurrent ViT's learned attention is far more in the biased-competition spirit than the Koch-Ullman spirit.

Third, **hard WTA versus soft selection**. The hard-WTA dynamics select a single location at a time. Behavioral and neural data show attention is graded, divisible (in some paradigms), and parametrically modulated by stimulus contrast and task — better captured by divisive normalization (Reynolds & Heeger 2009) or softmax-style soft selection than by hard WTA. The differentiable softmax used in modern attention mechanisms is the natural relaxation, and it is the form actually adopted in all subsequent computational models including Itti & Koch (2001) (whose readout is graded) and every learned-attention deep-network mechanism.

Fourth, the **conspicuity-map combination rule is unspecified**. The 1985 paper does not say how feature maps are combined into a single $C(x, y)$. This was operationally important: different combination rules (max, sum, normalized sum, learned weights) produce qualitatively different attention behavior on real images. Itti, Koch & Niebur (1998) had to engineer a specific center-surround + across-scale normalization scheme to make the architecture work on natural images. The unspecified-combination-rule issue is in some sense the *raison d'être* for learned attention: the modern softmax over learned features sidesteps the question entirely by letting gradient descent choose the combination.

Fifth, **no learning**. The Koch-Ullman architecture is hand-designed; no mechanism is proposed by which the feature maps, the conspicuity map, or the WTA parameters are *learned* from experience. The contrast with modern learned-attention systems is total. Whether the architecture would even work at scale on natural images was an open question for the next thirteen years until Itti, Koch & Niebur (1998) demonstrated a working instantiation.

The paper also predates the modern understanding of feature-integration (Treisman & Gelade 1980 is contemporaneous but not yet woven in here), the Posner cueing literature's chronometric constraints (Posner 1980), and the entire body of priority-map neurophysiology. As a 1985 sketch it cannot be faulted for this, but a present-day reader should treat it as a *seed* rather than a *theory*.

## 7. Connection to our work

The architectural lineage from Koch-Ullman 1985 to the user's research program runs through three successive generalizations, and articulating it clarifies what is and is not novel in the modern systems.

**Generalization 1: hard WTA → differentiable soft WTA.** The Koch-Ullman WTA is a discrete dynamical system that converges to a one-hot indicator over locations. The softmax operation used in transformer self-attention ($\alpha_i = e^{q^\top k_i} / \sum_j e^{q^\top k_j}$) is a temperature-controlled relaxation: as the temperature drops, softmax approaches hard WTA; at finite temperature it produces a graded, differentiable selection that supports gradient-based training. The Recurrent ViT (2502.10955) self-attention layer is, under this view, a multi-head soft-WTA over patches operating on the joint representation of bottom-up sensory features and recurrent memory feedback. The fundamental selection operation — pick the winner over a 2D map of locations — is unchanged from 1985. What changed is that the conspicuity values $C(x, y)$ are now learned bottom-up features combined multiplicatively with learned top-down memory queries (the Feedback Transformer construction), rather than hand-designed feature maps.

**Generalization 2: bottom-up saliency → prediction-error saliency.** PRISM v1's saliency map $S_t$ (THESIS.md §2.6) is a prediction-error map, not a feature-conspicuity map. The saliency-gated update (THESIS.md §2.7) is functionally a WTA on $S_t$: the locations with the largest prediction errors are the ones whose recurrent state gets updated most aggressively. This is the *Koch-Ullman selection rule applied to a Rao-Ballard residual* rather than to bottom-up feature contrast. It is the natural unification of the two founding theoretical traditions in computational attention.

**Generalization 3: receptive-field-level WTA → coalition-level WTA.** Koch & Ullman's WTA operates at the level of single locations in a single visual map. The user's *competition-emergent predictive coding* thesis (`the_user_architectural_program.md` §5) scales the same competitive selection principle to entire neural coalitions — hubs that compete for self-attention bandwidth across the whole architecture. The mechanism is the same (mutual inhibition among rivals, with the winner securing control of a shared representational resource); only the granularity changes. Koch-Ullman is the within-map limit; competition-emergent PC is the across-system extension.

The paper therefore belongs in the database as the **first commitment to selection-by-competition as the fundamental attentional operation**. Every architectural choice in the user's program that involves a softmax, a gated update, or competing memory states is, at root, doing what Koch & Ullman 1985 said attention must do — just learned end-to-end, applied to richer features, and scaled to richer competitors.

Two specific design implications:

- The Recurrent ViT's softmax (manuscript §3.2) is the differentiable form of the Koch-Ullman WTA. The connection licenses interpreting the attention map as a learned conspicuity map and the recurrent feedback as the top-down biasing input.
- PRISM v1's prediction-error gating (THESIS.md §2.7) is the Koch-Ullman selection rule on a Rao-Ballard residual. Inhibition of return — Koch & Ullman's mechanism for sequential scanning — has a direct analog in PRISM's temporal dynamics: once a region's prediction error is reduced by recurrent processing, the WTA naturally moves on to the next-highest-error region. This was not designed in; it falls out of the architecture, exactly as Koch & Ullman anticipated.
- The **central non-topographic representation** Koch & Ullman propose — the attended location's features routed into a downstream representation that holds one location's properties at a time — has a direct architectural analog in the user's iterative variational encoder-decoder (`the_user_architectural_program.md` §4): the encoder's "guide" state $H_t$ is updated over $n_{FR}$ forward-reasoning passes, with self-attention dynamics that focus and refocus the encoder onto different regions over recurrent steps. The qualitative attention-map dynamics the user reports on Food-101 ("maps focus, defocus, and reactivate over recurrent steps") are exactly what a learned, soft, multi-cycle Koch-Ullman WTA + IOR should produce. The 1985 paper predicted this behavior; the Recurrent ViT exhibits it as a learned emergent dynamic.

The cleanest statement of the relationship: **Koch & Ullman 1985 specified the *operation* that attention must perform** (competitive selection over a spatial map, with refractory dynamics that produce sequential coverage); **everything in the user's program supplies a different answer to the question "selection over *what map*, with *what feedback*, of *what competitors*"**. Bottom-up feature contrast (1985) → learned bottom-up + top-down memory features (Recurrent ViT) → prediction-error residuals (PRISM v1) → entire coalition activity (competition-emergent PC). The selection operation is invariant; the substrate on which it operates is what successive generations of the program rework.

## 8. Citations to follow

- `itti_koch2001_saliency_review` — already in the seed; the canonical computational instantiation of the Koch-Ullman architecture, supplying the formal feature-map combination rules the 1985 paper left unspecified.
- `treisman_gelade1980_feature_integration` — feature integration theory; contemporaneous behavioral framework for how parallel feature maps are bound at the attended location.
- `posner1980_orienting` — Posner cueing paradigm; the chronometric / behavioral data that any attentional-shift model (including this one) must explain.
- `desimone_duncan1995_biased_competition` — the principal modern alternative; attention as biased competition rather than bottom-up WTA. Critical contrast for §6.
- `bisley_goldberg2010_parietal_priority` — distributed priority-map account in LIP/FEF/SC/pulvinar that replaced the single-saliency-map assumption.
- `reynolds_heeger2009_normalization` — divisive normalization as the soft, graded selection mechanism that supplants hard WTA in modern models.
- `wolfe1994_guided_search` — Guided Search; integration of top-down task biases into a Koch-Ullman-style saliency-map architecture. Not yet in seed.
- `niebur_koch1996_wta_circuit` — explicit neural circuit implementation of the WTA mechanism; would deepen §4. Not yet in seed.
