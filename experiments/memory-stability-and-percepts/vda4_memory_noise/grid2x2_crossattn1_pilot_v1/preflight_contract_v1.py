#!/usr/bin/env python3
"""Fail-closed preflight for the paired native-2x2 VDA4 memory-noise pilot."""
from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import re
import sys
from datetime import datetime, timezone
from typing import Any


NOISE_LEVELS = (0.0, 0.5)
SEEDS = (0,)
EXPECTED_DESIGN_ID = "vda4_grid2x2_crossattn1_memory_noise_seed0_paired_pilot_v1"
EXPECTED_PARAMETERS = 2_209_476
EXPECTED_TOKENS = 4
EXPECTED_TOKEN_WIDTH = 140
EXPECTED_READOUT_DIM = 512
RUN_CONTRACTS = {
    "canary": {
        "launcher": "launch_canary_v1.sh",
        "iterations": 50,
        "terminal_iteration": 49,
        "allowed_seeds": SEEDS,
    },
    "production": {
        "launcher": "launch_production_v1.sh",
        "iterations": 20_000,
        "terminal_iteration": 19_999,
        "allowed_seeds": SEEDS,
    },
}

STATIC_LAUNCH_FRAGMENTS = (
    '--config "$CONFIG"',
    "--task vda4",
    "--T 7",
    "--frame-repeat 1",
    "--min-change-time 5",
    "--max-change-time 5",
    "--noise 5.0",
    "--patch-grid-rows 2",
    "--patch-grid-cols 2",
    "--cell xlstm",
    "--feedback crossattn1",
    "--d-mem 128",
    "--memory-decay 1.0",
    '--memory-noise-std "$MEMORY_NOISE_STD"',
    "--conv-frontend",
    "--n-actions 2",
    "--n-quantiles 5",
    "--init-action-bias 0.0 -1.5",
    "--jepa-coef 0.5",
    "--jepa-heads 4",
    "--jepa-proto-dim 256",
    "--jepa-tau-student 0.1",
    "--jepa-tau-teacher-start 0.04",
    "--jepa-tau-teacher-end 0.07",
    "--jepa-tau-warmup 300",
    "--jepa-center-momentum 0.9",
    "--jepa-ema-decay 0.996",
    "--curriculum",
    "--theta-start 65.0",
    "--curr-window 1000",
    "--curr-threshold 0.85",
    "--curr-step 3.0",
    "--curr-floor 8.0",
    "--lr 0.0003",
    "--gamma 0.95",
    "--entropy-coef 0.01",
    "--ema-decay 0.995",
    "--buffer-capacity 1000",
    "--qr-kappa 1.0",
    "--mpo-temperature 0.1",
    "--init-mode fresh",
    "--start-iteration 0",
    "--schedule-final-iteration 19999",
    "--episodes-per-iter 8",
    "--save-every 50",
    "--log-every 1",
    '--seed "$SEED"',
    "--device cuda",
    '--experiment-launcher "$LAUNCHER"',
)

FORBIDDEN_LAUNCH_FRAGMENTS = (
    "--checkpoint-path",
    "--expected-parent-sha256",
    "--allow-schedule-overrun-resume",
    "--two-lstm",
    "--jepa-same-time",
    "--effective-visual-streams",
    "--effective-memory-streams",
    "${ITERS:-",
    "${SEED:-",
    "${MEMORY_NOISE_STD:-",
    "${SCHEDULE_FINAL_ITERATION:-",
    "${EPISODES_PER_ITER:-",
)


def fail(message: str) -> None:
    raise SystemExit(f"PREFLIGHT_FAIL: {message}")


def sha256(path: pathlib.Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def canonical_sha256(payload: Any) -> str:
    rendered = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    ).encode("utf-8")
    return hashlib.sha256(rendered).hexdigest()


def _as_builtin(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): _as_builtin(item) for key, item in value.items()}
    if isinstance(value, (tuple, list)):
        return [_as_builtin(item) for item in value]
    if hasattr(value, "item"):
        return _as_builtin(value.item())
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    return str(value)


def _require_mapping_value(mapping: dict[str, Any], dotted_key: str, expected: Any) -> None:
    current: Any = mapping
    for component in dotted_key.split("."):
        if not isinstance(current, dict) or component not in current:
            fail(f"config missing {dotted_key!r}")
        current = current[component]
    if current != expected:
        fail(f"config {dotted_key!r}: expected {expected!r}, got {current!r}")


def validate_request(memory_noise_std: float, seed: int, run_kind: str) -> dict[str, Any]:
    if memory_noise_std not in NOISE_LEVELS:
        fail(f"memory-noise level must be one of {NOISE_LEVELS}; got {memory_noise_std}")
    if run_kind not in RUN_CONTRACTS:
        fail(f"run kind must be one of {tuple(RUN_CONTRACTS)}; got {run_kind!r}")
    contract = RUN_CONTRACTS[run_kind]
    if seed not in contract["allowed_seeds"]:
        fail(
            f"seed {seed} is not admitted for {run_kind}; "
            f"allowed={contract['allowed_seeds']}"
        )
    return contract


def validate_config(config: dict[str, Any], design_sha256: str) -> None:
    checks = {
        "contract.schema_version": 1,
        "contract.id": EXPECTED_DESIGN_ID,
        "contract.design_manifest_sha256": design_sha256,
        "contract.task": "vda4",
        "contract.active_items": 4,
        "contract.stimulus_grid": [2, 2],
        "contract.patch_memory_grid": [2, 2],
        "contract.tokens": 4,
        "contract.image_size": 50,
        "contract.feedback": "crossattn1",
        "contract.memory_noise_std_levels": [0.0, 0.5],
        "contract.seeds": [0],
        "run.init_mode": "fresh",
        "run.seed": 0,
        "run.device": "cuda",
        "run.log_every": 1,
        "run.save_every": 50,
        "environment.T": 7,
        "environment.frame_repeat": 1,
        "environment.min_change_time": 5,
        "environment.max_change_time": 5,
        "environment.noise_multiplier": 5.0,
        "environment.theta_start": 65.0,
        "environment.curriculum": True,
        "environment.curr_window": 1000,
        "environment.curr_threshold": 0.85,
        "environment.curr_step": 3.0,
        "environment.theta_floor": 8.0,
        "model.cell": "xlstm",
        "model.feedback": "crossattn1",
        "model.d_mem": 128,
        "model.memory_decay": 1.0,
        "model.memory_noise_std_levels": [0.0, 0.5],
        "model.conv_frontend": True,
        "model.rl.n_actions": 2,
        "model.rl.n_quantiles": 5,
        "model.rl.init_action_bias": [0.0, -1.5],
        "ppo.iters": 20_000,
        "ppo.episodes_per_iter": 8,
        "ppo.lr": 0.0003,
        "ppo.n_epochs": 4,
        "ppo.grad_clip": 0.5,
        "ppo.value_coef": 0.5,
        "ppo.entropy_coef": 0.01,
        "ppo.qr_kappa": 1.0,
        "ppo.gamma": 0.95,
        "ppo.mpo_temperature": 0.1,
        "ppo.bc_alpha": 0.1,
        "ppo.target_update_period": 0,
        "ppo.ema_decay": 0.995,
        "ppo.burn_in_iters": 20,
        "ppo.buffer_capacity": 1000,
        "ppo.per_n_replay": 4,
        "ppo.per_alpha": 0.6,
        "ppo.per_beta_start": 0.4,
        "ppo.per_beta_end": 1.0,
        "ppo.per_priority_clip": 50.0,
        "jepa.coef": 0.5,
        "jepa.heads": 4,
        "jepa.proto_dim": 256,
        "jepa.temporal": True,
        "jepa.tau_student": 0.1,
        "jepa.tau_teacher_start": 0.04,
        "jepa.tau_teacher_end": 0.07,
        "jepa.tau_warmup": 300,
        "jepa.center_momentum": 0.9,
        "jepa.ema_decay": 0.996,
    }
    for dotted_key, expected in checks.items():
        _require_mapping_value(config, dotted_key, expected)


def validate_launcher(
    launcher_path: pathlib.Path, run_kind: str, expected_hashes: dict[str, str]
) -> None:
    contract = RUN_CONTRACTS[run_kind]
    if launcher_path.name != contract["launcher"]:
        fail(
            f"launcher/run-kind mismatch: {run_kind} requires {contract['launcher']}, "
            f"got {launcher_path.name}"
        )
    text = launcher_path.read_text(encoding="utf-8")
    normalized = re.sub(r"\\\s*\n\s*", " ", text)
    for fragment in STATIC_LAUNCH_FRAGMENTS:
        if fragment not in normalized:
            fail(f"launcher missing exact fragment: {fragment}")
    if f"--iters {contract['iterations']}" not in normalized:
        fail(f"launcher does not freeze --iters {contract['iterations']}")
    for fragment in FORBIDDEN_LAUNCH_FRAGMENTS:
        if fragment in text:
            fail(f"launcher contains forbidden resume/override fragment: {fragment}")
    for fragment in (
        '[[ "$#" -eq 2 ]]',
        'MEMORY_NOISE_STD="$1"',
        'SEED="$2"',
        'case "$MEMORY_NOISE_STD" in 0.0|0.5)',
        '[[ "$SEED" == "0" ]]',
        ': "${VDA_PAIR_ID:',
        ': "${VDA_PAIR_RUNTIME_SHA256:',
        f"--run-kind {run_kind}",
        f'EXPECTED_CONFIG_SHA256="{expected_hashes["config"]}"',
        f'EXPECTED_DESIGN_SHA256="{expected_hashes["design"]}"',
    ):
        if fragment not in text:
            fail(f"launcher missing positional/hash/pair guard: {fragment}")


def initial_environment_reset_diagnostic(
    root: pathlib.Path, seed: int, trial_count: int
) -> str:
    import numpy as np  # pylint: disable=import-outside-toplevel

    sys.path.insert(0, str(root))
    from envs import make_env  # pylint: disable=import-outside-toplevel

    np.random.seed(seed)
    env = make_env(
        "vda4",
        T=7,
        frame_repeat=1,
        min_change_time=5,
        max_change_time=5,
        noise_multiplier=5.0,
        curriculum=True,
        theta=65.0,
        curr_window=1000,
        curr_threshold=0.85,
        curr_step=3.0,
        theta_floor=8.0,
    )
    trace = []
    for _ in range(trial_count):
        observation = env.reset()
        if tuple(observation.shape) != (50, 50, 3) or int(env.n_stim) != 4:
            fail("VDA4 reset did not realize the registered 50x50 four-item scene")
        trace.append(
            _as_builtin(
                {
                    "cue_index": env.cue_index,
                    "change_true": env.change_true,
                    "change_index": env.change_index,
                    "change_time": env.change_time,
                    "proportion": env.proportion,
                    "cue_color": env.cue_color,
                    "orientation_change": env.orientation_change,
                    "orientations": env.orientations,
                }
            )
        )
    return canonical_sha256(trace)


def named_trainable_sha256(model: Any) -> str:
    digest = hashlib.sha256()
    for name, parameter in model.named_parameters():
        if not parameter.requires_grad:
            continue
        tensor = parameter.detach().cpu().contiguous()
        digest.update(name.encode("utf-8"))
        digest.update(str(tensor.dtype).encode("ascii"))
        digest.update(json.dumps(list(tensor.shape), separators=(",", ":")).encode("ascii"))
        digest.update(tensor.numpy().tobytes(order="C"))
    return digest.hexdigest()


def _build_model(root: pathlib.Path, noise_std: float, seed: int) -> Any:
    sys.path.insert(0, str(root))
    from model import RViTPaperModel  # pylint: disable=import-outside-toplevel
    from train_rl import seed_training_rngs  # pylint: disable=import-outside-toplevel

    seed_training_rngs(seed)
    return RViTPaperModel(
        n_actions=2,
        n_quantiles=5,
        init_action_bias=[0.0, -1.5],
        seq_len=7,
        feedback="crossattn1",
        two_lstm=False,
        cell="xlstm",
        mem_heads=4,
        vae_in_channels=1,
        jepa_n_heads=4,
        jepa_proto_dim=256,
        frame_repeat=1,
        d_mem=128,
        memory_decay=1.0,
        memory_noise_std=noise_std,
        conv_frontend=True,
        grid_rows=2,
        grid_cols=2,
        image_size=50,
    )


def _validate_noise_semantics(models: dict[float, Any]) -> dict[str, Any]:
    import torch  # pylint: disable=import-outside-toplevel

    model0 = models[0.0]
    model5 = models[0.5]
    batch = 3
    torch.manual_seed(2026080305)
    z = torch.randn(batch, EXPECTED_TOKENS, EXPECTED_TOKEN_WIDTH)
    zeros = tuple(
        torch.zeros(batch, EXPECTED_TOKENS, 128)
        for _ in range(4)
    )
    with torch.no_grad():
        out0 = model0.encoder.lstm(z, *zeros, inject_memory_noise=True)
        out5_off = model5.encoder.lstm(z, *zeros, inject_memory_noise=False)
        torch.manual_seed(2026080306)
        out5_a = model5.encoder.lstm(z, *zeros, inject_memory_noise=True)
        torch.manual_seed(2026080306)
        out5_b = model5.encoder.lstm(z, *zeros, inject_memory_noise=True)
        torch.manual_seed(2026080307)
        out5_c = model5.encoder.lstm(z, *zeros, inject_memory_noise=True)
    deterministic_c = out0[1]
    if not torch.equal(deterministic_c, out5_off[1]):
        fail("noise level changes the deterministic cell update even when injection is disabled")
    if not torch.equal(out5_a[1], out5_b[1]):
        fail("memory-noise draw is not reproducible after resetting the torch RNG")
    if torch.equal(out5_a[1], out5_c[1]):
        fail("memory-noise draw does not change under a different torch RNG seed")
    residual = out5_a[1] - deterministic_c
    if not torch.isfinite(residual).all() or torch.count_nonzero(residual).item() == 0:
        fail("std=0.5 memory-noise injection produced no finite destructive interference")
    normalized = residual / (0.5 * (out5_a[2] + 1e-8))
    if float(normalized.std(unbiased=False)) <= 0.1:
        fail("std=0.5 residual does not vary independently across state elements")
    return {
        "noise0_injection_is_noop": True,
        "noise0p5_disabled_matches_noise0": True,
        "noise0p5_reproducible_after_rng_reset": True,
        "noise0p5_changes_with_rng_seed": True,
        "normalized_residual_mean": float(normalized.mean()),
        "normalized_residual_std": float(normalized.std(unbiased=False)),
        "checked_state_elements": int(normalized.numel()),
    }


def run_preflight(args: argparse.Namespace) -> dict[str, Any]:
    contract = validate_request(args.memory_noise_std, args.seed, args.run_kind)
    root = args.project_root.resolve()
    config_path = args.config.resolve()
    design_path = args.design.resolve()
    launcher_path = args.launcher.resolve()
    preflight_path = pathlib.Path(__file__).resolve()
    for path in (root / "train_rl.py", config_path, design_path, launcher_path, preflight_path):
        if not path.is_file():
            fail(f"missing required file: {path}")

    actual_config_sha = sha256(config_path)
    actual_design_sha = sha256(design_path)
    if actual_config_sha != args.expected_config_sha256.lower():
        fail(
            f"config SHA-256 mismatch: expected {args.expected_config_sha256}, "
            f"got {actual_config_sha}"
        )
    if actual_design_sha != args.expected_design_sha256.lower():
        fail(
            f"design SHA-256 mismatch: expected {args.expected_design_sha256}, "
            f"got {actual_design_sha}"
        )

    config = json.loads(config_path.read_text(encoding="utf-8"))
    design = json.loads(design_path.read_text(encoding="utf-8"))
    if design.get("schema_version") != 1 or design.get("design_id") != EXPECTED_DESIGN_ID:
        fail("design manifest identity/schema mismatch")
    if design.get("status") != "paired_pilot_contract_prepared_not_launched":
        fail("design status is not the frozen pre-launch state")
    validate_config(config, actual_design_sha)
    validate_launcher(
        launcher_path,
        args.run_kind,
        {"config": actual_config_sha, "design": actual_design_sha},
    )

    required_sources = design.get("source_contract", {}).get("required_sha256", {})
    if not isinstance(required_sources, dict) or not required_sources:
        fail("design lacks frozen source SHA-256 inventory")
    source_checks: dict[str, str] = {}
    for identity, expected in required_sources.items():
        path = root / identity
        if not path.is_file():
            fail(f"missing frozen source: {identity}")
        actual = sha256(path)
        if actual != expected:
            fail(f"frozen source SHA-256 mismatch for {identity}: {actual} != {expected}")
        source_checks[identity] = actual

    sys.path.insert(0, str(root))
    from envs import task_grid  # pylint: disable=import-outside-toplevel
    from train_rl import _producer_hashes, resolve_patch_grid  # pylint: disable=import-outside-toplevel

    if list(task_grid("vda4")) != [2, 2]:
        fail("task registry is not the native VDA4 2x2 geometry")
    if list(resolve_patch_grid("vda4", 2, 2)) != [2, 2]:
        fail("resolved patch/memory grid is not native 2x2")

    models = {level: _build_model(root, level, args.seed) for level in NOISE_LEVELS}
    trainable_hashes: dict[str, str] = {}
    model_checks: dict[str, Any] = {}
    for level, model in models.items():
        total = sum(parameter.numel() for parameter in model.parameters())
        trainable = sum(
            parameter.numel() for parameter in model.parameters() if parameter.requires_grad
        )
        if total != EXPECTED_PARAMETERS or trainable != EXPECTED_PARAMETERS:
            fail(
                f"parameter-count mismatch for noise={level}: all={total}, trainable={trainable}"
            )
        if (
            model.n_tokens != EXPECTED_TOKENS
            or model.front.token_dim != EXPECTED_TOKEN_WIDTH
            or model.encoder.readout_dim != EXPECTED_READOUT_DIM
        ):
            fail(f"native token/token-width/readout shape mismatch for noise={level}")
        if model.encoder.memory_decay != 1.0 or model.encoder.memory_noise_std != level:
            fail(f"model does not expose the requested memory contract for noise={level}")
        condition = "noise0p0" if level == 0.0 else "noise0p5"
        trainable_hashes[condition] = named_trainable_sha256(model)
        model_checks[condition] = {
            "memory_noise_std": level,
            "parameters": total,
            "trainable_parameters": trainable,
            "tokens": model.n_tokens,
            "token_width": model.front.token_dim,
            "readout_dim": model.encoder.readout_dim,
        }
    if len(set(trainable_hashes.values())) != 1:
        fail(f"paired levels do not have identical fresh initialization: {trainable_hashes}")
    noise_semantics = _validate_noise_semantics(models)

    trace_spec = design.get("initial_environment_reset_diagnostic", {})
    actual_trace = initial_environment_reset_diagnostic(
        root, args.seed, int(trace_spec.get("trial_count", 0))
    )
    if actual_trace != trace_spec.get("expected_sha256"):
        fail(
            f"initial environment reset diagnostic mismatch: "
            f"expected {trace_spec.get('expected_sha256')}, "
            f"got {actual_trace}"
        )

    producer_hashes = _producer_hashes(str(config_path), str(launcher_path))
    required_producer_keys = {
        "train_rl.py",
        "ppo.py",
        "model.py",
        "paper_encoder.py",
        "paper_heads.py",
        "conv_frontend.py",
        "envs/base.py",
        "envs/luo2015.py",
        "envs/tasks.py",
        "envs/__init__.py",
        "config/loader.py",
        "resolved_config",
        "experiment_launcher",
    }
    if not required_producer_keys.issubset(producer_hashes):
        fail(
            "producer hash set is incomplete: "
            f"{sorted(required_producer_keys - set(producer_hashes))}"
        )
    if producer_hashes["resolved_config"] != actual_config_sha:
        fail("train_rl producer config hash mismatch")
    if producer_hashes["experiment_launcher"] != sha256(launcher_path):
        fail("train_rl producer launcher hash mismatch")
    for identity, digest in source_checks.items():
        if producer_hashes.get(identity) != digest:
            fail(f"train_rl producer source hash mismatch for {identity}")

    request_condition = "noise0p0" if args.memory_noise_std == 0.0 else "noise0p5"
    return {
        "schema_version": 1,
        "status": "preflight_passed",
        "checked_at_utc": datetime.now(timezone.utc).isoformat(),
        "evidence_class": (
            "engineering_only_not_scientific_evidence"
            if args.run_kind == "canary"
            else "scientific_only_after_terminal_and_heldout_validation"
        ),
        "request": {
            "condition_id": request_condition,
            "memory_noise_std": args.memory_noise_std,
            "seed": args.seed,
            "run_kind": args.run_kind,
            "iterations": contract["iterations"],
            "terminal_iteration": contract["terminal_iteration"],
        },
        "project_root": str(root),
        "config": str(config_path),
        "design": str(design_path),
        "launcher": str(launcher_path),
        "preflight": str(preflight_path),
        "run_dir": str(args.run_dir.resolve()) if args.run_dir else None,
        "sha256": {
            "config": actual_config_sha,
            "design": actual_design_sha,
            "launcher": sha256(launcher_path),
            "preflight": sha256(preflight_path),
            "trainable_initialization": trainable_hashes[request_condition],
            "initial_environment_reset_diagnostic": actual_trace,
        },
        "paired_trainable_initialization_sha256_by_condition": trainable_hashes,
        "model_checks_by_condition": model_checks,
        "noise_semantics": noise_semantics,
        "source_sha256": source_checks,
        "producer_sha256": producer_hashes,
        "pairing_requirement": design.get("pairing_contract"),
        "evidence_boundaries": design.get("evidence_boundaries"),
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", type=pathlib.Path, required=True)
    parser.add_argument("--config", type=pathlib.Path, required=True)
    parser.add_argument("--design", type=pathlib.Path, required=True)
    parser.add_argument("--launcher", type=pathlib.Path, required=True)
    parser.add_argument("--expected-config-sha256", required=True)
    parser.add_argument("--expected-design-sha256", required=True)
    parser.add_argument(
        "--memory-noise-std", type=float, choices=NOISE_LEVELS, required=True
    )
    parser.add_argument("--seed", type=int, choices=SEEDS, required=True)
    parser.add_argument("--run-kind", choices=tuple(RUN_CONTRACTS), required=True)
    parser.add_argument("--run-dir", type=pathlib.Path)
    parser.add_argument("--emit-json", action="store_true")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    result = run_preflight(args)
    if args.emit_json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        request = result["request"]
        print(
            "PREFLIGHT_PASS|design="
            f"{EXPECTED_DESIGN_ID}|run_kind={request['run_kind']}|"
            f"memory_noise_std={request['memory_noise_std']}|seed={request['seed']}|"
            "grid=2x2|active=4|feedback=crossattn1|d_mem=128|decay=1|fresh"
        )


if __name__ == "__main__":
    main()
