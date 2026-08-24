# Luo 20x20, d_mem=32, mnemonic-noise SD 0.08, matched evaluation

This run doubles mnemonic-noise SD from `0.04` to `0.08` while preserving the existing Luo task and architecture. Its purpose is to prevent ceiling-level neutral performance from making the Luo--Maunsell criterion-versus-sensitivity reward manipulations behaviorally inert. The intended mechanism is that cross-attention learns to preserve task-relevant signal coherence under independent mnemonic corruption.

## Fixed model and task contract

- unchanged 50x50 Luo scene;
- 20x20 model patch/memory grid (400 tokens);
- `d_mem=32` (12,800 memory scalars per example);
- fresh independent Gaussian mnemonic noise for every scalar and recurrent update;
- mnemonic-noise SD `0.08`;
- retention `1.0` (no explicit decay);
- `crossattn1` feedback and xLSTM recurrence;
- JEPA auxiliary coefficient `0.5`;
- orientation-jitter SD `5.0` degrees;
- curriculum from 65 degrees to an 18-degree floor;
- three seeds, with 20,000 parent and 20,000 child iterations.

## Corrected competence evaluation

The parent gate is a same-environment competence measurement, not a train/test image split. It evaluates fresh balanced episodes with:

- the same task as the neutral parent;
- the same independent Uniform[0°, 180°) initial-orientation distribution;
- the same sensory-noise configuration;
- mnemonic noise enabled;
- sampled policy actions, matching training semantics;
- no gradient or replay updates;
- separate accuracy and engagement values for each location and change status.

This removes the prior accidental distribution shift caused by new base orientations, disabled mnemonic noise, and deterministic `argmax` actions.

## Scientific interpretation

Neutral competence remains required before criterion and sensitivity children branch, but ceiling performance is not the target outcome. The useful regime is one where the noisy perceptual/mnemonic process leaves sufficient headroom for location-specific value to alter sensitivity while criterion reward ratios alter response bias. The reward manipulations, behavioral `d'`/`c`, and internal location-specific modulation must be compared only after the matched neutral gate passes.
