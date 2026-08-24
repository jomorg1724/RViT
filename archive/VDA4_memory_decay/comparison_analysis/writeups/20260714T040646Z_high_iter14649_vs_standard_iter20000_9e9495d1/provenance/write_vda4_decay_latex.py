#!/usr/bin/env python3
"""Create the standalone LaTeX writeup for the VDA4 decay comparison."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
from typing import Any

import numpy as np


FIGURES = (
    "attention_metrics_and_response_strata.pdf",
    "psychometric_valid_invalid_comparison.pdf",
    "attention_event_query_averaged.pdf",
    "attention_query_level_valid_image_keys.pdf",
    "attention_query_level_valid_memory_keys.pdf",
    "attention_query_level_forced_invalid_image_keys.pdf",
    "attention_query_level_forced_invalid_memory_keys.pdf",
    "attention_nochange_image_keys.pdf",
    "attention_nochange_memory_keys.pdf",
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def f4(value: float) -> str:
    return f"{value:.4f}"


def signed(value: float) -> str:
    return f"{value:+.4f}"


def interval(record: dict[str, Any]) -> str:
    return f"[{record['ci_low']:+.4f}, {record['ci_high']:+.4f}]"


def breakable_hash(value: str) -> str:
    chunks = [value[index : index + 8] for index in range(0, len(value), 8)]
    return r"{\footnotesize\texttt{" + r"\allowbreak{}".join(chunks) + "}}"


def copy_exact(source: Path, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)
    if sha256(source) != sha256(destination):
        raise RuntimeError(f"copy hash mismatch: {source} -> {destination}")


def regenerate_accessible_figures(run_root: Path, output_dir: Path, summary: dict[str, Any]) -> None:
    """Render all admitted figure views from the validated cache using extractable fonts."""
    analysis_path = Path(__file__).with_name("vda4_decay_comparison.py")
    spec = importlib.util.spec_from_file_location("vda4_decay_comparison_for_writeup", analysis_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load analysis module: {analysis_path}")
    analysis = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(analysis)

    import matplotlib

    analysis.configure_matplotlib_for_artifacts(matplotlib)
    with np.load(run_root / "data" / "comparison_evidence.npz", allow_pickle=False) as payload:
        analysis._build_event_map_figure(payload, output_dir)
        analysis._build_query_level_figures(payload, output_dir)
        analysis._build_nochange_figures(payload, output_dir)
        analysis._build_metric_figure(payload, output_dir, summary)
        analysis._build_psychometric_figure(payload, output_dir)
    missing = [name for name in FIGURES if not (output_dir / name).is_file()]
    if missing:
        raise RuntimeError(f"accessible figure regeneration is incomplete: {missing}")


def render_tex(summary: dict[str, Any], frozen: dict[str, Any], run_name: str) -> str:
    primary = summary["primary_event_attention_motion"]
    secondary = summary["secondary_estimates"]
    anchor = summary["psychometric_anchor_100pct_15deg"]
    budget = summary["event_condition"]
    records = {record["role"]: record for record in frozen["checkpoints"]}
    standard = records["standard"]
    high = records["high_decay"]

    verdict = primary["hypothesis_verdict"]
    if verdict == "supported":
        answer = "The prespecified comparison supports the hypothesis for this checkpoint pair."
    elif verdict == "opposite":
        answer = "The prespecified comparison gives the opposite result for this checkpoint pair."
    else:
        answer = "The prespecified comparison is inconclusive for this checkpoint pair."

    standard_valid = anchor["standard"]["valid"]
    standard_invalid = anchor["standard"]["forced_invalid"]
    high_valid = anchor["high_decay"]["valid"]
    high_invalid = anchor["high_decay"]["forced_invalid"]
    run_name_tex = run_name.replace("_", r"\_")
    standard_hash_tex = breakable_hash(standard["sha256"])
    high_hash_tex = breakable_hash(high["sha256"])

    return rf"""\documentclass[11pt]{{article}}
\usepackage[margin=20mm,headheight=15pt,footskip=11mm]{{geometry}}
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
\usepackage{{enumitem}}
\definecolor{{VdaBlue}}{{HTML}}{{1F6FB2}}
\definecolor{{VdaPurple}}{{HTML}}{{7A3E9D}}
\definecolor{{VdaGreen}}{{HTML}}{{00876C}}
\definecolor{{VdaOrange}}{{HTML}}{{C44E28}}
\definecolor{{VdaGray}}{{HTML}}{{4C566A}}
\definecolor{{VdaLight}}{{HTML}}{{F1F5F8}}
\hypersetup{{colorlinks=true,linkcolor=VdaBlue,urlcolor=VdaBlue,pdftitle={{Memory decay and learned cross-attention dynamics}},pdfauthor={{AttentionManuscript}}}}
\graphicspath{{{{figures/}}}}
\captionsetup{{font=small,labelfont=bf,justification=justified,singlelinecheck=false,hypcap=false}}
\setlength{{\parindent}}{{0pt}}
\setlength{{\parskip}}{{0.55em}}
\setlist{{nosep,leftmargin=1.3em}}
\emergencystretch=2em
\raggedbottom
\widowpenalty=10000
\clubpenalty=10000
\newcolumntype{{Y}}{{>{{\RaggedRight\arraybackslash}}X}}
\newcommand{{\boundary}}[1]{{\par\smallskip\noindent\colorbox{{VdaLight}}{{\parbox{{0.96\linewidth}}{{\textbf{{Evidence boundary.}} #1}}}}\par\smallskip}}
\pagestyle{{fancy}}
\fancyhf{{}}
\fancyhead[L]{{\small VDA4 decay comparison}}
\fancyhead[R]{{\small \nouppercase{{\rightmark}}}}
\fancyfoot[C]{{\small \thepage}}
\renewcommand{{\headrulewidth}}{{0.3pt}}

\begin{{document}}
\begin{{titlepage}}
\thispagestyle{{empty}}
\vspace*{{16mm}}
{{\color{{VdaBlue}}\rule{{\textwidth}}{{2.2pt}}}}\\[10mm]
{{\fontsize{{27}}{{32}}\selectfont\bfseries Memory decay and learned\\ cross-attention dynamics\par}}
\vspace{{4mm}}
{{\fontsize{{16}}{{21}}\selectfont A frozen-checkpoint comparison in the four-location value-directed-attention task\par}}
\vspace{{15mm}}
{{\large AttentionManuscript --- standalone VDA4 analysis\par}}
\vfill
\begin{{tabularx}}{{\textwidth}}{{@{{}}p{{3.4cm}}Y@{{}}}}
\toprule
\textbf{{Comparison}} & Standard cross-attention ($\lambda=1.00$, iteration 20,000) versus high-decay cross-attention ($\lambda=0.80$, iteration 14,649).\\
\textbf{{Primary question}} & Does the high-decay checkpoint show more frame-to-frame movement in its complete learned $4\times8$ attention distributions?\\
\textbf{{Primary answer}} & {answer} High minus standard: {signed(primary['mean_difference'])}, paired trial-bootstrap 95\% interval {interval(primary)}.\\
\textbf{{Run identity}} & \texttt{{{run_name_tex}}}.\\
\bottomrule
\end{{tabularx}}
\vfill
{{\color{{VdaBlue}}\rule{{\textwidth}}{{2.2pt}}}}
\end{{titlepage}}

\begin{{abstract}}
This analysis tests a precise hypothesis about recurrent visual attention: whether a stronger memory decay is associated with more dynamic learned attention maps. Two preserved VDA4 cross-attention checkpoints were evaluated on shared trial sets under valid and deliberately forced-invalid conditions. ``Activity'' was fixed in advance as frame-to-frame total variation over every query-to-key attention distribution, because total softmax mass is constant by construction. The standard checkpoint averaged {f4(primary['standard_mean'])}; the high-decay checkpoint averaged {f4(primary['high_decay_mean'])}. The paired high-minus-standard difference was {signed(primary['mean_difference'])} (95\% trial-bootstrap interval {interval(primary)}; $n={primary['n']}$ matched trial identities, each evaluated under both event conditions). Thus the high-decay checkpoint was less, not more, dynamic under the primary metric. Behavioral curves, image-versus-memory allocation, selectivity, spatial reorientation, response-stratified traces, and raw query-level maps provide convergent description. The comparison remains associational: the high-decay checkpoint was frozen 5,351 iterations earlier, and only one training seed exists per condition.
\end{{abstract}}

\section{{Question, answer, and evidential scope}}
The scientific question is narrower than whether either model ``uses attention.'' Both networks produce normalized cross-attention at every frame. The question is whether reducing the xLSTM memory-decay factor from 1.00 to 0.80 is associated with larger changes in the learned attention distribution from one frame to the next. For each query row $q$ and consecutive frames $t-1,t$, activity is
\[
D_{{t,q}}=\tfrac12\sum_{{k=1}}^8\left|A_{{t,q,k}}-A_{{t-1,q,k}}\right|,
\]
then averaged over frames, queries, valid and forced-invalid conditions, and finally over matched trials. This total-variation distance is zero for an unchanged attention row and one for a complete shift between disjoint keys.

\noindent\colorbox{{VdaLight}}{{\parbox{{0.96\linewidth}}{{\textbf{{Answer.}} {answer} The high-decay network's mean activity was {f4(primary['high_decay_mean'])}, compared with {f4(primary['standard_mean'])} for the standard network. The observed difference, {signed(primary['mean_difference'])}, is not evidence that faster forgetting caused quieter attention because checkpoint maturity was not matched.}}}}

\boundary{{The standard checkpoint completed 20,000 training iterations. The high-decay snapshot was frozen at iteration 14,649 while its training process was active; a later final checkpoint was subsequently present at iteration 19,999, but the requested frozen snapshot was retained. One training seed per checkpoint means the model-difference intervals quantify evaluation-trial sampling only, not variation across training runs.}}

\section{{Frozen checkpoints and matched protocol}}
\begin{{center}}
\small
\captionof{{table}}{{Frozen model identities. Both checkpoints validate as VDA4, xLSTM, \texttt{{crossattn1}}, $d_{{mem}}=128$, convolutional front end, and $2\times2$ geometry.}}
\begin{{tabularx}}{{\textwidth}}{{@{{}}p{{2.5cm}}p{{1.5cm}}p{{1.8cm}}Y@{{}}}}
\toprule
Role & Iteration & Decay & Frozen SHA-256\\
\midrule
Standard & 20,000 & 1.00 & {standard_hash_tex}\\
High decay & 14,649 & 0.80 & {high_hash_tex}\\
\bottomrule
\end{{tabularx}}
\end{{center}}

Each event trial has seven frames: blank, cue at frame 1, delay, stimulus array at frames 3--6, and an orientation change at frame 5. The cue is fixed at S1. In the valid condition the $15^\circ$ change occurs at S1; in the forced-invalid condition it occurs at S4. The paired videos are identical through frame 4. The 100\%-cue invalid condition is an intervention for analysis, not a sample from the environment's natural 100\%-valid target distribution.

The event analysis uses {budget['attention_trials']} paired trials per condition. No-change attention uses {budget['nochange_trials']} trials at each displayed cue proportion (25, 50, 75, and 100\%). Psychometric curves use {budget['psychometric_trials']} shared trials at each combination of four displayed cue proportions, ten change magnitudes, and the valid or forced-invalid location. A qualifying response is the first greedy change action at frame 5 or 6. Every reported model-difference interval uses 10,000 deterministic paired bootstrap resamples; psychometric binomial-rate bands use Wilson intervals.

\section{{Results}}
\subsection{{Primary activity result and secondary descriptors}}
The direction was consistent within both event conditions. High-minus-standard activity was {signed(secondary['valid_attention_motion']['mean_difference'])} for valid changes (95\% interval {interval(secondary['valid_attention_motion'])}) and {signed(secondary['forced_invalid_attention_motion']['mean_difference'])} for forced-invalid changes ({interval(secondary['forced_invalid_attention_motion'])}). The no-change difference was {signed(secondary['nochange_attention_motion']['mean_difference'])} ({interval(secondary['nochange_attention_motion'])}). These measures jointly contradict the specific prediction that the frozen high-decay checkpoint has more moving attention maps.

Secondary descriptors show that ``less motion'' is not equivalent to uniformly flatter attention. High-decay selectivity was higher by {signed(secondary['event_selectivity']['mean_difference'])}, while its peak-key mass was lower by {signed(secondary['event_peak_key_mass']['mean_difference'])} and its image-key allocation was lower by {signed(secondary['event_image_key_mass']['mean_difference'])}. Immediate change-location reorientation, measured as changed-location spatial mass at frame 5 minus frame 4, differed by only {signed(secondary['valid_change_reorientation_t5_minus_t4']['mean_difference'])} for valid changes and {signed(secondary['forced_invalid_change_reorientation_t5_minus_t4']['mean_difference'])} for forced-invalid changes; both intervals include zero.

\begin{{table}}[ht]
\centering\small
\caption{{Paired high-decay minus standard estimates. Bootstrap intervals are over matched evaluation trials, not training seeds.}}
\begin{{tabular}}{{lrrr}}
\toprule
Measure & Standard & High decay & Difference [95\% interval]\\
\midrule
Overall attention motion & {f4(primary['standard_mean'])} & {f4(primary['high_decay_mean'])} & {signed(primary['mean_difference'])} {interval(primary)}\\
Valid attention motion & {f4(secondary['valid_attention_motion']['standard_mean'])} & {f4(secondary['valid_attention_motion']['high_decay_mean'])} & {signed(secondary['valid_attention_motion']['mean_difference'])} {interval(secondary['valid_attention_motion'])}\\
Forced-invalid attention motion & {f4(secondary['forced_invalid_attention_motion']['standard_mean'])} & {f4(secondary['forced_invalid_attention_motion']['high_decay_mean'])} & {signed(secondary['forced_invalid_attention_motion']['mean_difference'])} {interval(secondary['forced_invalid_attention_motion'])}\\
Selectivity & {f4(secondary['event_selectivity']['standard_mean'])} & {f4(secondary['event_selectivity']['high_decay_mean'])} & {signed(secondary['event_selectivity']['mean_difference'])} {interval(secondary['event_selectivity'])}\\
Peak-key mass & {f4(secondary['event_peak_key_mass']['standard_mean'])} & {f4(secondary['event_peak_key_mass']['high_decay_mean'])} & {signed(secondary['event_peak_key_mass']['mean_difference'])} {interval(secondary['event_peak_key_mass'])}\\
Image-key mass & {f4(secondary['event_image_key_mass']['standard_mean'])} & {f4(secondary['event_image_key_mass']['high_decay_mean'])} & {signed(secondary['event_image_key_mass']['mean_difference'])} {interval(secondary['event_image_key_mass'])}\\
\bottomrule
\end{{tabular}}
\end{{table}}

\clearpage
\begin{{center}}
\includegraphics[width=0.98\textwidth,height=0.68\textheight,keepaspectratio]{{attention_metrics_and_response_strata.pdf}}
\captionof{{figure}}{{\textbf{{Dynamic and spatial attention descriptors.}} Time courses compare the standard and high-decay checkpoints under valid and forced-invalid changes, show image-versus-memory allocation, and separate trials with and without a qualifying change response. Every trace derives from raw $4\times8$ softmax maps before summary.}}
\label{{fig:metrics}}
\end{{center}}

\subsection{{Behavior at valid and forced-invalid locations}}
At the matched 100\%-cue, $15^\circ$ anchor, the standard checkpoint produced qualifying change responses on {standard_valid['response_count']}/{standard_valid['trials']} valid trials ({standard_valid['response_rate']:.3f}) and {standard_invalid['response_count']}/{standard_invalid['trials']} forced-invalid trials ({standard_invalid['response_rate']:.3f}). The high-decay checkpoint responded on {high_valid['response_count']}/{high_valid['trials']} valid trials ({high_valid['response_rate']:.3f}) and {high_invalid['response_count']}/{high_invalid['trials']} forced-invalid trials ({high_invalid['response_rate']:.3f}). The full curves are more informative than this single anchor: they show how response probability changes with orientation magnitude at every displayed cue proportion.

These are change-response probabilities, not sensitivity estimates. No signal-detection decomposition separates discriminability from response criterion, so a difference in response rate cannot by itself establish improved detection.

\begin{{center}}
\includegraphics[width=0.98\textwidth,height=0.58\textheight,keepaspectratio]{{psychometric_valid_invalid_comparison.pdf}}
\captionof{{figure}}{{\textbf{{Behavioral comparison.}} Qualifying change-response probability across change magnitude for valid and deliberately forced-invalid locations at four displayed cue proportions. Difference panels show high decay minus standard. The target location is fixed by analysis in every curve; displayed validity changes the cue appearance but does not sample target location.}}
\label{{fig:psychometric}}
\end{{center}}

\clearpage
\subsection{{Where the attention moves}}
Figure~\ref{{fig:average-maps}} keeps image and recurrent-memory keys separate while averaging over the four query rows. This view exposes the broad frame schedule, but it can conceal query-specific routing. Figures~\ref{{fig:valid-image}}--\ref{{fig:invalid-memory}} therefore retain every query row. Bright columns identify the source location receiving attention; image-key and memory-key panels must be interpreted separately because each is only one four-key block of the normalized eight-key distribution.

The maps show the same broad schedule in both checkpoints: image-key concentration at the cue frame is followed by increased recurrent-memory routing during the delay and array frames. Relative to standard, the high-decay checkpoint's cue-orienting increase from frame 0 to frame 1 was larger by {signed(secondary['cue_orienting_t1_minus_t0']['mean_difference'])}, yet its event-average image-key mass was lower by {signed(secondary['event_image_key_mass']['mean_difference'])}; because image and memory blocks partition each normalized row, the latter is a corresponding shift toward memory keys. At the frame-5 change, high-minus-standard changed-location reorientation was only {signed(secondary['valid_change_reorientation_t5_minus_t4']['mean_difference'])} in valid trials and {signed(secondary['forced_invalid_change_reorientation_t5_minus_t4']['mean_difference'])} in forced-invalid trials, with both intervals spanning zero. The lower total variation therefore reflects a quieter routing trajectory after the strong cue transition, not an absence of cue-localized or source-selective structure.

\begin{{center}}
\includegraphics[width=0.98\textwidth,height=0.68\textheight,keepaspectratio]{{attention_event_query_averaged.pdf}}
\captionof{{figure}}{{\textbf{{Query-averaged event maps.}} Standard and high-decay attention under matched valid and forced-invalid videos. Image keys and recurrent-memory keys are displayed separately across all seven frames. This is the overview; the following plates preserve the full query axis.}}
\label{{fig:average-maps}}
\end{{center}}

\clearpage
\begin{{landscape}}
\thispagestyle{{plain}}
\begin{{center}}
\includegraphics[width=0.96\linewidth,height=0.62\linewidth,keepaspectratio]{{attention_query_level_valid_image_keys.pdf}}
\captionof{{figure}}{{\textbf{{Valid condition, image keys.}} Each tile preserves the four query rows and four image-key columns. The cue and $15^\circ$ change are both at S1; paired models receive identical videos.}}
\label{{fig:valid-image}}
\end{{center}}
\end{{landscape}}

\begin{{landscape}}
\thispagestyle{{plain}}
\begin{{center}}
\includegraphics[width=0.96\linewidth,height=0.62\linewidth,keepaspectratio]{{attention_query_level_valid_memory_keys.pdf}}
\captionof{{figure}}{{\textbf{{Valid condition, recurrent-memory keys.}} Full query-to-memory routing for the same valid trials. Comparison with Figure~\ref{{fig:valid-image}} shows whether a frame-to-frame shift is within a source block or between image and memory.}}
\label{{fig:valid-memory}}
\end{{center}}
\end{{landscape}}

\begin{{landscape}}
\thispagestyle{{plain}}
\begin{{center}}
\includegraphics[width=0.96\linewidth,height=0.62\linewidth,keepaspectratio]{{attention_query_level_forced_invalid_image_keys.pdf}}
\captionof{{figure}}{{\textbf{{Forced-invalid condition, image keys.}} The cue remains at S1 while the change is forced to S4. Videos are matched through frame 4, so valid--invalid divergence before the event would indicate analysis or stochastic mismatch.}}
\label{{fig:invalid-image}}
\end{{center}}
\end{{landscape}}

\begin{{landscape}}
\thispagestyle{{plain}}
\begin{{center}}
\includegraphics[width=0.96\linewidth,height=0.62\linewidth,keepaspectratio]{{attention_query_level_forced_invalid_memory_keys.pdf}}
\captionof{{figure}}{{\textbf{{Forced-invalid condition, recurrent-memory keys.}} Query-preserving memory routing after a change outside the cued location. This plate is the direct spatial test requested for invalid attention.}}
\label{{fig:invalid-memory}}
\end{{center}}
\end{{landscape}}

\section{{Interpretation}}
The frozen high-decay checkpoint does not show the predicted increase in attention-map activity. Its attention changes less from frame to frame in valid, forced-invalid, and no-change analyses. At the same time, some secondary descriptors move in different directions: selectivity is slightly higher while peak-key and image-key mass are lower. This pattern is why the conclusion is tied to the prespecified total-variation metric rather than generalized into ``more'' or ``less attention.'' Attention is a normalized distribution; its scientific content is where mass moves, between which sources, and when.

The result does not identify a causal memory-decay effect. Training maturity is confounded with decay, the two checkpoints were trained independently, and each represents only one training seed. A controlled answer requires matched training budgets, multiple seeds, checkpoint-acceptance criteria, and evaluation of both final checkpoints under this same paired-video battery. The present result is nevertheless decisive for the literal frozen-pair question: the available high-decay snapshot is not more dynamically attentive by the prespecified metric.

\section{{Reproducibility record}}
The numerical source is \texttt{{SUMMARY.json}}, derived from the validated \texttt{{comparison\_evidence.npz}} cache. Every figure was regenerated from that admitted cache in PDF, SVG, and PNG, using TrueType PDF embedding and text-preserving SVG settings. The analysis source, task/environment source, model source, runtime versions, exact command, frozen-input manifest, and file hashes are retained in the analysis run. This writeup copies its numerical and lineage inputs byte-for-byte; a package manifest records those copies, the regenerated figures, and the compiled manuscript.

\begin{{itemize}}
\item Analysis run: \path{{{run_name}}}.
\item Standard checkpoint SHA-256: {standard_hash_tex}.
\item High-decay checkpoint SHA-256: {high_hash_tex}.
\item Primary metric: {summary['hypothesis_definition']}
\item Interpretation boundary: {summary['interpretation_boundary']}
\end{{itemize}}

\end{{document}}
"""


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-root", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    args = parser.parse_args()

    run_root = args.run_root.resolve()
    output = args.output_dir.resolve()
    if not (run_root / "MANIFEST.json").is_file():
        raise RuntimeError(f"analysis run is not finalized: {run_root}")
    if output.exists():
        raise FileExistsError(f"writeup directory already exists: {output}")

    summary = json.loads((run_root / "SUMMARY.json").read_text())
    frozen = json.loads((run_root / "frozen_inputs.json").read_text())
    (output / "figures").mkdir(parents=True)
    (output / "provenance").mkdir(parents=True)
    (output / "build").mkdir(parents=True)

    regenerate_accessible_figures(run_root, output / "figures", summary)
    for name in ("SUMMARY.json", "REPORT.md", "frozen_inputs.json", "MANIFEST.json"):
        copy_exact(run_root / name, output / "provenance" / name)
    copy_exact(
        run_root / "data" / "comparison_evidence.npz",
        output / "provenance" / "comparison_evidence.npz",
    )
    copy_exact(Path(__file__).resolve(), output / "provenance" / "write_vda4_decay_latex.py")
    copy_exact(
        Path(__file__).with_name("vda4_decay_comparison.py").resolve(),
        output / "provenance" / "vda4_decay_comparison.py",
    )
    for relative in (
        Path("tables/paired_attention_and_response_estimates.csv"),
        Path("tables/psychometric_response_rates.csv"),
        Path("tables/event_attention_timecourses.csv"),
    ):
        copy_exact(run_root / relative, output / "provenance" / relative.name)

    tex = render_tex(summary, frozen, run_root.name)
    tex_path = output / "main.tex"
    tex_path.write_text(tex)
    print(json.dumps({"output_dir": str(output), "tex": str(tex_path)}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
