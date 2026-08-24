# First-wave VDA4/VDA9 production QA — 2026-07-11

## Verdict

**APPROVED.**

The production computation, strict semantic/provenance audit, canonical read-only audit, format validation, and complete visual inspection all passed. Independent production-artifact and pixel-level PNG/PDF reviewers subsequently returned `APPROVE` for this exact root and source revision.

## Authoritative build

- Root: `/Users/jonathanmorgan/AttentionManuscriptArtifacts/vda_first_wave_production_20260712_approved`
- Completion: 2026-07-11 PDT; builder exited 0 after 2,635 seconds.
- Manifest: `MANIFEST.json`
- Manifest SHA-256: `b627814dc19ba8dc11be8c2ac50c64b8b5f8fe9fb2fab9676d49dae3f2950677`
- Framed tree SHA-256: `3109d183238d3f92b30317e42f559f0c01990b3a9801014e6882a5e9600eac1b`
- Inventory: exactly 65 regular files; no missing, unmanifested, symlink, or special entries.
- Composition: 48 manifested artifacts, 16 frozen source/dependency snapshots, and one manifest.
- Producer SHA-256: `0bb4ee909f6b14abaace8aa97bf88749050b4cd073e1ed829f73a4cfa6c47f33`
- Builder SHA-256: `f10a1d3b910ec0cd969cb20bb435816df94a4300d8aff51a5c57da51d0cdb42b`
- Core SHA-256: `7f41d3674841421573fce1e7f00cbbac94a5ff8673351c1397c8e3a227b80773`
- Frozen producer dependencies: 14.

The earlier repository-resident root `reports/vda_series/first_wave_20260711_production` is rejected because unmanifested macOS `Icon\r` files contaminated its inventory. It is not an approved evidence source.

## Scientific scope

- Tasks: historical VDA4 and historical VDA9.
- Geometry: VDA4 is fully occupied 2×2; VDA9 is fully occupied 3×3.
- Feedback families: `affine_ew` and `crossattn1`.
- Focused condition: red cue at S1; valid change at S1.
- Invalid comparison: VDA4 S4; VDA9 S9, the true bottom-right location.
- Attention: 96 trials per task/feedback family; all query rows retained; seven logical timestep columns.
- Psychometrics: 300 trials per point; displayed cue proportions 25%, 50%, 75%, and 100%; orientation changes 0°, 3°, 6°, 9°, 12°, 15°, 18°, 22°, 26°, and 30°.
- Ordinate: probability of a qualifying change response, with all trials retained in the denominator.
- Uncertainty: Wilson 95% finite evaluation-trial intervals for one checkpoint, not training-seed uncertainty.
- Third panel: forced valid-versus-invalid location intervention at 100% displayed validity.

## Audit evidence

The independent audit `/tmp/audit_vda_first_wave_production.py` exited 0 and reported `PASS`. It checked:

- schema and complete inventory;
- all 48 artifact hashes and all frozen snapshot hashes;
- eight cache-record identities and cache/sidecar binding;
- selected checkpoint path, iteration, and SHA-256 stability;
- exact requested and realized trial counts;
- producer, builder, dependency, runtime, seed, and device closure;
- attention shapes, finite values, nonnegativity, and unit mass before spatial reduction;
- feedback-aware affine and image-plus-memory cross-attention reduction;
- psychometric counts, rates, denominators, point seeds, and Wilson semantics;
- canonical `--reuse-validated-cache` execution and byte-preserving tree identity.

Cache SHA-256 identities:

| Task | Feedback | Stage | SHA-256 |
|---|---|---|---|
| VDA4 | affine | attention | `326766c58dc878ce362aaf4102a7a4ceaed9393589b205fe3192a332533d2667` |
| VDA4 | affine | psychometric | `ef966abd2d643d83ed998ba03847f203b8c9579d70c477212951b701e355525f` |
| VDA4 | cross-attention | attention | `fed7ff25f0b95e121ef439368264c2a6834496d597c2d0793f8603400058cf28` |
| VDA4 | cross-attention | psychometric | `429a095946990ab73737122b70d2a96f3fbcde91ba742e89c11adf491c5bac66` |
| VDA9 | affine | attention | `b72b937d076ae0fd35d25370663e955c2acc2569b0c348b90d28ba19b943cb65` |
| VDA9 | affine | psychometric | `39ecd75e7ac25a54305b798aac9519d6eb46161bc323bf3855a4d7a0e1ccfb9b` |
| VDA9 | cross-attention | attention | `eef2432691167ea4be211f3f34c4d6d262c2f4b2091a68829f9eab57ba728fbd` |
| VDA9 | cross-attention | psychometric | `b64af40a14b85cfa00d6ae8c19f6205e03c0579574bf87947106374a796cfa04` |

## Format validation

- Ten one-page PDFs parsed with `pdfinfo`.
- Ten SVGs parsed as XML.
- Ten PNGs passed Pillow verification.
- Errors: zero.
- Every PDF was rasterized independently at 200 dpi for vector-export inspection.

## Figure-by-figure visual QA

| Figure | PNG | 200-dpi PDF | Verdict and observations |
|---|---:|---:|---|
| VDA4 environment | PASS | PASS | Complete 2×2 geometry; cue at S1; valid change at S1; invalid change at S4; labels and explanatory overlays clear. |
| VDA9 environment | PASS | PASS | Complete 3×3 geometry; cue at S1; valid change at S1; invalid change at S9; all nine occupied locations visible. |
| VDA4 affine attention | PASS | PASS | Complete 4×7 grid; four query labels and seven timestep headers; shared [0,1] colorbar; cue/change borders and affine reduction footer intact. |
| VDA4 cross-attention | PASS | PASS | Complete 4×7 grid; image/memory keys explicitly paired and summed by location; shared scale and all annotations intact. |
| VDA9 affine attention | PASS | PASS | Complete 9×7 grid; nine query labels and seven timestep headers; shared [0,1] scale; uniform baseline 0.111 disclosed. |
| VDA9 cross-attention | PASS | PASS | Complete 9×7 grid; cross-attention reduction disclosed; no missing cells, clipping, or colorbar defects. |
| VDA4 affine psychometric | PASS | PASS | Three panels, n=300 label, Wilson bands, legends, axes, denominator disclosure, and forced-location comparison all readable. |
| VDA4 cross-attention psychometric | PASS | PASS | Three panels and all uncertainty/forced-intervention disclosures intact; no collisions or clipping. |
| VDA9 affine psychometric | PASS | PASS | Three panels and all cue-proportion series distinguishable; forced invalid curve separated as expected from observed checkpoint output. |
| VDA9 cross-attention psychometric | PASS | PASS | Three panels and all disclosures intact. The lower invalid-location response at large changes is consistent across natural-invalid and forced-invalid panels; retained as checkpoint behavior, not treated as a rendering defect. |

Across all figures there were no blank panels, missing elements, font substitutions, legend collisions, clipped labels, raster artifacts, or PDF-specific export defects. Attention interpretation remains descriptive; this QA does not convert it into a causal claim.

## Runtime

- Python 3.12.13
- NumPy 2.4.6
- Matplotlib 3.10.9
- PyTorch 2.12.0
- SciPy 1.17.1
- Gymnasium 1.3.0
- Pillow 12.2.0
- Platform: macOS 26.3.1 arm64

## Independent approval

- Exact source and low-trial verification smoke: independently approved before production.
- Production artifact/provenance: independently approved after the full audit passed, all five corroborating hashes matched, and the exact 65-file inventory had no symlink, special-file, or hard-link aliases.
- Production visual presentation: independently approved from direct pixel inspection of every native PNG and every 200-dpi PDF rasterization.
- Approval scope: this exact 96/300 production root and the hashes recorded above. It does not establish training-seed replication, a controlled set-size effect, an affine-versus-cross-attention causal contrast, or a biological mechanism.
