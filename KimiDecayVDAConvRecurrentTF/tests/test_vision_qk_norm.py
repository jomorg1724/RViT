"""Vision-only, single full-C-head QKN; no training launched by these tests."""
import ast
import copy
import csv
import inspect
import io
import math
from types import SimpleNamespace

import pytest
import torch
import torch.nn.functional as F

from kda_conv_memory_model import ConvAttentionBlock, ConvMemoryBlock, KDAConvMemoryModel


@pytest.mark.parametrize("v_mode", ["learned", "learned_all"])
def test_full_model_qkn_only_adds_temperature_and_backpropagates(v_mode):
    kwargs = dict(n_channels=8, proto_dim=16, map_size=4, frame_window=1,
                  accum_mode="kda", kda_heads=2, kda_head_dim=4, attn_mode="token",
                  readout="h2", v_mode=v_mode, cls_head="conv", mem_every=2,
                  memory_noise_std=0.05)
    torch.manual_seed(731)
    legacy = KDAConvMemoryModel(**kwargs)
    legacy_rng = torch.get_rng_state().clone()
    torch.manual_seed(731)
    model = KDAConvMemoryModel(**kwargs, vision_qk_norm=True, vision_qk_temperature=4.0)
    assert model.vision_qk_norm and model.vision.vision_qk_norm
    assert torch.equal(legacy_rng, torch.get_rng_state())
    assert set(model.state_dict()) - set(legacy.state_dict()) == {"vision.log_temperature"}
    for key, value in legacy.state_dict().items():
        assert torch.equal(value, model.state_dict()[key]), key
    assert not hasattr(model.memory, "log_temperature")
    assert model.memory.scale == 8 ** -0.5
    assert model.vision.log_temperature.exp().item() == pytest.approx(4.0)
    # Step 5 reads the second memory tick: tick 1 queries zero initial H1.
    obs = torch.randn(2, 5, 16, 16, 3)
    representation = model.forward_seq(obs)
    assert representation.shape == (2, 5, 8, 4, 4)
    loss = (model.classify(representation[:, -1]).square().mean()
            + model.jepa_logits(representation).square().mean())
    loss.backward()
    for param in (model.vision.W_q.weight, model.vision.W_kx.weight,
                  model.vision.W_kh.weight, model.vision.log_temperature,
                  model.vision.V_X, model.vision.V_H, model.memory.W_q.weight):
        assert param.grad is not None and torch.isfinite(param.grad).all()
        assert param.grad.abs().sum() > 0
    if v_mode == "learned_all":
        assert model.memory.V_X.grad.abs().sum() > 0
        assert model.memory.V_H.grad.abs().sum() > 0
    # Frozen/non-tick H1 and ephemeral H2 semantics stay intact.
    state = model.init_state(2, torch.device("cpu"), torch.float32)
    _, next_state = model.step(torch.randn(2, 8, 4, 4), state, update_memory=False)
    assert torch.equal(state[0], next_state[0])
    assert torch.isfinite(next_state[1]).all()



def _block(**kwargs):
    return ConvAttentionBlock(c=8, in_c=16, map_size=2, attn_mode="token",
                              learned_v=True, **kwargs)


def test_split_allv_mem3_preserves_joint_initialization_and_full_backward():
    kwargs = dict(n_channels=8, proto_dim=16, map_size=4, frame_window=1,
                  accum_mode="kda", kda_heads=2, kda_head_dim=4, attn_mode="token",
                  readout="h2", v_mode="learned_all", cls_head="conv", mem_every=3,
                  memory_noise_std=0.05, vision_qk_norm=True)
    torch.manual_seed(3)
    joint = KDAConvMemoryModel(**kwargs)
    joint_rng = torch.get_rng_state().clone()
    torch.manual_seed(3)
    model = KDAConvMemoryModel(**kwargs, softmax_mode="split")
    assert torch.equal(torch.get_rng_state(), joint_rng)
    assert list(model.state_dict()) == list(joint.state_dict())
    for name, value in joint.state_dict().items():
        assert torch.equal(model.state_dict()[name], value), name
    assert model.vision.softmax_mode == model.memory.softmax_mode == "split"
    assert model.mem_every == 3 and model.readout == "h2"
    assert model.vision.learned_v and model.memory.learned_v
    assert [n for n, _ in model.named_parameters() if "log_temperature" in n] == ["vision.log_temperature"]
    assert not getattr(model.memory, "vision_qk_norm", False)
    assert not getattr(model.accumulator, "vision_qk_norm", False)
    assert model.memory.scale == 8 ** -0.5
    # Read after two memory ticks: zero initial H1 would otherwise mask memory Q/K gradients.
    representation = model.forward_seq(torch.randn(2, 7, 16, 16, 3))
    assert representation.shape == (2, 7, 8, 4, 4)
    loss = (model.classify(representation[:, -1]).square().mean()
            + model.jepa_logits(representation).square().mean())
    loss.backward()
    for param in (model.vision.W_q.weight, model.vision.W_kx.weight,
                  model.vision.W_kh.weight, model.vision.log_temperature,
                  model.vision.V_X, model.vision.V_H, model.memory.V_X, model.memory.V_H,
                  model.memory.W_q.weight, model.memory.W_kz.weight, model.memory.W_kh.weight):
        assert param.grad is not None and torch.isfinite(param.grad).all()
        assert param.grad.abs().sum() > 0
    for param in model.accumulator.parameters():
        assert param.grad is not None and torch.isfinite(param.grad).all()
    state = model.init_state(2, torch.device("cpu"), torch.float32)
    with torch.no_grad():
        r, next_state = model.step(torch.randn(2, 8, 4, 4), state, update_memory=False)
    assert torch.equal(state[0], next_state[0])
    assert torch.equal(r, next_state[1])  # H2-only readout; fresh vision read even off tick
    assert torch.isfinite(r).all()
    torch.testing.assert_close(model.vision.qk_stats["mass_x"], torch.tensor(1.0))
    torch.testing.assert_close(model.vision.qk_stats["mass_h"], torch.tensor(1.0))


def test_split_allv_memory_remains_exact_unnormalized_scaled_qk_sum():
    torch.manual_seed(3)
    block = ConvMemoryBlock(c=8, map_size=2, attn_mode="token", learned_v=True,
                            softmax_mode="split", memory_noise_std=0.0)
    z, h = torch.randn(2, 8, 2, 2) * 3, torch.randn(2, 8, 2, 2) * 5
    h1, h2 = block(z, h)
    q, kz, kh = [_tokens(t) for t in (block.W_q(h), block.W_kz(z), block.W_kh(h))]
    az, ah = [(q @ k.transpose(-1, -2) * 8 ** -0.5).softmax(-1) for k in (kz, kh)]
    for a in (az, ah):
        torch.testing.assert_close(a.sum(-1), torch.ones(2, 4))
    vz, vh = [_tokens(v).expand(2, -1, -1) for v in (block.V_X, block.V_H)]
    mixed = (az @ vz + ah @ vh).transpose(1, 2).reshape(2, 8, 2, 2).contiguous()
    expected = block.ffn(mixed)
    torch.testing.assert_close(h2, expected, rtol=0, atol=0)
    torch.testing.assert_close(h1, block.proj(block.se(torch.cat([h, expected], 1))), rtol=0, atol=0)
    assert not torch.allclose(h2, block.ffn(mixed / 2))
    qn, kzn, khn = [F.normalize(t, dim=-1) for t in (q, kz, kh)]
    an_z, an_h = [(qn @ k.transpose(-1, -2) * math.sqrt(8)).softmax(-1) for k in (kzn, khn)]
    normalized = (an_z @ vz + an_h @ vh).transpose(1, 2).reshape(2, 8, 2, 2)
    assert not torch.allclose(h2, block.ffn(normalized))


def _tokens(x):
    return x.flatten(2).transpose(1, 2).float()


@pytest.mark.parametrize("zero_h", [False, True])
def test_cosine_attention_manual_scale_invariance_and_backward(zero_h):
    torch.manual_seed(17)
    block = _block(vision_qk_norm=True, vision_qk_temperature=3.25)
    x = torch.randn(2, 16, 2, 2)
    h = torch.zeros(2, 8, 2, 2) if zero_h else torch.randn(2, 8, 2, 2)
    z, att, mass = block(x, h, return_attn=True)
    q, kx, kh = [F.normalize(_tokens(t), dim=-1)
                 for t in (block.W_q(x), block.W_kx(x), block._keys_h(h))]
    scores = 3.25 * torch.cat([q @ kx.transpose(-1, -2),
                              q @ kh.transpose(-1, -2)], dim=-1)
    weights = scores.softmax(-1)
    vx = _tokens(block.V_X).expand(2, -1, -1)
    vh = _tokens(block.V_H).expand(2, -1, -1)
    mixed = weights[..., :4] @ vx + weights[..., 4:] @ vh
    expected_att = block.ffn(mixed.transpose(1, 2).reshape(2, 8, 2, 2))
    expected_mass = torch.stack([weights[..., :4].sum(-1),
                                 weights[..., 4:].sum(-1)], dim=1).reshape(2, 2, 2, 2)
    torch.testing.assert_close(att, expected_att)
    torch.testing.assert_close(mass, expected_mass)
    torch.testing.assert_close(mass.sum(1), torch.ones_like(mass[:, 0]))
    assert torch.isfinite(z).all()
    if zero_h:
        assert torch.equal(scores[..., 4:], torch.zeros_like(scores[..., 4:]))
    (att.square().sum() + (mass[:, 0] * torch.arange(4).reshape(2, 2)).sum()).backward()
    for param in (block.W_q.weight, block.W_kx.weight, block.W_kh.weight,
                  block.log_temperature):
        assert param.grad is not None and torch.isfinite(param.grad).all()
        if not (zero_h and param is block.W_kh.weight):
            assert param.grad.abs().sum() > 0
    # Independent positive scaling of each projection leaves routing unchanged.
    with torch.no_grad():
        block.W_q.weight.mul_(5)
        block.W_kx.weight.mul_(0.125)
        block.W_kh.weight.mul_(11)
        _, scaled_att, scaled_mass = block(x, h, return_attn=True)
    torch.testing.assert_close(scaled_att, att)
    torch.testing.assert_close(scaled_mass, mass)


def test_default_off_retains_original_state_dict_and_rng():
    # Frozen constructor branch for _block's configuration, transcribed from
    # e3a2dbd80a3191d57a1d13eacf674dabb79ff773:
    # KimiDecayVDAConvRecurrentTF/kda_conv_memory_model.py (including SEBlock).
    # Keep this independent of the current constructors: seeded initialization
    # may differ across PyTorch/platform versions, but must match within a run.
    # No git checkout or network access is required when executing this test.
    nn = torch.nn

    class OriginalSEBlock(nn.Module):
        def __init__(self, channels, reduction=4):
            super().__init__()
            self.fc = nn.Sequential(
                nn.AdaptiveAvgPool2d(1),
                nn.Conv2d(channels, max(channels // reduction, 1), 1),
                nn.GELU(),
                nn.Conv2d(max(channels // reduction, 1), channels, 1),
                nn.Sigmoid(),
            )

    class OriginalConvAttentionBlock(nn.Module):
        def __init__(self):
            super().__init__()
            # c=8, in_c=16, map_size=2, attn_mode="token", learned_v=True;
            # softmax_mode="joint", h_key_embed=False, acc_stream=False.
            c, cin, map_size = 8, 16, 2
            self.acc_stream = False
            self.attn_mode = "token"
            self.softmax_mode = "joint"
            self.learned_v = True
            self.h_key_embed = False
            self.W_q = nn.Conv2d(cin, c, 1, bias=False)
            self.W_kx = nn.Conv2d(cin, c, 1, bias=False)
            self.W_kh = nn.Conv2d(c, c, 1, bias=False)
            self.V_X = nn.Parameter(torch.randn(1, c, map_size, map_size) * 0.02)
            self.V_H = nn.Parameter(torch.randn(1, c, map_size, map_size) * 0.02)
            self.ffn = nn.Sequential(nn.Conv2d(c, 2 * c, 1), nn.GELU(), nn.Conv2d(2 * c, c, 1))
            self.se = OriginalSEBlock(cin + c)
            self.proj = nn.Conv2d(cin + c, c, 1)
            self.scale = c ** -0.5

    torch.manual_seed(731)
    baseline = OriginalConvAttentionBlock()
    baseline_rng = torch.get_rng_state().clone()
    baseline_state = baseline.state_dict()
    blocks = []
    for config in ({}, {"vision_qk_norm": False}):
        torch.manual_seed(731)
        block = _block(**config)
        assert torch.equal(torch.get_rng_state(), baseline_rng), config
        state = block.state_dict()
        assert list(state) == list(baseline_state), config
        for key, expected in baseline_state.items():
            actual = state[key]
            assert actual.dtype == expected.dtype, (config, key)
            assert actual.shape == expected.shape, (config, key)
            assert torch.equal(actual, expected), (config, key)
        assert not block.vision_qk_norm
        assert not hasattr(block, "log_temperature")
        blocks.append(block)

    implicit, explicit = blocks
    x, h = torch.randn(2, 16, 2, 2), torch.randn(2, 8, 2, 2)
    for actual, expected in zip(explicit(x, h, return_attn=True),
                                implicit(x, h, return_attn=True)):
        assert torch.equal(actual, expected)


def test_split_qkn_is_exact_sum_of_independent_fullchannel_cosine_mixes():
    torch.manual_seed(3)
    block = ConvAttentionBlock(c=128, in_c=256, map_size=2, attn_mode="token",
                               learned_v=True, softmax_mode="split", vision_qk_norm=True)
    assert block.log_temperature.ndim == 0
    assert block.log_temperature.exp().item() == pytest.approx(math.sqrt(128))
    x, h = torch.randn(2, 256, 2, 2), torch.randn(2, 128, 2, 2)
    captured = []
    handle = block.ffn.register_forward_pre_hook(lambda module, args: captured.append(args[0]))
    try:
        z, att, mass = block(x, h, return_attn=True)
    finally:
        handle.remove()
    q, kx, kh = [F.normalize(_tokens(t), dim=-1)
                 for t in (block.W_q(x), block.W_kx(x), block._keys_h(h))]
    tau = block.log_temperature.exp()
    ax = (q @ kx.transpose(-1, -2) * tau).softmax(-1)
    ah = (q @ kh.transpose(-1, -2) * tau).softmax(-1)
    for weights in (ax, ah):
        torch.testing.assert_close(weights.sum(-1), torch.ones(2, 4))
    vx, vh = [_tokens(v).expand(2, -1, -1) for v in (block.V_X, block.V_H)]
    mixed = ax @ vx + ah @ vh
    expected = mixed.transpose(1, 2).reshape(2, 128, 2, 2).contiguous()
    torch.testing.assert_close(captured[0], expected, rtol=0, atol=0)
    torch.testing.assert_close(att, block.ffn(expected), rtol=0, atol=0)
    torch.testing.assert_close(mass, torch.ones_like(mass))
    torch.testing.assert_close(mass.sum(1), torch.full_like(mass[:, 0], 2.0))
    assert not torch.allclose(captured[0], expected / 2)  # SUM, never average
    assert torch.isfinite(z).all()
    att.square().sum().backward()
    for param in (block.W_q.weight, block.W_kx.weight, block.W_kh.weight,
                  block.log_temperature):
        assert param.grad is not None and torch.isfinite(param.grad).all()
        assert param.grad.abs().sum() > 0


@pytest.mark.parametrize("config", [
    {"attn_mode": "pixel_gate"},
    {"softmax_mode": "colgate"}, {"acc_stream": True},
])
def test_qkn_rejects_incompatible_two_stream_token_attention(config):
    kwargs = dict(c=8, attn_mode="token", vision_qk_norm=True)
    kwargs.update(config)
    with pytest.raises(ValueError, match="vision_qk_norm.*token.*joint.*two.stream"):
        ConvAttentionBlock(**kwargs)


@pytest.mark.parametrize("temperature", [0.0, -1.0, float("nan"), float("inf"), -float("inf")])
@pytest.mark.parametrize("enabled", [False, True])
def test_initial_temperature_must_be_positive_finite(temperature, enabled):
    with pytest.raises(ValueError, match="vision_qk_temperature.*positive.*finite"):
        _block(vision_qk_norm=enabled, vision_qk_temperature=temperature)


def test_detached_diagnostics_match_joint_attention_and_refresh():
    torch.manual_seed(11)
    block = _block(vision_qk_norm=True, vision_qk_temperature=2.0)
    assert block.qk_stats == {}
    x, h = torch.randn(2, 16, 2, 2), torch.randn(2, 8, 2, 2)
    _, _, mass = block(x, h, return_attn=True)
    raw = [block.W_q(x), block.W_kx(x), block._keys_h(h)]
    q, kx, kh = [F.normalize(_tokens(t), dim=-1) for t in raw]
    scores = 2.0 * torch.cat([q @ kx.transpose(-1, -2), q @ kh.transpose(-1, -2)], -1)
    weights = scores.softmax(-1)
    expected = {"score_std": scores.std(unbiased=False), "score_min": scores.min(),
                "score_max": scores.max(),
                "attn_entropy": -(weights * weights.clamp_min(1e-12).log()).sum(-1).mean(),
                "mass_x": mass[:, 0].mean(), "mass_h": mass[:, 1].mean(),
                "temperature": torch.tensor(2.0)}
    expected.update({name: t.float().norm(dim=1).mean()
                     for name, t in zip(("q_norm", "kx_norm", "kh_norm"), raw)})
    assert set(block.qk_stats) == set(expected)
    for key, value in block.qk_stats.items():
        assert value.ndim == 0 and not value.requires_grad and value.grad_fn is None
        torch.testing.assert_close(value, expected[key])
    # Zero keys/queries imply a uniform joint distribution, not two softmaxes.
    block(torch.zeros_like(x), torch.zeros_like(h))
    assert block.qk_stats["score_std"].item() == 0.0
    assert block.qk_stats["attn_entropy"].item() == pytest.approx(math.log(8))
    assert block.qk_stats["mass_x"].item() == 0.5
    assert block.qk_stats["mass_h"].item() == 0.5
    assert block.qk_stats["kh_norm"].item() == 0.0
    off = _block()
    off(x, h)
    assert off.qk_stats == {}


@pytest.mark.parametrize("zero_inputs", [False, True])
def test_split_diagnostics_report_mean_per_stream_entropy_nats(zero_inputs):
    torch.manual_seed(11)
    block = _block(softmax_mode="split", vision_qk_norm=True, vision_qk_temperature=2.0)
    make = torch.zeros if zero_inputs else torch.randn
    x, h = make(2, 16, 2, 2), make(2, 8, 2, 2)
    block(x, h)
    q, kx, kh = [F.normalize(_tokens(t), dim=-1)
                 for t in (block.W_q(x), block.W_kx(x), block._keys_h(h))]
    ax, ah = [(q @ k.transpose(-1, -2) * 2.0).softmax(-1) for k in (kx, kh)]
    ex, eh = [-(a * a.clamp_min(1e-12).log()).sum(-1).mean() for a in (ax, ah)]
    torch.testing.assert_close(block.qk_stats["attn_entropy"], (ex + eh) / 2)
    torch.testing.assert_close(block.qk_stats["attn_entropy_x"], ex)
    torch.testing.assert_close(block.qk_stats["attn_entropy_h"], eh)
    for key in ("mass_x", "mass_h"):
        assert block.qk_stats[key].item() == pytest.approx(1.0)
    for value in block.qk_stats.values():
        assert value.ndim == 0 and not value.requires_grad and value.grad_fn is None
    if zero_inputs:
        assert block.qk_stats["attn_entropy"].item() == pytest.approx(math.log(4))
        assert block.qk_stats["attn_entropy"].item() != pytest.approx(2 * math.log(4))


def _trainer_expression(node, namespace):
    """Exercise actual trainer wiring without executing its training loop."""
    return eval(compile(ast.Expression(node), "<trainer expression>", "eval"), namespace)


@pytest.mark.parametrize("extra, enabled, initial", [
    ([], False, None), (["--vision-qk-norm"], True, None),
    (["--vision-qk-norm", "--vision-qk-temperature", "3.5"], True, 3.5),
    (["--vision-qk-norm", "--softmax-mode", "split", "--mem-every", "3"], True, None),
])
def test_cli_model_checkpoint_roundtrip(extra, enabled, initial):
    import pretrain_kda_convmem as trainer
    args = trainer.build_parser().parse_args([
        "--attn-mode", "token", "--n-channels", "8", "--kda-heads", "2",
        "--kda-head-dim", "4", "--map-size", "4", "--proto-dim", "16",
        "--v-mode", "learned_all", "--readout", "h2", *extra])
    assert args.vision_qk_norm is enabled
    assert args.vision_qk_temperature == initial
    tree = ast.parse(inspect.getsource(trainer.main))
    constructor = next(n for n in ast.walk(tree) if isinstance(n, ast.Call)
                       and isinstance(n.func, ast.Name) and n.func.id == "KDAConvMemoryModel")
    namespace = dict(vars(trainer), args=args, device=torch.device("cpu"))
    model = _trainer_expression(constructor, namespace)
    assert model.vision.vision_qk_norm is enabled
    assert model.vision.softmax_mode == model.memory.softmax_mode == args.softmax_mode
    if enabled:
        assert model.vision.log_temperature.exp().item() == pytest.approx(initial or math.sqrt(8))
        with torch.no_grad():
            model.vision.log_temperature.add_(0.2)  # distinguish learned state from init metadata
    teacher = copy.deepcopy(model)
    save_call = next(n for n in ast.walk(tree) if isinstance(n, ast.Call)
                     and isinstance(n.func, ast.Attribute) and n.func.attr == "save"
                     and isinstance(n.func.value, ast.Name) and n.func.value.id == "torch")
    namespace.update(model=model, jepa_teacher=teacher, col=0,
                     env=SimpleNamespace(theta=65.0))
    payload = _trainer_expression(save_call.args[0], namespace)
    assert payload["vision_qk_norm"] is enabled
    assert payload["vision_qk_temperature"] == initial
    assert payload["vision_attn_entropy_semantics"] == (
        ("mean_per_stream_nats" if args.softmax_mode == "split" else "joint_nats")
        if enabled else None)
    assert payload["softmax_mode"] == args.softmax_mode
    assert payload["mem_every"] == args.mem_every
    storage = io.BytesIO()
    torch.save(payload, storage)
    storage.seek(0)
    checkpoint = torch.load(storage, map_location="cpu", weights_only=False)
    constructor_keys = inspect.signature(KDAConvMemoryModel).parameters
    restored = KDAConvMemoryModel(**{k: v for k, v in checkpoint.items() if k in constructor_keys})
    restored.load_state_dict(checkpoint["model_state_dict"], strict=True)
    restored_teacher = copy.deepcopy(restored)
    restored_teacher.load_state_dict(checkpoint["jepa_teacher_state_dict"], strict=True)
    for key, value in model.state_dict().items():
        assert torch.equal(value, restored.state_dict()[key])
        assert torch.equal(value, restored_teacher.state_dict()[key])


@pytest.mark.parametrize("temperature", ["0", "-1", "nan", "inf", "-inf"])
def test_cli_rejects_invalid_temperature(temperature, capsys):
    from pretrain_kda_convmem import build_parser
    with pytest.raises(SystemExit) as exc:
        build_parser().parse_args([f"--vision-qk-temperature={temperature}"])
    assert exc.value.code == 2
    assert "positive and finite" in capsys.readouterr().err


@pytest.mark.parametrize("enabled", [False, True])
@pytest.mark.parametrize("softmax_mode", ["joint", "split"])
def test_trainer_metrics_csv_opt_in_uses_detached_last_step_stats(enabled, softmax_mode):
    import pretrain_kda_convmem as trainer
    block = _block(vision_qk_norm=enabled, softmax_mode=softmax_mode)
    block(torch.randn(2, 16, 2, 2), torch.randn(2, 8, 2, 2))
    base_fields = ["collection", "n_trials", "loss_total", "loss_jepa_ce", "loss_jepa_var",
                   "loss_jepa_cov", "loss_change", "change_acc", "change_acc_all",
                   "grad_norm", "theta", "elapsed_s"]
    tree = ast.parse(inspect.getsource(trainer.main))
    field_assignment = next(n for n in ast.walk(tree) if isinstance(n, ast.Assign)
                            and any(isinstance(t, ast.Name) and t.id == "fieldnames" for t in n.targets))
    namespace = dict(vars(trainer), args=SimpleNamespace(vision_qk_norm=enabled, softmax_mode=softmax_mode),
                     model=SimpleNamespace(vision=block), acc={})
    namespace["fieldnames"] = _trainer_expression(field_assignment.value, namespace)
    # Execute only the QKN logging branches, NOT collection/optimizer/training code.
    for node in ast.walk(tree):
        if isinstance(node, ast.If) and ast.unparse(node.test) == "args.vision_qk_norm":
            exec(compile(ast.Module(body=[node], type_ignores=[]), "<metric wiring>", "exec"), namespace)
    expected = {"vision_" + k: float(v) for k, v in block.qk_stats.items()}
    assert namespace["fieldnames"][:len(base_fields)] == base_fields
    assert set(namespace["fieldnames"][len(base_fields):]) == set(expected)
    assert namespace["acc"] == expected
    row = dict.fromkeys(base_fields, 0.0)
    row.update(namespace["acc"])
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(namespace["fieldnames"])
    writer.writerow([row[k] for k in namespace["fieldnames"]])
    output.seek(0)
    restored = next(csv.DictReader(output))
    for key, value in expected.items():
        assert float(restored[key]) == pytest.approx(value)


@pytest.mark.skipif(not torch.cuda.is_available(), reason="CUDA required for fp16 autocast")
def test_fp16_autocast_zero_h1_has_finite_projection_gradients():
    torch.manual_seed(17)
    block = _block(vision_qk_norm=True).cuda()
    x = torch.randn(2, 16, 2, 2, device="cuda")
    h = torch.zeros(2, 8, 2, 2, device="cuda")
    with torch.autocast("cuda", dtype=torch.float16):
        _, att, mass = block(x, h, return_attn=True)
    assert mass.dtype == torch.float32
    assert torch.isfinite(att).all()
    (att.float().square().mean() * 1024).backward()
    for name in ("W_q.weight", "W_kx.weight", "W_kh.weight", "log_temperature"):
        grad = dict(block.named_parameters())[name].grad
        assert grad is not None and torch.isfinite(grad).all(), name


def test_cli_help_allows_qkn_joint_or_split_sum():
    from pretrain_kda_convmem import build_parser
    parser = build_parser()
    help_text = " ".join(parser.format_help().split())
    assert "joint or split" in help_text
    assert "sum the mixes" in help_text


def test_default_temperature_is_sqrt_full_channel_width():
    block = _block(vision_qk_norm=True)
    assert block.log_temperature.ndim == 0
    assert block.log_temperature.exp().item() == pytest.approx(math.sqrt(8))
