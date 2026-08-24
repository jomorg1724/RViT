"""
Deep-dive core harness for the trained RViT+ v5_part2 model.

Port of ``RViT_plus_v5/analysis/deepdive/dd_core.py`` adapted to the v5_part2
architecture, whose two structural differences from v5 are:

  * ENCODER is a CROSS-ATTENTION-over-memory block (NOT memory-as-tokens
    self-attention). The patch tokens X are the QUERIES (N tokens); the
    keys/values are [X ++ H1 ++ H2] = (1+n_lstm)·N = 3N tokens. Because there
    are only N queries the attention output Z is inherently (B, N, d_model) — no
    slice-from-3N. We provide ``cross_attn_forward_step`` — a bias-injectable,
    attention-returning replica of ``TxLSTMEncoder.forward_step`` that manually
    replicates each ``_CrossAttnBlock``'s multi-head cross-attention (so we can
    (a) return per-head weights of shape (B, heads, N, 3N) and (b) inject an
    ADDITIVE per-(layer, head, key) bias into the pre-softmax logits, broadcast
    over the N queries) and then advances the stacked LSTMCells exactly like the
    stock step. In eval() the dropouts are identity, so at bias=0 the recurrent
    output matches the stock forward exactly (verified in ``_selfcheck``).

  * DECODERS are tiny 1D-CONV heads — there is NO decoder attention, no CLS. So
    ``actor_decode`` / ``critic_decode`` just call the real
    ``model.actor_head`` / ``model.critic_head`` (critic indexed by action). Where
    v5 recorded an actor_cls / critic_cls CLS readout, we instead record the
    FLATTENED conv-trunk penultimate feature (``head.trunk(x).flatten(1)``) as the
    decoder readout latent.

The env (ChangeDetectionEnv) quadrant indexing is the project standard:
    0 = S1 top-left (gabor1, cue 'left')   2 = S3 top-right  (gabor3)
    1 = S2 bottom-left (gabor2)            3 = S4 bottom-right (gabor4, cue 'right')
Patch tokens are row-major on a 10x10 grid (token i*gw+j = grid cell (i,j)),
so each 25x25 Gabor quadrant is a 5x5 block of patch tokens. The 3N keys are
ordered [patch(0:N) ++ H1(N:2N) ++ H2(2N:3N)].
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

from RViT_plus_v5_part2.analysis import _behav_utils as bu  # noqa: E402

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

DEFAULT_CKPT = "/Users/jonathanmorgan/rvit_plus_checkpoints/v5_part2/v5p2_analysis_snapshot.pt"


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
# manual multi-head CROSS-attention (faithful to nn.MultiheadAttention)
# ──────────────────────────────────────────────────────────────────────────────
def manual_cross_attention(
    mha: torch.nn.MultiheadAttention,
    q_in: torch.Tensor,
    kv_in: torch.Tensor,
    score_bias: Optional[torch.Tensor] = None,
) -> Tuple[torch.Tensor, torch.Tensor]:
    """Replicate ``mha(q_in, kv_in, kv_in, need_weights=True,
    average_attn_weights=False)`` with full control of the pre-softmax scores.

    q_in       : (B, Sq, d_model) — the N (already-normed) patch queries.
    kv_in      : (B, Sk, d_model) — the 3N (already-normed) [patch ++ H1 ++ H2]
                 keys/values.
    score_bias : optional (n_heads, Sk) or (n_heads, Sq, Sk) additive bias added
                 to the attention logits BEFORE softmax. (n_heads, Sk) is
                 broadcast over the QUERY axis (a per-key, per-head bias — the form
                 used by the causal experiment). None → identity.

    nn.MultiheadAttention packs Q,K,V projections in ``in_proj_weight`` /
    ``in_proj_bias`` as rows [W_q; W_k; W_v]. With distinct query vs key/value
    inputs we project q_in by the Q chunk and kv_in by the K and V chunks.

    Returns (attn_out (B,Sq,d_model), attn_w (B, n_heads, Sq, Sk)). With
    score_bias=None this matches the stock module to <1e-5 (verified).
    """
    B, Sq, d = q_in.shape
    Sk = kv_in.shape[1]
    H = mha.num_heads
    dh = d // H
    w_q, w_k, w_v = mha.in_proj_weight.chunk(3, dim=0)               # (d,d) each
    if mha.in_proj_bias is not None:
        b_q, b_k, b_v = mha.in_proj_bias.chunk(3, dim=0)
    else:
        b_q = b_k = b_v = None
    q = F.linear(q_in, w_q, b_q)                                     # (B,Sq,d)
    k = F.linear(kv_in, w_k, b_k)                                    # (B,Sk,d)
    v = F.linear(kv_in, w_v, b_v)                                    # (B,Sk,d)
    q = q.view(B, Sq, H, dh).transpose(1, 2)                        # (B,H,Sq,dh)
    k = k.view(B, Sk, H, dh).transpose(1, 2)                        # (B,H,Sk,dh)
    v = v.view(B, Sk, H, dh).transpose(1, 2)                        # (B,H,Sk,dh)
    scores = torch.matmul(q, k.transpose(-2, -1)) / (dh ** 0.5)      # (B,H,Sq,Sk)
    if score_bias is not None:
        if score_bias.dim() == 2:                                   # (H,Sk) per-key
            scores = scores + score_bias[None, :, None, :]
        elif score_bias.dim() == 3:                                 # (H,Sq,Sk)
            scores = scores + score_bias[None]
        else:
            raise ValueError(f"score_bias must be 2D or 3D; got {tuple(score_bias.shape)}")
    attn = torch.softmax(scores, dim=-1)                            # (B,H,Sq,Sk)
    out = torch.matmul(attn, v)                                     # (B,H,Sq,dh)
    out = out.transpose(1, 2).contiguous().view(B, Sq, d)
    out = F.linear(out, mha.out_proj.weight, mha.out_proj.bias)
    return out, attn


# ──────────────────────────────────────────────────────────────────────────────
# bias-injectable, attention-returning CROSS-ATTENTION encoder step
# ──────────────────────────────────────────────────────────────────────────────
def cross_attn_forward_step(
    encoder,
    tokens: torch.Tensor,
    prev_state,
    attn_bias: Optional[torch.Tensor] = None,
    return_attn: bool = False,
):
    """Bias-injectable replica of TxLSTMEncoder.forward_step.

    For each ``_CrossAttnBlock`` (there are tx_layers of them, default 1):
        mem_kv = cat_k([ Hs[k] + mem_pos_emb + mem_tag[k] ])  over n_lstm memories
        kv     = norm_kv( cat([X, mem_kv]) )                  # (B, 3N, d)
        a, aw  = attn( norm_q(X), kv, kv )                    # query = N patch tokens
        Z      = X + drop(a)                                  # residual on the queries
        Z      = Z + ffn(norm_ff(Z))
    then advance the stacked LSTMCells exactly like the stock forward_step.

    attn_bias : optional (tx_layers, n_heads, 3N) additive per-key bias added to
                the pre-softmax attention logits of that block (broadcast over the
                N queries). Keys are ordered [patch(N) ++ H1(N) ++ H2(N)].
    Returns (new_state, rec[, attn_per_block]) exactly like the original;
    rec = [H1, …, H_{n_lstm}]; attn_per_block[i]: (B, heads, N, 3N).
    """
    Hs, Cs = list(prev_state[0]), list(prev_state[1])
    B, N = tokens.shape[0], encoder.n_tokens

    # Memory tokens = PREVIOUS-frame LSTM states, tagged by source + position.
    mem_kv = torch.cat(
        [Hs[k] + encoder.mem_pos_emb + encoder.mem_tag[k] for k in range(encoder.n_lstm)],
        dim=1,
    )                                                               # (B, n_lstm*N, d)

    X = tokens
    attn_per_block: List[Optional[torch.Tensor]] = []
    for li, blk in enumerate(encoder.blocks):
        kv = blk.norm_kv(torch.cat([X, mem_kv], dim=1))             # (B, (1+n_lstm)*N, d)
        q_in = blk.norm_q(X)                                        # (B, N, d)
        sb = None if attn_bias is None else attn_bias[li]           # (H, 3N)
        a, aw = manual_cross_attention(blk.attn, q_in, kv, sb)
        Z = X + blk.drop(a)                                         # residual on the queries
        Z = Z + blk.ffn(blk.norm_ff(Z))
        X = Z
        attn_per_block.append(aw)
    Z = X                                                           # (B, N, d_model)

    inp = Z
    for li, cell in enumerate(encoder.cells):
        h, c = cell(
            inp.reshape(B * N, inp.shape[-1]),
            (Hs[li].reshape(B * N, encoder.d_mem), Cs[li].reshape(B * N, encoder.d_mem)),
        )
        Hs[li] = h.view(B, N, encoder.d_mem)
        Cs[li] = c.view(B, N, encoder.d_mem)
        inp = Hs[li]
    rec = [Hs[li] for li in range(encoder.n_lstm)]
    if return_attn:
        return (Hs, Cs), rec, attn_per_block
    return (Hs, Cs), rec


# ──────────────────────────────────────────────────────────────────────────────
# decoder readouts (1D-conv heads — NO attention, NO CLS)
# ──────────────────────────────────────────────────────────────────────────────
def _trunk_feature(head, rec_states: List[torch.Tensor]) -> torch.Tensor:
    """Flattened conv-trunk penultimate feature (B, conv_ch*L') — the v5_part2
    stand-in for v5's CLS readout latent."""
    x = rec_states[-1].transpose(1, 2).contiguous()                 # (B, d_mem, N)
    return head.trunk(x).flatten(1)


def actor_decode(actor, rec_states, return_feat: bool = False):
    """Reproduce ActorDecoder: returns (logits[, trunk_feat]). There is NO decoder
    attention; trunk_feat is the flattened conv-trunk penultimate feature."""
    logits = actor(rec_states)                                      # (B, n_actions)
    if return_feat:
        return logits, _trunk_feature(actor, rec_states)
    return logits


def critic_decode(critic, rec_states, action: int, return_feat: bool = False):
    """Reproduce CriticDecoder for ONE action: returns (q_quantiles (B,Nq)[, feat]).
    The conv head emits (B, n_actions, Nq); we index the requested action."""
    q_all = critic(rec_states)                                      # (B, n_actions, Nq)
    q = q_all[:, action]                                            # (B, Nq)
    if return_feat:
        return q, _trunk_feature(critic, rec_states)
    return q


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
      (if record_latents) h1_mean,h2_mean (B,d); actor_cls,critic_press_cls
      (B, conv_ch*L' — the flattened conv-trunk penultimate feature, the
      v5_part2 stand-in for v5's decoder CLS readout); (if record_quad)
      h1_quad,h2_quad (B,4,d).
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
        states, rstates = cross_attn_forward_step(model.encoder, tokens, states, attn_bias=attn_bias)
        logits, a_feat = actor_decode(model.actor_head, rstates, return_feat=True)
        q_press, c_feat = critic_decode(model.critic_head, rstates, 1, return_feat=True)
        q_wait = critic_decode(model.critic_head, rstates, 0)
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
            rec["actor_cls"].append(a_feat.cpu().numpy())
            rec["critic_press_cls"].append(c_feat.cpu().numpy())
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
    and concatenate. Avoids the multi-GB (B,H,N,3N) attention allocation that a
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
    """Build a (tx_layers, n_heads, 3N) additive attention-logit bias that targets
    ONE (layer, head). Keys are ordered [patch(0:N) ++ H1(N:2N) ++ H2(2N:3N)].
    region ∈ {'patch','quad','memory','memquad'}:
      'patch'   → bias all N patch keys by `value`
      'quad'    → bias the patch keys of `quad` (its N/4-block) by `value`
      'memory'  → bias the 2N memory (H1+H2) keys by `value`
      'memquad' → bias the H1+H2 keys of `quad` by `value` (the quadrant's token
                  rows in BOTH carried memories)
    """
    enc = model.encoder
    nL, H, N = enc.tx_layers, enc.n_heads, model.n_tokens
    n_lstm = enc.n_lstm
    bias = torch.zeros(nL, H, (1 + n_lstm) * N, device=device)
    if region == "patch":
        bias[layer, head, :N] = value
    elif region == "memory":
        bias[layer, head, N:(1 + n_lstm) * N] = value
    elif region == "quad":
        assert quad is not None
        qi = quadrant_token_indices(model.patch_embed.grid_h, model.patch_embed.grid_w)[quad]
        bias[layer, head, qi] = value
    elif region == "memquad":
        assert quad is not None
        qi = quadrant_token_indices(model.patch_embed.grid_h, model.patch_embed.grid_w)[quad]
        for k in range(n_lstm):                     # H1 block, H2 block, …
            bias[layer, head, (1 + k) * N + qi] = value
    else:
        raise ValueError(region)
    return bias


@torch.no_grad()
def _selfcheck() -> None:
    """Verify the manual cross-attention step reproduces the stock encoder
    forward (bias=0) and that the decoder readouts match the stock heads."""
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
    # manual cross-attention step
    (Hs1, Cs1), rec1 = cross_attn_forward_step(model.encoder, tokens, states)
    d_enc = max(float((a - b).abs().max()) for a, b in zip(rec0, rec1))
    d_state = max(
        max(float((a - b).abs().max()) for a, b in zip(Hs0, Hs1)),
        max(float((a - b).abs().max()) for a, b in zip(Cs0, Cs1)),
    )
    # decoders (run on the stock rec)
    al0 = model.actor_head(rec0)
    al1 = actor_decode(model.actor_head, rec0)
    d_act = float((al0 - al1).abs().max())
    q0 = model.critic_head(rec0)                                     # (B, A, Nq)
    q1p = critic_decode(model.critic_head, rec0, 1)
    q1w = critic_decode(model.critic_head, rec0, 0)
    d_cri = max(
        float((q0[:, 1] - q1p).abs().max()),
        float((q0[:, 0] - q1w).abs().max()),
    )
    print(f"[selfcheck] encoder rec max|Δ|={d_enc:.2e}  (Hs/Cs Δ={d_state:.2e})  "
          f"actor logits Δ={d_act:.2e}  critic Δ={d_cri:.2e}")
    assert d_enc < 1e-4 and d_state < 1e-4 and d_act < 1e-4 and d_cri < 1e-4, \
        "manual cross-attention / decoder readout mismatch!"
    print("[selfcheck] OK — manual cross-attention + decoder readouts are faithful")


if __name__ == "__main__":
    _selfcheck()
