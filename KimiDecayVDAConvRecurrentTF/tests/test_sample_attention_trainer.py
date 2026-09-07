"""Execute real trainer AST slices (no environment collection or training launch)."""
import ast
import copy
import csv
import inspect
import io
from types import SimpleNamespace

import pytest
import torch
import pretrain_kda_convmem as trainer
from kda_conv_memory_model import KDAConvMemoryModel


def expression(node, ns):
    return eval(compile(ast.Expression(node), "<actual trainer expression>", "eval"), ns)


def execute(nodes, ns):
    exec(compile(ast.Module(body=nodes, type_ignores=[]), "<actual trainer slice>", "exec"), ns)


@pytest.mark.parametrize("sample,coef", [(False, 0.0), (True, 0.0), (True, 1e-6), (False, 1e-6)])
def test_cli_constructor_checkpoint_loss_and_csv(sample, coef):
    parser = trainer.build_parser()
    defaults = parser.parse_args([])
    assert hasattr(defaults, "sample_attention"), "missing sample-attention CLI"
    assert defaults.sample_attention is False and defaults.attention_entropy_coef == 0.0
    assert defaults.entropy_coef == 1e-5  # existing quantized H1 option unchanged
    args = parser.parse_args(["--n-channels", "8", "--proto-dim", "16", "--map-size", "4",
        "--kda-heads", "2", "--kda-head-dim", "4", "--attn-mode", "token", "--softmax-mode", "split",
        "--v-mode", "learned_all", "--readout", "h2", "--vision-qk-norm", "--mem-every", "3",
        "--jepa-coef", "0", "--attention-entropy-coef", str(coef),
        *(["--sample-attention"] if sample else [])])
    tree = ast.parse(inspect.getsource(trainer.main))
    ns = dict(vars(trainer), args=args, device=torch.device("cpu"))
    constructor = next(n for n in ast.walk(tree) if isinstance(n, ast.Call)
                       and isinstance(n.func, ast.Name) and n.func.id == "KDAConvMemoryModel")
    model = expression(constructor, ns)
    assert model.sample_attention is sample and model.attention_entropy_coef == coef
    assert model.memory.sample_attention is sample and model.vision.sample_attention is sample
    ns.update(model=model, jepa_teacher=copy.deepcopy(model), col=0, env=SimpleNamespace(theta=65.0))
    save = next(n for n in ast.walk(tree) if isinstance(n, ast.Call) and ast.unparse(n.func) == "torch.save")
    payload = expression(save.args[0], ns)
    assert payload["sample_attention"] is sample and payload["attention_entropy_coef"] == coef
    storage = io.BytesIO(); torch.save(payload, storage); storage.seek(0)
    restored = torch.load(storage, weights_only=False)
    keys = inspect.signature(KDAConvMemoryModel).parameters
    other = KDAConvMemoryModel(**{k: v for k, v in restored.items() if k in keys})
    other.load_state_dict(restored["model_state_dict"], strict=True)
    assert other.sample_attention is sample and other.attention_entropy_coef == coef

    # Real graph from soft probabilities; actual main loss slice, including H1 bonus.
    model.forward_seq(torch.randn(2, 7, 16, 16, 3))
    ns.update(jepa_loss=torch.tensor(0.0), change_loss=torch.tensor(0.75, requires_grad=True))
    inner = next(n for n in ast.walk(tree) if isinstance(n, ast.For)
                 and isinstance(n.target, ast.Name) and n.target.id == "mb")
    start = next(i for i, n in enumerate(inner.body) if isinstance(n, ast.Assign)
                 and any(isinstance(t, ast.Name) and t.id == "loss" for t in n.targets))
    end = next(i for i, n in enumerate(inner.body) if isinstance(n, ast.If)
               and "torch.isfinite(loss)" in ast.unparse(n.test))
    execute(inner.body[start:end], ns)
    ent = model.attention_entropy
    actual_bonus = -coef * ent if coef else 0.0
    torch.testing.assert_close(ns["loss"], ns["change_loss"] + actual_bonus, rtol=0, atol=0)
    assert float(ns["loss_attention_entropy"]) == pytest.approx(float(actual_bonus))
    if coef:
        actual_grad = torch.autograd.grad(ns["loss"], model.vision.log_temperature, retain_graph=True)[0]
        expected_grad = torch.autograd.grad(-coef * ent, model.vision.log_temperature)[0]
        torch.testing.assert_close(actual_grad, expected_grad, rtol=0, atol=0)
        assert actual_grad > 0

    field_assignment = next(n for n in ast.walk(tree) if isinstance(n, ast.Assign)
                           and any(isinstance(t, ast.Name) and t.id == "fieldnames" for t in n.targets))
    ns["fieldnames"] = expression(field_assignment.value, ns)
    ns["acc"] = {}
    branches = [n for n in ast.walk(tree) if isinstance(n, ast.If)
                and ast.unparse(n.test) == "args.sample_attention or args.attention_entropy_coef > 0"]
    assert len(branches) >= 3
    for branch in sorted(branches, key=lambda n: n.lineno):
        execute([branch], ns)
    expected_keys = {"attention_entropy", "loss_attention_entropy"} if sample or coef else set()
    assert set(ns["acc"]) == expected_keys
    assert set(ns["fieldnames"]) & {"attention_entropy", "loss_attention_entropy"} == expected_keys
    row = {k: ns["acc"].get(k, 0.0) for k in ns["fieldnames"]}
    out = io.StringIO(); writer = csv.DictWriter(out, fieldnames=ns["fieldnames"])
    writer.writeheader(); writer.writerow(row); out.seek(0)
    csv_row = next(csv.DictReader(out))
    if expected_keys:
        assert float(csv_row["attention_entropy"]) == pytest.approx(float(ent))
        assert float(csv_row["loss_attention_entropy"]) == pytest.approx(float(actual_bonus))


@pytest.mark.parametrize("coef", ["-1", "nan", "inf"])
def test_cli_rejects_invalid_attention_entropy_coef(coef, capsys):
    parser = trainer.build_parser()
    assert hasattr(parser.parse_args([]), "attention_entropy_coef")
    with pytest.raises(SystemExit) as exc:
        parser.parse_args(["--attention-entropy-coef=" + coef])
    assert exc.value.code == 2
    assert "nonnegative and finite" in capsys.readouterr().err
