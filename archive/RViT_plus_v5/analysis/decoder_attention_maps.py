"""
DECODER (actor & critic head) attention maps for RViT+ v5.

Companion to ``avg_attention_maps.py`` (which maps the ENCODER's memtok
attention). Here we map the attention INSIDE the actor and critic decoders —
the hypothesis being that the decision heads attend much more sharply than the
encoder does.

Each decoder is a 2-layer post-norm ``nn.TransformerEncoder`` over the token
sequence ``[CLS ++ H₁ ++ H₂]`` (1 + 2·N tokens). The CLS row (query 0) is the
decision readout: ``out[:, 0]`` → the MLP head → logits / Q. So the quantity of
interest is **the CLS token's attention over the memory keys**. Because each
memory row corresponds to a patch position (N = grid_h·grid_w), the CLS→memory
attention reshapes to a (grid_h, grid_w) spatial "decision attention" map.

We do NOT touch decoder.py — to read per-head weights we replicate each
``nn.TransformerEncoderLayer``'s forward (post-norm, GELU) and pull the
per-head ``(B, heads, S, S)`` attention from its ``self_attn`` with
``need_weights=True, average_attn_weights=False``. In eval() the dropouts are
no-ops, so this reproduces the decoder output exactly.

For each timestep we record, per decoder layer per head:
  * CLS→position saliency = attn(CLS→H₁_i) + attn(CLS→H₂_i), reshaped to the grid
  * CLS self-attention fraction (how much the readout attends to itself)
  * the position-attention perplexity (effective # patches the readout reads),
    directly comparable to the encoder's patch-attention perplexity.

The critic conditions on the action (its ``action_emb`` is added to the input
tokens and the decode is run once per action); we map the critic for a chosen
action (default press=1) so the map is "what the value-of-pressing reads".

Usage:
    .venv/bin/python RViT_plus_v5/analysis/decoder_attention_maps.py \
        --checkpoint <ckpt> --n-trials 96 --device cpu
"""
from __future__ import annotations

import argparse
import os
import sys
from typing import Dict, List, Tuple

import numpy as np
import torch

_HERE = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(os.path.dirname(_HERE))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from RViT_plus_v5.analysis import _behav_utils as bu
from RViT_plus_v5.analysis.avg_attention_maps import (
    CHANGE_LABEL, plot_head_alpha, plot_head_strip,
)


# ── per-layer forward that also returns per-head attention ───────────────────


def _tx_layer_with_attn(layer: torch.nn.Module, x: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
    """Faithful replica of a post-norm nn.TransformerEncoderLayer forward that
    also returns the (B, heads, S, S) self-attention weights. In eval() the
    dropouts are identities, so the returned x matches the layer's own output."""
    attn_out, attn_w = layer.self_attn(
        x, x, x, need_weights=True, average_attn_weights=False,
    )
    x = layer.norm1(x + layer.dropout1(attn_out))
    ff = layer.linear2(layer.dropout(layer.activation(layer.linear1(x))))
    x = layer.norm2(x + layer.dropout2(ff))
    return x, attn_w


def _run_decoder_with_attn(decoder, seq: torch.Tensor) -> List[torch.Tensor]:
    """Run a decoder's TransformerEncoder stack on the prepared token sequence,
    returning the per-layer attention weights [(B, heads, S, S), …]."""
    x = seq
    attns: List[torch.Tensor] = []
    for layer in decoder.tx.layers:
        x, aw = _tx_layer_with_attn(layer, x)
        attns.append(aw)
    return attns


def _actor_seq(actor, rec_states: List[torch.Tensor]) -> torch.Tensor:
    """Reproduce ActorDecoder.encode's token sequence: [CLS ++ (H₁,H₂)+pos]."""
    M = torch.cat(rec_states, dim=1) + actor.pos_emb
    B = M.shape[0]
    return torch.cat([actor.cls.expand(B, -1, -1), M], dim=1)


def _critic_seq(critic, rec_states: List[torch.Tensor], action: int) -> torch.Tensor:
    """Reproduce CriticDecoder.forward's per-action token sequence for ONE action:
    base pos-emb + that action's tiled action_emb, CLS prepended."""
    M = torch.cat(rec_states, dim=1) + critic.pos_emb
    a_enc = critic.action_emb.repeat(1, critic.n_states, 1)      # (A, n_input, d)
    Ma = M + a_enc[action].unsqueeze(0)                          # add action's code
    B = M.shape[0]
    return torch.cat([critic.cls.expand(B, -1, -1), Ma], dim=1)


# ── reductions ───────────────────────────────────────────────────────────────


def _cls_to_grid(attn: torch.Tensor, N: int, gh: int, gw: int):
    """attn: (B, heads, S, S), S = 1 + 2N. Take the CLS query row, sum the two
    memory blocks per patch position, reshape to the grid.

    Returns
    -------
    grid      : (heads, gh, gw)  mean-over-batch CLS→position saliency
    self_frac : (heads,)         mean CLS→CLS self-attention fraction
    perp      : (heads,)         effective #positions read (perplexity / N),
                                 from the position distribution renormalised over N
    """
    cls = attn[:, :, 0, :]                       # (B, heads, S)
    self_frac = cls[:, :, 0]                      # (B, heads)
    mem = cls[:, :, 1:]                           # (B, heads, 2N)
    pos = mem[:, :, :N] + mem[:, :, N:2 * N]      # (B, heads, N)  sum over H₁,H₂
    grid = pos.view(pos.shape[0], pos.shape[1], gh, gw).mean(dim=0)        # (heads,gh,gw)
    p = pos / pos.sum(dim=-1, keepdim=True).clamp_min(1e-12)
    perp = (-(p.clamp_min(1e-12) * p.clamp_min(1e-12).log()).sum(-1)).exp()  # (B,heads)
    return (grid.detach().cpu().numpy(),
            self_frac.mean(0).detach().cpu().numpy(),
            perp.mean(0).detach().cpu().numpy())


@torch.no_grad()
def decoder_attention_rollout(model, envs, obs0, device, *, critic_action: int):
    """Forced-wait rollout; collect per-layer CLS→position maps for the actor and
    the critic (at `critic_action`). Returns dicts keyed 'actor'/'critic' →
    list-over-layers of (T, heads, gh, gw), plus concentration accumulators and
    an obs example."""
    B = len(envs)
    model.eval()
    states = model.init_states(B, device=device)
    gh, gw, N = model.patch_embed.grid_h, model.patch_embed.grid_w, model.n_tokens
    nL = model.actor_head.tx.num_layers
    obs = list(obs0)
    T = envs[0].T
    frames = {"actor": [[] for _ in range(nL)], "critic": [[] for _ in range(nL)]}
    conc = {"actor": {"self": [[] for _ in range(nL)], "perp": [[] for _ in range(nL)]},
            "critic": {"self": [[] for _ in range(nL)], "perp": [[] for _ in range(nL)]}}
    obs_example: List[np.ndarray] = []
    t = 0
    done = np.zeros(B, dtype=bool)
    while t <= T and not done.all():
        x = bu._obs_to_tensor(obs, device)
        obs_example.append(np.asarray(obs[0], dtype=np.float32).copy())
        tokens = model.patch_embed(x)
        states, rec = model.encoder.forward_step(tokens, states)
        a_att = _run_decoder_with_attn(model.actor_head, _actor_seq(model.actor_head, rec))
        c_att = _run_decoder_with_attn(
            model.critic_head, _critic_seq(model.critic_head, rec, critic_action))
        for L in range(nL):
            for key, att in (("actor", a_att), ("critic", c_att)):
                grid, sf, perp = _cls_to_grid(att[L], N, gh, gw)
                frames[key][L].append(grid)
                conc[key]["self"][L].append(sf)
                conc[key]["perp"][L].append(perp)
        for i in range(B):
            if done[i]:
                continue
            o, r, d, _ = envs[i].step(0)
            obs[i] = o
            if d:
                done[i] = True
        t += 1
    maps = {k: [np.stack(fr, axis=0) for fr in frames[k]] for k in frames}    # (T,heads,gh,gw)
    return maps, conc, np.stack(obs_example, axis=0)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--checkpoint", default="RViT_plus_v5/checkpoints/rvit_plus_rl_latest.pt")
    ap.add_argument("--config", default=None)
    ap.add_argument("--out-dir", default="RViT_plus_v5/analysis/figures_decoder")
    ap.add_argument("--device", default="")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--n-trials", type=int, default=96)
    ap.add_argument("--change-time", type=int, default=15)
    ap.add_argument("--change-index", type=int, default=0)
    ap.add_argument("--change-mag", type=float, default=64.0)
    ap.add_argument("--critic-action", type=int, default=1, help="action whose critic pass to map (1=press)")
    ap.add_argument("--conditions", nargs="+", default=["left:1.0", "right:1.0"],
                    help="cue conditions as 'side:ring'")
    args = ap.parse_args(argv)

    os.makedirs(args.out_dir, exist_ok=True)
    device = bu.select_device(args.device)
    cfg = bu.load_config(args.config)
    model = bu.build_model(cfg, device)
    it = bu.load_checkpoint(model, args.checkpoint, device)
    env_kwargs = dict(min_change_time=int(cfg["environment"]["min_change_time"]),
                      max_change_time=int(cfg["environment"]["max_change_time"]))
    nL = model.actor_head.tx.num_layers
    print(f"[loaded] {args.checkpoint} (iter={it})  device={device}  decoder_layers={nL}")
    print(f"[fixed change] quadrant={CHANGE_LABEL[args.change_index]}  t={args.change_time}  "
          f"|Δθ|={args.change_mag}  critic_action={args.critic_action}")

    suffix = f"chg{args.change_index}_t{args.change_time}"
    for cond in args.conditions:
        side, ring = cond.split(":"); ring = float(ring)
        rng = np.random.default_rng(args.seed + (0 if side == "left" else 1000) + int(ring * 100))
        spec = bu.ForcedTrialSpec(
            cue_position=side, proportion=ring, change_true=1, change_time=args.change_time,
            change_index_mode=int(args.change_index), orientation_mag=float(args.change_mag),
        )
        envs, obs0 = bu.build_env_batch(spec, args.n_trials, rng, env_kwargs=env_kwargs,
                                        randomize_cue_position=False, randomize_color=True)
        valid_tag = "VALID" if bu.CUED_QUADRANT[side] == args.change_index else "INVALID"
        label = f"cue {side} · ring {ring} ({valid_tag})"
        maps, conc, obs_ex = decoder_attention_rollout(
            model, envs, obs0, device, critic_action=args.critic_action)
        safe = label.replace(" ", "").replace("·", "_").replace("(", "").replace(")", "")

        for key in ("actor", "critic"):
            ka = f"{key}(a={args.critic_action})" if key == "critic" else key
            for L in range(nL):
                strip = maps[key][L]                          # (T, heads, gh, gw)
                self_m = np.stack(conc[key]["self"][L], 0).mean(0)   # (heads,)
                perp_m = np.stack(conc[key]["perp"][L], 0).mean(0)   # (heads,)
                rng_txt = "  ".join(f"h{h}:perp={perp_m[h]:.1f},self={self_m[h]:.2f}"
                                    for h in range(len(perp_m)))
                print(f"  [{label}] {ka} L{L+1}: peak={strip.max():.3f}  {rng_txt}")
                plot_head_strip(
                    strip, obs_ex,
                    os.path.join(args.out_dir, f"dec_{key}_L{L+1}_{safe}_{suffix}.png"),
                    title=f"{ka} decoder · layer {L+1} · CLS→memory attention · {label} · n={args.n_trials}",
                    change_frame=args.change_time,
                )
                plot_head_alpha(
                    strip,
                    os.path.join(args.out_dir, f"dec_{key}_alpha_L{L+1}_{safe}_{suffix}.png"),
                    layer_idx=L, change_frame=args.change_time, change_index=args.change_index,
                    cond_label=f"{ka} · {label}",
                )
    print("[done]")
    return 0


if __name__ == "__main__":
    sys.exit(main())
