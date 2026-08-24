"""Re-export the paper PAC/QR-DQN/PER trainer for the DMD transformer model."""
from __future__ import annotations

import importlib.util
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_PAPER = os.path.join(os.path.dirname(_HERE), "RViT_plus_paper")
_PAPER_PPO = os.path.join(_PAPER, "ppo.py")

_spec = importlib.util.spec_from_file_location("paper_ppo_base_dmd", _PAPER_PPO)
base_ppo = importlib.util.module_from_spec(_spec)
assert _spec and _spec.loader

_old_path = list(sys.path)
_old_model = sys.modules.pop("model", None)
if _PAPER in sys.path:
    sys.path.remove(_PAPER)
sys.path.insert(0, _PAPER)
sys.modules["paper_ppo_base_dmd"] = base_ppo
_spec.loader.exec_module(base_ppo)
if _old_model is not None:
    sys.modules["model"] = _old_model
else:
    sys.modules.pop("model", None)
sys.path[:] = _old_path

RolloutBatch = base_ppo.RolloutBatch
EpisodeReplayBuffer = base_ppo.EpisodeReplayBuffer
PPOConfig = base_ppo.PPOConfig
collect_episodes = base_ppo.collect_episodes
ppo_update = base_ppo.ppo_update
train = base_ppo.train
