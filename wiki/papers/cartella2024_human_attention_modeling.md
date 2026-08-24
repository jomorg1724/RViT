---
id: cartella2024_human_attention_modeling
title: "Trends, Applications, and Challenges in Human Attention Modelling"
authors:
  - "Cartella, Giuseppe"
  - "Cornia, Marcella"
  - "Cuculo, Vittorio"
  - "D'Amelio, Alessandro"
  - "Zanca, Dario"
  - "Boccignone, Giuseppe"
  - "Cucchiara, Rita"
year: 2024
venue: "IJCAI 2024 (Survey Track)"
doi: ""
arxiv: "2402.18673"
url: "https://arxiv.org/abs/2402.18673"
tags:
  - visual-attention
  - saliency-models
  - deep-learning
  - review
concepts:
  - self-attention-over-tokens
  - attentional-spotlight
  - priority-map
  - top-down-feedback
  - recurrence-for-temporal-dynamics
related:
  - itti_koch2001_saliency_review
  - lemeur2006_coherent_attention
  - hassanin2024_attention_dl_survey
  - mehrani_tsotsos2023_attention_grouping
  - yamamoto2024_human_like_vit_attention
  - liu2024_human_attention_explainable_ai
  - dosovitskiy2020_vit
  - vaswani2017_attention
  - mnih2014_recurrent_attention
  - koch_ullman1984_winner_takes_all
relevance_to:
  - recurrent_vit
seed_source:
  - vit_paper_ref_120
status: full
depth: full
last_updated: "2026-05-16"
---

# Trends, Applications, and Challenges in Human Attention Modelling

## 1. Abstract

Human attention modelling has proven, in recent years, to be particularly useful not only for understanding the cognitive processes underlying visual exploration, but also for providing support to artificial intelligence models that aim to solve problems in various domains, including image and video processing, vision-and-language applications, and language modelling. This survey reviews recent efforts to integrate computational models of human attention — saliency prediction and scanpath prediction — into modern deep learning systems. The authors organise the field by predictive target (where humans look vs. how they look) and by downstream application (image and video processing, vision-and-language, language modelling, and domain-specific use cases such as autonomous driving and medical imaging). They close with a discussion of open challenges: scarcity of gaze data, privacy implications of large-scale eye-tracking, synthetic-scanpath generation, and integration of attention models with wearable devices and AR/VR. A companion GitHub repository (`awesome-human-visual-attention`) catalogues the literature.

## 2. Why this matters for us

Cartella et al. is the most recent comprehensive map of the *human-attention-modelling* sub-field, written from the deep-learning side rather than the cognitive-neuroscience side. It is the natural complement to Hassanin et al. 2024 (`hassanin2024_attention_dl_survey`) which surveys *attention mechanisms inside DL models*, and to Itti & Koch 2001 (`itti_koch2001_saliency_review`) which surveys the *cognitive* saliency-prediction tradition. For the Recurrent ViT program, the survey supplies three useful things at once: (i) it situates the published Recurrent ViT result — softmax self-attention maps that align with primate change-detection attention — inside a much larger literature on deep gaze prediction, identifying which prior work already takes the architectural step of reading attention out of self-attention vs. out of a dedicated saliency head; (ii) it inventories the eye-tracking and saliency benchmarks (SALICON, MIT1003, COCO-FreeView, DR(eye)VE, BDD-A, Ego4D, MIT/Tübingen) against which the Recurrent ViT, Yamamoto et al. (`yamamoto2024_human_like_vit_attention`), and any future PRISM-vs-DINO comparison should be evaluated; and (iii) it makes the field's *taxonomic distinction* — saliency vs. scanpath — explicit, which clarifies that the published Recurrent ViT result is a *task-driven saliency-like map* read off during change detection, not a sequential scanpath prediction. The survey's "Open Challenges" section also identifies precisely the gaps the user's program is positioned to fill: data scarcity (the user's RL formulation needs no gaze labels), top-down/goal-directed attention (under-explored according to the survey, but central to the Recurrent ViT's change-detection regime), and recurrent / temporal models (LSTM-based saliency refinement appears in the survey only briefly).

## 3. Key claims

1. Human attention modelling has crystallised into two predictive targets: *saliency prediction* (spatial attention maps over a static or short-clip stimulus) and *scanpath prediction* (sequential fixation trajectories), each with its own evaluation metrics and benchmark datasets.
2. Deep learning has displaced classical bottom-up saliency models (Itti–Koch family) on most benchmarks; the dominant architectures are convolutional encoders with optional recurrent (ConvLSTM) refinement, and more recently transformer encoders for long-range context.
3. Integration of human-attention signals into downstream AI systems is now a productive research direction across image and video processing, vision-and-language (captioning, VQA), language modelling, and domain-specific tasks (autonomous driving, medical imaging).
4. The field's growth is limited primarily by the *cost of gaze data collection* and by privacy concerns around large-scale eye-tracking, motivating work on synthetic scanpaths, wearable / AR-VR-based ecological data collection, and zero-shot / weakly-supervised regimes.
5. Goal-directed (top-down) attention prediction — as opposed to free-viewing — is identified as under-explored relative to its importance for real-world applications.
6. Transformer integration with saliency / scanpath prediction is a recent and active direction (Lou et al. 2022; gaze-guided ViTs for medical imaging), but the field has not yet converged on whether self-attention itself is a sufficient substrate for human-like attention or whether dedicated saliency heads remain necessary.
7. Gaze supervision in vision-and-language models is one of the strongest cases for human-attention integration in modern DL: predicted or measured fixations consistently improve captioning, VQA, and video QA, with the effect attributable in part to gaze acting as a weak alignment signal between image regions and language tokens.
8. Synthetic scanpath generation is a viable mitigation for gaze-data scarcity in NLP but remains under-developed in vision; this is identified as a near-term high-value research direction.

## 4. Methods

The paper is a survey, not an empirical study; its "method" is the taxonomy it imposes on the literature. The structure is:

**§ Introduction.** Motivates the survey by the dual role of human-attention modelling — explanatory (understanding cognition) and instrumental (improving AI systems). Distinguishes from prior surveys (notably Hassanin et al. 2024) by focusing specifically on *human* attention rather than attention mechanisms inside DL models.

**§ Human Attention Modelling.** Surveys the two predictive targets.
- *Saliency Prediction:* Itti–Koch-family bottom-up conspicuity maps; Judd et al.'s SVM with semantic features as the first incorporation of top-down information; deep saliency networks built on convolutional encoders; Cornia et al.'s ConvLSTM-based iterative refinement of the predicted saliency map; Lou et al. (2022)'s Transformer encoder built on top of convolutional features to capture long-range context; time-specific saliency models that predict per-frame or per-moment attention; models that explicitly address inter-subject variability.
- *Scanpath Prediction:* classical winner-take-all over a saliency map (Koch & Ullman 1984); motor-bias models that incorporate saccade-amplitude and orientation priors; physics-inspired gravitational-model approaches; deep models with fixation-history conditioning; goal-directed / zero-shot semantic scanpath prediction for visual search.

**§ Integrating Human Attention in AI Models.** Surveys downstream applications.
- *Image & video processing:* gaze-guided image classification, action recognition, video summarisation; gaze-conditioned representation learning. The dominant pattern is to use a predicted or measured saliency map as a soft weighting over visual features, either at the input (cropping / masking) or at intermediate feature levels (attention-modulated pooling).
- *Vision-and-language:* gaze-augmented image captioning (Sugano & Bulling 2016 first integrated fixations into an RNN captioner; Cornia et al. 2018a switched to predicted saliency maps as a weighting prior); gaze-augmented VQA (Das et al. 2016 introduced VQA-HAT; Qiao et al. 2018 trained for human-like attention maps; Sood et al. 2021/2023 jointly supervised image and text gaze; Ilaslan et al. 2023 extended to collaborative video QA). Sood et al. 2021's finding that human text-attention correlates with VQA performance is highlighted as evidence that gaze supervision is informative even at the text level.
- *Language modelling:* gaze-augmented reading-time prediction and surprisal models, with predicted scanpaths over text used to weight loss contributions or to inform attention masking in transformer LMs.
- *Domain-specific:* autonomous driving (DR(eye)VE, BDD-A, EyeCar attention datasets; gaze-conditioned driver models that predict accident likelihood or attentive driving from gaze); medical imaging (Ma et al. 2023's gaze-guided ViT for chest X-ray diagnosis, where the gaze map masks attention away from diagnostically irrelevant regions; Karargyris et al. 2021's radiologist-eye-tracking dataset is the foundational resource).

**§ Open Challenges and Future Directions.** Six challenges are flagged:
1. *Data scarcity* — eye-tracking is expensive; wearable devices and ecological collection (Ego4D-style daily-life video) are the principal mitigations.
2. *Privacy* — large-scale eye-tracking raises consent and re-identification risks the field has not engaged with seriously.
3. *Synthetic data* — NLP has matured synthetic-scanpath generation for reading-time augmentation; vision has not.
4. *Wearables / AR-VR* — gaze-informed AI in everyday scenarios is identified as the natural deployment regime, with accessibility (visually-impaired users) called out as a high-value application.
5. *Real-time gaze prediction* in dynamic environments — a methodological gap, particularly relevant to driving and robotics.
6. *Multimodal gaze following* — predicting where a third party is looking from third-person video; a vision-and-language regime with applications in social cognition and HCI.

**Datasets inventoried.** SALICON (mouse-click proxy; Jiang et al. 2015); MIT1003 (free-viewing eye-tracking on static images; Judd et al. 2009); COCO-FreeView; DR(eye)VE (in-car gaze under varied driving conditions; Palazzi et al. 2018); BDD-A and EyeCar (accident-prone scenarios; Xia et al. 2018; Baee et al. 2021); VQA-HAT and VQA-MHUG (VQA with gaze); Ego4D (3,670 hours of daily-life egocentric video with gaze); Karargyris et al. 2021 (chest X-ray with radiologist eye-tracking); MIT/Tübingen Saliency Benchmark.

## 5. Results

As a survey the paper reports no new quantitative results; what it reports is the structure of the field and a curated reading list. The substantive findings are:

- *Deep saliency models dominate classical bottom-up saliency on every standard benchmark*, with the largest gains coming from the move to convolutional encoders pre-trained on large image datasets. Recurrent refinement (ConvLSTM, in the Cornia et al. line) and transformer-based long-range context (Lou et al. 2022's TranSalNet-style encoder over convolutional features) give further incremental gains, but the field has not converged on whether the marginal benefit of transformer integration scales with model size or whether it saturates at the level Lou et al. report.
- *Free-viewing benchmarks remain the dominant evaluation regime.* SALICON (mouse-click proxy) and MIT1003 (free-viewing eye-tracking) are the most-cited training and benchmark datasets, with the MIT/Tübingen Saliency Benchmark serving as the standardised leaderboard. Goal-directed / task-driven attention is much less benchmarked, with DR(eye)VE, BDD-A and EyeCar (driving) and the VQA-HAT / VQA-MHUG family (vision-and-language) the principal task-driven datasets.
- *Vision-and-language tasks consistently benefit from gaze supervision*, with the strongest documented effect in VQA where human text-attention correlates with model performance (Sood et al. 2021). Captioning, VQA, and collaborative video QA (Ilaslan et al. 2023) all show measurable gains from incorporating predicted or measured gaze.
- *Egocentric / ecological data collection is the most promising route around data scarcity*, with Ego4D (3,670 hours of daily-life egocentric video with gaze annotations) cited as the new benchmark scale for wearable / AR-VR-driven attention research.
- *Goal-directed scanpath prediction* remains an open problem, with zero-shot semantic scanpath prediction for visual search highlighted as a frontier area but with no clear leader on a standardised benchmark.
- *Time-specific saliency prediction* (per-frame or per-moment attention maps in dynamic scenes) is identified as a regime where deep models add the most value over classical bottom-up models, since inter-subject variability and rapid scene change defeat static saliency assumptions.
- *The survey's GitHub repository* (`awesome-human-visual-attention`) is offered as the live reference list; the survey itself is a structured entry point to a field whose literature is growing too fast for static review.

## 6. Critique / limitations

The survey's coverage of *transformer-based human-attention models* is shallow. It mentions Lou et al. 2022 as the first to put a Transformer encoder on top of a convolutional saliency backbone, and Ma et al. 2023's gaze-guided ViT for medical imaging, but it does not engage with the larger question — explicit in Mehrani & Tsotsos 2023 (`mehrani_tsotsos2023_attention_grouping`) and Yamamoto et al. 2024 (`yamamoto2024_human_like_vit_attention`) — of whether ViT self-attention is itself a model of human attention, or only a feature-extraction substrate over which a dedicated saliency head must be learned. This is a substantive omission given that two of the most-cited 2023–2024 results on the topic take opposite positions on exactly this question (Mehrani–Tsotsos: self-attention is grouping not attention; Yamamoto et al.: DINO-trained ViT self-attention does match human gaze on video free-viewing).

The treatment of *recurrence* is similarly thin. ConvLSTM-based iterative refinement (Cornia et al.) is mentioned, but the survey does not engage with the broader question of whether *task-driven* attention (which evolves within a trial) requires recurrence, nor with the recent recurrent-ViT literature including the Recurrent ViT paper (2502.10955), Mnih et al. 2014's Recurrent Attention Model, or the recurrent-vision-network literature (Kietzmann et al. 2019). The survey's recurrence discussion is essentially confined to "iterative refinement of a static map," not "evolution of attention over within-trial time."

The *biological-plausibility / neuro-AI bridging* discussion is absent. The survey roots its modelling tradition in feature integration theory, motor biases, and saccade priors, but does not engage with the predictive-coding tradition (Rao & Ballard, Friston), with biased-competition accounts (Desimone & Duncan), or with the cortical-microcircuit literature (Bastos et al.). For a review titled "Trends, Applications, and Challenges in Human Attention Modelling" this is a noticeable scope choice; the survey is squarely a *DL-engineering* survey of human-gaze prediction, not a cognitive-modelling survey.

The *scanpath section* is more cursory than the saliency section, despite scanpath dynamics being arguably the harder and more cognitively-loaded prediction problem. Goal-directed scanpath prediction in particular is identified as under-explored, but the survey does not offer a sharp account of why deep models have struggled with it.

The *evaluation methodology* discussion is missing. The survey lists benchmarks but does not critically discuss saliency-evaluation metrics (CC, NSS, AUC, sAUC, KLD), which is a known methodological hazard in the field — different metrics rank models differently, and CC-vs-NSS preferences can flip leaderboard positions. A reader who wants to compare numbers across papers cannot do so from this survey alone. The Bylinskii et al. 2019 methodological review of saliency metrics is the natural companion the survey does not cite.

The *temporal granularity* of human attention is acknowledged ("time-specific saliency prediction") but not unpacked. The distinction between within-fixation dynamics (microsaccades, sustained vs. dynamic attention) and between-fixation dynamics (scanpath) is collapsed.

Finally, the survey's bibliographic *cut-off* is early 2024 and it does not include the wave of late-2024/2025 work on ViT-attention vs. human-attention alignment (Yamamoto et al. 2024 `yamamoto2024_human_like_vit_attention`, Liu et al. 2024 `liu2024_human_attention_explainable_ai`, the Recurrent ViT 2502.10955). A reader using this survey as a 2026 reference must supplement with these papers.

The survey's *language-modelling* coverage is the thinnest of the application areas. Reading-time prediction and gaze-augmented surprisal are mentioned, but the recent line of work using LLM attention patterns as a proxy for human attention (and the converse — using human gaze to fine-tune LLMs) is not engaged with. This is a near-term growth area the survey under-represents.

The survey does not engage with the *generative-attention* literature: diffusion-model cross-attention maps and their relationship to human attention (a 2023–2024 development around prompt-controlled diffusion) are absent. This bears on whether the survey's saliency-prediction taxonomy will need to be reorganised once attention-as-readout-from-generative-models becomes a third pillar alongside saliency and scanpath prediction.

The survey's *taxonomy of training objectives* is implicit and underdeveloped. Models are grouped by predictive target (saliency vs. scanpath) and by downstream application, but not by the *objective* under which the attention model is trained — supervised on fixations, weakly-supervised on click-maps (SALICON), self-supervised, RL-trained on a downstream task, or implicit (read out of a feature extractor). The Yamamoto et al. and Recurrent ViT results both make the case that the objective is the load-bearing variable, not the architecture; a reorganisation of the survey's literature by objective would make this point visible.

The survey treats *attention* monolithically, without distinguishing overt (gaze-related) from covert attention. The Recurrent ViT and PRISM produce attention maps that are best interpreted as *covert*-attention proxies — internal selection signals that may or may not drive gaze. The distinction matters for evaluation: covert-attention proxies are not directly comparable to fixation density, even when they predict similar spatial structure. The survey does not address this distinction.

## 7. Connection to our work

Cartella et al. 2024 sits at the intersection of three threads in the database: the human-attention-modelling tradition (Itti–Koch, Le Meur, Cornia LSTM-saliency), the DL-attention-mechanisms tradition (Hassanin 2024, Vaswani 2017, Dosovitskiy 2020), and the recent ViT-vs-human-attention alignment literature (Mehrani–Tsotsos 2023, Yamamoto 2024, Liu 2024, Recurrent ViT 2502.10955). Its role for the user's program is as a *map* of the human-attention-modelling field, against which the Recurrent ViT, PRISM v1/v2, and the Feedback Transformer program can be positioned.

**Bearing on the Recurrent ViT (2502.10955).** The survey's taxonomy splits human-attention models into saliency-prediction (spatial map) and scanpath-prediction (sequential trajectory). The Recurrent ViT result lives in neither cell cleanly: the model's softmax self-attention map, read off during change detection, is a *task-driven spatial attention map* that evolves *across recurrent passes within a trial*. It is closer to saliency than to scanpath, but unlike all saliency models surveyed by Cartella et al. it (i) emerges as a *byproduct* of a task-driven RL objective rather than from gaze supervision, and (ii) carries *within-trial temporal dynamics* of the kind the survey only addresses via per-frame "time-specific saliency." The user's positioning move is therefore: *the Recurrent ViT extends the human-attention-modelling literature into the regime of task-driven, recurrently-refined, label-free attention maps* — a regime the survey identifies as under-explored on three independent axes (top-down attention; recurrence; data-free supervision).

**Bearing on the Feedback Transformer / user's architectural program.** The survey's brief mention of Lou et al. 2022's transformer-augmented saliency backbone is the closest prior art to the Feedback Transformer's commitment to using self-attention as the attention readout, but Lou et al. add transformer layers *on top of* a convolutional saliency network — i.e., still treat self-attention as a feature-mixing operation over a separately-computed saliency representation. The user's program (`threads/the_user_architectural_program` §1) inverts this: self-attention *with multi-source recurrent feedback* is the attention mechanism, and no separate saliency readout is needed. The survey provides no example of this architectural commitment, which is a positive datum: the Feedback Transformer represents a genuinely novel architectural commitment in the human-attention-modelling literature.

**Bearing on validation against gaze data.** The survey's dataset inventory (SALICON, MIT1003, COCO-FreeView, DR(eye)VE, BDD-A, Ego4D, MIT/Tübingen) is the natural evaluation suite for any direct *Recurrent ViT vs. human gaze* comparison. The "Eye Tracking" section of the user's Evolution of Architecture document (thread §6) reports preliminary hierarchical-RViT eye-tracking results; following the survey's standardised benchmarks (MIT/Tübingen leaderboard; CC / NSS / sAUC / KLD metrics) would situate those results inside a comparable peer literature.

**Bearing on PRISM.** PRISM v1 substitutes a prediction-error map for the softmax attention map (`THESIS.md` §2.6); PRISM v2 reintroduces attention readout (`PRISM_V2_PROPOSAL.md` §3.4). On Cartella et al.'s taxonomy, both PRISM variants are *saliency-prediction* models, with PRISM v1 being a novel addition: a saliency map computed as a prediction error of an iterative inference loop, with no labels and no gaze supervision. A natural cross-validation is to evaluate PRISM v1's $S_t$ map and PRISM v2's attention map on SALICON / MIT1003 / MIT-Tübingen and compare both to the Recurrent ViT's attention map and to DINO's [CLS] attention (Yamamoto et al.). The survey provides the evaluation infrastructure for this comparison. Note that PRISM's $S_t$ as a saliency model is conceptually closest to the *prediction-error saliency* tradition (Itti & Koch 2001's bottom-up feature-anomaly maps reinterpreted in terms of top-down predictive-coding residuals); the survey does not cover this lineage, leaving it as a positioning opportunity for the PRISM papers.

**Bearing on goal-directed attention.** The survey identifies goal-directed attention prediction as under-explored. This is precisely the regime the Recurrent ViT and PRISM operate in (change detection — a task with explicit goals and time pressure, where gaze and attention are dominated by top-down signals). Positioning the user's program against the survey's "open challenges" framing — *we offer a recurrent, RL-trained, biologically-motivated architecture that addresses the survey's identified gap in goal-directed attention modelling* — is a publishable framing.

**Bearing on synthetic-data and label-free regimes.** The survey identifies synthetic scanpath generation and reduction of gaze-supervision requirements as open challenges. The Recurrent ViT and PRISM v1 are, in a strong sense, *label-free attention models*: their attention maps are produced as byproducts of task-driven RL or of prediction-error inference, requiring no gaze supervision at any stage. Framing the Recurrent ViT as "a gaze-supervision-free attention model that produces human-aligned attention maps" lands directly on the survey's data-scarcity open challenge. This is a publishable framing distinct from the change-detection-accuracy framing.

**Bearing on the wearable / AR-VR deployment regime.** The survey identifies wearable AR-VR devices as the natural deployment regime for gaze-informed AI. The Recurrent ViT's recurrent, on-the-fly attention map is naturally suited to this regime: it produces a continuously-updated spatial attention map under a task signal, which is precisely what an AR-VR accessibility application (e.g., a visually-impaired user's vision aid) needs. The user's program, taken seriously as a deployment direction, lands on the survey's "wearables" open challenge as well.

**Bearing on the bigger architectural thesis (Mehrani–Tsotsos / Yamamoto triangulation).** The survey is *neutral* on the deep question of whether ViT self-attention is itself a model of human attention. Mehrani & Tsotsos 2023 (`mehrani_tsotsos2023_attention_grouping`) says no (self-attention is grouping, not attention; needs feedback). Yamamoto et al. 2024 (`yamamoto2024_human_like_vit_attention`) says yes, but only for self-supervised DINO ViTs on free-viewing video. Liu et al. 2024 (`liu2024_human_attention_explainable_ai`) takes the explainability-from-gaze angle: human attention is a useful signal for *interpreting* what computer-vision models attend to, irrespective of whether the model's internal attention map matches. The user's program takes Mehrani–Tsotsos seriously — the architectural commitment to recurrent feedback into self-attention is the response — and predicts that the Yamamoto result will *strengthen* under recurrence (thread §1, §7). Cartella et al. provide the cognitive-task and dataset infrastructure under which all four positions (Mehrani–Tsotsos / Yamamoto / Liu / the user's program) can be tested against shared human-gaze ground truth.

**Bearing on the empirical strategy for publishing the Recurrent ViT line.** The survey's "Open Challenges" section essentially specifies the missing experiments that a follow-up Recurrent ViT paper could supply. Reading the survey as a *research roadmap*, the high-value experiments are: (i) evaluate the Recurrent ViT's attention map on MIT1003 / SALICON / MIT-Tübingen as a *zero-shot* saliency model — no gaze training, only the RL-trained change-detection model — and compare against deep-supervised saliency models; (ii) evaluate the Feedback Transformer's eye-tracking results (thread §6) on Ego4D and DR(eye)VE under the survey's standardised metrics; (iii) compare PRISM's prediction-error map and the Recurrent ViT's attention map as alternative *task-driven* saliency models, contributing to the under-explored goal-directed-attention regime the survey highlights. Each of these experiments has a natural home in the survey's taxonomy and addresses an open challenge the survey itself identifies.

**Bearing on the dual evaluation regime.** A natural consequence of (i)–(iii) above is that the Recurrent ViT and PRISM should be evaluated under *two* sets of metrics: change-detection accuracy (the original task) and human-attention-alignment (the post-hoc saliency comparison). The dual evaluation grounds the architectural claim — *recurrent self-attention with task-driven training recovers human-like attention* — in two independent observables. Cartella et al. supply the dataset and metric infrastructure for the second half of the dual evaluation.

## 8. Citations to follow

- `cornia2018_predicting_human_eye_fixations` — Cornia et al.'s ConvLSTM saliency-refinement model; the survey's main example of recurrent saliency, directly relevant to the Recurrent ViT's recurrent-attention claim.
- `lou2022_transalnet` — Lou et al.'s first integration of a Transformer encoder into deep saliency prediction; the closest prior art to the Feedback Transformer for human attention.
- `sood2021_multimodal_gaze_vqa` — Sood et al.'s finding that human text-attention correlates with VQA model performance; relevant to whether gaze supervision is a generally useful signal beyond vision.
- `judd2009_mit1003` — the MIT1003 free-viewing eye-tracking benchmark, foundational dataset for the saliency-prediction literature.
- `jiang2015_salicon` — SALICON mouse-click saliency benchmark, the largest deep-saliency training set and the de-facto pretraining corpus for modern saliency models.
- `palazzi2018_dreyeve` — DR(eye)VE driver-gaze dataset, the canonical task-driven gaze benchmark in the survey.
- `karargyris2021_chest_xray_eyetracking` — radiologist-eye-tracking dataset, relevant for domain-specific gaze applications and for any future RViT-on-medical-images evaluation.
- `ma2023_gaze_guided_vit` — Ma et al.'s gaze-guided ViT for medical diagnosis; an existing instance of feedback-from-gaze-into-ViT.
- `koch_ullman1984_winner_takes_all` — the WTA scanpath generation algorithm under saliency; foundational, cited by both Cartella et al. and Mehrani–Tsotsos.
- `kummerer2018_deepgaze` — supervised deep-gaze-prediction model, representative of the dominant saliency paradigm the survey covers.
- `bylinskii2019_saliency_metrics` — the methodological reference on saliency-evaluation metric choice, missing from the survey but essential for any cross-paper comparison.
- `xia2018_bdd_attention` — BDD-A driving-attention dataset.
- `baee2021_eyecar` — EyeCar accident-prone driving gaze dataset.
- `das2016_vqa_hat` — VQA-HAT, the foundational gaze-augmented VQA dataset.
- `qiao2018_human_attention_vqa` — Qiao et al.'s human-attention-supervised VQA model.
- `sood2023_multimodal_gaze` — Sood et al.'s multimodal (image + text) gaze-supervised model; relevant to vision-and-language gaze integration.
- `grauman2022_ego4d` — Ego4D foundational egocentric video dataset with gaze, the natural deployment regime for wearable / AR-VR attention models.
- `ilaslan2023_video_qa_gaze` — Ilaslan et al.'s collaborative video-QA-with-gaze model.
- `judd2009_learning_to_predict_where_humans_look` — Judd et al.'s SVM with semantic features, the first incorporation of top-down information into saliency.
- `sugano_bulling2016_seeing_with_humans` — Sugano & Bulling, first integration of fixation points into RNN captioning, foundational for vision-and-language gaze.
- `cornia2018a_paying_more_attention` — Cornia et al.'s saliency-as-prior captioning model; the canonical instance of "predicted saliency map weights a downstream task" in the survey.
- `mit_tubingen_saliency_benchmark` — the standardised leaderboard for saliency models; the natural target for any RViT-as-saliency-model evaluation.
- `zanca2019_gravitational_scanpath` — physics-inspired gravitational scanpath model; representative of the non-deep alternative scanpath tradition the survey covers and a candidate baseline for any sequential-attention follow-up.
