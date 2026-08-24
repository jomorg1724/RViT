"""Shared publication style for the deep-dive figures. Large, legible fonts; no
clipping (constrained layout); a consistent palette in which the two pathways have
fixed colours (PRIORITY = the stimulus-grounded pathway that drives the decision;
VALUE = the memory-anchored pathway that drives valuation), and the target and
distractor have fixed colours throughout."""
import matplotlib as mpl
import matplotlib.pyplot as plt

# pathway / task colours (used consistently across every figure)
PRIORITY = "#1f6fb2"   # priority pathway — drives the decision (was "salience")
VALUE    = "#8e44ad"   # value pathway — drives the valuation (was "top-down")
TARGET   = "#2ca02c"   # target quadrant
DISTRACT = "#e6194b"   # distractor quadrant
HIT      = "#1f6fb2"
FA       = "#e6194b"
NEUTRAL  = "#7f7f7f"
REWARD   = {"red": "#d62728", "green": "#2ca02c", "blue": "#1f77b4"}
MAPCMAP  = "magma"


def apply():
    mpl.rcParams.update({
        "figure.dpi": 130,
        "savefig.dpi": 200,
        "savefig.bbox": "tight",
        "font.size": 15,
        "axes.titlesize": 16,
        "axes.titleweight": "bold",
        "axes.titlelocation": "left",
        "axes.labelsize": 15,
        "xtick.labelsize": 13,
        "ytick.labelsize": 13,
        "legend.fontsize": 12.5,
        "legend.frameon": False,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.linewidth": 1.1,
        "lines.linewidth": 2.4,
        "lines.markersize": 7,
        "figure.constrained_layout.use": True,
        "figure.constrained_layout.h_pad": 0.08,
        "figure.constrained_layout.w_pad": 0.08,
    })


def panel_tag(ax, letter):
    """Bold panel letter at the top-left, outside the axes."""
    ax.set_title(ax.get_title(), loc="left", fontweight="bold")
