---
id: attention_program_lineage_boundaries
type: brief
status: stable
created: 2026-07-11
tags:
  - topic/attention
  - topic/research-lineage
  - topic/evidence-authority
summary: "Five boundaries govern the workspace: the 2025 empirical Recurrent ViT, the separate 2026 normative VDA paper, its Critique/Rebuild/Reconstruction repair chain, the RViT+ empirical line, and PRISM proposals. Evidence authority is scoped by lineage; no manuscript or wiki page overrides producer artifacts and audited provenance."
see_also:
  - slug: attention_program
    rel: defines
    summary: "Supplies the lineage and authority rules used by the top-level program map."
  - slug: recurrent_vit
    rel: informs
    summary: "Identifies arXiv:2502.10955 as the empirical Morgan–Albanna–Herman baseline."
  - slug: vda_normative_repair
    rel: informs
    summary: "Identifies Reconstruction as canonical and Rebuild as the deepest normative repair record."
  - slug: rvit_plus
    rel: informs
    summary: "Identifies RViT+ experiments and upgraded prose as extensions of the empirical baseline."
  - slug: prism_v1
    rel: informs
    summary: "Identifies PRISM v1 as an architectural proposal with separate historical evidence."
  - slug: prism_v2
    rel: informs
    summary: "Identifies PRISM v2 as a distinct pre-implementation hierarchical proposal."
  - slug: vda_battery_state_and_provenance
    rel: depends-on
    summary: "Provides the empirical run-level constraints that prose and wiki synthesis cannot override."
---

# Attention-program lineage boundaries and evidence authority

## TL;DR

The workspace contains five related but distinct lines: a 2025 empirical neural-model paper; a separate 2026 normative ideal-observer paper; that normative paper's audit and repair chain; RViT+ empirical experiments and manuscript; and PRISM architecture proposals. Authority must be evaluated inside the relevant line: primary/producer artifacts and audited provenance outrank manuscript prose and wiki summaries, while Reconstruction is the canonical normative manuscript and Rebuild is its deepest technical backstop.

## Plain explanation

Shared terms create a real risk of identity drift. “VDA” can refer to a normative quantity in an ideal-observer model or to an empirical family of trained recurrent-network tasks. “RViT” can refer to the published 2025 baseline or to later RViT+ checkpoints with different architecture and training. “PRISM” names proposals with their own prediction-error mechanisms. These projects can motivate tests for one another, but they do not share checkpoints, mathematical objects, or claim authority automatically.

## Research goal

Provide a compact rule set for deciding which artifact answers a lineage or evidence question and prevent results from being transferred across project families by name-level analogy.

## Method

The 2026-07-11 audit compared canonical paper/manuscript trees, producer code, run registries, raw metrics/checkpoint identities, derived analyses, evidence ledgers, and existing research-db threads. The boundaries below retain the strongest artifact that directly establishes each claim and mark manuscript/wiki layers as synthesis rather than primary evidence.

## Finding

### 1. Empirical Morgan–Albanna–Herman baseline

The 2025 paper *A recurrent vision transformer shows signatures of primate visual attention* (arXiv:2502.10955v1) is the empirical Recurrent ViT baseline. It is the predecessor of RViT+ and is not the source manuscript being corrected by Critique/Rebuild/Reconstruction. Route through [[recurrent_vit]].

### 2. Separate normative VDA paper

`Critique/source/main.pdf`, *When Does Value-Directed Attention Matter? A Normative Model with Independent Attentional Benefit and Cost*, is a stationary ideal-observer/signal-detection model. It contains no recurrent transformer, actor–critic training run, or model checkpoint.

### 3. Normative repair chain

The repair roles are complementary, not interchangeable:

- `Critique/` attacks claims and preserves live verdicts and replications.
- `Rebuild/` is the deepest technical repair and provenance record; `Rebuild/CLAIM_LEDGER.md` sets the claim-strength ceiling.
- `Reconstruction/` is the canonical corrected public-facing manuscript; `Reconstruction/TRACE.md` maps its assertions back to repair artifacts.

Thus Reconstruction is canonical for current normative prose, while Rebuild controls technical depth and permissible strength. Route through [[vda_normative_repair]].

### 4. RViT+ empirical line

`RVIT_PLUS_DESIGN.md`, the historical [[rvit_plus_engineering]] thread, the current producer `RViT_plus_paper_jepa_grid9/`, registered runs, saved analyses, and `reports/upgraded_paper/` form an empirical extension of the 2025 baseline. The current manuscript is affine-feedback only. It is not a corrected edition of the normative paper, even when it tests value and validity manipulations.

### 5. PRISM proposal line

`Prism/docs/THESIS.md` and `Prism/docs/PRISM_V2_PROPOSAL.md` describe PRISM v1 and v2 architecture programs. PRISM v2 is explicitly pre-implementation in its proposal. Historical outcomes need preserved run evidence or an audited state report; proposal text alone does not establish successful experiments. Route through [[prism_v1]] and [[prism_v2]].

## Evidence authority order

Use a scoped order rather than one global list:

### Empirical trained-model claims

1. Producer code and task semantics tied to the checkpoint.
2. Run registry plus raw metrics and checkpoint identity.
3. Versioned derived analysis with trial/replay provenance.
4. Evidence ledger and audited research-state reports.
5. Current empirical manuscript prose and figures.
6. Research-db notes, briefs, and MOCs as routing/synthesis.

A later layer may explain an earlier one but cannot manufacture missing seeds, commands, checkpoints, or results.

### Normative claims

1. `Reconstruction/manuscript/` for the canonical corrected narrative.
2. `Reconstruction/TRACE.md` for its provenance map.
3. `Rebuild/CLAIM_LEDGER.md`, simulations, derivations, and model tests for strength and technical detail.
4. Current `Critique/verdicts/` and associated attacks when checking survival under criticism.
5. `Critique/source/main.pdf` for original wording and framing, not for claims superseded by repair.
6. Research-db pages as navigation and synthesis.

If a current Critique verdict or Rebuild artifact conflicts with stale prose, report the conflict and do not silently elevate the prose.

## Evidence

- Lineage synthesis: `reports/research_state/2026-07-11_research_state_briefing.md`
- Implementation status: `reports/research_state/2026-07-11_implementation_log.md`
- Empirical registry: `research_db/registry/projects.json` and `research_db/registry/artifacts.jsonl`
- Empirical claim ledger: `reports/upgraded_paper/EVIDENCE_LEDGER.md`
- Normative source: `Critique/source/main.pdf`
- Normative attack layer: `Critique/README.md` and `Critique/verdicts/`
- Normative repair ceiling: `Rebuild/CLAIM_LEDGER.md`
- Canonical normative provenance: `Reconstruction/TRACE.md`
- Canonical normative manuscript: `Reconstruction/manuscript/main.pdf`
- PRISM proposals: `Prism/docs/THESIS.md` and `Prism/docs/PRISM_V2_PROPOSAL.md`
- RViT+ design and history: `RVIT_PLUS_DESIGN.md` and `research_db/threads/rvit_plus_engineering.md`

## Reproduction

To reproduce this boundary audit, begin with the research-state briefing's canonical-artifact table, confirm project identities in `research_db/registry/projects.json`, trace empirical run claims through `research_db/registry/artifacts.jsonl` and `reports/upgraded_paper/EVIDENCE_LEDGER.md`, then trace normative claims from `Reconstruction/TRACE.md` into `Rebuild/CLAIM_LEDGER.md` and current Critique verdicts. Verify every cited local path exists and never infer a run relationship from a shared task label alone.

## Caveats

- This brief defines authority routing; it does not independently validate every scientific claim inside each artifact.
- The workspace root is not a Git repository, so commit-based provenance is generally unavailable.
- Manuscripts and ledgers can evolve; dates and current live verdicts must be checked when claims are updated.
- An empirical observation can be consistent with a normative regime without proving that the trained model implements the normative optimizer.
- No line currently supports a convergence claim for the archived 20,000-row phases. VDA16 remains partial/incomplete, and its stop reason is unknown.

## Citations

- [[attention_program]] — top-level program map.
- [[recurrent_vit]] — 2025 empirical baseline.
- [[vda_normative_repair]] — normative source and repair roles.
- [[rvit_plus]] — current empirical extension.
- [[prism_v1]] — first PRISM proposal.
- [[prism_v2]] — hierarchical PRISM proposal.
- [[vda_battery_state_and_provenance]] — run-level empirical boundary.
