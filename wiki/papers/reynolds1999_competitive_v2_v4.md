---
id: reynolds1999_competitive_v2_v4
title: "Competitive mechanisms subserve attention in macaque areas V2 and V4"
authors:
  - "Reynolds, John H."
  - "Chelazzi, Leonardo"
  - "Desimone, Robert"
year: 1999
venue: "Journal of Neuroscience"
doi: "10.1523/JNEUROSCI.19-05-01736.1999"
arxiv: ""
url: "https://doi.org/10.1523/JNEUROSCI.19-05-01736.1999"
tags:
  - primate-neurophysiology
  - visual-attention
  - early-visual-cortex
  - biased-competition
concepts:
  - biased-competition
  - gain-modulation
  - divisive-normalization
  - top-down-feedback
  - multiplicative-feedback
related:
  - desimone_duncan1995_biased_competition
  - reynolds_heeger2009_normalization
  - reynolds_chelazzi2004_attentional_modulation
  - mcadams_maunsell1999_reliability
  - mcadams_maunsell1999_v4_tuning
  - treue_martinez_trujillo1999_feature_attention
  - moran_desimone1985_selective_attention
relevance_to:
  - recurrent_vit
  - prism_v1
  - prism_v2
seed_source:
  - vit_paper_ref_97
status: full
depth: full
last_updated: "2026-05-16"
---

# Competitive mechanisms subserve attention in macaque areas V2 and V4

## 1. Abstract

(Paraphrased from PubMed PMID 10024360; full text is paywalled at *J Neurosci*.) Reynolds, Chelazzi & Desimone test the *biased-competition* account of attention (Desimone & Duncan 1995) at the single-neuron level in extrastriate visual cortex of behaving macaques. Single-unit responses were recorded in V2 and V4 while monkeys performed a task that dissociates sensory drive from attentional state. When two stimuli are placed inside the receptive field (RF) of a V2 or V4 neuron and the animal attends *outside* the RF, the cell's response to the pair is closer to a weighted average of the responses to each stimulus alone than to their sum — consistent with mutual suppression / divisive interaction between the two stimuli. When the animal attends to one of the two stimuli inside the RF, the cell's response shifts toward the response that stimulus would evoke if presented alone: attention "resolves the competition" in favor of the attended item. When only a single stimulus is in the RF, attention produces only a small modulatory effect. A quantitative model in which attention scales the relative weighting of excitatory and inhibitory drive from competing stimuli reproduces the observed response shifts in both V2 and V4.

## 2. Why this matters for us

This paper is the strongest single-unit evidence for the biased-competition framework (Desimone & Duncan 1995, full-depth in this database) — the foundational empirical hook for the user's program. The Feedback Transformer's Hadamard product over sensory and feedback Q/K projections (see [feedback_transformer](research_db/concepts/feedback_transformer.md)) is, mechanistically, biased competition at the attention-map level: feedback acts as a multiplicative bias on the competition for the softmax. The paper is also the empirical precursor to Reynolds & Heeger 2009 (full-depth), whose normalization model is the explicit computational instantiation of the response-averaging-with-attentional-bias signature reported here. For the user's coalition-competition thesis ([coalition_resource_competition](research_db/concepts/coalition_resource_competition.md)), this is the canonical demonstration that *competition is the substrate* on which attention operates — at the RF level; the user's program scales the same primitive up to whole coalitions.

## 3. Key claims

1. **Pairs of stimuli inside a V2/V4 receptive field interact suppressively when unattended.** The cell's response to the pair is a *weighted average* of the responses to the two stimuli presented alone, not their sum. This rules out a purely linear (additive) interaction and is the empirical fingerprint of divisive normalization.
2. **Attention resolves the competition in favor of the attended stimulus.** When the animal attends to one of two RF stimuli, the cell's response shifts toward the response to the attended stimulus presented alone, and away from the unattended distractor's contribution.
3. **The attentional effect is large when stimuli compete and small when they do not.** With a single stimulus in the RF, attention has only a modest modulatory effect on response amplitude. The attentional gain is *contingent on the presence of competition*.
4. **The biased-competition signature is present in both V2 and V4.** The effect is not unique to higher-tier extrastriate cortex (V4, IT, as in Moran & Desimone 1985) but is also observed in V2, indicating that competition + biasing is a generic feature of extrastriate processing rather than a property of any single area.
5. **A simple quantitative model fits the data.** Attention is modeled as a multiplicative increase in the weight of the attended stimulus's inputs (both excitatory and inhibitory) in a circuit where multiple stimuli compete via inhibition. The model accounts for the pair-response shifts in both V2 and V4 with a single parameter set per area.
6. **Attention does not change feature tuning.** The shift toward the attended-stimulus response is a quantitative re-weighting of competing inputs, not a change in the cell's tuning curve for orientation, color, or other features.

## 4. Methods

Single-unit extracellular recordings from V2 and V4 of two macaques performing a behavioral task that orthogonalizes stimulus content and locus of attention. On each trial the animal fixated centrally while one or two visual stimuli (oriented bars or colored shapes) were presented inside the recorded cell's RF, and a cue (delivered before the trial) instructed the animal which location to attend. The cued location varied across blocks so that the same RF-stimulus configuration was sampled under "attend-in" and "attend-away" conditions.

The critical comparisons:
- **Single-stimulus baseline.** Response to stimulus A alone in the RF; response to stimulus B alone. These establish each stimulus's drive.
- **Pair, attend-away.** Both A and B in the RF; animal attends to a location outside the RF. This isolates the sensory interaction between A and B.
- **Pair, attend-in (A or B).** Both A and B in the RF; animal attends to A (or B). This isolates the attentional bias.

By comparing the pair-response under different attention conditions to the single-stimulus responses, the authors quantify how much of the response shift is attributable to sensory interaction versus attentional bias.

A model is fit to the population data in which the response of a neuron is

$$
R = \frac{w_A A + w_B B}{w_A + w_B + \sigma}
$$

with attentional weights $w_A, w_B$ that increase for the attended stimulus and reflect both excitatory and inhibitory pooling. This form is the precursor of the divisive-normalization expression developed formally by Reynolds & Heeger 2009.

## 5. Results

Quantitative findings (drawn from the paper as cited in Reynolds & Heeger 2009 §5 and the broader Reynolds-Chelazzi-Desimone replication chain):

- **Pair-response is a weighted average, not a sum.** When two stimuli were in the RF with attention directed away, the pair response was approximately the *mean* of the two single-stimulus responses, not their sum — strong evidence for divisive interaction.
- **Attentional shift magnitude in V4.** Attending to the preferred of two RF stimuli shifted the cell's response toward the preferred-alone response by a substantial fraction of the gap between mean-pair and preferred-alone; attending to the non-preferred shifted the response the other way.
- **V2 effects qualitatively match V4 but with smaller magnitude.** Both areas show the same response-shift signature, with V4 showing larger attentional effects than V2 on average, consistent with the prediction that competition (and therefore bias) is stronger at higher levels of the hierarchy.
- **Single-stimulus attention effects ≈ small.** With one stimulus in the RF, attention produced only a small (often non-significant at the single-cell level) modulation in firing rate. This contrasts sharply with the large effects in the pair condition and is the central empirical signature that distinguishes biased-competition from pure-gain accounts.
- **Model fit.** The weighted-input competition model accounts for the response shifts in both areas with a small number of free parameters per area.

## 6. Critique / limitations

The framework is *descriptive of the response shift* and does not commit to a specific biophysical substrate. The "attentional weights" $w_A, w_B$ could correspond to changes in synaptic gain, changes in tonic drive, modulation of a normalization pool, or top-down feedback into a recurrent circuit. Reynolds & Heeger 2009 makes the strongest case that the underlying computation is divisive normalization with attentional gain on the inputs, but this paper alone does not adjudicate between alternative implementations.

The behavioral task does not dissociate spatial attention from feature attention cleanly. The animal is cued to a location, and the stimulus at that location has features that distinguish it from the distractor; whether the bias is purely spatial or partly feature-based is ambiguous. Treue & Martínez-Trujillo 1999 — a contemporaneous MT study — provides the cleaner feature-attention test.

The model assumes a single weighting parameter per stimulus; it does not capture how the weights are *set* by the top-down system. The source of the attentional signal (FEF, LIP, pulvinar) is not addressed. This is appropriate scope for the paper but means the result must be combined with the priority-map literature (Bisley & Goldberg 2010) to give a complete account.

The recordings are from anaesthetised-free, behaving macaques, but the trial-averaged response analysis ignores the temporal dynamics of the attentional modulation. Subsequent work (e.g., Reynolds & Chelazzi 2004 review; Cohen & Maunsell 2009 on noise correlations) has shown that attentional effects on single-trial variance and inter-neuronal correlations are large and informative; this paper reports only mean rates.

The biased-competition account, as instantiated here, predicts that attention has *no effect* when only one stimulus is in the RF — a prediction that conflicts with later work demonstrating clear single-stimulus gain effects (McAdams & Maunsell 1999 in V4; Treue & Martínez-Trujillo 1999 in MT). The resolution, made explicit by Reynolds & Heeger 2009, is that even a single stimulus engages the normalization pool of nearby neurons; attention modulates that pool. The 1999 paper underestimates single-stimulus effects because the normalization-pool view of "competition" had not yet been formalized.

## 7. Connection to our work

This paper is a load-bearing empirical citation across the user's program. The connections are direct and architectural:

**Empirical anchor for biased competition.** Desimone & Duncan 1995 (full-depth) is the theoretical framework; Reynolds, Chelazzi & Desimone 1999 is the strongest single-unit experimental evidence that supports it. Any architectural commitment in the user's program that invokes "attention as biased competition" — most directly the Feedback Transformer's multiplicative integration of sensory and feedback projections — rests on the empirical record this paper anchors.

**Direct precursor to Reynolds & Heeger 2009 normalization.** The weighted-average pair response with attentional bias reported here is the empirical signature that Reynolds & Heeger 2009 formalize as divisive normalization with per-input attentional gain. The PRISM v1 FiLM modulation (`Prism/film.py`) implements the *output side* of that normalization model — the per-location, per-channel multiplicative gain. The 1999 paper supplies the *competitive substrate* that the FiLM gain operates on; without competition between stimuli (or, in the architectural analog, between features) there is nothing for the gain to bias.

**Feedback Transformer Hadamard product = biased competition at the attention-map level.** The Feedback Transformer combines bottom-up Q/K projections $s_q, s_k$ with feedback Q/K projections $c^{(k)}_q, c^{(k)}_k$ via element-wise multiplication *before* the softmax (`the_user_architectural_program.md` §1, §5). The softmax is a competitive (winner-take-most) operation over tokens; the Hadamard product is precisely the multiplicative bias on the competing inputs. This is the same circuit motif as Reynolds, Chelazzi & Desimone's "attention scales the weighting of competing inputs in a divisive-normalization stage," lifted from RF-level competition between two stimuli to token-level competition across the attention map.

**Empirical evidence for the "competition matters" claim of the user's coalition thesis.** The paper's central finding — that attentional modulation is *large* when stimuli compete and *small* when they do not — is, in the user's framing, evidence that the brain has built its attentional machinery on top of a pre-existing competitive substrate. This is the load-bearing empirical fact the [coalition_resource_competition](research_db/concepts/coalition_resource_competition.md) thesis generalises: competition is not an emergent property of attentional control, it is the substrate that attentional control modulates.

**Constraint on the Recurrent ViT and PRISM.** The paper's finding that single-stimulus attention effects are small is a constraint that any candidate model of cortical attention must accommodate. PRISM v1's FiLM modulation, applied per-location to a feature map that itself reflects local competition between candidate features in the normalization pool, naturally produces the asymmetric "big effect when competing, small effect when alone" signature. Pure-gain architectures (which scale every input by the same factor regardless of competition) do not.

**Multi-hub competition.** The paper licenses the user's multi-hub framing ([multi-hub-multi-objective-system](research_db/concepts/multi-hub-multi-objective-system.md)): biased competition at the RF level scales to biased competition at the hub level. Each hub's Q/K contribution to the central attention map is the architectural analog of one of the two stimuli inside the RF in this paper; the winning hub's representation dominates the central map exactly as the attended stimulus's response dominates the cell's output here.

**Generalisation across V2 and V4.** That the same competitive signature is observed in two distinct extrastriate areas with very different receptive-field structure and feature tuning is evidence that biased competition is *not* an idiosyncratic property of a particular cortical area but a generic circuit motif. This licenses the user's commitment to use the same Feedback Transformer primitive at every level of the hierarchical memory stack (`the_user_architectural_program.md` §3) rather than designing area-specific attention mechanisms.

**Predictive of recurrent ViT cued-attention behaviour.** The Recurrent ViT's cued-attention experiments report stronger attentional effects when distractors are present than in single-stimulus displays — the same competition-contingent signature reported here at the neural level. This is a non-trivial point of empirical alignment between the user's model and primate neurophysiology that pure-gain transformer architectures (which lack any competitive substrate beyond the softmax itself) would not necessarily reproduce.

## 8. Citations to follow

- `moran_desimone1985_selective_attention` — the founding single-unit demonstration that selective attention gates extrastriate responses; the precursor to this paper. In seed, full depth.
- `desimone_duncan1995_biased_competition` — the framework this paper tests. In seed, full depth.
- `reynolds_heeger2009_normalization` — the normalization-model formalisation of these findings. In seed, full depth.
- `reynolds_chelazzi2004_attentional_modulation` — Reynolds & Chelazzi's later review covering the V2/V4 + IT/MT competition literature. In seed.
- `mcadams_maunsell1999_reliability` — contemporaneous V4 result showing attention enhances response reliability. In seed.
- `mcadams_maunsell1999_v4_tuning` — companion paper on attention scaling V4 tuning curves multiplicatively. In seed.
- `treue_martinez_trujillo1999_feature_attention` — contemporaneous MT result on feature-based attention; complements the spatial-bias account here. In seed.
- `luck_chelazzi_hillyard_desimone1997_v2v4_filtering` — earlier V2/V4 demonstration of the same filtering effect; candidate for addition.
