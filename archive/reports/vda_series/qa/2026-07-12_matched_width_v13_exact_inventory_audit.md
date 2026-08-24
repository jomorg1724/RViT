# Matched-width summary v13 audit record

Date: 12 July 2026
Production root: `reports/vda_series/matched_width_20260712_production_v13/`
Upstream root: `RViT_plus_paper_jepa_grid9/vda_sweep/derived/2026-07-11_matched_width/`
Verdict for exact inventory and reconstruction: **PASS**

## Executed checks

1. The fresh-root build reran the immutable upstream battery audit, reconstructed all summary values and sample counts, rendered PDF/SVG/PNG, wrote strict JSON, and published `MANIFEST.json` only after filesystem quiescence.
2. The builder's immediate completed-tree audit returned exit code 0.
3. After a 15-second delay, a separate read-only invocation of `build_matched_width_summary.py --audit` returned exit code 0 against the completed v13 tree.
4. Focused summary tests passed: `9 passed in 0.52s`.
5. The integrated scientific/figure gate passed: `157 passed in 6.33s`.
6. Publication PDF/SVG/PNG/JSON and manifest copies were compared byte-for-byte with the v13 production tree before placement.
7. A delayed publication-tree audit found Finder's `Icon\r` sidecar. `lstat()` established that both the publication file and v13's manifested figure-directory counterpart were contained, zero-byte, regular, single-link files with identical bytes. The publication snapshot therefore has an explicit six-file inventory: five semantic files plus this manifested housekeeping sidecar.
8. The v13 PNG was visually inspected; its evidence footer, decoder labels, clamp estimand labels, legend, acceptance-gate annotation, and all four panels were legible with no clipping or collision.

## Publication hashes

- PDF: `b3249907602cc0623b53baff273fccce9df346281232f7da3fef706733b9392f`
- SVG: `7e56532084ba0cdf3a9b4bbd8b4afdbed0392e5675a5268cc63b1892cf918998`
- PNG: `4b26d6cc2f0d987c6cbe8058fdb49910a5225c82e25e89d5bcd12866e3426d26`
- JSON: `a923c7af6eadc9d44fc32ba42ef920ee50e446b8fc0d15f4820650b5aaa195e5`
- Production manifest snapshot: `8188a76ceff21d7ab09908d689864e903798edb910ce274103a375bbe83804b9`
- Manifested zero-byte `Icon\r` sidecar: `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`

## Scope boundary

This PASS authenticates tree identity, sample-count reconstruction, strict metadata, copied-byte identity, and delayed read-only stability. It does not erase scientific limits from separate training, one checkpoint per cell, absent seed replication, unavailable paired intervals, warning-excluded native decoder trajectories, acceptance-gated cells, or routing-specific intervention targets. Those limits are reviewed independently.
