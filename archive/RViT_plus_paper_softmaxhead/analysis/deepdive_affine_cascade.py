"""
Full deep-dive battery for the affine_cascade model (paper codebase, frozen VAE, T=7).

affine_cascade = two affine transformers + two xLSTMs, cascade + SPLIT readout:
  T1(input X, feedback H1) -> Z1 -> H1=LSTM1(Z1)         [H1 -> CRITIC]
  T2(input Z1, feedback H2) -> Z2 -> H2=LSTM2(Z2)        [H2 -> ACTOR ]

Five experiments, mirroring the lab's canonical deep dive (exp1-5), adapted to this
architecture and to the paper validity4 task (UNIFORM reward, white cue — so NO colour/value
effect; we report critic calibration + uncertainty instead):
  exp1  behaviour   — psychometric (hit vs Δ, cued vs uncued, by reliability) + chronometric
  exp2  attention   — per-frame spatial maps for BOTH transformers + cued-patch timecourse
  exp3  decoding    — temporal linear decoding of cue-location / validity / change-location /
                      time from H1 (critic memory) vs H2 (actor memory)
  exp4  causal      — bias each transformer's attention -> effect on the DECISION (hit, actor)
                      vs the CRITIC's uncertainty (the split-readout dissociation)
  exp5  value       — critic calibration (predicted V vs realised return), value timecourse,
                      outcome uncertainty vs change magnitude
Each experiment saves its own .npz under analysis/deepdive_out/affine_cascade/ so a later
failure never loses earlier results. Loads ONE model (CPU, thread-capped). No figures here
(see make_affine_cascade_figs.py)."""
from __future__ import annotations
import os, sys, glob
import numpy as np
import torch

_HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _HERE)
from model import RViTPaperModel                       # noqa: E402
from config.loader import load_checkpoint_weights      # noqa: E402
from envs import make_env                              # noqa: E402

CKPT = os.path.expanduser("~/rvit_plus_checkpoints/paper_affine_cascade_vae/affine_cascade_dd_snapshot.pt")
OUT = os.path.join(_HERE, "analysis", "deepdive_out", "affine_cascade")
os.makedirs(OUT, exist_ok=True)
T = 7
PROPORTIONS = [0.25, 0.5, 0.75, 1.0]
DELTAS = [4, 8, 16, 24, 40, 64]
DEV = torch.device("cpu")


def load_model():
    m = RViTPaperModel(n_quantiles=5, seq_len=7, feedback="affine_cascade")
    load_checkpoint_weights(m, CKPT, strict=True, device=DEV); m.eval()
    it = torch.load(CKPT, map_location="cpu", weights_only=False).get("iter")
    return m, it


def _x(o):
    return torch.from_numpy(o).float().permute(2, 0, 1).unsqueeze(0)


def attn_maps(out):
    """affine_cascade returns out['attn'][0] = [aw1(T1), aw2(T2)], each (1,4,4).
    Spatial map = attention received per patch = mean over queries → (4,)."""
    a1, a2 = out["attn"][0]
    return a1[0].mean(0).numpy(), a2[0].mean(0).numpy()


def hs(out):
    enc = out["new_states"][0]
    return enc[0][0][0].numpy(), enc[1][0][0].numpy()      # H1, H2  (4,1024) each


# ── exp1: behaviour ───────────────────────────────────────────────────────────
def run_trial(m, env, proportion, delta, cued, change=True):
    o = env.reset(); env.proportion = float(proportion); env.change_true = 1 if change else 0
    cue = env.cue_index; env.change_index = cue if cued else (3 if cue == 0 else 0)
    if change: env.orientation_change = float(delta) * (1.0 if np.random.rand() < .5 else -1.0)
    s = m.init_states(1); done = False; r = 0; rt = None; t = 0
    while not done:
        with torch.no_grad():
            out = m.rl_step(_x(o), s); s = out["new_states"]; a = int(torch.argmax(out["actor_logits"], -1))
        o, r, done, _ = env.step(a)
        if a == 1 and rt is None: rt = t
        t += 1
    return (r > 0), rt


def exp1_behaviour(m, env, n_per=50):
    resp = np.zeros((len(PROPORTIONS), len(DELTAS), 2)); rt = np.full_like(resp, np.nan)
    for vi, v in enumerate(PROPORTIONS):
        for di, d in enumerate(DELTAS):
            for ci, cued in enumerate([False, True]):
                hits, rts = [], []
                for _ in range(n_per):
                    h, t = run_trial(m, env, v, d, cued)
                    hits.append(h);  rts.append(t) if (h and t is not None) else None
                resp[vi, di, ci] = np.mean(hits)
                if rts: rt[vi, di, ci] = np.mean(rts)
    fa = np.zeros(len(PROPORTIONS))
    for vi, v in enumerate(PROPORTIONS):
        p = []
        for _ in range(n_per * 2):
            o = env.reset(); env.proportion = float(v); env.change_true = 0
            s = m.init_states(1); done = False; pressed = False
            while not done:
                with torch.no_grad():
                    out = m.rl_step(_x(o), s); s = out["new_states"]; a = int(torch.argmax(out["actor_logits"], -1))
                o, _, done, _ = env.step(a); pressed = pressed or (a == 1)
            p.append(pressed)
        fa[vi] = np.mean(p)
    np.savez(os.path.join(OUT, "exp1_behaviour.npz"), resp=resp, rt=rt, fa=fa,
             proportions=PROPORTIONS, deltas=DELTAS)
    print(f"[exp1] cued hit@Δ64 {resp[:,-1,1].mean():.3f} | FA {fa.mean():.3f}", flush=True)


# ── exp2: attention allocation (both transformers) ────────────────────────────
def exp2_attention(m, env, n=120):
    # per-frame T1/T2 maps for cue@S1 with/without change; cued-patch timecourse by condition
    conds = {}
    for name, change in [("nochange", False), ("change", True)]:
        a1 = np.zeros((T, 4)); a2 = np.zeros((T, 4)); frames = None
        for k in range(n):
            o = env.reset(); env.cue_index = 0; env.proportion = 1.0
            env.change_true = 1 if change else 0; env.change_index = 0
            if change: env.orientation_change = 60.0
            s = m.init_states(1); fr = []
            for t in range(T):
                if k == 0: fr.append(np.asarray(o).squeeze().copy())
                with torch.no_grad():
                    out = m.rl_step(_x(o), s, return_attn=True); s = out["new_states"]
                m1, m2 = attn_maps(out); a1[t] += m1; a2[t] += m2
                o, _, done, _ = env.step(0)
            if k == 0: frames = np.stack(fr)
        conds[name] = dict(T1=a1 / n, T2=a2 / n, frames=frames)
    # cue-following timecourse: FORCE the cue at S1 then at S4 (no change → PURE cue-driven),
    # record attention to BOTH cue locations (S1=idx0, S4=idx3) per transformer. A cue-follower
    # attends whichever location is cued; a position-biased stream does not. Same forced-cue
    # protocol as the maps above, so the two figures are directly consistent.
    tc = {}
    for cuepos in (0, 3):
        acc = {k: np.zeros(T) for k in ("T1_S1", "T1_S4", "T2_S1", "T2_S4")}
        for _ in range(n):
            o = env.reset(); env.cue_index = cuepos; env.proportion = 1.0; env.change_true = 0
            s = m.init_states(1)
            for t in range(T):
                with torch.no_grad():
                    out = m.rl_step(_x(o), s, return_attn=True); s = out["new_states"]
                m1, m2 = attn_maps(out)
                acc["T1_S1"][t] += m1[0]; acc["T1_S4"][t] += m1[3]
                acc["T2_S1"][t] += m2[0]; acc["T2_S4"][t] += m2[3]
                o, _, done, _ = env.step(0)
        tc[f"cue{cuepos}"] = {k: v / n for k, v in acc.items()}
    np.savez(os.path.join(OUT, "exp2_attention.npz"), conds=conds, timecourse=tc)
    # cue-following: does attention to the CUED location swap when the cue moves S1<->S4?
    t1_follow = tc["cue0"]["T1_S1"][5] - tc["cue3"]["T1_S1"][5]   # >0 if T1 tracks the cue
    t2_follow = tc["cue0"]["T2_S1"][5] - tc["cue3"]["T2_S1"][5]
    print(f"[exp2] T1 cue@S1 attends S1 t5={tc['cue0']['T1_S1'][5]:.2f} | cue@S4 attends S1 t5={tc['cue3']['T1_S1'][5]:.2f} "
          f"(follow Δ={t1_follow:+.2f}); T2 follow Δ={t2_follow:+.2f}", flush=True)


# ── exp3: latent decoding from H1 vs H2 ───────────────────────────────────────
def exp3_decoding(m, env, n=400):
    from sklearn.linear_model import LogisticRegression
    from sklearn.model_selection import cross_val_score
    H1 = np.zeros((n, T, 4096)); H2 = np.zeros((n, T, 4096))
    y_cue = np.zeros(n); y_val = np.zeros(n); y_chgloc = np.zeros(n); y_chg = np.zeros(n)
    for i in range(n):
        o = env.reset(); env.proportion = float(np.random.choice(PROPORTIONS))
        cue = env.cue_index; y_cue[i] = (cue == 0); y_val[i] = env.proportion
        y_chg[i] = env.change_true
        y_chgloc[i] = env.change_index if env.change_true == 1 else -1
        s = m.init_states(1)
        for t in range(T):
            with torch.no_grad():
                out = m.rl_step(_x(o), s); s = out["new_states"]
            h1, h2 = hs(out); H1[i, t] = h1.ravel(); H2[i, t] = h2.ravel()
            o, _, done, _ = env.step(0)

    def dec(X, y, mask=None):  # balanced 3-fold CV accuracy per frame
        acc = np.zeros(T)
        idx = np.ones(len(y), bool) if mask is None else mask
        for t in range(T):
            Xt = X[idx, t]; yt = y[idx]
            if len(np.unique(yt)) < 2: acc[t] = np.nan; continue
            clf = LogisticRegression(max_iter=400, C=0.5)
            acc[t] = cross_val_score(clf, Xt, yt, cv=3, scoring="balanced_accuracy").mean()
        return acc
    res = dict(
        cue_H1=dec(H1, y_cue), cue_H2=dec(H2, y_cue),
        val_H1=dec(H1, (y_val >= 0.75).astype(int)), val_H2=dec(H2, (y_val >= 0.75).astype(int)),
        chg_H1=dec(H1, y_chg), chg_H2=dec(H2, y_chg),
        chgloc_H1=dec(H1, y_chgloc, mask=(y_chg == 1)), chgloc_H2=dec(H2, y_chgloc, mask=(y_chg == 1)),
    )
    np.savez(os.path.join(OUT, "exp3_decoding.npz"), **res)
    print(f"[exp3] cue-loc decode pre-change(t4) H1 {res['cue_H1'][4]:.2f} H2 {res['cue_H2'][4]:.2f} "
          f"| change-loc post(t6) H1 {res['chgloc_H1'][6]:.2f} H2 {res['chgloc_H2'][6]:.2f}", flush=True)


# ── exp4: causal attention (split-readout dissociation) ───────────────────────
def _entropy(qd):  # quantile std of the PRESS distribution as an uncertainty proxy
    return qd[0, 1].std().item()


def exp4_causal(m, env, n=120, biases=(-6, -3, 0, 3, 6)):
    # clamp T1 or T2 attention TOWARD the changed patch; measure hit (actor) & critic uncertainty
    res = {}
    for lever in ("t1", "t2"):
        hit = np.zeros(len(biases)); ent = np.zeros(len(biases))
        for bi, b in enumerate(biases):
            hits, ents = [], []
            for _ in range(n):
                o = env.reset(); env.cue_index = 0; env.proportion = 1.0
                env.change_true = 1; env.change_index = 0; env.orientation_change = 18.0  # near-threshold
                s = m.init_states(1); done = False; r = 0; pressed_correct = False
                clamp = {lever: {0: float(b)}}
                last_ent = np.nan
                while not done:
                    with torch.no_grad():
                        out = m.rl_step(_x(o), s, attn_clamp=clamp); s = out["new_states"]
                        a = int(torch.argmax(out["actor_logits"], -1)); last_ent = _entropy(out["critic_q_dist"])
                    o, r, done, _ = env.step(a)
                hits.append(r > 0); ents.append(last_ent)
            hit[bi] = np.mean(hits); ent[bi] = np.nanmean(ents)
        res[f"hit_{lever}"] = hit; res[f"ent_{lever}"] = ent
    np.savez(os.path.join(OUT, "exp4_causal.npz"), biases=np.array(biases), **res)
    print(f"[exp4] hit Δ(+6 vs -6): T1 {res['hit_t1'][-1]-res['hit_t1'][0]:+.3f}  "
          f"T2 {res['hit_t2'][-1]-res['hit_t2'][0]:+.3f}", flush=True)


# ── exp5: value / critic calibration ──────────────────────────────────────────
def exp5_value(m, env, n=300, gamma=0.95):
    # value timecourse (change vs no-change), calibration (pred V vs MC return), unc vs Δ
    vt_chg = np.zeros(T); vt_noc = np.zeros(T); n_chg = n_noc = 0
    preds, rets = [], []
    unc_by_d = {d: [] for d in DELTAS}
    for i in range(n):
        change = i % 2
        o = env.reset(); env.proportion = 1.0; env.change_true = change; env.cue_index = 0
        env.change_index = 0
        d = int(np.random.choice(DELTAS));
        if change: env.orientation_change = float(d)
        s = m.init_states(1); done = False; vs = []; rewards = []; t = 0; unc_post = None
        while not done:
            with torch.no_grad():
                out = m.rl_step(_x(o), s); s = out["new_states"]
                a = int(torch.argmax(out["actor_logits"], -1))
                vs.append(float(out["V_scalar"][0]))
                if change and t == 5: unc_post = out["critic_q_dist"][0, 1].std().item()
            o, r, done, _ = env.step(a); rewards.append(r); t += 1
        # per-step predicted value vs discounted return-to-go (gives calibration variance)
        rtg = 0.0; rtgs = []
        for r in reversed(rewards): rtg = r + gamma * rtg; rtgs.append(rtg)
        rtgs = rtgs[::-1]
        for vt, gt in zip(vs, rtgs): preds.append(vt); rets.append(gt)
        L = len(vs)
        if change: vt_chg[:L] += np.array(vs); n_chg += 1
        else: vt_noc[:L] += np.array(vs); n_noc += 1
        if change and unc_post is not None: unc_by_d[d].append(unc_post)
    vt_chg /= max(n_chg, 1); vt_noc /= max(n_noc, 1)
    unc = np.array([np.mean(unc_by_d[d]) if unc_by_d[d] else np.nan for d in DELTAS])
    np.savez(os.path.join(OUT, "exp5_value.npz"), vt_chg=vt_chg, vt_noc=vt_noc,
             preds=np.array(preds), rets=np.array(rets), unc=unc, deltas=DELTAS)
    cc = np.corrcoef(preds, rets)[0, 1]
    print(f"[exp5] value calib r={cc:.3f}  unc(Δ4)={unc[0]:.3f}→unc(Δ64)={unc[-1]:.3f}", flush=True)


def main():
    only = set(sys.argv[1:])
    m, it = load_model()
    print(f"[dd] affine_cascade snapshot iter={it}  params={sum(p.numel() for p in m.parameters()):,}", flush=True)
    env = make_env("validity4", curriculum=False)
    exps = [("exp1", exp1_behaviour), ("exp2", exp2_attention), ("exp3", exp3_decoding),
            ("exp4", exp4_causal), ("exp5", exp5_value)]
    for name, fn in exps:
        if only and name not in only: continue
        try:
            fn(m, env)
        except Exception as e:
            import traceback; print(f"[{name}] FAILED: {e}"); traceback.print_exc()
    print("DD DONE", flush=True)


if __name__ == "__main__":
    main()
