---
id: silver2005_topographic_parietal
title: "Topographic maps of visual spatial attention in human parietal cortex"
authors:
  - "Silver, Michael A."
  - "Ress, David"
  - "Heeger, David J."
year: 2005
venue: "Journal of Neurophysiology"
doi: "10.1152/jn.01316.2004"
arxiv: ""
url: "https://doi.org/10.1152/jn.01316.2004"
tags:
  - human-neuroimaging
  - parietal-cortex
  - visual-attention
concepts:
  - priority-map
  - retinotopy
  - topographic-organization
  - attentional-spotlight
related:
  - bisley_goldberg2010_parietal_priority
  - bisley_mirpour2019_priority_map
  - mirpour2010_ppc_microstim
  - desimone_duncan1995_biased_competition
  - thomsen2005_conflicting_cues_fmri
relevance_to:
  - recurrent_vit
seed_source:
  - vit_paper_ref_82
status: full
depth: full
last_updated: "2026-05-15"
---

# Topographic maps of visual spatial attention in human parietal cortex

## 1. Abstract

Functional magnetic resonance imaging (fMRI) was used to measure activity in human parietal cortex during performance of a visual detection task in which the focus of attention systematically traversed the visual field. Critically, the stimuli were identical on all trials (except for slight contrast changes in a fully randomized selection of the target locations) whereas only the cued location varied. Traveling waves of activity were observed in posterior parietal cortex consistent with shifts in covert attention in the absence of eye movements. The temporal phase of the fMRI signal in each voxel indicated the corresponding visual field location. Visualization of the distribution of temporal phases on a flattened representation of parietal cortex revealed at least two distinct topographically organized cortical areas within the intraparietal sulcus (IPS), each representing the contralateral visual field. Two cortical areas were proposed based on this topographic organization, which we refer to as IPS1 and IPS2 to indicate their locations within the IPS. This nomenclature is neutral with respect to possible homologies with well-established cortical areas in the monkey brain. The two proposed cortical areas exhibited relatively little response to passive visual stimulation in comparison with early visual areas. These results provide evidence for multiple topographic maps in human parietal cortex.

## 2. Why this matters for us

Silver, Ress & Heeger 2005 is the human-fMRI counterpart of the macaque LIP literature (Bisley & Goldberg 2003; Goldberg et al. 2002). It demonstrates that the human intraparietal sulcus contains *retinotopically organized* maps of attention — IPS1 and IPS2 — in which voxel activity at a parietal location signals attention deployed at a specific visual-field location. This is the human-cortex anatomical substrate that the recurrent ViT's self-attention map most directly mirrors: the ViT's attention map is patch-retinotopic — each entry is indexed by an input patch location, and the activation pattern over patches *is* a spatial priority distribution. Silver et al. supply the empirical evidence that human cortex actually maintains such a retinotopic priority distribution at a parietal level above V1/V2/V3, and that the distribution dissociates from passive stimulation (i.e., it is attention-specific, not stimulus-specific).

## 3. Key claims

1. Posterior parietal cortex contains at least two distinct topographically organized attention maps — IPS1 and IPS2 — within the intraparietal sulcus.
2. Each map represents the contralateral visual field retinotopically, with the temporal phase of the fMRI signal in each voxel indicating the corresponding visual-field location.
3. The maps were revealed using a *traveling-wave* paradigm in which the cued attended location systematically rotated around the visual field while the bottom-up stimulus configuration was held constant.
4. The IPS maps are *attention-driven*, not stimulus-driven: passive visual stimulation produced much weaker responses in IPS1 and IPS2 than in early visual areas, even though the same stimuli drove robust retinotopic responses in V1/V2/V3.
5. The naming is intentionally neutral with respect to monkey homologies — Silver et al. avoid claiming IPS1/IPS2 are the human "LIP" — but the functional profile (retinotopic, attention-modulated) is the same.
6. The result establishes that retinotopic organization is a general principle of attentional control areas, not just of early sensory cortex.

## 4. Methods

Eight subjects performed a covert-attention contrast-discrimination task during 3T fMRI. The visual display contained eight peripheral stimulus locations arranged on a ring; on each trial subjects fixated centrally and covertly attended one location, judging a small contrast increment at that location. The cued location rotated systematically around the ring across trials, producing a *traveling wave* of attended location over time.

Crucially, the *physical stimulus was identical* across cuing conditions — only the cued location (and thus the locus of covert attention) varied. Eye position was monitored to confirm that the attentional shifts were covert. Functional images (spiral k-space readout; Glover 1999) were acquired and motion-corrected (Nestares & Heeger 2000; Jenkinson et al. 2002).

The analysis treats each voxel's BOLD time series as a periodic signal whose *phase* indicates which attended location maximally drives it. Voxels whose response is coherent with the cue-rotation frequency are mapped, and their phase is color-coded on a flattened cortical surface reconstruction (Wandell et al. 2000; Teo et al. 1997). The phase map reveals retinotopic organization: smoothly varying phase across the cortical surface = topographic representation of the visual field.

Separate scans used standard rotating-wedge / expanding-ring retinotopy (Engel et al. 1994; Sereno et al. 1995; DeYoe et al. 1996) to localize V1, V2, V3, V3A, V4, V7, and to compare passive-stimulation responses to attention-driven responses.

## 5. Results

- **Two new topographic areas, IPS1 and IPS2**, located in the intraparietal sulcus posterior to standard parietal landmarks. Both lie anterior to V7 in the dorsal stream.
- **Contralateral hemifield representation** in each: voxels in left IPS1/IPS2 respond when attention is in the right hemifield, and vice versa, with smoothly varying phase consistent with a continuous retinotopic map.
- **Polar-angle mapping** is the principal organizing axis; eccentricity organization is weaker (a limitation discussed below).
- **Attention-driven vs stimulus-driven dissociation**: the same voxels that show strong attention-driven phase responses show *much smaller* responses to identical stimuli presented passively (subjects performing a fixation task). The amplitude reduction is several-fold relative to V1/V2 responses on the same stimuli.
- **Eye-movement control**: eye-tracker monitoring confirmed that the rotating-attention trials produced no systematic saccadic pattern; the parietal phase maps therefore reflect covert attention, not eye position.
- The companion paper (Schluppeck, Glimcher & Heeger 2005, *J Neurophysiol* 94:1372–1384; same issue) reports the same retinotopic IPS1/IPS2 organization during *delayed saccades*, demonstrating that the maps also serve overt-action planning — exactly as expected of a priority-map substrate.

## 6. Critique / limitations

The paper does not claim direct homology to macaque LIP. IPS1/IPS2 are defined functionally (retinotopic and attention-driven); whether they correspond to LIP, VIP, MIP, or to some human-specific area is left open. Subsequent work (Sereno, Pitzalis & Martinez 2001; Sereno & Huang series; Konen & Kastner 2008) has expanded the count of human IPS retinotopic areas to four or more (IPS0–IPS5), and the relationship to macaque LIP remains imperfectly resolved.

The traveling-wave paradigm enforces a particular cue dynamic — uniform rotation through equally-spaced locations. This biases the analysis toward voxels with smoothly tiled spatial preferences and may understate non-retinotopic forms of attentional organization (feature- or object-based; cf. Bisley & Goldberg 2010 §6 on the spatial bias of priority-map work).

Eccentricity mapping is weaker than polar-angle mapping. Whether this reflects coarser eccentricity tuning at the IPS level or a methodological artifact (limited eccentricity coverage; rotation at a single ring radius) is not fully resolved.

The contrast between attention-driven and passive-stimulation responses establishes that IPS1/IPS2 are not simple sensory areas, but does not directly identify the *integration rule* by which the maps combine bottom-up and top-down inputs. Computational models of the integration (saliency-plus-template; biased competition; normalization with attentional gain) are not tested here.

BOLD fMRI is correlative. The paper does not establish *causal* contribution of IPS1/IPS2 to attentional deployment. Causal evidence for parietal contribution to attention comes from TMS, lesion, and patient studies (Posner et al. 1984; Mesulam 1999) — these are not engaged in this paper.

## 7. Connection to our work

Silver, Ress & Heeger 2005 supplies the **human-cortex retinotopic substrate** for the user's program, complementing the macaque single-unit framework (Bisley & Goldberg 2010 — `papers/bisley_goldberg2010_parietal_priority.md`).

**The recurrent ViT's attention map as IPS-analog.** The recurrent ViT (2502.10955) computes a self-attention map indexed by patch locations: each entry $\alpha_{ij}$ corresponds to attention from patch $i$ to patch $j$, and the row-summed pattern over patches is a *retinotopic priority distribution*. This is structurally exactly what IPS1/IPS2 implement: a map over visual-field locations whose amplitude at each location signals attentional priority. Silver et al. give the empirical license to interpret the ViT attention map this way — they show human cortex actually computes a stimulus-independent retinotopic attention map at a level above V1/V2.

**The central self-attention substrate (multi_hub_multi_objective_system) as an IPS/SPL-analog.** The user's [multi_hub_multi_objective_system](research_db/concepts/multi_hub_multi_objective_system.md) places a shared self-attention substrate at the center, integrating bottom-up sensory input and top-down memory/RL contributions to produce a priority distribution that drives downstream behavior. The biological analog is the parietal priority-map system: IPS1/IPS2 (and adjacent IPS/SPL areas) maintain a retinotopic representation of priority that integrates inputs from many sources and drives both attentional gain and saccade selection. Silver et al. is the imaging-level evidence that such a shared map exists in human cortex.

**Attention vs stimulus dissociation as an architectural commitment.** The Silver et al. result that IPS responses are attention-driven, not stimulus-driven, supports the user's commitment to *separating* the attention map from the feature representation. The ViT self-attention map is structurally separate from the V/feature stream (Q and K vs V); biological cortex achieves the same separation by having distinct cortical areas (V1 for stimulus, IPS for attention). The architectural principle — that priority and feature content occupy different representational pages — has cortical support.

**Multiple retinotopic maps as multi-compartment evidence.** Silver et al. identify *two* IPS retinotopic maps; subsequent work has identified more. This is the cortical analog of the user's commitment to a stack of recurrent priority-bearing representations in the [multi_compartmental_memory](research_db/concepts/multi_compartmental_memory.md) hierarchy: multiple priority-bearing maps, each potentially at a different level of abstraction, all retinotopically organized. The ViT's single-layer attention map is a simplification of this multi-map cortical organization; PRISM v2's hierarchical memory ([PRISM_V2_PROPOSAL.md](Prism/docs/PRISM_V2_PROPOSAL.md) §3.3–3.4) begins to recover it.

**Concrete ViT-paper hook.** The recurrent ViT paper cites Silver et al. (ref 82) when arguing that the recurrent ViT's attention-map dynamics are biologically interpretable. The full-depth deepening of this entry licenses citing Silver et al. directly when the manuscript discusses what the recurrent attention map *is* in cortical terms.

## 8. Citations to follow

- `bisley_goldberg2003_lip_attention` — Bisley & Goldberg's foundational single-unit demonstration of LIP attention coding. Not yet in seed; central reference for the macaque counterpart.
- `goldberg2002_attention_parietal` — Goldberg, Bisley et al.'s earlier review of LIP's role in saccades and visuospatial attention. Not yet in seed.
- `corbetta_shulman2002_attention_review` — *Nat Rev Neurosci* review of the dorsal/ventral attention networks. Foundational human-imaging review. Not yet in seed; high priority.
- `sereno_pitzalis_martinez2001_retinotopic_parietal` — earlier *Science* paper mapping contralateral space in human parietal cortex retinotopically. Direct predecessor. Not yet in seed.
- `schluppeck_glimcher_heeger2005_delayed_saccades` — companion paper showing IPS1/IPS2 also organize delayed saccades. Establishes the priority-map (attention+action) interpretation. Not yet in seed.
- `kastner1999_directed_attention` — Kastner et al. *Neuron* paper on baseline IPS activity during directed attention without visual stimulation. Foundational. Not yet in seed.
- `tootell1998_retinotopy_attention` — Tootell et al. *Neuron* paper on retinotopy of visual spatial attention in occipital cortex. The occipital counterpart to Silver et al.'s parietal finding. Not yet in seed.
- `yantis2002_parietal_attention_shifts` — Yantis et al. *Nat Neurosci* on transient parietal activity during attention shifts. Related to dynamic attention deployment. Not yet in seed.
- `wandell_brewer_dougherty2005_visual_field_clusters` — Wandell et al. visual-field-map clusters framework that informs the IPS map ontology. Not yet in seed.
- `hopfinger2000_top_down_control` — Hopfinger, Buonocore & Mangun *Nat Neurosci* on neural mechanisms of top-down attentional control. Connects parietal maps to frontal control. Not yet in seed.
