"""
Why does the affine (Γ·X + β) variant orient to the cue when multiplicative variants do not?

Loads ONE checkpoint at a time (CPU). For each variant in the matched family we report:
  (1) cue-frame (t=1) attention to the cued patch — the headline contrast;
  (2) validity-scaled orienting (cued − uncued at t=1).

For affine ONLY we decompose the mechanism at the cue frame:
  • attn_mod   — actual attention on modulated tokens X′ = Γ·X + β
  • attn_raw   — counterfactual SA on unmodulated X (same W_Q/K/V)
  • beta cue-bias — β[cue] − mean(β[uncued])
  • ||ΔΓ|| at cued patch — scale-matrix deviation from identity
  • X′ cue-bias — ||X′[cue]|| − mean(||X′[uncued]||)

Hypothesis: affine decouples memory from the Q/K Hadamard gate — memory reshapes X
before plain self-attention, so visually salient cues can drive orienting even when
multiplicative feedback would suppress Q when H is weak or uniform.

Usage:
    python RViT_plus_paper_softmaxhead/analysis/cue_orienting_diagnosis.py
    python RViT_plus_paper_softmaxhead/analysis/cue_orienting_diagnosis.py affine standard two_lstm
"""
from __future__ import annotations

import glob
import os
import sys

import numpy as np
import torch

_HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _HERE)

from config.loader import load_checkpoint_weights  # noqa: E402
from envs import make_env                              # noqa: E402
from model import RViTPaperModel                       # noqa: E402
from paper_encoder import AffineModulatedSelfAttention  # noqa: E402

CK = os.path.expanduser("~/rvit_plus_checkpoints")
OUT = os.path.join(_HERE, "analysis", "deepdive_out")
T = 7
VALIDITIES = [0.25, 0.5, 0.75, 1.0]
N = 200

VARIANTS = [
    ("standard",  "paper_vae_frozen",    dict(feedback="multiplicative")),
    ("affine",    "paper_affine_vae",    dict(feedback="affine")),
    ("affine2lstm", "paper_affine2lstm_vae", dict(feedback="affine", two_lstm=True)),
    ("dualhead",  "paper_dualhead_vae",  dict(feedback="dualhead")),
    ("two_lstm",  "paper_2lstm_vae",     dict(feedback="multiplicative", two_lstm=True)),
    ("crossattn", "paper_crossattn_vae", dict(feedback="crossattn")),
    ("dualmem",   "paper_dualmem_vae",   dict(feedback="dualmem")),
]


def spatial_attn(feedback: str, out: dict) -> np.ndarray:
    A = out["attn"][0]
    if isinstance(A, list):
        A = A[0]
    a = A[0]
    if feedback in ("crossattn", "dualmem"):
        a = a[:, :4]
    return a.mean(0).detach().cpu().numpy()


def h_prev_from_state(model, enc_state):
    if model.encoder.two_lstm:
        return enc_state[0][0]
    return enc_state[0]


def collect_cue_metrics(model, env, feedback: str, validity: float = 1.0):
    """Forced-wait rollouts; return per-frame cued/uncued attention + affine decomposition."""
    cued = np.zeros(T)
    uncued = np.zeros(T)
    attn_raw = np.zeros(T)
    beta_bias = np.zeros(T)
    gamma_dev_cue = np.zeros(T)
    xp_norm_bias = np.zeros(T)

    is_affine = isinstance(model.encoder.attn, AffineModulatedSelfAttention)

    for _ in range(N):
        o = env.reset()
        cue = env.cue_index
        rest = [j for j in range(4) if j != cue]
        env.proportion = float(validity)
        env.change_true = 0
        s = model.init_states(1)
        for t in range(T):
            x = torch.from_numpy(o).float().permute(2, 0, 1).unsqueeze(0)
            enc_state, t_idx = s
            if is_affine:
                X = model.front(model._to_bchw(x), t_idx)
                H_prev = h_prev_from_state(model, enc_state)
                _, _, mod = model.encoder.attn(X, H_prev, return_attn=True, return_modulation=True)
                aw_x = model.encoder.attn.attention_on(X)[0].mean(0).detach().cpu().numpy()
                attn_raw[t] += aw_x[cue]
                beta = mod["beta"][0].detach().cpu().numpy()
                beta_bias[t] += beta[cue].mean() - beta[rest].mean()
                gamma_dev_cue[t] += mod["gamma_dev"][0, cue].item()
                xp = mod["Xp"][0].detach().cpu().numpy()
                xp_norm_bias[t] += np.linalg.norm(xp[cue]) - np.mean([np.linalg.norm(xp[j]) for j in rest])

            out = model.rl_step(x, s, return_attn=True)
            s = out["new_states"]
            a = spatial_attn(feedback, out)
            cued[t] += a[cue]
            uncued[t] += a[rest].mean()
            o, _, done, _ = env.step(0)

    scale = 1.0 / N
    return dict(
        cued=cued * scale,
        uncued=uncued * scale,
        delta=(cued - uncued) * scale,
        attn_raw=attn_raw * scale,
        beta_bias=beta_bias * scale,
        gamma_dev_cue=gamma_dev_cue * scale,
        xp_norm_bias=xp_norm_bias * scale,
    )


def load_variant(name, ck_dir, kw):
    path = sorted(glob.glob(f"{CK}/{ck_dir}/*.pt"), key=os.path.getmtime, reverse=True)
    if not path:
        return None, None, None
    path = path[0]
    m = RViTPaperModel(n_quantiles=5, seq_len=7, **kw)
    load_checkpoint_weights(m, path, strict=True, device=torch.device("cpu"))
    m.eval()
    it = torch.load(path, map_location="cpu", weights_only=False).get("iter")
    return m, it, path


def main():
    only = set(sys.argv[1:]) if len(sys.argv) > 1 else set()
    env = make_env("validity4", curriculum=False)
    os.makedirs(OUT, exist_ok=True)

    summary = []
    by_validity = {}
    affine_decomp = None

    print("=== Cue-orienting diagnosis (100% validity, forced wait) ===\n")
    print(f"{'variant':>10} {'iter':>6} {'t1 cued':>8} {'t1 Δ':>8} {'peak Δ':>8} {'strong':>8}")
    print("-" * 58)

    for name, ck_dir, kw in VARIANTS:
        if only and name not in only:
            continue
        m, it, path = load_variant(name, ck_dir, kw)
        if m is None:
            print(f"{name:>10}  (no checkpoint)")
            continue
        fb = kw["feedback"]
        m100 = collect_cue_metrics(m, env, fb, validity=1.0)
        t1_cued = float(m100["cued"][1])
        t1_delta = float(m100["delta"][1])
        peak_delta = float(m100["delta"].max())
        summary.append((name, it, t1_cued, t1_delta, peak_delta, path))
        print(f"{name:>10} {str(it):>6} {t1_cued:8.3f} {t1_delta:+8.3f} {peak_delta:+8.3f} "
              f"{'YES' if t1_cued > 0.35 else 'no':>8}")

        by_validity[name] = {}
        for v in VALIDITIES:
            mv = collect_cue_metrics(m, env, fb, validity=v)
            by_validity[name][v] = dict(t1_cued=float(mv["cued"][1]), t1_delta=float(mv["delta"][1]))

        if name == "affine":
            affine_decomp = m100
            print("\n--- Affine mechanism decomposition (100% cue) ---")
            for label, t in [("cue frame t=1", 1), ("pre-change t=3-4 mean", None)]:
                if t is None:
                    idx = slice(3, 5)
                    tag = "t3-4"
                else:
                    idx = t
                    tag = f"t={t}"
                print(f"  [{tag}] attn cued (X′): {np.mean(m100['cued'][idx]):.3f}  "
                      f"attn cued (raw X): {np.mean(m100['attn_raw'][idx]):.3f}  "
                      f"mod gain: {np.mean(m100['cued'][idx] - m100['attn_raw'][idx]):+.3f}")
            t = 1
            print(f"  β cue-bias:     {m100['beta_bias'][t]:+.4f}")
            print(f"  ||ΔΓ||@cue:     {m100['gamma_dev_cue'][t]:.4f}")
            print(f"  ||X′|| cue-bias:{m100['xp_norm_bias'][t]:+.4f}\n")

        del m

    print("--- Mechanistic contrast ---")
    print("  Multiplicative: Q = (X·W) ⊙ (H·W) — memory gates Q/K/V.")
    print("  Affine:         X′ = Γ(H)·X + β(H); then plain SA on X′.")
    print("  If affine mod gain >> 0 at t=1, Γ/β amplifies cue before attention.\n")

    np.savez(
        os.path.join(OUT, "cue_orienting_diagnosis.npz"),
        summary=np.array(summary, dtype=object),
        by_validity=by_validity,
        affine_decomp=affine_decomp or {},
        validities=VALIDITIES,
    )
    print(f"Saved → {OUT}/cue_orienting_diagnosis.npz")

    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        fig, axes = plt.subplots(1, 2, figsize=(9, 3.5))
        names = [s[0] for s in summary]
        t1 = [s[2] for s in summary]
        colors = ["#1b9e77" if n == "affine" else "#888888" for n in names]
        axes[0].bar(names, t1, color=colors)
        axes[0].axhline(0.25, ls=":", c="k", lw=0.8)
        axes[0].set_ylabel("attention to cued patch")
        axes[0].set_title("Cue frame (t=1), 100% validity")
        axes[0].tick_params(axis="x", rotation=30)

        if affine_decomp is not None:
            frames = np.arange(T)
            axes[1].plot(frames, affine_decomp["cued"], "-o", label="attn (X′)", ms=4)
            axes[1].plot(frames, affine_decomp["attn_raw"], "--s", label="attn (raw X)", ms=4)
            axes[1].axhline(0.25, ls=":", c="k", lw=0.8)
            axes[1].axvline(1, ls="--", c="0.5")
            axes[1].set_xlabel("frame")
            axes[1].set_title("Affine: modulated vs counterfactual")
            axes[1].legend(frameon=False, fontsize=8)

        fig.tight_layout()
        figpath = os.path.join(OUT, "fig_cue_orienting_diagnosis.pdf")
        fig.savefig(figpath)
        print(f"Figure → {figpath}")
    except Exception as e:
        print(f"Figure skipped: {e}")


if __name__ == "__main__":
    main()
