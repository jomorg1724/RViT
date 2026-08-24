#!/usr/bin/env python3
"""Render the completed Luo scientific assay as a standalone PDF using ReportLab."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    Image, KeepTogether, PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle,
)

BLUE = colors.HexColor("#1F6FB2")
ORANGE = colors.HexColor("#D55E00")
LIGHT = colors.HexColor("#F1F5F8")


def fit_image(path: Path, max_width: float, max_height: float) -> Image:
    from PIL import Image as PILImage
    with PILImage.open(path) as image:
        width, height = image.size
    scale = min(max_width / width, max_height / height)
    return Image(str(path), width=width * scale, height=height * scale)


def page_number(canvas, doc) -> None:
    canvas.saveState()
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(colors.HexColor("#4C566A"))
    canvas.drawCentredString(A4[0] / 2, 10 * mm, f"Luo noisy-memory attention assay  •  {doc.page}")
    canvas.restoreState()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("report_root", type=Path)
    args = parser.parse_args()
    root = args.report_root.resolve()
    summary = json.loads((root / "data" / "summary.json").read_text(encoding="utf-8"))
    report = root / "report"
    report.mkdir(exist_ok=True)
    output = report / "luo2015_attention_scientific_report.pdf"

    styles = getSampleStyleSheet()
    title = ParagraphStyle("Title2", parent=styles["Title"], fontName="Helvetica-Bold", fontSize=24,
                           leading=29, textColor=BLUE, alignment=TA_CENTER, spaceAfter=10)
    subtitle = ParagraphStyle("Subtitle", parent=styles["Normal"], fontName="Helvetica", fontSize=12,
                              leading=16, textColor=colors.HexColor("#4C566A"), alignment=TA_CENTER)
    h1 = ParagraphStyle("H1", parent=styles["Heading1"], fontName="Helvetica-Bold", fontSize=16,
                        leading=19, textColor=BLUE, spaceBefore=10, spaceAfter=6)
    body = ParagraphStyle("Body2", parent=styles["BodyText"], fontName="Helvetica", fontSize=9.2,
                          leading=13, spaceAfter=6)
    caption = ParagraphStyle("Caption2", parent=body, fontSize=8, leading=10, textColor=colors.HexColor("#4C566A"))
    boundary = ParagraphStyle("Boundary", parent=body, backColor=LIGHT, borderPadding=7, borderColor=LIGHT,
                              borderWidth=1, spaceBefore=5, spaceAfter=8)

    c = summary["contract"]
    cp = summary["checkpoint"]
    overall = summary["intervention_overall"]
    effects = summary["paired_accuracy_effects"]
    curves = summary["curves"]
    mags = list(map(float, c["fixed_psychometric_magnitudes_degrees"]))
    idx18 = mags.index(18.0)
    trial = summary["specific_trial"]
    e = effects["tested_sample"]
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

    sentence = (
        f"Suppressing the future-tested sample region produced {e['discordant_pairs']} discordant correctness outcomes "
        f"among n={e['n']} paired trials (observed Δ accuracy {e['mean_inhibited_minus_natural']:+.3f}). "
        f"The ordinary paired bootstrap is degenerate because every observed pair agrees; the conservative two-sided "
        f"95% no-discordance bound is |Δ accuracy| &lt; {e['no_discordance_abs_bound_95']:.4f} under IID trial-pair sampling."
    )
    story = [
        Spacer(1, 18 * mm),
        Paragraph("Sample-phase spatial attention<br/>in the noisy-memory Luo task", title),
        Paragraph("Noise-averaged maps, oracle spatial inhibition, psychometrics, chronometrics, and one complete rendered trial", subtitle),
        Spacer(1, 13 * mm),
        Table([
            [Paragraph("Frozen checkpoint", body), Paragraph(f"Iteration {cp['iteration']}; SHA-256 <font name='Courier'>{cp['sha256']}</font>", body)],
            [Paragraph("Primary intervention", body), Paragraph(f"Bias {c['sample_inhibition_logit_bias']:.1f} at all visual and memory keys in the future-tested quadrant, sample frames t0–t1 only.", body)],
            [Paragraph("Primary result", body), Paragraph(sentence, body)],
            [Paragraph("Run", body), Paragraph(root.name, body)],
        ], colWidths=[42 * mm, 125 * mm], style=[
            ("BACKGROUND", (0, 0), (0, -1), LIGHT), ("BOX", (0, 0), (-1, -1), 0.5, BLUE),
            ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.white), ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING", (0, 0), (-1, -1), 6), ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ]),
        PageBreak(),
        Paragraph("Abstract", h1),
        Paragraph(
            f"We evaluated one frozen recurrent vision policy in a seven-frame Luo–Maunsell-inspired change-detection task. "
            f"Attention maps average {c['map_repeats_per_exact_latent_cell']} repeats of each exactly fixed latent condition while sensory, mnemonic, and policy-sampling noise vary. "
            f"The causal assay suppressed routing to the future-tested sample quadrant and used equal-area active-sample and blank-region controls. {sentence} "
            f"The manipulation reduced sample-frame mass at the future-tested region from {overall['natural']['target_region_sample_mass']:.4f} to {overall['tested_sample']['target_region_sample_mass']:.4f}. "
            "All estimates come from one mid-training checkpoint and do not quantify training-seed uncertainty.", body),
        Paragraph("Question and evidence boundary", h1),
        Paragraph("The task has no symbolic or spatial cue. Two sample Gabors appear simultaneously at locations 0 and 3. The lesion uses oracle knowledge of which sample location will later be tested; the model does not receive that information.", body),
        Paragraph("<b>Evidence boundary.</b> Raw attention maps are routing weights, not orientation-content decoding. A regional attention lesion tests the effect of changing that routing computation, but does not identify the content stored in recurrent tokens.", boundary),
        Paragraph("Frozen model and protocol", h1),
        Paragraph(
            f"The checkpoint uses a 20×20 token grid (400 current-image queries; 400 visual plus 400 recurrent-memory keys), sensory orientation-noise SD {c['sensory_noise_std_degrees']:.1f}°, and mnemonic-noise SD {c['mnemonic_noise_std']:.2f}. "
            f"Training sampled Δ uniformly from −{c['theta_uniform_training_bound_degrees']:.0f}° to +{c['theta_uniform_training_bound_degrees']:.0f}°. Actions were sampled. "
            f"Each exact map cell used {c['map_repeats_per_exact_latent_cell']} noisy repetitions. Fixed-magnitude behavioral curves used {c['curve_changed_trials_per_magnitude']} changed trials per point and {c['common_nochange_trials']} common no-change trials.", body),
        Paragraph("Behavioral effect of sample inhibition", h1),
    ]

    labels = {"natural": "Natural", "tested_sample": "Inhibit future-tested sample",
              "other_sample": "Inhibit other active sample", "blank_control": "Inhibit blank control"}
    table = [["Condition", "Correct", "Accuracy", "Sample mass", "Paired Δ; bound", "HR 18°", "d′ 18°"]]
    for role in ("natural", "tested_sample", "other_sample", "blank_control"):
        row = overall[role]
        effect = effects.get(role)
        effect_text = "reference" if effect is None else (
            f"{effect['mean_inhibited_minus_natural']:+.3f}; |Δ|<{effect['no_discordance_abs_bound_95']:.4f}"
        )
        table.append([
            labels[role], f"{row['correct_count']}/{row['total_trials']}", f"{row['all_trial_accuracy']:.3f}",
            f"{row['target_region_sample_mass']:.4f}", effect_text,
            f"{curves[role]['hit_rate'][idx18]:.3f}", f"{curves[role]['dprime'][idx18]:.3f}",
        ])
    t = Table(table, colWidths=[43 * mm, 18 * mm, 17 * mm, 20 * mm, 35 * mm, 17 * mm, 17 * mm], repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), BLUE), ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"), ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 7.4), ("GRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#B8C2CC")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"), ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LIGHT]),
    ]))
    story += [
        t, Spacer(1, 4 * mm), Paragraph(sentence, body),
        Paragraph("Phase-resolved routing", h1),
        Paragraph(
            f"At first-test onset t3, combined incoming attention favored the other active-sample quadrant over the tested quadrant: "
            f"tested-minus-other mass was {l0_t3['target_minus_other']:+.4f} at L0 (95% interval [{l0_t3['ci95_low']:+.4f}, {l0_t3['ci95_high']:+.4f}]) "
            f"and {l3_t3['target_minus_other']:+.4f} at L3. Among the small survivor sets reaching t4 on changed trials, recurrent-memory routing then favored the tested quadrant: "
            f"{l0_t4['target_minus_other']:+.4f} at L0 (n={l0_t4['n']}) and {l3_t4['target_minus_other']:+.4f} at L3 (n={l3_t4['n']}). "
            f"At guaranteed test 2, the memory contrast reversed by location ({l0_t6['target_minus_other']:+.4f} at L0 versus {l3_t6['target_minus_other']:+.4f} at L3), so it does not support a location-general same-site return.", body),
        Paragraph("Psychometric and chronometric shape", h1),
        Paragraph(
            f"The controlled psychometric slice was strongly non-monotonic: natural hit rate and d′ peaked at 18° "
            f"({curves['natural']['hit_rate'][idx18]:.3f}, {curves['natural']['dprime'][idx18]:.3f}) but fell to "
            f"{curves['natural']['hit_rate'][-1]:.3f} and {curves['natural']['dprime'][-1]:.3f} at 35°. Thus a monotone sigmoid would be a poor summary of this checkpoint. "
            f"All intervention hit-rate and d′ points were identical. The only visible timing deviation was a {rt_shift_12:+.3f}-frame mean-hit shift at 12° under tested-sample inhibition, without a correctness change.", body),
    ]

    figures = [
        ("sample_attention_inhibition_summary.png", "Sample-phase lesion and manipulation check. Accuracy pools all controlled changed trials and the common no-change bank."),
        ("psychometric_chronometric_curves.png", "Psychometric and chronometric slices. Response time is a logical frame index, not biological milliseconds."),
        ("attention_maps_combined_keys.png", "Combined visual-plus-memory incoming attention across four exact latent conditions and all seven logical frames. Gray frames were not experienced after termination."),
        ("attention_maps_recurrent_memory_keys.png", "Recurrent-memory source maps under the joint softmax. Sources are not independently renormalized."),
        ("attention_maps_visual_keys.png", "Current-visual source maps under the same fixed conditions, noise repetitions, and survivor rule."),
        ("attention_query_to_key_routing.png", "Query-quadrant to key-quadrant routing. Each 4×4 tile preserves query origin and spatial destination."),
    ]
    for index, (filename, cap) in enumerate(figures):
        story += [PageBreak(), Paragraph(cap.split(".")[0], h1),
                  fit_image(root / "figures" / filename, 174 * mm, 220 * mm), Spacer(1, 2 * mm),
                  Paragraph(f"<b>Figure {index + 1}.</b> {cap}", caption)]

    story += [
        PageBreak(), Paragraph("One complete trial", h1),
        Paragraph(
            f"The example had an unchanged first test at location 0 followed by a guaranteed +18° second test. "
            f"The sampled policy first declared at t{trial['first_press']}, producing {trial['outcome']}. "
            f"Declare probabilities were {[round(v, 4) for v in trial['declare_probabilities']]}; actions were {trial['sampled_actions']} (0=wait, 1=declare).", body),
        fit_image(root / "trial" / "specific_trial_montage.png", 174 * mm, 190 * mm),
        Paragraph("<b>Figure 7.</b> Every physical input frame in the specific trial. The companion GIF pairs each image with incoming attention and action probability.", caption),
        Paragraph("Interpretation and limitations", h1),
        Paragraph(
            "(1) This is one frozen checkpoint; intervals cover evaluation-trial noise, not independent training seeds. "
            "(2) The finite −6 logit bias is strong soft suppression, not hard exclusion: 0.48% of the natural target-region mass remained. It suppresses both visual and memory keys in a quadrant under a joint softmax, changing competitive routing rather than deleting pixels. "
            "(3) Oracle targeting is a mechanistic counterfactual, not an endogenous cue. "
            "(4) Fixed-magnitude curves condition the training sampler and must not be called same-distribution performance. "
            "(5) The biological target is Luo and Maunsell (2015) V4; cross-attention is a computational abstraction, not a firing-rate measure.", body),
        Paragraph("Reproducibility", h1),
        Paragraph(
            f"Checkpoint SHA-256: <font name='Courier'>{cp['sha256']}</font>. The report directory retains source-resolved reduced attention arrays, query-routing arrays, CSV curves, every trial frame, the GIF, producer hashes, and an artifact manifest. The mutable live-training checkpoint was never opened.", body),
        Paragraph("Reference", h1),
        Paragraph("Luo, T. Z. &amp; Maunsell, J. H. R. (2015). Neuronal modulations in visual cortex are associated with only one of multiple components of attention. <i>Neuron</i> 86, 1182–1188. doi:10.1016/j.neuron.2015.05.007.", body),
    ]

    document = SimpleDocTemplate(str(output), pagesize=A4, rightMargin=18 * mm, leftMargin=18 * mm,
                                 topMargin=17 * mm, bottomMargin=17 * mm, title="Luo sample-phase attention assay")
    document.build(story, onFirstPage=page_number, onLaterPages=page_number)
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
