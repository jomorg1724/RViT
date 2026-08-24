"""
Deep-dive #1 — behaviour (Morgan & Herman Fig 3): psychometric & chronometric functions
of the STANDARD model (multiplicative + frozen VAE, T=7) by cue validity, cued vs uncued.

Controlled sweep: present a cue of a given validity, force the change at the cued (S1) or
uncued (S4) location with a fixed magnitude Δ, measure P(detect) and reaction time. Fit a
4-parameter logistic per condition and read off the threshold (Position) — the paper's
headline is that higher validity shifts the cued psychometric leftward (lower threshold).
"""
from __future__ import annotations
import sys, os, glob
import numpy as np
import torch

_HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _HERE)
from model import RViTPaperModel                       # noqa: E402
from config.loader import load_checkpoint_weights      # noqa: E402
from envs import make_env                              # noqa: E402

CKPT = os.path.expanduser("~/rvit_plus_checkpoints/paper_vae_frozen")
OUT = os.path.join(_HERE, "analysis", "deepdive_out")
os.makedirs(OUT, exist_ok=True)
VALIDITIES = [0.25, 0.5, 0.75, 1.0]
DELTAS = [2, 4, 8, 12, 16, 24, 40, 64]
N_PER = 60


def load_model():
    ck = sorted(glob.glob(CKPT + "/*.pt"), key=os.path.getmtime)[-1]
    m = RViTPaperModel(n_quantiles=5, seq_len=7, feedback="multiplicative")
    load_checkpoint_weights(m, ck, strict=True, device=torch.device("cpu")); m.eval()
    return m


def run_trial(m, env, validity, delta, cued, change=True):
    o = env.reset()
    env.proportion = float(validity)
    env.change_true = 1 if change else 0
    cue = env.cue_index
    env.change_index = cue if cued else (3 if cue == 0 else 0)
    if change:
        env.orientation_change = float(delta) * (1.0 if np.random.rand() < 0.5 else -1.0)
    s = m.init_states(1); done = False; r = 0; rt = None; t = 0
    while not done:
        x = torch.from_numpy(o).float().permute(2, 0, 1).unsqueeze(0)
        with torch.no_grad():
            out = m.rl_step(x, s); s = out["new_states"]; a = int(torch.argmax(out["actor_logits"], -1))
        o, r, done, _ = env.step(a)
        if a == 1 and rt is None: rt = t
        t += 1
    return (r > 0), rt          # detected (hit), reaction-time frame


def collect(m):
    env = make_env("validity4", curriculum=False)
    # change trials: response rate + RT over (validity, delta, cued)
    resp = np.zeros((len(VALIDITIES), len(DELTAS), 2))      # [val, delta, cued] mean detect
    rt = np.full((len(VALIDITIES), len(DELTAS), 2), np.nan)
    for vi, val in enumerate(VALIDITIES):
        for di, dl in enumerate(DELTAS):
            for ci, cued in enumerate([False, True]):
                hits, rts = [], []
                for _ in range(N_PER):
                    h, t = run_trial(m, env, val, dl, cued, change=True)
                    hits.append(h)
                    if h and t is not None: rts.append(t)
                resp[vi, di, ci] = np.mean(hits)
                if rts: rt[vi, di, ci] = np.mean(rts)
    # no-change false-alarm rate by validity
    fa = np.zeros(len(VALIDITIES))
    for vi, val in enumerate(VALIDITIES):
        pressed = []
        for _ in range(N_PER * 2):
            o = env.reset(); env.proportion = float(val); env.change_true = 0
            s = m.init_states(1); done = False; p = False
            while not done:
                x = torch.from_numpy(o).float().permute(2, 0, 1).unsqueeze(0)
                with torch.no_grad():
                    out = m.rl_step(x, s); s = out["new_states"]; a = int(torch.argmax(out["actor_logits"], -1))
                o, _, done, _ = env.step(a)
                if a == 1: p = True
            pressed.append(p)
        fa[vi] = np.mean(pressed)
    return resp, rt, fa


def logistic4(x, guess, lapse, slope, pos):
    return guess + (1 - guess - lapse) / (1 + np.exp(-slope * (x - pos)))


def fit_threshold(deltas, y):
    from scipy.optimize import curve_fit
    try:
        p, _ = curve_fit(logistic4, deltas, y, p0=[0.05, 0.05, 0.2, 16],
                         bounds=([0, 0, 0.001, 0], [0.5, 0.5, 5, 80]), maxfev=20000)
        return p          # guess, lapse, slope, pos(threshold)
    except Exception:
        return None


def main():
    m = load_model()
    print("[dd] collecting behaviour ...")
    resp, rt, fa = collect(m)
    np.savez(os.path.join(OUT, "behavior.npz"), resp=resp, rt=rt, fa=fa,
             validities=VALIDITIES, deltas=DELTAS)
    da = np.array(DELTAS, float)

    print("\n=== PSYCHOMETRIC THRESHOLDS (4-param logistic 'Position') ===")
    print(f"{'validity':>9} | {'cued thr':>9} {'uncued thr':>11} {'benefit(unc-cued)':>18}")
    thr = {}
    for vi, val in enumerate(VALIDITIES):
        fc = fit_threshold(da, resp[vi, :, 1]); fu = fit_threshold(da, resp[vi, :, 0])
        tc = fc[3] if fc is not None else np.nan
        tu = fu[3] if fu is not None else np.nan
        thr[val] = (tc, tu)
        print(f"{val:>9.2f} | {tc:>9.1f} {tu:>11.1f} {tu-tc:>18.1f}")
    print(f"\nFalse-alarm rate by validity: " +
          "  ".join(f"{v:.2f}:{fa[i]:.3f}" for i, v in enumerate(VALIDITIES)))

    # ── figure (Fig-3 style) ─────────────────────────────────────────────────
    try:
        import matplotlib; matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        fig, ax = plt.subplots(1, 3, figsize=(13, 4))
        xs = np.linspace(0, 64, 100)
        # A: cued psychometric by validity
        for vi, val in enumerate(VALIDITIES):
            ax[0].plot(da, resp[vi, :, 1], "o", color=plt.cm.viridis(vi/3))
            f = fit_threshold(da, resp[vi, :, 1])
            if f is not None: ax[0].plot(xs, logistic4(xs, *f), color=plt.cm.viridis(vi/3), label=f"{int(val*100)}%")
        ax[0].set(title="A. Cued psychometric by validity", xlabel="Δ (deg)", ylabel="P(detect)")
        ax[0].legend(title="validity")
        # B/C: cued vs uncued at 25% and 100%
        for k, vi in enumerate([0, 3]):
            for ci, lab, col in [(1, "cued", "C0"), (0, "uncued", "C3")]:
                ax[1+k].plot(da, resp[vi, :, ci], "o", color=col)
                f = fit_threshold(da, resp[vi, :, ci])
                if f is not None: ax[1+k].plot(xs, logistic4(xs, *f), color=col, label=lab)
            ax[1+k].set(title=f"{'B' if k==0 else 'C'}. {int(VALIDITIES[vi]*100)}% validity",
                        xlabel="Δ (deg)", ylabel="P(detect)"); ax[1+k].legend()
        fig.tight_layout(); fig.savefig(os.path.join(OUT, "fig_psychometric.pdf"))
        # chronometric
        fig2, ax2 = plt.subplots(figsize=(5, 4))
        for vi, val in enumerate(VALIDITIES):
            ax2.plot(da, rt[vi, :, 1], "-o", color=plt.cm.viridis(vi/3), label=f"{int(val*100)}%")
        ax2.set(title="Chronometric: RT vs Δ (cued)", xlabel="Δ (deg)", ylabel="RT (frames)"); ax2.legend(title="validity")
        fig2.tight_layout(); fig2.savefig(os.path.join(OUT, "fig_chronometric.pdf"))
        print(f"\n[dd] figures → {OUT}/fig_psychometric.pdf, fig_chronometric.pdf")
    except Exception as e:
        print(f"[dd] figure step skipped: {e}")
    print("[dd] done.")


if __name__ == "__main__":
    main()
