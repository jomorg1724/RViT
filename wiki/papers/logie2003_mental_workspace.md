---
id: logie2003_mental_workspace
title: "Spatial and Visual Working Memory: A Mental Workspace"
authors:
  - "Logie, Robert H."
year: 2003
venue: "Psychology of Learning and Motivation (vol. 42, pp. 37-78)"
doi: "10.1016/S0079-7421(03)01002-8"
arxiv: ""
url: "https://www.sciencedirect.com/science/article/pii/S0079742103010028"
tags:
  - working-memory
  - review
  - theoretical-essay
concepts:
  - working-memory-persistent-activity
  - feature-binding
related:
  - luck_vogel2013_wm_capacity_review
  - awh2006_attention_wm
  - panichello_buschman2021_shared_mechanisms
  - hollingworth2008_vstm_function
  - bays2024_wm_representation
relevance_to:
  - prism_v1
  - prism_v2
seed_source:
  - prism_private_notes
status: full
depth: full
last_updated: "2026-05-16"
---

# Spatial and Visual Working Memory: A Mental Workspace

## 1. Abstract

A chapter-length theoretical synthesis in the *Cognitive Vision* volume of *Psychology of Learning and Motivation* (vol. 42, pp. 37-78, Academic Press, 2003). Logie reviews evidence that visuospatial working memory (VSWM) is best understood not as a passive store but as a *mental workspace* — an active substrate in which visual and spatial representations are held, combined, manipulated, refreshed, and used to drive imagery, mental rotation, mental synthesis, and spatial reasoning. The chapter consolidates Logie's longstanding fractionation of the Baddeley visuospatial sketchpad into two functionally dissociable subsystems: a *visual cache*, a passive store of visual surface form (colour, shape, texture), and an *inner scribe*, an active sequential-spatial mechanism for movement, rehearsal, and refresh of cached content. Evidence is drawn from dual-task selective interference, neuropsychological dissociation, individual differences, and imagery work. The workspace framing argues that VSWM is *productive* — it constructs and transforms representations, it is not merely a buffer — and that this is what makes it cognitively useful for vision, action planning, and reasoning. Logie's broader claim is that visuospatial cognition cannot be understood without a workspace concept: imagery, planning, and many forms of reasoning are workspace operations on cached content, and the empirical signature of an operation (its interference profile, its capacity cost, its individual-differences variance) is the signature of a manipulation done within the workspace rather than of a separate cognitive faculty.

## 2. Why this matters for us

Logie 2003 supplies the *cognitive-science precedent* for treating visuospatial working memory as an **active, manipulable workspace** rather than as a passive snapshot store. This is the conceptual posture the user's program adopts at the architectural level: the Recurrent ViT's persistent hidden state $H^{(t-1)}$ and PRISM's iterative variational decoder both treat memory as a substrate that is *iteratively refined* during a task rather than written once and read once. The "mental workspace" idiom is the precise cognitive-science framing for the iterate-and-refine dynamics the user's program implements computationally. The chapter is in the user's `prism_private_notes` cite trail specifically because it provides the cleanest extant statement of WM-as-workspace, with the visual-cache / inner-scribe fractionation providing a useful analog for the user's multi-compartmental memory commitments.

## 3. Key claims

1. **VSWM is a mental workspace, not a passive store.** Visuospatial representations held in WM can be *manipulated, combined, rotated, scanned, and transformed*. Capacity-limited content is operated upon, not merely retained, and this operational character is what makes VSWM cognitively useful.
2. **The visuospatial sketchpad fractionates into a visual cache and an inner scribe.** The visual cache passively stores visual surface form (colour, shape, pattern); the inner scribe is an active mechanism that processes spatial and movement information and rehearses / refreshes the cache. The two subsystems are functionally specialised but routinely interact.
3. **The two subsystems are doubly dissociable.** Selective interference from concurrent visual tasks (e.g., irrelevant pictures) disrupts visual-cache content; selective interference from concurrent spatial/movement tasks (e.g., spatial tapping) disrupts inner-scribe function. Neuropsychological dissociations show patients with selective deficits in one but not the other.
4. **VSWM supports mental imagery.** Image generation, maintenance, scanning, and inspection draw on the same workspace as VSWM tasks proper. The chapter argues against treating imagery as a separate faculty distinct from VSWM.
5. **VSWM is closely coupled to but separable from verbal WM and the central executive.** Concurrent verbal tasks selectively impair phonological-loop performance; concurrent executive load (e.g., random-number generation) impairs workspace operations that require active control of the workspace's content.
6. **Manipulation is the load-bearing function.** Tasks that merely require storage place light demand on the workspace; tasks that require combining, transforming, or rotating representations expose the workspace's capacity and structure. The interesting variance in VSWM performance is in the manipulation regime, not the storage regime.
7. **Capacity is fractional and content-specific.** The workspace shows ~4-item-like capacity limits for static items, but capacity drops further when manipulation is required, and the bottleneck is at the manipulation-and-refresh stage rather than the storage stage per se.
8. **Imagery and perception share substrate.** VSWM-as-workspace predicts (and the literature supports) overlap of mechanisms used for perceiving and for imagining the same visual content. Visual imagery is, on this view, perception turned inward and run on the workspace's own contents.
9. **VSWM is constructive.** New representations are built within the workspace by combining, segmenting, or transforming existing content; the workspace's productivity (in the linguistic sense) is what underwrites visual creativity, mental synthesis, and counterfactual scene construction.
10. **The workspace is online, not offline.** Workspace content is used to drive ongoing action and perception, not merely to be retrieved later. This is the functional argument for why a system whose memory is *workspace-like* is more useful than one whose memory is a passive log.

## 4. Methods

A narrative theoretical review and synthesis. Logie marshals four lines of evidence:

- **Dual-task selective interference.** A primary VSWM task is performed concurrently with a secondary task that selectively loads either visual content (visual interference) or spatial/movement content (spatial interference), and the resulting impairment pattern is used to dissect the workspace's substructure. The logic is that if subsystem A and B are independent, secondary tasks loading A should impair primary tasks that depend on A but not those that depend on B, and vice versa.
- **Neuropsychological dissociations.** Brain-injured patients showing selective impairment of visual-cache content vs. inner-scribe-mediated rehearsal are cited to establish biological reality of the fractionation. Double dissociations between visual and spatial WM patients carry particular weight, since they are difficult to explain on a single-resource account.
- **Individual-differences correlations.** Performance on VSWM, imagery, and reasoning tasks is correlated to argue for a shared underlying workspace, with the pattern of correlations and dissociations interpreted as evidence for the substructure.
- **Imagery experiments.** Mental-rotation, mental-scanning, and image-generation paradigms are used to argue that the workspace is *productive* — it actively constructs and transforms representations rather than only retaining them.

The chapter is theoretical/integrative; it does not report new empirical data but argues from the prior literature (much of it the author's own). The argumentative strategy is to converge on the workspace claim from four independent methodological angles rather than to rest on a single experimental signature.

## 5. Results

The chapter is integrative rather than reporting fresh numbers, but the key empirical regularities it consolidates:

- **Visual interference (e.g., irrelevant flashing pictures during retention) selectively disrupts memory for static visual surface form** (colour patches, abstract shapes) more than memory for spatial sequences.
- **Spatial / movement interference (e.g., spatial tapping, arm movements during retention) selectively disrupts memory for spatial sequences** (Corsi-block patterns, movement paths) more than memory for static visual form.
- **Articulatory suppression (verbal interference) does not selectively disrupt VSWM**, replicating earlier double dissociations between phonological loop and sketchpad.
- **Concurrent executive load (e.g., random generation) disrupts manipulation tasks** (mental rotation, mental synthesis) more than pure-storage tasks of equivalent set size, isolating the *manipulation* component from the *storage* component.
- **VSWM span is ~3-4 items for static visual surface form** and similar for spatial sequences, consistent with the broader VSTM capacity literature (Luck & Vogel 1997; see [luck_vogel2013_wm_capacity_review](research_db/papers/luck_vogel2013_wm_capacity_review.md)).
- **Imagery tasks load the workspace.** Mental scanning, image inspection, and mental rotation produce interference patterns indistinguishable from explicit VSWM tasks, supporting the claim that imagery is a workspace operation.
- **Manipulation costs are separable from storage costs.** When set size is held constant, adding a manipulation requirement (e.g., rotating each item by 90 degrees before report) increases error rates and slows responses in a manner that cannot be reduced to a storage-capacity effect. The workspace's bottleneck has at least two components: how much it can hold and how much it can transform.
- **Visual cache content is more decay-prone than inner-scribe-rehearsed content.** Cached visual surface form decays over seconds in the absence of inner-scribe refresh; rehearsed content is more robust. The empirical signature distinguishing the two subsystems is a difference in temporal robustness.
- **Imagery generation places a heavy load on the workspace.** Generating a novel mental image from instructions (rather than retrieving a familiar one) is among the most demanding workspace operations, consistent with the productive-workspace claim.

## 6. Critique / limitations

The fractionation into visual cache and inner scribe is one of several competing accounts of VSWM substructure. Continuous-resource accounts (Bays-style, see [bays2024_wm_representation](research_db/papers/bays2024_wm_representation.md)) and feature-bundle accounts argue against discrete subsystems with their own capacity. The selective-interference evidence on which Logie relies is open to alternative explanations involving general processing competition rather than dedicated subsystem load: a single shared resource that is differentially taxed by visual vs spatial concurrent tasks could in principle produce the same dissociation pattern without any subsystem fractionation.

The "mental workspace" claim is metaphorical at the cognitive level and does not by itself specify a computational mechanism. The chapter does not commit to a particular neural or algorithmic implementation, which is both a strength (it abstracts away from premature commitments) and a weakness (it does not generate strong falsifiable predictions about substrate).

The chapter precedes the modern primate-electrophysiology and human-neuroimaging literatures that have refined our picture of where and how VSWM is implemented — e.g., the parietal / occipital persistent-activity work of Christophel and colleagues, the PFC-as-domain-general-controller account of [panichello_buschman2021_shared_mechanisms](research_db/papers/panichello_buschman2021_shared_mechanisms.md), and the transient-activity / activity-silent debate around Lundqvist and Stokes. The workspace framing is consistent with these but predates them.

The dissociation between storage and manipulation, while empirically robust, is not formalized in the chapter. Subsequent computational work (e.g., resource-allocation models, attractor-network models of WM) has done more to make the manipulation operation precise.

The chapter focuses on healthy adult cognition; developmental and clinical literatures are touched on but not central. Cross-species comparison is largely absent — there is no engagement with primate-electrophysiology evidence on the neural substrate of WM-as-workspace, which has since become the most empirically detailed line of evidence on the topic.

Finally, the chapter does not engage with reinforcement-learning or active-inference accounts of WM. Subsequent computational frameworks that treat WM as the substrate for variational free-energy minimisation (Friston 2010 and successors) or for control-theoretic action selection are silent in the chapter; the workspace framing is purely descriptive-cognitive rather than normative-computational.

## 7. Connection to our work

Logie 2003 is the *cognitive-science articulation* of the architectural posture the user's program adopts toward memory: WM is **not a passive snapshot** but an **active workspace in which representations are iteratively constructed, combined, refreshed, and manipulated**. This is the conceptual basis for several specific commitments in the program.

**The Recurrent ViT's persistent hidden state as a workspace.** The published Recurrent ViT (2502.10955) treats $H^{(t)}$ as a state that is *updated and used* at every recurrent step, not as a buffer that is written once at encoding and read once at retrieval. Logie's workspace framing licenses this design philosophy: the model's memory should be doing work between observations, not merely holding content. The "iterate-and-refine" dynamics observed in the Food-101 classification experiments (see thread `the_user_architectural_program`, §6) — where attention maps focus, defocus, and reactivate over recurrent passes — are the computational analog of workspace manipulation operations: the system is doing something with its memory across recurrent steps, not merely storing.

**Iterative variational encoder-decoder (PRISM v2 direction).** The user's iterative-VAE construction (thread `the_user_architectural_program`, §4) explicitly runs $n_{FR}$ forward-reasoning passes and $n_{BR}$ backward-reasoning passes over the same input, with reconstruction proposals refined at each backward step. This is the *strongest* expression of WM-as-workspace in the user's program: the decoder *manipulates its latent / hidden state* over $n_{BR}$ steps to produce successively better reconstructions of the target, exactly as Logie's workspace combines and transforms its content to produce useful outputs. Logie 2003 is the cognitive-science precedent that motivates this design choice as something more than an engineering convenience — it is a computational instantiation of an empirically supported cognitive primitive. Each backward-reasoning step in PRISM v2 is, in Logie's terms, a workspace operation: the decoder takes its current guide state and current latent, applies a transformation, and produces an updated proposal — the operation is *productive* in exactly Logie's sense, generating a new representation from existing content.

**Visual cache / inner scribe as analog for multi-compartmental memory.** Logie's fractionation of VSWM into a *passive content store* and an *active rehearsal/manipulation mechanism* is a coarser cognitive-level analog of the user's multi-compartmental memory commitment (thread `the_user_architectural_program`, §3). The user's design is finer-grained — multiple GridCell RNN states at different hierarchical levels, each with its own resolution and update timescale — but the same architectural intuition is operative: a useful WM is **not a single bag of slots** but a **structured ensemble of differently-purposed states** that communicate via dedicated machinery (the Feedback Transformer in the user's program; verbal-spatial coupling in Logie's). The visual cache / inner scribe split is not isomorphic to the user's layer-1 / layer-2 / layer-3 split, but it shares the structural commitment that different aspects of "memory" are handled by different mechanisms operating in coordination.

**Manipulation is load-bearing.** Logie's claim that manipulation is the load-bearing function of VSWM directly motivates evaluating PRISM and the Recurrent ViT not just on storage-style change-detection but on tasks that require *manipulation*: mental rotation, scene composition, prediction of future scenes from a partial observation. PRISM v2's decoder direction (`PRISM_V2_PROPOSAL.md` §3.4) is precisely such a manipulation-demanding setting. Future evaluation protocols should adopt manipulation-heavy benchmarks; Logie's chapter is the citation that grounds why this matters.

**Imagery-perception substrate overlap.** Logie's claim that imagery and perception share substrate is consistent with the user's program's commitment that the encoder and decoder are *structurally identical* instances of the same multi-compartmental memory stack (thread, §4). If imagery is workspace manipulation under the same mechanisms used for perception, then an encoder-decoder pair that uses the *same architecture* for both is the natural computational expression of that claim.

**Refresh as iterative update.** Logie's inner scribe is explicitly characterised as a *refresh* mechanism that prevents decay of cached visual content by re-instantiating it. The Recurrent ViT's recurrent update of $H^{(t)}$ at every time step is a natural computational analog: rather than letting a memory state decay or freeze, it is re-derived from itself plus current sensory input. The conceptual move "memory is something you *do*, not something you *have*" is identical in both cases. PRISM v1's inner variational-inference loop over $M_t$ (THESIS.md §2.8) is an even more direct analog: each inner step is a refresh in Logie's sense, with the variational objective playing the role of a normative criterion for "good" refresh.

**Connection to luck_vogel2013_wm_capacity_review.** The Luck & Vogel discrete-slot framework is concerned with the *storage* dimension of WM — how many items can be held. Logie's workspace framing is orthogonal: even granting a ~4-item capacity, the more important question is what is *done* with those items. The two frames are complementary rather than competing, and any computational model of WM (the user's program included) needs to make commitments along both axes: how much it stores, and what it does with what it stores.

**Where Logie does not constrain us.** The chapter is cognitive-level and does not specify neural or algorithmic mechanism. The user's program goes further than Logie does in this respect, committing to specific computational primitives (Feedback Transformer, GridCell RNN, iterative variational rollout). Logie 2003 is best read as a *conceptual umbrella* under which the user's specific architectural commitments sit, not as a constraint on what those commitments should be. The chapter is most usefully cited alongside [awh2006_attention_wm](research_db/papers/awh2006_attention_wm.md) (for the attention-WM coupling) and [panichello_buschman2021_shared_mechanisms](research_db/papers/panichello_buschman2021_shared_mechanisms.md) (for the modern primate-electrophysiology articulation of WM as a dynamically transformed substrate) to give a single coherent triangulation: WM is an active, manipulable, attention-coupled substrate whose representations are transformed in service of behaviour.

**Relation to Hollingworth, Richard & Luck 2008.** [hollingworth2008_vstm_function](research_db/papers/hollingworth2008_vstm_function.md) makes a complementary functional claim: VSTM (or VSWM) is the substrate for transsaccadic object correspondence and gaze correction — that is, it is used *in service of moment-to-moment perception and action*, not as a retrospective log. This is the *behavioural-ecological* counterpart of Logie's *cognitive-architectural* workspace claim. Read together, the two papers establish that VSWM is (a) structured as a workspace with active manipulation machinery and (b) deployed in service of ongoing perception. The Recurrent ViT and PRISM's commitment to a memory state that is used at every recurrent step, not at a retrieval phase, is licensed by both claims jointly.

**Relation to Awh, Vogel & Oh 2006.** [awh2006_attention_wm](research_db/papers/awh2006_attention_wm.md) makes the case that attention and WM share substrate. Logie's workspace framing is consistent with this — a workspace that is operated on by attentional control is exactly what Awh and colleagues describe — but Logie's particular contribution is to insist that the WM side of the coupling is itself *internally articulated* (visual cache + inner scribe + executive control), not a single state. The user's program inherits both commitments: a multi-compartmental memory (Logie) that is in tight coupling with the central self-attention substrate (Awh).

## 8. Citations to follow

- `baddeley_hitch1974_working_memory` — the founding 1974 paper that introduced the multi-component WM model on which Logie's workspace fractionation rests. Not in seed; should be added as a foundational entry.
- `baddeley2000_episodic_buffer` — Baddeley's 2000 addition of the episodic buffer to the WM model, complementary to Logie's workspace framing. Not in seed.
- `logie_pearson_baddeley1994_visuospatial` — earlier empirical paper laying out the visual-cache / inner-scribe dissociation. Not in seed.
- `kosslyn1994_image_brain` — Kosslyn's imagery-as-perception framework, parallel to Logie's workspace claim. Not in seed.
- `pearson_logie2014_workspace_imagery_review` — modern update of the workspace framing with neuroimaging evidence. Not in seed.
- `christophel2017_distributed_wm` — distributed neural substrate of WM that the workspace claim should map onto. Not in seed.
- `lundqvist2018_gamma_bursts_wm` — activity-silent / burst-based WM, contemporary counterpoint to persistent-activity views. Not in seed.
- `logie2023_workspace_revisited` — Logie's recent restatement and update of the workspace claim. Cited in user's notes as the 2023 companion to this 2003 chapter. Not in seed.
- `cowan2001_magical_number_4` — Cowan's "embedded processes" account of WM, partly complementary to and partly competing with Logie's framing. Not in seed.
- `shepard_metzler1971_mental_rotation` — the founding mental-rotation paper that the workspace concept must accommodate. Not in seed.
- `kosslyn_thompson_ganis2006_imagery_debate` — modern synthesis of the imagery-as-perception debate that Logie's chapter feeds into. Not in seed.
