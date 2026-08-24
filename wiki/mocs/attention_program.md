---
id: attention_program
type: moc
status: stable
created: 2026-07-11
tags:
  - topic/attention
  - topic/recurrent-vision
  - topic/value-directed-attention
scope: "Top-level map of the empirical, architectural, and normative attention research program"
summary: "The attention program contains several related but non-identical lineages: the 2025 empirical Recurrent ViT, PRISM proposals, RViT+ experiments and manuscript, and the separate 2026 normative VDA paper with its repair chain. This hub routes readers without treating those lineages as successive versions or claiming convergence."
see_also:
  - slug: attention_program_lineage_boundaries
    rel: defines
    summary: "Sets the lineage boundaries and scoped evidence-authority orders used throughout this hub."
  - slug: recurrent_vit
    rel: informs
    summary: "Routes to the 2025 Morgan–Albanna–Herman empirical baseline, arXiv:2502.10955."
  - slug: prism_v1
    rel: informs
    summary: "Routes to the first predictive-coding PRISM proposal and its historical empirical lessons."
  - slug: prism_v2
    rel: informs
    summary: "Routes to the distinct hierarchical PRISM v2 proposal and its unfulfilled scale-up claims."
  - slug: rvit_plus
    rel: informs
    summary: "Routes to the RViT+ design, current producer, battery, and upgraded empirical manuscript."
  - slug: vda_normative_repair
    rel: informs
    summary: "Routes to the separate normative VDA paper and its Critique/Rebuild/Reconstruction repair chain."
---

# Attention research program

## TL;DR

This workspace contains companion empirical, architectural, and normative projects, not one continuous paper lineage. Start with the lineage brief, then enter the project hub matching the question; no current run should be described as converged, and the partial sixteen-item VDA runs, whose stop reason is unknown, are not completed failures.

## Plain explanation

The 2025 Recurrent ViT paper reports an empirical recurrent neural model of cued visual change detection. PRISM v1 and v2 are architecture proposals centered on predictive coding. RViT+ is a later empirical engineering and manuscript line with checkpoints, behavioral analyses, and causal interventions. A separate 2026 paper asks a normative question—when an ideal observer should change decision criteria, reallocate sensitivity, or use a decorrelation lever—and is repaired through Critique, Rebuild, and the canonical Reconstruction.

These projects inform one another, but a shared phrase such as “value-directed attention” does not make their evidence interchangeable. See [[attention_program_lineage_boundaries]] before moving claims between hubs.

## Reading routes

1. **Published empirical baseline:** [[recurrent_vit]].
2. **Predictive-coding architecture proposals:** [[prism_v1]] then [[prism_v2]].
3. **Current empirical producer and manuscript:** [[rvit_plus]].
4. **Normative theory and repair:** [[vda_normative_repair]].

## Current boundaries

- The current empirical battery is based on separately trained checkpoints. Fixed evaluation batches characterize within-model evaluation uncertainty; they are not training replications.
- The archived VDA1/2/4/9 ladder mixes validity semantics and, at the 4-to-9 transition, geometry and model-interface dimensions. It supports a qualified cross-checkpoint association, not a pure capacity law.
- VDA16 is partial/incomplete, and the stop reason is unknown. Task correctness remained near chance at checkpoint 599; the preserved evidence does not establish failure after a consumed training budget.
- Exact-validity and fixed-grid code added on 2026-07-11 applies prospectively. No completed corrected analysis or controlled fixed-grid training result exists yet.

## Project artifacts

- Research-state synthesis: `reports/research_state/2026-07-11_research_state_briefing.md`
- Implementation status: `reports/research_state/2026-07-11_implementation_log.md`
- Empirical evidence ledger: `reports/upgraded_paper/EVIDENCE_LEDGER.md`
- Run registry: `research_db/registry/projects.json` and `research_db/registry/artifacts.jsonl`
