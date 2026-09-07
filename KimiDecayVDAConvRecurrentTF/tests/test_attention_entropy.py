"""Raw soft-probability entropy, invocation weighting, and loss wiring."""
import inspect
import math
import pytest
import torch
import kda_conv_memory_model as mod
from test_sample_attention import config


def test_soft_entropy_bonus_gradient_and_hard_forward():
    assert "entropy_terms" in inspect.signature(mod._two_stream_token_attn).parameters
    q = torch.tensor([[[[2.0, 0.5]]]], requires_grad=True)
    k = torch.tensor([[[[1.0, -1.0]]]])
    v = torch.tensor([[[[2.0, 7.0]]]])
    terms = []
    att, masses = mod._two_stream_token_attn(q, k, k, v, v, 1.0, split=True,
                            sample_attention=True, entropy_terms=terms, entropy_grad=True)
    p = (q.flatten(2).transpose(1, 2) @ k.flatten(2)).softmax(-1)
    expected = -(p * p.log()).sum(-1).mean()
    assert len(terms) == 1 and terms[0].requires_grad
    torch.testing.assert_close(terms[0], expected, rtol=0, atol=0)
    assert ((att == 4) | (att == 9) | (att == 14)).all()
    assert torch.equal(masses, torch.ones_like(masses))
    (-1e-6 * terms[0]).backward()
    assert (q.grad > 0).all()  # gradient descent reduces nonuniform positive score gaps
    with torch.no_grad():
        p_new = ((q - q.grad * 1e6).flatten(2).transpose(1, 2) @ k.flatten(2)).softmax(-1)
    assert -(p_new * p_new.log()).sum(-1).mean() > expected


@pytest.mark.parametrize("return_stats", [False, True])
def test_sequence_entropy_actual_invocations_mem3_reset_and_soft_grad(return_stats):
    assert "attention_entropy_coef" in inspect.signature(mod.KDAConvMemoryModel).parameters
    torch.manual_seed(3)
    model = mod.KDAConvMemoryModel(**config(sample_attention=True, attention_entropy_coef=1e-6))
    records = {"vision": [], "memory": []}
    handles = [getattr(model, key).register_forward_hook(
        lambda block, args, out, key=key: records[key].append(block.attention_entropy)) for key in records]
    obs = torch.randn(2, 7, 16, 16, 3)
    model.forward_seq(obs, return_stats=return_stats)
    assert [len(records[k]) for k in records] == [7, 2]
    expected = torch.stack(records["vision"] + records["memory"]).mean()
    torch.testing.assert_close(model.attention_entropy, expected, rtol=0, atol=0)
    assert model.attention_entropy_count == 9
    assert model.attention_entropy.requires_grad and model.aux_entropy is None
    for key in records:
        torch.testing.assert_close(model.attention_entropy_stats[key], torch.stack(records[key]).mean())
        assert not model.attention_entropy_stats[key].requires_grad
    (-1e-6 * model.attention_entropy).backward()
    assert model.vision.log_temperature.grad > 0
    records["vision"].clear(); records["memory"].clear()
    model.forward_seq(obs[:, :2])
    assert model.attention_entropy_count == 2
    assert model.memory.attention_entropy is None
    assert model.attention_entropy_stats["memory"] is None
    torch.testing.assert_close(model.attention_entropy, torch.stack(records["vision"]).mean())
    for h in handles:
        h.remove()


@pytest.mark.parametrize("sample", [False, True])
def test_zero_coef_keeps_no_entropy_graph(sample):
    assert "attention_entropy_coef" in inspect.signature(mod.KDAConvMemoryModel).parameters
    model = mod.KDAConvMemoryModel(**config(sample_attention=sample))
    model.forward_seq(torch.randn(2, 4, 16, 16, 3))
    for obj in (model, model.vision, model.memory):
        ent = obj.attention_entropy
        if not sample or obj is model.memory:  # fourth step is off the mem3 cadence
            assert ent is None
        else:
            assert ent is not None and not ent.requires_grad and ent.grad_fn is None


@pytest.mark.parametrize("coef", [-1., float("nan"), float("inf")])
def test_invalid_entropy_coefficient_rejected(coef):
    assert "attention_entropy_coef" in inspect.signature(mod.KDAConvMemoryModel).parameters
    with pytest.raises(ValueError, match="attention_entropy_coef.*nonnegative.*finite"):
        mod.KDAConvMemoryModel(**config(attention_entropy_coef=coef))
