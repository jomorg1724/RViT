"""
EXP 6 — How the straw works: measuring the patch VALUE STREAM of the v8 encoder.

The v8 H1-residual makes the attention value stream over the N patch keys the
ONLY route by which current-frame visual content reaches the recurrent state
(see tx_lstm_encoder.py). Exp4 nudged the softmax WEIGHTS of that channel;
nothing has measured or intervened on its CONTENT. This experiment instruments
the per-head value sum

    a_patch = sum_{i in patch keys} alpha_i * W_v x_i        (the "straw")
    a_mem   = sum_{j in memory keys} alpha_j * W_v m_j       (the memory stream)

via dd_core's `value_edit` hook (manual_cross_attention computes the two
key-block sums separately and lets the hook record or replace them; an identity
hook is verified to reproduce the stock forward at FP precision).

NOTE on what "zeroing the straw" means: with a_patch := 0 the patch CONTENT is
removed, but the patch tokens still act as queries and still compete in the
softmax — query-side modulation of the memory stream survives. So the blind-all
condition additionally tests whether that residual query-side channel alone can
support the behaviour (the unit-tested no-bypass property zeroed the whole
out_proj, removing both).

Probes (all on the trained snapshot, exp4's near-threshold paired-trial setup —
|Δθ|=10, ring=0.75, change@t=15, cued change, cue FIXED left so the changed
quadrant is always S1, colour randomized, argmax policy, same trial seed across
all conditions so contrasts are paired). Because the ablations are drastic and
the change time is fixed, a clock-driven pressing policy would score "hits"
without seeing anything — so every behaviour condition is run a second time on
paired NO-CHANGE trials and reported as detect = hit − false-alarm rate:

  1. MAGNITUDE, NOT MASS — forced-wait recording of, per frame: per-head patch
     attention mass; per-head ||a_patch||/||a_mem|| (pre-out_proj); model-space
     (post-W_o) token-mean norms of the patch/memory contributions vs the H1
     residual; per-quadrant patch-contribution norms. Run at |Δθ|=10, 44, and
     no-change. Is the straw a high-gain, change-locked channel despite its
     ~18% attention mass?

  2. NECESSITY / TIMING — zero a_patch on selected frames: everywhere (blind),
     everywhere except small windows around the change, before vs after the
     change (the LSTM-comparator test: with no pre-change reference, can the
     tilt be detected?), cue-only / no-cue, and two FREEZE controls that replay
     the last pre-change a_patch forever: one leaving the attention weights
     live (only the CONTENT channel is cut) and one also freezing the weights
     (content AND query-side gating cut). The contrast between them — and the
     blind-all condition — dissociates the straw's two sub-channels: the value
     CONTENT it carries vs the query-driven RE-GATING of memory values.

  3. SPATIAL FOOTPRINT — recompute a_patch from only the changed quadrant's
     patch KEYS (or only the other three), and zero a_patch for QUERIES outside
     (or inside) the changed quadrant. Is the straw ~25 tokens wide?

  4. RANK — PCA the concat-head straw vector (d=128 per query) over random
     trials; during rollout re-inject only the top-k principal components
     (mean + rank-k reconstruction), sweeping k at several |Δθ|. The smallest k
     preserving the psychometric curve is the straw's effective dimensionality.

  5. ONE HEAD? — zero a_patch of each head individually, and of all heads
     EXCEPT the most image-watching one. Is the straw literally one head's
     value stream?

  + DECODING — linear-decode change presence / location / magnitude per frame
     from the straw's pooled model-space content alone (token-mean and
     quadrant-pooled), vs the same readouts of the memory stream.

Usage:
  .venv/bin/python -m RViT_plus_v8_part2.analysis.deepdive.exp6_straw --device cpu
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Dict, List, Optional, Sequence

import numpy as np
import torch
import torch.nn.functional as F

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(_HERE)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from RViT_plus_v8_part2.analysis import _behav_utils as bu  # noqa: E402
from RViT_plus_v8_part2.analysis.deepdive import dd_core as dd  # noqa: E402

FIGS = os.path.join(_HERE, "figs")
TABS = os.path.join(_HERE, "tables")
LOG = os.path.join(_HERE, "exp6.log")

_LOGF = None


def log(msg: str = "") -> None:
    print(msg)
    if _LOGF is not None:
        _LOGF.write(msg + "\n")
        _LOGF.flush()


# ──────────────────────────────────────────────────────────────────────────────
# value-stream edit hooks (all consumed via dd_core's value_edit plumbing;
# signature: edit(t, li, attn=, v=, out_patch=, out_mem=) -> (out_patch, out_mem))
# ──────────────────────────────────────────────────────────────────────────────
def make_temporal_edit(keep_frames: Optional[Sequence[int]] = None,
                       close_frames: Optional[Sequence[int]] = None):
    """Zero the straw outside `keep_frames` (or inside `close_frames`).
    keep_frames=[] → blind at every frame."""
    assert (keep_frames is None) != (close_frames is None)
    keep_s = None if keep_frames is None else {int(x) for x in keep_frames}
    close_s = None if close_frames is None else {int(x) for x in close_frames}

    def edit(t, li, attn, v, out_patch, out_mem):
        open_ = (t in keep_s) if keep_s is not None else (t not in close_s)
        if open_:
            return out_patch, out_mem
        return torch.zeros_like(out_patch), out_mem
    return edit


def make_freeze_edit(freeze_from: int):
    """Replay the straw CONTENT recorded at frame `freeze_from - 1` for every
    frame >= freeze_from: the change never enters the straw's value stream.
    NOTE: the current frame still shapes the attention WEIGHTS via the queries,
    so the memory stream remains frame-dependent (the gating channel survives).
    Stateful — build a fresh hook per rollout."""
    cache: Dict[int, torch.Tensor] = {}

    def edit(t, li, attn, v, out_patch, out_mem):
        if t == freeze_from - 1:
            cache[li] = out_patch.detach().clone()
        if t >= freeze_from:
            return cache[li].clone(), out_mem
        return out_patch, out_mem
    return edit


def make_freeze_full_edit(freeze_from: int, n_patch: int):
    """FULL visual cutoff from `freeze_from` on: replay the cached straw content
    AND recompute the memory stream with the cached attention WEIGHTS (memory
    values still evolve, but no frame >= freeze_from can influence the output
    through either the content or the gating channel). The contrast with
    make_freeze_edit isolates the query-side gating channel. Stateful."""
    cache: Dict[object, torch.Tensor] = {}

    def edit(t, li, attn, v, out_patch, out_mem):
        if t == freeze_from - 1:
            cache[("p", li)] = out_patch.detach().clone()
            cache[("a", li)] = attn.detach().clone()
        if t >= freeze_from:
            a_prev = cache[("a", li)]
            om = torch.matmul(a_prev[..., n_patch:], v[:, :, n_patch:])
            return cache[("p", li)].clone(), om
        return out_patch, out_mem
    return edit


def make_key_quad_edit(qidx: np.ndarray, keep: bool = True):
    """Recompute the straw from ONLY the given quadrant's patch keys (keep=True)
    or from all patch keys EXCEPT them (keep=False)."""
    qi = torch.as_tensor(np.asarray(qidx), dtype=torch.long)

    def edit(t, li, attn, v, out_patch, out_mem):
        sel = qi.to(attn.device)
        out_q = torch.matmul(attn[..., sel], v[:, :, sel])      # straw from quad keys
        return (out_q if keep else out_patch - out_q), out_mem
    return edit


def make_query_quad_edit(qidx: np.ndarray, n_tokens: int, keep: bool = True):
    """Zero the straw for queries OUTSIDE the quadrant (keep=True) or INSIDE it
    (keep=False) — i.e. restrict which token rows receive visual content."""
    m = torch.zeros(n_tokens)
    m[np.asarray(qidx)] = 1.0
    if not keep:
        m = 1.0 - m
    mask = m.view(1, 1, n_tokens, 1)

    def edit(t, li, attn, v, out_patch, out_mem):
        return out_patch * mask.to(out_patch.device), out_mem
    return edit


def make_head_edit(zero_heads: Sequence[int]):
    """Zero the straw of the given heads only (memory stream untouched)."""
    zh = list(int(h) for h in zero_heads)

    def edit(t, li, attn, v, out_patch, out_mem):
        op = out_patch.clone()
        op[:, zh] = 0.0
        return op, out_mem
    return edit


def make_rank_edit(mean_vec: np.ndarray, components: np.ndarray):
    """Project each query's concat-head straw vector (d = H*dh) onto the top-k
    PCA components: u -> mean + P^T P (u - mean). components: (k, d); k=0 →
    inject the mean alone."""
    mu = torch.as_tensor(mean_vec, dtype=torch.float32)
    P = torch.as_tensor(components, dtype=torch.float32) if components.size else None

    def edit(t, li, attn, v, out_patch, out_mem):
        B, H, Sq, dh = out_patch.shape
        m = mu.to(out_patch.device)
        u = out_patch.permute(0, 2, 1, 3).reshape(B, Sq, H * dh)
        if P is None:
            u2 = m.expand_as(u).contiguous()
        else:
            Pd = P.to(out_patch.device)
            c = u - m
            u2 = m + torch.matmul(torch.matmul(c, Pd.T), Pd)
        op = u2.view(B, Sq, H, dh).permute(0, 2, 1, 3).contiguous()
        return op, out_mem
    return edit


# ──────────────────────────────────────────────────────────────────────────────
# probe-1 recorder: forced-wait rollout recording straw/memory/residual content
# ──────────────────────────────────────────────────────────────────────────────
@torch.no_grad()
def _record_straw_chunk(model, envs, obs0, device, *, record_feats: bool,
                        sample_queries: int, rng: Optional[np.random.Generator]):
    """One forced-wait chunk. Records, per frame:
      head_patch_mass (B,H)  attention mass on patch keys (mean over queries)
      head_patch_norm/head_mem_norm (B,H)  pre-out_proj value-sum norms
      patch_norm/mem_norm/resid_norm (B,)  model-space token-mean norms
      patch_quad_norm (B,4)  model-space straw norm per query quadrant
      [record_feats] a_patch_mean/a_mem_mean (B,d), a_patch_quad/a_mem_quad (B,4,d)
      [sample_queries>0] u_samples: concat-head straw vectors for PCA
    Only block 0 is recorded (tx_layers == 1 for the trained v8)."""
    enc = model.encoder
    assert enc.tx_layers == 1, "probe-1 recorder assumes the single-block v8 encoder"
    B, N, H = len(envs), model.n_tokens, enc.n_heads
    d = enc.d_model
    W_o = enc.blocks[0].attn.out_proj.weight                       # (d, d)
    qidx = dd.quadrant_token_indices(model.patch_embed.grid_h, model.patch_embed.grid_w)
    qidx_t = {q: torch.as_tensor(ix, device=device) for q, ix in qidx.items()}

    holder: Dict[str, torch.Tensor] = {}

    def rec_hook(t, li, attn, v, out_patch, out_mem):
        if li == 0:
            holder["attn"] = attn
            holder["out_patch"] = out_patch
            holder["out_mem"] = out_mem
        return out_patch, out_mem

    model.eval()
    states = model.init_states(B, device=device)
    obs = list(obs0)
    T = envs[0].T
    keys = ["head_patch_mass", "head_patch_norm", "head_mem_norm",
            "patch_norm", "mem_norm", "resid_norm", "patch_quad_norm"]
    if record_feats:
        keys += ["a_patch_mean", "a_mem_mean", "a_patch_quad", "a_mem_quad"]
    rec: Dict[str, List[np.ndarray]] = {k: [] for k in keys}
    u_samples: List[np.ndarray] = []

    for t in range(T):
        x = bu._obs_to_tensor(obs, device)
        tokens = model.patch_embed(x)
        resid = states[0][0]                                        # prev-frame H1 (B,N,d)
        rec["resid_norm"].append(resid.norm(dim=-1).mean(dim=1).cpu().numpy())
        ve = lambda li, _t=t, **kw: rec_hook(_t, li, **kw)          # noqa: E731
        states, _rstates = dd.cross_attn_forward_step(enc, tokens, states, value_edit=ve)

        attn = holder["attn"]                                       # (B,H,N,3N)
        op, om = holder["out_patch"], holder["out_mem"]             # (B,H,N,dh)
        rec["head_patch_mass"].append(attn[..., :N].sum(-1).mean(2).cpu().numpy())
        rec["head_patch_norm"].append(op.norm(dim=-1).mean(2).cpu().numpy())
        rec["head_mem_norm"].append(om.norm(dim=-1).mean(2).cpu().numpy())

        # model-space contributions (post W_o, bias omitted — it is stream-neutral)
        up = op.permute(0, 2, 1, 3).reshape(B, N, d)                # concat heads
        um = om.permute(0, 2, 1, 3).reshape(B, N, d)
        ap = F.linear(up, W_o)                                      # (B,N,d)
        am = F.linear(um, W_o)
        rec["patch_norm"].append(ap.norm(dim=-1).mean(dim=1).cpu().numpy())
        rec["mem_norm"].append(am.norm(dim=-1).mean(dim=1).cpu().numpy())
        pq = torch.stack([ap[:, qidx_t[q]].norm(dim=-1).mean(dim=1) for q in range(4)], dim=1)
        rec["patch_quad_norm"].append(pq.cpu().numpy())
        if record_feats:
            rec["a_patch_mean"].append(ap.mean(dim=1).cpu().numpy())
            rec["a_mem_mean"].append(am.mean(dim=1).cpu().numpy())
            rec["a_patch_quad"].append(
                torch.stack([ap[:, qidx_t[q]].mean(dim=1) for q in range(4)], dim=1).cpu().numpy())
            rec["a_mem_quad"].append(
                torch.stack([am[:, qidx_t[q]].mean(dim=1) for q in range(4)], dim=1).cpu().numpy())
        if sample_queries > 0:
            qs = rng.choice(N, size=sample_queries, replace=False)
            u_samples.append(up[:, qs].reshape(-1, d).cpu().numpy())

        for i in range(B):
            o, _r, _d, _ = envs[i].step(0)                          # force wait
            obs[i] = o

    out: Dict[str, object] = {k: np.stack(v, axis=0) for k, v in rec.items()}  # (T, B, ...)
    if sample_queries > 0:
        out["u_samples"] = np.concatenate(u_samples, axis=0)
    out.update({
        "change_time": np.array([int(e.change_time) for e in envs], dtype=np.int64),
        "change_true": np.array([int(e.change_true) for e in envs], dtype=np.int64),
        "change_index": np.array([int(getattr(e, "change_index", -1)) for e in envs], dtype=np.int64),
        "orientation_change": np.array([float(e.orientation_change) for e in envs], dtype=np.float32),
    })
    return out


_TRIAL_KEYS = {"change_time", "change_true", "change_index", "orientation_change"}


def record_straw(model, envs, obs0, device, *, record_feats=False,
                 sample_queries=0, rng=None, chunk=256):
    """Chunked wrapper around _record_straw_chunk (the (B,H,N,3N) attention
    tensor is the memory hog — keep B per chunk modest)."""
    parts = []
    for s in range(0, len(envs), chunk):
        parts.append(_record_straw_chunk(model, envs[s:s + chunk], obs0[s:s + chunk], device,
                                         record_feats=record_feats,
                                         sample_queries=sample_queries, rng=rng))
    out: Dict[str, object] = {}
    for k in parts[0]:
        if k == "u_samples" or k in _TRIAL_KEYS:
            out[k] = np.concatenate([p[k] for p in parts], axis=0)
        else:
            out[k] = np.concatenate([p[k] for p in parts], axis=1)   # (T, B, ...)
    return out


# ──────────────────────────────────────────────────────────────────────────────
# behaviour under a value-stream edit (exp4's paired-trial harness)
# ──────────────────────────────────────────────────────────────────────────────
def behaviour_under_edit(model, device, env_kwargs, *, value_edit, mag, ring,
                         change_time, n_trials, seed, mode="cued", cue="left",
                         edit_factory=None):
    """argmax-policy rollout with a value-stream edit; exp4 metrics PLUS a paired
    no-change batch for the FALSE-ALARM rate. The drastic ablations here can
    leave a pure clock-driven pressing policy whose presses at t>=tc count as
    "hits" with a fixed change time, so detection must be read as hit − FA.

    The global numpy RNG is seeded per rollout (the env draws its base gabor
    orientations from it at reset) so the trial set is paired across conditions
    at reset level. The cue position is FIXED so quadrant-aligned edits align
    with the change on every trial; colour stays randomized.

    `edit_factory`, if given, rebuilds the hook for the second (no-change)
    rollout — required for STATEFUL hooks like the freeze edit.
    """
    def _one(chg_true: int, edit):
        np.random.seed(seed)                       # env uses the global RNG at reset
        rng = np.random.default_rng(seed)
        spec = bu.ForcedTrialSpec(cue_position=cue, proportion=ring, change_true=chg_true,
                                  change_time=change_time,
                                  change_index_mode=mode if chg_true else None,
                                  orientation_mag=float(mag))
        envs, obs0 = bu.build_env_batch(spec, n_trials, rng, env_kwargs=env_kwargs,
                                        randomize_cue_position=False, randomize_color=True)
        return dd.record_rollout(model, envs, obs0, device, policy="argmax",
                                 value_edit=edit, record_latents=False, record_quad=False)

    rec = _one(1, value_edit)
    hit = rec["hit"]
    rt = rec["rt"][~np.isnan(rec["rt"])]
    ct = min(int(change_time), rec["v_scalar"].shape[0] - 1)   # guard early-ending batches
    vadv = float((rec["q_press"][ct] - rec["q_wait"][ct]).mean())
    qent = float(rec["qent_press"][ct].mean())
    edit_fa = edit_factory() if edit_factory is not None else value_edit
    rec0 = _one(0, edit_fa)
    fa = float(rec0["pressed"].mean())
    return {
        "hit_rate": float(hit.mean()),
        "fa_rate": fa,
        "detect": float(hit.mean()) - fa,
        "median_rt": float(np.median(rt)) if rt.size else float("nan"),
        "premature_rate": float(rec["premature"].mean()),
        "press_rate": float(rec["pressed"].mean()),
        "v_press_minus_wait": vadv, "qent_press": qent,
        "n_hits": int(rt.size),
    }


def _fmt(r):
    rtv = r["median_rt"]
    return (f"hit={r['hit_rate']:.3f} FA={r['fa_rate']:.3f} det={r['detect']:+.3f} "
            f"rt={rtv if not np.isnan(rtv) else float('nan'):>4} "
            f"prem={r['premature_rate']:.3f} Vadv={r['v_press_minus_wait']:+.3f} "
            f"qent={r['qent_press']:+.3f}")


# ──────────────────────────────────────────────────────────────────────────────
# linear decoders (exp3's CV recipes)
# ──────────────────────────────────────────────────────────────────────────────
def cv_classify(X, y, n_splits=5, seed=0):
    from sklearn.linear_model import LogisticRegression
    from sklearn.model_selection import StratifiedKFold
    from sklearn.preprocessing import StandardScaler
    from sklearn.metrics import balanced_accuracy_score
    y = np.asarray(y)
    classes, counts = np.unique(y, return_counts=True)
    if len(classes) < 2 or counts.min() < n_splits:
        return float("nan")
    skf = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=seed)
    accs = []
    for tr, te in skf.split(X, y):
        sc = StandardScaler().fit(X[tr])
        clf = LogisticRegression(max_iter=2000, C=1.0)
        clf.fit(sc.transform(X[tr]), y[tr])
        accs.append(balanced_accuracy_score(y[te], clf.predict(sc.transform(X[te]))))
    return float(np.mean(accs))


def cv_regress(X, y, n_splits=5, seed=0):
    from sklearn.linear_model import Ridge
    from sklearn.model_selection import KFold
    from sklearn.preprocessing import StandardScaler
    from sklearn.metrics import r2_score
    y = np.asarray(y, float)
    if y.size < n_splits * 2 or np.ptp(y) == 0:
        return float("nan")
    kf = KFold(n_splits=n_splits, shuffle=True, random_state=seed)
    r2s = []
    for tr, te in kf.split(X):
        sc = StandardScaler().fit(X[tr])
        rg = Ridge(alpha=10.0).fit(sc.transform(X[tr]), y[tr])
        r2s.append(r2_score(y[te], rg.predict(sc.transform(X[te]))))
    return float(np.mean(r2s))


# ──────────────────────────────────────────────────────────────────────────────
def main(argv=None):
    global _LOGF
    ap = argparse.ArgumentParser()
    ap.add_argument("--checkpoint", default=dd.DEFAULT_CKPT)
    ap.add_argument("--config", default=None)
    ap.add_argument("--device", default="")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--n-trials", type=int, default=256, help="paired trials per behaviour condition")
    ap.add_argument("--n-norm", type=int, default=192, help="forced-wait trials per probe-1 condition")
    ap.add_argument("--n-collect", type=int, default=1200, help="random trials for decoding + PCA basis")
    ap.add_argument("--change-time", type=int, default=15)
    ap.add_argument("--ring", type=float, default=0.75)
    ap.add_argument("--mag", type=float, default=10.0, help="near-threshold |Δθ|")
    ap.add_argument("--rank-mags", type=float, nargs="+", default=[5.0, 10.0, 20.0, 44.0])
    ap.add_argument("--ranks", type=int, nargs="+", default=[0, 1, 2, 4, 8, 16, 32, 128])
    args = ap.parse_args(argv)

    os.makedirs(FIGS, exist_ok=True)
    os.makedirs(TABS, exist_ok=True)
    _LOGF = open(LOG, "w")

    device = dd.select_device(args.device)
    cfg = dd.load_config(args.config)
    model = dd.build_model(cfg, device)
    it = dd.load_checkpoint(model, args.checkpoint, device)
    env_kwargs = dict(min_change_time=int(cfg["environment"]["min_change_time"]),
                      max_change_time=int(cfg["environment"]["max_change_time"]))
    enc = model.encoder
    N, H = model.n_tokens, enc.n_heads
    d = enc.d_model
    tc = args.change_time
    qidx = dd.quadrant_token_indices(model.patch_embed.grid_h, model.patch_embed.grid_w)
    log(f"[loaded] {args.checkpoint} (iter={it}) device={device}  "
        f"encoder {enc.tx_layers}block×{H}H, N={N}, d={d} — instrumenting the PATCH VALUE STREAM")
    log(f"[setup] |Δθ|={args.mag} ring={args.ring} change@t={tc} n={args.n_trials} "
        f"cued change, cue FIXED left (changed quadrant = S1)")
    log("[note] zeroing the straw removes patch CONTENT only; patch tokens still query "
        "and still compete in the softmax (query-side modulation of memory survives).")

    rng = np.random.default_rng(args.seed)
    results: Dict[str, object] = {
        "checkpoint": args.checkpoint, "iter": it, "mag": args.mag, "ring": args.ring,
        "change_time": tc, "n_trials": args.n_trials,
    }

    # ══════════════════════════════════════════════════════════════════════════
    # PROBE 1 — magnitude, not mass
    # ══════════════════════════════════════════════════════════════════════════
    log("\n=== PROBE 1: straw magnitude vs memory stream vs H1 residual (forced wait) ===")
    norm_runs: Dict[str, dict] = {}
    for name, mag, chg in [("mag10", args.mag, 1), ("mag44", 44.0, 1), ("nochange", args.mag, 0)]:
        np.random.seed(args.seed + 11)             # env reset draws from the global RNG
        spec = bu.ForcedTrialSpec(cue_position="left", proportion=args.ring,
                                  change_true=chg, change_time=tc,
                                  change_index_mode="cued" if chg else None,
                                  orientation_mag=float(mag))
        envs, obs0 = bu.build_env_batch(spec, args.n_norm, np.random.default_rng(args.seed + 11),
                                        env_kwargs=env_kwargs,
                                        randomize_cue_position=False, randomize_color=True)
        norm_runs[name] = record_straw(model, envs, obs0, device)
    r10 = norm_runs["mag10"]
    T = r10["patch_norm"].shape[0]
    mass = r10["head_patch_mass"].mean(axis=1)                       # (T, H)
    mass_trial = mass.mean(axis=0)                                   # (H,) per-head patch mass
    top_head = int(np.argmax(mass_trial))
    log(f"[mass] per-head patch attention mass (trial mean): "
        + "  ".join(f"H{h}={mass_trial[h]:.3f}" for h in range(H)))
    log(f"[mass] image-watching head = H{top_head} ({mass_trial[top_head]:.3f}); "
        f"all-head mean = {mass_trial.mean():.3f}")
    for name in ("mag10", "mag44", "nochange"):
        r = norm_runs[name]
        pn, mn, rn = (r["patch_norm"].mean(1), r["mem_norm"].mean(1), r["resid_norm"].mean(1))
        pre = slice(3, tc)
        post = slice(tc, min(tc + 3, T))
        log(f"[norms {name:8s}] model-space token-mean ‖·‖ — "
            f"straw pre/post-change: {pn[pre].mean():.3f}/{pn[post].mean():.3f}  "
            f"memory: {mn[pre].mean():.3f}/{mn[post].mean():.3f}  "
            f"H1-residual: {rn[pre].mean():.3f}/{rn[post].mean():.3f}")
    pq = r10["patch_quad_norm"].mean(1)                              # (T, 4)
    post = slice(tc, min(tc + 3, T))
    log(f"[quad] straw norm by query quadrant post-change (mag10): "
        + "  ".join(f"S{q+1}={pq[post, q].mean():.3f}" for q in range(4))
        + "   (change is at S1)")
    results["probe1"] = {
        "head_patch_mass": mass_trial.tolist(), "top_head": top_head,
        "timecourses": {name: {k: norm_runs[name][k].mean(1).tolist()
                               for k in ("patch_norm", "mem_norm", "resid_norm")}
                        for name in norm_runs},
        "patch_quad_norm_mag10": pq.tolist(),
        "head_patch_norm_mag10": r10["head_patch_norm"].mean(1).tolist(),
        "head_mem_norm_mag10": r10["head_mem_norm"].mean(1).tolist(),
        "head_patch_mass_t_mag10": mass.tolist(),
    }

    # ══════════════════════════════════════════════════════════════════════════
    # COLLECT random trials (decoding features + PCA basis for probe 4)
    # ══════════════════════════════════════════════════════════════════════════
    log(f"\n[collect] {args.n_collect} fully-random forced-wait trials "
        f"(straw features + PCA basis) ...")
    np.random.seed(args.seed + 23)
    envs, obs0 = [], []
    for _ in range(args.n_collect):
        e = bu.ChangeDetectionEnv(**env_kwargs)
        o = e.reset()
        envs.append(e)
        obs0.append(o)
    coll = record_straw(model, envs, obs0, device, record_feats=True,
                        sample_queries=4, rng=rng)
    U = coll["u_samples"]                                            # (M, d) concat-head straw
    log(f"[collect] done: T={coll['a_patch_mean'].shape[0]}, B={args.n_collect}, "
        f"change-trials={int(coll['change_true'].sum())}, PCA rows={U.shape[0]}")

    mu = U.mean(axis=0)
    C = np.cov((U - mu).T)
    evals, evecs = np.linalg.eigh(C)
    order = np.argsort(evals)[::-1]
    evals, evecs = evals[order], evecs[:, order]                     # evecs[:, i] = i-th PC
    var_frac = np.cumsum(evals) / evals.sum()
    k90 = int(np.searchsorted(var_frac, 0.90) + 1)
    k99 = int(np.searchsorted(var_frac, 0.99) + 1)
    log(f"[pca] straw variance: top-1={evals[0]/evals.sum():.3f}  "
        f"90% at k={k90}  99% at k={k99} (of d={d})")
    results["pca"] = {"explained_frac": (evals / evals.sum()).tolist(), "k90": k90, "k99": k99}

    # ══════════════════════════════════════════════════════════════════════════
    # baseline behaviour (paired seed shared by every condition below)
    # ══════════════════════════════════════════════════════════════════════════
    seed0 = args.seed + 1
    base = behaviour_under_edit(model, device, env_kwargs, value_edit=None, mag=args.mag,
                                ring=args.ring, change_time=tc, n_trials=args.n_trials, seed=seed0)
    log(f"\n[baseline] {_fmt(base)}")
    results["baseline"] = base

    def run(name, edit_factory, desc):
        """One paired-trial condition; edit_factory() builds a FRESH hook per
        rollout (stateful hooks must not leak across rollouts)."""
        r = behaviour_under_edit(model, device, env_kwargs, value_edit=edit_factory(),
                                 edit_factory=edit_factory,
                                 mag=args.mag, ring=args.ring, change_time=tc,
                                 n_trials=args.n_trials, seed=seed0)
        log(f"[{name:24s}] {_fmt(r)}   ({desc})")
        return r

    # ══════════════════════════════════════════════════════════════════════════
    # PROBE 2 — necessity / timing
    # ══════════════════════════════════════════════════════════════════════════
    log("\n=== PROBE 2: when must the straw be open? (zero a_patch outside the window) ===")
    temporal_specs = [
        ("blind_all",        lambda: make_temporal_edit(keep_frames=[]),
         "straw closed at every frame"),
        ("open_change_only", lambda: make_temporal_edit(keep_frames=[tc]),
         f"open ONLY at the change frame t={tc}"),
        ("open_change_pm1",  lambda: make_temporal_edit(keep_frames=range(tc - 1, tc + 2)),
         "open t=change±1"),
        ("open_change_pm2",  lambda: make_temporal_edit(keep_frames=range(tc - 2, tc + 3)),
         "open t=change±2"),
        ("open_cue_change",  lambda: make_temporal_edit(keep_frames=[1, tc]),
         "open at cue frame + change frame"),
        ("open_from_change", lambda: make_temporal_edit(keep_frames=range(tc, 99)),
         "blind BEFORE the change (no pre-change reference → comparator test)"),
        ("open_until_change", lambda: make_temporal_edit(keep_frames=range(0, tc)),
         "blind FROM the change on (change never seen → false-press control)"),
        ("closed_cue_only",  lambda: make_temporal_edit(close_frames=[1]),
         "closed only at the cue frame (cue-through-the-straw test)"),
        ("freeze_at_change", lambda: make_freeze_edit(tc),
         "replay pre-change straw CONTENT forever (query-side gating stays live)"),
        ("freeze_full",      lambda: make_freeze_full_edit(tc, N),
         "freeze content AND attention weights at the change (both channels cut)"),
    ]
    results["temporal"] = {}
    for name, fac, desc in temporal_specs:
        results["temporal"][name] = run(name, fac, desc)

    # ══════════════════════════════════════════════════════════════════════════
    # PROBE 3 — spatial footprint
    # ══════════════════════════════════════════════════════════════════════════
    log("\n=== PROBE 3: spatial footprint (changed quadrant = S1; straw open at all t) ===")
    spatial_specs = [
        ("keys_S1_only",    lambda: make_key_quad_edit(qidx[0], keep=True),
         "straw rebuilt from S1 patch KEYS only (25/100 keys)"),
        ("keys_not_S1",     lambda: make_key_quad_edit(qidx[0], keep=False),
         "straw without the S1 patch keys"),
        ("queries_S1_only", lambda: make_query_quad_edit(qidx[0], N, keep=True),
         "only S1 QUERY rows receive visual content"),
        ("queries_not_S1",  lambda: make_query_quad_edit(qidx[0], N, keep=False),
         "every query row EXCEPT S1 receives visual content"),
    ]
    results["spatial"] = {}
    for name, fac, desc in spatial_specs:
        results["spatial"][name] = run(name, fac, desc)

    # ══════════════════════════════════════════════════════════════════════════
    # PROBE 5 — is the straw one head?
    # ══════════════════════════════════════════════════════════════════════════
    log(f"\n=== PROBE 5: per-head straw knockouts (image-watcher = H{top_head}) ===")
    results["heads"] = {}
    for h in range(H):
        results["heads"][f"zero_H{h}"] = run(
            f"zero_H{h}", lambda h=h: make_head_edit([h]),
            f"straw of head {h} zeroed (mass {mass_trial[h]:.3f})")
    others = [h for h in range(H) if h != top_head]
    results["heads"][f"only_H{top_head}"] = run(
        f"only_H{top_head}", lambda: make_head_edit(others),
        f"ONLY head {top_head}'s straw survives")

    # ══════════════════════════════════════════════════════════════════════════
    # PROBE 4 — rank of the straw
    # ══════════════════════════════════════════════════════════════════════════
    log("\n=== PROBE 4: rank-k straw (PCA re-injection), psychometric sweep ===")
    results["rank"] = {"ranks": list(args.ranks), "mags": list(args.rank_mags), "sweep": {}}
    log("  detect = hit − FA;  columns are straw rank k ('mean' = rank 0)")
    log("  |Δθ| \\ k " + "".join(f"{('full' if k >= d else ('mean' if k == 0 else k)):>7}"
                                 for k in args.ranks) + "   baseline")
    for mag in args.rank_mags:
        b = behaviour_under_edit(model, device, env_kwargs, value_edit=None, mag=mag,
                                 ring=args.ring, change_time=tc,
                                 n_trials=args.n_trials, seed=seed0)
        rows = []
        for k in args.ranks:
            comps = evecs[:, :k].T.copy() if k > 0 else np.zeros((0, d))
            edit = make_rank_edit(mu, comps)
            r = behaviour_under_edit(model, device, env_kwargs, value_edit=edit, mag=mag,
                                     ring=args.ring, change_time=tc,
                                     n_trials=args.n_trials, seed=seed0)
            rows.append(r)
        results["rank"]["sweep"][f"{mag:g}"] = {
            "hit_by_k": [r["hit_rate"] for r in rows],
            "fa_by_k": [r["fa_rate"] for r in rows],
            "detect_by_k": [r["detect"] for r in rows],
            "baseline": b,
        }
        log(f"  {mag:7g} " + "".join(f"{r['detect']:7.3f}" for r in rows)
            + f"   {b['detect']:8.3f}")

    # ══════════════════════════════════════════════════════════════════════════
    # DECODING — what the straw carries, frame by frame
    # ══════════════════════════════════════════════════════════════════════════
    log("\n=== DECODING: change variables from the straw's pooled content (per frame) ===")
    chg = coll["change_true"].astype(bool)
    chg_idx = coll["change_index"]
    chg_time = coll["change_time"]
    mag_lbl = np.abs(coll["orientation_change"])
    Tc = coll["a_patch_mean"].shape[0]
    sources = ["a_patch_mean", "a_patch_quad", "a_mem_mean", "a_mem_quad"]
    dec_curves: Dict[str, Dict[str, List[float]]] = {}
    for target in ("change_present", "change_location", "change_magnitude"):
        dec_curves[target] = {}
        for src in sources:
            cs = []
            for t in range(Tc):
                Xt = coll[src][t][chg].reshape(int(chg.sum()), -1)
                if target == "change_present":
                    yy = (t >= chg_time[chg]).astype(int)
                    cs.append(cv_classify(Xt, yy, seed=args.seed)
                              if len(np.unique(yy)) > 1 else float("nan"))
                elif target == "change_location":
                    cs.append(cv_classify(Xt, chg_idx[chg], seed=args.seed))
                else:
                    cs.append(cv_regress(Xt, mag_lbl[chg], seed=args.seed))
            dec_curves[target][src] = cs
        peaks = {s: float(np.nanmax(dec_curves[target][s])) for s in sources}
        log(f"  {target:17s} peaks: " + "  ".join(f"{s}={peaks[s]:.3f}" for s in sources))
    results["decoding"] = dec_curves

    # ══════════════════════════════════════════════════════════════════════════
    # tables
    # ══════════════════════════════════════════════════════════════════════════
    with open(f"{TABS}/exp6_straw.json", "w") as f:
        json.dump(results, f, indent=2)
    lines = ["condition\thit\tFA\tdetect\tΔdetect\tpremature\tpress\tmedian_rt\tVadv"]
    for group in ("temporal", "spatial", "heads"):
        for name, r in results[group].items():
            lines.append(f"{name}\t{r['hit_rate']:.3f}\t{r['fa_rate']:.3f}\t"
                         f"{r['detect']:+.3f}\t{r['detect']-base['detect']:+.3f}\t"
                         f"{r['premature_rate']:.3f}\t{r['press_rate']:.3f}\t"
                         f"{r['median_rt']:.1f}\t{r['v_press_minus_wait']:+.3f}")
    with open(f"{TABS}/exp6_summary.tsv", "w") as f:
        f.write("\n".join(lines) + "\n")

    # ══════════════════════════════════════════════════════════════════════════
    # figures
    # ══════════════════════════════════════════════════════════════════════════
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams.update({"font.size": 9})
    cmap = plt.get_cmap("tab10")

    # Fig 1 — probe 1: norms & mass
    fig, axes = plt.subplots(1, 3, figsize=(15, 4.4))
    ax = axes[0]
    for h in range(H):
        ax.plot(range(T), mass[:, h], color=cmap(h), lw=1.3,
                label=f"H{h}" + (" (watcher)" if h == top_head else ""))
    ax.set_title("patch attention mass per head")
    ax.set_ylabel("mass on patch keys")
    ax.legend(fontsize=6, ncol=2)
    ax = axes[1]
    for name, ls in [("mag10", "-"), ("mag44", "--"), ("nochange", ":")]:
        r = norm_runs[name]
        ax.plot(range(T), r["patch_norm"].mean(1), "tab:blue", ls=ls, lw=1.5,
                label=f"straw {name}")
    r = norm_runs["mag10"]
    ax.plot(range(T), r["mem_norm"].mean(1), "tab:red", lw=1.5, label="memory stream")
    ax.plot(range(T), r["resid_norm"].mean(1), "tab:green", lw=1.5, label="H1 residual")
    ax.set_title("model-space contribution norms")
    ax.set_ylabel("token-mean ‖·‖")
    ax.legend(fontsize=7)
    ax = axes[2]
    for q in range(4):
        ax.plot(range(T), pq[:, q], color=cmap(q), lw=1.5,
                label=f"S{q+1}" + (" (changed)" if q == 0 else ""))
    ax.set_title("straw norm by query quadrant (|Δθ|=10)")
    ax.set_ylabel("token-mean ‖a_patch‖")
    ax.legend(fontsize=7)
    for ax in axes:
        ax.axvline(1, color="k", ls=":", alpha=.4)
        ax.axvline(3, color="grey", ls=":", alpha=.3)
        ax.axvline(tc, color="purple", ls=":", alpha=.6)
        ax.set_xlabel("frame t (cue@1, gabors@3, change@15)")
        ax.grid(alpha=.3)
    fig.suptitle("PROBE 1 — the straw's magnitude and timing (forced wait)")
    fig.tight_layout()
    fig.savefig(f"{FIGS}/exp6_straw_norms.png", dpi=130, bbox_inches="tight")
    plt.close(fig)

    # Fig 2 — probes 2+3: ablation bars
    fig, axes = plt.subplots(1, 2, figsize=(14, 4.6), width_ratios=[2.2, 1])
    for ax, group, ttl in zip(axes, ("temporal", "spatial"),
                              ("PROBE 2 — when the straw must be open",
                               "PROBE 3 — spatial footprint")):
        names = list(results[group].keys())
        hits = [results[group][n]["hit_rate"] for n in names]
        fas = [results[group][n]["fa_rate"] for n in names]
        dets = [results[group][n]["detect"] for n in names]
        xs = np.arange(len(names))
        ax.bar(xs - 0.22, hits, width=0.22, color="tab:blue", label="P(hit)")
        ax.bar(xs, fas, width=0.22, color="tab:orange", label="P(FA) no-change")
        ax.bar(xs + 0.22, dets, width=0.22, color="tab:green", label="detect (hit−FA)")
        ax.axhline(base["detect"], color="k", ls="--", alpha=.5, label="baseline detect")
        ax.set_xticks(xs)
        ax.set_xticklabels(names, rotation=35, ha="right", fontsize=7)
        ax.set_ylabel("rate")
        ax.set_title(ttl)
        ax.grid(alpha=.3, axis="y")
        ax.legend(fontsize=7)
    fig.tight_layout()
    fig.savefig(f"{FIGS}/exp6_ablation_behaviour.png", dpi=130, bbox_inches="tight")
    plt.close(fig)

    # Fig 3 — probe 5: head knockouts
    fig, ax = plt.subplots(figsize=(8, 4.4))
    names = list(results["heads"].keys())
    hits = [results["heads"][n]["detect"] for n in names]
    colors = ["tab:red" if (f"H{top_head}" in n) else "tab:blue" for n in names]
    ax.bar(range(len(names)), hits, color=colors)
    ax.axhline(base["detect"], color="k", ls="--", alpha=.5, label="baseline detect")
    ax2 = ax.twinx()
    ax2.plot(range(H), mass_trial, "o-", color="tab:green", label="patch mass")
    ax2.set_ylabel("per-head patch attention mass", color="tab:green")
    ax.set_xticks(range(len(names)))
    ax.set_xticklabels(names, rotation=35, ha="right", fontsize=7)
    ax.set_ylabel("detect (hit − FA)")
    ax.set_title(f"PROBE 5 — per-head straw knockouts (image-watcher = H{top_head})")
    ax.grid(alpha=.3, axis="y")
    ax.legend(fontsize=8, loc="lower left")
    fig.tight_layout()
    fig.savefig(f"{FIGS}/exp6_head_knockout.png", dpi=130, bbox_inches="tight")
    plt.close(fig)

    # Fig 4 — probe 4: rank sweep
    fig, ax = plt.subplots(figsize=(7.5, 4.6))
    ks = [k if k > 0 else 0.5 for k in args.ranks]                  # 0 plotted at 0.5 on log axis
    for i, mag in enumerate(args.rank_mags):
        rr = results["rank"]["sweep"][f"{mag:g}"]
        ax.plot(ks, rr["detect_by_k"], "o-", color=cmap(i), lw=1.6, label=f"|Δθ|={mag:g}")
        ax.axhline(rr["baseline"]["detect"], color=cmap(i), ls=":", alpha=.5)
    ax.set_xscale("log", base=2)
    ax.set_xticks(ks)
    ax.set_xticklabels(["mean" if k == 0 else str(k) for k in args.ranks])
    ax.set_xlabel("k (straw rank: top-k PCA re-injection)")
    ax.set_ylabel("detect (hit − FA)")
    ax.set_title("PROBE 4 — the straw's effective dimensionality (dotted = unrestricted)")
    ax.grid(alpha=.3)
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(f"{FIGS}/exp6_rank_sweep.png", dpi=130, bbox_inches="tight")
    plt.close(fig)

    # Fig 5 — decoding curves
    srccol = {"a_patch_mean": "tab:blue", "a_patch_quad": "tab:cyan",
              "a_mem_mean": "tab:red", "a_mem_quad": "tab:orange"}
    fig, axes = plt.subplots(1, 3, figsize=(15, 4.4))
    for ax, target in zip(axes, ("change_present", "change_location", "change_magnitude")):
        for src in sources:
            ax.plot(range(Tc), dec_curves[target][src], color=srccol[src], lw=1.6, label=src)
        if target == "change_present":
            ax.axhline(0.5, color="grey", ls=":")
        elif target == "change_location":
            ax.axhline(0.25, color="grey", ls=":")
        else:
            ax.axhline(0.0, color="grey", ls=":")
        ax.axvline(1, color="k", ls=":", alpha=.4)
        ax.axvline(3, color="grey", ls=":", alpha=.3)
        ax.set_title(target)
        ax.set_xlabel("frame t")
        ax.set_ylabel("balanced acc" if target != "change_magnitude" else "R²")
        ax.grid(alpha=.3)
    axes[0].legend(fontsize=7)
    fig.suptitle("What the straw carries — per-frame linear decoding from pooled stream content")
    fig.tight_layout()
    fig.savefig(f"{FIGS}/exp6_straw_decoding.png", dpi=130, bbox_inches="tight")
    plt.close(fig)

    log(f"\n[saved] {TABS}/exp6_straw.json")
    log(f"[saved] {TABS}/exp6_summary.tsv")
    log(f"[saved] {FIGS}/exp6_straw_norms.png, exp6_ablation_behaviour.png, "
        f"exp6_head_knockout.png, exp6_rank_sweep.png, exp6_straw_decoding.png")
    log("[done]")
    if _LOGF is not None:
        _LOGF.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
