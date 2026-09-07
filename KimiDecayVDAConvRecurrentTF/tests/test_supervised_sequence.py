"""Real trainer slices + real VDA16 env; no training loop/optimizer execution."""
import ast
import copy
import inspect

import numpy as np
import pytest
import torch

import pretrain_kda_convmem as trainer


def execute(nodes, ns):
    exec(compile(ast.Module(body=nodes, type_ignores=[]), "<actual trainer slice>", "exec"), ns)


def expression(node, ns):
    return eval(compile(ast.Expression(node), "<actual trainer expression>", "eval"), ns)


def setup_collection(monkeypatch, extra=()):
    args = trainer.build_parser().parse_args([
        "--device", "cpu", "--collection-size", "8", "--batch-size", "8",
        "--n-channels", "8", "--map-size", "4", "--proto-dim", "16",
        "--kda-heads", "2", "--kda-head-dim", "4", "--change-per-step", *extra])
    tree = ast.parse(inspect.getsource(trainer.main))
    ns = dict(vars(trainer), args=args, device=torch.device("cpu"))
    call = next(n for n in ast.walk(tree) if isinstance(n, ast.Call)
                and isinstance(n.func, ast.Name) and n.func.id == "make_env")
    env = expression(call, ns)
    trials = []
    reset, step = env.reset, env.step

    def record_reset():
        obs = reset()
        trials.append(dict(frames=[obs.copy()], times=[env.t], done=[],
                           change=int(env.change_true), valid=int(env.valid),
                           change_time=int(env.change_time)))
        return obs

    def record_step(action):
        assert action == 0
        result = step(action)
        trials[-1]["frames"].append(result[0].copy())
        trials[-1]["times"].append(env.t)
        trials[-1]["done"].append(result[2])
        return result

    monkeypatch.setattr(env, "reset", record_reset)
    monkeypatch.setattr(env, "step", record_step)
    ns.update(env=env, T=env.T)
    collection = next(n for n in ast.walk(tree) if isinstance(n, ast.For)
                      and isinstance(n.target, ast.Name) and n.target.id == "col")
    stop = next(i for i, n in enumerate(collection.body) if isinstance(n, ast.Assign)
                and any(isinstance(t, ast.Name) and t.id == "acc" for t in n.targets))
    np.random.seed(123)
    execute(collection.body[:stop], ns)
    return args, tree, ns, trials


def run_student(tree, ns):
    call = next(n for n in ast.walk(tree) if isinstance(n, ast.Call)
                and isinstance(n.func, ast.Name) and n.func.id == "KDAConvMemoryModel")
    model = expression(call, ns)
    seen = []
    hook = model.stem.register_forward_pre_hook(lambda module, inputs: seen.append(inputs[0].detach().clone()))
    ns.update(model=model, obs_mb=ns["obs"].float())
    forward = next(n for n in ast.walk(tree) if isinstance(n, ast.Assign)
                   and ast.unparse(n.value) == "model.forward_seq(obs_mb)")
    with torch.no_grad():
        execute([forward], ns)
    hook.remove()
    return model, seen


def run_labels(tree, ns):
    ns.update(bidx=torch.arange(len(ns["change"])), change_mb=ns["change"])
    branch = next(n for n in ast.walk(tree) if isinstance(n, ast.If)
                  and ast.unparse(n.test) == "args.change_per_step and args.label == 'change'")
    with torch.no_grad():
        execute([branch], ns)
    return ns["step_labels"]


def test_actual_collector_sends_reset_blank_to_stem_and_exact_seven_frames(monkeypatch):
    torch.set_num_threads(1)
    args, tree, ns, trials = setup_collection(monkeypatch)
    model, seen = run_student(tree, ns)
    assert len(seen) == 7
    reset_batch = torch.from_numpy(np.stack([t["frames"][0] for t in trials])).permute(0, 3, 1, 2)
    torch.testing.assert_close(seen[0], reset_batch, rtol=0, atol=0)
    assert ns["obs"].shape == (8, 7, 100, 100, 3)
    assert {t["change"] for t in trials} == {0, 1}
    for i, trial in enumerate(trials):
        assert trial["times"] == list(range(7)), "never request terminal-return t7"
        assert not any(trial["done"])
        expected = np.stack(trial["frames"])
        np.testing.assert_array_equal(ns["obs"][i].numpy(), expected)
        assert not expected[0].any() and not expected[2].any()
        assert expected[1].any() and all(expected[t].any() for t in (3, 4, 5, 6))
    for t in range(7):
        torch.testing.assert_close(seen[t], ns["obs"][:, t].permute(0, 3, 1, 2), rtol=0, atol=0)
    labels = run_labels(tree, ns)
    assert labels.tolist() == [[0, 0, 0, 0, 0, t["change"], t["change"]] for t in trials]
    assert model.memory_noise_std == args.memory_noise_std == 0.05
    assert model.frame_window == model.frame_stride == model.mem_every == 1
    assert ns["env"].noise_multiplier == args.noise == 5.0


def test_labels_follow_physical_repeat_and_model_window_endpoints(monkeypatch):
    torch.set_num_threads(1)
    args, tree, ns, trials = setup_collection(monkeypatch, [
        "--frame-repeat", "2", "--frame-window", "2", "--frame-stride", "3", "--mem-every", "3"])
    model, seen = run_student(tree, ns)
    assert len(seen) == 5
    assert model.frame_window == 2 and model.frame_stride == model.mem_every == 3
    labels = run_labels(tree, ns)
    assert labels.tolist() == [[0, 0, 0, t["change"], t["change"]] for t in trials]
    assert all(t["times"] == list(range(14)) for t in trials)


def test_collector_preserves_seeded_noise_without_rerendering(monkeypatch):
    _, _, ns, trials = setup_collection(monkeypatch)
    # Independent, real-env replay: same reset + six steps and no extra RNG draws.
    reference = trainer.make_env("vda16", T=7, noise_multiplier=5.0, curriculum=False)
    np.random.seed(123)
    for i in range(8):
        frames = [reference.reset()]
        frames.extend(reference.step(0)[0] for _ in range(6))
        np.testing.assert_array_equal(ns["obs"][i].numpy(), np.stack(frames))
        assert reference.change_true == trials[i]["change"]
        assert not np.array_equal(frames[3], frames[4]), "observation noise remains active"


def checkpoint_payload(monkeypatch):
    args, tree, ns, _ = setup_collection(monkeypatch)
    model, _ = run_student(tree, ns)
    ns.update(jepa_teacher=copy.deepcopy(model), col=0)
    save = next(n for n in ast.walk(tree) if isinstance(n, ast.Call)
                and ast.unparse(n.func) == "torch.save")
    return tree, ns, expression(save.args[0], ns)


def test_actual_checkpoint_metadata_records_blank_first_environment_times(monkeypatch):
    _, _, payload = checkpoint_payload(monkeypatch)
    assert payload.get("supervised_sequence_version") == "blank_first_v1"
    assert payload["environment_time_indices"] == list(range(7))
    assert payload["model_time_indices"] == list(range(7))
    assert payload["frame_repeat"] == 1
    assert payload.get("memory_noise_std") == 0.05


@pytest.mark.parametrize("key,value", [
    ("supervised_sequence_version", None), ("supervised_sequence_version", "step_first_v0"),
    ("environment_time_indices", list(range(1, 8))), ("model_time_indices", [1, 3, 6]),
    ("frame_repeat", 2), ("frame_window", 2), ("frame_stride", 2),
    ("raw_attention_readout", True), ("memory_noise_std", 0.0),
])
def test_actual_resume_rejects_incompatible_protocol_before_loading_weights(monkeypatch, tmp_path, key, value):
    tree, ns, payload = checkpoint_payload(monkeypatch)
    if value is None:
        payload.pop(key, None)
    else:
        payload[key] = value
    torch.save(payload, tmp_path / "kda_convmem_latest.pt")
    ns.update(ckpt_dir=str(tmp_path))
    ns["args"].resume = True
    def forbidden_load(*args, **kwargs):
        pytest.fail("incompatible checkpoint reached model.load_state_dict")
    monkeypatch.setattr(ns["model"], "load_state_dict", forbidden_load)
    monkeypatch.setattr(ns["jepa_teacher"], "load_state_dict", forbidden_load)
    branch = next(n for n in ast.walk(tree) if isinstance(n, ast.If)
                  and ast.unparse(n.test) == "args.resume")
    with pytest.raises(ValueError, match="sequence protocol"):
        execute([branch], ns)


def test_actual_resume_accepts_matching_protocol(monkeypatch, tmp_path):
    tree, ns, payload = checkpoint_payload(monkeypatch)
    torch.save(payload, tmp_path / "kda_convmem_latest.pt")
    first = next(ns["model"].parameters())
    expected = first.detach().clone()
    with torch.no_grad():
        first.add_(10)
    ns.update(ckpt_dir=str(tmp_path), prev_elapsed=0.0)
    ns["args"].resume = True
    branch = next(n for n in ast.walk(tree) if isinstance(n, ast.If)
                  and ast.unparse(n.test) == "args.resume")
    execute([branch], ns)
    assert ns["start_col"] == 1
    torch.testing.assert_close(first, expected, rtol=0, atol=0)


def test_actual_nomemory_trainer_wiring_preserves_raw_readout_and_blank_first(monkeypatch):
    defaults = trainer.build_parser().parse_args([])
    assert hasattr(defaults, "raw_attention_readout"), "missing no-memory raw readout CLI"
    assert defaults.raw_attention_readout is False
    _, tree, ns, trials = setup_collection(monkeypatch, [
        "--raw-attention-readout", "--v-mode", "learned_z", "--readout", "h2",
        "--memory-noise-std", "0", "--mem-every", "3", "--attn-mode", "token",
        "--softmax-mode", "split", "--vision-qk-norm", "--sample-attention",
        "--attention-entropy-coef", "0.000001"])
    model, seen = run_student(tree, ns)
    assert model.raw_attention_readout is True and model.vision.raw_attention_readout is True
    assert model.memory is None and model.memory_noise_std == 0
    assert model.v_mode == "learned_z" and model.readout == "h2" and model.mem_every == 3
    assert len(seen) == 7 and not seen[0].any()
    assert model.attention_entropy_count == 7
    assert run_labels(tree, ns).tolist() == [[0, 0, 0, 0, 0, t["change"], t["change"]] for t in trials]
    ns.update(jepa_teacher=copy.deepcopy(model), col=0)
    save = next(n for n in ast.walk(tree) if isinstance(n, ast.Call)
                and ast.unparse(n.func) == "torch.save")
    payload = expression(save.args[0], ns)
    assert payload.get("raw_attention_readout") is True
    assert payload["supervised_sequence_version"] == "blank_first_v1"
    constructor_keys = inspect.signature(trainer.KDAConvMemoryModel).parameters
    restored = trainer.KDAConvMemoryModel(**{k: v for k, v in payload.items() if k in constructor_keys})
    restored.load_state_dict(payload["model_state_dict"], strict=True)
    assert restored.memory is None and restored.memory_noise_std == 0
    assert restored.raw_attention_readout is True

