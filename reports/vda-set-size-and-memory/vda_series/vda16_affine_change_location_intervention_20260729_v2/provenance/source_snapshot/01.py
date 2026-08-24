"""Paired attention-manipulation experiment at cued, changed, and control locations.

On trials with the physical change forced away from the cue (invalid trials), this
sweeps the same graded additive key-logit bias already used for the cued-location
clamp (Section 5.1 of the manuscript), independently targeted at three locations:

  1. the true change location  -- the rescue/lesion test itself;
  2. the cued (wrong) location  -- a negative control;
  3. a third, task-irrelevant location -- a spatial-specificity control.

It reuses existing, already-tested primitives without any new model code:
``vda_core.clamp_alpha`` (graded additive key-logit bias, already generic over
location index), ``vda_core.make_video_batch`` (forced-location trial generation),
and ``matched_width._sdt_from_counts`` (d'/criterion from hit/false-alarm counts).
The only new logic is a thin step loop that calls ``model.rl_step`` with both
``return_attn=True`` and ``attn_clamp`` together (both already accepted by every
attention module; see ``paper_encoder.py``), mirroring ``vda_core.press_times_clamp``
but additionally collecting the attention trajectory.

Each environment is admitted only if its checkpoint file is actually present and its
SHA-256 matches the registered value; a missing checkpoint is recorded as blocked in
the manifest rather than silently skipped or fabricated.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import platform
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
import sys

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from vda_sweep import matched_width as MW
from vda_sweep import vda_core as core

CLAMP_DOSE_PARAMETERS = MW.CLAMP_DOSE_PARAMETERS  # (0.0, 0.25, 0.5, 0.75, 1.0)
CLAMP_LOGIT_SCALE = MW.CLAMP_LOGIT_SCALE  # 6.0
NATURAL_DOSE = 0.5
TRIALS_PER_CONDITION = 300
INVALID_TRIALS_SEED = 20270719
NOCHANGE_TRIALS_SEED = 20270720
CLAMP_FROM = 5
QUALIFYING_FRAMES = (5, 6)
LOCATION_ROLES = ("change", "cued", "control")
ROLE_COLORS = {"change": "#0072B2", "cued": "#D55E00", "control": "#888888"}
ROLE_LABELS = {
    "change": "target = true change location (rescue/lesion test)",
    "cued": "target = cued (wrong) location (negative control)",
    "control": "target = task-irrelevant location (specificity control)",
}


@dataclass(frozen=True)
class EnvSpec:
    env: str
    feedback: str
    width: int
    grid: tuple[int, int]
    n_locations: int
    cue_index: int
    change_index: int
    control_index: int
    focal_magnitude: float
    displayed_validity: float
    checkpoint_path: Path
    checkpoint_sha256: str


VDA16_CHECKPOINT = (
    ROOT
    / "reports/vda_series/vda16_crossattn_nodecay_20260719_production/provenance/checkpoints/rvit_paper_vda16_final.pt"
)

ENV_SPECS: list[EnvSpec] = [
    EnvSpec(
        env="vda16",
        feedback="crossattn1",
        width=128,
        grid=(4, 4),
        n_locations=16,
        cue_index=0,
        change_index=15,
        control_index=5,
        focal_magnitude=30.0,
        displayed_validity=1.0,
        checkpoint_path=VDA16_CHECKPOINT,
        checkpoint_sha256="b40d9aa49ec28c352d7a790de84f5902e1a307f7b2abe5fe68dc9e6aabb4f84d",
    ),
    EnvSpec(
        env="vda4",
        feedback="crossattn1",
        width=128,
        grid=(2, 2),
        n_locations=4,
        cue_index=0,
        change_index=3,
        control_index=1,
        focal_magnitude=18.0,
        displayed_validity=1.0,
        checkpoint_path=MW.CHECKPOINT_ROOT / "vda4_crossattn1_d128/rvit_plus_rl_latest.pt",
        checkpoint_sha256=MW._HASHES[("vda4", "crossattn1", 128)],
    ),
    EnvSpec(
        env="vda9",
        feedback="crossattn1",
        width=128,
        grid=(3, 3),
        n_locations=9,
        cue_index=0,
        change_index=8,
        control_index=4,
        focal_magnitude=18.0,
        displayed_validity=1.0,
        checkpoint_path=MW.CHECKPOINT_ROOT / "vda9_crossattn1_d128/rvit_plus_rl_latest.pt",
        checkpoint_sha256=MW._HASHES[("vda9", "crossattn1", 128)],
    ),
]


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def role_target(spec: EnvSpec, role: str) -> int:
    return {"change": spec.change_index, "cued": spec.cue_index, "control": spec.control_index}[role]


def rollout_with_clamp(
    model: Any, videos: "torch.Tensor", clamp: dict[str, float] | None, clamp_from: int
) -> tuple[np.ndarray, np.ndarray]:
    """Step the model over the trial with an optional attn_clamp from ``clamp_from``.

    Mirrors ``vda_core.press_times_clamp`` exactly (same clamp-gating logic) but
    additionally collects the raw attention tensor at every timestep, which the
    existing helper discards.
    """
    import torch

    batch = int(videos.shape[0])
    state = model.init_states(batch, device=core.DEVICE)
    press = np.full(batch, -1, dtype=np.int64)
    attn_frames = []
    for t in range(core.T):
        active_clamp = clamp if (clamp and t >= clamp_from) else None
        with torch.no_grad():
            step = model.rl_step(videos[:, t], state, return_attn=True, attn_clamp=active_clamp)
            actions = step["actor_logits"].argmax(-1).cpu().numpy()
            state = step["new_states"]
            attn = step["attn"]
        newly_pressed = (actions == 1) & (press < 0)
        press[newly_pressed] = t
        attn_frames.append(attn[0].detach().cpu().numpy() if attn is not None else None)
    attn_seq = np.stack(attn_frames, axis=1)  # (B, T, N, K)
    return press, attn_seq


def achieved_location_mass(raw_attention: np.ndarray, n_locations: int) -> np.ndarray:
    """Return trial x time x location mass, summing image+memory keys for cross-attention."""
    raw = np.asarray(raw_attention, dtype=np.float64)
    _, _, queries, keys = raw.shape
    if keys == 2 * n_locations:
        image = raw[..., :n_locations]
        memory = raw[..., n_locations:]
        mass = (image + memory).mean(axis=2)
    elif keys == n_locations:
        mass = raw.mean(axis=2)
    else:
        raise ValueError(f"unexpected key count {keys} for {n_locations} locations")
    np.testing.assert_allclose(
        mass.sum(axis=-1), np.ones(mass.shape[:2]), rtol=1e-4, atol=1e-5,
        err_msg="achieved spatial attention mass does not sum to one",
    )
    return mass


def qualifying_response(press: np.ndarray) -> np.ndarray:
    return np.isin(press, QUALIFYING_FRAMES)


def conditional_mean_frame(press: np.ndarray, qualifying: np.ndarray) -> float:
    if not np.any(qualifying):
        return float("nan")
    return float(press[qualifying].mean())


def run_environment(spec: EnvSpec, output_root: Path) -> dict[str, Any]:
    env_root = output_root / spec.env
    data_dir = env_root / "data"
    figures_dir = env_root / "figures"

    if not spec.checkpoint_path.is_file():
        record = {
            "env": spec.env,
            "status": "blocked",
            "reason": "checkpoint file not present in this working environment",
            "expected_path": str(spec.checkpoint_path),
            "expected_sha256": spec.checkpoint_sha256,
        }
        env_root.mkdir(parents=True, exist_ok=True)
        (env_root / "BLOCKED.json").write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
        print(f"[{spec.env}] BLOCKED: checkpoint not found at {spec.checkpoint_path}")
        return record

    checkpoint_sha256 = sha256_file(spec.checkpoint_path)
    if checkpoint_sha256 != spec.checkpoint_sha256:
        raise RuntimeError(
            f"{spec.env}: checkpoint SHA-256 {checkpoint_sha256} does not match "
            f"registered {spec.checkpoint_sha256}"
        )

    import scipy
    import torch

    model, iteration = core.load(
        spec.env, spec.feedback, spec.width, checkpoint_path=str(spec.checkpoint_path)
    )
    print(f"[{spec.env}] loaded checkpoint at iteration {iteration}")

    invalid_videos = core.make_video_batch(
        spec.env, spec.cue_index, spec.displayed_validity, "red", 1, spec.change_index,
        spec.focal_magnitude, B=TRIALS_PER_CONDITION, seed=INVALID_TRIALS_SEED,
    )
    nochange_videos = core.make_video_batch(
        spec.env, spec.cue_index, spec.displayed_validity, "red", 0, -1,
        spec.focal_magnitude, B=TRIALS_PER_CONDITION, seed=NOCHANGE_TRIALS_SEED,
    )

    keys = 2 * spec.n_locations if spec.feedback == "crossattn1" else spec.n_locations

    def evaluate(clamp: dict[str, float] | None) -> dict[str, np.ndarray]:
        invalid_press, invalid_attn = rollout_with_clamp(model, invalid_videos, clamp, CLAMP_FROM)
        nochange_press, nochange_attn = rollout_with_clamp(model, nochange_videos, clamp, CLAMP_FROM)
        invalid_mass = achieved_location_mass(invalid_attn, spec.n_locations)
        return {
            "invalid_press": invalid_press,
            "invalid_mass": invalid_mass,
            "nochange_press": nochange_press,
        }

    print(f"[{spec.env}] natural (dose={NATURAL_DOSE}, no clamp) condition")
    natural = evaluate(None)

    results: dict[str, dict[float, dict[str, np.ndarray]]] = {role: {} for role in LOCATION_ROLES}
    for role in LOCATION_ROLES:
        results[role][NATURAL_DOSE] = natural
        for dose in CLAMP_DOSE_PARAMETERS:
            if np.isclose(dose, NATURAL_DOSE):
                continue
            target = role_target(spec, role)
            clamp = core.clamp_alpha(keys, spec.n_locations, target, dose, scale=CLAMP_LOGIT_SCALE)
            print(f"[{spec.env}] role={role} target_loc={target} dose={dose}")
            results[role][dose] = evaluate(clamp)

    if sha256_file(spec.checkpoint_path) != checkpoint_sha256:
        raise RuntimeError(f"{spec.env}: checkpoint changed during analysis")

    doses_sorted = sorted({NATURAL_DOSE, *CLAMP_DOSE_PARAMETERS})
    summary: dict[str, Any] = {
        "env": spec.env,
        "status": "ok",
        "feedback": spec.feedback,
        "width": spec.width,
        "grid": list(spec.grid),
        "n_locations": spec.n_locations,
        "checkpoint_iteration": iteration,
        "checkpoint_path": str(spec.checkpoint_path),
        "checkpoint_sha256": checkpoint_sha256,
        "cue_index": spec.cue_index,
        "change_index": spec.change_index,
        "control_index": spec.control_index,
        "focal_magnitude_degrees": spec.focal_magnitude,
        "displayed_validity": spec.displayed_validity,
        "trials_per_condition": TRIALS_PER_CONDITION,
        "clamp_from_frame": CLAMP_FROM,
        "qualifying_response_frames": list(QUALIFYING_FRAMES),
        "doses": doses_sorted,
        "roles": {role: ROLE_LABELS[role] for role in LOCATION_ROLES},
        "role_target_location": {role: role_target(spec, role) for role in LOCATION_ROLES},
        "seed_policy": (
            "common random numbers: one invalid-change trial batch and one no-change trial "
            "batch, shared across every role/dose condition; only the attn_clamp differs"
        ),
    }

    per_role_dose_metrics: dict[str, dict[str, list[float]]] = {
        role: {
            "response_rate": [],
            "false_alarm_rate": [],
            "dprime": [],
            "criterion": [],
            "conditional_mean_response_frame": [],
            "achieved_change_mass_t6": [],
            "achieved_cued_mass_t6": [],
            "achieved_control_mass_t6": [],
        }
        for role in LOCATION_ROLES
    }
    for role in LOCATION_ROLES:
        for dose in doses_sorted:
            payload = results[role][dose]
            qualifying = qualifying_response(payload["invalid_press"])
            hit_count = int(qualifying.sum())
            false_alarm_count = int((payload["nochange_press"] >= 0).sum())
            dprime, criterion = MW._sdt_from_counts(
                np.asarray(hit_count), np.asarray(false_alarm_count), TRIALS_PER_CONDITION
            )
            metrics = per_role_dose_metrics[role]
            metrics["response_rate"].append(hit_count / TRIALS_PER_CONDITION)
            metrics["false_alarm_rate"].append(false_alarm_count / TRIALS_PER_CONDITION)
            metrics["dprime"].append(float(dprime))
            metrics["criterion"].append(float(criterion))
            metrics["conditional_mean_response_frame"].append(
                conditional_mean_frame(payload["invalid_press"], qualifying)
            )
            mass_t6 = payload["invalid_mass"][:, 6, :].mean(axis=0)
            metrics["achieved_change_mass_t6"].append(float(mass_t6[spec.change_index]))
            metrics["achieved_cued_mass_t6"].append(float(mass_t6[spec.cue_index]))
            metrics["achieved_control_mass_t6"].append(float(mass_t6[spec.control_index]))

    summary["metrics"] = per_role_dose_metrics

    data_dir.mkdir(parents=True, exist_ok=True)
    figures_dir.mkdir(parents=True, exist_ok=True)

    npz_payload = {"doses": np.asarray(doses_sorted, dtype=np.float64)}
    for role in LOCATION_ROLES:
        for dose in doses_sorted:
            key = f"{role}_dose{dose}"
            npz_payload[f"{key}_invalid_press"] = results[role][dose]["invalid_press"]
            npz_payload[f"{key}_nochange_press"] = results[role][dose]["nochange_press"]
            npz_payload[f"{key}_invalid_mass"] = results[role][dose]["invalid_mass"]
    cache_path = data_dir / "change_location_intervention.npz"
    np.savez_compressed(cache_path, **npz_payload, metadata_json=np.asarray(json.dumps(summary, sort_keys=True)))

    figure_paths = render_figures(spec, doses_sorted, per_role_dose_metrics, results, figures_dir)

    summary["cache_path"] = str(cache_path.resolve())
    summary["cache_sha256"] = sha256_file(cache_path)
    summary["figure_outputs"] = {name: str(path.resolve()) for name, path in figure_paths.items()}
    summary["runtime_versions"] = {
        "python": platform.python_version(),
        "numpy": np.__version__,
        "torch": torch.__version__,
        "scipy": scipy.__version__,
        "matplotlib": matplotlib.__version__,
        "device": str(core.DEVICE),
    }
    summary["producer_path"] = str(Path(__file__).resolve())
    summary["producer_sha256"] = sha256_file(Path(__file__).resolve())

    summary_path = data_dir / "summary.json"
    summary_path.write_text(json.dumps(summary, indent=2, allow_nan=True) + "\n", encoding="utf-8")

    csv_path = data_dir / "curves.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(
            ["role", "dose", "bias", "response_rate", "false_alarm_rate", "dprime", "criterion",
             "conditional_mean_response_frame", "achieved_change_mass_t6", "achieved_cued_mass_t6",
             "achieved_control_mass_t6"]
        )
        for role in LOCATION_ROLES:
            metrics = per_role_dose_metrics[role]
            for i, dose in enumerate(doses_sorted):
                bias = CLAMP_LOGIT_SCALE * (2.0 * dose - 1.0)
                writer.writerow(
                    [role, dose, bias]
                    + [metrics[field][i] for field in (
                        "response_rate", "false_alarm_rate", "dprime", "criterion",
                        "conditional_mean_response_frame", "achieved_change_mass_t6",
                        "achieved_cued_mass_t6", "achieved_control_mass_t6",
                    )]
                )

    print(f"[{spec.env}] wrote {env_root}")
    return summary


def render_figures(
    spec: EnvSpec,
    doses_sorted: list[float],
    metrics: dict[str, dict[str, list[float]]],
    results: dict[str, dict[float, dict[str, np.ndarray]]],
    figures_dir: Path,
) -> dict[str, Path]:
    plt.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "font.size": 9,
            "axes.titlesize": 10,
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
        }
    )
    biases = [CLAMP_LOGIT_SCALE * (2.0 * d - 1.0) for d in doses_sorted]
    figure, axes = plt.subplots(2, 2, figsize=(11.0, 8.6), constrained_layout=True)
    for role in LOCATION_ROLES:
        color = ROLE_COLORS[role]
        label = role
        axes[0, 0].plot(biases, metrics[role]["response_rate"], color=color, marker="o", ms=4, lw=1.8, label=label)
        axes[0, 1].plot(biases, metrics[role]["dprime"], color=color, marker="o", ms=4, lw=1.8, label=label)
        axes[1, 0].plot(biases, metrics[role]["criterion"], color=color, marker="o", ms=4, lw=1.8, label=label)
        target_mass_field = f"achieved_{role if role != 'cued' else 'cued'}_mass_t6"
        # each role's own target location mass:
        target_key = {"change": "achieved_change_mass_t6", "cued": "achieved_cued_mass_t6",
                       "control": "achieved_control_mass_t6"}[role]
        axes[1, 1].plot(biases, metrics[role][target_key], color=color, marker="o", ms=4, lw=1.8, label=label)

    valid_ref = metrics["change"]["response_rate"][doses_sorted.index(NATURAL_DOSE)]
    axes[0, 0].axhline(valid_ref, color="#333333", lw=0.8, ls=":", label="natural invalid-trial baseline")
    axes[0, 0].set(
        title="A  Qualifying response rate on invalid trials",
        xlabel="additive bias at targeted location",
        ylabel="P(qualifying response)",
        ylim=(-0.02, 1.02),
    )
    axes[0, 1].set(title="B  Sensitivity $d'$", xlabel="additive bias at targeted location", ylabel="$d'$")
    axes[1, 0].set(title="C  Criterion $c$", xlabel="additive bias at targeted location", ylabel="$c$")
    axes[1, 1].axhline(1.0 / spec.n_locations, color="#555555", lw=0.8, ls=":", label="uniform location mass")
    axes[1, 1].set(
        title="D  Achieved attention mass at the targeted location (t6)",
        xlabel="additive bias at targeted location",
        ylabel="achieved attention mass",
    )
    for axis in axes.flat:
        axis.grid(alpha=0.2)
        axis.axvline(0.0, color="#aaaaaa", lw=0.7, ls="--")
    axes[0, 0].legend(frameon=False, fontsize=7)
    figure.suptitle(
        f"{spec.env.upper()} {spec.feedback} -- paired attention manipulation on invalid trials "
        f"({spec.focal_magnitude:g}° focal change, cue at S1, forced change away from cue)",
        fontsize=10,
        fontweight="bold",
    )
    figure.text(
        0.5,
        -0.01,
        "Each curve targets the additive key-logit bias at a different location while the trial "
        "itself (cue at S1, physical change forced away from the cue) is held fixed; positive bias "
        "boosts, negative bias suppresses. Error bars omitted for readability; n=300 trials per point "
        "from one checkpoint, not training-seed uncertainty.",
        ha="center",
        fontsize=7.5,
        color="#4C566A",
    )
    summary_path = figures_dir / f"{spec.env}_change_location_intervention_summary"
    figure.savefig(summary_path.with_suffix(".pdf"), bbox_inches="tight")
    figure.savefig(summary_path.with_suffix(".png"), dpi=300, bbox_inches="tight")
    plt.close(figure)

    # trajectory figure: achieved change-location mass over all 7 frames, one panel per role,
    # lines for suppress / natural / boost doses
    trajectory_figure, traj_axes = plt.subplots(1, 3, figsize=(13.2, 4.0), constrained_layout=True, sharey=True)
    highlight_doses = [min(doses_sorted), NATURAL_DOSE, max(doses_sorted)]
    dose_labels = {min(doses_sorted): "full suppress", NATURAL_DOSE: "natural (no clamp)", max(doses_sorted): "full boost"}
    dose_colors = {min(doses_sorted): "#D55E00", NATURAL_DOSE: "#555555", max(doses_sorted): "#009E73"}
    for axis, role in zip(traj_axes, LOCATION_ROLES):
        for dose in highlight_doses:
            mass = results[role][dose]["invalid_mass"][:, :, spec.change_index].mean(axis=0)
            axis.plot(
                np.arange(core.T), mass, color=dose_colors[dose], marker="o", ms=3, lw=1.8,
                label=dose_labels[dose],
            )
        axis.axhline(1.0 / spec.n_locations, color="#aaaaaa", lw=0.7, ls=":")
        axis.set_title(f"target = {role}", fontsize=9)
        axis.set_xlabel("logical timestep")
        axis.grid(alpha=0.2)
    traj_axes[0].set_ylabel("achieved mass at the true change location")
    traj_axes[0].legend(frameon=False, fontsize=7)
    trajectory_figure.suptitle(
        f"{spec.env.upper()} -- attention mass at the true change location over the trial, "
        "by intervention target and dose",
        fontsize=10,
        fontweight="bold",
    )
    trajectory_path = figures_dir / f"{spec.env}_change_location_attention_trajectory"
    trajectory_figure.savefig(trajectory_path.with_suffix(".pdf"), bbox_inches="tight")
    trajectory_figure.savefig(trajectory_path.with_suffix(".png"), dpi=300, bbox_inches="tight")
    plt.close(trajectory_figure)

    return {"summary": summary_path.with_suffix(".pdf"), "trajectory": trajectory_path.with_suffix(".pdf")}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output-root",
        type=Path,
        default=ROOT / "reports/vda_series/change_location_intervention_20260719",
    )
    parser.add_argument("--envs", nargs="*", default=[spec.env for spec in ENV_SPECS])
    args = parser.parse_args()
    args.output_root.mkdir(parents=True, exist_ok=True)

    manifest: dict[str, Any] = {"schema_version": 1, "created_by": str(Path(__file__).resolve()), "environments": {}}
    for spec in ENV_SPECS:
        if spec.env not in args.envs:
            continue
        manifest["environments"][spec.env] = run_environment(spec, args.output_root)

    (args.output_root / "MANIFEST.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"wrote manifest to {args.output_root / 'MANIFEST.json'}")


if __name__ == "__main__":
    main()
