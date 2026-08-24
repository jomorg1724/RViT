# Independent matched-width checkpoint execution audit

Date: 2026-07-12

- Upstream manifest: `/Users/jonathanmorgan/AttentionManuscript/reports/vda_series/matched_width_20260712_production_v14/MANIFEST.json`
- Upstream manifest SHA-256: `0f5ceafff75fa43742b2ea9750235abd5cdae4570f1eabd39f041b0a5c7af4dd`
- Publication-v15 manifest: `/Users/jonathanmorgan/AttentionManuscript/reports/vda_series/matched_width_20260712_production_v15/MANIFEST.json`
- Publication-v15 manifest SHA-256: `3ded3023a0cd81a344487807e11d8a06fa46b7c29cf7f5f499ef5ac659ff5e24`
- Scope: all 12 admitted checkpoint cells, production CPU loading, parameter/state identity, finite tensors, and minimal executable forward/evaluation paths.
- Reviewer edited no workspace files.

---

APPROVE WITH LIMITS

## Outcome

All 12 registry-admitted task × routing × width checkpoint cells passed independent CPU loading and execution with the production model/evaluation code.

- Exact SHA-256, path, iteration, geometry, routing, width, and parameter-count checks passed.
- All checkpoint tensors and all loaded model parameters/buffers were finite.
- Production loading reported no missing or unexpected state-dict keys.
- All 12 checkpoints had distinct paths, inodes, whole-file hashes, and canonical state-dict fingerprints. No substitution, aliasing, or duplication was found within any width pair or across the battery.
- A real task-generated seven-frame video passed through both:
  - `forward_rl_sequence(..., return_attn=True, return_cell=True)`
  - the stepwise production evaluation path `press_times_clamp(...)`
- VDA9 cross-attention d256 is retained among the 12 recomputed/inventoried cells but deliberately excluded from the five reported width contrasts because of its competence gate. It was not accidentally admitted into contrast reporting.
- The canonical upstream read-only audit also passed.

## Twelve admitted checkpoint cells

| Cell | Exact checkpoint path | SHA-256 | Trainable parameters |
|---|---|---|---:|
| vda1 / affine_ew / d128 | `/Users/jonathanmorgan/AttentionManuscript/battery_sweep_results/pod2/ckpt2/vda1_affine_ew_d128/rvit_plus_rl_latest.pt` | `1869701f8ff7d18c7caaeaabb0e9440b005af8d009a4e0eb5e7950191806d0f0` | 2,200,092 |
| vda1 / affine_ew / d256 | `/Users/jonathanmorgan/AttentionManuscript/battery_sweep_results/pod2/ckpt2/vda1_affine_ew_d256/rvit_plus_rl_latest.pt` | `bc8b2792dd3c18b02010bb2fcd74c3048f4943baa6a86c435c582efa23bc017c` | 2,805,020 |
| vda1 / crossattn1 / d128 | `/Users/jonathanmorgan/AttentionManuscript/battery_sweep_results/pod2/ckpt2/vda1_crossattn1_d128/rvit_plus_rl_latest.pt` | `7e62d83a2241ec4b0aee7a05755d9b8053689910e06f35a10d0db02ad7abc492` | 2,209,476 |
| vda1 / crossattn1 / d256 | `/Users/jonathanmorgan/AttentionManuscript/battery_sweep_results/pod2/ckpt2/vda1_crossattn1_d256/rvit_plus_rl_latest.pt` | `b6699c3ea52aa91b25546004a6352aa14b41a8d4631a4b7c72fb073a95c8b55f` | 2,842,052 |
| vda4 / affine_ew / d128 | `/Users/jonathanmorgan/AttentionManuscript/battery_sweep_results/pod2/ckpt2/vda4_affine_ew_d128/rvit_plus_rl_latest.pt` | `2341026363e6e1d2115a34a8ad9a91a73e385aab4a223aace763529e4047e085` | 2,200,092 |
| vda4 / affine_ew / d256 | `/Users/jonathanmorgan/AttentionManuscript/battery_sweep_results/pod2/ckpt2/vda4_affine_ew_d256/rvit_plus_rl_latest.pt` | `a991273cffb0ea54e0546a44d065c756333e089774627adada66aeda00a3b38d` | 2,805,020 |
| vda4 / crossattn1 / d128 | `/Users/jonathanmorgan/AttentionManuscript/battery_sweep_results/pod2/ckpt2/vda4_crossattn1_d128/rvit_plus_rl_latest.pt` | `1a2fa8ae2a57982b6c91dc75079d8293781ce843271b92fe3cfbe5fc16137155` | 2,209,476 |
| vda4 / crossattn1 / d256 | `/Users/jonathanmorgan/AttentionManuscript/battery_sweep_results/pod2/ckpt2/vda4_crossattn1_d256/rvit_plus_rl_latest.pt` | `e211fef85616e9d5e0bcc2991a9e4ca294d04c475246f44f3c693045d5b1cb17` | 2,842,052 |
| vda9 / affine_ew / d128 | `/Users/jonathanmorgan/AttentionManuscript/battery_sweep_results/pod2/ckpt2/vda9_affine_ew_d128/rvit_plus_rl_latest.pt` | `22f028f6232d9c3ea040019aff357645ddcaa69e4a09c2f8ceff224ea568d8d7` | 2,535,257 |
| vda9 / affine_ew / d256 | `/Users/jonathanmorgan/AttentionManuscript/battery_sweep_results/pod2/ckpt2/vda9_affine_ew_d256/rvit_plus_rl_latest.pt` | `cf594ad8d65deb5a227a52b2181249a94a49ea73eb1fddf3a917fd9c8b955612` | 3,470,425 |
| vda9 / crossattn1 / d128 | `/Users/jonathanmorgan/AttentionManuscript/battery_sweep_results/pod2/ckpt2/vda9_crossattn1_d128/rvit_plus_rl_latest.pt` | `6c0587201cd2bf99b43e02278d4c65b03ab79d9b1f811406fc4962d962714946` | 2,545,271 |
| vda9 / crossattn1 / d256 | `/Users/jonathanmorgan/AttentionManuscript/battery_sweep_results/pod2/ckpt2/vda9_crossattn1_d256/rvit_plus_rl_latest.pt` | `c26b2ad3202c69aedfa2ecbc4add9c81ba5b5fae73b32a41624a92f1629d751c` | 3,509,367 |

All were iteration `19999`.

## Architecture and execution checks

For every cell:

- Model class: `RViTPaperModel`
- Recurrent cell: single `xlstm`
- Front end: production convolutional frontend
- Routing:
  - `affine_ew` reconstructed as `ElementwiseAffineSelfAttention`
  - `crossattn1` reconstructed as `CrossAttentionXH`
- Geometry:
  - VDA1: `VDASetSizeEnv(set_size=1)`, 2×2 grid, 50 px, four tokens
  - VDA4: `VDAEnv`, 2×2 grid, 50 px, four tokens
  - VDA9: `VDA9Env`, 3×3 grid, 75 px, nine tokens
- Recurrent width: exactly 128 or 256 as registered.
- Readout dimensions:
  - four-token d128/d256: 512/1,024
  - nine-token d128/d256: 1,152/2,304
- Attention output geometry:
  - affine: N query × N key
  - cross-attention: N query × 2N key
- Actor, critic, value-distribution, attention, and recurrent-cell outputs were finite with expected shapes.
- Stepwise evaluation returned a valid response code in `{−1, 0, …, 6}` for every cell. A `−1` is the model’s valid “no declaration” result, not an execution failure.

## VDA9 cross-attention d256 competence exclusion

The gate is intact and correctly applied:

- Preserved evidence at metrics-inventory line 41:
  - last correct: `0.480000`
  - late-50 mean correct: `0.459350`
  - best correct: `0.582500`
  - last theta: `65.000000`
- The upstream manifest registers it as `competence_gated`.
- The production summary contains five width-pair records, not six.
- No VDA9/crossattn1 width contrast appears among those records.
- Its explicit exclusion is:  
  `d256 checkpoint is competence_gated; no width contrast is estimated`  
  (`matched_width_summary.json:809-814`).

Thus, the checkpoint is admitted for immutable recomputation/inventory and executable auditing, but its routing-family width contrast is excluded from scientific interpretation.

## Limits

- Checkpoint payloads contain only `iter` and `model_state_dict`; they do not embed task, routing, or width metadata. Routing and width are independently recoverable from architecture/state shapes, but task identity—especially VDA1 versus VDA4, which share four-token geometry—is registry/path/adjacent-metrics bound rather than self-authenticating inside the checkpoint.
- The execution probe establishes loadability and finite forward/evaluation behavior, not behavioral competence or full-battery numerical reproduction.
- The VDA9 competence determination was verified against the hash-bound metrics inventory and production exclusion logic; it was not re-estimated through a new held-out competence experiment.
- Parameter counts are not matched across widths; “matched width” here means fixed task geometry and routing while recurrent width changes.
- Single checkpoints per cell do not establish seed robustness or a causal population-level width effect.

## Integrity and modifications

- Canonical upstream read-only audit: **pass**
- Live upstream `MANIFEST.json` and production `UPSTREAM_MANIFEST.json`: byte-identical, SHA-256  
  `f80ee096ed0d51aa6339b7819f5cfbb8c5de6b94b0f87fece2819529db159a11`
- Audited sources, manifests, summaries, metrics evidence, and all 12 checkpoints remained hash-stable across execution.
- No cache directories appeared in either immutable tree.
- **Files created or modified: none.**
- Git attribution was unavailable because `/Users/jonathanmorgan/AttentionManuscript` is not a Git repository.
- One initial audit-harness assertion used the wrong expected affine class name; inspection showed the production class is `ElementwiseAffineSelfAttention`. The corrected complete audit then passed; this was not an artifact defect.