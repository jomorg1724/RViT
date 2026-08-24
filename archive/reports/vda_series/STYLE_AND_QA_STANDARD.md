# VDA figure and manuscript style standard

## What the reference establishes

The MAH paper uses a direct computational-neuroscience sequence. The task is made concrete before the architecture is introduced; behavior precedes mechanism; intrinsic attention maps precede causal perturbations; the supplement then deepens the account through equations, architecture comparisons, decoding, policy logits, value signals, signal-detection theory, and supervised-versus-reinforcement-learning comparisons. Captions are substantive and often carry the full panel logic.

Its strongest visual idioms are:

- a seven-frame task timeline paired with cue configurations;
- compact architecture flow diagrams with explicit information direction;
- six-panel psychometric/chronometric grids;
- condition-by-time attention-map arrays, followed by scalar time courses;
- matched natural-versus-intervention behavioral curves;
- confusion-matrix batteries for memory and actor representations;
- two-dimensional policy-logit geometry colored by signal magnitude;
- value and temporal-difference trajectories;
- criterion and sensitivity decompositions.

The VDA series retains those scientific idioms while improving legibility. The source PDF often places dense raster figures into narrow columns, producing small labels and legends. Some curves rely too heavily on color alone, some architecture text is too small at page size, and several multi-panel figures leave little separation between labels, legends, and plotted data. These are reference-content features, not quality targets.

## Prose standard

1. Begin each environment manuscript with one literal sentence stating the task geometry, active-item count, token count, visual frontend, recurrent cell, feedback mechanism, and training objective.
2. Define displayed cue validity separately from realized target probability. Historical semantics must be stated as historical facts, not silently rewritten.
3. Describe model maturity through measured behavior. Iteration numbers may identify checkpoints but may not substitute for a convergence analysis.
4. Present representation and prediction before interpretation: first establish what is behaviorally expressed and decodable, then discuss candidate mechanisms.
5. Use connected formal prose. Avoid clipped inventories, causal language unsupported by interventions, and claims of biological identity.
6. Use “attention weight,” “memory state,” “policy logit,” “criterion,” and “sensitivity” for measured quantities. Use “FEF-like” or “SC-like” only for a specified intervention correspondence, never as an anatomical identification.
7. Distinguish correlation from intervention, fixed-checkpoint evaluation uncertainty from training replication, and a completed log from convergence.
8. Captions must be independently intelligible: identify every panel, condition, sample count, interval, fit, baseline, and evidence class.

## Figure design system

### Output

- Vector PDF is the archival figure.
- PNG is exported at 300 dpi or greater with a metadata sidecar.
- Use `constrained_layout=True` and verify the saved bounding box; never rely on `tight_layout()` as the sole overlap check.
- Generate figures only from cached NPZ/CSV analysis outputs. Plot builders must not import Torch.

### Typography

- Sans-serif body and labels, matching the reference’s clean computational-neuroscience character.
- Minimum final-size text: 9 pt for tick labels, 10 pt for axes and legends, 11 pt for panel titles, 12 pt bold for panel letters.
- A figure embedded at its manuscript width must still meet those minima; increasing source-canvas size without checking final placement does not count.
- Mathematical symbols and units are defined once and used consistently: degrees for orientation change, recurrent frame t, attention alpha_i, criterion c, sensitivity d-prime.

### Palette and redundant encoding

Use the project’s established semantic colors:

- PRIORITY / decision pathway: `#1f6fb2`.
- VALUE / valuation pathway: `#8e44ad`.
- Cued or target condition: `#009E73`.
- Uncued or distractor condition: `#D55E00`.
- No-change / neutral baseline: `#6F6F6F`.

Cue-validity levels use a perceptually ordered, color-vision-safe sequential palette sampled from viridis. Every multi-condition line also receives a unique marker and dash pattern. Red and green may not be the only distinction. Figures must be checked in grayscale and under deuteranopia/protanopia simulations.

### Axes and statistics

- Share axis ranges when panels invite direct comparison.
- Attention heatmaps share a color scale within a scientific comparison; auto-normalizing each panel independently is prohibited.
- Mark uniform-attention and decoding-chance baselines explicitly.
- Psychometric points show binomial intervals; lines show the named four-parameter logistic fit.
- Chronometric panels state the reaction-time convention and treatment of nonresponses.
- Confusion matrices show both normalized rates and support counts, with readable cell text and a shared color range.
- Clamp/intervention plots always show the natural condition and paired intervention deltas from the same sampled trials where available.
- Every panel states n, seed or seed set, checkpoint identifier, and whether intervals reflect trials, evaluation batches, or training replicates.

### Layout

- Panel letters occupy a fixed outer margin and never float over data.
- Legends are placed in reserved whitespace or outside axes, never over curves or heatmaps.
- Long condition names are moved to row/column headers rather than repeated as tiny axis titles.
- Multi-panel grids reserve at least one text-height of separation between axis labels and adjacent panels.
- Architecture diagrams use a limited vocabulary of shapes and line types, left-to-right flow, and no embedded paragraph-sized text.
- Do not mix pixel interpolation styles within a heatmap figure.

## Mandatory visual QA

For every figure:

1. Open the vector PDF directly and inspect at 100%, 200%, and fit-to-page.
2. Inspect the high-resolution PNG for rasterization artifacts.
3. Render the manuscript page containing the figure and inspect at final placement size.
4. Generate an environment contact sheet to detect cross-figure inconsistency.
5. Record pass/fail for: clipping; text overlap; legend overlap; panel-letter collision; indistinguishable colors; inadequate contrast; inconsistent axes; inconsistent heatmap scale; unreadable cell labels; missing uncertainty; missing n; missing baseline; and caption mismatch.
6. Correct every defect and rerender before marking the figure complete.

A machine-only bounding-box check is necessary but insufficient. Completion requires rendered-page visual inspection.
