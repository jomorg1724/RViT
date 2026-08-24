"""Emit the registered constant-parameter VDA stream-factorial matrix."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from experiments.vda_stream_factorial.stream_model import build_stream_factorial_model


FEEDBACKS = ("crossattn1", "affine_ew")
STREAM_LEVELS = (4, 100)
EXPECTED_PARAMETERS = {"crossattn1": 8_682_948, "affine_ew": 8_661_468}


def build_matrix(seeds=(0, 1, 2)) -> dict:
    families = {}
    for feedback in FEEDBACKS:
        counts = set()
        rows = []
        for visual in STREAM_LEVELS:
            for memory in STREAM_LEVELS:
                model = build_stream_factorial_model(visual, memory, feedback)
                parameter_count = sum(p.numel() for p in model.parameters())
                trainable_count = sum(p.numel() for p in model.parameters() if p.requires_grad)
                counts.add(parameter_count)
                rows.append(
                    {
                        "visual_streams": visual,
                        "memory_streams": memory,
                        "carrier_tokens": model.n_tokens,
                        "token_width": model.front.token_dim,
                        "readout_dim": model.encoder.readout_dim,
                        "parameters": parameter_count,
                        "trainable_parameters": trainable_count,
                        "seeds": list(seeds),
                    }
                )
                del model
        if counts != {EXPECTED_PARAMETERS[feedback]}:
            raise RuntimeError(f"{feedback} parameter-count mismatch: {sorted(counts)}")
        families[feedback] = rows
    return {
        "status": "design_only_not_launched",
        "task": "vda4",
        "display": "unchanged 50x50 four-item display",
        "carrier_grid": [10, 10],
        "effective_visual_streams": list(STREAM_LEVELS),
        "effective_memory_streams": list(STREAM_LEVELS),
        "paired_initialization": "same seed starts from identical trainable tensors within routing family",
        "training_contract": {
            "iterations": 20000,
            "schedule_final_iteration": 19999,
            "episodes_per_iteration": 8,
            "d_mem": 128,
            "memory_decay": 1.0,
            "jepa_coef": 0.5,
            "no_early_stopping": True,
        },
        "families": families,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--seeds", type=int, nargs="+", default=[0, 1, 2])
    args = parser.parse_args()
    payload = build_matrix(tuple(args.seeds))
    rendered = json.dumps(payload, indent=2, sort_keys=True)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered + "\n", encoding="utf-8")
    print(rendered)


if __name__ == "__main__":
    main()
