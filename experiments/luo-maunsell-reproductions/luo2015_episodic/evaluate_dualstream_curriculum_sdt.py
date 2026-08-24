#!/usr/bin/env python
"""Matched SDT assay for mixed-phase dual-stream Luo sensitivity checkpoints.

Primary branches evaluate each frozen checkpoint at its own terminal theta. A
separate common-theta branch is explicitly a difficulty-transfer comparison.
All policy actions are sampled; the primary branch retains trained mnemonic
noise. No optimizer, replay, or environment curriculum update is executed.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

import numpy as np

# Checkpoints were produced with NumPy 2 while this controller uses NumPy 1.
sys.modules.setdefault("numpy._core", np.core)
sys.modules.setdefault("numpy._core.multiarray", np.core.multiarray)
sys.modules.setdefault("numpy._core.numeric", np.core.numeric)

import torch

_REPO = Path(__file__).resolve().parents[2]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from experiments.luo2015_episodic.analyze_matrix import balanced_trial_bank
from experiments.luo2015_episodic.evaluate_latest_full_battery import (
    _evaluate_bank,
    _press_on_device,
    _seed_policy,
    counterphased_did,
    evaluation_conditions,
)
from experiments.luo2015_episodic.evaluate_selected_replication import validate_checkpoint
from luo2015_analysis import luo2015_core as core


def evaluation_plan(models: list[dict], *, common_theta: float) -> dict:
    return {
        "matched_frozen_policy": {
            str(model["id"]): {
                "theta": float(model["terminal_theta"]),
                "conditions": ["trained_noise", "zero_mnemonic_noise"],
                "claim_scope": "contract_matched_terminal_difficulty",
            }
            for model in models
        },
        "common_theta_transfer": {
            "theta": float(common_theta),
            "conditions": ["trained_noise"],
            "claim_scope": "difficulty_transfer_not_contract_matched_for_every_model",
        },
    }


def validate_curriculum_checkpoint(path: Path, spec: dict, contract: dict) -> dict:
    provenance = validate_checkpoint(path, spec, contract)
    checkpoint = torch.load(path, map_location="cpu", weights_only=False)
    environment_state = checkpoint["environment_state"]
    arguments = checkpoint["training_args"]
    ppo = checkpoint["ppo_config"]
    environment = environment_state["environment_config"]
    checks = {
        "curriculum": environment_state.get("curriculum") is True,
        "terminal_theta": float(environment_state.get("theta", -1)) == float(spec["terminal_theta"]),
        "curriculum_window": int(environment_state.get("curr_window", -1)) == 1000,
        "curriculum_threshold": float(environment_state.get("curr_threshold", -1)) == 0.85,
        "curriculum_step": float(environment_state.get("curr_step", -1)) == 3.0,
        "curriculum_floor": float(environment_state.get("theta_floor", -1)) == 8.0,
        "dual_stream": arguments.get("dual_actor_critic_streams") is True,
        "bc_disabled": float(ppo.get("bc_alpha", -1)) == 0.0,
        "orientation_sampling": environment.get("orientation_sampling") == "independent_uniform_axial_0_180",
        "orientation_period": float(environment.get("orientation_period_degrees", -1)) == 180.0,
    }
    failed = sorted(name for name, passed in checks.items() if not passed)
    if failed:
        raise RuntimeError(f"curriculum checkpoint contract failed for {spec['id']}: {failed}")
    return {**provenance, "curriculum_contract": checks,
            "terminal_theta": float(environment_state["theta"]),
            "transition_parent_iteration": int(spec["transition_parent_iteration"])}


def build_bank(theta: float, n: int, seed: int, sensory_noise: float):
    return balanced_trial_bank(
        magnitude=float(theta), trials_per_location=int(n), seed=int(seed),
        task="luo2015_sensitivity", noise_multiplier=float(sensory_noise),
        spatial_grid_size=2,
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--checkpoint-root", type=Path, default=None)
    parser.add_argument("--device", default="cuda")
    parser.add_argument("--trials-per-status-per-location", type=int, default=None)
    parser.add_argument("--batch-size", type=int, default=256)
    parser.add_argument("--bootstrap-draws", type=int, default=5000)
    args = parser.parse_args(argv)

    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    contract = manifest["evaluation_contract"]
    models = manifest["models"]
    n = args.trials_per_status_per_location or int(contract["primary_trials_per_status_per_location"])
    common_theta = float(contract["common_theta_transfer"])
    seed = int(contract["evaluation_seed"])
    sensory_noise = float(contract["sensory_orientation_noise_sd"])
    device = torch.device(args.device)
    if device.type == "cuda" and not torch.cuda.is_available():
        raise RuntimeError("PyTorch CUDA unavailable")
    core.DEVICE = device
    args.output_dir.mkdir(parents=True, exist_ok=True)
    press = _press_on_device(device)
    plan = evaluation_plan(models, common_theta=common_theta)
    common_bank = build_bank(common_theta, n, seed + 50_000, sensory_noise)

    matched = {condition: [] for condition in evaluation_conditions()}
    common_results: list[dict] = []
    for model_index, spec in enumerate(models):
        checkpoint = (args.checkpoint_root / f"{spec['id']}.pt"
                      if args.checkpoint_root is not None else Path(spec["checkpoint"]))
        provenance = validate_curriculum_checkpoint(checkpoint, spec, contract)
        model, iteration = core.load_model(str(checkpoint))
        matched_bank = build_bank(float(spec["terminal_theta"]), n, seed, sensory_noise)

        for condition_index, (condition, kwargs) in enumerate(evaluation_conditions().items()):
            policy_seed = seed + model_index * 100 + condition_index
            _seed_policy(policy_seed, device)
            summary, raw = _evaluate_bank(
                model, matched_bank, condition_loc=int(spec["condition_loc"]),
                session="sensitivity", batch_size=args.batch_size,
                bootstrap_draws=args.bootstrap_draws, bootstrap_seed=policy_seed,
                press=press, kwargs=kwargs,
            )
            summary.update({
                "id": spec["id"], "task": spec["task"], "gamma": spec["gamma"],
                "checkpoint": str(checkpoint), "checkpoint_iteration": iteration,
                "checkpoint_provenance": provenance, "policy_seed": policy_seed,
                "measurement_condition": condition, "evaluation_theta": float(spec["terminal_theta"]),
                "claim_scope": "matched_frozen_policy_measurement",
            })
            matched[condition].append(summary)
            np.savez_compressed(args.output_dir / f"{spec['id']}_{condition}_matched_outcomes.npz", **raw)

        common_kwargs = evaluation_conditions()["trained_noise"]
        common_seed = seed + 10_000 + model_index
        _seed_policy(common_seed, device)
        summary, raw = _evaluate_bank(
            model, common_bank, condition_loc=int(spec["condition_loc"]),
            session="sensitivity", batch_size=args.batch_size,
            bootstrap_draws=args.bootstrap_draws, bootstrap_seed=common_seed,
            press=press, kwargs=common_kwargs,
        )
        summary.update({
            "id": spec["id"], "task": spec["task"], "gamma": spec["gamma"],
            "checkpoint": str(checkpoint), "checkpoint_iteration": iteration,
            "checkpoint_provenance": provenance, "policy_seed": common_seed,
            "measurement_condition": "trained_noise_common_theta_transfer",
            "evaluation_theta": common_theta,
            "claim_scope": "difficulty_transfer_not_contract_matched_for_every_model",
        })
        common_results.append(summary)
        np.savez_compressed(args.output_dir / f"{spec['id']}_trained_noise_common56_transfer_outcomes.npz", **raw)
        del model
        if device.type == "cuda": torch.cuda.empty_cache()

    common_effects = {
        "sensitivity_dprime_did": counterphased_did(common_results, "sensitivity", "dprime"),
        "sensitivity_criterion_cross_did": counterphased_did(common_results, "sensitivity", "criterion"),
    }
    output = {
        "schema_version": 1, "design": manifest["design"],
        "claim_scope": manifest["claim_scope"], "paper_targets": manifest["paper_targets"],
        "evaluation_plan": plan,
        "evaluation_contract": {**contract, "device": str(device),
                                "primary_trials_per_status_per_location": n,
                                "bootstrap_draws": args.bootstrap_draws,
                                "policy_action_semantics": "sampled_categorical"},
        "matched_frozen_policy": matched,
        "common_theta_transfer": {"theta": common_theta, "models": common_results,
                                  "counterphased_effects": common_effects},
    }
    result_path = args.output_dir / "dualstream_curriculum_sdt_results.json"
    result_path.write_text(json.dumps(output, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(result_path)
    for condition, rows in matched.items():
        for row in rows:
            contrast = row["contrasts"]["condition_minus_control"]
            print(condition, row["id"], f"theta={row['evaluation_theta']}",
                  f"delta_dprime={contrast['dprime']:.4f}",
                  f"delta_c={contrast['criterion']:.4f}",
                  f"strict={row['paper_like_tests']['strict_behavioral_dissociation']}")
    print("common_theta_transfer", json.dumps(common_effects, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
