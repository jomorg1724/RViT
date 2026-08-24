---
id: oberauer2002_access_wm
title: "Access to information in working memory: exploring the focus of attention"
authors:
  - "Oberauer, Klaus"
year: 2002
venue: "JEP: LMC"
doi: "10.1037/0278-7393.28.3.411"
arxiv: ""
url: "https://pubmed.ncbi.nlm.nih.gov/12018494/"
tags:
  - working-memory
  - visual-attention
  - reaction-time
concepts:
  - working-memory-persistent-activity
  - attentional-template
related:
  - olivers2011_wm_states_attention
  - awh2006_attention_wm
  - kiyonaga_egner2013_wm_internal_attention
  - luck_vogel1997_wm_capacity
  - panichello_buschman2021_shared_mechanisms
relevance_to:
  - recurrent_vit
  - prism_v2
seed_source:
  - vit_paper_ref_16
status: full
depth: full
last_updated: "2026-05-14"
---

# Access to information in working memory: exploring the focus of attention

## 1. Abstract

Oberauer proposes a three-state model of working memory (WM) in which information is held at three nested levels of accessibility: (i) an *activated portion of long-term memory* containing a potentially large set of items in a heightened-availability state; (ii) a capacity-limited *region of direct access* holding a small number of items (roughly the canonical WM-capacity figure of about four) immediately available to cognitive operations; and (iii) a single-item *focus of attention* in which the currently-processed item resides. The model is tested with an arithmetic-on-digits paradigm in which participants maintain an "active" set of digits (operated on by upcoming arithmetic tasks) alongside a "passive" set (merely remembered). Reaction times scale with the size of the active set but not the passive set, and switching the operation from one digit to another produces robust object-switch costs. These results support the distinction between the focus of attention (one item), the region of direct access (active set), and activated LTM (passive set), and quantify the time required to move items between layers.

## 2. Why this matters for us

Oberauer 2002 is the canonical cognitive-psychology source for a *three-layered* working-memory architecture in which only a single item occupies the "focus of attention" at any moment, a small set of items is in a "region of direct access," and the rest is held in activated long-term memory. This is the cognitive-psychology counterpart to Olivers et al. 2011's active/accessory distinction and supplies the explicit vocabulary the user's program needs to describe what the Recurrent ViT and PRISM v2 do architecturally: the softmax attention map peaks on a single location ("focus of attention"); the rest of the recurrent state holds the broader scene ("region of direct access"); and PRISM v2's slow memory plays the role of the activated-LTM background. The three-layer hierarchy is also a cleaner match for the user's multi-compartmental memory than the binary active/accessory framing.

## 3. Key claims

1. **Three states of WM, not two.** Working memory contains items at three nested levels of accessibility: activated LTM, region of direct access (capacity-limited, ~4 items), and a one-item focus of attention.
2. **The focus of attention holds exactly one item.** Only one chunk is "directly available" to cognitive operations at any moment. Switching the focus from one item to another incurs a measurable cost.
3. **Region of direct access is capacity-limited but multi-item.** A small set of items (consistent with Cowan's ~4) is held in a state where they can be brought into the focus with minimal cost.
4. **Activated LTM is functionally distinct from direct access.** Items in activated LTM are *available* (recallable, recognizable above chance) but are not *immediately accessible* to ongoing operations and produce no measurable interference with concurrent processing.
5. **Active-set size affects RT; passive-set size does not.** RT in the arithmetic task scales with the number of digits in the active set (region of direct access) but is essentially independent of the number of passive digits (activated LTM).
6. **Object-switch costs index focus-of-attention movement.** When successive operations target different digits within the active set, RTs increase relative to repeated-target trials — the signature of moving the focus between items in the region of direct access.
7. **Items can be moved between layers.** Cueing a previously-passive digit as the next target moves it into the focus of attention; encoding a previously-active item into the passive set takes approximately 2 seconds before its memory load stops interfering with ongoing performance.

## 4. Methods

The core paradigm is an arithmetic-on-digits task with two memory sets.

- **Active set.** A small set of digits (size manipulated, typically 1–4) that participants will subsequently operate on with arithmetic instructions (e.g., "add 3 to digit X"). These digits must remain immediately available for operation.
- **Passive set.** A separate set of digits (size manipulated independently) that participants must remember and recall at the end of the trial but do *not* operate on during the trial.

After memorization, a sequence of arithmetic instructions targets digits in the active set. RTs to each instruction are the primary dependent measure. After all operations, participants recall both sets.

Key manipulations:

- **Active-set size $\times$ passive-set size.** Crossed factorially to dissociate which set's size affects ongoing RT.
- **Object switches.** Successive arithmetic operations either target the same active-set digit (repeat) or a different one (switch). Switch–repeat RT difference indexes focus-of-attention shifts.
- **Active-to-passive re-encoding (Experiment 2).** After a phase of operating on a digit in the active set, the digit is cued to move to the passive set. The lag before its presence stops interfering with ongoing operations on remaining active digits measures the time cost of moving an item from the focus / direct-access region into activated LTM.

The argument is that the three behavioral signatures — active-set-size effects on RT, object-switch costs, and a measurable re-encoding latency — jointly require three distinct WM states.

## 5. Results

- **Active-set-size effect.** RT increases approximately linearly with active-set size (roughly tens of milliseconds per added active item).
- **No passive-set-size effect on RT.** Holding additional passive digits does not slow ongoing arithmetic operations, despite the passive digits being recallable at trial end.
- **Object-switch cost.** Switching the operation from one active-set digit to another adds on the order of 100–200 ms to RT relative to repeating the same digit. This is the canonical signature of moving the focus of attention between items in the region of direct access.
- **Re-encoding latency (Experiment 2).** Approximately 2 seconds are required after a cue to re-encode an active digit into the passive set before its presence ceases to slow operations on the remaining active digits. This is the temporal cost of demoting an item from the region of direct access to activated LTM.
- **Recall performance.** Both active and passive digits are recalled at high accuracy, confirming that the passive set is *maintained* in WM — it simply does not occupy the region of direct access during ongoing operations.

## 6. Critique / limitations

The "exactly one item in the focus" claim is strong and has been refined by subsequent work. Some studies (e.g., Gilchrist & Cowan 2011; Oberauer's own later work) suggest the focus can sometimes contain a small set of bound features, or that the focus capacity varies with task demands. The strict "one" may be an idealization.

The boundary between region of direct access and activated LTM is operationalized by the active/passive manipulation, which conflates two factors: whether items are *currently relevant* and whether they will be *operated on*. A more direct manipulation — e.g., cueing different subsets of items as relevant within a single trial — would more cleanly isolate the region-of-direct-access layer.

The paradigm uses discrete digit stimuli and arithmetic operations. Whether the three-state structure generalizes to visual / spatial WM (where capacity, binding, and persistence operate differently) is an empirical question. The Olivers et al. 2011 active-accessory framework is the visual-WM counterpart, but the mapping from Oberauer's three states onto Olivers's binary distinction is not exact.

Object-switch costs are interpreted as focus-of-attention movement, but alternative accounts (e.g., proactive interference from the just-operated item) can produce similar effects. The interpretive load on the switch-cost measure is heavier than the methodology cleanly supports.

The three-state model is presented as a structural commitment, but a continuous-activation account (items vary along an activation gradient) can produce many of the same behavioral signatures. The Oberauer model is best read as a useful coarse-graining of a continuous underlying state space.

## 7. Connection to our work

The three-state architecture supplies a strong cognitive-psychology framing for the Recurrent ViT and PRISM v2:

**Softmax attention as the focus of attention.** The Recurrent ViT's softmax over patch tokens produces an attention map dominated, in most trials, by a single peak — the architectural form of "one item in the focus." This is the same observation Olivers et al. 2011 frames as the active item ([olivers2011_wm_states_attention](olivers2011_wm_states_attention.md)), but Oberauer's vocabulary is cleaner for the *single-item* commitment: the focus is structurally defined as the locus of the current operation, not as the locus of "active" representation. The attention map *is* the focus of attention in the model. Models that produce multi-peak attention maps are testing whether the focus-capacity-of-one generalizes.

**Recurrent state as region of direct access.** The full recurrent state $H_t$ in the Recurrent ViT (and the fast memory $M_t$ in PRISM v2) holds the broader scene representation — multiple locations, multiple features — available for the *next* attention operation but not currently being read out. This is the architectural analog of Oberauer's region of direct access: capacity-limited (the recurrent-state channel dimension and spatial grid bound it), multi-item, and immediately available to the next attention step. Object-switch costs in the cognitive paradigm correspond to the architectural cost of the attention map shifting from one location to another between recurrent steps.

**Slow memory as activated LTM.** PRISM v2's slow memory (`PRISM_V2_PROPOSAL.md` §3.3) maintains a longer-timescale representation that survives multiple updates of the fast memory. This is the architectural analog of activated LTM: items are *maintained* but do not directly drive the next attention readout, and moving an item from slow to fast memory takes time (the architectural analog of the 2-second re-encoding latency). The slow/fast distinction in PRISM v2 is therefore not only a temporal-multiscale design choice but a structural commitment matching the region-of-direct-access / activated-LTM distinction in Oberauer's model.

**Multi-hub system implications.** The user's multi-hub architecture (`the_user_architectural_program.md` §5) has each hub holding its own memory state, with all hubs competing for the central self-attention substrate. Oberauer's three-layer model suggests a corresponding three-layer competition: which hub's contribution lands in the focus of attention (one hub at a time wins the softmax peak), which hubs are in the region of direct access (contributing to the attention computation but not winning the peak), and which are in activated-LTM background (holding state for future use but not currently competing).

**Quantitative parallels to test.** The object-switch cost in cognitive experiments (~100–200 ms) and the re-encoding latency (~2 s) are concrete quantitative predictions that could be tested on the model: time the attention map's transition between locations when the cue changes, and time the slow-memory update to incorporate a new item. If the model reproduces ratios broadly consistent with the human data, that is evidence the architecture instantiates the three-layer structure non-trivially.

## 8. Citations to follow

- `cowan2001_magical_number_four` — the four-item capacity limit Oberauer's region of direct access is calibrated to. Not yet in seed.
- `awh2006_attention_wm` — broader attention-WM framework; the Olivers / Oberauer ideas in unified form. In seed.
- `oberauer2009_design_wm` — Oberauer's later, more developed three-state architecture. Not in seed.
- `gilchrist_cowan2011_focus_capacity` — challenges the strict capacity-of-1 for the focus. Not in seed.
- `luck_vogel1997_wm_capacity` — the original ~4-item visual WM capacity finding. In seed.
- `panichello_buschman2021_shared_mechanisms` — modern subspace analysis; output subspace as a candidate neural substrate for the focus of attention. In seed.
- `kiyonaga_egner2013_wm_internal_attention` — internal-attention framing of WM access. In seed.
