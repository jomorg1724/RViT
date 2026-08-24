"""
Deep-dive core harness for the trained RViT+ v5 model.

Extends ``analysis/_behav_utils.py`` with the machinery the deep-dive needs but
the first-look SOP did not:

  * a manual, mathematically faithful replica of every transformer's
    multi-head self-attention that (a) returns per-head weights and (b) can have
    an ADDITIVE per-(layer, head, key) bias injected into the pre-softmax
    attention logits — this is the substrate for both the attention maps and the
    causal attention-manipulation experiment;
  * ``memtok_forward_step`` — a bias-injectable, attention-returning version of
    ``MemTokEncoder.forward_step`` that reuses the trained submodules unchanged
    (in eval() the dropouts are identity, so the output matches the stock
    forward exactly when bias=0; verified in ``_selfcheck``);
  * ``record_rollout`` — a batched rollout under either the argmax policy or a
    forced action that records, per timestep, the recurrent latents (token-mean
    and per-quadrant pooled H1/H2), the actor/critic CLS readouts, the actor
    logits/policy entropy, and the critic's full distributional value (V_dist,
    Q for each action) so value / entropy / decoding analyses share ONE pass;
  * quadrant bookkeeping and critic-distribution summary statistics.

The env (ChangeDetectionEnv) quadrant indexing is the project standard:
    0 = S1 top-left (gabor1, cue 'left')   2 = S3 top-right  (gabor3)
    1 = S2 bottom-left (gabor2)            3 = S4 bottom-right (gabor4, cue 'right')
Patch tokens are row-major on a 10x10 grid (token i*gw+j = grid cell (i,j)),
so each 25x25 Gabor quadrant is a 5x5 block of patch tokens.
"""
from __future__ import annotations

import os
import sys
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np
import torch
import torch.nn.functional as F

_HERE = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(_HERE)))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from RViT_plus_v5.analysis import _behav_utils as bu  # noqa: E402

# re-export the pieces every deep-dive script reuses
ForcedTrialSpec = bu.ForcedTrialSpec
reset_with_spec = bu.reset_with_spec
build_env_batch = bu.build_env_batch
build_model = bu.build_model
load_checkpoint = bu.load_checkpoint
load_config = bu.load_config
select_device = bu.select_device
_obs_to_tensor = bu._obs_to_tensor
CUED_QUADRANT = bu.CUED_QUADRANT
COLOR_VALUE = bu.COLOR_VALUE

QUAD_NAMES = {0: "S1 top-left", 1: "S2 bottom-left", 2: "S3 top-right", 3: "S4 bottom-right"}
COLORS = ["red", "green", "blue"]
PROPORTIONS = [1.0, 0.75, 0.5, 0.25]

DEFAULT_CKPT = "/Users/jonathanmorgan/rvit_plus_checkpoints/v5/rvit_plus_v5_rl_final.pt"


# ──────────────────────────────────────────────────────────────────────────────
# quadrant <-> token bookkeeping
# ──────────────────────────────────────────────────────────────────────────────
def quadrant_token_indices(gh: int = 10, gw: int = 10) -> Dict[int, np.ndarray]:
    """Token indices (row-major i*gw+j) belonging to each env quadrant."""
    idx = np.arange(gh * gw).reshape(gh, gw)
    hh, ww = gh // 2, gw // 2
    return {
        0: idx[:hh, :ww].ravel().copy(),   # top-left  (S1)
        1: idx[hh:, :ww].ravel().copy(),   # bottom-left (S2)
        2: idx[:hh, ww:].ravel().copy(),   # top-right (S3)
        3: idx[hh:, ww:].ravel().copy(),   # bottom-right (S4)
    }


def grid_to_image(grid: np.ndarray, patch: int = 5) -> np.ndarray:
    """Upsample a (gh, gw) patch-grid map to a (gh*patch, gw*patch) image by
    nearest-neighbour block expansion — the alpha 'project back onto a box of the
    input-image shape' visualization."""
    return np.kron(grid, np.ones((patch, patch), dtype=grid.dtype))


# ──────────────────────────────────────────────────────────────────────────────
# manual multi-head self-attention (faithful to nn.MultiheadAttention)
# ──────────────────────────────────────────────────────────────────────────────
def manual_self_attention(
    mha: torch.nn.MultiheadAttention,
    x: torch.Tensor,
    score_bias: Optional[torch.Tensor] = None,
) -> Tuple[torch.Tensor, torch.Tensor]:
    """Replicate ``mha(x, x, x, need_weights=True, average_attn_weights=False)``
    with full control of the pre-softmax scores.

    x          : (B, S, d_model), batch_first.
    score_bias : optional (n_heads, S) or (n_heads, S_q, S_k) additive bias added
                 to the attention logits BEFORE softmax. (n_heads, S) is
                 broadcast over the query axis (a per-key, per-head bias — the
                 form used by the causal experiment). None → identity.

    Returns (attn_out (B,S,d_model), attn_w (B, n_heads, S, S)). With
    score_bias=None this matches the stock module to <1e-5 (verified).
    """
    B, S, d = x.shape
    H = mha.num_heads
    dh = d // H
    # in-projection (packed q,k,v)
    qkv = F.linear(x, mha.in_proj_weight, mha.in_proj_bias)           # (B,S,3d)
    q, k, v = qkv.chunk(3, dim=-1)
    q = q.view(B, S, H, dh).transpose(1, 2)                           # (B,H,S,dh)
    k = k.view(B, S, H, dh).transpose(1, 2)
    v = v.view(B, S, H, dh).transpose(1, 2)
    scores = torch.matmul(q, k.transpose(-2, -1)) / (dh ** 0.5)       # (B,H,S,S)
    if score_bias is not None:
        if score_bias.dim() == 2:                                    # (H,S_k) per-key
            scores = scores + score_bias[None, :, None, :]
        elif score_bias.dim() == 3:                                  # (H,S_q,S_k)
            scores = scores + score_bias[None]
        else:
            raise ValueError(f"score_bias must be 2D or 3D; got {tuple(score_bias.shape)}")
    attn = torch.softmax(scores, dim=-1)                             # (B,H,S,S)
    out = torch.matmul(attn, v)                                       # (B,H,S,dh)
    out = out.transpose(1, 2).contiguous().view(B, S, d)
    out = F.linear(out, mha.out_proj.weight, mha.out_proj.bias)
    return out, attn


def _prenorm_layer(layer: torch.nn.TransformerEncoderLayer, seq: torch.Tensor,
                   score_bias: Optional[torch.Tensor] = None):
    """norm_first=True encoder-layer forward with optional attention bias; returns
    (out, attn_w). Matches MemTokEncoder._layer_with_attn at bias=0."""
    normed = layer.norm1(seq)
    attn_out, attn_w = manual_self_attention(layer.self_attn, normed, score_bias)
    x = seq + layer.dropout1(attn_out)
    ff = layer.linear2(layer.dropout(layer.activation(layer.linear1(layer.norm2(x)))))
    x = x + layer.dropout2(ff)
    return x, attn_w


def _postnorm_layer(layer: torch.nn.TransformerEncoderLayer, x: torch.Tensor,
                    score_bias: Optional[torch.Tensor] = None):
    """post-norm (decoder) encoder-layer forward with optional attention bias."""
    attn_out, attn_w = manual_self_attention(layer.self_attn, x, score_bias)
    x = layer.norm1(x + layer.dropout1(attn_out))
    ff = layer.linear2(layer.dropout(layer.activation(layer.linear1(x))))
    x = layer.norm2(x + layer.dropout2(ff))
    return x, attn_w


# ──────────────────────────────────────────────────────────────────────────────
# bias-injectable, attention-returning encoder step
# ──────────────────────────────────────────────────────────────────────────────
def memtok_forward_step(
    encoder,
    tokens: torch.Tensor,
    prev_state,
    attn_bias: Optional[torch.Tensor] = None,
    return_attn: bool = False,
):
    """Bias-injectable replica of MemTokEncoder.forward_step.

    attn_bias : optional (n_layers, n_heads, 3N) additive per-key bias added to
                the pre-softmax attention logits of that layer (broadcast over
                queries). Keys are ordered [patch(N) ++ H1(N) ++ H2(N)].
    Returns (new_state, rec_states[, attn_per_layer]) exactly like the original.
    """
    Hs, Cs = list(prev_state[0]), list(prev_state[1])
    B, N = tokens.shape[0], encoder.n_tokens
    sf = encoder.src_emb.weight[0]
    mtag = [encoder.src_emb.weight[k + 1] for k in range(encoder.n_layers)]
    mpe = encoder.mem_pos_emb
    attn_per_layer: List[Optional[torch.Tensor]] = [None] * encoder.n_layers
    for _ in range(encoder.n_FR):
        X = tokens
        for li in range(encoder.n_layers):
            mem_toks = [Hs[k] + mpe + mtag[k] for k in range(encoder.n_layers)]
            seq = torch.cat([X + sf] + mem_toks, dim=1)              # (B,3N,d)
            sb = None if attn_bias is None else attn_bias[li]       # (H,3N)
            out, aw = _prenorm_layer(encoder.enc[li], seq, sb)
            attn_per_layer[li] = aw
            Z = out[:, :N]
            h, c = encoder.cells[li](
                Z.reshape(B * N, encoder.d_model),
                (Hs[li].reshape(B * N, encoder.d_mem), Cs[li].reshape(B * N, encoder.d_mem)),
            )
            Hs[li] = h.view(B, N, encoder.d_mem)
            Cs[li] = c.view(B, N, encoder.d_mem)
            X = Z
    rec = [Hs[li] for li in range(encoder.n_layers)]
    if return_attn:
        return (Hs, Cs), rec, attn_per_layer
    return (Hs, Cs), rec


# ──────────────────────────────────────────────────────────────────────────────
# decoder CLS readout + attention (faithful to decoder.py)
# ──────────────────────────────────────────────────────────────────────────────
def actor_decode(actor, rec_states, return_attn: bool = False):
    """Reproduce ActorDecoder: returns (logits, cls_vec[, attn_per_layer])."""
    M = torch.cat(rec_states, dim=1) + actor.pos_emb
    B = M.shape[0]
    seq = torch.cat([actor.cls.expand(B, -1, -1), M], dim=1)
    attns = []
    x = seq
    for layer in actor.tx.layers:
        x, aw = _postnorm_layer(layer, x)
        attns.append(aw)
    cls = actor.dp(actor.norm(x[:, 0]))
    logits = actor.head(cls)
    if return_attn:
        return logits, cls, attns
    return logits, cls


def critic_decode(critic, rec_states, action: int, return_attn: bool = False):
    """Reproduce CriticDecoder for ONE action: returns (q_quantiles (B,Nq),
    cls_vec[, attn_per_layer])."""
    M = torch.cat(rec_states, dim=1) + critic.pos_emb
    a_enc = critic.action_emb.repeat(1, critic.n_states, 1)
    Ma = M + a_enc[action].unsqueeze(0)
    B = M.shape[0]
    seq = torch.cat([critic.cls.expand(B, -1, -1), Ma], dim=1)
    attns = []
    x = seq
    for layer in critic.tx.layers:
        x, aw = _postnorm_layer(layer, x)
        attns.append(aw)
    cls = critic.dp(critic.norm(x[:, 0]))
    q = critic.head(cls)
    if return_attn:
        return q, cls, attns
    return q, cls


# ──────────────────────────────────────────────────────────────────────────────
# critic distribution summaries
# ──────────────────────────────────────────────────────────────────────────────
def quantile_entropy(q: torch.Tensor) -> torch.Tensor:
    """Differential-entropy-like spread of a QR distribution given its sorted-ish
    quantile support values q (..., Nq). Treats consecutive quantiles as equal-
    probability (1/Nq) bins of width dz; H = sum (1/Nq) log(Nq*dz_clamped).
    Higher = more spread-out value distribution = more outcome uncertainty."""
    qs, _ = torch.sort(q, dim=-1)
    Nq = qs.shape[-1]
    dz = (qs[..., 1:] - qs[..., :-1]).clamp_min(1e-6)
    return ((1.0 / Nq) * torch.log(Nq * dz)).sum(dim=-1)


def quantile_std(q: torch.Tensor) -> torch.Tensor:
    return q.std(dim=-1)


def policy_entropy(logits: torch.Tensor) -> torch.Tensor:
    """Shannon entropy (nats) of softmax(logits) over the action axis."""
    logp = F.log_softmax(logits, dim=-1)
    p = logp.exp()
    return -(p * logp).sum(dim=-1)


# ──────────────────────────────────────────────────────────────────────────────
# recording rollout
# ──────────────────────────────────────────────────────────────────────────────
@torch.no_grad()
def record_rollout(
    model,
    envs,
    obs0,
    device,
    *,
    policy: str = "wait",            # 'wait' | 'argmax'
    attn_bias: Optional[torch.Tensor] = None,
    record_latents: bool = True,
    record_quad: bool = True,
    run_full: bool = False,          # always run all T frames (needed for chunked concat)
) -> Dict[str, object]:
    """Run B trials in parallel, recording behaviour + per-step latents/value.

    policy='wait'  → force action 0 every step (every trial runs full T; for
                     attention/latent/value time-courses).
    policy='argmax'→ act greedily (for behaviour under intervention).

    Records per timestep t (list over t, each (B, ...)):
      v_scalar, q_wait, q_press (mean over quantiles), v_dist (B,Nq),
      qent_press, qstd_press, pol_entropy, press_prob, actor_logits,
      (if record_latents) h1_mean,h2_mean (B,d); (if record_quad)
      h1_quad,h2_quad (B,4,d); actor_cls,critic_press_cls (B,d).
    Plus per-trial behaviour: press_index, hit, premature, rt, reward, and the
    env label arrays.
    """
    B = len(envs)
    model.eval()
    states = model.init_states(B, device=device)
    obs = list(obs0)
    T = envs[0].T
    rec: Dict[str, List] = {k: [] for k in [
        "v_scalar", "q_wait", "q_press", "v_dist", "qent_press", "qstd_press",
        "pol_entropy", "press_prob", "actor_logits", "frame_mean"]}
    if record_latents:
        rec.update({"h1_mean": [], "h2_mean": [], "actor_cls": [], "critic_press_cls": []})
    if record_quad:
        rec.update({"h1_quad": [], "h2_quad": []})
    qidx = quadrant_token_indices(model.patch_embed.grid_h, model.patch_embed.grid_w)
    qidx_t = {q: torch.as_tensor(ix, device=device) for q, ix in qidx.items()}

    press_index = np.full(B, -1, dtype=np.int64)
    reward = np.zeros(B, dtype=np.float32)
    done = np.zeros(B, dtype=bool)
    change_time = np.array([int(e.change_time) for e in envs], dtype=np.int64)
    change_true = np.array([int(e.change_true) for e in envs], dtype=np.int64)
    t = 0
    while t < T and (run_full or not done.all()):
        x = _obs_to_tensor(obs, device)
        tokens = model.patch_embed(x)
        states, rstates = memtok_forward_step(model.encoder, tokens, states, attn_bias=attn_bias)
        logits, a_cls = actor_decode(model.actor_head, rstates)
        q_press, c_cls = critic_decode(model.critic_head, rstates, 1)
        q_wait, _ = critic_decode(model.critic_head, rstates, 0)
        q_dist = torch.stack([q_wait, q_press], dim=1)               # (B,2,Nq)
        pi = torch.softmax(logits, dim=-1)
        v_dist = (pi.detach().unsqueeze(-1) * q_dist).sum(dim=1)     # (B,Nq)
        rec["v_scalar"].append(v_dist.mean(-1).cpu().numpy())
        rec["q_wait"].append(q_wait.mean(-1).cpu().numpy())
        rec["q_press"].append(q_press.mean(-1).cpu().numpy())
        rec["v_dist"].append(v_dist.cpu().numpy())
        rec["qent_press"].append(quantile_entropy(q_press).cpu().numpy())
        rec["qstd_press"].append(quantile_std(q_press).cpu().numpy())
        rec["pol_entropy"].append(policy_entropy(logits).cpu().numpy())
        rec["press_prob"].append(pi[:, 1].cpu().numpy())
        rec["actor_logits"].append(logits.cpu().numpy())
        rec["frame_mean"].append(x.abs().mean(dim=(1, 2, 3)).cpu().numpy())
        if record_latents:
            rec["h1_mean"].append(rstates[0].mean(1).cpu().numpy())
            rec["h2_mean"].append(rstates[1].mean(1).cpu().numpy())
            rec["actor_cls"].append(a_cls.cpu().numpy())
            rec["critic_press_cls"].append(c_cls.cpu().numpy())
        if record_quad:
            h1q = torch.stack([rstates[0][:, qidx_t[q]].mean(1) for q in range(4)], dim=1)
            h2q = torch.stack([rstates[1][:, qidx_t[q]].mean(1) for q in range(4)], dim=1)
            rec["h1_quad"].append(h1q.cpu().numpy())
            rec["h2_quad"].append(h2q.cpu().numpy())
        # act
        if policy == "argmax":
            actions = logits.argmax(-1).cpu().numpy().astype(np.int64)
        else:
            actions = np.zeros(B, dtype=np.int64)
        for i in range(B):
            if done[i]:
                continue
            a = int(actions[i])
            o, r, d, _ = envs[i].step(a)
            obs[i] = o
            if a == 1 and press_index[i] < 0:
                press_index[i] = t
            reward[i] = float(r)
            if d:
                done[i] = True
        t += 1

    out: Dict[str, object] = {}
    for k, v in rec.items():
        out[k] = np.stack(v, axis=0)                                 # (T, B, ...)
    pressed = press_index >= 0
    premature = pressed & (press_index < change_time)
    hit = pressed & (press_index >= change_time) & (change_true == 1)
    rt = np.where(hit, press_index - change_time, np.nan).astype(np.float32)
    out.update({
        "press_index": press_index, "pressed": pressed, "premature": premature,
        "hit": hit, "rt": rt, "reward": reward,
        "change_time": change_time, "change_true": change_true,
        "cue_position": np.array([e.cue_position for e in envs], dtype=object),
        "cue_color": np.array([e.cue_color for e in envs], dtype=object),
        "proportion": np.array([float(e.proportion) for e in envs], dtype=np.float32),
        "change_index": np.array([int(getattr(e, "change_index", -1)) for e in envs], dtype=np.int64),
        "orientation_change": np.array([float(e.orientation_change) for e in envs], dtype=np.float32),
        "n_steps": t,
    })
    return out


_PER_TRIAL_KEYS = {
    "press_index", "pressed", "premature", "hit", "rt", "reward", "change_time",
    "change_true", "cue_position", "cue_color", "proportion", "change_index",
    "orientation_change",
}


def record_rollout_chunked(model, envs, obs0, device, *, chunk: int = 400, **kw):
    """Memory-safe wrapper: split the trials into chunks of ≤`chunk`, run each
    through record_rollout (run_full=True so every chunk yields exactly T frames),
    and concatenate. Avoids the multi-GB (B,H,3N,3N) attention allocation that a
    single huge batch would make. kw forwarded to record_rollout."""
    kw["run_full"] = True
    B = len(envs)
    parts = []
    for s in range(0, B, chunk):
        e = envs[s:s + chunk]; o = obs0[s:s + chunk]
        parts.append(record_rollout(model, e, o, device, **kw))
    out: Dict[str, object] = {}
    for k in parts[0]:
        if k == "n_steps":
            out[k] = max(int(p[k]) for p in parts)
        elif k in _PER_TRIAL_KEYS:
            out[k] = np.concatenate([p[k] for p in parts], axis=0)
        else:                                       # time-series (T, B, ...)
            out[k] = np.concatenate([p[k] for p in parts], axis=1)
    return out


# ──────────────────────────────────────────────────────────────────────────────
# attention-bias builders for the causal experiment
# ──────────────────────────────────────────────────────────────────────────────
def make_attn_bias(model, device, *, layer: int, head: int, region: str,
                   value: float, quad: Optional[int] = None) -> torch.Tensor:
    """Build a (n_layers, n_heads, 3N) additive attention-logit bias that targets
    ONE (layer, head). region ∈ {'patch','quad','memory'}:
      'patch'  → bias all N patch keys by `value`
      'quad'   → bias the N-block patch keys of `quad` by `value`
      'memory' → bias the 2N memory keys by `value`
    """
    nL, H, N = model.encoder.n_layers, model.encoder.enc[0].self_attn.num_heads, model.n_tokens
    bias = torch.zeros(nL, H, 3 * N, device=device)
    if region == "patch":
        bias[layer, head, :N] = value
    elif region == "memory":
        bias[layer, head, N:3 * N] = value
    elif region == "quad":
        assert quad is not None
        qi = quadrant_token_indices(model.patch_embed.grid_h, model.patch_embed.grid_w)[quad]
        bias[layer, head, qi] = value
    else:
        raise ValueError(region)
    return bias


def _selfcheck() -> None:
    """Verify the manual attention reproduces the stock forward (bias=0)."""
    cfg = load_config()
    device = torch.device("cpu")
    model = build_model(cfg, device)
    model.eval()
    B = 3
    states = model.init_states(B, device=device)
    x = torch.randn(B, 3, 50, 50)
    tokens = model.patch_embed(x)
    # stock encoder step
    (Hs0, Cs0), rec0 = model.encoder.forward_step(tokens, states)
    # manual
    (Hs1, Cs1), rec1 = memtok_forward_step(model.encoder, tokens, states)
    d_enc = max(float((a - b).abs().max()) for a, b in zip(rec0, rec1))
    # decoders
    al0 = model.actor_head(rec0)
    al1, _ = actor_decode(model.actor_head, rec0)
    d_act = float((al0 - al1).abs().max())
    q0 = model.critic_head(rec0)
    q1p, _ = critic_decode(model.critic_head, rec0, 1)
    d_cri = float((q0[:, 1] - q1p).abs().max())
    print(f"[selfcheck] encoder rec max|Δ|={d_enc:.2e}  actor logits Δ={d_act:.2e}  "
          f"critic(press) Δ={d_cri:.2e}")
    assert d_enc < 1e-4 and d_act < 1e-4 and d_cri < 1e-4, "manual attention mismatch!"
    print("[selfcheck] OK — manual attention is faithful")


if __name__ == "__main__":
    _selfcheck()
