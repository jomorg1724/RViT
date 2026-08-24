#!/usr/bin/env python3
"""Compile the publication-style LaTeX writeup for an affine_ew comparison run."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
from typing import Any

FIGURES = (
    "attention_metrics_and_response_strata.pdf",
    "psychometric_valid_invalid_comparison.pdf",
    "attention_event_query_averaged.pdf",
    "attention_query_level_valid.pdf",
    "attention_query_level_forced_invalid.pdf",
    "attention_nochange_spatial.pdf",
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def tex_text(value: Any) -> str:
    text = str(value)
    replacements = {
        "\\": r"\textbackslash{}",
        "&": r"\&",
        "%": r"\%",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
    }
    return "".join(replacements.get(char, char) for char in text)


def signed(value: float) -> str:
    return f"{value:+.4f}"


def interval(record: dict[str, Any]) -> str:
    return f"[{record['ci_low']:+.4f}, {record['ci_high']:+.4f}]"


def copy_exact(source: Path, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)
    if sha256(source) != sha256(destination):
        raise RuntimeError(f"copy hash mismatch: {source} -> {destination}")


def render_tex(summary: dict[str, Any], frozen: dict[str, Any], run_name: str) -> str:
    primary = summary["primary_event_attention_motion"]
    secondary = summary["secondary_estimates"]
    anchor = summary["psychometric_anchor_100pct_15deg"]
    budget = summary["event_condition"]
    records = {record["role"]: record for record in frozen["checkpoints"]}
    if primary["hypothesis_verdict"] == "supported":
        answer = "The frozen high-decay checkpoint is more active under the prespecified metric."
    elif primary["hypothesis_verdict"] == "opposite":
        answer = "The frozen high-decay checkpoint is less active under the prespecified metric."
    else:
        answer = "The frozen checkpoint pair is inconclusive under the prespecified metric."
    rows = [
        ("Overall attention motion", primary),
        ("Valid attention motion", secondary["valid_attention_motion"]),
        ("Forced-invalid attention motion", secondary["forced_invalid_attention_motion"]),
        ("Selectivity", secondary["event_selectivity"]),
        ("Peak-key mass", secondary["event_peak_key_mass"]),
        ("Cued-location mass", secondary["event_cue_location_mass"]),
        ("No-change attention motion", secondary["nochange_attention_motion"]),
        ("Cue orienting (t1--t0)", secondary["cue_orienting_t1_minus_t0"]),
        ("Valid change reorientation", secondary["valid_change_reorientation_t5_minus_t4"]),
        ("Forced-invalid reorientation", secondary["forced_invalid_change_reorientation_t5_minus_t4"]),
        ("Valid qualifying response", secondary["valid_qualifying_response"]),
        ("Forced-invalid qualifying response", secondary["forced_invalid_qualifying_response"]),
    ]
    table_rows = "\n".join(
        f"{tex_text(label)} & {record['standard_mean']:.4f} & {record['high_decay_mean']:.4f} & {signed(record['mean_difference'])} [{record['ci_low']:+.4f}, {record['ci_high']:+.4f}] \\\\" for label, record in rows
    )
    run_name_tex = tex_text(run_name)
    run_name_path = run_name
    standard_hash = tex_text(records["standard"]["sha256"])
    high_hash = tex_text(records["high_decay"]["sha256"])
    return rf"""\documentclass[11pt]{{article}}
\usepackage[margin=19mm,headheight=15pt,footskip=10mm]{{geometry}}
\usepackage{{fontspec}}
\setmainfont{{Avenir Next}}
\setsansfont{{Avenir Next}}
\usepackage{{microtype}}
\usepackage{{graphicx}}
\usepackage{{booktabs,tabularx,array}}
\usepackage{{ragged2e}}
\usepackage{{pdflscape}}
\usepackage{{caption}}
\usepackage{{xcolor}}
\usepackage{{hyperref}}
\usepackage{{fancyhdr}}
\usepackage{{amsmath}}
\definecolor{{VdaBlue}}{{HTML}}{{1F6FB2}}
\definecolor{{VdaOrange}}{{HTML}}{{C44E28}}
\definecolor{{VdaGray}}{{HTML}}{{4C566A}}
\definecolor{{VdaLight}}{{HTML}}{{F1F5F8}}
\hypersetup{{colorlinks=true,linkcolor=VdaBlue,urlcolor=VdaBlue,pdftitle={{VDA4 affine\_ew memory-decay comparison}},pdfauthor={{AttentionManuscript}}}}
\graphicspath{{{{figures/}}}}
\captionsetup{{font=small,labelfont=bf,justification=justified,singlelinecheck=false,hypcap=false}}
\setlength{{\parindent}}{{0pt}}
\setlength{{\parskip}}{{0.45em}}
\emergencystretch=2em
\raggedbottom
\pagestyle{{fancy}}
\fancyhf{{}}
\fancyhead[L]{{\small VDA4 affine\_ew comparison}}
\fancyhead[R]{{\small \nouppercase{{\rightmark}}}}
\fancyfoot[C]{{\small \thepage}}
\renewcommand{{\headrulewidth}}{{0.3pt}}
\newcommand{{\boundary}}[1]{{\par\smallskip\noindent\colorbox{{VdaLight}}{{\parbox{{0.96\linewidth}}{{\textbf{{Evidence boundary.}} #1}}}}\par\smallskip}}

\begin{{document}}
\begin{{titlepage}}
\thispagestyle{{empty}}
\vspace*{{14mm}}
{{\color{{VdaBlue}}\rule{{\textwidth}}{{2.2pt}}}}\\[9mm]
{{\fontsize{{26}}{{31}}\selectfont\bfseries Memory decay and learned\\ affine spatial attention\par}}
\vspace{{4mm}}
{{\fontsize{{15}}{{20}}\selectfont A frozen-checkpoint comparison in the four-location value-directed-attention task\par}}
\vspace{{14mm}}
{{\large AttentionManuscript --- standalone affine\_ew analysis\par}}
\vfill
\begin{{tabularx}}{{\textwidth}}{{@{{}}p{{3.8cm}}X@{{}}}}
\toprule
\textbf{{Comparison}} & Standard affine\_ew ($\lambda=1.00$, iteration {int(records['standard']['checkpoint_iteration'])}) versus high-decay affine\_ew ($\lambda=0.80$, iteration {int(records['high_decay']['checkpoint_iteration'])}).\\
\textbf{{Primary question}} & Does the high-decay checkpoint show more frame-to-frame movement in its complete learned $4\times4$ spatial attention distributions?\\
\textbf{{Primary answer}} & {tex_text(answer)} High minus standard: {signed(primary['mean_difference'])}, paired trial-bootstrap 95\% interval {interval(primary)}.\\
\textbf{{Run identity}} & \texttt{{{run_name_tex}}}.\\
\bottomrule
\end{{tabularx}}
\vfill
{{\color{{VdaBlue}}\rule{{\textwidth}}{{2.2pt}}}}
\end{{titlepage}}

\begin{{abstract}}
This analysis compares two preserved VDA4 affine\_ew checkpoints on shared CPU-generated trials. Activity is fixed in advance as frame-to-frame total variation over every query-to-key row of the normalized $4\times4$ spatial attention map. The standard checkpoint averaged {primary['standard_mean']:.4f}; the high-decay checkpoint averaged {primary['high_decay_mean']:.4f}. The paired high-minus-standard difference was {signed(primary['mean_difference'])} (95\% trial-bootstrap interval {interval(primary)}; $n={primary['n']}$ matched trial-level estimates). {tex_text(answer)} The comparison is associational: training maturity is not matched and only one training seed exists per condition.
\end{{abstract}}

\section{{Question, answer, and evidential scope}}
The scientific question is narrower than whether either model ``uses attention.'' Both networks produce normalized affine spatial attention at every frame. For query $q$ and consecutive frames $t-1,t$, activity is
\[
D_{{t,q}}=\tfrac12\sum_{{k=1}}^4\left|A_{{t,q,k}}-A_{{t-1,q,k}}\right|,
\]
then averaged over frames, queries, the valid and deliberately forced-invalid event conditions, and matched trials. Total attention mass is not an activity measure because each query row sums to one.

\noindent\colorbox{{VdaLight}}{{\parbox{{0.96\linewidth}}{{\textbf{{Answer.}} {tex_text(answer)} The high-decay network's mean activity was {primary['high_decay_mean']:.4f}, compared with {primary['standard_mean']:.4f} for standard. The observed difference was {signed(primary['mean_difference'])}.}}}}

\boundary{{The standard checkpoint is iteration {int(records['standard']['checkpoint_iteration'])}; the high-decay checkpoint is iteration {int(records['high_decay']['checkpoint_iteration'])}. The frozen pair therefore confounds decay with training maturity. Confidence intervals quantify evaluation-trial sampling only, not variation across training seeds.}}

\section{{Frozen checkpoints and matched protocol}}
\begin{{center}}
\small
\captionof{{table}}{{Frozen model identities. Both checkpoints validate as VDA4, xLSTM, \texttt{{affine\_ew}}, $d_{{mem}}=128$, convolutional front end, and $2\times2$ geometry.}}
\begin{{tabularx}}{{\textwidth}}{{@{{}}p{{2.7cm}}p{{1.4cm}}p{{1.4cm}}X@{{}}}}
\toprule
Role & Iteration & Decay & Frozen SHA-256\\
\midrule
Standard & {int(records['standard']['checkpoint_iteration'])} & 1.00 & \texttt{{{standard_hash}}}\\
High decay & {int(records['high_decay']['checkpoint_iteration'])} & 0.80 & \texttt{{{high_hash}}}\\
\bottomrule
\end{{tabularx}}
\end{{center}}

Each event trial has seven logical frames: blank, cue, delay, stimulus array, maintenance, change, and response. The cue is fixed at S1. The valid condition changes S1; the forced-invalid condition changes S4. The paired videos are identical through frame 4. Event attention uses {budget['attention_trials']} trials per condition. No-change attention uses {budget['nochange_trials']} trials at 25, 50, 75, and 100\% displayed cue proportions. Psychometrics use {budget['psychometric_trials']} shared trials at each combination of four displayed cue proportions, ten change magnitudes, and two fixed change locations. A first greedy change action at frame 5 or 6 qualifies as a response.\

\section{{Results}}
At the prespecified primary metric, the high-minus-standard difference was {signed(primary['mean_difference'])} with interval {interval(primary)}. Valid-condition motion differed by {signed(secondary['valid_attention_motion']['mean_difference'])}; forced-invalid motion differed by {signed(secondary['forced_invalid_attention_motion']['mean_difference'])}. The affine analysis preserves query rows but does not split keys into image and recurrent-memory source groups: affine\_ew has one spatial key per location.

\begin{{table}}[ht]
\centering\small
\caption{{Paired high-decay minus standard estimates. Intervals are over matched evaluation trials, not training seeds.}}
\begin{{tabular}}{{lrrr}}
\toprule
Measure & Standard & High decay & Difference [95\% interval]\\
\midrule
{table_rows}
\bottomrule
\end{{tabular}}
\end{{table}}

At the matched 100\%-cue, 15$^\circ$ anchor, standard produced qualifying responses on {anchor['standard']['valid']['response_count']}/{anchor['standard']['valid']['trials']} valid trials ({anchor['standard']['valid']['response_rate']:.3f}) and {anchor['standard']['forced_invalid']['response_count']}/{anchor['standard']['forced_invalid']['trials']} forced-invalid trials ({anchor['standard']['forced_invalid']['response_rate']:.3f}). High decay produced {anchor['high_decay']['valid']['response_count']}/{anchor['high_decay']['valid']['trials']} valid ({anchor['high_decay']['valid']['response_rate']:.3f}) and {anchor['high_decay']['forced_invalid']['response_count']}/{anchor['high_decay']['forced_invalid']['trials']} forced-invalid ({anchor['high_decay']['forced_invalid']['response_rate']:.3f}). These are response probabilities, not sensitivity estimates.

\clearpage
\begin{{center}}
\includegraphics[width=0.98\textwidth,height=0.76\textheight,keepaspectratio]{{attention_metrics_and_response_strata.pdf}}
\captionof{{figure}}{{\textbf{{Affine spatial-attention descriptors.}} Time courses compare standard and high-decay checkpoints under valid and forced-invalid changes, and preserve query-level spatial routing before summary.}}
\end{{center}}

\clearpage
\begin{{center}}
\includegraphics[width=0.98\textwidth,height=0.68\textheight,keepaspectratio]{{psychometric_valid_invalid_comparison.pdf}}
\captionof{{figure}}{{\textbf{{Behavioral comparison.}} Qualifying response probability across orientation change magnitude at four displayed cue proportions. Difference heatmaps show high decay minus standard.}}
\end{{center}}

\clearpage
\begin{{center}}
\includegraphics[width=0.98\textwidth,height=0.72\textheight,keepaspectratio]{{attention_event_query_averaged.pdf}}
\captionof{{figure}}{{\textbf{{Query-averaged event maps.}} Standard and high-decay affine spatial attention under matched valid and forced-invalid videos. The query axis is averaged only for this overview; query-preserving plates follow.}}
\end{{center}}

\clearpage
\begin{{landscape}}
\thispagestyle{{plain}}
\begin{{center}}
\includegraphics[width=0.97\linewidth,height=0.73\linewidth,keepaspectratio]{{attention_query_level_valid.pdf}}
\captionof{{figure}}{{\textbf{{Valid condition, query-preserving spatial maps.}} Each tile preserves one of four query rows and four spatial keys across all seven frames. Cue and change are both at S1.}}
\end{{center}}
\end{{landscape}}

\clearpage
\begin{{landscape}}
\thispagestyle{{plain}}
\begin{{center}}
\includegraphics[width=0.97\linewidth,height=0.73\linewidth,keepaspectratio]{{attention_query_level_forced_invalid.pdf}}
\captionof{{figure}}{{\textbf{{Forced-invalid condition, query-preserving spatial maps.}} The cue remains at S1 while the change is forced to S4.}}
\end{{center}}
\end{{landscape}}

\clearpage
\begin{{landscape}}
\thispagestyle{{plain}}
\begin{{center}}
\includegraphics[width=0.97\linewidth,height=0.73\linewidth,keepaspectratio]{{attention_nochange_spatial.pdf}}
\captionof{{figure}}{{\textbf{{No-change cue-proportion sweep.}} Query-averaged spatial attention for 25, 50, 75, and 100\% displayed cue proportions without a physical change.}}
\end{{center}}
\end{{landscape}}

\section{{Reproducibility record}}
The numerical source is \texttt{{SUMMARY.json}}, derived from the validated \texttt{{comparison\_evidence.npz}} cache. The analysis run retains the executable source snapshot, task/environment/model provenance, runtime versions, exact command, frozen-input manifest, and file hashes. The figures in this writeup are byte-for-byte copies of the validated PDF figures from that run.

\begin{{itemize}}
\item Analysis run: \path{{{run_name_path}}}.
\item Standard checkpoint SHA-256: \texttt{{{standard_hash}}}.
\item High-decay checkpoint SHA-256: \texttt{{{high_hash}}}.
\item Primary metric: {tex_text(summary['hypothesis_definition'])}
\item Interpretation boundary: {tex_text(summary['interpretation_boundary'])}
\end{{itemize}}

\end{{document}}
"""


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-root", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    args = parser.parse_args()
    run_root = args.run_root.expanduser().resolve()
    output = args.output_dir.expanduser().resolve()
    if not (run_root / "SUMMARY.json").is_file() or not (run_root / "frozen_inputs.json").is_file():
        raise FileNotFoundError(f"run root is missing SUMMARY.json or frozen_inputs.json: {run_root}")
    if output.exists():
        raise FileExistsError(f"writeup output already exists: {output}")
    summary = json.loads((run_root / "SUMMARY.json").read_text(encoding="utf-8"))
    frozen = json.loads((run_root / "frozen_inputs.json").read_text(encoding="utf-8"))
    output.mkdir(parents=True)
    figure_output = output / "figures"
    for name in FIGURES:
        source = run_root / "figures" / name
        if not source.is_file():
            raise FileNotFoundError(f"required source figure is missing: {source}")
        copy_exact(source, figure_output / name)
    tex_path = output / "main.tex"
    tex_path.write_text(render_tex(summary, frozen, run_root.name), encoding="utf-8")
    for _ in range(2):
        subprocess.run(["xelatex", "-interaction=nonstopmode", "-halt-on-error", "-output-directory", str(output), str(tex_path)], cwd=output, check=True, capture_output=True, text=True)
    compiled = output / "main.pdf"
    final_pdf = output / "vda4_affine_decay_comparison.pdf"
    copy_exact(compiled, final_pdf)
    with tempfile.TemporaryDirectory(prefix="vda4-affine-writeup-verify-") as temporary_directory:
        temporary_root = Path(temporary_directory)
        info = subprocess.run(["pdfinfo", str(final_pdf)], check=True, capture_output=True, text=True).stdout
        pages_line = next(line for line in info.splitlines() if line.startswith("Pages:"))
        pages = int(pages_line.split(":", 1)[1].strip())
        if pages < 7:
            raise RuntimeError(f"compiled writeup has too few pages: {pages}")
        for page in (1, pages):
            raster_base = temporary_root / f"page_{page}"
            subprocess.run(["pdftoppm", "-f", str(page), "-l", str(page), "-singlefile", "-r", "120", "-png", str(final_pdf), str(raster_base)], check=True, capture_output=True)
            from PIL import Image
            with Image.open(raster_base.with_suffix(".png")) as image:
                if image.width < 800 or image.height < 500:
                    raise RuntimeError(f"compiled page raster unexpectedly small: {page} {image.size}")
        font_output = subprocess.run(["pdffonts", str(final_pdf)], check=True, capture_output=True, text=True).stdout
        if "TrueType" not in font_output and "Type 0" not in font_output:
            raise RuntimeError("compiled writeup does not expose embedded text fonts")
    inventory = []
    for path in sorted(output.rglob("*")):
        if path.is_file() and path.name != "writeup_manifest.json":
            inventory.append({"path": str(path.relative_to(output)), "bytes": path.stat().st_size, "sha256": sha256(path)})
    manifest = {"status": "complete", "run_root": str(run_root), "source_summary_sha256": sha256(run_root / "SUMMARY.json"), "source_manifest_sha256": sha256(run_root / "MANIFEST.json"), "figures": list(FIGURES), "compiled_pdf": str(final_pdf), "pdf_pages": pages, "artifact_inventory": inventory}
    (output / "writeup_manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": "complete", "output_dir": str(output), "pdf": str(final_pdf), "pages": pages, "manifest": str(output / "writeup_manifest.json")}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
