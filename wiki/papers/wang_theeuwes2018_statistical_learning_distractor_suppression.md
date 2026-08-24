---
id: wang_theeuwes2018_statistical_learning_distractor_suppression
title: "Statistical regularities modulate attentional capture"
authors:
  - "Wang, Benchi"
  - "Theeuwes, Jan"
year: 2018
venue: "JEP:HPP"
doi: "10.1037/xhp0000472"
arxiv: ""
url: "https://pubmed.ncbi.nlm.nih.gov/29309194/"
tags:
  - visual-attention
  - psychophysics
concepts:
  - priority-map
related:
  - failing_theeuwes2018_selection_history
  - hickey2010_reward_salience_acc
  - desimone_duncan1995_biased_competition
  - bisley_goldberg2010_parietal_priority
relevance_to:
  - recurrent_vit
  - prism_v1
  - prism_v2
seed_source:
  - manual
status: stub
depth: abstract
last_updated: "2026-05-19"
---

# Statistical regularities modulate attentional capture

## 1. Abstract

The present study investigated whether statistical regularities can influence visual selection. We used the classic additional singleton task in which participants search for a salient shape singleton while ignoring a color distractor singleton. The color distractor singleton was systematically presented more often in 1 location than in all other locations. For this high-probability location, we found that both the amount of attentional capture by distractors and the efficiency of selecting the target were reduced. There was a spatial gradient of suppression, as the attentional capture effect and the efficiency of selecting the target scaled with the distance from the high-probability location. Some participants were aware of the statistical regularities, but this did not affect the results whatsoever. We interpret these findings as evidence that spatially statistical regularities that are unknown to the observer can influence attention such that locations that have a high probability of containing a distractor are suppressed relative to all other locations. (Verbatim published abstract; Journal of Experimental Psychology: Human Perception and Performance 44(1):13–17. Source: PubMed PMID 29309194, DOI 10.1037/xhp0000472.)

<!--
Stub added 2026-05-19 by the VDA skeptical-reviewer agent (run-007, CR-031),
depth: abstract, per mission §4.2 of agents/skeptical_reviewer_prompt.md.
This is the canonical "statistical learning of distractor locations"
demonstration; it is the suppression-history complement to
failing_theeuwes2018_selection_history (which lists this paper in its §8
"citations to follow"). Used as primary evidence in the C4 (no-inversion)
literature attack: the suppressed location is a low-target-probability /
high-distractor-probability location, i.e. an ANTI-CUED (V < 1/N) location
in the target paper's model — exactly the regime in which the model itself
predicts below-uniform allocation (see Critique/verdicts/C4--no-inversion.md
Version 0.2). It is therefore NOT a counterexample to C4's V >= 1/N scope.

Two closely related primary papers were read at abstract depth from PubMed in
the same run but NOT stubbed (mission §8.5 "increments, not leaps"); they are
cited by full bibliographic reference in the C4 verdict and queued for
stubbing as CR-035:
  - Wang, Samara & Theeuwes (2019) "Statistical regularities bias overt
    attention", Atten Percept Psychophys 81(6):1813–1821, PMID 30919311,
    DOI 10.3758/s13414-019-01708-5 — eye-tracking: fewer saccades land at the
    high-probability distractor location; raised saccade latency to targets
    appearing there.
  - Kong, Li, Wang & Theeuwes (2020) "Proactively location-based suppression
    elicited by statistical learning", PLoS ONE 15(6):e0233544, PMID 32479531,
    DOI 10.1371/journal.pone.0233544 — biased-competition resource
    reallocation: suppressing the distractor location yields MORE attention at
    the target location (the behavioural analogue of the paper's §5.1 zero-sum
    reallocation framing).

Taxonomy gap noted (not acted on; surfaced to owner in the C4 verdict's Wiki
cross-references): research_db has no `selection-history` or
`statistical-learning-of-priority` concept; closest-fit existing concept
`priority-map` was used. The paper would justify adding such a concept.
-->
