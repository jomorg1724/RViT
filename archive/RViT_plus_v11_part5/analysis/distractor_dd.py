"""
Distractor deep-dive harness for the trained v11_part5 model (shared-memory /
cross-talk dual-stream agent, tested on the cued-SIDE task WITH distractors).

The encoder is architecturally identical to v11_part2 (sal_block Q=X/KV=[H1‖H2]/res=X,
td_block Q=X/KV=H2/res=H2, sal_tag, cell1←X, cell2←Z_sal), so the faithful,
bias-injectable attention replica below is exact (verified by selfcheck against the
stock encoder.forward_step). What is NEW here is the TASK: each trial has a TARGET
change on the cued side and, with prob distractor_prob, a DISTRACTOR change on the
UNCUED side with independent time/magnitude. The agent must detect the target and
SUPPRESS responses to the distractor.

  quadrants: 0=top-left, 1=bottom-left  → LEFT side ; 2=top-right, 3=bottom-right → RIGHT side
  cue 'left'  → cued side {0,1} (primary 0, secondary 1), distractor side {2,3}
  cue 'right' → cued side {3,2} (primary 3, secondary 2), distractor side {0,1}
"""
from __future__ import annotations

import json
import os
import sys
from typing import Dict, List, Optional

import numpy as np
import torch
import torch.nn.functional as F

_HERE = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(os.path.dirname(_HERE))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from RViT_plus_v11_part5.env import ChangeDetectionEnv, SIDE_QUADRANTS
from RViT_plus_v11_part5.model import RViTPlusV11Part5Model

DEFAULT_CKPT = "/Users/jonathanmorgan/rvit_plus_checkpoints/v11_part5/rvit_plus_v11_part5_rl_latest.pt"
COLOR_VALUE = {"red": 5, "green": 3, "blue": 1}     # color_rewards keyed reward magnitude
PROPORTIONS = [1.0, 0.75, 0.5, 0.25]


# ── model / config ──────────────────────────────────────────────────────────
def load_config() -> dict:
    p = os.path.join(_PROJECT_ROOT, "RViT_plus_v11_part5", "config", "rvit_plus_config.json")
    with open(p) as f:
        return json.load(f)


def build_model(cfg: dict, device) -> RViTPlusV11Part5Model:
    m = cfg["model"]; rl = m["rl"]
    model = RViTPlusV11Part5Model(
        patch_size=m["patch_size"], patch_hidden=m["patch_hidden"], d_model=m["d_model"],
        d_mem=m["d_mem"], tx_heads=m["tx_heads"], tx_layers=m["tx_layers"], n_lstm=m["n_lstm"],
        conv_channels=m["conv_channels"], n_conv_layers=m["n_conv_layers"], conv_kernel=m["conv_kernel"],
        n_actions=rl["n_actions"], n_quantiles=rl["n_quantiles"],
        init_action_bias=rl.get("init_action_bias"), seq_len=cfg["ppo"]["seq_len"],
    ).to(device)
    return model.eval()


def load_checkpoint(model, ckpt_path: str, device) -> int:
    ck = torch.load(ckpt_path, map_location=device, weights_only=False)
    sd = ck["model_state_dict"]
    info = model.load_state_dict(sd, strict=False)
    if info.missing_keys or info.unexpected_keys:
        print(f"[load] WARN missing={len(info.missing_keys)} unexpected={len(info.unexpected_keys)}")
    return int(ck.get("iter", -1))


def _obs_to_tensor(obs_list, device) -> torch.Tensor:
    arr = np.stack([o.astype(np.float32) for o in obs_list], axis=0)
    return torch.from_numpy(arr).permute(0, 3, 1, 2).contiguous().to(device)


# ── quadrant / side bookkeeping ───────────────────────────────────────────────
def quadrant_token_indices(gh: int = 10, gw: int = 10) -> Dict[int, np.ndarray]:
    idx = np.arange(gh * gw).reshape(gh, gw)
    hh, ww = gh // 2, gw // 2
    return {0: idx[:hh, :ww].ravel().copy(), 1: idx[hh:, :ww].ravel().copy(),
            2: idx[:hh, ww:].ravel().copy(), 3: idx[hh:, ww:].ravel().copy()}


def cued_side_quads(cue_position: str):
    s = SIDE_QUADRANTS[cue_position]
    return s["primary"], s["secondary"], list(s["distractor"])


# ── faithful, bias-injectable cross-attention (exact replica, arch == v11_part2) ──
def manual_cross_attention(mha, q_in, kv_in, score_bias=None):
    B, Sq, d = q_in.shape
    Sk = kv_in.shape[1]; H = mha.num_heads; dh = d // H
    w_q, w_k, w_v = mha.in_proj_weight.chunk(3, dim=0)
    b_q, b_k, b_v = (mha.in_proj_bias.chunk(3, dim=0) if mha.in_proj_bias is not None else (None, None, None))
    q = F.linear(q_in, w_q, b_q).view(B, Sq, H, dh).transpose(1, 2)
    k = F.linear(kv_in, w_k, b_k).view(B, Sk, H, dh).transpose(1, 2)
    v = F.linear(kv_in, w_v, b_v).view(B, Sk, H, dh).transpose(1, 2)
    scores = torch.matmul(q, k.transpose(-2, -1)) / (dh ** 0.5)
    if score_bias is not None:
        scores = scores + (score_bias[None, :, None, :] if score_bias.dim() == 2 else score_bias[None])
    attn = torch.softmax(scores, dim=-1)
    out = torch.matmul(attn, v).transpose(1, 2).contiguous().view(B, Sq, d)
    return F.linear(out, mha.out_proj.weight, mha.out_proj.bias), attn


def _apply_block(blk, q_src, kv_src, residual, score_bias):
    a, aw = manual_cross_attention(blk.attn, blk.norm_q(q_src), blk.norm_kv(kv_src), score_bias)
    Z = residual + blk.drop(a)
    return Z + blk.ffn(blk.norm_ff(Z)), aw


def dual_stream_step(encoder, tokens, prev_state, attn_bias=None, return_attn=False):
    Hs, Cs = list(prev_state[0]), list(prev_state[1])
    B, N = tokens.shape[0], encoder.n_tokens
    H1, H2 = Hs[0], Hs[1]; C1, C2 = Cs[0], Cs[1]
    X = tokens; pos = encoder.mem_pos_emb
    sb_sal = None if attn_bias is None else attn_bias.get("sal")
    sb_td = None if attn_bias is None else attn_bias.get("td")
    sal_kv = torch.cat([H1 + pos + encoder.sal_tag[0], H2 + pos + encoder.sal_tag[1]], dim=1)
    Z_sal, aw_sal = _apply_block(encoder.sal_block, X, sal_kv, residual=X, score_bias=sb_sal)
    Z_td, aw_td = _apply_block(encoder.td_block, X, H2 + pos, residual=H2, score_bias=sb_td)
    h1, c1 = encoder.cell1(X.reshape(B * N, encoder.d_model),
                           (H1.reshape(B * N, encoder.d_mem), C1.reshape(B * N, encoder.d_mem)))
    h2, c2 = encoder.cell2(Z_sal.reshape(B * N, encoder.d_model),
                           (H2.reshape(B * N, encoder.d_mem), C2.reshape(B * N, encoder.d_mem)))
    new = ([h1.view(B, N, encoder.d_mem), h2.view(B, N, encoder.d_mem)],
           [c1.view(B, N, encoder.d_mem), c2.view(B, N, encoder.d_mem)])
    rec = [Z_sal, Z_td]
    return (new, rec, [aw_sal, aw_td]) if return_attn else (new, rec)


def actor_decode(actor, rec, return_feat=False):
    z = [rec[0]]; logits = actor(z)
    if return_feat:
        x = torch.cat(z, dim=-1).transpose(1, 2).contiguous()
        return logits, actor.trunk(x).flatten(1)
    return logits


def critic_decode(critic, rec, action, return_feat=False):
    z = [rec[1]]; q = critic(z)[:, action]
    if return_feat:
        x = torch.cat(z, dim=-1).transpose(1, 2).contiguous()
        return q, critic.trunk(x).flatten(1)
    return q


STREAM2I = {"sal": 0, "salience": 0, "td": 1, "topdown": 1}


def make_attn_bias(model, device, *, stream, region, value, quad=None, head=None) -> dict:
    enc = model.encoder; H, N = enc.n_heads, model.n_tokens
    sidx = STREAM2I[stream]
    qi = None if quad is None else quadrant_token_indices(model.patch_embed.grid_h, model.patch_embed.grid_w)[quad]
    heads = range(H) if head is None else [head]
    out = {"sal": None, "td": None}
    if sidx == 0:
        b = torch.zeros(H, 2 * N, device=device)
        cols = {"all": slice(0, 2 * N), "h1": slice(0, N), "h2": slice(N, 2 * N)}.get(region)
        if cols is None:
            cols = (qi if region == "h1quad" else N + qi)
        for h in heads:
            b[h, cols] = value
        out["sal"] = b
    else:
        b = torch.zeros(H, N, device=device)
        cols = slice(0, N) if region == "all" else qi
        for h in heads:
            b[h, cols] = value
        out["td"] = b
    return out


# ── recording rollout (behavior + distractor fields + side-resolved attention + value) ──
@torch.no_grad()
def record_rollout(model, envs, obs0, device, *, policy="argmax", attn_bias=None,
                   capture_attn=False, capture_value=False, capture_map=False,
                   capture_quadlat=False, run_full=False, probe_offset=None) -> Dict[str, object]:
    B = len(envs); model.eval()
    states = model.init_states(B, device=device)
    obs = list(obs0); T = envs[0].T
    qidx = quadrant_token_indices(model.patch_embed.grid_h, model.patch_embed.grid_w)
    qidx_t = {q: torch.as_tensor(ix, device=device) for q, ix in qidx.items()}

    press_index = np.full(B, -1, dtype=np.int64)
    reward = np.zeros(B, dtype=np.float32)
    done = np.zeros(B, dtype=bool)
    # change-aligned probe: capture per-quadrant latents at t == change_time + probe_offset
    ctime_arr = np.array([int(e.change_time) for e in envs], dtype=np.int64)
    probe = None
    if probe_offset is not None:
        dq = model.encoder.d_mem
        probe = {k: np.zeros((B, 4, dq), dtype=np.float32) for k in ("zsal", "ztd", "h1", "h2")}
        probe_t = ctime_arr + int(probe_offset)
    seq = {"press_prob": [], "actor_logits": []}
    if capture_attn:
        seq.update({"sal_quad": [], "td_quad": []})     # (T,B,4) attention mass per quadrant
    if capture_map:
        # full 10x10 spatial attention maps (mean over heads & queries):
        #   sal_map_h1/sal_map_h2 = the two key blocks of the salience stream; td_map = top-down.
        seq.update({"sal_map_h1": [], "sal_map_h2": [], "td_map": []})  # (T,B,N)
    if capture_quadlat:
        seq.update({"ql_zsal": [], "ql_ztd": [], "ql_h1": [], "ql_h2": []})  # (T,B,4,d) per-quad latents
    if capture_value:
        seq.update({"q_press": [], "q_wait": [], "v_scalar": [], "qstd_press": []})

    t = 0
    while t < T and (run_full or not done.all()):
        x = _obs_to_tensor(obs, device)
        tokens = model.patch_embed(x)
        if capture_attn or capture_map:
            states, rec, attn = dual_stream_step(model.encoder, tokens, states, attn_bias=attn_bias, return_attn=True)
            aw_sal, aw_td = attn                          # (B,heads,N,2N),(B,heads,N,N)
            # mean over heads & query tokens → per-key attention.
            sal_key = aw_sal.mean(dim=(1, 2))             # (B,2N) keys [H1(0:N)‖H2(N:2N)]
            td_key = aw_td.mean(dim=(1, 2))               # (B,N)
            N = model.n_tokens
            sal_h1 = sal_key[:, :N]; sal_h2 = sal_key[:, N:]   # the two salience key blocks
            if capture_attn:
                seq["sal_quad"].append(torch.stack([sal_h2[:, qidx_t[q]].sum(1) for q in range(4)], 1).cpu().numpy())
                seq["td_quad"].append(torch.stack([td_key[:, qidx_t[q]].sum(1) for q in range(4)], 1).cpu().numpy())
            if capture_map:
                seq["sal_map_h1"].append(sal_h1.cpu().numpy())
                seq["sal_map_h2"].append(sal_h2.cpu().numpy())
                seq["td_map"].append(td_key.cpu().numpy())
        else:
            states, rec = dual_stream_step(model.encoder, tokens, states, attn_bias=attn_bias)
        if probe is not None:
            H1n, H2n = states[0][0], states[0][1]
            for i in range(B):
                if t == probe_t[i]:
                    for name, src in (("zsal", rec[0]), ("ztd", rec[1]), ("h1", H1n), ("h2", H2n)):
                        probe[name][i] = torch.stack([src[i, qidx_t[q]].mean(0) for q in range(4)], 0).cpu().numpy()
        if capture_quadlat:
            H1n, H2n = states[0][0], states[0][1]
            for key, src in (("ql_zsal", rec[0]), ("ql_ztd", rec[1]), ("ql_h1", H1n), ("ql_h2", H2n)):
                seq[key].append(torch.stack([src[:, qidx_t[q]].mean(1) for q in range(4)], 1).cpu().numpy())  # (B,4,d)
        logits = actor_decode(model.actor_head, rec)
        pi = torch.softmax(logits, dim=-1)
        seq["press_prob"].append(pi[:, 1].cpu().numpy())
        seq["actor_logits"].append(logits.cpu().numpy())
        if capture_value:
            qp = critic_decode(model.critic_head, rec, 1)
            qw = critic_decode(model.critic_head, rec, 0)
            q_dist = torch.stack([qw, qp], dim=1)
            v = (pi.detach().unsqueeze(-1) * q_dist).sum(1)
            seq["q_press"].append(qp.mean(-1).cpu().numpy()); seq["q_wait"].append(qw.mean(-1).cpu().numpy())
            seq["v_scalar"].append(v.mean(-1).cpu().numpy()); seq["qstd_press"].append(qp.std(-1).cpu().numpy())
        actions = (logits.argmax(-1).cpu().numpy().astype(np.int64) if policy == "argmax"
                   else np.zeros(B, dtype=np.int64))
        for i in range(B):
            if done[i]:
                continue
            a = int(actions[i]); o, r, d, _ = envs[i].step(a); obs[i] = o
            if a == 1 and press_index[i] < 0:
                press_index[i] = t
            reward[i] = float(r)
            if d:
                done[i] = True
        t += 1

    out = {k: np.stack(v, axis=0) for k, v in seq.items()}
    F_ = lambda name, default=-1: np.array([int(getattr(e, name, default)) for e in envs], dtype=np.int64)
    Ff = lambda name: np.array([float(getattr(e, name, np.nan)) for e in envs], dtype=np.float32)
    change_time = F_("change_time"); change_true = F_("change_true")
    distractor_true = F_("distractor_true"); distractor_time = F_("distractor_time")
    pressed = press_index >= 0
    premature = pressed & (press_index < change_time)
    hit = pressed & (press_index >= change_time) & (change_true == 1)
    out.update({
        "press_index": press_index, "pressed": pressed, "premature": premature, "hit": hit,
        "rt": np.where(hit, press_index - change_time, np.nan).astype(np.float32), "reward": reward,
        "change_time": change_time, "change_true": change_true, "change_index": F_("change_index"),
        "distractor_true": distractor_true, "distractor_time": distractor_time,
        "distractor_index": F_("distractor_index"), "distractor_change": Ff("distractor_change"),
        "cue_position": np.array([e.cue_position for e in envs], dtype=object),
        "cue_color": np.array([e.cue_color for e in envs], dtype=object),
        "proportion": Ff("proportion"), "orientation_change": Ff("orientation_change"),
        "n_steps": t,
    })
    if probe is not None:
        for k, v in probe.items():
            out[f"probe_{k}"] = v
    return out


_PER_TRIAL = {"press_index", "pressed", "premature", "hit", "rt", "reward", "change_time", "change_true",
              "change_index", "distractor_true", "distractor_time", "distractor_index", "distractor_change",
              "cue_position", "cue_color", "proportion", "orientation_change",
              "probe_zsal", "probe_ztd", "probe_h1", "probe_h2"}


def record_rollout_chunked(model, n_envs, device, *, chunk=256, seed=0, distractor_prob=0.5, **kw):
    kw["run_full"] = True
    rng = np.random.RandomState(seed)
    parts = []
    for s in range(0, n_envs, chunk):
        b = min(chunk, n_envs - s)
        envs = [ChangeDetectionEnv(distractor_prob=distractor_prob) for _ in range(b)]
        for j, e in enumerate(envs):
            np.random.seed(int(rng.randint(0, 2**31 - 1)))
            e.reset()
        obs0 = [e._next_observation() for e in envs]
        parts.append(record_rollout(model, envs, obs0, device, **kw))
    out = {}
    for k in parts[0]:
        if k == "n_steps":
            out[k] = max(int(p[k]) for p in parts)
        elif k in _PER_TRIAL:
            out[k] = np.concatenate([p[k] for p in parts], axis=0)
        else:
            out[k] = np.concatenate([p[k] for p in parts], axis=1)
    return out


def selfcheck():
    device = torch.device("cpu")
    model = build_model(load_config(), device)
    B = 3; states = model.init_states(B, device=device)
    x = torch.randn(B, 3, 50, 50); tokens = model.patch_embed(x)
    (Hs0, Cs0), rec0 = model.encoder.forward_step(tokens, states)
    (Hs1, Cs1), rec1 = dual_stream_step(model.encoder, tokens, states)
    d_rec = max(float((a - b).abs().max()) for a, b in zip(rec0, rec1))
    al0, q0, _, _ = model._run_heads(rec0)
    d_act = float((al0 - actor_decode(model.actor_head, rec0)).abs().max())
    d_cri = float((q0[:, 1] - critic_decode(model.critic_head, rec0, 1)).abs().max())
    print(f"[selfcheck] rec max|Δ|={d_rec:.2e}  actor Δ={d_act:.2e}  critic Δ={d_cri:.2e}")
    assert d_rec < 1e-4 and d_act < 1e-4 and d_cri < 1e-4, "manual replica mismatch!"
    print("[selfcheck] OK — faithful dual-stream step + split decoders (v11_part5)")


if __name__ == "__main__":
    selfcheck()
