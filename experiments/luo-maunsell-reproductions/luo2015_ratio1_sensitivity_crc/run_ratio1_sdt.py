#!/usr/bin/env python3
"""Frozen-policy SDT assay for ONE freshly trained ratio-1 sensitivity policy.

This is the in-job measurement half of `train_and_measure.slurm`: it runs in the same
Slurm job as the training that produced the checkpoint, so a run never lands as a
trained policy with no behavioural data.

It is a driver, not a new measurement. Every quantity comes from the same functions the
August assay used -- `balanced_trial_bank`, `summarize_policy`, `_location_metrics`,
`_dc` -- so the numbers stay directly comparable. Three things differ, all of them
driver-level:

  * ONE checkpoint per invocation, because one Slurm task trains one policy. The
    counterphased difference-in-differences needs both lineages and is therefore
    computed across runs afterwards by `analyze_did.py`. To make that possible this
    script writes out the per-trial hit/false-alarm indicator arrays, so the DiD
    bootstrap never needs to re-run the model.

  * A DENSE theta grid. The August assay used three common thetas, which exactly
    saturates the equal-variance SDT model and leaves no residual degrees of freedom to
    estimate the variance ratio from. Denser sampling is nearly free -- the same
    rollouts, more conditions -- and it is cheaper to collect now than to re-run.

  * Trial banks are built ONE THETA AT A TIME rather than all upfront. At 2,000 trials
    per location a single bank is ~1.7 GB of float32 video; holding ten of them would
    need ~17 GB. Building one, measuring it, and freeing it keeps the job inside a
    normal memory allocation. The banks are still shared across policies: they are a
    deterministic function of (theta, bank seed), which this script derives identically
    in every run, and `balanced_trial_bank` saves and restores global NumPy state.

The reward table does not enter the measurement. `balanced_trial_bank` renders trial
videos and the policy is read out from `actor_logits_seq`; no reward is consulted. The
ratio-1 change is therefore visible here only through the policy it produced, which is
exactly what we want to measure.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import platform
import sys
import time
from pathlib import Path

import numpy as np
import torch

# Checkpoints may be written under NumPy 2 while this controller runs NumPy 1; unpickling
# them needs the `numpy._core` names to resolve. Install the aliases only if they are
# genuinely missing, and only AFTER importing torch -- registering them beforehand
# segfaults the torch import outright (observed with torch 2.10 / numpy 1.26). Our own
# checkpoints are written and read by the same environment, so this is purely a
# compatibility path for reading externally produced checkpoints.
if "numpy._core" not in sys.modules:
    try:
        import numpy._core  # noqa: F401
    except ImportError:
        sys.modules["numpy._core"] = np.core
        sys.modules["numpy._core.multiarray"] = np.core.multiarray
        sys.modules["numpy._core.numeric"] = np.core.numeric

_TREE = Path(__file__).resolve().parent
if str(_TREE) not in sys.path:
    sys.path.insert(0, str(_TREE))

from experiments.luo2015_episodic.analyze_matrix import balanced_trial_bank
from experiments.luo2015_episodic.evaluate_selected_replication import (
    _location_metrics,
    summarize_policy,
)
from luo2015_analysis import luo2015_core as core

# Spans the measurable range while retaining 38/47/50 -- the three common thetas the
# August assay reported -- so the new runs stay directly comparable at those points.
DEFAULT_THETAS = [12.0, 18.0, 24.0, 30.0, 36.0, 38.0, 42.0, 47.0, 50.0, 56.0]

MEASUREMENT_CONDITIONS = {
    "trained_noise": {"inject_memory_noise": True, "sample_actions": True},
    "zero_mnemonic_noise": {"inject_memory_noise": False, "sample_actions": True},
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def checkpoint_facts(path: Path) -> dict:
    """Record what produced this policy, including the reward table it was trained on."""
    ck = torch.load(path, map_location="cpu", weights_only=False)
    env_state = ck.get("environment_state", {})
    env_cfg = env_state.get("environment_config", {})
    args = ck.get("training_args", {}) or {}
    reward_table = env_cfg.get("reward_table")
    if isinstance(reward_table, dict):
        reward_table = {str(k): list(v) for k, v in reward_table.items()}
    return {
        "path": str(path),
        "sha256": sha256(path),
        "bytes": path.stat().st_size,
        "iter": int(ck.get("iter", -1)),
        "terminal_theta": float(env_state.get("theta", -1)),
        "curriculum": bool(env_state.get("curriculum", False)),
        "curr_threshold": env_state.get("curr_threshold"),
        "curr_step": env_state.get("curr_step"),
        "curr_window": env_state.get("curr_window"),
        "theta_floor": env_state.get("theta_floor"),
        "high_loc": args.get("high_loc", env_cfg.get("condition_loc")),
        # The Step-1 manipulation. Absent on pre-Option-A checkpoints, hence .get().
        "high_hit_cr_ratio": env_cfg.get("high_hit_cr_ratio"),
        "low_hit_cr_ratio": env_cfg.get("low_hit_cr_ratio"),
        "reward_table": reward_table,
        "reward_scale": env_cfg.get("reward_scale", env_state.get("reward_scale")),
        "memory_noise_std": ck.get("model_kwargs", {}).get("memory_noise_std"),
        "d_mem": ck.get("model_kwargs", {}).get("d_mem"),
        "dual_streams": args.get("dual_actor_critic_streams"),
        "gamma": ck.get("ppo_config", {}).get("gamma"),
        "bc_alpha": ck.get("ppo_config", {}).get("bc_alpha"),
        "seed": args.get("seed"),
        "orientation_sampling": env_cfg.get("orientation_sampling"),
        "init_mode": ck.get("initialization_contract", {}).get("mode"),
        "producer_hashes": ck.get("producer_hashes"),
        "run_started_at_utc": ck.get("run_started_at_utc"),
    }


def press_batched(model, videos, batch_size, device, **kwargs) -> np.ndarray:
    out = []
    for start in range(0, len(videos), batch_size):
        chunk = videos[start:start + batch_size].to(device)
        out.append(core.press_times(model, chunk, **kwargs))
    return np.concatenate(out)


def bank_seed_for(theta: float, base: int) -> int:
    """Deterministic per-theta bank seed, identical in every run of the sweep.

    Derived from theta itself rather than its position in the list, so adding or
    removing a theta cannot silently change the bank at any other theta.
    """
    return int(base) + int(round(float(theta) * 1000.0))


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--checkpoint", type=Path, required=True,
                        help="the policy to measure (a .pt file, or a run directory)")
    parser.add_argument("--condition-loc", type=int, required=True, choices=(0, 3),
                        help="the high-value location this lineage was trained with")
    parser.add_argument("--run-id", required=True,
                        help="identifier recorded in the output, e.g. ratio1_loc0_seed42")
    parser.add_argument("--output", type=Path, required=True,
                        help="destination JSON for the per-policy summaries")
    parser.add_argument("--indicators", type=Path, default=None,
                        help="destination .npz for per-trial hit/FA indicators "
                             "(default: alongside --output)")
    parser.add_argument("--thetas", type=float, nargs="+", default=DEFAULT_THETAS)
    parser.add_argument("--trials", type=int, default=2000,
                        help="trials per location per change condition (August used 2000)")
    parser.add_argument("--batch-size", type=int, default=256)
    parser.add_argument("--bootstrap-draws", type=int, default=5000)
    parser.add_argument("--bank-seed", type=int, default=20260902,
                        help="base seed for the SHARED trial banks; must match across the sweep")
    parser.add_argument("--eval-seed", type=int, default=20260902)
    parser.add_argument("--sensory-noise", type=float, default=5.0)
    parser.add_argument("--device", default="cuda")
    args = parser.parse_args(argv)

    device = torch.device(args.device)
    if device.type == "cuda" and not torch.cuda.is_available():
        raise SystemExit("--device cuda requested but CUDA is unavailable")
    core.DEVICE = device

    checkpoint = args.checkpoint
    if checkpoint.is_dir():
        preferred = checkpoint / "rvit_plus_rl_latest.pt"
        candidates = [preferred] if preferred.exists() else sorted(checkpoint.glob("*.pt"))
        if not candidates:
            raise SystemExit(f"no .pt checkpoint found in {checkpoint}")
        checkpoint = candidates[-1]

    facts = checkpoint_facts(checkpoint)
    print("== policy under measurement ==")
    print(f"  {args.run_id}: iter={facts['iter']} terminal_theta={facts['terminal_theta']} "
          f"high_loc={facts['high_loc']} seed={facts['seed']}")
    print(f"  H:CR ratios = {facts['high_hit_cr_ratio']} (high) / "
          f"{facts['low_hit_cr_ratio']} (low)")
    print(f"  reward table = {facts['reward_table']}")
    if facts["high_loc"] is not None and int(facts["high_loc"]) != int(args.condition_loc):
        raise SystemExit(
            f"--condition-loc {args.condition_loc} contradicts the checkpoint's "
            f"high_loc={facts['high_loc']}; refusing to mislabel the lineage"
        )

    model, iteration = core.load_model(str(checkpoint))

    thetas = sorted({float(t) for t in args.thetas})
    print(f"\n== measuring {len(thetas)} thetas x {len(MEASUREMENT_CONDITIONS)} conditions "
          f"@ {args.trials} trials/location ==")

    summaries: list[dict] = []
    indicators: dict[str, np.ndarray] = {}

    for theta in thetas:
        t0 = time.time()
        seed = bank_seed_for(theta, args.bank_seed)
        change_videos, no_change_videos, change_locs, no_change_locs = balanced_trial_bank(
            magnitude=theta,
            trials_per_location=int(args.trials),
            seed=seed,
            task="luo2015_sensitivity",
            noise_multiplier=float(args.sensory_noise),
        )
        build_seconds = time.time() - t0

        for condition_index, (condition, kwargs) in enumerate(MEASUREMENT_CONDITIONS.items()):
            policy_seed = (int(args.eval_seed)
                           + 1000 * (int(facts["seed"]) if facts["seed"] is not None else 0)
                           + 10 * int(round(theta))
                           + condition_index)
            torch.manual_seed(policy_seed)
            if device.type == "cuda":
                torch.cuda.manual_seed_all(policy_seed)

            change_press = press_batched(model, change_videos, args.batch_size, device, **kwargs)
            no_change_press = press_batched(model, no_change_videos, args.batch_size, device, **kwargs)

            summary = summarize_policy(
                change_press, no_change_press, change_locs, no_change_locs,
                condition_loc=int(args.condition_loc), session="sensitivity",
                bootstrap_draws=int(args.bootstrap_draws), bootstrap_seed=policy_seed,
            )
            summary.update({
                "run_id": args.run_id,
                "measurement_condition": condition,
                "evaluation_theta": theta,
                "bank_seed": seed,
                "policy_seed": policy_seed,
                "checkpoint_iteration": iteration,
                "trials_per_location": int(args.trials),
                "claim_scope": "ratio1_sensitivity_dense_theta_shared_bank",
            })
            summaries.append(summary)

            # Per-trial indicators, so the cross-run DiD is pure post-processing.
            for loc in (0, 3):
                _, hit, fa = _location_metrics(
                    np.asarray(change_press), np.asarray(no_change_press),
                    np.asarray(change_locs), np.asarray(no_change_locs), loc)
                key = f"{condition}|theta{theta:g}|loc{loc}"
                indicators[f"{key}|hit"] = np.asarray(hit, dtype=np.uint8)
                indicators[f"{key}|fa"] = np.asarray(fa, dtype=np.uint8)

            contrast = summary["contrasts"]["condition_minus_control"]
            ci = summary["contrasts"]["bootstrap_ci95"]
            print(f"  theta={theta:>5.1f} [{condition:<19}] "
                  f"dd'={contrast['dprime']:+.4f} CI[{ci['dprime'][0]:+.3f},{ci['dprime'][1]:+.3f}]  "
                  f"dc={contrast['criterion']:+.4f} CI[{ci['criterion'][0]:+.3f},{ci['criterion'][1]:+.3f}]"
                  + (f"   (bank {build_seconds:.0f}s)" if condition_index == 0 else ""))

        # Free the bank before building the next one; see the module docstring.
        del change_videos, no_change_videos
        if device.type == "cuda":
            torch.cuda.empty_cache()

    payload = {
        "run_id": args.run_id,
        "condition_loc": int(args.condition_loc),
        "session": "sensitivity",
        "checkpoint_provenance": facts,
        "thetas": thetas,
        "trials_per_location": int(args.trials),
        "bank_seed_base": int(args.bank_seed),
        "eval_seed": int(args.eval_seed),
        "sensory_noise": float(args.sensory_noise),
        "bootstrap_draws": int(args.bootstrap_draws),
        "measurement_conditions": {k: dict(v) for k, v in MEASUREMENT_CONDITIONS.items()},
        "summaries": summaries,
        "environment": {
            "device": str(device),
            "torch": torch.__version__,
            "numpy": np.__version__,
            "python": platform.python_version(),
            "node": platform.node(),
        },
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"\n[assay] summaries -> {args.output}")

    indicator_path = args.indicators or args.output.with_suffix(".indicators.npz")
    indicator_path.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(indicator_path, **indicators)
    print(f"[assay] per-trial indicators -> {indicator_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
