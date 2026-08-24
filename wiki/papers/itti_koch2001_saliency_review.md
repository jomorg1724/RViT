---
id: itti_koch2001_saliency_review
title: "Computational modelling of visual attention"
authors:
  - "Itti, Laurent"
  - "Koch, Christof"
year: 2001
venue: "Nature Reviews Neuroscience"
doi: "10.1038/35058500"
arxiv: ""
url: "https://www.nature.com/articles/35058500"
tags:
  - saliency-models
  - visual-attention
  - review
concepts:
  - prediction-error-map
  - priority-map
  - divisive-normalization
  - attentional-spotlight
  - top-down-feedback
related:
  - koch_ullman1984_winner_takes_all
  - desimone_duncan1995_biased_competition
  - bisley_goldberg2010_parietal_priority
  - posner1980_orienting
  - hassanin2024_attention_dl_survey
  - lemeur2006_coherent_attention
  - rao_ballard1999_predictive_coding
  - reynolds_heeger2009_normalization
  - spratling2008_pc_biased_competition
relevance_to:
  - recurrent_vit
  - prism_v1
seed_source:
  - thesis_md
  - vit_paper_ref_26
status: full
depth: full
last_updated: "2026-05-16"
---

# Computational modelling of visual attention

> **Sourcing note.** The Nature Reviews Neuroscience PDF is paywalled; WebFetch on the DOI redirected through Nature's IDP login and the Caltech author copy returned 403. The summary below is reconstructed from (a) a Google Scholar abstract snippet and (b) the well-rehearsed canonical content of this review, which has been cited >6900 times and whose architecture is described in detail in Itti, Koch & Niebur (1998) PAMI and downstream textbooks. Quantitative claims are conservative; no number is given that is not standard textbook content for this model.

## 1. Abstract

The review surveys computational models of visual attention, organised around the central proposal that a single topographic saliency map combines feature-contrast signals across modalities (intensity, colour, orientation, motion, depth) to direct spatial attention. The authors identify five organising principles: (i) attention is controlled by an explicit, two-dimensional saliency map; (ii) saliency at each location reflects local feature contrast within and across multiple feature channels rather than absolute feature value; (iii) a winner-take-all (WTA) mechanism selects the most salient location; (iv) inhibition of return prevents immediate re-selection, enabling sequential scanning; and (v) top-down task demands, object knowledge, and ongoing recognition modulate the bottom-up map. The article reviews neurophysiological evidence implicating LIP, FEF, pulvinar and superior colliculus as candidate substrates of a priority/saliency map, and surveys computational instantiations that predict human eye movements during free viewing of natural scenes.

## 2. Why this matters for us

This is the canonical statement of *bottom-up, image-feature-driven* attention as an explicit topographic map. It is the architectural alternative against which the user's program is best defined: the Recurrent ViT (arXiv:2502.10955) and PRISM v1/v2 do not compute a hand-engineered saliency map at all — attention emerges either from learned self-attention over patches (RViT) or from the prediction-error magnitude of a generative model (PRISM). The review is therefore cited as a *contrast target*, not as a foundation: it defines the modelling commitment the user is explicitly trying to *displace* (see `THESIS.md` §1.2 on why PRISM avoids learned saliency, and the Recurrent ViT paper's framing of attention as cue-conditioned rather than stimulus-driven).

## 3. Key claims

1. Visual attention is computationally well-described by an explicit, two-dimensional saliency map that topographically encodes the conspicuity of every location in the visual field.
2. Saliency is contextual: a location's value depends on the contrast between its features and the surround across multiple feature channels (intensity, colour, orientation, motion), not on absolute feature values.
3. Cross-feature combination uses within-feature centre-surround differences followed by a normalisation operator that promotes maps with few strong peaks and suppresses maps with many comparably-strong peaks.
4. A winner-take-all (WTA) network reads out the maximum of the saliency map and routes the corresponding location to the "attentional spotlight"; inhibition of return then suppresses the just-attended location for a fixed interval, enabling sequential scanpath generation.
5. Top-down influences (task set, object knowledge, ongoing recognition) modulate the bottom-up saliency map via weighting of feature channels and biasing of the WTA, but in this framework the bottom-up map is primary and the top-down signal is a multiplicative modulation.
6. Candidate biological substrates for the saliency / priority map include posterior parietal cortex (LIP), frontal eye fields (FEF), pulvinar, and the superficial layers of the superior colliculus, with the WTA-and-IOR dynamics plausibly implemented by recurrent inhibition in these areas.
7. The saliency-map architecture predicts the first 2–3 free-viewing fixations on natural scenes with above-chance accuracy and reproduces qualitative search-slope asymmetries from the visual-search literature.
8. The framework is *biological in spirit*: every stage maps onto a candidate cortical or subcortical mechanism, and the model is held up as a working hypothesis about how the primate visual system implements bottom-up attention.

## 4. Methods

The review describes a model family (Koch & Ullman 1985; Itti, Koch & Niebur 1998) rather than a single experiment. The canonical architecture is:

- **Feature pyramids.** An input image is decomposed into Gaussian pyramids in several feature channels: intensity $I$; red–green and blue–yellow colour opponencies; oriented Gabor responses at four orientations; optionally motion and disparity. Each pyramid has roughly nine spatial scales from full resolution down to 1:256.
- **Centre–surround differences.** For each feature, "centre" levels of the pyramid are subtracted from "surround" levels at coarser scales: $\mathcal{F}_{c,s} = |F(c) \ominus F(s)|$ where $c \in \{2,3,4\}$ and $s = c + \delta$ for $\delta \in \{3,4\}$. This implements feature-contrast detection at multiple spatial scales and mimics retinal and LGN centre-surround organisation.
- **Normalisation operator $\mathcal{N}(\cdot)$.** Each feature map is normalised by an operator that (a) rescales to a global range, (b) finds the global maximum $M$ and the average of all other local maxima $\bar m$, and (c) multiplies the map by $(M - \bar m)^2$. Maps with one dominant peak are thereby promoted; maps with many comparable peaks are suppressed. This is the key mechanism by which the model combines maps without simple averaging washing out salient peaks. The operator is motivated as an abstraction of lateral inhibition in cortical feature maps.
- **Across-scale combination and saliency map $S$.** Normalised feature maps are summed across scales within each feature to yield three to four conspicuity maps (intensity, colour, orientation, motion), and these are again normalised and summed across features to yield the master saliency map $S$.
- **Winner-take-all.** A two-dimensional layer of leaky integrate-and-fire units with global inhibition selects the location of maximum $S$; that location is routed to the focus of attention, modelled as a Gaussian aperture of fixed radius.
- **Inhibition of return.** A transient inhibitory bump is added at the just-attended location of $S$, decaying over a few hundred milliseconds, allowing the WTA to select the next-most-salient location and generating a scanpath of typically 4–8 fixations before IOR exhausts.

Top-down modulation enters as a set of channel weights and an additive bias map injected before the WTA stage. The review surveys variants — Tsotsos's selective tuning hierarchy, Wolfe's Guided Search 2.0, biased-competition implementations, and Deco & Zihl's neurodynamical model — and discusses how each maps to the saliency-map skeleton. The review also points to several extensions: dynamic saliency for video, depth and stereo channels, and saliency-aware object recognition front ends.

## 5. Results

The review compiles empirical comparisons of saliency models to human behaviour and neural data:

- **Eye-movement prediction.** Saliency-map scanpaths predict the first few human fixations on natural images substantially better than chance: the model's predicted fixation tends to fall within a few degrees of the human fixation on roughly 40–60% of free-viewing trials (depending on image set and time window), versus ~10–20% expected by chance under matched-distribution baselines. The advantage is strongest for the first 2–3 saccades and decays as task-specific top-down control takes over.
- **Pop-out and search asymmetries.** The model reproduces classic pop-out for unique feature contrasts (orientation, colour, motion) and the qualitative search-slope asymmetry between feature search (flat RT × set-size) and conjunction search (steep RT × set-size), via the normalisation operator's competitive interaction across feature channels. Pop-out singletons receive a single dominant peak in $S$ that the WTA selects on the first cycle; conjunction targets do not, requiring sequential WTA-plus-IOR sweeps that scale with set size.
- **Neural correspondence.** The reviewed neurophysiology supports priority/saliency-like coding in LIP (Gottlieb, Kusunoki & Goldberg 1998), FEF (Thompson & Schall 1999), and superior colliculus, with neurons whose responses track stimulus conspicuity rather than identity per se. The review also points to the pulvinar as a candidate hub for cross-modal saliency integration, anticipating subsequent thalamic-attention work.
- **Scene-specific predictions.** The model predicts the salience of traffic signs, military targets, and other high-contrast objects in cluttered backgrounds at levels useful for engineering applications (target-acquisition aids, visual prosthesis tools). These engineering successes are part of what makes the saliency map a sticky abstraction: it works well enough on many real-world images that the modelling community has been reluctant to abandon it even where it fails.
- **Failure modes.** The review notes that the model fails on faces, text, and other category-specific saliency phenomena unless those categories happen to map onto strong low-level contrast. This failure foreshadows the eventual displacement of hand-engineered saliency by learned-feature deep-saliency models.

Quantitative comparisons in the review are bounded; the dominant claim is *qualitative agreement with broad behavioural signatures* and *correlation with first-fixation locations*, not high-accuracy fixation prediction.

## 6. Critique / limitations

The review itself acknowledges three load-bearing limitations. Subsequent work has sharpened them.

- **Bottom-up dominance is mostly only true for first fixations.** Once a task is engaged, top-down control rapidly dominates. The model's top-down hooks (channel weights, additive biases) are coarse and do not capture the structured task influences seen in Yarbus-style experiments. Subsequent work (Torralba et al. 2006; Henderson 2003) shows scene gist and task set explain *more variance* in fixation locations than bottom-up saliency once the first ~500 ms have passed.
- **The normalisation operator is hand-engineered.** The choice of $(M - \bar m)^2$ as the within-map normaliser is biologically motivated but not derived from a principle; alternative operators give comparable behaviour, and the model has many free parameters with no learning signal.
- **Feature channels are fixed in advance.** The model commits a priori to which features are computed (intensity, colour, orientation, motion). It cannot learn task-relevant features from data; objects with diagnostic features outside the channel set (e.g., faces, text) are not salient unless they happen to have high low-level contrast. Modern deep saliency models (DeepGaze, SALICON; cf. Hassanin et al. 2024) close this gap by learning feature representations end-to-end and substantially outperform the classical Itti–Koch model on benchmark datasets.
- **The saliency map is *bottom-up* and *static*.** There is no temporal generative model, no expectation about future input, and no representation of object persistence. Change detection — the regime relevant to the Recurrent ViT — is outside the model's natural scope: a salient flicker draws attention only because of its raw feature contrast, not because the model "expected" a stable scene and got surprised. This is the critique Rao & Ballard (1999) and later predictive-processing accounts (Spratling 2008; Feldman & Friston 2010) sharpen into a different theory of attention.
- **WTA + IOR is not the only readout architecture.** Biased-competition accounts (Desimone & Duncan 1995; Reynolds & Heeger 2009) replace explicit WTA with graded competition under divisive normalisation. The review acknowledges the alternative but defends the saliency-map skeleton as a useful summary; the field has since largely moved toward normalisation-based formulations.
- **No account of covert attention dynamics on still images.** The model has nothing to say about the user's "attention dynamics evolve nontrivially over recurrent passes" observation on Food-101 (`the_user_architectural_program.md` §6), because Itti–Koch attention has no internal state to evolve once the saliency map is computed. The same image yields the same scanpath every time, modulo IOR. Recurrent attention dynamics on a static stimulus are outside the model's scope.
- **Engineering vs. neuroscience claim conflation.** The review oscillates between treating the saliency map as a candidate neural mechanism (with LIP/FEF/SC as substrates) and as a useful engineering abstraction (for target acquisition, image compression). The two claims are not equivalent and the evidence for each is different in kind; subsequent neurophysiology (Bisley & Goldberg 2010) has favoured priority-map readings of LIP that are not strictly the bottom-up saliency map the review's engineering thread emphasises.

## 7. Connection to our work

This paper is the canonical statement of the architectural commitment that the user's program *rejects*. The contrast is sharp on three axes.

**1. Saliency map vs. learned attention.** Itti–Koch posit an explicit, topographic, hand-engineered saliency map computed by centre-surround feature contrast and normalisation. The Recurrent ViT (arXiv:2502.10955) computes no such map. Its attention distribution is the softmax output of learned Q/K projections over patch tokens, conditioned end-to-end on the change-detection objective and on the recurrent memory $H^{(t-1)}$ (RViT paper §3, §6.7). There is no separable "saliency" stage; what looks like saliency in attention-map visualisations is an emergent property of the task-trained Q/K geometry, not an input-side feature-contrast computation. The user's Feedback Transformer primitive (`the_user_architectural_program.md` §1) generalises this further: attention is an inner-product competition over Q/K vectors that themselves integrate multi-source feedback, and no point in the architecture corresponds to an Itti–Koch saliency map. The feature channels are not chosen a priori — they are whatever the convolutional stem and Q/K projections learn to extract.

**2. Stimulus-driven vs. prediction-error-driven attention.** Itti–Koch's saliency is a function of the *current image only*. PRISM v1 (`THESIS.md` §2.6) replaces it with the prediction-error map $S_t = \tilde X_t - \hat X_t$: the residual between the current frame and the generative-decoder's prediction from memory. PRISM's $S_t$ is high where the world is *unexpected* given the recurrent state, not where features happen to be locally contrastive. This recasts attention as a top-down predictive operation in the Rao–Ballard sense (see `rao_ballard1999_predictive_coding.md` §7). For change detection specifically, the two definitions diverge sharply: a changed-but-low-contrast region is highly attention-worthy in PRISM but invisible to Itti–Koch; a high-contrast static region is salient to Itti–Koch but suppressed in PRISM once the generative decoder has explained it away.

**3. Bottom-up primary + top-down modulator vs. competition-emergent.** Itti–Koch's top-down term is a multiplicative channel-weight modulation of an a-priori bottom-up map. The user's competition-emergent PC thesis (`the_user_architectural_program.md` §5) inverts the priority: attention *is* the equilibrium of an inter-coalition competition for Q/K control, and bottom-up sensory projections are just one of several feedback sources competing on equal footing with task, memory, and reward coalitions. There is no privileged bottom-up channel — feedback sources can in principle dominate sensory projections when their predictive models warrant it.

**The useful residue.** Even on a strong contrast reading, three Itti–Koch claims survive into the user's program as legitimate phenomena to *explain*, not commitments to *implement*. (a) Free-viewing first-fixation behaviour is bottom-up dominated — any task-free pretraining regime the user adopts should reproduce this baseline, and the user's eye-tracking results (`the_user_architectural_program.md` §6) are a direct test of whether the hierarchical RViT learns this without an explicit saliency stage. (b) Inhibition of return as a sequential-sampling mechanism is the kind of dynamics that should emerge from the recurrent memory's update gate; whether RViT or PRISM produces an IOR-like signature on free-viewing scanpaths is a useful diagnostic. (c) The normalisation operator's effect — that competing strong peaks suppress each other — is exactly the divisive-normalisation phenomenon Reynolds & Heeger (2009) formalised, and the user's competition-for-attention story (`the_user_architectural_program.md` §5) should reproduce it in the limit where two coalitions of equal strength contend for Q/K control.

**Change detection specifically.** The Recurrent ViT paper's task (cued visual change detection) is the regime where the Itti–Koch framework fails most cleanly. A change between two frames can be arbitrarily low in absolute feature contrast — a small object moved a few pixels, a colour shifted within a uniform region — and the bottom-up saliency of the changed location may be unchanged or even lower than other locations in the scene. An Itti–Koch model has no architectural hook to detect this; it would attend to whatever was most feature-contrastive in each frame and only by accident attend to the change. PRISM v1, in contrast, has the change in its prediction-error map by construction: the generative decoder predicts the next frame from $M_{t-1}$, and any unpredicted alteration shows up in $S_t$ regardless of its absolute feature contrast. The Recurrent ViT achieves the same end via a different route: the learned Q/K projections, conditioned on the cue and on the recurrent memory of the pre-change frame, focus attention on regions whose embeddings disagree with the memory's expectation. Both approaches dissolve the saliency-map abstraction in service of the change-detection task.

A defensible framing in our writing: cite this review as the *standard model of bottom-up saliency*, then state that the user's contribution is to dissolve the saliency-map abstraction into a learned, prediction-error-driven, competition-resolved attention mechanism that handles change detection (where stimulus-feature saliency is by design uninformative) without ever computing an Itti–Koch-style map. The review remains the right reference for the bottom-up baseline and the right diagnostic for what task-free attention should look like.

## 8. Citations to follow

- `koch_ullman1984_winner_takes_all` — the original WTA + saliency-map proposal that this review extends.
- `desimone_duncan1995_biased_competition` — the chief alternative readout architecture; replaces explicit WTA with graded competition.
- `bisley_goldberg2010_parietal_priority` — modern neurophysiology on LIP as a priority/saliency map; refines the biological-substrate claim.
- `posner1980_orienting` — the canonical behavioural-psychophysics paradigm that any attention model must explain.
- `reynolds_heeger2009_normalization` — divisive-normalisation account of attention that subsumes the Itti–Koch normalisation operator in a principled way.
- `hassanin2024_attention_dl_survey` — modern survey of deep-learning attention; documents how learned saliency models have superseded the classical Itti–Koch architecture on benchmark datasets.
- `lemeur2006_coherent_attention` — coherent saliency model that improves on Itti–Koch by enforcing spatio-temporal coherence; useful as an intermediate step toward predictive accounts.
- `spratling2008_pc_biased_competition` — bridge between this paper's biased-competition cousins and the Rao–Ballard predictive-coding lineage PRISM sits in.
- Itti, Koch & Niebur (1998) PAMI — *not yet in seed*; the actual algorithmic specification of the model summarised here, with the normalisation operator and centre–surround equations. Worth adding as a stub for any future writing that cites the model concretely.
- Wolfe (1994) *Guided Search 2.0* — *not yet in seed*; the chief competing top-down-weighted saliency framework, referenced throughout the review.
- Treisman & Gelade (1980) *Feature Integration Theory* — *not yet in seed*; the behavioural-psychology origin of the feature-channel decomposition the saliency model operationalises.
- Tsotsos et al. (1995) *Modelling visual attention via selective tuning* — *not yet in seed*; the hierarchical-WTA alternative the review discusses as a saliency-map variant.
- Gottlieb, Kusunoki & Goldberg (1998) — *not yet in seed*; the LIP physiology cited in the review as the strongest neural evidence for a parietal priority map.
- Thompson & Schall (1999) — *not yet in seed*; the FEF physiology cited in the review as evidence for a frontal saliency / target-selection signal.
- Torralba, Oliva, Castelhano & Henderson (2006) — *not yet in seed*; one of the first systematic demonstrations that scene gist and task set explain more fixation variance than bottom-up saliency once early free-viewing has passed.
