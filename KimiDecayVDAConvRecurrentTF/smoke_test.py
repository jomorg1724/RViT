"""
Smoke test for the KDA visual-accumulator conv recurrent transformer (VDA16).

NOT a training run. Builds the model in each accum_mode, pushes one random
(B=2, T=7, 100, 100, 3) batch through forward_seq on CPU, checks shapes and
finiteness, and verifies that gradients flow back into every parameter group
(stem, accumulator, vision, memory, heads). Run when ready:

    python smoke_test.py                # all three accum modes
    python smoke_test.py --mode kda     # one mode only
"""
from __future__ import annotations

import argparse

import torch

from kda_conv_memory_model import KDAConvMemoryModel

B, T, S, C, MAP = 2, 7, 100, 128, 16


def check_mode(mode: str) -> None:
    torch.manual_seed(0)
    model = KDAConvMemoryModel(n_channels=C, proto_dim=64, map_size=MAP,
                               memory_noise_std=0.05, accum_mode=mode,
                               accum_decay=0.5, kda_heads=4, kda_head_dim=32)
    obs = torch.randn(B, T, S, S, 3).clamp(-1, 1)

    R_seq, stats = model.forward_seq(obs, return_stats=True)
    assert R_seq.shape == (B, T, 4 * C, MAP, MAP), f"{mode}: R_seq shape {tuple(R_seq.shape)}"
    assert torch.isfinite(R_seq).all(), f"{mode}: non-finite values in R_seq"
    assert len(stats) == T and "alpha_mean" in stats[0] and "beta_mean" in stats[0]
    if mode == "kda":
        assert "err_norm" in stats[0], "kda: expected err_norm diagnostic"
        assert torch.isfinite(stats[-1]["err_norm"]), "kda: non-finite err_norm"

    logits = model.classify(R_seq[:, -1])
    assert logits.shape == (B, 2), f"{mode}: logits shape {tuple(logits.shape)}"
    z = model.jepa_logits(R_seq)
    assert z.shape == (B, T, MAP, MAP, 64), f"{mode}: jepa logits shape {tuple(z.shape)}"

    # gradient flow: one scalar loss over the whole sequence, full BPTT;
    # the JEPA head is only engaged via jepa_logits, so z must be in the loss
    loss = R_seq.float().pow(2).mean() + logits.float().pow(2).mean() + z.float().pow(2).mean()
    loss.backward()
    missing = [n for n, p in model.named_parameters()
               if p.grad is None or not torch.isfinite(p.grad).all()]
    assert not missing, f"{mode}: params without finite gradients: {missing[:5]}..."

    # state shapes
    H1, H2, ACC = model.init_state(B, "cpu", torch.float32)
    assert H1.shape == H2.shape == (B, C, MAP, MAP)
    if mode == "kda":
        assert ACC.shape == (B, 4, 32, 32, MAP * MAP), f"kda: state {tuple(ACC.shape)}"
    else:
        assert ACC.shape == (B, C, MAP, MAP), f"{mode}: state {tuple(ACC.shape)}"

    n_params = sum(p.numel() for p in model.parameters())
    print(f"[smoke:{mode}] OK  R_seq={tuple(R_seq.shape)}  params={n_params:,}  "
          f"alpha0={stats[0]['alpha_mean']:.3f} beta0={stats[0]['beta_mean']:.3f}"
          + (f"  err0={stats[0]['err_norm']:.3f}" if mode == "kda" else ""))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["ema", "gated", "kda"], default=None)
    args = ap.parse_args()
    modes = [args.mode] if args.mode else ["ema", "gated", "kda"]
    for mode in modes:
        check_mode(mode)
    print("[smoke] all modes passed")


if __name__ == "__main__":
    main()
