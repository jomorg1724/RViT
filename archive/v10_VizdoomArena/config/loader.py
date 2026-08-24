"""
Config loader for RViT+ training scripts.

Provides a tiny utility that:
  1. Looks for a JSON config file (default path or explicit `--config` flag).
  2. Loads it, flattens nested sections into a single dot-keyed dict.
  3. Returns the dict so the caller can use it as argparse defaults.

Loading priority for a given setting:
    CLI argument  >  config file  >  hardcoded default in the script

Format matches Prism/, HRA/, PrismV2/: JSON with sectioned structure
(`run`, `model`, `environment`, etc.) and inline `_comment` / `_note_*`
documentation keys (which are silently skipped by the flattener — they
are documentation only, not config values).
"""
from __future__ import annotations

import json
import os
import sys
from typing import Any, Dict, Optional


# Default config file location relative to this loader.py.
_HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_CONFIG_PATH = os.path.join(_HERE, "v10_config.json")


def _flatten(d: dict, prefix: str = "") -> Dict[str, Any]:
    """Flatten nested sections into dot-keyed flat dict.

    Example:
        {"ae": {"iters": 10000}}  →  {"ae.iters": 10000}

    `_comment` and `_note_*` keys are skipped — they exist for documentation
    inside the JSON file (since JSON has no native comment syntax) and are
    not actual configuration values.
    """
    out: Dict[str, Any] = {}
    for k, v in d.items():
        if k == "_comment" or k.startswith("_note_"):
            continue   # documentation, not config
        key = f"{prefix}{k}"
        if isinstance(v, dict):
            out.update(_flatten(v, prefix=f"{key}."))
        else:
            out[key] = v
    return out


def load_config(path: Optional[str] = None, *, required: bool = False) -> Dict[str, Any]:
    """Load the project JSON config and return a flattened dot-keyed dict.

    Args
    ----
    path     : explicit path to a config file, or None to use DEFAULT_CONFIG_PATH.
    required : if True, raise when the file is missing; if False, return {}.

    Returns
    -------
    dict with FLATTENED dot-keyed entries (e.g. {"ae.iters": 10000,
    "run.checkpoint_path": "...", "model.rl.split_c3": true, ...}). Empty
    dict if the file does not exist and `required=False`.
    """
    p = path or DEFAULT_CONFIG_PATH
    if not os.path.exists(p):
        if required:
            raise FileNotFoundError(f"config file not found: {p}")
        return {}
    with open(p, "r") as f:
        raw = json.load(f)
    return _flatten(raw)


def cfg_get(cfg: Dict[str, Any], key: str, fallback: Any) -> Any:
    """Get `key` from the loaded (flattened) config dict, or `fallback` if missing.

    Treats empty strings as "not set" (returns fallback) — useful for paths
    where "" in the TOML means "no path".
    """
    val = cfg.get(key, fallback)
    if val == "":
        return fallback
    return val


def load_checkpoint_weights(
    model,
    ckpt_path: str,
    *,
    strict: bool,
    device,
) -> Dict[str, Any]:
    """Load weights from a checkpoint into `model`.

    Two modes:
        strict=False : PARTIAL load. Only keys whose name+shape match the
                       current model are restored; the rest are silently
                       skipped. Use this for AE → RL warm-starts where the
                       checkpoint doesn't contain actor/critic weights.
        strict=True  : FULL load. Every key in the checkpoint must be in the
                       current model and vice versa, every shape must match.
                       Use this when resuming the SAME model from its own
                       checkpoint. Raises a RuntimeError on any mismatch
                       (with a list of missing/unexpected keys).

    Returns
    -------
    info dict with diagnostic counts and the original checkpoint's metadata
    (iter, model_kwargs if present). The trainer can use this to log a
    descriptive message at startup.
    """
    import torch
    ckpt = torch.load(ckpt_path, map_location=device, weights_only=False)
    loaded_sd = ckpt.get("model_state_dict", ckpt)
    own_sd = model.state_dict()

    info: Dict[str, Any] = {
        "path": ckpt_path,
        "ckpt_iter": ckpt.get("iter", None),
        "ckpt_model_kwargs": ckpt.get("model_kwargs", None),
        "strict": strict,
    }

    if strict:
        # torch's native load handles strict loading + raises on mismatch.
        result = model.load_state_dict(loaded_sd, strict=True)
        info["loaded"] = len(loaded_sd)
        info["skipped"] = 0
        info["missing"] = list(result.missing_keys)
        info["unexpected"] = list(result.unexpected_keys)
    else:
        # Partial load: classify every tensor into three buckets so the
        # trainer can surface which weights actually stayed at random init.
        compatible = {}             # in both, shape matches → restored
        ckpt_skipped = []           # in ckpt but not usable (extra key or wrong shape)
        for k, v in loaded_sd.items():
            if k in own_sd and own_sd[k].shape == v.shape:
                compatible[k] = v
            else:
                ckpt_skipped.append(k)
        # Model keys that the checkpoint did not provide → stayed at random init.
        random_init_keys = [k for k in own_sd.keys() if k not in compatible]
        own_sd.update(compatible)
        model.load_state_dict(own_sd)
        info["loaded"] = len(compatible)
        info["skipped"] = len(ckpt_skipped)
        info["skipped_keys"] = ckpt_skipped
        info["random_init_keys"] = random_init_keys
        info["n_random_init"] = len(random_init_keys)
    return info


def print_resolved_config(cfg: Dict[str, Any], used_keys: list[str]) -> None:
    """Print which config values are actually being used. Useful diagnostic
    at the start of a training run so the user can see what was loaded
    from the file vs left at script default.
    """
    if not cfg:
        print("[config] (no config file loaded — using script defaults)")
        return
    print(f"[config] {len(cfg)} keys loaded from config:")
    for k in sorted(used_keys):
        if k in cfg:
            v = cfg[k]
            print(f"  {k:35s} = {v!r}")
