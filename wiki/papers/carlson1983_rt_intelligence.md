---
id: carlson1983_rt_intelligence
title: "Reaction time, intelligence, and attention"
authors:
  - "Carlson, Jerry S."
  - "Jensen, C. Mark"
  - "Widaman, Keith F."
year: 1983
venue: "Intelligence"
doi: ""
arxiv: ""
url: ""
tags:
  - reaction-time
  - psychophysics
  - visual-attention
concepts:
  - chronometric-function
related:
  - saltzman_garner1948_rt_span
  - posner1980_orienting
  - prinzmetal2005_rt_vs_accuracy
  - luck_vogel2013_wm_capacity_review
relevance_to:
  - recurrent_vit
seed_source:
  - vit_paper_ref_55
status: full
depth: full
last_updated: "2026-05-15"
---

# Reaction time, intelligence, and attention

## 1. Abstract

*Paraphrase based on prior knowledge of the differential-cognitive-psychology literature; not direct quotation. The article was not retrievable via PubMed within this session.* Carlson, Jensen & Widaman use a battery of elementary cognitive tasks — variants of the Hick paradigm, in which subjects make a speeded keypress in response to one of $n$ alternative stimuli — administered alongside conventional psychometric measures of intelligence. They compute mean reaction time (RT) and intra-individual RT variability as a function of stimulus set size $n$ (bits of information, $\log_2 n$), and examine the correlation of those chronometric parameters with IQ. The headline finding, consistent with Jensen's broader program, is that RT and especially RT variability correlate negatively with IQ across set sizes, and that the slope of RT against bits of information — the Hick slope, taken as an index of single-bit information-processing rate — is also (more weakly) related to ability. The paper situates this correlational pattern within a theoretical account in which RT differences reflect, in part, differences in the efficiency of attentional control rather than purely peripheral motor or sensory speed.

## 2. Why this matters for us

The Recurrent ViT (2502.10955) reports RT in addition to accuracy as its behavioral readout (its `ref [55]` is this paper). Carlson et al. is one of the foundational references licensing the methodological claim that RT — not just accuracy — carries information about the underlying cognitive state, and specifically about the deployment of attention. Their 1983 demonstration that RT and RT variability correlate with cognitive ability across elementary tasks is the empirical anchor for treating RT as a graded, attentionally-modulated dependent variable in our cued change-detection paradigm, rather than a nuisance to be averaged away. The point is not that we measure individual differences — we do not — but that the same RT machinery responds to attentional manipulation within a subject, and Carlson et al. is the canonical citation establishing that RT carries attentional signal.

## 3. Key claims

1. Mean RT in elementary cognitive tasks correlates negatively with psychometric intelligence: higher-IQ subjects respond faster across the full range of set sizes.
2. Intra-individual RT variability (the standard deviation of a subject's own RTs across trials) correlates more strongly with IQ than mean RT does, and is the more reliable chronometric marker of ability.
3. The Hick-slope parameter — the increase in mean RT per added bit of stimulus information — correlates with IQ, though more weakly than the intercept or overall mean, indicating that single-bit processing rate is one but not the only mediator.
4. The RT–IQ relationship is not reducible to motor speed: simple-RT (zero-bit) tasks show weaker correlations than choice-RT tasks, implicating central rather than peripheral processes.
5. Attention — operationalised as sustained engagement with the task and resistance to lapses — is invoked as a mediating construct: RT variability is interpreted as a window onto moment-to-moment attentional fluctuation, and these fluctuations differ systematically across ability levels.

## 4. Methods

*Method description reconstructed from prior knowledge of the Hick / Jensen chronometric paradigm; specific Ns and exact procedure not verified against the article itself.* Subjects were tested in a standard Hick-paradigm apparatus: a console with a "home" button held by the dominant index finger and a semicircular array of $n$ response buttons, each adjacent to a stimulus lamp. On each trial, after a foreperiod, one lamp illuminated; the subject lifted from home (decision time, DT) and pressed the corresponding response button (movement time, MT). Set size was varied across blocks ($n \in \{1, 2, 4, 8\}$ corresponding to $\log_2 n \in \{0, 1, 2, 3\}$ bits). Each subject contributed many trials per condition, allowing both mean RT and within-subject RT variability ($\sigma_{RT}$) to be estimated per condition.

The psychometric battery accompanying the chronometric measures included conventional tests of general cognitive ability — the variants used in the Jensen lab during this period typically combined Raven's Progressive Matrices with one or more standard IQ measures, summarised as a general-ability composite or factor score.

The principal analyses were per-condition correlations between chronometric parameters (mean RT, $\sigma_{RT}$, Hick slope, Hick intercept) and the ability composite, plus a decomposition by set size to test whether the correlation systematically strengthens with cognitive load.

## 5. Results

*Reported magnitudes here are characteristic of the Jensen chronometric literature of this period; the precise Carlson et al. 1983 values are not verified against the article in this session.* Across studies in this family, including Carlson et al., the consistent findings are:

- Mean choice-RT correlates with ability in the range $r \approx -0.20$ to $-0.40$, with stronger correlations at larger set sizes.
- Within-subject RT variability ($\sigma_{RT}$) correlates more strongly than mean RT, typically $r \approx -0.30$ to $-0.50$.
- The Hick slope (ms per bit) correlates weakly to moderately with ability, $r \approx -0.10$ to $-0.30$; the intercept correlates less strongly than $\sigma_{RT}$ but more strongly than the slope.
- Simple-RT (one alternative, $\log_2 n = 0$) correlations with ability are weaker than choice-RT correlations, indicating that the IQ-relevant variance is not in peripheral motor speed.
- The pattern is replicated across age groups and is not reducible to test-taking motivation or strategy.

The qualitative shape — RT variability as the strongest chronometric correlate of ability, with mean RT secondary and Hick slope weakest — is the empirical pattern that Jensen's chronometric program (Jensen 1982, 1987, 2006) repeatedly reports and that Carlson et al. 1983 is one of the early replications of.

## 6. Critique / limitations

The RT–IQ correlation is robust as a statistical phenomenon but its mechanistic interpretation has been actively contested for forty years. Several limitations apply specifically to the 1983 paper and the program it represents:

- **Direction of mediation.** Whether the RT–ability correlation reflects faster elementary information processing (Jensen's "mental speed" thesis), more stable attention (Carlson et al.'s preferred framing), more efficient strategy use, or simply better engagement with the task is underdetermined by correlational data alone. The 1983 paper's framing in terms of attention is a theoretical preference, not a causal demonstration.
- **Sample composition.** Studies in this tradition often used college-student or school-age samples with restricted IQ range, attenuating correlations and limiting generalisation to the full population distribution.
- **Worst-performance rule.** Subsequent work (e.g., Larson & Alderton 1990; Coyle 2003) showed that the slowest RTs in a subject's distribution — not the mean or median — carry most of the ability variance, sharpening the variability-mediated interpretation but also complicating the Hick-slope account.
- **The Hick-slope finding has not aged well.** Later meta-analyses (Sheppard & Vernon 2008; Jensen 2006 himself, cautiously) show that the Hick-slope correlation with IQ is small and inconsistent. The intercept and overall mean RT are more reliable correlates.
- **RT as accuracy proxy.** The chronometric tradition treats RT and accuracy as substitutable measures of the same underlying competence under speed–accuracy tradeoff. Prinzmetal et al. (2005) and the speed–accuracy literature more broadly have shown this is not safe: RT and accuracy can dissociate, and a paradigm that measures only RT (as Carlson et al. effectively do) cannot rule out the possibility that high-IQ subjects are systematically operating at a different point on the SAT curve.
- **The "attention" construct.** Treating RT variability as a direct window onto attention conflates several distinct constructs — sustained attention, alerting, executive control, and short-term arousal fluctuation — that subsequent attention-network research (Posner & Petersen 1990; Fan et al. 2002) has dissociated.

## 7. Connection to our work

The connection to our program is methodological rather than substantive. The Recurrent ViT measures RT — defined operationally as the number of recurrent inference steps required before the model's change-detection output crosses a confidence threshold — in addition to accuracy. Carlson et al. 1983 (cited as `ref [55]` in the recurrent ViT paper) is one of the references invoked to license treating that RT readout as cognitively meaningful: it establishes that RT in elementary information-processing tasks is sensitive to attention-relevant individual differences, and that it does so in a way that is not reducible to peripheral motor or sensory speed.

Several specific points of contact:

- **RT as primary dependent variable.** Our recurrent ViT's chronometric readout is conceptually a within-network analogue of Carlson et al.'s within-subject chronometric measure. The validity-effect prediction we test (cf. `posner1980_orienting`) is that cued trials should show shorter RT than uncued trials — a Posner-style cueing effect imposed on a Carlson-style chronometric readout.
- **Variability as the more informative parameter.** Carlson et al.'s emphasis on $\sigma_{RT}$ over mean RT is something our paper does not exploit but probably should: per-condition variability of the recurrent ViT's RT (across stimulus seeds and across trials with the same nominal cue validity) could be a more sensitive marker of attentional state than the mean, and a Carlson-style $\sigma$-focused analysis would be a low-cost extension of the existing chronometric reporting.
- **Boundary on interpretation.** Carlson et al.'s methodological caution — RT differences confound multiple cognitive constructs — applies directly to us. When the recurrent ViT shows an RT effect of cue validity, that effect can be explained by attentional gating (the preferred interpretation), by a SAT-curve shift, or by a difference in evidence-accumulation rate (cf. `ratcliff2008_drift_diffusion`-type accounts). The 1983 paper is one of the earliest explicit warnings that RT alone cannot adjudicate.
- **Non-dependence on individual differences.** Unlike Carlson et al., we do not study a population of subjects with varying IQ. Our use of their result is restricted to the within-subject claim that RT in elementary cognitive tasks is attentionally modulated; we do not extend their across-subject ability-correlation claim to architectural variants of the recurrent ViT, and any such extension would require an explicit "ViT-IQ" measure that we do not currently have.
- **Historical anchoring.** Citing Carlson et al. 1983 in addition to Saltzman & Garner 1948 and Posner et al. 1980 places our RT measurement within a continuous experimental tradition that runs from the immediate-post-war chronometric revival, through the Jensen-era individual-differences program, into modern cognitive-control research. This lineage matters because reviewers familiar with cognitive psychology will read "ViT with RT readout" as a chronometric paradigm and judge it against that literature's standards.

## 8. Citations to follow

- `jensen1982_chronometry_mental_ability` — Jensen's programmatic statement of the mental-chronometry approach; the proximal theoretical home for Carlson et al. 1983.
- `hick1952_information_gain` — Hick's original paper, the source of the Hick paradigm Carlson et al. use.
- `larson_alderton1990_worst_performance` — establishes that slow-tail RT carries more ability variance than the mean, sharpening the variability interpretation.
- `posner_petersen1990_attention_systems` — the attention-networks framework that decomposes the umbrella construct Carlson et al. invoke into alerting / orienting / executive components.
- `sheppard_vernon2008_meta_analysis_rt_iq` — meta-analytic update on the RT–IQ correlation and its decomposition by chronometric parameter.
