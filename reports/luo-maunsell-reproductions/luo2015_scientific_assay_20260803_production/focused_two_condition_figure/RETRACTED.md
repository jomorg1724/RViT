# RETRACTED: task-contract error

Do not use the response-rate figure or its previous “absolute-orientation novelty” interpretation as evidence about the intended Luo delayed change-detection task.

The intended curriculum semantics are:

- on each trial, signed orientation change is sampled as `change ~ Uniform(-theta, theta)`;
- `theta` is the current maximum absolute change, not a fixed change magnitude;
- after a successful curriculum window, `theta` is reduced by 3 degrees (down to its floor).

The implementation in `envs/luo2015.py` also uses the same mutable `theta` to construct the two sample orientations:

```python
self.samp[i] = self.base_orientations[i] + (theta if hi[i] else 0.0)
self.orientation_change = np.random.uniform(-theta, theta)
```

Therefore curriculum updates simultaneously change both:

1. the support of the orientation-change distribution; and
2. one of the possible sample orientations at every location.

This coupling invalidates the previous interpretation of the fixed-magnitude sweep. At the checkpoint value `theta=35°`, forcing a `35°` change can map one sample value exactly onto the other only because sample-pair separation was also set to `theta`. That is an implementation artifact, not the intended meaning of uniformly sampled changes.

The previous claim that the checkpoint had learned an “absolute-orientation novelty shortcut” is retracted. The observed transition asymmetry is real for this flawed implemented contract, but it cannot establish that mechanism or characterize the intended task.

Before further behavioral or causal interpretation, sample-orientation generation must be decoupled from the curriculum change bound, the intended fixed sample-orientation contract must be specified, and the neutral model must be retrained/evaluated under that corrected contract.
