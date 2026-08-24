# Build instructions — VDA-rebuild manuscript

The manuscript is plain LaTeX (`article` class) under
`Rebuild/manuscript/`. Each rebuild increment touches one
`sections/*.tex` file plus, when relevant, copies one figure from a
sibling `Rebuild/sims/*/output/figures/` directory into
`Rebuild/manuscript/figures/`.

## Toolchain (verified rb-005)

- `pdflatex` — TeX Live 2026 (`/Library/TeX/texbin/pdflatex`,
  pdfTeX 3.141592653-2.6-1.40.29). Confirmed present in the sandbox.
- `bibtex`   — bundled with TeX Live 2026.
- `latexmk`  — **not** in the sandbox at rb-005; manual two-pass build
  below is used instead. If `latexmk` becomes available later, prefer
  `latexmk -pdf main.tex` as the single command.

## Build (manual two-pass; rb-005 default)

From `Rebuild/manuscript/`:

```sh
pdflatex -interaction=nonstopmode -halt-on-error main.tex
bibtex   main
pdflatex -interaction=nonstopmode -halt-on-error main.tex
pdflatex -interaction=nonstopmode -halt-on-error main.tex
```

The first `pdflatex` populates `main.aux`; `bibtex` resolves
citations; the next two passes resolve cross-refs (`\Cref{...}`) and
the bibliography back-references. The final `main.pdf` lands beside
`main.tex`.

If `bibtex` reports "I found no \citation commands" while every
section is still a stub, that is expected; the warning resolves once
a section actually cites an entry from `refs.bib`.

## Clean

```sh
rm -f main.aux main.bbl main.blg main.log main.out main.toc main.pdf
```

`main.pdf` is a build artifact and is regeneratable from source; do
not check it in.

## Per-section workflow (for subsequent rebuild increments)

1. Open the target section file under `sections/`.
2. Replace the bracketed stub block with the real prose; cite every
   number to its backing artifact in `BUILD_LOG.md` / `CLAIM_LEDGER.md`.
3. If the section needs a figure, copy it from the sim's output:
   ```sh
   cp ../sims/<sim-dir>/output/figures/<fig>.png figures/<fig>.png
   ```
   and `\includegraphics[width=\linewidth]{figures/<fig>.png}` in the
   section. Caption with the claim it supports and the parameters it
   was run at (mission §5.4).
4. Compile via the four-command block above. Confirm exit 0 on every
   pass; record any unresolved `\ref`/`\cite` warnings.
5. Update the section's incremental status in the build-log entry for
   that run.

## Notes

- Theorem environments (`theorem`, `proposition`, `lemma`, `corollary`,
  `assumption`, `remark`) and macros for the project notation
  (`\Phinorm`, `\dprime`, `\VDA`, `\CF`, `\corr`, `\rdagger`,
  `\rstarinv`, …) are pre-declared in `main.tex`. Use them rather than
  introducing parallel notation.
- `siunitx` is **not** in the sandbox's TeX Live 2026basic install;
  rb-005 dropped it from `main.tex`. If a later increment wants
  `\num{...}`, either install it via `tlmgr install siunitx` or use
  the existing math-mode formatting directly.
- The skeleton is intentionally thin: every section file is a stub
  pending its own manuscript increment in `REBUILD_BACKLOG.md`.
