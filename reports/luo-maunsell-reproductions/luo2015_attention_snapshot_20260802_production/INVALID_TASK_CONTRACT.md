# INVALID FOR THE CORRECTED LUO TASK CONTRACT

This checkpoint/report lineage used the broken pre-fix initial-orientation generator.

The intended and now-enforced contract is:

- each sample orientation is independently drawn from `Uniform[0°, 180°)` on every trial;
- the signed change is drawn from `Uniform(-theta, theta)`;
- `theta` controls only the maximum absolute change and is the only orientation parameter changed by curriculum;
- unchanged first tests retain the sampled orientation; the guaranteed second test adds the sampled signed change.

This frozen checkpoint records `theta=35°`, contains `base_orientations`, and has no `orientation_sampling` contract marker. It was therefore trained under the invalid fixed-pair/curriculum-coupled implementation. Preserve it only for forensic provenance. Do not use it for Luo behavioral, attention, lesion, psychometric, d-prime, or criterion claims under the corrected task.

A new neutral parent must be trained from scratch after this fix. Warm-starting from this checkpoint would contaminate the corrected experiment with representations learned under the invalid task.
