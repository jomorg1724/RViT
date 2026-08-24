# Bibliographic ledger and research-wiki index

This file is the append-only ledger for papers that entered the database, including provenance and recorded depth. Append a new paper to the appropriate source section; **do not rewrite or renumber existing paper rows**. `tools/audit.py` validates files under `papers/`, but the ledger is maintained by operators and may contain dated historical commentary below.

Legend for depth: `M` = metadata only, `A` = + abstract, `S` = + summary, `F` = full structured body.

## Current operator state (verified 2026-07-11)

- [`README.md`](README.md) — authority order, lineage boundaries, layout, and standard commands.
- [`SCHEMA.md`](SCHEMA.md) — compatibility boundary between grandfathered legacy pages and wiki-native conventions.
- [`HANDOFF.md`](HANDOFF.md) — restart-safe operator workflow and preservation gates.
- [`mocs/attention_program.md`](mocs/attention_program.md) — top-level MOC, with verified routes to [`recurrent_vit`](mocs/recurrent_vit.md), [`rvit_plus`](mocs/rvit_plus.md), [`prism_v1`](mocs/prism_v1.md), [`prism_v2`](mocs/prism_v2.md), and [`vda_normative_repair`](mocs/vda_normative_repair.md).
- [`registry/README.md`](registry/README.md) — canonical run-index operations. The live registry contained 44 unique records; both audit modes returned 0 errors, with 217 explicit unknown-provenance warnings.
- [`graph/graph_summary.md`](graph/graph_summary.md) — generated graph snapshot. It is a rebuildable output, not canonical run or scientific evidence; the current JSON, GraphML, and summary artifacts report 388 nodes and 3,859 edges, including 89 referenced taxonomy-concept nodes.
- [`../reports/research_state/2026-07-11_research_state_briefing.md`](../reports/research_state/2026-07-11_research_state_briefing.md) — dated manuscript lineage, evidence, and research-state audit.
- [`../reports/research_state/2026-07-11_implementation_log.md`](../reports/research_state/2026-07-11_implementation_log.md) — dated implementation and safety log.

The expanded audit discovered **265 paper cards** (261 full-depth and 4 abstract-depth), **16 concepts**, **6 threads**, **6 MOCs**, **5 notes**, and **1 brief**, and completed with 0 issues under the dual-schema compatibility policy. Existing legacy paper/concept/thread pages are grandfathered; newly wiki-native pages require the current base fields. The workspace root is not a Git repository. Re-run the documented commands before citing these dated counts.

### Provenance boundaries for this ledger

- Section A is the bibliography of the **2025 empirical** MAH/Recurrent ViT paper (arXiv:2502.10955v1).
- Sections B and C seed the **PRISM v1/v2 architecture history**; they do not define the current RViT+ empirical producer.
- Later manual and programmatic sections expand the literature corpus and preserve their own source labels.
- The separate **2026 normative** paper and its `Critique/` → `Rebuild/` → `Reconstruction/` audit/repair lineage are not revisions of the 2025 empirical paper. Their project navigation belongs in current MOCs/research-state reports, not by relabeling bibliographic rows.

---

## Section A — References from 2502.10955v1 (Recurrent ViT, Morgan, Albanna & Herman, 2025)

Bracketed reference number is the in-paper citation index.

| Ref | Authors (year) | Short title | File id | Depth |
|---|---|---|---|---|
| [1] | Carrasco (2011) | Visual attention: past 25 years | `carrasco2011_visual_attention_25y` | M |
| [2] | Clark, Squire, Merrikhi, Noudoost (2015) | Visual attention: linking prefrontal sources | `clark2015_prefrontal_attention` | M |
| [3] | Hoffman (2016) | Visual attention and eye movements | `hoffman2016_attention_eye_movements` | M |
| [4] | Bhatnagar & Orquin (2022) | Meta-analysis: visual attention on choice | `bhatnagar2022_attention_choice_metaanalysis` | M |
| [5] | Rust & Cohen (2022) | Priority coding in the visual system | `rust_cohen2022_priority_coding` | M |
| [6] | McAdams & Maunsell (1999a) | Attention on reliability of individual neurons | `mcadams_maunsell1999_reliability` | M |
| [7] | McAdams & Maunsell (1999b) | Attention on orientation-tuning V4 | `mcadams_maunsell1999_v4_tuning` | M |
| [8] | Thiele & Bellgrove (2018) | Neuromodulation of attention | `thiele_bellgrove2018_neuromodulation` | M |
| [9] | Cohen & Maunsell (2009) | Attention reducing interneuronal correlations | `cohen_maunsell2009_correlations` | M |
| [10] | Ruff & Cohen (2016) | Attention spike-count correlations across areas | `ruff_cohen2016_cross_area_correlations` | M |
| [11] | Posner, Snyder & Davidson (1980) | Attention and detection of signals | `posner1980_orienting` | F |
| [12] | Awh, Vogel & Oh (2006) | Attention–working memory interactions | `awh2006_attention_wm` | M |
| [13] | Gazzaley & Nobre (2012) | Top-down modulation bridging | `gazzaley_nobre2012_topdown` | M |
| [14] | Kiyonaga & Egner (2013) | Working memory as internal attention | `kiyonaga_egner2013_wm_internal_attention` | M |
| [15] | Panichello & Buschman (2021) | Shared mechanisms attention–WM | `panichello_buschman2021_shared_mechanisms` | M |
| [16] | Oberauer (2002) | Access to information in WM | `oberauer2002_access_wm` | M |
| [17] | McNab & Klingberg (2008) | PFC + basal ganglia control of WM | `mcnab_klingberg2008_pfc_bg_wm` | M |
| [18] | Carlisle, Arita, Pardo & Woodman (2011) | Attentional templates in WM | `carlisle2011_attentional_templates` | M |
| [19] | van Moorselaar, Theeuwes & Olivers (2014) | Competition for attentional template | `vanmoorselaar2014_template_competition` | M |
| [20] | Berggren & Eimer (2018) | WM load disrupts template-guided selection | `berggren_eimer2018_wm_load` | M |
| [21] | Carlisle & Kristjánsson (2018) | WM contents prime visual attention | `carlisle_kristjansson2018_wm_priming` | M |
| [22] | van Ede, Chekroud & Nobre (2019) | Human gaze tracks attention in WM | `vanede2019_gaze_internal_wm` | M |
| [23] | Vaswani et al. (2017) | Attention is all you need | `vaswani2017_attention` | F |
| [24] | Dosovitskiy et al. (2020) | An image is worth 16x16 words (ViT) | `dosovitskiy2020_vit` | F |
| [25] | Khan, Naseer, Hayat et al. (2022) | Transformers in vision: a survey | `khan2022_transformers_vision_survey` | M |
| [26] | Itti & Koch (2001) | Computational modelling of visual attention | `itti_koch2001_saliency_review` | F |
| [27] | Le Meur, Le Callet, Barba, Thoreau (2006) | Coherent computational approach to bottom-up attention | `lemeur2006_coherent_attention` | M |
| [28] | Krüger, Tünnermann, Scharlau (2017) | Measuring/modeling salience with TVA | `kruger2017_tva_salience` | M |
| [29] | Zou, Zhang, Li, Tian, Ding (2023) | Human attention in reading via task optimization | `zou2023_reading_attention` | M |
| [30] | Mehrani & Tsotsos (2023) | Self-attention as perceptual grouping | `mehrani_tsotsos2023_attention_grouping` | M |
| [31] | Yamamoto, Akahoshi, Kitazawa (2024) | Human-like attention in self-supervised ViT | `yamamoto2024_human_like_vit_attention` | M |
| [32] | Bardes et al. (2023) | V-JEPA: latent video prediction | `bardes2023_vjepa` | F |
| [33] | Luck & Vogel (1997) | Capacity of visual WM for features and conjunctions | `luck_vogel1997_wm_capacity` | M |
| [34] | Luck & Vogel (2013) | Visual WM capacity review | `luck_vogel2013_wm_capacity_review` | M |
| [35] | Brady & Tenenbaum (2013) | Probabilistic model of visual WM | `brady_tenenbaum2013_probabilistic_wm` | M |
| [36] | Emrich, Lockhart & Al-Aidroos (2017) | Attention mediates WM resource allocation | `emrich2017_attention_wm_resources` | M |
| [37] | Olivers, Peters, Houtkamp & Roelfsema (2011) | Different states in WM guide attention | `olivers2011_wm_states_attention` | M |
| [38] | Teng & Kravitz (2019) | Visual WM directly alters perception | `teng_kravitz2019_wm_alters_perception` | M |
| [39] | Bays, Schneegans, Ma & Brady (2024) | Representation/computation in visual WM | `bays2024_wm_representation` | M |
| [40] | Hochreiter & Schmidhuber (1997) | Long short-term memory | `hochreiter_schmidhuber1997_lstm` | F |
| [41] | Beck, Pöppel, Spanring et al. (2024) | xLSTM: extended LSTM | `beck2024_xlstm` | M |
| [42] | Srinath, Ruff & Cohen (2021) | Attention improves information flow between populations | `srinath2021_attention_information_flow` | M |
| [43] | Moore & Armstrong (2003) | Selective gating by microstimulation of FEF | `moore_armstrong2003_fef_microstim` | F |
| [44] | Cavanaugh & Wurtz (2004) | Subcortical modulation counters change blindness | `cavanaugh_wurtz2004_sc_change_blindness` | M |
| [45] | Cavanaugh, Alvarez & Wurtz (2006) | Brain stimulation: attentional shift or visual cue? | `cavanaugh2006_brain_stim_attention` | M |
| [46] | Egly, Driver & Rafal (1994) | Shifting attention between objects and locations | `egly1994_object_attention` | M |
| [47] | Thomsen, Specht, Ersland & Hugdahl (2005) | Conflicting cues in attention-shift fMRI | `thomsen2005_conflicting_cues_fmri` | M |
| [48] | Brisson & Jolicoeur (2008) | Express re-engagement after invalid spatial cues | `brisson_jolicoeur2008_express_reengagement` | M |
| [49] | Lu & Dosher (1998) | External noise distinguishes attention mechanisms | `lu_dosher1998_external_noise` | M |
| [50] | Solomon (2004) | Effect of spatial cues on visual sensitivity | `solomon2004_cues_sensitivity` | M |
| [51] | Cameron, Tai & Carrasco (2002) | Covert attention affects contrast psychometric | `cameron2002_covert_attention_contrast` | M |
| [52] | Müller & Findlay (1987) | Sensitivity and criterion effects in spatial cuing | `muller_findlay1987_sensitivity_criterion` | M |
| [53] | Hawkins, Hillyard, Luck et al. (1990) | Visual attention modulates signal detectability | `hawkins1990_attention_detectability` | M |
| [54] | Saltzman & Garner (1948) | Reaction time as span of attention | `saltzman_garner1948_rt_span` | M |
| [55] | Carlson, Jensen & Widaman (1983) | Reaction time, intelligence, attention | `carlson1983_rt_intelligence` | M |
| [56] | Prinzmetal, McCool & Park (2005) | Attention: RT vs accuracy mechanisms | `prinzmetal2005_rt_vs_accuracy` | M |
| [57] | Jehu, Desponts, Paquet, Lajoie (2015) | Prioritizing attention improves RT/postural | `jehu2015_postural_attention` | M |
| [58] | Herman & Krauzlis (2017) | Color-change detection in primate SC | `herman_krauzlis2017_sc_change_detection` | M |
| [59] | Ghose & Maunsell (2002) | Attentional modulation depends on task timing | `ghose_maunsell2002_task_timing` | M |
| [60] | Sani, Santandrea, Morrone & Chelazzi (2017) | Temporally evolving gain mechanisms V4 | `sani2017_temporal_v4_gain` | M |
| [61] | Wang, Chen, Yan et al. (2015) | Modulation of V1 by exogenous attention | `wang2015_v1_exogenous_attention` | M |
| [62] | Thompson, Hanes, Bichot, Schall (1996) | Perceptual/motor stages in FEF | `thompson1996_fef_stages` | M |
| [63] | Sharma, Sugihara, Katz et al. (2015) | Attention and temporal expectation in V1 | `sharma2015_attention_temporal_v1` | M |
| [64] | Jaramillo & Zador (2011) | Auditory cortex and acoustic temporal expectation | `jaramillo_zador2011_auditory_temporal` | M |
| [65] | Nobre & van Ede (2018) | Anticipated moments: temporal structure in attention | `nobre_vanede2018_anticipated_moments` | M |
| [66] | Mirpour, Ong & Bisley (2010) | Microstimulation of posterior parietal biases search | `mirpour2010_ppc_microstim` | M |
| [67] | Bollimunta, Bogadhi & Krauzlis (2018) | Comparing FEF and SC contributions to covert attention | `bollimunta2018_fef_sc_covert` | M |
| [68] | Monosov, Sheinberg & Thompson (2011) | PFC inactivation on IT responses in search | `monosov2011_pfc_inactivation_it` | M |
| [69] | Zénon & Krauzlis (2012) | Attention deficits without cortical deficits | `zenon_krauzlis2012_attention_deficits` | M |
| [70] | Herman, Katz & Krauzlis (2018) | Midbrain activity explains perceptual decisions | `herman2018_midbrain_decisions` | M |
| [71] | Sridharan, Steinmetz, Moore, Knudsen (2017) | Does SC control sensitivity or bias? | `sridharan2017_sc_sensitivity_bias` | M |
| [72] | Luo & Maunsell (2018) | Attentional changes in criterion vs sensitivity | `luo_maunsell2018_criterion_sensitivity` | M |
| [73] | Baluch & Itti (2011) | Mechanisms of top-down attention | `baluch_itti2011_topdown_mechanisms` | M |
| [74] | Bisley & Goldberg (2010) | Attention, intention, priority in parietal lobe | `bisley_goldberg2010_parietal_priority` | F |
| [75] | Knudsen (2007) | Fundamental components of attention | `knudsen2007_fundamental_components` | M |
| [76] | Lamy, Segal & Ruderman (2006) | Grouping does not require attention | `lamy2006_grouping_no_attention` | M |
| [77] | Bahle, Beck & Hollingworth (2018) | Architecture of WM × visual attention | `bahle2018_wm_attention_architecture` | M |
| [78] | Wheeler & Treisman (2002) | Binding in short-term visual memory | `wheeler_treisman2002_binding` | M |
| [79] | Botta & Lupiáñez (2014) | Attentional bias from multiple cues in VWM | `botta_lupianez2014_attentional_bias_vwm` | M |
| [80] | Desimone & Duncan (1995) | Neural mechanisms of selective attention | `desimone_duncan1995_biased_competition` | F |
| [81] | Krauzlis, Lovejoy & Zénon (2013) | SC and visual spatial attention | `krauzlis2013_sc_attention` | M |
| [82] | Silver, Ress & Heeger (2005) | Topographic maps of spatial attention in parietal | `silver2005_topographic_parietal` | M |
| [83] | Huda, Sipe, Breton-Provencher et al. (2020) | PFC top-down circuits modulate sensorimotor behavior | `huda2020_pfc_topdown_circuits` | M |
| [84] | Bolton, Murata, Kirchner et al. (2015) | Diencephalic dopamine source to SC | `bolton2015_dopamine_sc` | M |
| [85] | Pradel, Drwiega, Basiak (2021) | SC controls rostromedial tegmental nuclei | `pradel2021_sc_rmtg` | M |
| [86] | Essig & Felsen (2016) | Warning! dopaminergic modulation of SC | `essig_felsen2016_dopamine_sc` | M |
| [87] | Pérez-Fernández, Kardamakis, Suzuki et al. (2017) | Dopaminergic projections from SNc to tectum (lamprey) | `perezfernandez2017_snc_tectum` | M |
| [88] | Hikosaka, Nakamura, Nakahara (2006) | Basal ganglia orient eyes to reward | `hikosaka2006_bg_reward_eyes` | M |
| [89] | Hickey, Chelazzi & Theeuwes (2010) | Reward changes salience via anterior cingulate | `hickey2010_reward_salience_acc` | M |
| [90] | Failing & Theeuwes (2018) | Selection history: reward modulates selectivity | `failing_theeuwes2018_selection_history` | M |
| [91] | Friston, Kilner & Harrison (2006) | Free-energy principle for the brain | `friston2006_free_energy_brain` | M |
| [92] | Feldman & Friston (2010) | Attention, uncertainty and free-energy | `feldman_friston2010_attention_free_energy` | F |
| [93] | Friston, Shiner, FitzGerald et al. (2012) | Dopamine, affordance and active inference | `friston2012_dopamine_active_inference` | M |
| [94] | Khezri (2022) | Free-energy principle (continuous transformation chapter) | `khezri2022_fep_chapter` | M |
| [95] | Mazzaglia, Verbelen, Çatal, Dhoedt (2022) | FEP for perception/action: deep learning perspective | `mazzaglia2022_fep_deep_learning` | M |
| [96] | Hassanin, Anwar, Radwan, Khan, Mian (2024) | Visual attention in deep learning: in-depth survey | `hassanin2024_attention_dl_survey` | M |
| [97] | Reynolds, Chelazzi & Desimone (1999) | Competitive mechanisms in V2/V4 | `reynolds1999_competitive_v2_v4` | M |
| [98] | Bisley & Mirpour (2019) | Neural instantiation of a priority map | `bisley_mirpour2019_priority_map` | M |
| [99] | Wolfe (2021) | Guided search 6.0 | `wolfe2021_guided_search_6` | M |
| [100] | Desimone (1996) | Neural mechanisms for visual memory in attention | `desimone1996_visual_memory_attention` | M |
| [101] | Van der Stigchel, Belopolsky, Peters et al. (2009) | Limits of top-down control of visual attention | `vanderstigchel2009_topdown_limits` | M |
| [102] | Lee, Greening, Mather (2015) | Emotional arousal and goal-relevant encoding | `lee_greening_mather2015_emotional_arousal` | M |
| [103] | Herman, Arcizet, Krauzlis (2020) | Attention-related caudate modulation depends on SC | `herman_arcizet2020_caudate_sc` | M |
| [104] | Bettencourt & Somers (2009) | Target enhancement and distractor suppression in MOT | `bettencourt_somers2009_mot` | M |
| [105] | Meyerhoff, Papenmeier & Huff (2017) | MOT paradigm: tutorial review | `meyerhoff2017_mot_review` | M |
| [106] | Wolfe, Võ, Evans, Greene (2011) | Visual search in scenes: selective vs nonselective | `wolfe2011_scene_search` | M |
| [107] | Tas, Luck & Hollingworth (2016) | Visual attention and WM encoding: covert vs overt | `tas2016_attention_wm_covert_overt` | M |
| [108] | Gresch, Boettcher, van Ede, Nobre (2024) | Shifting attention between perception and WM | `gresch2024_perception_wm_shifts` | M |
| [109] | Gupta & Sridharan (2024) | Pre-saccadic attention does not facilitate change detection | `gupta_sridharan2024_presaccadic_change` | M |
| [110] | Felleman & Van Essen (1991) | Distributed hierarchical processing primate cortex | `felleman_vanessen1991_hierarchical_cortex` | F |
| [111] | Kietzmann, Spoerer, Sörensen et al. (2019) | Recurrence required to capture human visual dynamics | `kietzmann2019_recurrence_required` | M |
| [112] | Zhuang, Yan, Nayebi et al. (2021) | Unsupervised neural network models of ventral stream | `zhuang2021_unsupervised_ventral` | M |
| [113] | Botvinick, Wang, Dabney et al. (2020) | Deep RL and its neuroscientific implications | `botvinick2020_deep_rl_neuro` | M |
| [114] | Babayan, Uchida, Gershman (2018) | Belief state representation in dopamine system | `babayan_uchida_gershman2018_belief_states_dopamine` | M |
| [115] | Monosov (2020) | Outcome uncertainty mediates attention/learning/decisions | `monosov2020_outcome_uncertainty` | M |
| [116] | Mante, Sussillo, Shenoy, Newsome (2013) | Context-dependent computation by PFC recurrent dynamics | `mante2013_context_dependent_pfc` | M |
| [117] | Gattass & Desimone (2014) | Microstimulation of SC on visual spatial attention | `gattass_desimone2014_sc_microstim` | M |
| [118] | Miconi & VanRullen (2016) | Feedback model of attention: firing rates and RFs | `miconi_vanrullen2016_feedback_attention` | M |
| [119] | Liu, Zhang, Chan, Hsiao (2024) | Human attention guided explainable AI vision | `liu2024_human_attention_explainable_ai` | M |
| [120] | Cartella, Cornia, Cuculo et al. (2024) | Trends, applications, challenges in human attention modelling | `cartella2024_human_attention_modeling` | M |
| [121] | Pertzov & Husain (2014) | Privileged role of location in visual WM | `pertzov_husain2014_location_wm` | M |
| [122] | Schneegans & Bays (2017) | Neural architecture for feature binding in WM | `schneegans_bays2017_feature_binding_wm` | M |
| [123] | Tsotsos (1988) | A complexity-level analysis of immediate vision | `tsotsos1988_complexity_vision` | M |
| [124] | Koch & Ullman (1984) | Selecting one among the many: shifts in attention | `koch_ullman1984_winner_takes_all` | F |
| [125] | Sutton (RL: Introduction, 2018) | Reinforcement Learning: An Introduction | `sutton_barto2018_rl_intro` | M |
| [126] | Springenberg et al. (2024) | Offline actor-critic RL scales to large models | `springenberg2024_offline_actor_critic` | M |

## Section B — References from Prism/docs/THESIS.md (PRISM v1)

| Authors (year) | Short title | File id | Depth |
|---|---|---|---|
| Ba, Mnih & Kavukcuoglu (2015) | Multiple object recognition with visual attention | `ba2015_multiple_object_recognition` | M |
| Ballas, Yao, Pal, Courville (2016) | Delving deeper into convolutional networks for video | `ballas2016_convgru` | M |
| Bastos, Usrey, Adams et al. (2012) | Canonical microcircuits for predictive coding | `bastos2012_canonical_microcircuits` | F |
| Brefczynski & DeYoe (1999) | Physiological correlate of attention spotlight | `brefczynski_deyoe1999_spotlight_fmri` | M |
| Buckley, Kim, McGregor, Seth (2017) | FEP for action and perception: mathematical review | `buckley2017_fep_mathematical` | M |
| Constantinidis, Funahashi, Lee et al. (2018) | Persistent spiking activity underlies WM | `constantinidis2018_persistent_activity` | F |
| Cutrell & Marrocco (2002) | Microstimulation of PPC for covert attention | `cutrell_marrocco2002_ppc_microstim` | M |
| De Valois & De Valois (1988) | Spatial Vision (book) | `devalois1988_spatial_vision` | M |
| Friston (2010) | Free-energy principle: a unified brain theory | `friston2010_fep_unified_theory` | F |
| Funahashi, Bruce, Goldman-Rakic (1989) | Mnemonic coding of visual space in dlPFC | `funahashi1989_mnemonic_dlpfc` | F |
| Gold & Shadlen (2007) | Neural basis of decision making | `gold_shadlen2007_decision_making` | M |
| Goldman-Rakic (1995) | Cellular basis of working memory | `goldman_rakic1995_cellular_wm` | M |
| Hanks & Summerfield (2017) | Perceptual decision making in rodents/monkeys/humans | `hanks_summerfield2017_perceptual_decisions` | M |
| Heilman, Watson, Valenstein (2003) | Neglect and related disorders | `heilman2003_neglect` | M |
| Hollingworth, Richard, Luck (2008) | Function of visual short-term memory | `hollingworth2008_vstm_function` | M |
| Hubel & Wiesel (1962) | RFs in cat visual cortex | `hubel_wiesel1962_receptive_fields` | F |
| Jozefowicz, Zaremba, Sutskever (2015) | Empirical exploration of RNN architectures | `jozefowicz2015_rnn_exploration` | M |
| Kingma & Ba (2015) | Adam: stochastic optimization | `kingma_ba2015_adam` | M |
| Kriegeskorte, Mur, Bandettini (2008) | Representational similarity analysis | `kriegeskorte2008_rsa` | M |
| Lisman & Grace (2005) | Hippocampal-VTA loop: novelty gates LTM | `lisman_grace2005_hippocampal_vta` | M |
| Locatello, Weissenborn, Unterthiner et al. (2020) | Slot attention | `locatello2020_slot_attention` | M |
| Maunsell (2015) | Neuronal mechanisms of visual attention | `maunsell2015_attention_mechanisms` | M |
| Mnih, Heess, Graves, Kavukcuoglu (2014) | Recurrent models of visual attention | `mnih2014_recurrent_attention` | F |
| Müller, Philiastides & Newsome (2005) | SC microstimulation focuses attention without eye movement | `muller2005_sc_microstim_covert` | M |
| Perez, Strub, De Vries, Dumoulin, Bengio (2018) | FiLM: feature-wise linear modulation | `perez2018_film` | F |
| Pleines, Pallasch, Zimmer, Preuss (2022) | Generalization in recurrent PPO | `pleines2022_recurrent_ppo` | M |
| Rao & Ballard (1999) | Predictive coding in visual cortex | `rao_ballard1999_predictive_coding` | F |
| Ratcliff (1978) | Theory of memory retrieval (drift-diffusion) | `ratcliff1978_drift_diffusion` | M |
| Reynolds & Chelazzi (2004) | Attentional modulation of visual processing | `reynolds_chelazzi2004_attentional_modulation` | M |
| Reynolds & Heeger (2009) | Normalization model of attention | `reynolds_heeger2009_normalization` | F |
| Riley & Constantinidis (2016) | PFC persistent activity in WM | `riley_constantinidis2016_pfc_persistent` | M |
| Roitman & Shadlen (2002) | LIP during visual-discrimination RT task | `roitman_shadlen2002_lip_rt` | M |
| Schulman, Moritz, Levine et al. (2016) | High-dimensional control with GAE | `schulman2016_gae` | M |
| Schulman, Wolski, Dhariwal et al. (2017) | Proximal policy optimization | `schulman2017_ppo` | F |
| Spratling (2008) | Predictive coding as biased competition | `spratling2008_pc_biased_competition` | M |
| Sutton (2019) | The Bitter Lesson | `sutton2019_bitter_lesson` | F |
| Treisman & Gelade (1980) | Feature-integration theory of attention | `treisman_gelade1980_feature_integration` | M |
| Wu & He (2018) | Group normalization | `wu_he2018_groupnorm` | M |

## Section C — Additional references unique to Prism/docs/PRISM_V2_PROPOSAL.md

| Authors (year) | Short title | File id | Depth |
|---|---|---|---|
| Mujika, Meier, Steger (2017) | Fast-slow recurrent neural networks | `mujika2017_fast_slow_rnn` | M |
| Tallec & Ollivier (2018) | Can recurrent networks warp time? (chrono-init) | `tallec_ollivier2018_chrono_init` | M |
| Wen, Han, Liu et al. (2018) | Deep predictive coding networks for object recognition | `wen2018_deep_pc_networks` | M |
| Pinchetti et al. (2024) | Benchmarking predictive-coding networks | `pinchetti2024_benchmark_pc_networks` | M |
| Voita, Talbot, Moiseev et al. (2019) | Analyzing multi-head attention head specialization | `voita2019_head_specialization` | M |
| DiCarlo, Zoccolan & Rust (2012) | How does the brain solve visual object recognition? | `dicarlo2012_object_recognition` | M |
| Buzsáki & Wang (2012) | Mechanisms of gamma oscillations | `buzsaki_wang2012_gamma` | M |
| Banino, Balaguer, Barreca et al. (2021) | PonderNet: adaptive computation | `banino2021_pondernet` | M |
| Graves (2016) | Adaptive computation time for RNNs | `graves2016_act` | M |

## Section D — References cited in the user's Private & Shared notes (cite-trail)

Papers cited in the four Notion-exported folders (`Private & Shared`, `-2 Classifier`, `-3 VAE`, `-4 Evolution of Architecture`) that are load-bearing for the user's architectural program. Stubbed in the initial session by `tools/generate_private_stubs.py`.

| Authors (year) | Short title | File id |
|---|---|---|
| Schmidhuber (2015) | On learning to think — coupled-RNN world models | `schmidhuber2015_learn_to_think` |
| Wang et al. (2025) | Hierarchical Reasoning Model | `wang2025_hierarchical_reasoning_model` |
| Higgins et al. (2017) | Factorized representations / β-VAE | `higgins2017_factorized_representations` |
| Manns & Eichenbaum (2006) | LEC / MEC factorization | `manns_eichenbaum2006_lec_mec` |
| Sherman (2022) | Cortico-thalamo-cortical loop functions | `sherman2022_ctc_loop` |
| Haber (2015) | CBGTC circuits in goal-directed behavior | `haber2015_cbgtc_circuits` |
| Weiler et al. (2025) | L6 corticocortical feedback | `weiler2025_l6_corticocortical` |
| Jordan et al. (2023) | Dendritic Bayes-optimal cue integration | `jordan2023_dendritic_bayesian` |
| Laughlin et al. (1998) | Metabolic cost of neural information | `laughlin1998_metabolic_cost` |
| Senkowski & Engel (2024) | Multi-timescale MSI | `senkowski_engel2024_multi_timescale_msi` |
| Choi et al. (2023) | MSI review | `choi2023_msi_review` |
| Masse et al. (2019) | Circuit mechanisms of WM | `masse2019_circuit_wm` |
| Riesenhuber & Poggio (1999) | Hierarchical models of object recognition | `riesenhuber_poggio1999_hierarchical_models` |
| Mishkin et al. (1983) | Two cortical pathways | `mishkin1983_two_pathways` |
| Hubel & Wiesel (1968) | Macaque striate cortex | `hubel_wiesel1968_macaque` |
| Tanaka (1996) | IT and object vision | `tanaka1996_it_object_vision` |
| Larkum (2013) | Apical/basal dendrites | `larkum2013_apical_basal` |
| Gilbert & Li (2013) | Top-down influences on vision | `gilbert_li2013_topdown` |
| LeCun (2022) | A path towards autonomous machine intelligence | `lecun2022_path_to_agi` |
| Marcus (2025) | LLM world-model critique | `marcus2025_llm_critique` |
| Pearl (2018) | The Book of Why / Ladder of Causation | `pearl2018_book_of_why` |
| Hawkins (2021) | A Thousand Brains | `hawkins2021_thousand_brains` |
| Clark (2013) | Whatever next? Predictive brains | `clark2013_whatever_next` |
| Keller & Mrsic-Flogel (2018) | Predictive processing as canonical computation | `keller_mrsic_flogel2018_pc_review` |
| Srinivasan, Laughlin & Dubs (1982) | Predictive coding in the retina | `srinivasan1982_predictive_coding_retina` |
| Friston (2005) | A theory of cortical responses | `friston2005_cortical_responses` |
| Summerfield & de Lange (2014) | Expectation in perceptual decision making | `summerfield_delange2014_expectation` |
| Aitchison & Lengyel (2017) | PC and Bayesian inference | `aitchison_lengyel2017_pc_bayesian` |
| Moran & Desimone (1985) | Selective attention gates extrastriate | `moran_desimone1985_selective_attention` |
| Miller & Cohen (2001) | Integrative theory of PFC | `miller_cohen2001_pfc_function` |
| Bundesen et al. (2005) | Neural theory of visual attention | `bundesen2005_neural_theory_attention` |
| Edelman (1987) | Neural Darwinism | `edelman1987_neural_darwinism` |
| Buzsáki (2010) | Cell assemblies / synapsembles | `buzsaki2010_cell_assemblies` |
| Lee (2008) | Game theory and neural basis of social decisions | `lee2008_game_theory_neural` |
| Carrillo & Dewatripont (2008) | Brain as central executive | `carrillo_dewatripont2008_brain_executive` |
| Glimcher (2011) | Dopamine RPE hypothesis | `glimcher2011_dopamine_rpe` |
| Logie (2003) | Spatial/visual WM as mental workspace | `logie2003_mental_workspace` |
| Varela, Thompson & Rosch (1991) | The Embodied Mind | `varela_thompson_rosch_embodied` |

## Section E — Programmatic-expansion candidates

Papers added via programmatic PubMed / bioRxiv searches.

| Authors (year) | Short title | File id | Depth |
|---|---|---|---|
| Shipp (2024) | Visual predictive coding circuitry — computational components | `shipp2024_visual_pc_computational` | M |
| Boshra & Kastner (2022) | Attention control in the primate brain | `boshra_kastner2022_attention_control` | M |
| Vijayraghavan & Everling (2021) | Muscarinic neuromodulation of PFC persistent activity | `vijayraghavan_everling2021_muscarinic_wm` | M |
| Pezzulo, Parr & Friston (2024) | Active inference as a theory of sentient behavior | `pezzulo_parr_friston2024_active_inference` | M |
| Hu & Dan (2021) | Inferior–superior colliculus circuit for cued visual attention | `hu_dan2021_ic_sc_attention` | M |

## Section F — Manual cite-trail additions (from full-depth entries' citations-to-follow)

Papers added when a full-depth entry referenced them and they were not yet in the database. `seed_source: manual`.

| Authors (year) | Short title | File id | Depth |
|---|---|---|---|
| McKinnon, Mo & Sherman (2025) | Transthalamic V1 disruption impairs visual discrimination | `mckinnon_mo_sherman2025_transthalamic_v1` | M |
| Attwell & Laughlin (2001) | Energy budget for grey-matter signaling | `attwell_laughlin2001_brain_energy_budget` | M |
| Bai, Kolter & Koltun (2019) | Deep Equilibrium Models | `bai_kolter_koltun2019_deep_equilibrium_models` | M |
| Ha & Schmidhuber (2018) | World Models | `ha_schmidhuber2018_world_models` | M |
| Hafner et al. (2020) | Dreamer — latent-imagination control | `hafner2020_dreamer` | M |
| Larkum, Zhu & Sakmann (1999) | BAC firing — coupling apical/basal inputs | `larkum_zhu_sakmann1999_bac_firing` | M |
| Bastos et al. (2015) | Feedforward gamma / feedback alpha — macaque laminar | `bastos2015_laminar_macaque` | M |
| Ernst & Banks (2002) | Optimal visual-haptic cue integration | `ernst_banks2002_cue_combination` | M |
| Urbanczik & Senn (2014) | Learning by dendritic prediction of somatic spiking | `urbanczik_senn2014_predictive_dendrite` | M |
| Sherman & Guillery (2011) | Distinct functions for direct vs transthalamic corticocortical | `sherman_guillery2011_distinct_functions` | M |
| Stănișor et al. (2013) | Unified selection signal for attention and reward in V1 | `stanisor2013_v1_value_attention` | A |
| Bellemare, Dabney & Munos (2017) | C51 — distributional perspective on RL | `bellemare2017_c51` | A |
| Dabney, Rowland, Bellemare & Munos (2018) | QR-DQN — distributional RL with quantile regression | `dabney2018_qr_dqn` | A |
| Dabney et al. (2020) | A distributional code for value in dopamine-based RL | `dabney2020_distributional_dopamine` | A |

---

## Section G — Working memory / VWM / hippocampus / world-model deep-dive (2026-05-23)

Manual deep-dive batch of 20 full-depth papers spanning four target domains, with attention-link prioritization. All entries `seed_source: manual_deep_dive_2026_05_23`, `depth: full`. See [threads/wm_vwm_hippocampus_world_models_deep_dive.md](threads/wm_vwm_hippocampus_world_models_deep_dive.md) for the cross-paper synthesis.

### G.1 — Working memory (5 papers)

| Authors (year) | Short title | File id | Depth |
|---|---|---|---|
| Baddeley & Hitch (1974) | Working Memory — original tripartite model | `baddeley_hitch1974_working_memory` | F |
| D'Esposito & Postle (2015) | The Cognitive Neuroscience of Working Memory | `desposito_postle2015_wm_neuroscience` | F |
| Stokes (2015) | 'Activity-silent' working memory in PFC — dynamic coding | `stokes2015_activity_silent_wm` | F |
| Christophel, Klink, Spitzer, Roelfsema & Haynes (2017) | The Distributed Nature of Working Memory | `christophel2017_distributed_wm` | F |
| Bays & Husain (2008) | Dynamic Shifts of Limited WM Resources in Human Vision | `bays_husain2008_dynamic_resources` | F |

### G.2 — Visual working memory & attention-WM bridges (5 papers)

| Authors (year) | Short title | File id | Depth |
|---|---|---|---|
| Soto, Hodsoll, Rotshtein & Humphreys (2008) | Automatic guidance of attention from WM | `soto2008_automatic_attention_wm` | F |
| Foster, Bsales, Jaffe & Awh (2017) | Alpha-band activity reveals spontaneous spatial WM | `foster2017_alpha_vwm` | F |
| Postle (2006) | Working memory as an emergent property | `postle2006_wm_emergent` | F |
| Sreenivasan & D'Esposito (2019) | The what, where and how of delay activity | `sreenivasan_desposito2019_delay_activity` | F |
| Awh & Jonides (2001) | Overlapping mechanisms of attention and spatial WM | `awh_jonides2001_overlapping_attention_wm` | F |

### G.3 — Hippocampus, place/grid cells, cognitive maps (5 papers)

| Authors (year) | Short title | File id | Depth |
|---|---|---|---|
| O'Keefe & Dostrovsky (1971) | The hippocampus as a spatial map — first place cells | `okeefe_dostrovsky1971_hippocampal_map` | F |
| Hafting, Fyhn, Molden, Moser & Moser (2005) | Microstructure of a spatial map in EC — grid cells | `hafting2005_grid_cells` | F |
| Whittington et al. (2020) | Tolman-Eichenbaum Machine (TEM) — relational+spatial | `whittington2020_tem` | F |
| Stachenfeld, Botvinick & Gershman (2017) | The hippocampus as a predictive map (SR) | `stachenfeld2017_predictive_map` | F |
| Behrens et al. (2018) | What is a cognitive map? | `behrens2018_cognitive_map` | F |

### G.4 — World models & predictive-architecture RL (5 papers)

| Authors (year) | Short title | File id | Depth |
|---|---|---|---|
| Hafner, Pasukonis, Ba & Lillicrap (2023) | DreamerV3 — mastering diverse domains | `hafner2023_dreamerv3` | F |
| Wayne et al. (2018) | MERLIN — unsupervised predictive memory in goal-directed agent | `wayne2018_merlin` | F |
| Schrittwieser et al. (2020) | MuZero — planning with a learned model | `schrittwieser2020_muzero` | F |
| Banino et al. (2018) | Vector-based navigation — grid-like representations in RL agents | `banino2018_vector_navigation` | F |
| Assran et al. (2023) | I-JEPA — joint-embedding predictive architecture for images | `assran2023_ijepa` | F |

**Selection criteria.** Mix of foundational (Baddeley-Hitch 1974, O'Keefe 1971, Hafting 2005) and recent (DreamerV3 2023, TEM 2020, I-JEPA 2023). Coverage gap targeting: hippocampus had only 1 prior entry (Lisman-Grace); world models had only 3 (Ha-Schmidhuber, Dreamer V1, V-JEPA); neural-WM substrate was sparse (no D'Esposito-Postle, no Stokes, no Christophel). Attention-link bonus prioritized: Soto, Foster, Awh-Jonides, Bays-Husain, Sreenivasan-D'Esposito, TEM (transformer link), Stachenfeld (RL+attention), Banino (RL+grid+attention), MERLIN (attention-based memory reads), I-JEPA (latent-attention prediction).

**Replacements from initial target list.** Three planned papers were already in the database at full depth: `gazzaley_nobre2012_topdown`, `lecun2022_path_to_agi`, `panichello_buschman2021_shared_mechanisms`. Replacements: Awh & Jonides 2001 (for Gazzaley & Nobre), I-JEPA (for LeCun position paper).

---

## Section H — Random-dot motion + microstimulation (2026-07-04)

Five seminal MT/LIP microstimulation-on-random-dot-motion papers, added as a non-orientation (motion-direction) task line and the biological precedent for the model's `attn_clamp` causal perturbation (the in-silico microstimulation analog). Anchors the `motion4` battery env. Note the sensory-node (MT) vs decision-node (LIP) perturbation axis. All `seed_source: pubmed`, `depth: full`, `status: summary`.

| Authors (year) | Short title | File id | Depth |
|---|---|---|---|
| Salzman, Britten & Newsome (1990) | MT microstimulation biases motion-direction judgements (seminal) | `salzman1990_mt_microstim` | F |
| Salzman, Murasugi, Britten & Newsome (1992) | MT microstim direction discrimination — effect sizes / equivalent-signal | `salzman1992_mt_microstim_methods` | F |
| Salzman & Newsome (1994) | 8-alternative motion decision — winner-take-all vs vector-averaging read-out | `salzman_newsome1994_winner_take_all` | F |
| Ditterich, Mazurek & Shadlen (2003) | MT microstim affects decision SPEED (RT / drift-diffusion) | `ditterich2003_microstim_rt` | F |
| Hanks, Ditterich & Shadlen (2006) | LIP microstim — decision-stage (accumulator) perturbation | `hanks2006_lip_microstim` | F |

## Threads (cross-paper narratives)

| Thread id | Title | Source |
|---|---|---|
| `the_user_architectural_program` | The user's architectural program (Feedback Transformer, multi-compartmental memory, competition-emergent PC) | Private & Shared notes |
| `predictive_coding_as_canonical_computation` | The development of predictive coding from retina (1982) through canonical-microcircuit (2012) to active-inference (2024) | Curated synthesis |
| `feedback_substrates` | Anatomical and computational substrates of cortical feedback (L6 CC, transthalamic, apical-basal, microcircuit) | Curated synthesis |
| `coupled_rnn_architectures` | The lineage from LSTM through Schmidhuber's C–M, Dreamer, JEPA, HRM to the user's multi-hub system | Curated synthesis |

## Concepts (mechanism-level nodes)

### Tier 1 — User's architectural program

| Concept id | Title | Anchors |
|---|---|---|
| `feedback_transformer` | The Feedback Transformer | Vaswani, ViT, Locatello, Mante, Perez (FiLM), Weiler, Larkum 2013, Bahdanau, Voita, Sherman, McKinnon-Mo-Sherman, Bastos 2012, Felleman-Van Essen (14 anchors total as of 2026-05-18) |
| `gridcell_rnn` | The GridCell RNN | LSTM, ViT, ConvGRU, FiLM, Vaswani |
| `multi_compartmental_memory` | Multi-compartmental memory | LSTM, xLSTM, Mujika, Tallec-Ollivier, Constantinidis, Goldman-Rakic, Funahashi |
| `bidirectional_hierarchical_feedback` | Bidirectional hierarchical feedback | Rao-Ballard, Bastos, Felleman & Van Essen, DiCarlo, Kietzmann, Miconi, Friston |
| `multi_hub_multi_objective_system` | Multi-hub multi-objective system (MSI + RL + VAE) | Schmidhuber, Ha-Schmidhuber, Dreamer, V-JEPA, LeCun, Mante, Haber, MSI reviews |
| `iterative_variational_encoder_decoder` | Iterative variational encoder–decoder ($n_{FR} \to n_{BR}$) | Friston, Rao-Ballard, V-JEPA, LeCun, Higgins, ViT |
| `coalition_resource_competition` | Coalition resource competition (resource-scarcity theoretical foundation) | Laughlin, Attwell-Laughlin, Edelman, Buzsáki, Lee, Desimone-Duncan, Reynolds, Schmidhuber |
| `competition_emergent_predictive_coding` | PC as emergent from coalition competition | Rao-Ballard, Friston, Desimone & Duncan, Reynolds, Spratling, Mante, Feldman-Friston |
| `world_model_emergence` | Emergent world model from inter-hub competition (falsifiable test) | Schmidhuber, Ha-Schmidhuber, Dreamer, V-JEPA, LeCun, Mante, Desimone-Duncan |

### Tier 2 — Canonical neuroscience and architectural-pattern nodes

| Concept id | Title | Anchors |
|---|---|---|
| `hierarchical_predictive_coding` | Hierarchical predictive coding framework | Rao-Ballard, Friston, Bastos, Keller-Mrsic-Flogel, Shipp, Spratling, Feldman-Friston, Clark, Aitchison-Lengyel, Wen, Pinchetti, Srinivasan, Pezzulo-Parr-Friston |
| `cortico_thalamo_cortical_loops` | Transthalamic feedback pathways | Sherman-Guillery, Miller-Hansen & Sherman, McKinnon-Mo-Sherman, Weiler, Felleman-Van Essen, Bastos, Boshra-Kastner |
| `cortico_basal_ganglia_thalamic_loops` | CBGTC loops (RL substrate) | Haber, Hikosaka, McNab-Klingberg, Herman-Arcizet, Glimcher, Botvinick, Babayan-Uchida-Gershman |
| `apical_basal_dendritic_integration` | Apical-basal dendritic AND-gate | Larkum 2013, Larkum-Zhu-Sakmann 1999, Jordan, Urbanczik-Senn, Bastos, Keller-Mrsic-Flogel, Rao-Ballard |
| `slow_fast_recurrence` | Multi-timescale coupled RNNs | Mujika, Tallec-Ollivier, HRM, Schmidhuber, LSTM, xLSTM, Buzsáki-Wang, Goldman-Rakic, Funahashi, Constantinidis, Masse |
| `coupled_rnn_world_models` | Controller-world-model lineage | Schmidhuber, Ha-Schmidhuber, Dreamer, V-JEPA, LeCun, HRM, Mante |

Future sessions can add more concepts as new mechanisms come into focus. Candidates include `precision_weighting_attention`, `priority_map_construction`, `multi_sensory_integration_architectures`, `dendritic_credit_assignment`.

---

## Corpus state (live operator view; verified 2026-07-11)

- **Paper cards:** 265 total; 261 `depth: full`, 4 `depth: abstract`; 0 legacy-audit issues.
- **Wiki pages:** 16 concepts, 6 threads, 6 MOCs, 5 evidence notes, and 1 lineage brief.
- **Audit state:** 0 issues under the dual-schema compatibility policy; legacy paper/concept/thread pages are grandfathered, while newly wiki-native pages require current base fields.
- **Derived graph:** the rebuilt JSON, GraphML, and Markdown summary report 388 nodes and 3,859 edges, including 89 referenced taxonomy-concept nodes.
- **Run registry:** 44 canonical run records; 0 audit errors and 217 preserved unknown-provenance warnings.

The completion batches and queues below are a historical work log, not a current corpus-count authority. Use the operator links at the top of this file for current routing.

### Priority queue for future deepening sessions

**Completed 2026-05-13** (struck through):

1. ~~`schmidhuber2015_learn_to_think`~~ — coupled-RNN world models. *Deepened 2026-05-13; sourcing-caveat softened after arXiv abstract verified.*
2. ~~`wang2025_hierarchical_reasoning_model`~~ — coupled H/L RNN. *Deepened 2026-05-13; revised against the actual arXiv PDF v3, sourcing-caveat removed.*
3. ~~`weiler2025_l6_corticocortical`~~ — Layer 6 corticocortical feedback. *Deepened 2026-05-13 against eLife PMID 40153297.*
4. ~~`sherman2022_ctc_loop`~~ — transthalamic feedback. *Deepened 2026-05-13 against Miller-Hansen & Sherman 2022 PNAS, PMID 35588455. Identity note: best match to user's citation.*
5. ~~`haber2015_cbgtc_circuits`~~ — corticostriatal circuitry. *Deepened 2026-05-13 against Haber 2016 DCN, PMID 27069376. Identity note: nominal year 2015, actual publication early 2016.*
6. ~~`keller_mrsic_flogel2018_pc_review`~~ — predictive processing canonical computation. *Deepened 2026-05-13 against Neuron PMID 30359606.*
7. ~~`bastos2012_canonical_microcircuits`~~ — canonical microcircuits for PC. *Deepened 2026-05-13 against Neuron PMID 23177956.*
8. ~~`larkum2013_apical_basal`~~ — cellular mechanism for cortical associations. *Deepened 2026-05-13 against TINS PMID 23273272.*
9. ~~`jordan2023_dendritic_bayesian`~~ — conductance-based dendrites perform Bayes-optimal cue integration. *Deepened 2026-05-13 against arXiv 2104.13238.*
10. ~~`laughlin1998_metabolic_cost`~~ — metabolic cost of neural information. *Deepened 2026-05-13 against Nature Neuroscience PMID 10195106.*

**Completed 2026-05-13 (canonical PC and biased-competition batch):**

11. ~~`feldman_friston2010_attention_free_energy`~~ — *Deepened against Front Hum Neurosci PMID 21160551.*
12. ~~`spratling2008_pc_biased_competition`~~ — *Deepened against Vision Research PMID 18442841.*
13. ~~`mante2013_context_dependent_pfc`~~ — *Deepened against Nature PMID 24201281.*
14. ~~`kietzmann2019_recurrence_required`~~ — *Deepened against PNAS PMID 31591217.*
15. ~~`constantinidis2018_persistent_activity`~~ — *Deepened against J Neurosci PMID 30089641 (dual-perspective format, counterpoint noted).*
16. ~~`bisley_goldberg2010_parietal_priority`~~ — *Deepened against Annu Rev Neurosci PMID 20192813.*
17. ~~`attwell_laughlin2001_brain_energy_budget`~~ — *Deepened against J Cereb Blood Flow Metab PMID 11598490.*
18. ~~`desimone_duncan1995_biased_competition`~~ — *Deepened against Annu Rev Neurosci PMID 7605061.*

**Completed 2026-05-14 (cellular / world-models / active-inference batch):**

19. ~~`larkum_zhu_sakmann1999_bac_firing`~~ — *Deepened against Nature PMID 10192334.*
20. ~~`bastos2015_laminar_macaque`~~ — *Deepened against Neuron PMID 25556836. Identity note: actual publication date is late 2014, volume 85(2) early 2015; year set to 2014 in frontmatter.*
21. ~~`bai_kolter_koltun2019_deep_equilibrium_models`~~ — *Deepened against arXiv 1909.01377.*
22. ~~`mckinnon_mo_sherman2025_transthalamic_v1`~~ — *Deepened against J Neurosci PMID 40139804.*
23. ~~`ha_schmidhuber2018_world_models`~~ — *Deepened against arXiv 1803.10122.*
24. ~~`hafner2020_dreamer`~~ — *Deepened against arXiv 1912.01603.*
25. ~~`urbanczik_senn2014_predictive_dendrite`~~ — *Deepened against Neuron PMID 24507189.*
26. ~~`ernst_banks2002_cue_combination`~~ — *Deepened against Nature PMID 11807554.*
27. ~~`pezzulo_parr_friston2024_active_inference`~~ — *Deepened against Biol Psychol PMID 38182015.*
28. ~~`shipp2024_visual_pc_computational`~~ — *Deepened against Front Neural Circuits PMID 38259953.*

**Completed 2026-05-14 (PC-foundations / attention-WM batch):**

29. ~~`clark2013_whatever_next`~~ — *Deepened against Behav Brain Sci PMID 23663408.*
30. ~~`aitchison_lengyel2017_pc_bayesian`~~ — *Deepened against Curr Opin Neurobiol PMID 28942084.*
31. ~~`friston2005_cortical_responses`~~ — *Deepened against Phil Trans R Soc B PMID 15937014.*
32. ~~`srinivasan1982_predictive_coding_retina`~~ — *Deepened against Proc R Soc B PMID 6129637.*
33. ~~`summerfield_delange2014_expectation`~~ — *Deepened against Nat Rev Neurosci PMID 25315388.*
34. ~~`awh2006_attention_wm`~~ — *Deepened against Neuroscience PMID 16324792.*
35. ~~`gazzaley_nobre2012_topdown`~~ — *Deepened against Trends Cogn Sci PMID 22209601.*
36. ~~`panichello_buschman2021_shared_mechanisms`~~ — *Deepened against Nature PMID 33790467.*
37. ~~`clark2015_prefrontal_attention`~~ — *Deepened against Prog Neurobiol PMID 26159708.*

**Completed 2026-05-14 (SC-attention / WM-capacity / decision-making batch):**

38. ~~`cavanaugh_wurtz2004_sc_change_blindness`~~ — *Deepened against J Neurosci PMID 15601929.*
39. ~~`herman_krauzlis2017_sc_change_detection`~~ — *Deepened against eNeuro PMID 28413825. Direct precursor paper, Herman is the user's co-author.*
40. ~~`krauzlis2013_sc_attention`~~ — *Deepened against Annu Rev Neurosci PMID 23682659.*
41. ~~`bisley_mirpour2019_priority_map`~~ — *Deepened against Curr Opin Psychol PMID 30731260.*
42. ~~`luck_vogel1997_wm_capacity`~~ — *Deepened against Nature PMID 9384378.*
43. ~~`luck_vogel2013_wm_capacity_review`~~ — *Deepened against Trends Cogn Sci PMID 23850263.*
44. ~~`bays2024_wm_representation`~~ — *Deepened against Nat Hum Behav PMID 38849647.*
45. ~~`kiyonaga_egner2013_wm_internal_attention`~~ — *Deepened against Psychon Bull Rev PMID 23233157.*
46. ~~`olivers2011_wm_states_attention`~~ — *Deepened against Trends Cogn Sci PMID 21665518.*
47. ~~`gold_shadlen2007_decision_making`~~ — *Deepened against Annu Rev Neurosci PMID 17600525.*

**Completed 2026-05-14 (attention-psychophysics / SDT batch):**

48. ~~`lu_dosher1998_external_noise`~~ — *Deepened against Vision Research PMID 9666987.*
49. ~~`cameron2002_covert_attention_contrast`~~ — *Deepened against Vision Research PMID 11934448.*
50. ~~`solomon2004_cues_sensitivity`~~ — *Deepened against Vision Research PMID 15066386.*
51. ~~`muller_findlay1987_sensitivity_criterion`~~ — *Deepened against Percept Psychophys PMID 3684496. Abstract unavailable on PubMed; deepening from prior knowledge.*
52. ~~`hawkins1990_attention_detectability`~~ — *Deepened against JEP HPP PMID 2148593.*
53. ~~`luo_maunsell2018_criterion_sensitivity`~~ — *Deepened against Neuron PMID 29503191.*
54. ~~`sridharan2017_sc_sensitivity_bias`~~ — *Deepened against J Neurosci PMID 28100734.*
55. ~~`gupta_sridharan2024_presaccadic_change`~~ — *Deepened against PLoS Biology PMID 38271460.*
56. ~~`treue_martinez_trujillo1999_feature_attention`~~ — *New file created and deepened against Nature PMID 10376597. Did not exist as a stub.*

**Completed 2026-05-14 (ML / vision-transformer / RNN-architectures batch — first parallel-agent batch):**

57. ~~`khan2022_transformers_vision_survey`~~ — *Deepened against arXiv 2101.01169 / ACM CSUR. Full PDF read.*
58. ~~`itti_koch2001_saliency_review`~~ — *Deepened against Nat Rev Neurosci, DOI 10.1038/35058500. Paywalled; deepened from prior knowledge with explicit sourcing note.*
59. ~~`koch_ullman1984_winner_takes_all`~~ — *Deepened against PubMed PMID 3836989. Title/venue updated: actual title "Shifts in selective visual attention: towards the underlying neural circuitry", Human Neurobiology 1985 (id ending kept as 1984 per no-rename rule).*
60. ~~`hassanin2024_attention_dl_survey`~~ — *Deepened against arXiv 2204.07756 / Information Fusion. Full PDF read.*
61. ~~`mehrani_tsotsos2023_attention_grouping`~~ — *Deepened against arXiv 2303.01542. Abstract verified; methods/results partly from prior knowledge.*
62. ~~`yamamoto2024_human_like_vit_attention`~~ — *Deepened against arXiv 2410.22768. Abstract verified; specific numerical results flagged as paper-PDF-dependent.*
63. ~~`beck2024_xlstm`~~ — *Deepened against arXiv 2405.04517. Architecture details verified; quantitative benchmarks flagged as approximate.*
64. ~~`hochreiter_schmidhuber1997_lstm`~~ — *Deepened against bioinf.jku.at mirror of the Neural Computation paper. Full PDF read.*
65. ~~`tay2022_efficient_transformers_survey`~~ — *New file created and deepened against arXiv 2009.06732 / ACM CSUR.*
66. ~~`mnih2014_recurrent_attention`~~ — *Deepened against arXiv 1406.6247. Abstract verbatim; some quantitative MNIST numbers from prior knowledge.*

**Note on parallel deepening.** The 2026-05-14 ML batch was the first to use parallel sub-agents (10 spawned simultaneously), with each agent independently fetching its paper's source, reading the schema and exemplar, and writing the full file. All 10 files passed audit cleanly on first attempt. The approach scales the deepening throughput by an order of magnitude per session.

**Completed 2026-05-15 (DL / vision history + recurrent ViT bibliography stragglers — tenth parallel-agent batch):**

67. ~~`kingma_ba2015_adam`~~ — *Deepened against arXiv 1412.6980 (abstract + PDF). Optimizer foundational for training Recurrent ViT and PRISM. Body notes: no optimizer-related TAXONOMY concepts existed; concepts list left empty to preserve vocabulary discipline. AdamW + warmup recommendation flowing from §6 critique.*
68. ~~`bahdanau2014_neural_translation`~~ — *New file created and deepened against arXiv 1409.0473. The foundational attention paper — soft-alignment / Q-K-V structure feeds the lineage of the Recurrent ViT's attention. Flagged `cho2014_gru` for future addition (parent GRU paper missing from db).*
69. ~~`jozefowicz2015_rnn_exploration`~~ — *Deepened against ICML 2015. Forget-gate-bias=1 prescription cited as load-bearing for the recurrent ViT, PRISM v1 ConvGRU, PRISM v2 slow-fast memory, and the GridCell RNN. Flagged `cho2014_gru` and `greff2016_lstm_search_space_odyssey` as load-bearing absences.*
70. ~~`kriegeskorte2008_rsa`~~ — *Deepened against Front Syst Neurosci, DOI 10.3389/neuro.06.004.2008. The methodological substrate for any future Recurrent-ViT-vs-IT cortex validation. §7 surfaces a concrete falsifiable test: later-step recurrent ViT RDMs should be more IT-aligned than early-step ones.*
71. ~~`ballas2016_convgru`~~ — *Deepened against arXiv 1511.06432 (abstract only — PDF binary). ConvGRU is PRISM v1's memory-cell substrate. Quantitative numbers flagged as approximate. Flagged `cho2014_gru` and `shi2015_convlstm` (true conv-recurrent precursor) as missing.*
72. ~~`perez2018_film`~~ — *Deepened against arXiv 1709.07871 (abstract + PDF). Author correction: "Bengio, Aaron" → "Courville, Aaron". FiLM (γ⊙x + β) is PRISM v1/v2's modulation primitive — explicit table mapping FiLM components to PRISM. Treue-Martínez-Trujillo FBA cast as the biological correlate of γ; β is the additive criterion. Feedback Transformer cast as generalization of FiLM.*
73. ~~`wu_he2018_groupnorm`~~ — *Deepened against arXiv 1803.08494 / ECCV 2018. GN is batch-size-independent — critical for the recurrent-rollout training used in change-detection. The MCLSTM memory file explicitly noted GroupNorm was load-bearing. §7 connects GN to Reynolds-Heeger divisive normalization.*
74. ~~`schulman2016_gae`~~ — *Deepened against arXiv 1506.02438 / ICLR 2016. The λ knob frames the bias-variance tradeoff in advantage estimation for the user's RL hub. §7 ties TD-residual to `glimcher2011_dopamine_rpe` and `cortico_basal_ganglia_thalamic_loops`. Flagged absence of a `td-lambda` concept node.*
75. ~~`funahashi1989_mnemonic_dlpfc`~~ — *New stub deepened against PubMed PMID 2918358 (abstract; journal landing 403). 288 PFC neurons, 87 delay-active, 79% directional, ODR task. Identified `memory-field`, `attractor-dynamics`, `dynamic-coding` as missing concept candidates for future taxonomy additions.*
76. ~~`goldman_rakic1995_cellular_wm`~~ — *Deepened against PubMed PMID 7695894 (no PubMed abstract available; reconstructed from canonical content). DOI 10.1016/0896-6273(95)90304-6. The synthesis paper for Funahashi 1989 delay activity. Promoted `relevance_to` to include `recurrent_vit` (in addition to `prism_v1`, `prism_v2`).*

**Note on parallel deepening.** Batches 17 and 18 were both tenth-and-eleventh parallel-agent batches; all 20 papers across both batches passed audit cleanly on first attempt. The pattern is now well-validated at scale. One file (`bahdanau2014_neural_translation`) was created from scratch via the agent's prompt — the create-vs-deepen distinction is invisible to the audit.

**Completed 2026-05-15 (cite-trail closures + foundational neuroscience — eleventh parallel-agent batch):**

77. ~~`cho2014_gru`~~ — *New file. Deepened against arXiv 1406.1078 (abstract; PDF binary). Original GRU paper; parent of every GRU-based model in the user's program. §7 covers five threads: ConvGRU/PRISM v1, gate → FiLM lineage, encoder-decoder → iterative VAE, bidirectional information flow, slow-fast dual memory.*
78. ~~`mnih2016_a3c`~~ — *New file. Deepened against arXiv 1602.01783. A3C foundation paper. `mnih2014_recurrent_attention` added to `related` (same first author, conceptual predecessor). §7 frames A3C async-parallel rollouts as conceptual precedent for multi-hub competition pattern.*
79. ~~`sutton1988_td`~~ — *New file. Sources paywalled (Springer auth, Sutton's site parked); content reconstructed from canonical TD($\lambda$) content + cross-check via Wikipedia + cross-reference to `schulman2016_gae`. §7 surfaces TD-residual as "competitive currency" for inter-hub competition (extending the brief). Flagged absence of `td-learning` concept node — recommended addition under "Decision and action."*
80. ~~`shi2015_convlstm`~~ — *New file. Deepened against arXiv 1506.04214. ConvLSTM is true conv-recurrent precursor. §7 develops five threads including ConvLSTM's $3\times3$ locality limit as the gap Feedback Transformer fills. Flagged absence of dedicated `convlstm-cell` concept (reused `convgru-cell`).*
81. ~~`greff2016_lstm_search_space_odyssey`~~ — *New file (id retains `greff2016_` despite TNNLS 2017 publication, matching dangling reference). Deepened against arXiv 1503.04069 abstract. fANOVA prescriptions (forget gate / output activation essential; peepholes optional; learning rate dominates). §7 ties to xLSTM, Recurrent ViT §6.7 ablations.*
82. ~~`hubel_wiesel1962_receptive_fields`~~ — *Deepened against PMID 14449617. Tagged `early-visual-cortex` and `cortical-anatomy` (dropped `primate-neurophysiology` since work was in cat). Flagged taxonomy gap: no general "animal-neurophysiology" or `cortical-columns` concept. §7 covers simple/complex hierarchy → CNN, V1 orientation tuning → FBA substrate, hierarchical wiring → PRISM multi-stage.*
83. ~~`felleman_vanessen1991_hierarchical_cortex`~~ — *Deepened against PMID 1822724. 32-area hierarchy, 305 connections, ascending/descending classification. §7 makes four required connections: bidirectional hierarchical feedback grounding, Feedback Transformer per-direction Q/K/V justification, multi-stage processing bounded by 10-level hierarchy, explicit companion framing with Bastos 2012, Sherman 2022, Weiler 2025. Flagged taxonomy gap: dedicated `ascending-descending-laminar-asymmetry` concept warranted.*
84. ~~`mishkin1983_two_pathways`~~ — *Deepened from canonical content (TINS 1983 paywalled, no PubMed abstract). Dorsal/ventral dichotomy as architectural basis for the user's multi-hub system. §7 covers PRISM v1 ConvGRU as dorsal-stream analog, Goodale-Milner perception-vs-action refinement.*
85. ~~`moran_desimone1985_selective_attention`~~ — *Deepened against PMID 4023713. Founding paper for V4/IT attention gating. §7 covers within-RF competition as the substrate the recurrent ViT's per-token attention implements; Reynolds-Heeger normalization formalization; McAdams-Maunsell tuning extension.*
86. ~~`ratcliff1978_drift_diffusion`~~ — *Deepened from canonical content (APA PsycNet returned loader page). DDM 4 parameters (v, a, z, Ter) mapped to sensitivity/bias/threshold/latency. §7 ties DDM to Sridharan 2017 multialternative SDT framework as modern descendant. `relevance_to` expanded to all three works.*

**Note.** Eleventh parallel-agent batch — all 10 completed first try, audit clean. Batch closed 5 dangling cite-trail references (cho/mnih/sutton/shi/greff) that were flagged by prior batches.

**Cumulative parallel-agent statistics through batch 19.** 110 papers deepened/created via parallel agents across 11 batches; **all 11 batches passed audit cleanly on first attempt**. The 10-papers-per-batch cadence with lean prompts (2-3 fetch attempts max) is the stable working pattern. Zero re-spawns needed in batches 17, 18, 19.

**Completed 2026-05-15 (IT / decision-making / PFC cluster — twelfth parallel-agent batch):**

87. ~~`tanaka1996_it_object_vision`~~ — *Deepened against PMID 8833438 / DOI 10.1146/annurev.ne.19.030196.000545. IT columnar organization, moderately complex feature combinations. Flagged taxonomy gaps: `columnar-organization`, `object-recognition` / `it-cortex`, `feature-similarity-gain`.*
88. ~~`dicarlo2012_object_recognition`~~ — *Deepened against PMID 22325196 / DOI 10.1016/j.neuron.2012.01.010. Hierarchical-untangling framework. §7 covers ViT layer transformation lineage, recurrent untangling extension, ConvGRU as temporal untangling.*
89. ~~`miller_cohen2001_pfc_function`~~ — *Deepened against PMID 11283309 / DOI 10.1146/annurev.neuro.24.1.167. PFC-biases-posterior-cortex framework. Flagged taxonomy gaps: `cognitive-control`, `rule-encoding`, `task-set-maintenance`, `executive-function`.*
90. ~~`riesenhuber_poggio1999_hierarchical_models`~~ — *Deepened against PMID 10526343 / DOI 10.1038/14819. HMAX as direct ancestor of CNN architecture. §7 frames the user's program as superseding HMAX via attention + recurrence + feedback.*
91. ~~`hanks_summerfield2017_perceptual_decisions`~~ — *Deepened from canonical content (PubMed redirect issue, paywall on direct PMID/DOI). Cross-species evidence-accumulation review. §7 frames the recurrent ViT as primate-decision-model.*
92. ~~`roitman_shadlen2002_lip_rt`~~ — *Deepened against PMID 12417672 / DOI 10.1523/JNEUROSCI.22-21-09475.2002. LIP ramping during RT decisions. Numerical specifics (cell counts, firing rates, latencies) framed as approximate. §7 connects LIP=sensitivity/SC=bias dichotomy.*
93. ~~`desimone1996_visual_memory_attention`~~ — *Deepened against PMID 8942962 / DOI 10.1073/pnas.93.24.13494. Explicit WM-attention link. Added `reynolds_chelazzi2004_attentional_modulation` to related (existing).*
94. ~~`sherman_guillery2011_distinct_functions`~~ — *Deepened against PMID 21676936. **DOI correction**: stub had `10.1152/jn.00181.2011`, corrected to `10.1152/jn.00429.2011`. Removed inaccurate `primate-neurophysiology` tag (paper is cat/rodent theory). Flagged taxonomy gaps: `efference-copy`, `thalamic-gating`.*
95. ~~`riley_constantinidis2016_pfc_persistent`~~ — *Deepened against PMID 26834579 / DOI 10.3389/fnsys.2015.00181. Defense of persistent-activity WM. §7 identifies three-paper spine: Funahashi 1989 (discovery) → Goldman-Rakic 1995 (mechanism) → Riley-Constantinidis 2016/2018 (defense). Flagged taxonomy gap: `activity-silent-working-memory` for the activity-silent counterpart.*
96. ~~`masse2019_circuit_wm`~~ — *Deepened against PMC7321806 / PMID 31182866 / DOI 10.1038/s41593-019-0414-3. Trained-RNN WM circuit model. §7 frames Masse as reconciliation between persistent-activity (Funahashi/Goldman-Rakic/Riley-Constantinidis) and activity-silent (Stokes/Mongillo) literatures. Added `slow-fast-recurrence` concept.*

**Notes from batch 20:**
- **DOI typo fixed mid-batch**: `sherman_guillery2011` had wrong DOI in original stub (`00181.2011` → `00429.2011`). One-off audit pass on remaining stubs' DOIs may be warranted.
- **Three-paper PFC-WM spine consolidated** through batches 18-20: Funahashi 1989 → Goldman-Rakic 1995 → Riley-Constantinidis 2016. Reverse-citation graph density is meaningfully improved.
- **Persistent-vs-silent debate** now well-anchored on persistent side (Funahashi, Goldman-Rakic, Constantinidis, Riley-Constantinidis, Masse) — Mongillo 2008 and Stokes 2013 emerged as the most load-bearing absences for completing the debate node.

**Cumulative parallel-agent statistics through batch 20.** 120 papers deepened/created via parallel agents across 12 batches; **all 12 batches passed audit cleanly on first attempt**. Zero re-spawns needed in batches 17-20.

**Completed 2026-05-15 (visual-attention / MOT / V1-foundation / WM-debate — thirteenth parallel-agent batch):**

97. ~~`wolfe2021_guided_search_6`~~ — *Deepened against PMC8965574 / DOI 10.3758/s13423-020-01859-9. Note: PMID 33547581 (listed in our prompt) resolves to an unrelated paper; PMC8965574 is the correct ref. GS6 integrates priority maps, attentional templates, and selection history.*
98. ~~`wolfe2011_scene_search`~~ — *Deepened against PMID 21227734 / DOI 10.1016/j.tics.2010.12.001. Dual-pathway (selective + nonselective) framework. Flagged taxonomy gaps: `dual-pathway-search`, `scene-gist`, `feature-integration-theory`.*
99. ~~`bundesen2005_neural_theory_attention`~~ — *Deepened against PMID 15783288 / DOI 10.1037/0033-295X.112.2.291. NTVA's weight equation, rate equation, filtering vs pigeonholing decomposition. Flagged taxonomy gap: `tva-framework`.*
100. ~~`tsotsos1988_complexity_vision`~~ — *Deepened from Tsotsos 2017 retrospective (PMC5552749) + canonical content (original paywalled). Complexity-theoretic motivation for selection. Flagged taxonomy gaps: `complexity-bound` / `np-complete-selection`, `selective-tuning`.*
101. ~~`gilbert_li2013_topdown`~~ — *Deepened against PMID 23595013 / PMC3864796 / DOI 10.1038/nrn3476. Top-down modulation in V1 review.*
102. ~~`heilman2003_neglect`~~ — *Deepened from canonical content (book chapter, no PMID/DOI). Identified as Heilman, Watson & Valenstein 2003, Clinical Neuropsychology 4th ed., Oxford UP. §7 proposes a falsifiable five-step model-neglect prediction: hemifield attention-logit masking + bilateral-simultaneous extinction test + decoder-side representational-neglect test.*
103. ~~`bettencourt_somers2009_mot`~~ — *Deepened against PMID 19761324 (stub had typo: 19761328) / DOI 10.1167/9.7.9. PMID correction noted. MOT target-enhancement / distractor-suppression.*
104. ~~`meyerhoff2017_mot_review`~~ — *Deepened from canonical content (all sources paywalled). Flagged taxonomy gap: `multiple-object-tracking` / `multi-focal-attention` as a missing concept under "Attention mechanisms."*
105. ~~`hubel_wiesel1968_macaque`~~ — *Deepened against PMID 4966457 / DOI 10.1113/jphysiol.1968.sp008455. Macaque V1 extension of 1962 cat work; primate-relevant simple/complex cells and columns.*
106. ~~`mongillo2008_synaptic_wm`~~ — *New file. Deepened against PMID 18339943 / DOI 10.1126/science.1150769. The activity-silent / synaptic-plasticity challenger to persistent-activity WM. Closes the persistent-vs-silent debate node together with Funahashi/Goldman-Rakic/Riley-Constantinidis/Constantinidis/Masse. **Critical taxonomy gaps flagged**: `synaptic-working-memory` and `activity-silent-memory` concepts both absent — recommended additions under "Memory mechanisms."*

**Notes from batch 21:**
- **Stub-correction patterns continue**: wolfe2021 had wrong PMID, bettencourt_somers2009 had wrong PMID. Confirms value of a future audit pass.
- **Persistent-vs-silent debate node closed** on the silent side with mongillo2008. Stokes 2013 (activity-silent fMRI/MEG evidence) remains as a load-bearing follow-up but is not in the seed.
- **Taxonomy gaps accumulating**: a dedicated curation pass to add `activity-silent-memory`, `synaptic-working-memory`, `multiple-object-tracking`, `selective-tuning`, `complexity-bound`, `tva-framework`, `cognitive-control`, `efference-copy`, etc. is increasingly warranted.

**Cumulative parallel-agent statistics through batch 21.** 130 papers deepened/created via parallel agents across 13 batches; **all 13 batches passed audit cleanly on first attempt**. Zero re-spawns needed in batches 17-21.

**Completed 2026-05-15 (attention / RL / adaptive-compute / FEP cluster — fourteenth parallel-agent batch):**

107. ~~`lisman_grace2005_hippocampal_vta`~~ — *Deepened against PMID 15924857 / DOI 10.1016/j.neuron.2005.05.002. Hippocampus-VTA loop for novelty-gated memory. Added `error-gated-update` and `slow-fast-recurrence` concepts.*
108. ~~`vijayraghavan_everling2021_muscarinic_wm`~~ — *Deepened against PMID 33790746. **Identity refinement**: actual paper is Vijayraghavan & Everling 2021 Front Neural Circuits 15:648624 ("Neuromodulation of Persistent Activity and Working Memory Circuitry in Primate Prefrontal Cortex by Muscarinic Receptors") — a review, not Nat Neurosci primary data. Galvin et al. 2020 Neuron may be what was conflated.*
109. ~~`maunsell2015_attention_mechanisms`~~ — *Deepened from canonical content (Annual Reviews paywalled). Multiplicity of attention mechanisms — supports multi-hub framing. Flagged taxonomy gaps: `noise-correlation-reduction`, `gamma-band-coherence`, `criterion-shift`/`sensitivity-vs-bias` as own concept.*
110. ~~`baluch_itti2011_topdown_mechanisms`~~ — *Deepened from canonical content (all DOI/PMID fetches 403'd). Taxonomy of top-down signals (spatial, feature, object, scene-gist, value-driven). Flagged taxonomy gaps: `scene-gist-priors`, `value-driven-attention`, `feature-similarity-gain`.*
111. ~~`ba2015_multiple_object_recognition`~~ — *Deepened against arXiv 1412.7755 (PDF extraction succeeded via pdftotext). DRAM = LSTM core + context net + REINFORCE+CE. §7 frames REINFORCE→PPO+GAE as the load-bearing architectural choice point between DRAM and recurrent ViT. Added `recurrent-attention` concept.*
112. ~~`banino2021_pondernet`~~ — *Deepened against arXiv 2107.05407. **Author correction**: stub had "Banino, Balaguer, Barreca…" — correct is "Banino, Balaguer, Blundell." Bayesian halting distribution + per-step prediction loss. §7 proposes a concrete PRISM v2 extension: $\lambda_n$ head + geometric prior $\lambda_p \approx 0.2$ matching default $n_{FR}=5$.*
113. ~~`graves2016_act`~~ — *Deepened against arXiv 1603.08983. Halting probability + cumulative-halting threshold + ponder cost. The prototype of PonderNet's variable-step learning. §7 connects to per-patch halting via GridCell RNN and per-hub halting in multi-hub system.*
114. ~~`boshra_kastner2022_attention_control`~~ — *Deepened against PMID 35850060 / PMC13014281 / DOI 10.1016/j.conb.2022.102605. Pulvinar/transthalamic/theta-rhythmic attention-control review. §7 has six anchors covering pulvinar = central self-attention substrate, CTC loops, multi-hub framing, theta sampling = $n_{FR}/n_{BR}$ iteration, theta-rhythmic re-arbitration = competition-emergent PC.*
115. ~~`brefczynski_deyoe1999_spotlight_fmri`~~ — *Deepened against PMID 10204545 / DOI 10.1038/7280. Direct fMRI visualization of attentional spotlight in human V1. Added `retinotopy` concept (existing in TAXONOMY).*
116. ~~`buckley2017_fep_mathematical`~~ — *Deepened against arXiv 1705.09156 (PDF extraction succeeded). Mathematical formalization of FEP — Laplace approximation, generalized coordinates, action equation, thermostat agent example. Added `variational-free-energy`, `precision-weighting`, `inner-inference-loop`, `generative-decoder` concepts.*

**Notes from batch 22:**
- **Identity corrections continuing**: vijayraghavan2021 (review not primary), banino2021 (author error in stub). 4 batches in a row have surfaced stub errors — a sweep of all remaining stubs' bibliographic fields before deepening would catch these proactively.
- **Adaptive-compute cluster consolidated**: graves2016_act ↔ banino2021_pondernet ↔ bai_kolter_koltun2019_deep_equilibrium_models ↔ wang2025_hierarchical_reasoning_model ↔ schmidhuber2015_learn_to_think now form a tight cite cluster anchored on the $n_{FR}$ iterate-count framework.
- **FEP cluster strengthened**: buckley2017_fep_mathematical provides the mathematical core that ties friston2006/2005/2010, feldman_friston2010, pezzulo_parr_friston2024, clark2013, aitchison_lengyel2017 into a coherent theoretical scaffold for the user's competition-emergent-PC thesis.
- **Pulvinar/CTC consolidated**: boshra_kastner2022 adds the modern Kastner-lab synthesis to sherman_guillery1998/2011/2022 + mckinnon_mo_sherman2025 + bastos2012/2015 + weiler2025 — the CTC concept is now the most densely-supported node in the graph.

**Cumulative parallel-agent statistics through batch 22.** 140 papers deepened/created via parallel agents across 14 batches; **all 14 batches passed audit cleanly on first attempt**.

**Completed 2026-05-16 (attention/WM cleanup — fifteenth parallel-agent batch):**

117. ~~`hu_dan2021_ic_sc_attention`~~ — *Deepened against DOI 10.1016/j.neuron.2021.10.004. Hu & Dan 2021 Neuron, IC → nBIC → SC pathway for auditory-cued visual spatial attention (mouse optogenetics). §7 ties to MSI hub.*
118. ~~`berggren_eimer2018_wm_load`~~ — *Deepened against PMID 30125222 / DOI 10.1162/jocn_a_01324. WM load disrupts template-guided selection. Flagged taxonomy gaps: `n2pc`/`lateralised-erp`, `wm-attention-shared-resource`.*
119. ~~`cutrell_marrocco2002_ppc_microstim`~~ — ***Stub correction**: DOI was wrong in stub (`00221-001-0921-8` → correct `00221-002-1032-x`), PMID was wrong (12012226 → 11976764). Orienting + alerting decomposition of PPC microstim. Flagged candidate: `posner_tripartite_attention` concept file (alerting/orienting/executive recurs across multiple papers).*
120. ~~`emrich2017_attention_wm_resources`~~ — ***Stub correction**: PMID 28447846 in our prompt resolves to an unrelated paper; correct PMID is 28368161. Attention dynamically allocates VWM resources. Added `schneegans_bays2017_feature_binding_wm` to related.*
121. ~~`cartella2024_human_attention_modeling`~~ — *Deepened against arXiv 2402.18673. **Identity refinement**: this is a *survey* paper (IJCAI 2024 Survey Track, 7 authors Cartella/Cornia/Cuculo/D'Amelio/Zanca/Boccignone/Cucchiara), not an empirical modeling study. Companion to hassanin2024 (DL-internal-attention survey).*
122. ~~`khezri2022_fep_chapter`~~ — ***Important identity flag**: this is Bijan Khezri 2022, "Free Energy Principle (FEP)", Ch. 4 of *Governing Continuous Transformation* (Springer Contributions to Management Science, DOI 10.1007/978-3-030-95473-4_4) — a **corporate-governance/management book chapter**, not a neuroscience text. Khezri is a corporate executive with a PhD in management from St. Gallen. Treated as out-of-domain witness in the FEP cluster.*
123. ~~`hollingworth2008_vstm_function`~~ — *Deepened against PMID 18248135 / DOI 10.1037/0096-3445.137.1.163. PMC full text fetched cleanly. Transsaccadic object correspondence. Flagged taxonomy gaps: `transsaccadic-memory`, `object-correspondence`, `change-detection-task`.*
124. ~~`lamy2006_grouping_no_attention`~~ — *Deepened against PMID 16617826 / DOI 10.3758/BF03193652. Pre-attentive perceptual grouping. Counterpoint to mehrani_tsotsos2023. Flagged taxonomy gaps: `perceptual-grouping`/`gestalt-grouping`, `pre-attentive-processing`, `awareness-without-report`.*
125. ~~`kruger2017_tva_salience`~~ — *Deepened against PMID 28537010 / DOI 10.3758/s13414-017-1325-6. TVA-extended salience modeling. Key empirical findings: power-function exponents (orientation b≈0.6, luminance b≈0.5), additive cross-dimensional combination, capacity C≈40-60 items/s. §7 frames softmax row-sum normalization as homologous to TVA capacity invariance.*
126. ~~`liu2024_human_attention_explainable_ai`~~ — *Deepened against PMID 38788290 / DOI 10.1016/j.neunet.2024.106392. **Title correction**: stub had "AI" abbreviated; published version uses "artificial intelligence." HAG-XAI uses human gaze as supervisory signal for CAM-family methods.*

**Notes from batch 23:**
- **Three stub corrections this batch** (cutrell_marrocco DOI/PMID, emrich2017 PMID, liu2024 title). Five batches running with stub errors surfaced. A bibliographic-cleanup pass on the 21 remaining stubs before deepening is increasingly warranted.
- **Identity refinements (not corrections, but worth recording)**: cartella2024 is a *survey* not an empirical paper; khezri2022 is a *management* chapter not a neuroscience text. Both required reframing of §7 connection to user's program.
- **Concept-file candidate strongly recommended**: `concepts/posner_tripartite_attention.md` (alerting/orienting/executive) would anchor multiple papers (cutrell_marrocco, mirpour, cavanaugh_wurtz, posner1980, krauzlis2013). Could be added in a future taxonomy/concept curation pass.

**Cumulative parallel-agent statistics through batch 23.** 150 papers deepened/created via parallel agents across 15 batches; **all 15 batches passed audit cleanly on first attempt**. The 10-papers-per-batch lean-prompt pattern is now thoroughly stress-tested.

**Completed 2026-05-16 (Herman-lab/Knudsen/WM-perception/ML-history — sixteenth parallel-agent batch):**

127. ~~`zenon_krauzlis2012_attention_deficits`~~ — *Deepened against PMID 22972195 / DOI 10.1038/nature11497. **Recording-area correction**: paper records from MT/MST (motion-sensitive), not V4. Body §6 notes the loose "V4-style" framing in downstream literature.*
128. ~~`herman2018_midbrain_decisions`~~ — *Deepened against PMID 30349100 / DOI 10.1038/s41593-018-0234-x. SC decoder explains 67% of RT variance. Herman is user's co-author on recurrent ViT.*
129. ~~`herman_arcizet2020_caudate_sc`~~ — *Deepened against PMID 32940607 / DOI 10.7554/eLife.53998. **Title correction**: "Attention-related modulation of caudate neurons depends on **superior colliculus** activity" (stub abbreviated). Caudate ↔ SC reversible-muscimol experiment. §7 proposes a falsifiable PRISM v2+ prediction: ablate central attention → Q-critic epoch-decoding collapses selectively.*
130. ~~`knudsen2007_fundamental_components`~~ — *Deepened against PMID 17417935 / DOI 10.1146/annurev.neuro.30.051606.094256. The four-component decomposition (WM, competitive selection, sensitivity control, top-down bias) is **the most direct conceptual ancestor of the multi-hub framing** — explicit mapping given in §7.*
131. ~~`miconi_vanrullen2016_feedback_attention`~~ — *Deepened against PMID 26890584 / DOI 10.1371/journal.pcbi.1004770. **Title correction**: stub had abbreviated form; full title "A Feedback Model of Attention Explains the Diverse Effects of Attention on Neural Firing Rates **and Receptive Field Structure**." Multiplicative-feedback model — directly relevant to Feedback Transformer.*
132. ~~`carlisle_kristjansson2018_wm_priming`~~ — *Deepened against DOI 10.1007/s00426-017-0866-6. Selection-history / priming as a third channel. Flagged taxonomy gap: `selection-history`/`intertrial-priming` concept.*
133. ~~`teng_kravitz2019_wm_alters_perception`~~ — *Deepened against DOI 10.1038/s41562-019-0606-6. VWM content directly biases perception. §7 frames bias as predicted by iterative-VAE decoder. Flagged taxonomy gaps: `sensory-recruitment-vwm`, `serial-dependence`.*
134. ~~`vanede2019_gaze_internal_wm`~~ — ***Venue correction**: stub had "Journal of Vision" — corrected to **Nature Human Behaviour** 3:462-470. **PMID correction**: 30988480 in prompt resolves to van Lieshout 2019 (curiosity) — DOI 10.1038/s41562-019-0549-y is correct. Micro-saccades track internal WM.*
135. ~~`sutton2019_bitter_lesson`~~ — *Deepened from incompleteideas.net essay. §7 addresses the tension head-on: the user's program is a deliberate bet *against* the Bitter Lesson — biological priors as compute-multipliers, not domain-engineering shortcuts. Articulates the three-part defense and the risk conditions under which the wager fails.*
136. ~~`springenberg2024_offline_actor_critic`~~ — *Deepened against arXiv 2402.05546. **Venue correction**: stub had "arXiv:2402.05546" — paper is ICML 2024. Perceiver-Actor-Critic (PAC) with MPO-style offline AC + Retrace($\lambda$) critic. §7 proposes behavior-policy → offline AC → online fine-tune as training pipeline for PRISM v2.*

**Notes from batch 24:**
- **Stub corrections continuing across six consecutive batches**: zenon_krauzlis (recording area), herman_arcizet (truncated title), miconi_vanrullen (truncated title), vanede2019 (wrong venue + wrong PMID), springenberg2024 (venue). The pattern is now well-established — a future curation pass with bulk DOI/PMID validation against bibliographic source would catch these proactively.
- **Herman lab thread now complete**: herman_krauzlis2017_sc_change_detection + herman2018_midbrain_decisions + herman_arcizet2020_caudate_sc all at full depth. The user's co-author lineage is fully traceable through the database.
- **Knudsen 2007 four-component → user's multi-hub mapping**: This is one of the strongest §7 connections in the database. The four-component decomposition (WM, competitive selection, sensitivity control, top-down bias) is conceptually pre-figurative of the user's multi-hub multi-objective architecture.
- **Sutton 2019 vs the user's program**: The Bitter Lesson essay is the closest thing to a *direct philosophical critique* of the user's neuroscience-aligned-architecture program. §7 treats this honestly rather than defensively — articulates the user's wager and the conditions under which it pays off vs. fails.

**Cumulative parallel-agent statistics through batch 24.** 160 papers deepened/created via parallel agents across 16 batches; **all 16 batches passed audit cleanly on first attempt**. The pattern is now thoroughly stress-tested across diverse paper types (theory, primary data, reviews, essays, position papers).

**Completed 2026-05-16 (final-cleanup batch — seventeenth parallel-agent batch — DATABASE COMPLETE):**

137. ~~`botta_lupianez2014_attentional_bias_vwm`~~ — *Deepened against PMID 24793127 / DOI 10.1016/j.actpsy.2014.03.013. Title: "Spatial distribution of attentional bias in visuo-spatial working memory following multiple cues." Endogenous/exogenous double-cueing study — spatial-distribution counterpart to van Moorselaar feature-template capacity finding.*
138. ~~`devalois1988_spatial_vision`~~ — *Deepened from canonical content (Oxford UP monograph, paywalled). Gabor-receptive-field synthesis tying Campbell-Robson psychophysical channels with V1 single-unit physiology. §7 grounds CNN first-layer filters and ViT patch projections.*
139. ~~`gresch2024_perception_wm_shifts`~~ — *Deepened against PMID 38278040 / DOI 10.1016/j.cognition.2024.105731. Gresch/Boettcher/van Ede/Nobre 2024 Cognition. Cross-domain (perception ↔ WM) attentional switching with unique control function.*
140. ~~`hoffman2016_attention_eye_movements`~~ — *Deepened against DOI 10.4324/9781315784762-4. Hoffman premotor-theory chapter in Routledge handbook. Covert-overt attention substrate-sharing.*
141. ~~`jehu2015_postural_attention`~~ — *Deepened against PMID 24655152 / DOI 10.3109/00207454.2014.907573. **Title correction**: "Prioritizing attention on a reaction time task improves postural control **and reaction time**" (stub was abbreviated). Dual-task prioritization, n=20.*
142. ~~`lemeur2006_coherent_attention`~~ — ***PMID correction**: prompt PMID 16683053 was wrong — correct is **16640265**. DOI 10.1109/TPAMI.2006.86 verified. Le Meur et al. saliency model with CC=0.70 vs Itti's 0.66.*
143. ~~`logie2003_mental_workspace`~~ — *Deepened from publisher metadata + canonical Logie visual-cache/inner-scribe framework (paywalled). DOI 10.1016/S0079-7421(03)01002-8. baddeley_hitch1974 omitted from `related:` (not in db).*
144. ~~`tas2016_attention_wm_covert_overt`~~ — *Deepened against PMC4977214 / DOI 10.1037/xhp0000212. **Authors update**: Tas, Luck & Hollingworth (not just Tas). Covert-vs-overt orienting dissociation in VWM encoding.*
145. ~~`vanderstigchel2009_topdown_limits`~~ — *Deepened against PMID 19635610 / DOI 10.1016/j.actpsy.2009.07.001. **Author list completed**: Van der Stigchel, Belopolsky, Peters, Wijnen, Meeter, Theeuwes (stub was truncated). Boundary conditions for top-down control — counterpoint to Gilbert-Li 2013.*
146. ~~`zhuang2021_unsupervised_ventral`~~ — ***PMID correction**: prompt PMID 33390503 was wrong — correct is **33431673**. DOI 10.1073/pnas.2014196118. Contrastive SSL (LA, IR, SimCLR, MoCo, CMC) matches/exceeds supervised on V4/IT brain alignment.*
147. ~~`zou2023_reading_attention`~~ — *Deepened against DOI 10.7554/eLife.87197. eLife article RP87197, published Nov 30 2023. Task-optimized transformer attention predicts human reading-time behavior. **The 235th and final paper.***

**Notes from batch 25 (final batch):**
- **Three stub corrections** (PMID for lemeur2006 and zhuang2021; truncated title for jehu2015; truncated authors for tas2016 and vanderstigchel2009). Seven consecutive batches with bibliographic stub errors — a future bulk-validation pass on the database's bibliographic fields would catch these proactively.
- **First-try-clean streak**: all 11 agents in this final batch wrote audit-passing files on the first try.

## Historical completion record (2026-05-16, refreshed 2026-05-19)

**Total cumulative parallel-agent work (batches 17-25):** 171 papers deepened/created via parallel agents across 17 batches; **all 17 batches passed audit cleanly on first attempt with zero re-spawns**.

**State at 2026-05-16 close-of-deepening:**
- 235 / 235 papers at full depth (100%) — 0 stubs.
- 257 graph nodes; 2058 graph edges.
- 15 concept files; 4 thread files. 0 audit issues.

**Historical post-routine snapshot (2026-05-19; not current — see the operator state at the top of this file):**
- **239 papers** (235 full-depth + 4 abstract-depth stubs added via the wiki-maintenance routine: `stanisor2013_v1_value_attention`, `bellemare2017_c51`, `dabney2018_qr_dqn`, `dabney2020_distributional_dopamine`).
- **261 graph nodes** (239 papers + 15 concepts + 4 threads + 3 works).
- **2504 graph edges**: anchors 214 (was 202, +12 since 2026-05-16 close), cites 1617 (was 1586, +31), has-concept 125 (was 114, +11), related-concept 73 (was 60, +13), relevant-to 465 (was 458, +7), touches-concept 10 (unchanged). **Run `python3 research_db/tools/build_graph.py` followed by `query.py stats` to refresh exact counts after each routine iteration.**
- 15 concept files unchanged. 4 thread files unchanged. **0 audit issues.**

**Top-cited papers (by inbound edges, end-state):** the friston/glimcher/krauzlis/desimone-duncan/bisley-goldberg cluster anchors the most densely-connected region; ConvGRU/PRISM/Feedback Transformer/multi-hub user-program concepts anchor the architectural cluster.

**Pending future curation work** (not blockers for any current task):
1. **Bulk DOI/PMID validation pass** — 7+ batches surfaced bibliographic stub errors; programmatically checking each paper's frontmatter against PubMed/DOI.org would catch remaining issues.
2. **Taxonomy expansion**: ~25 concept terms have been flagged as candidates during deepening:
   - Memory: `synaptic-working-memory`, `activity-silent-memory`, `sensory-recruitment-vwm`, `transsaccadic-memory`, `serial-dependence`, `variable-precision-model`, `memory-field`, `attractor-dynamics`
   - Attention: `multiple-object-tracking`/`multi-focal-attention`, `selective-tuning`, `complexity-bound`, `tva-framework`, `scene-gist-priors`, `feature-similarity-gain`, `value-driven-attention`, `feature-integration-theory`, `attentional-window`, `perceptual-grouping`/`gestalt-grouping`, `pre-attentive-processing`, `posner-tripartite-attention`
   - Decision/control: `td-learning`/`temporal-difference`, `cognitive-control`, `rule-encoding`, `task-set-maintenance`, `executive-function`, `criterion-shift`/`sensitivity-vs-bias`, `evidence-accumulation`
   - Circuits: `ascending-descending-laminar-asymmetry`, `cortical-columns`, `animal-neurophysiology`, `efference-copy`, `thalamic-gating`, `premotor-theory-of-attention`, `oculomotor-priority-map`
   - ML: `convlstm-cell`, `forget-gate-bias-init`, `neural-architecture-search`, `noise-correlation-reduction`, `gamma-band-coherence`, `gaze-prediction`/`scanpath-prediction`
3. **Cite-trail closures still missing** (papers referenced from existing entries but not yet stubbed): Stokes 2013 (activity-silent fMRI/MEG), Compte 2000 (bump attractor), Wang 1999 (NMDA bistability), Mongillo precursors, Universal Transformer, MPO/V-MPO/CRR/AWAC/IQL (offline RL), Decision Transformer, Tsotsos 1995 Selective Tuning, baddeley_hitch1974 (WM foundation), Cohen-Maunsell 2009 (V4 attention dissociation), etc.
4. **Concept-file candidate**: `concepts/posner_tripartite_attention.md` (alerting/orienting/executive) would anchor 5+ papers.

### Sourcing access (2026-05-13 audit)

WebFetch against `arxiv.org` succeeded in this session for both abstract pages and PDFs. The previous sourcing debt on Schmidhuber 2015 and HRM 2025 is therefore partially resolved:

- **HRM (Wang et al. 2025) — verified.** The arXiv PDF v3 was successfully accessed and read; the deepening entry has been revised against the PDF and the sourcing caveat removed.
- **Schmidhuber 2015 — partially verified.** The abstract page was successfully fetched and confirms the title, sole author, and high-level claims; the PDF was downloaded but its binary stream could not be parsed for body text in this session. The conceptual claims are confidently sourced; specific equations or empirical content remain unverified at the paragraph level.

Both entries' sourcing notes have been updated to reflect this status.

### Outstanding sourcing debt

- Schmidhuber 2015 PDF body content (equations, AIT formalism, any empirical demonstrations) — a future session should re-attempt PDF extraction or use `pdftotext` on the downloaded file.
- The 10 manual cite-trail stubs (Section F) and the 5 programmatic-PubMed stubs (Section E) are metadata-only and pending deepening.
- The 4 abstract-depth stubs added by the post-completion routine (`stanisor2013_v1_value_attention`, `bellemare2017_c51`, `dabney2018_qr_dqn`, `dabney2020_distributional_dopamine`) are pending promotion to full depth. The three distributional-RL papers are blocking the creation of `concepts/distributional_critic.md` (see SKILL queue).

## Post-completion wiki-routine activity (2026-05-17 — 2026-05-19)

After the database hit nominal completion on 2026-05-16, work shifted from paper-deepening to **structural/edge-building maintenance** via the wiki-routine at `.claude/scheduled-tasks/do-some-research/SKILL.md`. This subsection summarises iterations to date; the SKILL file's RUN LOG is the authoritative per-iteration record.

**Run 2026-05-17 (FT anchor expansion + thread synthesis).** Concept `feedback_transformer` anchor papers expanded 6 → 14 (added weiler2025, larkum2013, bahdanau2014, voita2019, sherman2022, mckinnon2025, bastos2012, felleman_vanessen1991). Concept body extended with "Architectural antecedents" and "Biological correlate" subsections. Thread `the_user_architectural_program` §6 extended with HRA empirical results. Open question 4 (FT-attention-uniform mystery) connected to voita2019 head-collapse + schulman2017_ppo flat-minima literature, generating a code-side follow-up proposal for an attention-supervision auxiliary in HRA. *Graph delta:* +8 anchors edges (202 → 210).

**Run 2026-05-17 (D6 grounding in MODEL_DESIGN.md).** Appended "Wiki anchors for D6" subsection to `MODEL_DESIGN.md` citing 6 papers organised by three axes (algorithmic / neuroAI / primate biology). Added reciprocal `related:` edge botvinick2020 ↔ monosov2020. Added `distributional-rl` concept to monosov2020. *Graph delta:* +2 cites edges. *Surfaced gap:* `concepts/distributional_critic.md` does not exist, so `distributional-rl` taxonomy term creates 0 graph edges — three QR-DQN-lineage paper stubs (Bellemare 2017, Dabney 2018, Dabney 2020) referenced by name in existing entries but missing from the db.

**Run 2026-05-18 (inverse FT edges + concept-to-concept sweep).** Added `feedback-transformer` to `concepts:` frontmatter of all 8 new FT anchor papers, so the previously-1 incoming has-concept edge to FT became 9. Swept all 15 concept files for missing "Connection to other concepts" mentions of canonical concept ids — added 12 new related-concept edges, each with a one-sentence justification. *Graph delta:* +8 has-concept, +12 related-concept (60 → 72 total). *Surprise:* discovered an orphan paper file `stanisor2013_v1_value_attention.md` (mtime ~7h before this run) of unknown provenance — flagged for integration; this run formally added it to INDEX.md Section F on 2026-05-19.

**Run 2026-05-18 (thin-concept anchor build-up).** Surveyed all 15 concepts; 5 had ≤7 anchored papers. Brought 4 of them up to 8: `apical_basal_dendritic_integration` (+weiler2025), `cortico_thalamo_cortical_loops` (+choi2023), `coupled_rnn_world_models` (+mujika2017), `iterative_variational_encoder_decoder` (+buckley2017). Each anchor addition was justified by a body extension in the concept file, not a bare frontmatter edit. Reciprocal has-concept edges added on the 3 papers that did not already declare the concept. *Graph delta:* +4 anchors (210 → 214), +3 has-concept, +1 related-concept (72 → 73).

**Run 2026-05-19 (this iteration — INDEX refresh + distributional-RL stubs).** Updated this Final Statistics block to reflect graph drift since 2026-05-16. Created 3 new abstract-depth stubs (`bellemare2017_c51`, `dabney2018_qr_dqn`, `dabney2020_distributional_dopamine`), each with a verbatim or paraphrased abstract sourced via arXiv WebFetch and PubMed. Wired into `concepts:[distributional-rl]` and reciprocally linked into the `related:` lists of `botvinick2020_deep_rl_neuro` (+3), `hikosaka2006_bg_reward_eyes` (+1), `schulman2017_ppo` (+2), `babayan_uchida_gershman2018_belief_states_dopamine` (+1), `monosov2020_outcome_uncertainty` (+1). Fixed a placeholder id (`dabney2020_distributional_rl_dopamine` → `dabney2020_distributional_dopamine`) in the §8 of hikosaka2006. Formally listed the orphan `stanisor2013_v1_value_attention` and the 3 new stubs in Section F. *Graph delta:* +3 papers (236 → 239); +25 cites (1592 → 1617); +3 relevant-to (462 → 465). **has-concept unchanged at 125** — the 3 new stubs each declare `concepts:[distributional-rl]` but the corresponding concept file does not yet exist, so the edges silently fail to graph (queued task: create `concepts/distributional_critic.md`).

### Routine outlook

The wiki-routine maintains the database as a *graph* rather than just a *bibliography*. Per-iteration patterns observed across the first 5 runs:

1. **Edge-building (Type B) is the highest-leverage work** — concept anchor lists and reciprocal has-concept edges are where structural query reachability is built. Concept files that earn 8+ anchors transition from "stub with three papers" to "useful starting point for cross-paper retrieval."
2. **Wiki ↔ HRA grounding (Type D) is where the routine pays for itself for the user.** The 2026-05-17 D6 grounding entry in `MODEL_DESIGN.md` is the proof-of-concept: a HRA decision now cites 6 verifiable papers organised by an interpretable axis, instead of a vague "based on the literature."
3. **Adding a taxonomy term to a paper's `concepts:` list is a silent no-op unless the corresponding `concepts/<term>.md` file exists.** This is the routine's single most common failure mode. Future runs should pair-check.
4. **The marginal anchor becomes "spiritual fit but not literal fit" as concept anchor sets fill toward 10+.** Future runs should be explicit about this rather than padding for count.
