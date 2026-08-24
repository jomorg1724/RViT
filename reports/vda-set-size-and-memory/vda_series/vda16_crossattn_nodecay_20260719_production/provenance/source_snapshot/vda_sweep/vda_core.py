"""Analysis core for the VALUE-DIRECTED set-size sweep (vda1/2/4/9/16).
VDA1/2/4 share a 2x2 display; VDA9 and VDA16 use 3x3 and 4x4 displays.

Feedback variants: crossattn1 has N image + N memory keys (K=2N); affine_ew has N self keys (K=N).
Controlled protocol: cue always at TL(0); VDA2's sole uncued active location is BR(3).
vda1 (set_size=1) has only the target active -> no invalid condition (valid-only baseline).
CPU by default (leak-free; see reference_torch212_conv_backward_leak). No training."""
import glob
import hashlib
import numbers
import os
from pathlib import Path
import sys

import numpy as np
import torch
import torch.nn as nn

torch.set_num_threads(3)
_ROOT = os.environ.get(
    "RVIT_PROJECT_ROOT",
    str(Path(__file__).resolve().parents[1]),
)
sys.path.insert(0, _ROOT)
from model import RViTPaperModel
from envs import make_env

NP = 4; T = 7
COLORS = ["red", "green", "blue"]; COLOR_VAL = {"red": 5, "green": 3, "blue": 1}
TOK = ["S1", "TR", "BL", "S4"]; TL = 0; BR = 3
CKROOT = os.environ.get(
    "RVIT_CHECKPOINT_ROOT",
    str(Path(_ROOT).parent / "battery_sweep_results" / "pod2" / "ckpt2"),
)
DEVICE = os.environ.get("RVIT_DEVICE", "cpu")          # cpu = leak-free
FIGS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "figs")


def ckpt(task, feedback, dm=128):
    d = f"{CKROOT}/{task}_{feedback}_d{dm}"
    if task == "vda2" and os.path.isdir(d + "_2x2"):
        d = d + "_2x2"          # use the 2x2-grid vda2 (4 tokens) — matches the vda1/vda4 sweep grid
    p = os.path.join(d, "rvit_plus_rl_latest.pt")
    if os.path.exists(p):
        return p
    g = sorted(glob.glob(os.path.join(d, "*.pt")))
    return g[-1] if g else None


GRID = {"vda1": (2, 2, 50), "vda2": (2, 2, 50), "vda4": (2, 2, 50),
        "vda9": (3, 3, 75), "vda16": (4, 4, 100)}   # model grid per set-size env

# Controlled analysis protocol metadata. Reduced-set-size models share the 2x2
# display, with a fixed TL cue and (for VDA2) BR as the sole uncued location.
VDA_TASK_METADATA = {
    "vda1": {"cue_index": TL, "active_locations": (TL,)},
    "vda2": {"cue_index": TL, "active_locations": (TL, BR)},
    "vda4": {"cue_index": TL, "active_locations": tuple(range(4))},
    "vda9": {"cue_index": TL, "active_locations": tuple(range(9))},
    "vda16": {"cue_index": TL, "active_locations": tuple(range(16))},
}


def vda_task_metadata(task):
    try:
        metadata = VDA_TASK_METADATA[task]
    except KeyError as exc:
        raise ValueError(f"unknown VDA task {task!r}") from exc
    return {"cue_index": metadata["cue_index"],
            "active_locations": tuple(metadata["active_locations"])}


def sha256_file(path):
    """Return the SHA-256 digest of a checkpoint without deserializing it."""
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load(
    task,
    feedback,
    dm=128,
    checkpoint_path=None,
    *,
    expected_checkpoint_sha256=None,
    require_iteration=None,
    validate_metadata=True,
):
    """Load one analysis checkpoint and validate its declared architecture.

    Schema-3 training checkpoints are reconstructed from their embedded
    ``model_kwargs``.  Older archives remain readable through the historical
    task defaults, while callers producing manuscript evidence can additionally
    bind the exact file hash and required terminal iteration.
    """
    snap = checkpoint_path or ckpt(task, feedback, dm)
    if not snap:
        raise FileNotFoundError(f"no checkpoint for {task} {feedback} d{dm}")
    snap = Path(snap).expanduser().resolve()
    if not snap.is_file():
        raise FileNotFoundError(snap)
    checkpoint_sha256 = sha256_file(snap)
    if (
        expected_checkpoint_sha256 is not None
        and checkpoint_sha256 != str(expected_checkpoint_sha256)
    ):
        raise RuntimeError(
            f"checkpoint SHA-256 mismatch for {snap}: "
            f"{checkpoint_sha256} != {expected_checkpoint_sha256}"
        )

    ck = torch.load(snap, map_location="cpu", weights_only=False)
    if not isinstance(ck, dict) or "model_state_dict" not in ck:
        raise ValueError(f"checkpoint lacks a model_state_dict: {snap}")
    sd = ck["model_state_dict"]
    gr, gc, isz = GRID.get(task, (2, 2, 50))
    embedded = ck.get("model_kwargs")
    if isinstance(embedded, dict):
        model_kwargs = dict(embedded)
        if validate_metadata:
            declared_task = ck.get("task")
            if declared_task is not None and str(declared_task) != str(task):
                raise ValueError(
                    f"checkpoint task {declared_task!r} does not match requested {task!r}"
                )
            expected = {
                "feedback": str(feedback),
                "d_mem": int(dm),
                "grid_rows": int(gr),
                "grid_cols": int(gc),
                "image_size": int(isz),
            }
            for field, value in expected.items():
                if field not in model_kwargs:
                    raise ValueError(f"schema checkpoint is missing model_kwargs[{field!r}]")
                actual = (
                    str(model_kwargs[field])
                    if field == "feedback"
                    else int(model_kwargs[field])
                )
                if actual != value:
                    raise ValueError(
                        f"checkpoint {field}={actual!r} does not match requested {value!r}"
                    )
            schema = ck.get("checkpoint_schema_version")
            if schema is not None and int(schema) >= 3:
                producer = ck.get("producer_sha256")
                if not isinstance(producer, dict) or not producer:
                    raise ValueError("schema-3 checkpoint lacks producer SHA-256 provenance")
        m = RViTPaperModel(**model_kwargs)
    else:
        m = RViTPaperModel(
            cell="xlstm",
            feedback=feedback,
            n_quantiles=5,
            seq_len=T,
            jepa_n_heads=4,
            jepa_proto_dim=256,
            frame_repeat=1,
            d_mem=dm,
            conv_frontend=True,
            grid_rows=gr,
            grid_cols=gc,
            image_size=isz,
        )
    if "front.out_norm.bias" in sd and not isinstance(m.front.out_norm, nn.LayerNorm):
        m.front.out_norm = nn.LayerNorm(128)
    r = m.load_state_dict(sd, strict=False)
    if r.missing_keys or r.unexpected_keys:
        raise RuntimeError(
            f"checkpoint/model key mismatch: missing={r.missing_keys}, "
            f"unexpected={r.unexpected_keys}"
        )
    iteration = int(ck.get("iter", -1))
    if require_iteration is not None and iteration != int(require_iteration):
        raise ValueError(
            f"checkpoint iteration is {iteration}, expected {int(require_iteration)}"
        )
    if validate_metadata:
        if int(m.n_tokens) != int(gr * gc):
            raise ValueError(
                f"loaded model has {m.n_tokens} tokens, expected {gr * gc} for {task}"
            )
        if str(m.encoder.feedback) != str(feedback):
            raise ValueError(
                f"loaded feedback is {m.encoder.feedback!r}, expected {feedback!r}"
            )
        if int(m.encoder.d_mem) != int(dm):
            raise ValueError(
                f"loaded recurrent width is {m.encoder.d_mem}, expected {int(dm)}"
            )
    m.eval()
    m.to(DEVICE)
    m.analysis_checkpoint_path = str(snap)
    m.analysis_checkpoint_sha256 = checkpoint_sha256
    return m, iteration


def _env(task):
    return make_env(task, T=T, frame_repeat=1, min_change_time=5, max_change_time=5,
                    noise_multiplier=5.0, curriculum=False)


def _active_for(task, invalid=False):
    del invalid  # active locations are task protocol metadata, not outcome-dependent
    return list(vda_task_metadata(task)["active_locations"])


def make_video(task, cue, prop, color, ct, ci, mag=56.0, seed=None):
    """Generate one video from an isolated legacy-NumPy RNG stream.

    The environments still use ``np.random`` internally.  Temporarily installing
    a private state lets callers replay a video without consuming or replacing
    their process-global NumPy RNG state.
    """
    if seed is None:
        seed = int(np.random.default_rng().integers(0, 2**32, dtype=np.uint32))
    if isinstance(seed, (bool, np.bool_)) or not isinstance(seed, (int, np.integer)):
        raise TypeError("seed must be an integer (not bool)")
    caller_state = np.random.get_state()
    try:
        np.random.seed(int(seed))
        e = _env(task); e.reset()
        while e.change_true != ct:
            e.reset()
        if hasattr(e, "active"):
            e.active = _active_for(task, ci != cue)
        e.cue_index = int(cue); e.cue_color = color; e.proportion = float(prop)
        if ct:
            e.change_index = int(ci); e.orientation_change = float(mag)
        fr = [e._next_observation().copy()]
        for _ in range(1, T):
            o, _, _, _ = e.step(0); fr.append(o.copy())
        return np.stack(fr)
    finally:
        np.random.set_state(caller_state)


def _tens(v):
    return torch.from_numpy(np.stack(v).astype(np.float32)).permute(0, 1, 4, 2, 3).contiguous()


def make_video_batch(task, cue, prop, color, ct, ci, mag=56.0, B=300, seed=0):
    """Build a replayable tensor batch from one private RNG stream."""
    if isinstance(B, (bool, np.bool_)) or not isinstance(B, (int, np.integer)):
        raise TypeError("B must be an integer (not bool)")
    if B <= 0:
        raise ValueError("B must be positive")
    rng = np.random.default_rng(seed)
    videos = [
        make_video(
            task, cue, prop, color, ct, ci, mag,
            seed=int(rng.integers(0, 2**32, dtype=np.uint32)),
        )
        for _ in range(int(B))
    ]
    return _tens(videos).to(DEVICE)


def press_times(m, task, cue, prop, color, ct, ci, mag=56.0, B=300):
    with torch.no_grad():
        V = _tens([make_video(task, cue, prop, color, ct, ci, mag) for _ in range(B)]).to(DEVICE)
        act = m.forward_rl_sequence(V)["actor_logits_seq"].argmax(-1).cpu().numpy()
    press = np.full(B, -1)
    for t in range(T):
        h = (act[:, t] == 1) & (press < 0); press[h] = t
    return press


def behavior(m, task, cue, prop, ci, mag, color="red", ct=1, B=300):
    p = press_times(m, task, cue, prop, color, ct, ci, mag, B); det = p >= 5
    return float(det.mean()), (float(p[det].mean()) if det.any() else np.nan)


def attn_maps(m, task, cue, prop, color, ct, ci, mag=56.0, B=96):
    with torch.no_grad():
        V = _tens([make_video(task, cue, prop, color, ct, ci, mag) for _ in range(B)]).to(DEVICE)
        a = m.forward_rl_sequence(V, return_attn=True)["attn_seq"].cpu().numpy().mean(0)   # (7,4,K)
    return a


def loc_attn(a):
    """Collapse (T,N,K) attention to per-location attention alpha_i (mean over query patches).
    Uses the ACTUAL patch count N (=a.shape[1]), so it is correct for 9-patch (vda9, 3x3) as well
    as 4-patch (vda1/2/4, 2x2) models -- NOT the old hardcoded NP=4, which silently dropped 5 of
    vda9's 9 locations. crossattn1: K=2N -> image key i + memory key N+i; affine_ew: K=N -> self key i."""
    T_, N_, K = a.shape
    out = np.zeros((T_, N_))
    for i in range(N_):
        keys = [i, N_ + i] if K == 2 * N_ else [i]
        out[:, i] = a[:, :, keys].sum(-1).mean(1)
    return out                                            # (T,N), uniform baseline = 1/N


def _loc_keys(K, N, i):
    """Return attention-key indices for location ``i`` using the runtime patch count ``N``."""
    values = {"K": K, "N": N, "i": i}
    if any(
        isinstance(value, (bool, np.bool_)) or not isinstance(value, (int, np.integer))
        for value in values.values()
    ):
        raise TypeError(f"K, N, and i must be integers (not bool); got {values}")
    K, N, i = int(K), int(N), int(i)
    if N <= 0 or K not in (N, 2 * N):
        raise ValueError(f"K must equal N or 2*N with N > 0; got K={K}, N={N}")
    if not 0 <= i < N:
        raise ValueError(f"location i must satisfy 0 <= i < N; got i={i}, N={N}")
    return [i, N + i] if K == 2 * N else [i]


def clamp_on(K, N, i, b=100.0):   return {str(k): b for k in _loc_keys(K, N, i)}
def clamp_off(K, N, i, b=-100.0): return {str(k): b for k in _loc_keys(K, N, i)}


def clamp_alpha(K, N, i, alpha, scale=6.0):
    """Graded additive key-logit bias on location i: alpha in [0,1], 0.5 ~ natural."""
    for name, value in (("alpha", alpha), ("scale", scale)):
        if isinstance(value, (bool, np.bool_)) or not isinstance(value, numbers.Real):
            raise TypeError(f"{name} must be a finite real number (not bool)")
        if not np.isfinite(value):
            raise ValueError(f"{name} must be finite")
    alpha, scale = float(alpha), float(scale)
    if not 0.0 <= alpha <= 1.0:
        raise ValueError(f"alpha must satisfy 0 <= alpha <= 1; got {alpha}")
    b = scale * (2.0 * alpha - 1.0)
    return {str(k): b for k in _loc_keys(K, N, i)}


def press_times_clamp(m, task, cue, prop, color, ct, ci, mag, clamp=None,
                      clamp_from=5, B=300, videos=None, seed=0):
    V = (make_video_batch(task, cue, prop, color, ct, ci, mag, B=B, seed=seed)
         if videos is None else videos.to(DEVICE))
    B = int(V.shape[0])
    s = m.init_states(B, device=DEVICE); press = np.full(B, -1)
    for t in range(T):
        cl = clamp if (clamp and t >= clamp_from) else None
        with torch.no_grad():
            st = m.rl_step(V[:, t], s, attn_clamp=cl)
            a = st["actor_logits"].argmax(-1).cpu().numpy(); s = st["new_states"]
        h = (a == 1) & (press < 0); press[h] = t
    return press


def rollout(m, task, cue, prop, color, ct, ci, mag, clamp=None, clamp_from=5,
            B=300, videos=None, seed=0):
    """Full closed-loop rollout returning per-step actor logits, V, V_dist(quantiles), cell H.
    Used for entropy (policy + critic-quantile), SDT, and decoding."""
    V = (make_video_batch(task, cue, prop, color, ct, ci, mag, B=B, seed=seed)
         if videos is None else videos.to(DEVICE))
    B = int(V.shape[0])
    s = m.init_states(B, device=DEVICE)
    logits, Vsc, Vdist, cells = [], [], [], []
    for t in range(T):
        cl = clamp if (clamp and t >= clamp_from) else None
        with torch.no_grad():
            st = m.rl_step(V[:, t], s, attn_clamp=cl)
            s = st["new_states"]
        logits.append(st["actor_logits"].cpu().numpy())
        Vsc.append(st["V_scalar"].cpu().numpy())
        Vdist.append(st["V_dist"].cpu().numpy())
        cells.append(st["rec"].cpu().numpy() if "rec" in st else st.get("cell", None))
    return (np.stack(logits, 1), np.stack(Vsc, 1), np.stack(Vdist, 1),
            np.stack(cells, 1) if cells[0] is not None else None)


def sdt(hit, fa, n=300):
    from scipy.stats import norm
    hit = min(max(hit, 1 / (2 * n)), 1 - 1 / (2 * n)); fa = min(max(fa, 1 / (2 * n)), 1 - 1 / (2 * n))
    zh, zf = norm.ppf(hit), norm.ppf(fa)
    return -0.5 * (zh + zf), zh - zf          # (criterion c, sensitivity d')


def logistic4(d, A, B, C, D):
    return A + (1 - A - B) / (1 + np.exp(-(np.asarray(d) - D) / C))


def fit_logistic(deltas, rates):
    from scipy.optimize import curve_fit
    d = np.asarray(deltas, float); y = np.asarray(rates, float)
    p0 = [max(y.min(), 0.02), max(1 - y.max(), 0.02), 5.0,
          d[np.argmin(np.abs(y - 0.5))] if len(d) else 15.0]
    try:
        popt, _ = curve_fit(logistic4, d, y, p0=p0, maxfev=20000,
                            bounds=([0, 0, 0.5, -10], [0.5, 0.5, 40, 60]))
        return dict(guess=float(popt[0]), lapse=float(popt[1]), slope=float(1 / popt[2]),
                    position=float(popt[3]), popt=popt)
    except Exception:
        return dict(guess=np.nan, lapse=np.nan, slope=np.nan, position=np.nan, popt=p0)
