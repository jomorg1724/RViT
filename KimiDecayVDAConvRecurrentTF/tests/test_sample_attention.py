"""Categorical row sampling: exact hard forward, softmax surrogate backward."""
import inspect
import pytest
import torch
import torch.nn.functional as F
import kda_conv_memory_model as mod


def test_rowwise_categorical_exact_forward_and_surrogate_backward():
    sample = getattr(mod, "_sample_attention_st", None)
    assert callable(sample), "missing categorical STE helper"
    torch.manual_seed(314)
    logits = torch.randn(3, 11, 5, dtype=torch.float64, requires_grad=True)
    p = logits.softmax(-1)
    rng = torch.get_rng_state()
    a = sample(p)
    assert torch.equal(a.sum(-1), torch.ones_like(a[..., 0]))
    assert ((a == 0) | (a == 1)).all()
    torch.set_rng_state(rng)
    assert torch.equal(a, sample(p))
    values = torch.randn(5, 7, dtype=torch.float64, requires_grad=True)
    upstream = torch.randn(3, 11, 7, dtype=torch.float64)
    ((a @ values) * upstream).sum().backward()
    expected = torch.autograd.grad(((logits.softmax(-1) @ values.detach()) * upstream).sum(), logits)[0]
    torch.testing.assert_close(logits.grad, expected, rtol=0, atol=0)
    torch.testing.assert_close(values.grad, a.detach().flatten(0, 1).T @ upstream.flatten(0, 1), rtol=0, atol=0)


def test_nonuniform_empirical_sampling_independent_rows_calls_no_grad():
    sample = getattr(mod, "_sample_attention_st", None)
    assert callable(sample), "missing categorical STE helper"
    p = torch.tensor([0.1, 0.3, 0.6]).expand(4, 3000, 3)
    torch.manual_seed(21)
    with torch.no_grad():
        a, b = sample(p), sample(p)
    torch.testing.assert_close(a.mean((0, 1)), p[0, 0], atol=0.015, rtol=0)
    assert not torch.equal(a, b)
    assert all(not torch.equal(a[0], a[i]) for i in range(1, 4))
    assert a.argmax(-1).unique().numel() == 3


def config(**kwargs):
    result = dict(n_channels=8, proto_dim=16, map_size=4, accum_mode="kda",
                  kda_heads=2, kda_head_dim=4, attn_mode="token", softmax_mode="split",
                  readout="h2", v_mode="learned_all", cls_head="conv", mem_every=3,
                  memory_noise_std=0.0, vision_qk_norm=True)
    result.update(kwargs)
    return result


@pytest.mark.parametrize("memory", [False, True])
def test_blocks_sample_separate_rows_sum_and_preserve_soft_diagnostics(memory):
    cls = mod.ConvMemoryBlock if memory else mod.ConvAttentionBlock
    assert "sample_attention" in inspect.signature(cls).parameters
    kw = dict(c=8, map_size=2, attn_mode="token", softmax_mode="split", learned_v=True,
              sample_attention=True)
    if not memory:
        kw.update(in_c=16, vision_qk_norm=True)
    torch.manual_seed(82)
    block = cls(**kw).eval()
    x = torch.randn(3, 8 if memory else 16, 2, 2)
    h = torch.randn(3, 8, 2, 2)
    tokens = lambda t: t.flatten(2).transpose(1, 2)
    q = block.W_q(h if memory else x)
    kx = block.W_kz(x) if memory else block.W_kx(x)
    kh = block.W_kh(h)
    if not memory:
        q, kx, kh = [F.normalize(t, dim=1) for t in (q, kx, kh)]
    q, kx, kh = map(tokens, (q, kx, kh))
    scale = block.scale if memory else block.log_temperature.exp()
    px, ph = [(q @ k.transpose(-1, -2) * scale).softmax(-1) for k in (kx, kh)]
    torch.manual_seed(127)
    ax, ah = mod._sample_attention_st(px), mod._sample_attention_st(ph)
    expected = (ax @ tokens(block.V_X) + ah @ tokens(block.V_H)).transpose(1, 2).reshape(3, 8, 2, 2)
    captured = []
    handle = block.ffn.register_forward_pre_hook(lambda m, args: captured.append(args[0]))
    with torch.no_grad():
        torch.manual_seed(127)
        out1 = block(x, h)
        torch.manual_seed(127)
        out2 = block(x, h)
        out3 = block(x, h)
    handle.remove()
    torch.testing.assert_close(captured[0], expected, rtol=0, atol=0)
    assert torch.equal(out1[1], out2[1]) and not torch.equal(out2[1], out3[1])
    assert not torch.equal(ax, ah)
    if not memory:
        entropy = sum(-(p * p.clamp_min(1e-12).log()).sum(-1).mean() for p in (px, ph)) / 2
        torch.testing.assert_close(block.qk_stats["attn_entropy"], entropy)
        assert block.qk_stats["mass_x"] == block.qk_stats["mass_h"] == 1


@pytest.mark.parametrize("incompatible", [dict(attn_mode="pixel_gate"), dict(softmax_mode="joint"),
                                           dict(softmax_mode="colgate"), dict(acc_stream=True)])
def test_reject_incompatible_sampling(incompatible):
    assert "sample_attention" in inspect.signature(mod.KDAConvMemoryModel).parameters
    with pytest.raises(ValueError, match="sample_attention.*token.*split.*two.stream"):
        mod.KDAConvMemoryModel(**config(sample_attention=True, **incompatible))


def test_full_allv_c128_mem3_seven_steps_gradients():
    assert "sample_attention" in inspect.signature(mod.KDAConvMemoryModel).parameters
    torch.set_num_threads(2)
    torch.manual_seed(3)
    model = mod.KDAConvMemoryModel(**config(n_channels=128, kda_heads=4, kda_head_dim=32,
                                          sample_attention=True))
    assert model.sample_attention and model.vision.sample_attention and model.memory.sample_attention
    assert not hasattr(model.accumulator, "sample_attention")
    assert model.memory.scale == 128 ** -0.5 and not hasattr(model.memory, "log_temperature")
    r = model.forward_seq(torch.randn(2, 7, 16, 16, 3))
    F.cross_entropy(model.classify(r[:, -1]), torch.tensor([0, 1])).backward()
    for block in (model.vision, model.memory):
        for name, p in block.named_parameters():
            if name.startswith(("W_q", "W_k", "V_", "log_temperature")):
                assert p.grad is not None and torch.isfinite(p.grad).all(), name
                assert p.grad.abs().sum() > 0, name
