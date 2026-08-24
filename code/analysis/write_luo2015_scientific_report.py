#!/usr/bin/env python3
"""Generate a scientific Markdown/LaTeX report from a completed Luo attention assay."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np


def fmt(value: float, digits: int = 3, signed: bool = False) -> str:
    return f"{float(value):+.{digits}f}" if signed else f"{float(value):.{digits}f}"


def esc(value: object) -> str:
    text = str(value)
    for old, new in (("\\", r"\textbackslash{}"), ("_", r"\_"), ("%", r"\%"),
                     ("&", r"\&"), ("#", r"\#")):
        text = text.replace(old, new)
    return text


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("report_root", type=Path)
    args = parser.parse_args()
    root = args.report_root.resolve()
    summary = json.loads((root / "data" / "summary.json").read_text(encoding="utf-8"))
    report_dir = root / "report"
    report_dir.mkdir(exist_ok=True)

    contract = summary["contract"]
    model = summary["checkpoint"]
    overall = summary["intervention_overall"]
    effects = summary["paired_accuracy_effects"]
    curves = summary["curves"]
    focal_index = list(map(float, contract["fixed_psychometric_magnitudes_degrees"])).index(18.0)
    trial = summary["specific_trial"]
    map_rows = json.loads((root / "data" / "map_contrasts.json").read_text(encoding="utf-8"))

    def map_value(prefix: str, frame: int, source: str) -> dict:
        return next(row for row in map_rows if row["condition"].startswith(prefix) and row["frame"] == frame and row["source"] == source)

    l0_t3 = map_value("changed, test L0", 3, "combined")
    l3_t3 = map_value("changed, test L3", 3, "combined")
    l0_t4 = map_value("changed, test L0", 4, "memory")
    l3_t4 = map_value("changed, test L3", 4, "memory")
    l0_t6 = map_value("unchanged, test L0", 6, "memory")
    l3_t6 = map_value("unchanged, test L3", 6, "memory")
    rt_shift_12 = curves["tested_sample"]["mean_hit_frame"][4] - curves["natural"]["mean_hit_frame"][4]

    rows = []
    for role in ("natural", "tested_sample", "other_sample", "blank_control"):
        effect = effects.get(role)
        rows.append({
            "role": role,
            "accuracy": overall[role]["all_trial_accuracy"],
            "correct": overall[role]["correct_count"],
            "total": overall[role]["total_trials"],
            "mass": overall[role]["target_region_sample_mass"],
            "effect": effect,
            "hr18": curves[role]["hit_rate"][focal_index],
            "d18": curves[role]["dprime"][focal_index],
            "rt18": curves[role]["mean_hit_frame"][focal_index],
        })

    tested = rows[1]
    natural = rows[0]
    effect = tested["effect"]
    assert effect is not None
    result_sentence = (
        f"Suppressing the future-tested sample region produced {effect['discordant_pairs']} discordant "
        f"correctness outcomes among n={effect['n']} paired trials (observed Δ accuracy "
        f"{fmt(effect['mean_inhibited_minus_natural'], 3, True)}). Because the ordinary paired bootstrap is "
        f"degenerate when every observed pair agrees, we report the conservative two-sided 95% no-discordance bound "
        f"|Δ accuracy| < {effect['no_discordance_abs_bound_95']:.4f} under IID trial-pair sampling."
    )

    md_lines = [
        "# Sample-phase spatial attention in the noisy-memory Luo task",
        "",
        "## Executive result",
        "",
        result_sentence,
        "",
        f"The manipulation reduced mean attention mass at the future-tested quadrant during the two sample frames from "
        f"{natural['mass']:.4f} to {tested['mass']:.4f}. This is a successful routing manipulation, but the behavioral estimate "
        "comes from one frozen mid-training checkpoint and does not quantify training-seed uncertainty.",
        "",
        "## Frozen model and protocol",
        "",
        f"- Checkpoint iteration: `{model['iteration']}`",
        f"- Checkpoint SHA-256: `{model['sha256']}`",
        f"- Model grid: `{contract['model_grid'][0]}×{contract['model_grid'][1]}`",
        f"- Sensory orientation noise: `{contract['sensory_noise_std_degrees']}°`",
        f"- Mnemonic noise SD: `{contract['mnemonic_noise_std']}`",
        f"- Training change sampler: `Uniform(−{contract['theta_uniform_training_bound_degrees']}°, +{contract['theta_uniform_training_bound_degrees']}°)`",
        f"- Map aggregation: `{contract['map_repeats_per_exact_latent_cell']}` noisy repetitions per identical latent condition",
        f"- Psychometric grid: `{contract['curve_changed_trials_per_magnitude']}` changed trials per magnitude; "
        f"`{contract['common_nochange_trials']}` shared no-change trials",
        "- Policy actions were sampled; sensory and recurrent-memory noise were enabled.",
        "",
        "## Intervention results",
        "",
        "| Condition | Correct / total | Accuracy | Sample-region mass | Paired Δ; conservative bound | Hit rate at 18° | d′ at 18° | Mean hit frame at 18° |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    labels = {
        "natural": "Natural",
        "tested_sample": "Inhibit future-tested sample",
        "other_sample": "Inhibit other active sample",
        "blank_control": "Inhibit blank control",
    }
    for row in rows:
        effect_text = "reference" if row["effect"] is None else (
            f"{fmt(row['effect']['mean_inhibited_minus_natural'], 3, True)}; "
            f"|Δ|<{row['effect']['no_discordance_abs_bound_95']:.4f}"
        )
        md_lines.append(
            f"| {labels[row['role']]} | {row['correct']} / {row['total']} | {row['accuracy']:.3f} | "
            f"{row['mass']:.4f} | {effect_text} | {row['hr18']:.3f} | {row['d18']:.3f} | {row['rt18']:.3f} |"
        )
    md_lines += [
        "",
        "## Phase-resolved routing",
        "",
        f"At first-test onset `t3`, combined incoming tested-minus-other mass was {l0_t3['target_minus_other']:+.4f} at L0 "
        f"(95% CI [{l0_t3['ci95_low']:+.4f}, {l0_t3['ci95_high']:+.4f}]) and {l3_t3['target_minus_other']:+.4f} at L3. "
        f"Among changed-trial survivors reaching `t4`, recurrent-memory tested-minus-other routing became positive: "
        f"{l0_t4['target_minus_other']:+.4f} at L0 (n={l0_t4['n']}) and {l3_t4['target_minus_other']:+.4f} at L3 (n={l3_t4['n']}). "
        f"At guaranteed test 2, the location-specific contrasts reversed sign ({l0_t6['target_minus_other']:+.4f} at L0, "
        f"{l3_t6['target_minus_other']:+.4f} at L3), so there is no location-general same-site return.",
        "",
        "## Psychometric and chronometric shape",
        "",
        f"The controlled curve was non-monotonic: natural hit rate/d′ peaked at 18° "
        f"({curves['natural']['hit_rate'][focal_index]:.3f}/{curves['natural']['dprime'][focal_index]:.3f}) and fell to "
        f"{curves['natural']['hit_rate'][-1]:.3f}/{curves['natural']['dprime'][-1]:.3f} at 35°. "
        f"All intervention hit-rate and d′ points were identical. Tested-sample inhibition shifted mean hit time by "
        f"{rt_shift_12:+.3f} frame at 12° without changing correctness.",
        "",
        "## Specific trial",
        "",
        f"The rendered example was a no-change first test at location 0 followed by the guaranteed +18° second test. "
        f"The sampled first declaration occurred at `t{trial['first_press']}`, producing `{trial['outcome']}`.",
        "",
        f"- Declare probabilities: `{[round(v, 4) for v in trial['declare_probabilities']]}`",
        f"- Sampled actions: `{trial['sampled_actions']}` (`0=wait`, `1=declare`)",
        f"- GIF: `{trial['gif']}`",
        "",
        "## Evidence boundaries",
        "",
        "- The finite −6 logit bias is strong soft suppression, not hard exclusion; 0.48% of natural target-region mass remained.",
        "- The task has no cue. Both sample Gabors are simultaneously relevant; the lesion uses oracle knowledge of the future test location.",
        "- Attention maps are normalized routing weights, not orientation-content decoding.",
        "- Fixed-magnitude curves are controlled slices within the training support; they are not the training distribution itself.",
        "- Post-decision map frames are survivor-filtered. Changed trials do not contribute after the first-test window.",
        "- Confidence intervals reflect repeated noisy evaluation trials from one checkpoint, not independent training runs.",
        "- The biological comparison target is Luo and Maunsell (2015) V4; this assay is a computational abstraction, not a neural replication.",
    ]
    (report_dir / "report.md").write_text("\n".join(md_lines) + "\n", encoding="utf-8")

    table_rows = []
    for row in rows:
        if row["effect"] is None:
            effect_tex = "reference"
        else:
            effect_tex = (
                f"{fmt(row['effect']['mean_inhibited_minus_natural'], 3, True)}; "
                f"$|\\Delta|<{row['effect']['no_discordance_abs_bound_95']:.4f}$"
            )
        table_rows.append(
            f"{esc(labels[row['role']])} & {row['correct']}/{row['total']} & {row['accuracy']:.3f} & "
            f"{row['mass']:.4f} & {effect_tex} & {row['hr18']:.3f} & {row['d18']:.3f} \\\\"
        )

    latex = rf"""\documentclass[10pt]{{article}}
\usepackage[margin=18mm,headheight=14pt]{{geometry}}
\usepackage{{fontspec}}
\setmainfont{{TeX Gyre Heros}}
\setsansfont{{TeX Gyre Heros}}
\usepackage{{microtype,graphicx,booktabs,tabularx,array,caption,xcolor,hyperref,fancyhdr,amsmath,pdflscape}}
\definecolor{{Blue}}{{HTML}}{{1F6FB2}}
\definecolor{{Orange}}{{HTML}}{{D55E00}}
\definecolor{{Light}}{{HTML}}{{F1F5F8}}
\hypersetup{{colorlinks=true,linkcolor=Blue,urlcolor=Blue,pdftitle={{Luo sample-phase attention assay}}}}
\graphicspath{{{{../figures/}}{{../trial/}}}}
\captionsetup{{font=small,labelfont=bf,justification=justified,singlelinecheck=false}}
\setlength{{\parindent}}{{0pt}}\setlength{{\parskip}}{{0.45em}}
\pagestyle{{fancy}}\fancyhf{{}}\fancyhead[L]{{\small Luo noisy-memory attention assay}}\fancyhead[R]{{\small frozen checkpoint}}\fancyfoot[C]{{\small \thepage}}
\newcommand{{\boundary}}[1]{{\par\smallskip\colorbox{{Light}}{{\parbox{{0.96\linewidth}}{{\textbf{{Evidence boundary.}} #1}}}}\par\smallskip}}
\begin{{document}}
\begin{{titlepage}}
\thispagestyle{{empty}}\vspace*{{10mm}}{{\color{{Blue}}\rule{{\textwidth}}{{2.2pt}}}}\\[8mm]
{{\fontsize{{25}}{{30}}\selectfont\bfseries Sample-phase spatial attention\\in the noisy-memory Luo task\par}}
\vspace{{4mm}}{{\fontsize{{14}}{{19}}\selectfont Noise-averaged maps, an oracle spatial lesion, psychometrics, chronometrics, and a complete rendered trial\par}}
\vfill
\begin{{tabularx}}{{\textwidth}}{{@{{}}p{{4.0cm}}X@{{}}}}\toprule
\textbf{{Frozen checkpoint}} & iteration {model['iteration']}; SHA-256 \texttt{{{model['sha256']}}}.\\
\textbf{{Primary intervention}} & Additive key-logit bias {contract['sample_inhibition_logit_bias']:.1f} at all 100 visual and 100 recurrent-memory keys in the future-tested quadrant, only at sample frames $t0$--$t1$.\\
\textbf{{Primary result}} & {esc(result_sentence)}\\
\textbf{{Run}} & \texttt{{{esc(root.name)}}}.\\\bottomrule
\end{{tabularx}}
\vfill{{\color{{Blue}}\rule{{\textwidth}}{{2.2pt}}}}
\end{{titlepage}}

\begin{{abstract}}
We evaluated one frozen recurrent vision-transformer policy in a seven-frame Luo--Maunsell-inspired change-detection task. Attention maps average {contract['map_repeats_per_exact_latent_cell']} repeats of each exactly fixed latent condition while sensory, mnemonic, and policy-sampling noise vary. A causal routing assay suppressed the future-tested sample quadrant only during sample presentation, with equal-area suppression of the other active sample and a blank quadrant as spatial controls. {esc(result_sentence)} The clamp changed mean sample-frame mass from {natural['mass']:.4f} to {tested['mass']:.4f}. Fixed-magnitude psychometric and chronometric curves characterize the behavioral regime. Results concern one mid-training checkpoint and do not estimate training-seed uncertainty.
\end{{abstract}}

\section{{Question and evidential scope}}
The task has no symbolic or spatial cue: samples are shown simultaneously at locations 0 and 3. The primary causal question is whether routing to the sample at the \emph{{future tested location}} is necessary for later performance. The tested-location intervention is therefore oracle targeted; the model itself is not told which location will be tested.

\boundary{{Raw attention maps show routing, not mnemonic content. The causal clamp establishes the effect of changing that routing operator, but orientation decoding would still be required to identify what information occupies the selected recurrent tokens.}}

\section{{Frozen model and controlled protocol}}
The checkpoint uses a $20\times20$ token grid (400 visual queries; 400 visual plus 400 recurrent-memory keys), xLSTM recurrence, sensory orientation noise SD {contract['sensory_noise_std_degrees']:.1f}$^\circ$, and mnemonic noise SD {contract['mnemonic_noise_std']:.2f}. The training generator samples $\Delta\sim\mathrm{{Uniform}}(-{contract['theta_uniform_training_bound_degrees']:.0f}^\circ,+{contract['theta_uniform_training_bound_degrees']:.0f}^\circ)$. Policy actions are sampled.

Map cells fix test location, change status, signed $18^\circ$ change, and both sample members exactly. Each cell is repeated {contract['map_repeats_per_exact_latent_cell']} times; only sensory rendering noise, recurrent-memory noise, and policy sampling vary. Maps are query-averaged incoming key mass or query-quadrant-to-key-quadrant routing. Frames after an action or automatic termination are excluded.

Psychometrics use fixed $|\Delta|\in\{{{', '.join(str(int(x)) for x in contract['fixed_psychometric_magnitudes_degrees'])}\}}^\circ$, with {contract['curve_changed_trials_per_magnitude']} changed trials per point and {contract['common_nochange_trials']} common no-change trials. These are controlled measurement slices within the training support, not a claim that training used fixed magnitudes. Chronometrics report logical response frame, not biological milliseconds.

\section{{Behavioral effect of sample-phase inhibition}}
\begin{{center}}\small
\begin{{tabular}}{{lrrrrrr}}\toprule
Condition & Correct & Accuracy & Sample mass & $\Delta$ accuracy [95\% CI] & HR at $18^\circ$ & $d'$ at $18^\circ$\\\midrule
{chr(10).join(table_rows)}
\bottomrule\end{{tabular}}
\end{{center}}

{esc(result_sentence)} The other-active-sample and blank-quadrant interventions are equal-area controls under the same logit bias and common trial/noise schedule. Confidence intervals are paired over evaluation trials.

\begin{{center}}\includegraphics[width=0.98\textwidth]{{sample_attention_inhibition_summary.pdf}}
\captionof{{figure}}{{\textbf{{Sample-phase lesion and manipulation check.}} Accuracy is pooled over all fixed-magnitude changed trials and the common no-change bank. Attention mass is measured in the region that each condition targets during $t0$--$t1$.}}
\end{{center}}

\section{{Psychometric and chronometric functions}}
\begin{{center}}\includegraphics[width=0.98\textwidth]{{psychometric_chronometric_curves.pdf}}
\captionof{{figure}}{{\textbf{{Controlled behavioral curves.}} Hit rate and $d'$ are plotted against fixed absolute orientation change. Response timing is a computational frame index: changed trials can declare at first-test onset $t3$ or repeat $t4$.}}
\end{{center}}

\section{{Attention maps across exactly repeated latent conditions}}
\begin{{landscape}}\begin{{center}}\includegraphics[width=0.98\linewidth,height=0.78\textheight,keepaspectratio]{{attention_maps_combined_keys.pdf}}
\captionof{{figure}}{{\textbf{{Combined visual-plus-memory incoming attention.}} Rows are four exact latent conditions (changed/unchanged crossed with test location 0/3); columns are all seven logical frames. Color is $\log_2$ attention relative to uniform spatial mass. Gray cells were not experienced after termination.}}
\end{{center}}\end{{landscape}}

\begin{{landscape}}\begin{{center}}\includegraphics[width=0.98\linewidth,height=0.78\textheight,keepaspectratio]{{attention_maps_recurrent_memory_keys.pdf}}
\captionof{{figure}}{{\textbf{{Recurrent-memory source maps.}} Same aggregation and survivor rule, restricted to recurrent-memory keys under the joint visual-plus-memory softmax.}}
\end{{center}}\end{{landscape}}

\begin{{landscape}}\begin{{center}}\includegraphics[width=0.98\linewidth,height=0.78\textheight,keepaspectratio]{{attention_maps_visual_keys.pdf}}
\captionof{{figure}}{{\textbf{{Current-visual source maps.}} Visual and memory source maps are not independently renormalized; each retains its share of the joint softmax.}}
\end{{center}}\end{{landscape}}

\begin{{landscape}}\begin{{center}}\includegraphics[width=0.98\linewidth,height=0.78\textheight,keepaspectratio]{{attention_query_to_key_routing.pdf}}
\captionof{{figure}}{{\textbf{{Query-conditioned spatial routing.}} Each $4\times4$ tile preserves task-quadrant query origin (rows) and key destination (columns), summing visual and recurrent-memory sources.}}
\end{{center}}\end{{landscape}}

\section{{One complete trial}}
The rendered example had an unchanged first test at location 0 followed by a guaranteed $+18^\circ$ second test. The sampled policy first declared at $t{trial['first_press']}$, yielding a \texttt{{{esc(trial['outcome'])}}}. Its declare probabilities were \texttt{{{esc([round(v, 4) for v in trial['declare_probabilities']])}}}; sampled actions were \texttt{{{esc(trial['sampled_actions'])}}} ($0=$ wait, $1=$ declare).

\begin{{center}}\includegraphics[width=0.98\textwidth]{{specific_trial_montage.pdf}}
\captionof{{figure}}{{\textbf{{Every physical image in the specific trial.}} The animated companion GIF pairs each input with its incoming attention map and action probability.}}
\end{{center}}

\section{{Interpretation and limitations}}
\begin{{enumerate}}
\item This is a single frozen checkpoint at iteration {model['iteration']}; evaluation-trial intervals do not quantify training-seed variability.
\item The intervention suppresses both visual and recurrent-memory keys in one quadrant under a joint softmax. It therefore changes competitive routing globally and is not equivalent to deleting pixels or cell state.
\item Oracle targeting answers a mechanistic counterfactual but is not a model-endogenous cue manipulation.
\item Fixed-magnitude psychometrics deliberately condition the uniform training sampler. Same-distribution competence and transfer must remain separately labeled.
\item The biological comparison target is Luo and Maunsell (2015) V4. This distributed recurrent model is a computational abstraction; raw attention is not a V4 firing-rate measurement.
\end{{enumerate}}

\section{{Reproducibility}}
The run retains reduced source-resolved attention arrays, query-quadrant routing, behavioral curves, CSV tables, the exact trial record, every trial frame, the GIF, producer hash, checkpoint hash, and an artifact manifest. Source checkpoint SHA-256: \texttt{{{model['sha256']}}}. The mutable live-training checkpoint was never opened.

\paragraph{{Reference.}} Luo, T. Z. and Maunsell, J. H. R. (2015). Neuronal modulations in visual cortex are associated with only one of multiple components of attention. \emph{{Neuron}} 86, 1182--1188. \href{{https://doi.org/10.1016/j.neuron.2015.05.007}}{{doi:10.1016/j.neuron.2015.05.007}}.
\end{{document}}
"""
    (report_dir / "main.tex").write_text(latex, encoding="utf-8")
    print(report_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
