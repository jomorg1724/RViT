"""
Deep-dive analysis of the PARALLEL DUAL-STREAM v11 model trained on the
FRAME-REPEAT short task (7 logical frames, each held 5 physical steps = 35 steps;
change at logical frame 5 => physical step 25). value+validity environment.

Five experiments, matching the canonical v11 deep dive but with PHYSICAL
alignment for the held frames:
  exp1  behaviour      psychometric / chronometric / value-by-colour
  exp2  attention      salience vs top-down per-quadrant maps + S1 timecourse
  exp3  decoding       linear decode of task variables from H1 / H2 over time
  exp4  causal         bias each attention lever -> effect on decision vs value
  exp5  value          critic value timecourse, press advantage, uncertainty

Reuses dd_core (faithful bias-injectable dual-stream step) + _behav_utils
(model/env construction). Serial, thread-capped — one model, no fan-out.
"""
from __future__ import annotations
import os, sys, argparse
import numpy as np
import torch

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)
import dd_core as dd

# ── frame-repeat task geometry ────────────────────────────────────────────────
FR        = 5                       # physical steps per logical frame
N_FRAMES  = 7                       # logical frames
CHG_LOG   = 5                       # logical change frame
T_PHYS    = N_FRAMES * FR           # 35 physical steps
CHG_PHYS  = CHG_LOG * FR            # 25 physical change onset
ENV_KW    = dict(n_frames=N_FRAMES, min_change_time=CHG_LOG, max_change_time=CHG_LOG, frame_repeat=FR)
# The env's orientation change is in DEGREES, drawn from uniform(-theta, theta) with theta=64
# in training. So magnitudes must be on a 0–64° scale, not 0–1.
THETA_MAX = 64.0
DELTAS    = [0.0, 4.0, 8.0, 16.0, 28.0, 44.0, 64.0]   # |Δθ| sweep in degrees
MAG_VIS   = 56.0                                       # a clearly supra-threshold change
MAG_THR   = 24.0                                       # a near-threshold change (for causal headroom)
OUT       = os.path.join(_HERE, "out_framerepeat")
os.makedirs(OUT, exist_ok=True)


def _load(ckpt, device):
    cfg = dd.load_config()
    model = dd.build_model(cfg, device)
    dd.load_checkpoint(model, ckpt, device)
    model.eval()
    qidx = dd.quadrant_token_indices(model.patch_embed.grid_h, model.patch_embed.grid_w)
    return model, qidx


# ──────────────────────────────────────────────────────────────────────────────
# rollout helpers (frame-repeat aware)
# ──────────────────────────────────────────────────────────────────────────────
@torch.no_grad()
def greedy_rollout(model, envs, obs_list, device, *, bias=None, stop_on_press=True):
    """Greedy (argmax) rollout to T_PHYS. Returns correct (env reward>0), press_phys,
    pressed, and the critic entropy at the physical change frame."""
    B = len(envs)
    obs = dd._obs_to_tensor(obs_list, device)
    state = model.init_states(B, device=device)
    pressed = np.zeros(B, bool); press_phys = np.full(B, -1, np.int64)
    correct = np.zeros(B, bool); done = np.zeros(B, bool)
    ent_chg = np.full(B, np.nan, np.float32)
    for t in range(T_PHYS):
        tok = model.patch_embed(obs)
        state, rec, _ = dd.dual_stream_forward_step(model.encoder, tok, state, attn_bias=bias, return_attn=True)
        logits = dd.actor_decode(model.actor_head, rec)
        if t == CHG_PHYS:                                  # uncertainty at change onset
            q = model.critic_head(rec)                     # (B, A, Nq)
            ent_chg = dd.quantile_entropy(q[:, 1]).cpu().numpy()
        act = logits.argmax(-1).cpu().numpy()
        nxt = []
        for b in range(B):
            if done[b]:
                nxt.append(obs_list[b]); continue
            a = int(act[b])
            if a == 1 and not pressed[b]:
                pressed[b] = True; press_phys[b] = t
            o, r, d, _ = envs[b].step(a)
            nxt.append(o)
            if r > 0: correct[b] = True
            if d or (a == 1 and stop_on_press): done[b] = True
        obs = dd._obs_to_tensor(nxt, device); obs_list = nxt
        if done.all(): break
    return correct, press_phys, pressed, ent_chg


@torch.no_grad()
def forced_wait_record(model, envs, obs_list, device, qidx, *, bias=None):
    """Forced-wait (action 0) rollout to T_PHYS, recording faithful attention.
    Returns per-frame per-quadrant attention for each stream, per-quadrant pooled
    memories H1/H2, critic q for press, and actor logits."""
    B = len(envs)
    obs = dd._obs_to_tensor(obs_list, device)
    state = model.init_states(B, device=device)
    aq = {s: np.zeros((T_PHYS, B, 4), np.float32) for s in ("sal", "td")}    # quadrant attention
    amap = {s: np.zeros((T_PHYS, B, model.n_tokens), np.float32) for s in ("sal", "td")}
    memq = {m: np.zeros((T_PHYS, B, 4, model.encoder.d_mem), np.float32) for m in ("H1", "H2")}
    qpress = np.zeros((T_PHYS, B, model.n_quantiles), np.float32)
    vmean  = np.zeros((T_PHYS, B), np.float32)
    for t in range(T_PHYS):
        tok = model.patch_embed(obs)
        state, rec, attn = dd.dual_stream_forward_step(model.encoder, tok, state, attn_bias=bias, return_attn=True)
        for s, aw in zip(("sal", "td"), attn):
            a = aw.mean(dim=(1, 2)).cpu().numpy()          # (B, Nk) mean over heads+queries, sums to 1
            amap[s][t] = a
            for q in range(4):
                aq[s][t, :, q] = a[:, qidx[q]].sum(1)
        H1, H2 = state[0][0], state[0][1]                  # (B, N, d_mem)
        for m, Hm in (("H1", H1), ("H2", H2)):
            for q in range(4):
                memq[m][t, :, q] = Hm[:, qidx[q]].mean(1).cpu().numpy()
        qd = model.critic_head(rec)
        qpress[t] = qd[:, 1].cpu().numpy()
        logits = dd.actor_decode(model.actor_head, rec)
        _, vsc = model.critic_head.derive_V(qd, logits)
        vmean[t] = vsc.cpu().numpy()
        nxt = [envs[b].step(0)[0] for b in range(B)]
        obs = dd._obs_to_tensor(nxt, device)
    return dict(aq=aq, amap=amap, memq=memq, qpress=qpress, vmean=vmean)


def _spec(cue="left", color=None, prop=1.0, change=1, mode="cued", mag=None):
    return dd.ForcedTrialSpec(cue_position=cue, cue_color=color, proportion=prop,
                              change_true=change, change_index_mode=mode, orientation_mag=mag)


# ──────────────────────────────────────────────────────────────────────────────
# exp1  behaviour
# ──────────────────────────────────────────────────────────────────────────────
def exp1_behaviour(model, device, rng, n=60):
    print("[exp1] behaviour …", flush=True)
    # signal-detection decomposition on the natural 50/50 change / no-change mix.
    # reward is paid for BOTH a hit (press after a real change) AND a correct rejection
    # (waiting out a no-change trial), so overall accuracy = ½·hit + ½·CR.
    envs, obs = dd.build_env_batch(_spec("left", None, 1.0, None, "cued", None), 600, rng,
                                   env_kwargs=ENV_KW, randomize_color=True, randomize_cue_position=True)
    cor, pp, pr, _ = greedy_rollout(model, envs, obs, device)
    chg = np.array([e.change_true for e in envs]).astype(bool)
    sdt = dict(overall=float(cor.mean()), hit=float(cor[chg].mean()),
               correct_reject=float(cor[~chg].mean()), false_alarm=float(pr[~chg].mean()))
    # psychometric/chronometric: valid vs invalid x proportion x delta
    hit = np.zeros((len(dd.PROPORTIONS), 2, len(DELTAS)))
    rt  = np.full((len(dd.PROPORTIONS), 2, len(DELTAS)), np.nan)
    for pi, prop in enumerate(dd.PROPORTIONS):
        for vi, mode in enumerate(("cued", "uncued")):     # valid / invalid
            for di, dlt in enumerate(DELTAS):
                envs, obs = dd.build_env_batch(_spec("left", None, prop, 1, mode, dlt), n, rng,
                                               env_kwargs=ENV_KW, randomize_color=True)
                cor, pp, pr, _ = greedy_rollout(model, envs, obs, device)
                hit[pi, vi, di] = cor.mean()
                prt = pp[cor] - CHG_PHYS            # physical steps after change onset (within-frame deliberation)
                if cor.any(): rt[pi, vi, di] = np.median(prt)
    # value-by-colour at a near-threshold magnitude
    val_hit = {}; val_rt = {}
    for c in dd.COLORS:
        envs, obs = dd.build_env_batch(_spec("left", c, 1.0, 1, "cued", MAG_THR), 120, rng, env_kwargs=ENV_KW)
        cor, pp, pr, _ = greedy_rollout(model, envs, obs, device)
        val_hit[c] = float(cor.mean())
        prt = pp[cor] - CHG_PHYS
        val_rt[c] = float(np.median(prt)) if cor.any() else np.nan
    # false-alarm rate on no-change trials
    envs, obs = dd.build_env_batch(_spec("left", None, 1.0, 0, "cued", None), 200, rng,
                                   env_kwargs=ENV_KW, randomize_color=True)
    _, _, pr, _ = greedy_rollout(model, envs, obs, device)
    fa = float(pr.mean())
    np.savez(f"{OUT}/exp1_behaviour.npz", hit=hit, rt=rt, deltas=DELTAS, proportions=dd.PROPORTIONS,
             val_hit=np.array([val_hit[c] for c in dd.COLORS]),
             val_rt=np.array([val_rt[c] for c in dd.COLORS]), colors=dd.COLORS, false_alarm=fa,
             overall=sdt["overall"], hit_rate=sdt["hit"], correct_reject=sdt["correct_reject"],
             fa_nochange=sdt["false_alarm"])
    print(f"        OVERALL acc={sdt['overall']:.3f} (hit={sdt['hit']:.2f} CR={sdt['correct_reject']:.2f} "
          f"FA={sdt['false_alarm']:.3f}) | valid hit@Δ1={hit[0,0,-1]:.2f} invalid={hit[0,1,-1]:.2f} | "
          f"value r/g/b={val_hit['red']:.2f}/{val_hit['green']:.2f}/{val_hit['blue']:.2f}")


# ──────────────────────────────────────────────────────────────────────────────
# exp2  attention allocation
# ──────────────────────────────────────────────────────────────────────────────
def exp2_attention(model, device, rng, qidx, n=48):
    print("[exp2] attention …", flush=True)
    conds = [(p, side) for p in dd.PROPORTIONS for side in ("left", "right")]  # valid=left, invalid=right
    S1_sal = np.zeros((len(conds), T_PHYS)); S1_td = np.zeros((len(conds), T_PHYS))
    # spatial maps for the canonical valid cue (left, ring 1.0, change@S1)
    rec_main = None
    for ci, (prop, side) in enumerate(conds):
        # change ALWAYS at S1 (cued quadrant of a left cue); cue side varies validity
        envs, obs = dd.build_env_batch(_spec(side, None, prop, 1, ("cued" if side == "left" else "uncued"), MAG_VIS),
                                       n, rng, env_kwargs=ENV_KW, randomize_color=True)
        # force change at S1 (quadrant 0) regardless of cue side
        for e in envs: e.change_index = 0
        r = forced_wait_record(model, envs, obs, device, qidx)
        S1_sal[ci] = r["aq"]["sal"][:, :, 0].mean(1)       # S1 = quadrant 0
        S1_td[ci]  = r["aq"]["td"][:, :, 0].mean(1)
        if prop == 1.0 and side == "left":
            rec_main = {"sal_map": r["amap"]["sal"].mean(1), "td_map": r["amap"]["td"].mean(1),
                        "sal_quad": r["aq"]["sal"].mean(1), "td_quad": r["aq"]["td"].mean(1)}
    np.savez(f"{OUT}/exp2_attention.npz", S1_sal=S1_sal, S1_td=S1_td,
             conds=np.array([f"{p}_{s}" for p, s in conds]), chg_phys=CHG_PHYS, T=T_PHYS, fr=FR,
             grid_h=model.patch_embed.grid_h, grid_w=model.patch_embed.grid_w, **rec_main)
    sal_pre = S1_sal[0, CHG_PHYS-1]; td_pre = S1_td[0, CHG_PHYS-1]; td_post = S1_td[0, min(CHG_PHYS+3, T_PHYS-1)]
    print(f"        salience S1 pre-change={sal_pre:.2f}  top-down S1 pre={td_pre:.2f}->post={td_post:.2f}")


# ──────────────────────────────────────────────────────────────────────────────
# exp3  latent decoding
# ──────────────────────────────────────────────────────────────────────────────
def exp3_decoding(model, device, rng, qidx, n=320):
    print("[exp3] decoding …", flush=True)
    from sklearn.linear_model import LogisticRegression, Ridge
    from sklearn.model_selection import cross_val_score
    # randomized trials: color, proportion, change side
    colors, props, chg_q = [], [], []
    envs, obs = [], []
    for _ in range(n):
        c = dd.COLORS[rng.integers(3)]; p = dd.PROPORTIONS[rng.integers(4)]
        side = "left" if rng.random() < 0.5 else "right"
        e, o = dd.build_env_batch(_spec(side, c, p, 1, "cued", MAG_VIS), 1, rng, env_kwargs=ENV_KW)
        e[0].change_index = int(rng.integers(4))           # change location INDEPENDENT of the cue
        envs += e; obs += o
        colors.append(dd.COLORS.index(c)); props.append(dd.PROPORTIONS.index(p))
        chg_q.append(e[0].change_index)
    r = forced_wait_record(model, envs, obs, device, qidx)
    colors = np.array(colors); props = np.array(props); chg_q = np.array(chg_q)
    targets = {"cue_colour": (colors, "clf"), "cue_reliability": (props, "clf"),
               "change_quadrant": (chg_q, "clf")}
    acc = {mem: {k: np.zeros(T_PHYS) for k in targets} for mem in ("H1", "H2")}
    for mem in ("H1", "H2"):
        feat_all = r["memq"][mem].reshape(T_PHYS, n, -1)   # (T, n, 4*d_mem) per-quadrant pooled
        for t in range(T_PHYS):
            X = feat_all[t]
            X = (X - X.mean(0)) / (X.std(0) + 1e-6)
            for k, (y, kind) in targets.items():
                if kind == "clf":
                    clf = LogisticRegression(max_iter=200, C=0.5)
                    try: acc[mem][k][t] = cross_val_score(clf, X, y, cv=3, scoring="balanced_accuracy").mean()
                    except Exception: acc[mem][k][t] = np.nan
    np.savez(f"{OUT}/exp3_decoding.npz",
             **{f"{m}_{k}": acc[m][k] for m in acc for k in targets},
             chance_colour=1/3, chance_rel=1/4, chance_quad=1/4, chg_phys=CHG_PHYS, T=T_PHYS)
    print(f"        H2 colour@end={acc['H2']['cue_colour'][-1]:.2f}  "
          f"H2 change-quad@end={acc['H2']['change_quadrant'][-1]:.2f}  "
          f"H1 change-quad@end={acc['H1']['change_quadrant'][-1]:.2f}")


# ──────────────────────────────────────────────────────────────────────────────
# exp4  causal attention levers
# ──────────────────────────────────────────────────────────────────────────────
def exp4_causal(model, device, rng, n=160):
    print("[exp4] causal …", flush=True)
    biases = [-6., -3., 0., 3., 6.]
    levers = [("topdown", "quad", 0, "TD→S1"), ("topdown", "all", None, "TD uniform"),
              ("salience", "quad", 0, "SAL→S1"), ("salience", "all", None, "SAL uniform")]
    hit = np.zeros((len(levers), len(biases))); ent = np.zeros((len(levers), len(biases)))
    for li, (stream, region, quad, _) in enumerate(levers):
        for bi, bv in enumerate(biases):
            bias = dd.make_attn_bias(model, device, stream=stream, head=None, region=region, value=bv, quad=quad)
            # valid trials, change at S1, near-threshold magnitude
            envs, obs = dd.build_env_batch(_spec("left", None, 1.0, 1, "cued", MAG_THR), n, rng,
                                           env_kwargs=ENV_KW, randomize_color=True)
            for e in envs: e.change_index = 0
            cor, pp, pr, ec = greedy_rollout(model, envs, obs, device, bias=bias)
            hit[li, bi] = cor.mean(); ent[li, bi] = np.nanmean(ec)
    np.savez(f"{OUT}/exp4_causal.npz", hit=hit, ent=ent, biases=biases,
             levers=np.array([l[3] for l in levers]))
    eff = hit[:, -1] - hit[:, 0]
    print("        decision effect (b=+6 − −6): " +
          "  ".join(f"{l[3]}={eff[i]:+.2f}" for i, l in enumerate(levers)))


# ──────────────────────────────────────────────────────────────────────────────
# exp5  value / critic
# ──────────────────────────────────────────────────────────────────────────────
def exp5_value(model, device, rng, qidx, n=120):
    print("[exp5] value …", flush=True)
    vt = {}; adv = {}
    for c in dd.COLORS + ["nochange"]:
        if c == "nochange":
            envs, obs = dd.build_env_batch(_spec("left", None, 1.0, 0, "cued", None), n, rng,
                                           env_kwargs=ENV_KW, randomize_color=True)
        else:
            envs, obs = dd.build_env_batch(_spec("left", c, 1.0, 1, "cued", MAG_VIS), n, rng, env_kwargs=ENV_KW)
            for e in envs: e.change_index = 0
        r = forced_wait_record(model, envs, obs, device, qidx)
        vt[c] = r["vmean"].mean(1)                          # value over time
        # press-vs-wait advantage from the press-action quantile mean minus value
        adv[c] = r["qpress"].mean(2).mean(1) - r["vmean"].mean(1)
    # uncertainty vs magnitude (entropy just after change)
    mags = DELTAS[1:]; ent_mag = np.zeros(len(mags))
    for mi, m in enumerate(mags):
        envs, obs = dd.build_env_batch(_spec("left", None, 1.0, 1, "cued", m), n, rng,
                                       env_kwargs=ENV_KW, randomize_color=True)
        for e in envs: e.change_index = 0
        r = forced_wait_record(model, envs, obs, device, qidx)
        post = min(CHG_PHYS + 2, T_PHYS - 1)
        q = torch.tensor(r["qpress"][post])
        ent_mag[mi] = dd.quantile_entropy(q).mean().item()
    np.savez(f"{OUT}/exp5_value.npz",
             **{f"vt_{c}": vt[c] for c in vt}, **{f"adv_{c}": adv[c] for c in adv},
             mags=mags, ent_mag=ent_mag, chg_phys=CHG_PHYS, T=T_PHYS, colors=dd.COLORS)
    print(f"        value red={vt['red'][-1]:.2f} green={vt['green'][-1]:.2f} blue={vt['blue'][-1]:.2f}  "
          f"ent(Δ.1)={ent_mag[0]:.2f}->ent(Δ1.0)={ent_mag[-1]:.2f}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ckpt", default=os.path.expanduser("~/rvit_plus_checkpoints/v11_framerepeat5/v11_fr_dd_snapshot.pt"))
    ap.add_argument("--device", default="cpu")
    ap.add_argument("--only", default="all")
    args = ap.parse_args()
    torch.set_num_threads(3)
    device = torch.device(args.device)
    rng = np.random.default_rng(0)
    model, qidx = _load(args.ckpt, device)
    print(f"[load] {args.ckpt}  n_tokens={model.n_tokens}  d_mem={model.encoder.d_mem}", flush=True)
    todo = args.only.split(",") if args.only != "all" else ["1", "2", "3", "4", "5"]
    if "1" in todo: exp1_behaviour(model, device, rng)
    if "2" in todo: exp2_attention(model, device, rng, qidx)
    if "3" in todo: exp3_decoding(model, device, rng, qidx)
    if "4" in todo: exp4_causal(model, device, rng)
    if "5" in todo: exp5_value(model, device, rng, qidx)
    print("[done] npz in", OUT, flush=True)


if __name__ == "__main__":
    main()
