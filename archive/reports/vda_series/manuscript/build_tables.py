from __future__ import annotations

import csv
from collections import Counter, OrderedDict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
MATRIX = ROOT / "reports" / "vda_series" / "PANEL_COVERAGE.csv"
OUT = HERE / "generated"
OUT.mkdir(parents=True, exist_ok=True)

ENV_ABBR = OrderedDict([
    ("validity4", "Val4"),
    ("vda1", "H1"),
    ("vda2", "H2"),
    ("vda4", "H4"),
    ("vda9", "H9"),
    ("vda16_historical", "H16"),
    ("vda_excl", "Excl"),
    ("vda_probe_cued", "PC"),
    ("vda_probe_uncued", "PU"),
    ("vda_fixed1", "F1"),
    ("vda_fixed2", "F2"),
    ("vda_fixed4", "F4"),
    ("vda_fixed9", "F9"),
    ("vda_fixed16", "F16"),
])
STATUSES = OrderedDict([
    ("complete", "C"),
    ("partial", "P"),
    ("available", "A"),
    ("training", "T"),
    ("blocked", "B"),
    ("undefined", "U"),
    ("inapplicable", "I"),
])


def esc(value: str) -> str:
    replacements = {
        "\\": r"\textbackslash{}",
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
        "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
    }
    return "".join(replacements.get(ch, ch) for ch in value)


def envs_for(row: dict[str, str], status: str) -> str:
    values = [abbr for key, abbr in ENV_ABBR.items() if row[key] == status]
    return ", ".join(values) if values else r"\textemdash"


def main() -> None:
    with MATRIX.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    allowed = set(STATUSES)
    observed = {row[key] for row in rows for key in ENV_ABBR}
    if not observed <= allowed:
        raise ValueError(f"unexpected panel status values: {sorted(observed - allowed)}")

    counts = Counter(row[key] for row in rows for key in ENV_ABBR)
    total = len(rows) * len(ENV_ABBR)
    summary = [
        r"\begin{tabular}{@{}lrr@{}}",
        r"\toprule",
        r"Status & Cells & Share \\",
        r"\midrule",
    ]
    row_end = " " + chr(92) * 2
    for status in STATUSES:
        n = counts.get(status, 0)
        summary.append(f"{status.title()} & {n} & {100*n/total:.1f}\\%" + row_end)
    summary.extend([r"\midrule", f"Total & {total} & 100.0\\%" + row_end, r"\bottomrule", r"\end{tabular}"])
    (OUT / "status_summary.tex").write_text("\n".join(summary) + "\n", encoding="utf-8")

    table = [
        r"\begingroup",
        r"\footnotesize",
        r"\setlength{\tabcolsep}{2.5pt}",
        r"\renewcommand{\arraystretch}{1.08}",
        r"\begin{longtable}{@{}p{1.8cm}p{3.9cm}p{2.2cm}p{2.2cm}p{2.0cm}p{2.3cm}p{2.35cm}p{2.5cm}@{}}",
        r"\caption{Exact source-panel disposition by environment. The table is generated directly from \texttt{PANEL\_COVERAGE.csv}; comma-separated abbreviations name every environment assigned to each state.}\label{tab:panel-matrix}\\",
        r"\toprule",
        r"Panel & Purpose & C/P & Available & Training & Blocked & Undefined & Inapplicable \\",
        r"\midrule",
        r"\endfirsthead",
        r"\multicolumn{8}{c}{\tablename\ \thetable\ (continued)}\\",
        r"\toprule",
        r"Panel & Purpose & C/P & Available & Training & Blocked & Undefined & Inapplicable \\",
        r"\midrule",
        r"\endhead",
        r"\midrule \multicolumn{8}{r}{Continued on next page}\\ \endfoot",
        r"\bottomrule \endlastfoot",
    ]
    previous_object = None
    for row in rows:
        obj = row["source_object"]
        if previous_object is not None and obj != previous_object:
            table.append(r"\addlinespace[2pt]")
        cp = []
        for status in ("complete", "partial"):
            envs = envs_for(row, status)
            if envs != r"\textemdash":
                cp.append(f"{STATUSES[status]}: {envs}")
        cp_text = "; ".join(cp) if cp else r"\textemdash"
        fields = [
            esc(row["panel_group"]),
            esc(row["purpose"]),
            cp_text,
            envs_for(row, "available"),
            envs_for(row, "training"),
            envs_for(row, "blocked"),
            envs_for(row, "undefined"),
            envs_for(row, "inapplicable"),
        ]
        table.append(" & ".join(fields) + r" \\")
        previous_object = obj
    table.extend([r"\end{longtable}", r"\endgroup"])
    (OUT / "panel_coverage_table.tex").write_text("\n".join(table) + "\n", encoding="utf-8")

    object_rows = []
    for obj in OrderedDict.fromkeys(row["source_object"] for row in rows):
        selected = [row for row in rows if row["source_object"] == obj]
        object_counts = Counter(row[key] for row in selected for key in ENV_ABBR)
        object_rows.append(
            f"{esc(obj)} & {len(selected)} & "
            + " & ".join(str(object_counts.get(status, 0)) for status in STATUSES)
            + r" \\"
        )
    object_table = [
        r"\begingroup",
        r"\normalsize",
        r"\renewcommand{\arraystretch}{1.10}",
        r"\begin{longtable}{@{}lrrrrrrrr@{}}",
        r"\caption{Coverage counts by source object. Counts are panel--environment cells, not independent experiments. Status codes are C complete, P partial, A available, T training, B blocked, U undefined, and I inapplicable.}\label{tab:object-counts}\\",
        r"\toprule",
        r"Object & Groups & C & P & A & T & B & U & I \\",
        r"\midrule\endfirsthead",
        r"\toprule Object & Groups & C & P & A & T & B & U & I \\ \midrule\endhead",
        *object_rows,
        r"\bottomrule",
        r"\end{longtable}",
        r"\endgroup",
    ]
    (OUT / "object_status_counts.tex").write_text("\n".join(object_table) + "\n", encoding="utf-8")
    print(f"generated tables from {len(rows)} panel groups × {len(ENV_ABBR)} environments = {total} cells")


if __name__ == "__main__":
    main()
