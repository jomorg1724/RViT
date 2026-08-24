"""
Uniform per-model atlas for the SUCCESSFUL T=29 models (v5, v5_part2, v8, v11, v11_part2,
v11_part5). Each lives in its own codebase; this driver imports each project's shared
`_behav_utils` (or, for v11_part5, its `distractor_dd`) and produces ONE npz per model with
the SAME schema as the T=7 atlas:
  - attention maps (10x10) at EVERY frame, for [cue100%@S1 no-change] and [cue100%@S1 visible
    change@S1], split by token source. CROSS-ATTENTION models (v5,v5_part2,v8) expose
    separate IMAGE-key and MEMORY-key (H1,H2) maps; DUAL-STREAM models (v11,v11_part2,
    v11_part5) expose per-stream memory maps (salience->H1/H2, topdown->H2) since the image
    is the QUERY there (no image keys).
  - psychometric (cued vs uncued x validity) + chronometric (RT) + false-alarm rate.
Models are loaded ONE AT A TIME (CPU, thread-capped). Run: python t29_atlas_analysis.py [names...]
"""
from __future__ import annotations
import sys, os, importlib
import numpy as np
import torch

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")
os.makedirs(OUT, exist_ok=True)

CK = os.path.expanduser("~/rvit_plus_checkpoints")
DEVICE = torch.device("cpu")
VALIDITIES = [1.0, 0.75, 0.5, 0.25]
DELTAS = [4, 8, 16, 24, 40, 64]
N_ATTN = 80
N_PER = 40
CHANGE_T = 15          # fixed change onset (in [11,25]) for the attention change-condition
VISIBLE = 55.0         # clearly-visible orientation change (theta=64)

# name, package, checkpoint, attention-extraction kind, backend
MODELS = [
    ("v11_part2", "RViT_plus_v11_part2", f"{CK}/v11_part2/v11_part2_analysis_snapshot.pt", "dualstream_2N", "behav"),
    ("v5",        "RViT_plus_v5",        f"{CK}/v5/v5_analysis_snapshot_curr.pt",          "selfattn3N",    "behav"),
    ("v5_part2",  "RViT_plus_v5_part2",  f"{CK}/v5_part2/v5p2_analysis_snapshot.pt",        "crossattn3N",   "behav"),
    ("v8",        "RViT_plus_v8",        f"{CK}/v8/v8_analysis_snapshot.pt",                "crossattn3N",   "behav"),
    ("v11",       "RViT_plus_v11",       f"{CK}/v11/v11_analysis_snapshot.pt",              "dualstream_NN", "behav"),
    ("v11_part5", "RViT_plus_v11_part5", f"{CK}/v11_part5/rvit_plus_v11_part5_rl_latest.pt", "dualstream_2N", "distractor"),
]


def extract_maps(kind, attn, N, gh, gw):
    """attn = list of attention tensors from forward_step; return {src: (gh,gw)} batch-averaged."""
    g = lambda v: np.asarray(v).reshape(gh, gw)
    m = lambda a: a.mean(dim=(0, 1, 2)).detach().cpu().numpy()    # mean over batch,heads,queries -> (K,)
    if kind == "selfattn3N":                                     # v5: last layer, (B,h,3N,3N)
        v = m(attn[-1]); return {"image": g(v[:N]), "memory H1": g(v[N:2*N]), "memory H2": g(v[2*N:3*N])}
    if kind == "crossattn3N":                                    # v5_part2,v8: (B,h,N,3N)
        v = m(attn[0]); return {"image": g(v[:N]), "memory H1": g(v[N:2*N]), "memory H2": g(v[2*N:3*N])}
    if kind == "dualstream_NN":                                  # v11: [sal(B,h,N,N), td(B,h,N,N)]
        return {"salience->H1": g(m(attn[0])), "topdown->H2": g(m(attn[1]))}
    if kind == "dualstream_2N":                                  # v11_part2/part5: sal(B,h,N,2N), td(B,h,N,N)
        sa = m(attn[0]); return {"salience->H1": g(sa[:N]), "salience->H2": g(sa[N:2*N]),
                                 "topdown->H2": g(m(attn[1]))}
    raise ValueError(kind)


def attn_rollout(ctx, envs, obs0, kind):
    B = len(envs); states = ctx["init_states"](B, device=DEVICE); obs = list(obs0)
    N, gh, gw, T = ctx["N"], ctx["gh"], ctx["gw"], envs[0].T
    acc = None; frames = []
    for t in range(T):
        frames.append(np.asarray(obs[0], dtype=np.float32).copy())
        x = ctx["obs_to_tensor"](obs, DEVICE); tokens = ctx["patch_embed"](x)
        states, attn = ctx["forward_attn"](tokens, states)
        d = extract_maps(kind, attn, N, gh, gw)
        if acc is None: acc = {k: np.zeros((T, gh, gw)) for k in d}
        for k, v in d.items(): acc[k][t] = v
        for i in range(B):
            o, _, _, _ = envs[i].step(0); obs[i] = o
    return acc, np.stack(frames)


# ── standard backend (v5, v5_part2, v8, v11, v11_part2) ──────────────────────────
def make_behav_ctx(pkg, ckpt):
    bu = importlib.import_module(f"{pkg}.analysis._behav_utils")
    cfg = bu.load_config(); model = bu.build_model(cfg, DEVICE); it = bu.load_checkpoint(model, ckpt, DEVICE)
    model.eval()
    def forward_attn(tokens, states):
        ret = model.encoder.forward_step(tokens, states, return_attn=True)
        return ret[0], ret[-1]
    ctx = dict(model=model, bu=bu, it=it, init_states=model.init_states, patch_embed=model.patch_embed,
               obs_to_tensor=bu._obs_to_tensor, N=model.n_tokens,
               gh=model.patch_embed.grid_h, gw=model.patch_embed.grid_w, forward_attn=forward_attn)
    return ctx


def behav_attn_envs(ctx, change, rng):
    bu = ctx["bu"]
    spec = bu.ForcedTrialSpec(cue_position="left", cue_color="red", proportion=1.0,
                              change_true=1 if change else 0,
                              change_time=CHANGE_T if change else None,
                              change_index_mode="cued" if change else None,
                              orientation_mag=VISIBLE if change else None)
    return bu.build_env_batch(spec, N_ATTN, rng)


def behav_psycho(ctx, rng):
    bu = ctx["bu"]
    resp = np.zeros((len(VALIDITIES), len(DELTAS), 2)); rt = np.full_like(resp, np.nan)
    for vi, val in enumerate(VALIDITIES):
        for di, dl in enumerate(DELTAS):
            for ci, cued in enumerate([False, True]):
                spec = bu.ForcedTrialSpec(cue_position="left", cue_color="red", proportion=val,
                                          change_true=1, change_index_mode="cued" if cued else "uncued",
                                          orientation_mag=float(dl))
                envs, obs0 = bu.build_env_batch(spec, N_PER, rng)
                r = bu.batched_behavior_rollout(ctx["model"], envs, obs0, DEVICE)
                resp[vi, di, ci] = r["hit"].mean()
                rr = r["rt"][r["hit"]]
                if rr.size: rt[vi, di, ci] = float(np.nanmean(rr))
    fa = np.zeros(len(VALIDITIES))
    for vi, val in enumerate(VALIDITIES):
        spec = bu.ForcedTrialSpec(cue_position="left", cue_color="red", proportion=val, change_true=0)
        envs, obs0 = bu.build_env_batch(spec, N_PER * 2, rng)
        r = bu.batched_behavior_rollout(ctx["model"], envs, obs0, DEVICE)
        fa[vi] = r["pressed"].mean()
    return resp, rt, fa


# ── distractor backend (v11_part5) — same cued task with distractors OFF ──────────
def make_distractor_ctx(pkg, ckpt):
    dd = importlib.import_module(f"{pkg}.analysis.distractor_dd")
    env_mod = importlib.import_module(f"{pkg}.env")
    cfg = dd.load_config(); model = dd.build_model(cfg, DEVICE); it = dd.load_checkpoint(model, ckpt, DEVICE)
    model.eval()
    SIDE = env_mod.SIDE_QUADRANTS
    def forward_attn(tokens, states):
        ret = dd.dual_stream_step(model.encoder, tokens, states, return_attn=True)
        return ret[0], ret[-1]
    def make_env(): return env_mod.ChangeDetectionEnv(distractor_prob=0.0)
    ctx = dict(model=model, dd=dd, env_mod=env_mod, SIDE=SIDE, it=it, init_states=model.init_states,
               patch_embed=model.patch_embed, obs_to_tensor=dd._obs_to_tensor, N=model.n_tokens,
               gh=model.patch_embed.grid_h, gw=model.patch_embed.grid_w, forward_attn=forward_attn,
               make_env=make_env)
    return ctx


def _distractor_trial(ctx, val, change_true, cued, ori_mag, change_time, rng):
    e = ctx["make_env"](); e.reset()
    e.cue_position = "left"; e.cue_color = "red"; e.proportion = float(val)
    e.change_true = int(change_true); e.distractor_true = 0
    if change_true:
        prim = ctx["SIDE"]["left"]["primary"]; unc = ctx["SIDE"]["right"]["primary"]
        e.change_index = prim if cued else unc
        e.change_time = int(change_time)
        e.orientation_change = float(ori_mag) * (1.0 if rng.random() < 0.5 else -1.0)
    e.t = 0
    return e, e._next_observation()


def distractor_attn_envs(ctx, change, rng):
    envs, obs0 = [], []
    for _ in range(N_ATTN):
        e, o = _distractor_trial(ctx, 1.0, 1 if change else 0, True, VISIBLE, CHANGE_T, rng)
        envs.append(e); obs0.append(o)
    return envs, obs0


def distractor_psycho(ctx, rng):
    dd = ctx["dd"]
    resp = np.zeros((len(VALIDITIES), len(DELTAS), 2)); rt = np.full_like(resp, np.nan)
    for vi, val in enumerate(VALIDITIES):
        for di, dl in enumerate(DELTAS):
            for ci, cued in enumerate([False, True]):
                envs, obs0 = [], []
                for _ in range(N_PER):
                    e, o = _distractor_trial(ctx, val, 1, cued, float(dl), int(rng.integers(11, 26)), rng)
                    envs.append(e); obs0.append(o)
                r = dd.record_rollout(ctx["model"], envs, obs0, DEVICE, policy="argmax")
                resp[vi, di, ci] = r["hit"].mean()
                rr = r["rt"][r["hit"]]
                if rr.size: rt[vi, di, ci] = float(np.nanmean(rr))
    fa = np.zeros(len(VALIDITIES))
    for vi, val in enumerate(VALIDITIES):
        envs, obs0 = [], []
        for _ in range(N_PER * 2):
            e, o = _distractor_trial(ctx, val, 0, True, 0.0, CHANGE_T, rng)
            envs.append(e); obs0.append(o)
        r = dd.record_rollout(ctx["model"], envs, obs0, DEVICE, policy="argmax")
        fa[vi] = r["pressed"].mean()
    return resp, rt, fa


def run_model(name, pkg, ckpt, kind, backend):
    rng = np.random.default_rng(0)
    if backend == "behav":
        ctx = make_behav_ctx(pkg, ckpt)
        attn_envs = lambda ch: behav_attn_envs(ctx, ch, rng)
        psycho = lambda: behav_psycho(ctx, rng)
    else:
        ctx = make_distractor_ctx(pkg, ckpt)
        attn_envs = lambda ch: distractor_attn_envs(ctx, ch, rng)
        psycho = lambda: distractor_psycho(ctx, rng)
    print(f"[{name}] iter={ctx['it']} grid={ctx['gh']}x{ctx['gw']} N={ctx['N']} — attention maps ...", flush=True)
    amaps, frames = {}, {}
    for cond, ch in [("nochange", False), ("change", True)]:
        envs, obs0 = attn_envs(ch)
        amaps[cond], frames[cond] = attn_rollout(ctx, envs, obs0, kind)
    print(f"[{name}] psychometrics ...", flush=True)
    resp, rt, fa = psycho()
    np.savez(os.path.join(OUT, f"{name}.npz"), name=name, iter=ctx["it"], kind=kind,
             arch_family=("crossattn" if kind in ("selfattn3N", "crossattn3N") else "dualstream"),
             amaps=amaps, frames=frames, resp=resp, rt=rt, fa=fa,
             validities=VALIDITIES, deltas=DELTAS, gh=ctx["gh"], gw=ctx["gw"], change_t=CHANGE_T)
    print(f"[{name}] saved (mean cued-hit {resp[:,:,1].mean():.3f}, FA {fa.mean():.3f})", flush=True)
    del ctx


def main():
    only = set(sys.argv[1:])
    for name, pkg, ckpt, kind, backend in MODELS:
        if only and name not in only: continue
        if not os.path.exists(ckpt):
            print(f"[{name}] checkpoint missing: {ckpt}", flush=True); continue
        try:
            run_model(name, pkg, ckpt, kind, backend)
        except Exception as e:
            import traceback; print(f"[{name}] FAILED: {e}", flush=True); traceback.print_exc()
    print("ALL DONE", flush=True)


if __name__ == "__main__":
    main()
