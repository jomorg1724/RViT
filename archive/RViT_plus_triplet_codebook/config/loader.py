"""Tiny JSON config loader for the triplet-codebook variant."""
from __future__ import annotations

import json
import os
from typing import Any, Dict, Optional

_HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_CONFIG_PATH = os.path.join(_HERE, "default.json")


def _flatten(d: dict, prefix: str = "") -> Dict[str, Any]:
    out: Dict[str, Any] = {}
    for k, v in d.items():
        if k == "_comment" or k.startswith("_note_"):
            continue
        key = f"{prefix}{k}"
        if isinstance(v, dict):
            out.update(_flatten(v, prefix=f"{key}."))
        else:
            out[key] = v
    return out


def load_config(path: Optional[str] = None, *, required: bool = False) -> Dict[str, Any]:
    p = path or DEFAULT_CONFIG_PATH
    if not os.path.exists(p):
        if required:
            raise FileNotFoundError(f"config file not found: {p}")
        return {}
    with open(p, "r") as f:
        return _flatten(json.load(f))


def cfg_get(cfg: Dict[str, Any], key: str, fallback: Any) -> Any:
    val = cfg.get(key, fallback)
    return fallback if val == "" else val


def load_checkpoint_weights(model, ckpt_path: str, *, strict: bool, device) -> Dict[str, Any]:
    import torch
    ckpt = torch.load(ckpt_path, map_location=device, weights_only=False)
    loaded_sd = ckpt.get("model_state_dict", ckpt)
    if strict:
        result = model.load_state_dict(loaded_sd, strict=True)
        return {"path": ckpt_path, "ckpt_iter": ckpt.get("iter"), "loaded": len(loaded_sd),
                "skipped": 0, "missing": list(result.missing_keys),
                "unexpected": list(result.unexpected_keys), "strict": True}
    own_sd = model.state_dict()
    compatible = {k: v for k, v in loaded_sd.items() if k in own_sd and own_sd[k].shape == v.shape}
    own_sd.update(compatible)
    model.load_state_dict(own_sd)
    return {"path": ckpt_path, "ckpt_iter": ckpt.get("iter"), "loaded": len(compatible),
            "skipped": len(loaded_sd) - len(compatible), "strict": False}
