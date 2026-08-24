---
type: conversation
agent: constructive-rebuilder
prompt_version: 0.2
run_id: rb-049-2026-05-30
started: 2026-05-30T15:00:00Z
ended: 2026-05-30T15:30:00Z
worked_on: RB-049
output_kind: manuscript
claims_touched: [cross-cutting]
artifacts_written:
  - Rebuild/manuscript/sections/intro.tex
  - Rebuild/manuscript/main.pdf
  - Rebuild/REBUILD_BACKLOG.md
  - Rebuild/CLAIM_LEDGER.md
  - Rebuild/rebuilder_state.json
  - Rebuild/BUILD_LOG.md
  - Rebuild/conversations/2026-05-30-rebuilder-intro-bookend.md
papers_added: []
spawned_tasks: []
---

# rb-049 — §intro bookend manuscript

## What I built

Replaced the rb-005 stub in
[Rebuild/manuscript/sections/intro.tex](../manuscript/sections/intro.tex)
(34 lines, ~60% placeholder + 13-line scoping paragraph) with a
6-paragraph self-contained introduction at the §3.3 unifying-reframe
voice (~165 LaTeX lines, ~1,100 words). The intro restates the
original VDA question verbatim in spirit, articulates the corrective
voice up-front, introduces the missing third lever (decorrelation),
previews the four C-row headline results at CLAIM_LEDGER-licensed
strength, previews the three extension levers and the A6 deferral,
and outlines the manuscript layout.

The intro is the third drafted bookend after rb-047's §abstract and
rb-048's §limitations. The rebuilt paper now has all three drafted
bookends (abstract → intro → limitations) for the first time; only
the §methods bookend remains as a structural increment.

## How it connects to the ledger

No claim's rebuilt strength changes in this increment. The intro is a
downstream consumer of every wired body section — it previews the
licensed strengths of every C-row claim (C1 distributional,
C2 closed-form, C3 graded, C4 conditional + anti-cue prediction,
C5 universal real-number identity) and every A-row extension
(A1 ρ channel, A2 bounded heterogeneity, A3 power-mean conservation
family, A8 N-dim policy with new conditional binding, A6 deferred).

The §3.3 unifying-reframe voice is now articulated in three places in
the manuscript: the abstract (paragraph 1's "every headline result at
its defensible distributional, graded, or conditional strength rather
than as a categorical floor"), the intro (paragraph 2's quoted
overstatement → corrective voice pivot), and the §limitations §7.6
"what the rebuild does not claim" paragraph. The corrective voice is
the manuscript's narrative spine rather than an implicit pattern
across body sections.

The 10 live verdict labels were re-checked at the start of the run
and match the §3 table of `agents/paper_rebuilder_prompt.md` v0.2
exactly: C1 CONTESTED, C2 CONFIRMED-UNDER-ATTACK, C3 CONTESTED,
C4 CONFIRMED-CONDITIONAL, C5 CONFIRMED-UNDER-ATTACK; A1 CONTESTED,
A2 CONFIRMED-CONDITIONAL, A3 CONTESTED, A6 WEAKLY-SUPPORTED (the §3
A6 entry is still stale at "OPEN", flagged in CLAIM_LEDGER but not
load-bearing for this run), A8 CONFIRMED-CONDITIONAL.

## Simulation evidence

No new simulation. This is a manuscript bookend increment; the
evidence backing the intro's quantitative claims is the body of
already-cited sims:

- C1 distributional: rb-003 sim sha256
  `91fc4692dbc106eca9c90770c79e22f7f4757d76421ed55e7e8e91f80e44706c`
- C2 closed-form r†(v): rb-004 sim sha256
  `09ecef3c2c5a101820951398ed7d6e67d3398aede80c5f0bddfa42b6224fd783`,
  rb-023 ρ-extension verify sha256
  `ddbd3988e0253fde2cfae5906ca2749cda872d1382055b3d243b4b7c6a0678dc`
- C3 graded contour band: rb-010 sim sha256
  `72820559e1c1ab1919f74308623eaf4230aa3ea92ad3d9c62d81e993e4f27de6`
- C4 conditional theorem + anti-cue: rb-012 sim sha256
  `6ad651d648ae597cdfb28c6fd19b6261e4f9d5cb96b599557e10aad47ffd6d96`
- C5 universal real-number identity: rb-001 recovery test sha256
  `d3c62215cedbe2f797c484a8d76e8bef1d5ac42cdb3092ff099a34aea1b6f18f`
- A1 cell-wise sign-flip: rb-025 sim sha256
  `489c7c2581d1e940cfc67427e0793959bb33b24afda075ee648743aa2ac659ea`
- A2 bounded heterogeneity: rb-021 sim sha256
  `22b183f942d6b1f8868848ec1143ab959afd78c72cd6d3704763eedf5713e615`
- A3 conservation family: rb-016 sim sha256
  `055bf4ec862c711f2c6a3fa0831e1373b806a84c5f5c1a6b13fd1d9d7a039a33`
- A8 N-dim policy: rb-027 sim sha256
  `beb2aa879402e5c9f4c354a2c9f53a98c466d0989085dc8c78370be99dee290b`

Recovery-test digests for the model substrate (all unchanged after
this manuscript-only increment): rb-001
`d3c62215cedbe2f797c484a8d76e8bef1d5ac42cdb3092ff099a34aea1b6f18f`;
rb-015 (conservation family)
`f4f57a89e5108db47447cbeaf2f15440f56cdfffb65f3d173dc4a0550121791e`;
rb-019 (heterogeneous r)
`0486921f8a4e253a1682ee0731e52c7de800bf6c3dbb1b5e8ff3200602454c7e`;
rb-020 (general policy)
`883ea15af9fd069e04c05ff156d65f33a7d25278891092539c6441d2248c3d39`.

PDF: 59 pages / 2,815,939 bytes (was 58 / 2,807,597 at rb-048 →
+1 page, +8,342 bytes). 4-pass pdflatex+bibtex clean after one
mid-build `\citep` → `\cite` correction on pass 1.

## What the manuscript can now say

The rebuilt paper now has all three drafted bookends (abstract → intro
→ limitations) for the first time. The §3.3 unifying-reframe voice is
the manuscript's narrative spine, stated explicitly up-front (intro
¶2) and again at the end (§limitations §7.6). The corrective stance
— distributional, graded, or conditional by default — is no longer an
implicit pattern across body sections but the paper's stated method.

Every quantitative claim the intro previews is at exactly the
licensed strength of its body section: $\CF \in [0.30, 1.00]$ with
median $0.76$; the closed-form $\rdagger(\val) = K_u/[(\Nloc-1)K_c]$
with ρ extension and conservation invariance; the hierarchical $\valid$
thresholds for the iso-$\VDA$ contour band; the conditional theorem
$\valid \ge 1/[(\Nloc-1)\val+1]$ with anti-cue inversion at $36.1\%$
incidence; the universal real-number $\Rsens=1$ identity. The intro
never states anything more strongly than its CLAIM_LEDGER row.

## Next increment

**§methods bookend** (replace the rb-005 stub in
`sections/methods.tex`, 33 lines, ~70% placeholder) is the only
remaining structural increment. The §methods can be a catalogue of
the rebuild's simulation infrastructure: `Rebuild/model/` with the
four recovery-test digests
(`d3c62215…` / `f4f57a89…` / `0486921f…` / `883ea15a…`),
`Rebuild/sims/` with the nine sim-output digests,
`Rebuild/derivations/` with the four derivations, the deterministic
reproducibility convention (seeds, hashes, byte-identical reruns),
and the `Rebuild/manuscript/BUILD.md` toolchain (TeX Live 2026basic,
pdflatex+bibtex, no latexmk/multirow). After §methods, the manuscript
is structurally complete and the remaining work is sharpening passes
only.

Alternatives: any of the 14 queued low-priority sharpening tasks
(RB-023, RB-024, RB-027, RB-028, RB-029, RB-031, RB-032, RB-036,
RB-037, RB-039, RB-040, RB-043, RB-044, RB-045 — all already named in
§limitations §7.5).

## Wiki cross-references

Sweep performed; keywords: {value-directed attention, criterion
fraction, decorrelation lever, three-lever decomposition, anti-cue
inversion, conservation family, equicorrelated Gaussian, escape
threshold, narrow regime, central tendency, distributional vs
categorical claim, symmetric recovery, missing-lever framing}.

Every paper the intro cites was already wired through body sections:

- `CohenMaunsell2009` — already wired from rb-009 (§results-C1
  reproducibility paragraph), rb-011 (§results-C3 A1 sign-flip
  cross-axis paragraph), rb-013/RB-012 (§results-C4 behavioural
  anchor), and the §model §sec:model-rho-channel empirical envelope
  ($r_{SC} \approx 0.2$).
- `RuffCohen2016` — already wired from rb-009 (§model
  §sec:model-rho-channel scoped-limitation citation for
  structured-covariance violations of the one-factor reduction).
- `Srinath2021` — already wired from rb-009 (§model
  §sec:model-rho-channel scoped-limitation citation, alongside
  RuffCohen2016).

No new `research_db/papers/` stubs added. `audit.py` not re-run (no
wiki writes).
