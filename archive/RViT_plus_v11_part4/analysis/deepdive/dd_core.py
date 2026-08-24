"""
Deep-dive core harness for the trained RViT+ v11_part2 model (SPLIT-readout
dual-stream, single head, Tμ salience reads [H1‖H2]).

Adapted from the v11 dd_core. v11_part2's differences from v11:

  * Tμ SALIENCE: Q=X, K=V=[H1 ‖ H2] (each source-tagged with encoder.sal_tag),
    residual=X → Z_sal. So the salience attention is (B, heads, N, 2N), keys
    ordered [H1(0:N) ‖ H2(N:2N)]. (v11 salience read K=V=H1 only, N keys.)
  * TQ TOP-DOWN: Q=X, K=V=H2 (+pos), residual=H2 → Z_td. (B, heads, N, N). Same as v11.
  * SINGLE head per stream (n_heads=1).
  * SPLIT readout: the ACTOR reads ONLY Z_sal, the CRITIC reads ONLY Z_td (each
    head ingests d_model channels, not 2·d_model). So actor_decode is fed [Z_sal]
    and critic_decode is fed [Z_td].

``dual_stream_forward_step`` is a bias-injectable, attention-returning replica of
``DualStreamEncoder.forward_step`` verified against the stock encoder (selfcheck).
The injected bias is a dict {'sal': (heads, 2N) | None, 'td': (heads, N) | None}
added to the pre-softmax logits of the respective stream (broadcast over queries).

Quadrant indexing (project standard): 0=S1 top-left (cue 'left'), 1=S2 bottom-left,
2=S3 top-right, 3=S4 bottom-right. Patch tokens row-major on a 10x10 grid; each
memory row i ↔ patch position i.
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

from RViT_plus_v11_part2.analysis import _behav_utils as bu  # noqa: E402

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
STREAMS = ["salience", "topdown"]            # actor reads salience, critic reads top-down
STREAM2I = {"sal": 0, "salience": 0, "td": 1, "topdown": 1}

DEFAULT_CKPT = "/Users/jonathanmorgan/rvit_plus_checkpoints/v11_part2/v11_part2_analysis_snapshot.pt"


# ──────────────────────────────────────────────────────────────────────────────
# quadrant <-> token bookkeeping
# ──────────────────────────────────────────────────────────────────────────────
def quadrant_token_indices(gh: int = 10, gw: int = 10) -> Dict[int, np.ndarray]:
    idx = np.arange(gh * gw).reshape(gh, gw)
    hh, ww = gh // 2, gw // 2
    return {
        0: idx[:hh, :ww].ravel().copy(),
        1: idx[hh:, :ww].ravel().copy(),
        2: idx[:hh, ww:].ravel().copy(),
        3: idx[hh:, ww:].ravel().copy(),
    }


def grid_to_image(grid: np.ndarray, patch: int = 5) -> np.ndarray:
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
    """Replicate mha(q_in, kv_in, kv_in, need_weights=True, average_attn_weights=False).
    score_bias: optional (n_heads, Sk) per-key bias (broadcast over queries) or
    (n_heads, Sq, Sk). Returns (out (B,Sq,d), attn (B,heads,Sq,Sk))."""
    B, Sq, d = q_in.shape
    Sk = kv_in.shape[1]
    H = mha.num_heads
    dh = d // H
    w_q, w_k, w_v = mha.in_proj_weight.chunk(3, dim=0)
    if mha.in_proj_bias is not None:
        b_q, b_k, b_v = mha.in_proj_bias.chunk(3, dim=0)
    else:
        b_q = b_k = b_v = None
    q = F.linear(q_in, w_q, b_q).view(B, Sq, H, dh).transpose(1, 2)
    k = F.linear(kv_in, w_k, b_k).view(B, Sk, H, dh).transpose(1, 2)
    v = F.linear(kv_in, w_v, b_v).view(B, Sk, H, dh).transpose(1, 2)
    scores = torch.matmul(q, k.transpose(-2, -1)) / (dh ** 0.5)      # (B,H,Sq,Sk)
    if score_bias is not None:
        if score_bias.dim() == 2:
            scores = scores + score_bias[None, :, None, :]
        elif score_bias.dim() == 3:
            scores = scores + score_bias[None]
        else:
            raise ValueError(f"score_bias must be 2D or 3D; got {tuple(score_bias.shape)}")
    attn = torch.softmax(scores, dim=-1)
    out = torch.matmul(attn, v).transpose(1, 2).contiguous().view(B, Sq, d)
    out = F.linear(out, mha.out_proj.weight, mha.out_proj.bias)
    return out, attn


def _apply_block(blk, q_src, kv_src, residual, score_bias):
    kv = blk.norm_kv(kv_src)
    q_in = blk.norm_q(q_src)
    a, aw = manual_cross_attention(blk.attn, q_in, kv, score_bias)
    Z = residual + blk.drop(a)
    Z = Z + blk.ffn(blk.norm_ff(Z))
    return Z, aw


# ──────────────────────────────────────────────────────────────────────────────
# bias-injectable, attention-returning DUAL-STREAM encoder step (v11_part2)
# ──────────────────────────────────────────────────────────────────────────────
def dual_stream_forward_step(
    encoder,
    tokens: torch.Tensor,
    prev_state,
    attn_bias: Optional[dict] = None,
    return_attn: bool = False,
):
    """Bias-injectable replica of v11_part2 DualStreamEncoder.forward_step.

    Tμ SALIENCE: Z_sal = X  + attn(Q=X, K=V=[H1+pos+tag0 ‖ H2+pos+tag1]) + FFN  (res X)
    TQ TOP-DOWN: Z_td  = H2 + attn(Q=X, K=V=H2+pos) + FFN                       (res H2)
    Then H1 = LSTM1(X) ; H2 = LSTM2(Z_sal).

    attn_bias : optional dict {'sal': (heads, 2N) | None, 'td': (heads, N) | None}
                added to pre-softmax logits (broadcast over queries). Salience keys
                ordered [H1(0:N) ‖ H2(N:2N)]; top-down keys are the N H2 rows.
    Returns (new_state, rec=[Z_sal, Z_td][, attn=[aw_sal, aw_td]]);
    aw_sal (B,heads,N,2N), aw_td (B,heads,N,N).
    """
    Hs, Cs = list(prev_state[0]), list(prev_state[1])
    B, N = tokens.shape[0], encoder.n_tokens
    H1, H2 = Hs[0], Hs[1]
    C1, C2 = Cs[0], Cs[1]
    X = tokens
    pos = encoder.mem_pos_emb
    sb_sal = None if attn_bias is None else attn_bias.get("sal")
    sb_td = None if attn_bias is None else attn_bias.get("td")

    sal_kv = torch.cat([H1 + pos + encoder.sal_tag[0], H2 + pos + encoder.sal_tag[1]], dim=1)  # (B,2N,d)
    Z_sal, aw_sal = _apply_block(encoder.sal_block, X, sal_kv, residual=X, score_bias=sb_sal)
    Z_td, aw_td = _apply_block(encoder.td_block, X, H2 + pos, residual=H2, score_bias=sb_td)

    h1, c1 = encoder.cell1(
        X.reshape(B * N, encoder.d_model),
        (H1.reshape(B * N, encoder.d_mem), C1.reshape(B * N, encoder.d_mem)),
    )
    h2, c2 = encoder.cell2(
        Z_sal.reshape(B * N, encoder.d_model),
        (H2.reshape(B * N, encoder.d_mem), C2.reshape(B * N, encoder.d_mem)),
    )
    new_Hs = [h1.view(B, N, encoder.d_mem), h2.view(B, N, encoder.d_mem)]
    new_Cs = [c1.view(B, N, encoder.d_mem), c2.view(B, N, encoder.d_mem)]
    rec = [Z_sal, Z_td]
    if return_attn:
        return (new_Hs, new_Cs), rec, [aw_sal, aw_td]
    return (new_Hs, new_Cs), rec


# ──────────────────────────────────────────────────────────────────────────────
# decoder readouts — SPLIT: actor reads [Z_sal], critic reads [Z_td]
# ──────────────────────────────────────────────────────────────────────────────
def _trunk_feature(head, stream_list: List[torch.Tensor]) -> torch.Tensor:
    """Flattened conv-trunk penultimate feature from a single readout stream
    (d_model channels). stream_list is a 1-element list ([Z_sal] or [Z_td])."""
    x = torch.cat(stream_list, dim=-1).transpose(1, 2).contiguous()  # (B, d, N)
    return head.trunk(x).flatten(1)


def actor_decode(actor, rec_states, return_feat: bool = False):
    """ActorDecoder reads ONLY Z_sal (rec_states[0])."""
    z_sal = [rec_states[0]]
    logits = actor(z_sal)
    if return_feat:
        return logits, _trunk_feature(actor, z_sal)
    return logits


def critic_decode(critic, rec_states, action: int, return_feat: bool = False):
    """CriticDecoder reads ONLY Z_td (rec_states[1])."""
    z_td = [rec_states[1]]
    q_all = critic(z_td)                                            # (B, n_actions, Nq)
    q = q_all[:, action]
    if return_feat:
        return q, _trunk_feature(critic, z_td)
    return q


# ──────────────────────────────────────────────────────────────────────────────
# critic distribution summaries
# ──────────────────────────────────────────────────────────────────────────────
def quantile_entropy(q: torch.Tensor) -> torch.Tensor:
    qs, _ = torch.sort(q, dim=-1)
    Nq = qs.shape[-1]
    dz = (qs[..., 1:] - qs[..., :-1]).clamp_min(1e-6)
    return ((1.0 / Nq) * torch.log(Nq * dz)).sum(dim=-1)


def quantile_std(q: torch.Tensor) -> torch.Tensor:
    return q.std(dim=-1)


def policy_entropy(logits: torch.Tensor) -> torch.Tensor:
    logp = F.log_softmax(logits, dim=-1)
    p = logp.exp()
    return -(p * logp).sum(dim=-1)


# ──────────────────────────────────────────────────────────────────────────────
# recording rollout
# ──────────────────────────────────────────────────────────────────────────────
@torch.no_grad()
def record_rollout(
    model, envs, obs0, device, *,
    policy: str = "wait",
    attn_bias: Optional[dict] = None,
    record_latents: bool = True,
    record_quad: bool = True,
    run_full: bool = False,
) -> Dict[str, object]:
    """Run B trials, recording behaviour + per-step latents/value. Latents:
    z_sal/z_td (the actor/critic readouts) and h1/h2 (LSTM memories), mean + quad;
    actor_cls = conv-trunk feature on Z_sal, critic_press_cls = on Z_td."""
    B = len(envs)
    model.eval()
    states = model.init_states(B, device=device)
    obs = list(obs0)
    T = envs[0].T
    rec: Dict[str, List] = {k: [] for k in [
        "v_scalar", "q_wait", "q_press", "v_dist", "qent_press", "qstd_press",
        "pol_entropy", "press_prob", "actor_logits", "frame_mean"]}
    if record_latents:
        rec.update({"z_sal_mean": [], "z_td_mean": [], "h1_mean": [], "h2_mean": [],
                    "actor_cls": [], "critic_press_cls": []})
    if record_quad:
        rec.update({"z_sal_quad": [], "z_td_quad": [], "h1_quad": [], "h2_quad": []})
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
        states, rstates = dual_stream_forward_step(model.encoder, tokens, states, attn_bias=attn_bias)
        H1, H2 = states[0][0], states[0][1]
        logits, a_feat = actor_decode(model.actor_head, rstates, return_feat=True)
        q_press, c_feat = critic_decode(model.critic_head, rstates, 1, return_feat=True)
        q_wait = critic_decode(model.critic_head, rstates, 0)
        q_dist = torch.stack([q_wait, q_press], dim=1)
        pi = torch.softmax(logits, dim=-1)
        v_dist = (pi.detach().unsqueeze(-1) * q_dist).sum(dim=1)
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
            rec["z_sal_mean"].append(rstates[0].mean(1).cpu().numpy())
            rec["z_td_mean"].append(rstates[1].mean(1).cpu().numpy())
            rec["h1_mean"].append(H1.mean(1).cpu().numpy())
            rec["h2_mean"].append(H2.mean(1).cpu().numpy())
            rec["actor_cls"].append(a_feat.cpu().numpy())
            rec["critic_press_cls"].append(c_feat.cpu().numpy())
        if record_quad:
            for name, src in (("z_sal_quad", rstates[0]), ("z_td_quad", rstates[1]),
                              ("h1_quad", H1), ("h2_quad", H2)):
                rec[name].append(
                    torch.stack([src[:, qidx_t[q]].mean(1) for q in range(4)], dim=1).cpu().numpy())
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
        out[k] = np.stack(v, axis=0)
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


def record_rollout_chunked(model, envs, obs0, device, *, chunk: int = 256, **kw):
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
        else:
            out[k] = np.concatenate([p[k] for p in parts], axis=1)
    return out


# ──────────────────────────────────────────────────────────────────────────────
# attention-bias builders for the causal experiment
# ──────────────────────────────────────────────────────────────────────────────
def make_attn_bias(model, device, *, stream: str, head: Optional[int], region: str,
                   value: float, quad: Optional[int] = None) -> dict:
    """Build {'sal': (heads,2N)|None, 'td': (heads,N)|None}. Only the chosen stream
    is non-None. head=None → all heads. region:
      salience stream keys ordered [H1(0:N) ‖ H2(N:2N)]:
        'all'    → all 2N salience keys
        'h1'     → the N H1 keys ; 'h2' → the N H2 keys
        'h1quad'/'h2quad' → that memory's keys for one quadrant
      top-down stream keys = N H2 rows:
        'all'   → all N ; 'quad' → one quadrant's H2 keys
    """
    enc = model.encoder
    H, N = enc.n_heads, model.n_tokens
    sidx = STREAM2I[stream]
    qi = (None if quad is None
          else quadrant_token_indices(model.patch_embed.grid_h, model.patch_embed.grid_w)[quad])
    heads = range(H) if head is None else [head]
    out = {"sal": None, "td": None}
    if sidx == 0:                                   # salience: 2N keys
        b = torch.zeros(H, 2 * N, device=device)
        if region == "all":
            cols = slice(0, 2 * N)
        elif region == "h1":
            cols = slice(0, N)
        elif region == "h2":
            cols = slice(N, 2 * N)
        elif region == "h1quad":
            cols = qi
        elif region == "h2quad":
            cols = N + qi
        else:
            raise ValueError(region)
        for h in heads:
            b[h, cols] = value
        out["sal"] = b
    else:                                           # top-down: N keys
        b = torch.zeros(H, N, device=device)
        if region == "all":
            cols = slice(0, N)
        elif region == "quad":
            cols = qi
        else:
            raise ValueError(region)
        for h in heads:
            b[h, cols] = value
        out["td"] = b
    return out


def _selfcheck() -> None:
    cfg = load_config()
    device = torch.device("cpu")
    model = build_model(cfg, device)
    model.eval()
    B = 3
    states = model.init_states(B, device=device)
    x = torch.randn(B, 3, 50, 50)
    tokens = model.patch_embed(x)
    (Hs0, Cs0), rec0 = model.encoder.forward_step(tokens, states)
    (Hs1, Cs1), rec1 = dual_stream_forward_step(model.encoder, tokens, states)
    d_rec = max(float((a - b).abs().max()) for a, b in zip(rec0, rec1))
    d_state = max(
        max(float((a - b).abs().max()) for a, b in zip(Hs0, Hs1)),
        max(float((a - b).abs().max()) for a, b in zip(Cs0, Cs1)),
    )
    # split-readout decode vs stock model._run_heads
    al0, q0, _, _ = model._run_heads(rec0)
    al1 = actor_decode(model.actor_head, rec0)
    q1p = critic_decode(model.critic_head, rec0, 1)
    q1w = critic_decode(model.critic_head, rec0, 0)
    d_act = float((al0 - al1).abs().max())
    d_cri = max(float((q0[:, 1] - q1p).abs().max()), float((q0[:, 0] - q1w).abs().max()))
    _, _, attn = dual_stream_forward_step(model.encoder, tokens, states, return_attn=True)
    shapes = [tuple(a.shape) for a in attn]
    print(f"[selfcheck] rec [Z_sal,Z_td] max|delta|={d_rec:.2e}  (Hs/Cs delta={d_state:.2e})  "
          f"actor delta={d_act:.2e}  critic delta={d_cri:.2e}  attn shapes={shapes}")
    assert d_rec < 1e-4 and d_state < 1e-4 and d_act < 1e-4 and d_cri < 1e-4, \
        "manual dual-stream / split-readout mismatch!"
    print("[selfcheck] OK — manual dual-stream step + split-readout decoders are faithful")


if __name__ == "__main__":
    _selfcheck()
