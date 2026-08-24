#!/usr/bin/env python3
"""Fail-closed preflight for the production-v1 cross-attention stream factorial."""
from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import re
import sys
from datetime import datetime, timezone
from typing import Any


LEVELS = (4, 100)
SEEDS = (0, 1, 2)
CELLS = ((4, 4), (4, 100), (100, 4), (100, 100))
EXPECTED_PARAMETERS = 8_682_948
EXPECTED_TOKEN_WIDTH = 236
EXPECTED_READOUT_DIM = 12_800
EXPECTED_CARRIER_TOKENS = 100
EXPECTED_DESIGN_ID = "vda4_stream_factorial_crossattn1_production_v1"
RUN_CONTRACTS = {
    "canary": {
        "launcher": "launch_crossattn1_canary_v1.sh",
        "iterations": 50,
        "terminal_iteration": 49,
        "allowed_seeds": (0,),
    },
    "production": {
        "launcher": "launch_crossattn1_production_v1.sh",
        "iterations": 20_000,
        "terminal_iteration": 19_999,
        "allowed_seeds": SEEDS,
    },
}

STATIC_LAUNCH_FRAGMENTS = (
    "--config \"$CONFIG\"",
    "--task vda4",
    "--T 7",
    "--frame-repeat 1",
    "--min-change-time 5",
    "--max-change-time 5",
    "--noise 5.0",
    "--patch-grid-rows 10",
    "--patch-grid-cols 10",
    "--effective-visual-streams \"$VISUAL_STREAMS\"",
    "--effective-memory-streams \"$MEMORY_STREAMS\"",
    "--cell xlstm",
    "--feedback crossattn1",
    "--d-mem 128",
    "--memory-decay 1.0",
    "--memory-noise-std 0.0",
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
    "--seed \"$SEED\"",
    "--device cuda",
    "--experiment-launcher \"$LAUNCHER\"",
)

FORBIDDEN_LAUNCH_FRAGMENTS = (
    "--checkpoint-path",
    "--expected-parent-sha256",
    "--allow-schedule-overrun-resume",
    "--two-lstm",
    "--jepa-same-time",
    "${ITERS:-",
    "${SEED:-",
    "${VISUAL_STREAMS:-",
    "${MEMORY_STREAMS:-",
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


def validate_request(visual: int, memory: int, seed: int, run_kind: str) -> dict[str, Any]:
    if visual not in LEVELS:
        fail(f"visual stream level must be one of {LEVELS}; got {visual}")
    if memory not in LEVELS:
        fail(f"memory stream level must be one of {LEVELS}; got {memory}")
    if run_kind not in RUN_CONTRACTS:
        fail(f"run kind must be one of {tuple(RUN_CONTRACTS)}; got {run_kind!r}")
    contract = RUN_CONTRACTS[run_kind]
    if seed not in contract["allowed_seeds"]:
        fail(
            f"seed {seed} is not admitted for {run_kind}; "
            f"allowed={contract['allowed_seeds']}"
        )
    return contract


def environment_rng_trace(root: pathlib.Path, seed: int, trial_count: int) -> str:
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
        env.reset()
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


def named_trainable_sha256(model) -> str:
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


def _require_mapping_value(mapping: dict[str, Any], dotted_key: str, expected: Any) -> None:
    current: Any = mapping
    for component in dotted_key.split("."):
        if not isinstance(current, dict) or component not in current:
            fail(f"config missing {dotted_key!r}")
        current = current[component]
    if current != expected:
        fail(f"config {dotted_key!r}: expected {expected!r}, got {current!r}")


def validate_config(config: dict[str, Any], design_sha256: str) -> None:
    checks = {
        "contract.schema_version": 1,
        "contract.id": EXPECTED_DESIGN_ID,
        "contract.task": "vda4",
        "contract.active_items": 4,
        "contract.stimulus_grid": [2, 2],
        "contract.carrier_grid": [10, 10],
        "contract.carrier_tokens": 100,
        "contract.image_size": 50,
        "contract.feedback": "crossattn1",
        "contract.effective_visual_streams": [4, 100],
        "contract.effective_memory_streams": [4, 100],
        "contract.seeds": [0, 1, 2],
        "contract.design_manifest_sha256": design_sha256,
        "run.init_mode": "fresh",
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
        "model.memory_noise_std": 0.0,
        "model.conv_frontend": True,
        "model.rl.n_actions": 2,
        "model.rl.n_quantiles": 5,
        "model.rl.init_action_bias": [0.0, -1.5],
        "ppo.iters": 20000,
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


def validate_launcher(launcher_path: pathlib.Path, run_kind: str, expected_hashes: dict[str, str]) -> None:
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
        '[[ "$#" -eq 3 ]]',
        'VISUAL_STREAMS="$1"',
        'MEMORY_STREAMS="$2"',
        'SEED="$3"',
        f'--run-kind {run_kind}',
        f'EXPECTED_CONFIG_SHA256="{expected_hashes["config"]}"',
        f'EXPECTED_DESIGN_SHA256="{expected_hashes["design"]}"',
    ):
        if fragment not in text:
            fail(f"launcher missing positional/hash guard: {fragment}")


def run_preflight(args: argparse.Namespace) -> dict[str, Any]:
    contract = validate_request(
        args.visual_streams, args.memory_streams, args.seed, args.run_kind
    )
    root = args.project_root.resolve()
    config_path = args.config.resolve()
    design_path = args.design.resolve()
    launcher_path = args.launcher.resolve()
    preflight_path = pathlib.Path(__file__).resolve()
    required = (
        root / "train_rl.py",
        root / "experiments" / "vda_stream_factorial" / "stream_model.py",
        root / "experiments" / "vda_stream_factorial" / "design_matrix.py",
        config_path,
        design_path,
        launcher_path,
        preflight_path,
    )
    for path in required:
        if not path.is_file():
            fail(f"missing required file: {path}")

    actual_design_sha = sha256(design_path)
    actual_config_sha = sha256(config_path)
    if not re.fullmatch(r"[0-9a-fA-F]{64}", args.expected_design_sha256):
        fail("expected design SHA-256 is not 64 hexadecimal characters")
    if not re.fullmatch(r"[0-9a-fA-F]{64}", args.expected_config_sha256):
        fail("expected config SHA-256 is not 64 hexadecimal characters")
    if actual_design_sha != args.expected_design_sha256.lower():
        fail(
            f"design manifest hash mismatch: expected {args.expected_design_sha256}, "
            f"got {actual_design_sha}"
        )
    if actual_config_sha != args.expected_config_sha256.lower():
        fail(
            f"config hash mismatch: expected {args.expected_config_sha256}, got {actual_config_sha}"
        )

    design = json.loads(design_path.read_text(encoding="utf-8"))
    config = json.loads(config_path.read_text(encoding="utf-8"))
    if design.get("schema_version") != 1 or design.get("design_id") != EXPECTED_DESIGN_ID:
        fail("design manifest identity/schema mismatch")
    if design.get("status") != "production_contract_prepared_not_launched":
        fail("design manifest status does not preserve the not-launched evidence boundary")
    if design.get("factor_levels", {}).get("training_seeds") != list(SEEDS):
        fail("design manifest training-seed matrix changed")
    observed_cells = {
        (row.get("effective_visual_streams"), row.get("effective_memory_streams"))
        for row in design.get("cells", [])
    }
    if observed_cells != set(CELLS):
        fail(f"design manifest factorial cells changed: {sorted(observed_cells)}")

    source_contract = design.get("source_contract", {})
    stream_model_path = root / source_contract.get("stream_model_path", "")
    design_matrix_path = root / source_contract.get("design_matrix_path", "")
    if sha256(stream_model_path) != source_contract.get("stream_model_sha256"):
        fail("stream_model.py hash differs from the frozen design")
    if sha256(design_matrix_path) != source_contract.get("design_matrix_sha256"):
        fail("design_matrix.py hash differs from the frozen design")

    validate_config(config, actual_design_sha)
    validate_launcher(
        launcher_path,
        args.run_kind,
        {"config": actual_config_sha, "design": actual_design_sha},
    )

    sys.path.insert(0, str(root))
    import torch  # pylint: disable=import-outside-toplevel
    from envs import make_env, task_grid  # pylint: disable=import-outside-toplevel
    from experiments.vda_stream_factorial.stream_model import (  # pylint: disable=import-outside-toplevel
        build_stream_factorial_model,
    )
    from train_rl import (  # pylint: disable=import-outside-toplevel
        _producer_hashes,
        build_arg_parser,
        resolve_patch_grid,
        resolve_stream_factorial_model_factory,
        seed_training_rngs,
    )

    if list(task_grid("vda4")) != [2, 2]:
        fail("VDA4 stimulus registry geometry is not 2x2")
    if list(resolve_patch_grid("vda4", 10, 10)) != [10, 10]:
        fail("carrier patch/memory grid does not resolve to 10x10")
    env = make_env(
        "vda4", T=7, frame_repeat=1, min_change_time=5, max_change_time=5,
        noise_multiplier=5.0, curriculum=True, theta=65.0,
        curr_window=1000, curr_threshold=0.85, curr_step=3.0, theta_floor=8.0,
    )
    if (env.grid_rows, env.grid_cols, env.n_stim, env.S, env.T) != (2, 2, 4, 50, 7):
        fail("constructed VDA4 environment geometry/timeline changed")
    if tuple(env.observation_space.shape) != (50, 50, 3):
        fail("VDA4 observation shape is not 50x50x3")

    parser_args = build_arg_parser().parse_args(
        [
            "--task", "vda4",
            "--patch-grid-rows", "10",
            "--patch-grid-cols", "10",
            "--effective-visual-streams", str(args.visual_streams),
            "--effective-memory-streams", str(args.memory_streams),
            "--conv-frontend",
            "--cell", "xlstm",
            "--feedback", "crossattn1",
            "--d-mem", "128",
            "--memory-decay", "1.0",
        ]
    )
    model_factory = resolve_stream_factorial_model_factory(
        parser_args, grid_rows=10, grid_cols=10
    )
    if model_factory != {
        "kind": "stream_factorial_v1",
        "effective_visual_streams": args.visual_streams,
        "effective_memory_streams": args.memory_streams,
        "carrier_grid": [10, 10],
    }:
        fail(f"train_rl resolved an unexpected model factory: {model_factory}")

    trainable_hashes: dict[str, str] = {}
    model_checks: dict[str, Any] = {}
    for visual, memory in CELLS:
        seed_training_rngs(args.seed)
        model = build_stream_factorial_model(visual, memory, "crossattn1")
        parameter_count = sum(parameter.numel() for parameter in model.parameters())
        trainable_count = sum(
            parameter.numel() for parameter in model.parameters() if parameter.requires_grad
        )
        if parameter_count != EXPECTED_PARAMETERS or trainable_count != EXPECTED_PARAMETERS:
            fail(
                f"parameter-count mismatch in V={visual},M={memory}: "
                f"all={parameter_count}, trainable={trainable_count}"
            )
        if (
            model.n_tokens != EXPECTED_CARRIER_TOKENS
            or model.front.token_dim != EXPECTED_TOKEN_WIDTH
            or model.encoder.readout_dim != EXPECTED_READOUT_DIM
        ):
            fail(f"carrier/token/readout shape mismatch in V={visual},M={memory}")
        visual_projector = model.front.projector
        memory_projector = model.encoder.memory_projector
        visual_rank = int(torch.linalg.matrix_rank(visual_projector.matrix).item())
        memory_rank = int(torch.linalg.matrix_rank(memory_projector.matrix).item())
        if visual_rank != visual or memory_rank != memory:
            fail(
                f"projector rank mismatch in V={visual},M={memory}: "
                f"observed {visual_rank},{memory_rank}"
            )
        for name, projector in (
            ("visual", visual_projector), ("memory", memory_projector)
        ):
            matrix = projector.matrix
            if not torch.isfinite(matrix).all():
                fail(f"{name} projector is non-finite in V={visual},M={memory}")
            if not torch.allclose(matrix @ matrix, matrix, atol=1e-7, rtol=0.0):
                fail(f"{name} projector is not idempotent in V={visual},M={memory}")
        cell_id = f"visual{visual}_memory{memory}"
        trainable_hashes[cell_id] = named_trainable_sha256(model)
        model_checks[cell_id] = {
            "parameters": parameter_count,
            "trainable_parameters": trainable_count,
            "carrier_tokens": model.n_tokens,
            "token_width": model.front.token_dim,
            "readout_dim": model.encoder.readout_dim,
            "visual_projector_rank": visual_rank,
            "memory_projector_rank": memory_rank,
        }
        del model

    if len(set(trainable_hashes.values())) != 1:
        fail(f"paired seed does not yield identical trainable initialization: {trainable_hashes}")

    trace_spec = design.get("environment_rng_trace", {})
    trial_count = trace_spec.get("trial_count")
    expected_trace = trace_spec.get("expected_sha256_by_seed", {}).get(str(args.seed))
    actual_trace = environment_rng_trace(root, args.seed, trial_count)
    if not re.fullmatch(r"[0-9a-f]{64}", str(expected_trace)):
        fail(f"design has no frozen environment RNG trace for seed {args.seed}")
    if actual_trace != expected_trace:
        fail(
            f"environment RNG trace mismatch for seed {args.seed}: "
            f"expected {expected_trace}, got {actual_trace}"
        )

    producer_hashes = _producer_hashes(
        str(config_path), str(launcher_path), model_factory=model_factory
    )
    required_hash_keys = {
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
        "experiments/vda_stream_factorial/stream_model.py",
        "experiments/vda_stream_factorial/design_matrix.py",
        "experiments/vda_stream_factorial/design_manifest.json",
        "experiments/vda_stream_factorial/preflight_contract_v1.py",
        "resolved_config",
        "experiment_launcher",
    }
    if not required_hash_keys.issubset(producer_hashes):
        fail(
            "producer hash set is incomplete: "
            f"{sorted(required_hash_keys - set(producer_hashes))}"
        )
    if producer_hashes["resolved_config"] != actual_config_sha:
        fail("train_rl producer config hash mismatch")
    if producer_hashes["experiment_launcher"] != sha256(launcher_path):
        fail("train_rl producer launcher hash mismatch")
    if producer_hashes[source_contract["stream_model_path"]] != source_contract["stream_model_sha256"]:
        fail("train_rl producer stream_model hash mismatch")
    if producer_hashes[source_contract["design_matrix_path"]] != source_contract["design_matrix_sha256"]:
        fail("train_rl producer design_matrix hash mismatch")
    if producer_hashes["experiments/vda_stream_factorial/design_manifest.json"] != actual_design_sha:
        fail("train_rl producer design-manifest hash mismatch")
    if producer_hashes["experiments/vda_stream_factorial/preflight_contract_v1.py"] != sha256(preflight_path):
        fail("train_rl producer preflight-contract hash mismatch")

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
            "visual_streams": args.visual_streams,
            "memory_streams": args.memory_streams,
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
            "trainable_initialization": next(iter(trainable_hashes.values())),
            "environment_rng_trace": actual_trace,
        },
        "paired_trainable_initialization_sha256_by_cell": trainable_hashes,
        "model_checks_by_cell": model_checks,
        "model_factory": model_factory,
        "producer_sha256": producer_hashes,
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
    parser.add_argument("--visual-streams", type=int, required=True)
    parser.add_argument("--memory-streams", type=int, required=True)
    parser.add_argument("--seed", type=int, required=True)
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
            "PREFLIGHT_PASS|design=vda4_stream_factorial_crossattn1_production_v1|"
            f"run_kind={request['run_kind']}|visual={request['visual_streams']}|"
            f"memory={request['memory_streams']}|seed={request['seed']}|"
            "carrier=10x10|active=4|d_mem=128|decay=1|fresh"
        )


if __name__ == "__main__":
    main()
