"""Config loader — thin copy of RViT_plus_paper/config/loader.py."""
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
    own_sd = model.state_dict()
    info: Dict[str, Any] = {
        "path": ckpt_path, "ckpt_iter": ckpt.get("iter"), "ckpt_model_kwargs": ckpt.get("model_kwargs"),
        "strict": strict,
    }
    if strict:
        result = model.load_state_dict(loaded_sd, strict=True)
        info.update(loaded=len(loaded_sd), skipped=0, missing=list(result.missing_keys),
                    unexpected=list(result.unexpected_keys))
    else:
        compatible = {k: v for k, v in loaded_sd.items() if k in own_sd and own_sd[k].shape == v.shape}
        ckpt_skipped = [k for k in loaded_sd if k not in compatible]
        random_init_keys = [k for k in own_sd if k not in compatible]
        own_sd.update(compatible)
        model.load_state_dict(own_sd)
        info.update(loaded=len(compatible), skipped=len(ckpt_skipped), skipped_keys=ckpt_skipped,
                    random_init_keys=random_init_keys, n_random_init=len(random_init_keys))
    return info
