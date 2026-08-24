from __future__ import annotations

import numpy as np
import torch


def test_selected_assay_uses_training_noise_and_sampled_actions(monkeypatch):
    from experiments.luo2015_episodic import evaluate_selected_replication as assay

    calls = []
    def fake_press(model, videos, batch_size, **kwargs):
        calls.append(kwargs)
        if len(calls) == 1:
            return np.asarray([3, 4, -1, -1])
        return np.asarray([6, 6, 3, 3])

    bank = (
        torch.zeros(4, 7, 3, 50, 50), torch.zeros(4, 7, 3, 50, 50),
        np.asarray([0, 0, 3, 3]), np.asarray([0, 0, 3, 3]),
    )
    result, raw = assay.evaluate_model(
        object(), bank, condition_loc=0, session="sensitivity", batch_size=2,
        bootstrap_draws=100, bootstrap_seed=7, press_function=fake_press,
    )
    assert calls == [
        {"inject_memory_noise": True, "sample_actions": True},
        {"inject_memory_noise": True, "sample_actions": True},
    ]
    assert result["evaluation_contract"]["memory_noise_enabled"] is True
    assert result["evaluation_contract"]["sample_actions"] is True
    assert raw["change_press"].tolist() == [3, 4, -1, -1]


def test_sensitivity_and_criterion_primary_contrasts_have_paper_signs():
    from experiments.luo2015_episodic.evaluate_selected_replication import summarize_policy

    locations = np.asarray([0] * 100 + [3] * 100)
    # Sensitivity loc3: same criterion geometry, larger separation at loc3.
    change = np.asarray([3] * 60 + [-1] * 40 + [3] * 90 + [-1] * 10)
    no_change = np.asarray([3] * 20 + [6] * 80 + [3] * 10 + [6] * 90)
    s = summarize_policy(change, no_change, locations, locations, condition_loc=3,
                         session="sensitivity", bootstrap_draws=200, bootstrap_seed=1)
    assert s["contrasts"]["condition_minus_control"]["dprime"] > 0

    # Criterion loc3: similar d-prime geometry, both HR and FA shifted upward at loc3.
    change = np.asarray([3] * 60 + [-1] * 40 + [3] * 90 + [-1] * 10)
    no_change = np.asarray([3] * 20 + [6] * 80 + [3] * 50 + [6] * 50)
    c = summarize_policy(change, no_change, locations, locations, condition_loc=3,
                         session="criterion", bootstrap_draws=200, bootstrap_seed=2)
    assert c["contrasts"]["condition_minus_control"]["criterion"] < 0


def test_existing_matrix_analyzer_explicitly_preserves_training_policy_semantics():
    from pathlib import Path
    source = (Path(__file__).resolve().parents[1] / "experiments" / "luo2015_episodic" / "analyze_matrix.py").read_text()
    assert "inject_memory_noise=True" in source
    assert "sample_actions=True" in source
