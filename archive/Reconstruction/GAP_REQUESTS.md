# GAP_REQUESTS.md — rebuilder-directed punch list

Owner-facing list of places where the reconstruction's narrative wants a
scientific element that no `Rebuild/` artifact currently supplies
(mission §5.4, §9.5). The synthesizer places a visibly-marked
placeholder in the `.tex` (so the draft still compiles) and logs the gap
here. **Gap closure is owner-mediated:** the synthesizer does NOT write
into `Rebuild/`. The owner routes a gap to the rebuilder; a later
synthesizer run closes it once the artifact exists.

Row schema:

```yaml
- id: G-NNN
  opened: <ISO timestamp>
  manuscript_loc: "<section / spot>"
  needs: "<exactly what artifact closes it>"
  owner_agent: rebuilder | reviewer | owner
  status: open | closed
  closed_by: <synth run id | none>
  notes: "..."
```

---

## Open gaps

```yaml
- id: G-001
  opened: 2026-05-30T22:30:00Z
  manuscript_loc: "Model §2.3 (Attention-to-perception mapping), end of the asymmetry paragraph"
  needs: "A regenerated attention-to-$d'$ mapping figure = the original's Figure 1 (Critique/source/main.pdf p.3): $\\dprime$ at the cued location and at each uncued location as functions of $\\alphacued$, for three benefit/cost regimes $\\Rsens \\in \\{0.3, 1.0, 3.0\\}$, at $\\Nloc{=}4$, $\\dprimemax{=}2$, $f_0{=}0.5$, $\\sqrt{\\cdot}$ form. No equivalent figure exists under Rebuild/manuscript/figures/ or Rebuild/sims/*/output/ (the A1 sim emits vda_curves/cf_vs_rho only, which are Results-A1 figures, not the model-illustration mapping). The figure is pure model illustration (no claim), so it is recoverable directly from Rebuild/model/core.py:d_prime_asym."
  owner_agent: rebuilder
  status: open
  closed_by: none
  notes: "Non-blocking: the Model section compiles with a visibly-marked red placeholder in place of \\includegraphics. Opened at SY-002. A later synth run replaces the placeholder once the rebuilder stages the figure under Rebuild/manuscript/figures/ (suggested name: attention_dprime_mapping.png)."
```

## Closed gaps
_None yet._
