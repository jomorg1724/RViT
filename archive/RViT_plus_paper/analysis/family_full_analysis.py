"""
Per-model atlas: for EVERY variant, compute (a) attention maps at every time point for two
conditions [cue 100% @ S1, no change] and [cue 100% @ S1, visible change @ S1], with the
attention split into image vs memory token streams for the cross-attention variants;
(b) attention scores (the same maps, tabulated); (c) psychometric and (d) chronometric
functions. Models are loaded ONE AT A TIME (CPU, thread-capped) and each model's results are
written to its own npz immediately, so the job is safe to run alongside nothing-heavy and
resumable in spirit. No figures here — see make_atlas_figs.py (reads the npz, no torch)."""
from __future__ import annotations
import sys, os, glob
import numpy as np
import torch

_HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _HERE)
from model import RViTPaperModel                       # noqa: E402
from config.loader import load_checkpoint_weights      # noqa: E402
from envs import make_env                              # noqa: E402

CK = os.path.expanduser("~/rvit_plus_checkpoints")
OUT = os.path.join(_HERE, "analysis", "deepdive_out", "family_atlas")
os.makedirs(OUT, exist_ok=True)
T = 7
VALIDITIES = [0.25, 0.5, 0.75, 1.0]
DELTAS = [4, 8, 16, 24, 40, 64]
N_PER = 40            # psychometric trials per (validity, delta, cued)
N_ATTN = 150          # attention-map trials per condition
VISIBLE = 60.0        # "visible change" magnitude for the change condition

# most-recent-first (the user's 5 newest, then the standard reference, then older exploratory)
MODELS = [
    ("dualmem",  "paper_dualmem_vae",   dict(feedback="dualmem")),
    ("crossattn","paper_crossattn_vae", dict(feedback="crossattn")),
    ("two_lstm", "paper_2lstm_vae",     dict(feedback="multiplicative", two_lstm=True)),
    ("dualhead", "paper_dualhead_vae",  dict(feedback="dualhead")),
    ("affine",   "paper_affine_vae",    dict(feedback="affine")),
    ("standard", "paper_vae_frozen",    dict(feedback="multiplicative")),
    ("hyper",    "paper_hyper_vae",     dict(feedback="hyper")),
    ("hypercb",  "paper_hypercb_vae",   dict(feedback="hyper_codebook")),
]


def attn_split(feedback, out):
    """Return {token_source: (4,) attention received per spatial patch}."""
    A = out["attn"][0]
    if isinstance(A, (list, tuple)):                              # dualhead → two heads
        return {"sensory": A[0][0].mean(0).detach().numpy(),
                "feedback": A[1][0].mean(0).detach().numpy()}
    a = A[0]                                                      # (Q, K)
    if feedback == "crossattn":                                  # K = [X(4) ‖ H1(4)]
        return {"image": a[:, :4].mean(0).detach().numpy(),
                "memory": a[:, 4:8].mean(0).detach().numpy()}
    if feedback == "dualmem":                                    # K = [X(4) ‖ H1(4) ‖ H2(4)]
        return {"image":  a[:, :4].mean(0).detach().numpy(),
                "mem_H1": a[:, 4:8].mean(0).detach().numpy(),
                "mem_H2": a[:, 8:12].mean(0).detach().numpy()}
    return {"image": a.mean(0).detach().numpy()}                 # plain 4×4 self-attention


def attention_maps(m, env, feedback):
    """Two conditions × 7 frames; maps averaged over N_ATTN trials; input frames from trial 0."""
    conds = {}
    frames = {}
    for cond, change in [("nochange", False), ("change", True)]:
        acc = None
        for k in range(N_ATTN):
            o = env.reset()
            env.cue_index = 0; env.proportion = 1.0          # force 100% cue at S1
            env.change_true = 1 if change else 0
            env.change_index = 0
            if change: env.orientation_change = VISIBLE
            s = m.init_states(1); fr = []
            for t in range(T):
                if k == 0: fr.append(np.asarray(o).squeeze().copy())
                x = torch.from_numpy(o).float().permute(2, 0, 1).unsqueeze(0)
                with torch.no_grad():
                    out = m.rl_step(x, s, return_attn=True); s = out["new_states"]
                d = attn_split(feedback, out)
                if acc is None:
                    acc = {src: np.zeros((T, 4)) for src in d}
                for src, v in d.items():
                    acc[src][t] += v
                o, _, done, _ = env.step(0)                  # forced wait → full timecourse
            if k == 0: frames[cond] = np.stack(fr)
        conds[cond] = {src: acc[src] / N_ATTN for src in acc}
    return conds, frames


def run_trial(m, env, validity, delta, cued, change=True):
    o = env.reset(); env.proportion = float(validity); env.change_true = 1 if change else 0
    cue = env.cue_index
    env.change_index = cue if cued else (3 if cue == 0 else 0)
    if change: env.orientation_change = float(delta) * (1.0 if np.random.rand() < 0.5 else -1.0)
    s = m.init_states(1); done = False; r = 0; rt = None; t = 0
    while not done:
        x = torch.from_numpy(o).float().permute(2, 0, 1).unsqueeze(0)
        with torch.no_grad():
            out = m.rl_step(x, s); s = out["new_states"]; a = int(torch.argmax(out["actor_logits"], -1))
        o, r, done, _ = env.step(a)
        if a == 1 and rt is None: rt = t
        t += 1
    return (r > 0), rt


def psychometrics(m, env):
    resp = np.zeros((len(VALIDITIES), len(DELTAS), 2)); rt = np.full_like(resp, np.nan)
    for vi, val in enumerate(VALIDITIES):
        for di, dl in enumerate(DELTAS):
            for ci, cued in enumerate([False, True]):
                hits, rts = [], []
                for _ in range(N_PER):
                    h, t = run_trial(m, env, val, dl, cued, True)
                    hits.append(h)
                    if h and t is not None: rts.append(t)
                resp[vi, di, ci] = np.mean(hits)
                if rts: rt[vi, di, ci] = np.mean(rts)
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


def main():
    only = set(sys.argv[1:])                                    # optional model-name filter
    env = make_env("validity4", curriculum=False)
    for name, d, kw in MODELS:
        if only and name not in only: continue
        paths = sorted(glob.glob(f"{CK}/{d}/*.pt"), key=os.path.getmtime, reverse=True)
        if not paths:
            print(f"[{name}] no checkpoint — skip", flush=True); continue
        try:
            m = RViTPaperModel(n_quantiles=5, seq_len=7, **kw)
            load_checkpoint_weights(m, paths[0], strict=True, device=torch.device("cpu")); m.eval()
        except Exception as e:
            print(f"[{name}] load failed: {e}", flush=True); continue
        it = torch.load(paths[0], map_location="cpu", weights_only=False).get("iter")
        print(f"[{name}] iter={it} — attention maps ...", flush=True)
        amaps, frames = attention_maps(m, env, kw["feedback"])
        print(f"[{name}] psychometrics ...", flush=True)
        resp, rt, fa = psychometrics(m, env)
        np.savez(os.path.join(OUT, f"{name}.npz"),
                 name=name, iter=it, feedback=kw["feedback"],
                 amaps=amaps, frames=frames,
                 resp=resp, rt=rt, fa=fa,
                 validities=VALIDITIES, deltas=DELTAS)
        hit = resp[:, :, 1].mean(); fam = fa.mean()
        print(f"[{name}] saved → {name}.npz  (mean cued-hit {hit:.3f}, mean FA {fam:.3f})", flush=True)
        del m
    print("ALL DONE", flush=True)


if __name__ == "__main__":
    main()
