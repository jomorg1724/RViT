"""
RViT+ "jump-softmax" model — a FiLM-affine feedback transformer + a SOFTMAX-BOUNDED memory
transformer (the memory state is a per-patch distribution on the simplex). This variant replaces
the handcrafted leaky-OU + LayerScale + LayerNorm boundedness of the jump model with a single
per-patch softmax: H ← softmax_features(log(H_prev) + attn_write + FFN). n_mem defaults to 1 (a
clean A/B against the single-memory jump baseline); set n_mem>1 to stack the softmax memories
hierarchically. Designed around a manifold/jump-diffusion view of working memory.

Conceptual frame (cf. BehavioralSegmentation/paper2: latent state on a low-D manifold with
drift + anisotropic diffusion + a state-conditioned JUMP process):
  • Each memory H_k is a *point on a mnemonic manifold* — visual working memory, per patch (+CLS).
  • The recurrent update is NON-GATED and additive: each memory is itself a transformer that
    self-attends over [input ‖ H_k] and writes H_k on a leaky-OU RESIDUAL (additive drift =
    gradient highway over time; a frame whose attention locks onto a changed token is a large
    write = a *jump*). LayerScale keeps writes small and the OU leak bounds the state. No
    sigmoid/elu/exp gating anywhere — ReLU/GELU maps realise the sharp basin-to-basin jumps that
    exponential gates smear out.
  • THREE memories are stacked as a depth hierarchy of timescales: the percept Z feeds mem1→H1;
    H1 feeds mem2→H2; H2 feeds mem3→H3. H1 tracks the percept fast, H3 integrates the slowest,
    most abstract context. Each keeps its own recurrent state.
  • The transformer is FiLM-affine: each token's percept is modulated by the TOP memory,
    X' = (1+γ(H3))⊙X + β(H3) — a BROADCAST (element-wise) scale + additive shift, projected per
    patch from H3 by W∈(d_mem,d_model), zero-init ⇒ identity start. Top-down feedback: the most
    abstract memory reshapes perception; attention then runs over the modulated tokens.
  • Both Z and H3 carry a CLS token (a global belief coordinate); [Z_cls ‖ H3_cls] (1536) is read
    by the actor and the critic, with Z_cls and H3_cls LayerNorm'd separately so the larger H3
    cannot swamp Z.

Task: the value+validity ChangeDetectionEnv (coloured cue = value red/green/blue, ring
completeness = validity). d_model=512, d_mem=1024, 4 patches (+CLS), n_mem=3.
"""
from __future__ import annotations
from typing import List, Optional, Tuple
import torch
import torch.nn as nn
import torch.nn.functional as F


# ── front-end: 4 patches → d_model (conv-free, VAE-free) + CLS ─────────────────
class PatchEmbedCLS(nn.Module):
    def __init__(self, in_ch=3, image_h=50, image_w=50, patch_size=25, d_model=512):
        super().__init__()
        assert image_h % patch_size == 0 and image_w % patch_size == 0
        self.patch_size = patch_size
        self.gh, self.gw = image_h // patch_size, image_w // patch_size
        self.n_patches = self.gh * self.gw                      # 4
        self.n_tokens = self.n_patches + 1                      # + CLS
        self.d_model = d_model
        pdim = in_ch * patch_size * patch_size
        # per-patch projection (shared, applied independently per patch — no cross-patch mix)
        self.proj = nn.Sequential(nn.Linear(pdim, d_model), nn.GELU(), nn.Linear(d_model, d_model))
        self.norm = nn.LayerNorm(d_model)
        self.cls = nn.Parameter(torch.zeros(1, 1, d_model)); nn.init.normal_(self.cls, std=0.02)
        self.pos = nn.Parameter(torch.zeros(1, self.n_tokens, d_model)); nn.init.normal_(self.pos, std=0.02)

    def forward(self, x):                                       # x: (B,3,50,50) or (B,50,50,3)
        if x.dim() == 4 and x.shape[-1] == 3 and x.shape[1] != 3:
            x = x.permute(0, 3, 1, 2)
        B, C, H, W = x.shape; p, gh, gw = self.patch_size, self.gh, self.gw
        x = x.reshape(B, C, gh, p, gw, p).permute(0, 2, 4, 1, 3, 5).contiguous()
        patches = x.reshape(B, gh * gw, C * p * p)              # (B,4,pdim) row-major [TL,TR,BL,BR]
        tok = self.proj(patches)                               # (B,4,d_model)
        cls = self.cls.expand(B, -1, -1)                       # (B,1,d_model)
        X = torch.cat([cls, tok], dim=1)                       # (B,5,d_model)  [CLS,p0..p3]
        return self.norm(X) + self.pos


# ── memory update bounded by a PER-PATCH SOFTMAX (no leaky-OU / LayerScale / LayerNorm) ──
class MemoryTransformer(nn.Module):
    """The working memory is itself a transformer, but its state is kept bounded by a SOFTMAX over
    each patch's feature vector — replacing the handcrafted leaky-OU + LayerScale + LayerNorm
    boundedness. Each patch's memory H_k is a probability distribution over the d_mem features (a
    per-patch categorical belief on the simplex). We self-attend over [Z ‖ H], add the attention
    write to the prior belief IN LOGIT SPACE, and renormalise:

        H ← softmax_features( log(H_prev) + Attn([Z‖H])[H part] + FFN )      (per patch)

    The softmax is the ONLY normalisation / boundedness: the state never leaves the simplex, so it
    cannot explode and no decay / LayerScale / LayerNorm is needed on the carry. log(H_prev) is the
    integration path — it recovers the accumulated logits so evidence still accumulates over time;
    a plain `H_prev + write` would be swamped (simplex values are ~1/d_mem) and the memory would be
    effectively memoryless. A frame whose attention locks onto a changed Z is a large logit write =
    a sharp move of the distribution (a jump). No gates."""
    def __init__(self, in_dim=512, d_mem=1024, n_heads=8, n_tokens=5, drop=0.1):
        super().__init__()
        self.z_proj = nn.Linear(in_dim, d_mem)                           # lift input (percept Z, or memory below) → d_mem
        self.type_emb = nn.Parameter(torch.zeros(2, 1, d_mem))           # [percept-type, memory-type]
        self.pos_emb = nn.Parameter(torch.zeros(1, n_tokens, d_mem))     # shared patch position (Z & H1)
        nn.init.normal_(self.type_emb, std=0.02); nn.init.normal_(self.pos_emb, std=0.02)
        self.attn = nn.MultiheadAttention(d_mem, n_heads, dropout=drop, batch_first=True)
        self.ffn = nn.Sequential(nn.Linear(d_mem, 4 * d_mem), nn.GELU(),
                                 nn.Dropout(drop), nn.Linear(4 * d_mem, d_mem))
        self.drop = nn.Dropout(drop)
        # NO leaky-OU / LayerScale / LayerNorm on the carry — the per-patch softmax in forward()
        # is the only normalisation and the only thing keeping the state bounded (on the simplex).

    def forward(self, inp, H_prev, return_attn=False):
        B, N, _ = H_prev.shape
        z = self.z_proj(inp) + self.type_emb[0] + self.pos_emb         # input tokens  (B,N,d_mem)
        h = H_prev + self.type_emb[1] + self.pos_emb                   # memory tokens — H_prev is a per-patch distribution
        seq = torch.cat([z, h], dim=1)                                  # (B,2N,d_mem); NO pre-LN
        out, aw = self.attn(seq, seq, seq, need_weights=return_attn, average_attn_weights=True)
        delta = self.drop(out[:, N:])                                   # attention write onto the memory tokens
        delta = delta + self.ffn(delta)                                # FFN sublayer (on the O(1) write, no norm)
        # integrate in LOGIT space (log H_prev recovers the accumulated logits), then renormalise
        # with a per-patch SOFTMAX = the sole boundedness. Zero-init H_prev → uniform log-prior.
        H = torch.softmax(torch.log(H_prev.clamp_min(1e-9)) + delta, dim=-1)
        return (H, aw) if return_attn else (H, None)


# ── single FiLM-affine feedback transformer ───────────────────────────────────
class FiLMAffineBlock(nn.Module):
    def __init__(self, d_model=512, d_mem=1024, n_heads=8, drop=0.1):
        super().__init__()
        self.d_model = d_model
        # FiLM params projected per-token from H1 (W ∈ (d_mem,d_model)); zero-init ⇒ identity start
        self.norm_h = nn.LayerNorm(d_mem)                                 # bound the (accumulating) FiLM input
        self.W_gamma = nn.Linear(d_mem, d_model)
        self.W_beta = nn.Linear(d_mem, d_model)
        nn.init.zeros_(self.W_gamma.weight); nn.init.zeros_(self.W_gamma.bias)
        nn.init.zeros_(self.W_beta.weight); nn.init.zeros_(self.W_beta.bias)
        self.attn = nn.MultiheadAttention(d_model, n_heads, dropout=drop, batch_first=True)
        self.norm_ff = nn.LayerNorm(d_model)
        self.ffn = nn.Sequential(nn.Linear(d_model, 4 * d_model), nn.GELU(),
                                 nn.Dropout(drop), nn.Linear(4 * d_model, d_model))
        self.drop = nn.Dropout(drop)

    def forward(self, X, H1_prev, return_attn=False):
        Hn = self.norm_h(H1_prev)
        gamma = self.W_gamma(Hn); beta = self.W_beta(Hn)                  # (B,N,d_model) each
        Xp = (1.0 + gamma) * X + beta                                     # broadcast scale + shift
        a, aw = self.attn(Xp, Xp, Xp, need_weights=return_attn,
                          average_attn_weights=True)
        Z = X + self.drop(a)                                              # residual on X
        Z = Z + self.ffn(self.norm_ff(Z))
        return (Z, aw) if return_attn else (Z, None)


# ── encoder: FiLM transformer → Z → 3 HIERARCHICAL memory transformers → H1→H2→H3
#    rec = [Z_cls ‖ H_top_cls] ; FiLM perception feedback comes from the TOP memory
class JumpEncoder(nn.Module):
    def __init__(self, d_model=512, d_mem=1024, n_heads=8, n_tokens=5, drop=0.1, n_mem=3):
        super().__init__()
        self.d_model, self.d_mem, self.n_mem = d_model, d_mem, n_mem
        self.block = FiLMAffineBlock(d_model, d_mem, n_heads, drop)       # perception transformer (FiLM ← top memory)
        # HIERARCHICAL stack of memory transformers, each with its OWN recurrent state H_k.
        # mem1 reads the percept Z (d_model); every higher memory reads the memory below it (d_mem),
        # self-attends over [input ‖ H_k] and writes H_k on the leaky-OU residual. A depth hierarchy
        # of timescales: H1 tracks the percept fast, H3 integrates the slowest abstract context.
        mems = [MemoryTransformer(d_model, d_mem, n_heads, n_tokens, drop)]
        mems += [MemoryTransformer(d_mem, d_mem, n_heads, n_tokens, drop) for _ in range(n_mem - 1)]
        self.mems = nn.ModuleList(mems)
        self.rec_dim = d_model + d_mem                                    # [Z_cls ‖ H_top_cls] = 1536

    def init_states(self, B, n_tokens, device=None, dtype=torch.float32):
        return torch.zeros(B, self.n_mem, n_tokens, self.d_mem, device=device, dtype=dtype)  # [H1..Hn]

    def forward_step(self, X, states_prev, return_attn=False):
        Hs = list(states_prev.unbind(1))                                 # [H1,H2,H3] each (B,N,d_mem)
        Z, aw = self.block(X, Hs[-1], return_attn=return_attn)           # FiLM feedback from the TOP memory H_top
        inp, new = Z, []
        for k, mem in enumerate(self.mems):
            Hk, _ = mem(inp, Hs[k])                                       # self-attn over [input ‖ H_k], residual on H_k
            new.append(Hk); inp = Hk                                      # the updated memory feeds the next one up
        rec = torch.cat([Z[:, 0], new[-1][:, 0]], dim=-1)                # [Z_cls ‖ H_top_cls]
        return torch.stack(new, dim=1), rec, aw                          # state = stacked [H1,H2,H3]


# ── actor / critic heads on the CLS readout ───────────────────────────────────
class MLPActor(nn.Module):
    def __init__(self, in_dim, n_actions=2, hidden=256, init_action_bias=None):
        super().__init__()
        self.net = nn.Sequential(nn.Linear(in_dim, hidden), nn.GELU(), nn.Linear(hidden, hidden), nn.GELU())
        self.out = nn.Linear(hidden, n_actions)
        if init_action_bias is not None:
            with torch.no_grad(): self.out.bias.copy_(torch.tensor(init_action_bias, dtype=torch.float32))

    def forward(self, rec): return self.out(self.net(rec))


class QRCriticMLP(nn.Module):
    def __init__(self, in_dim, n_actions=2, n_quantiles=51, hidden=256):
        super().__init__()
        self.n_actions, self.n_quantiles = n_actions, n_quantiles
        self.net = nn.Sequential(nn.Linear(in_dim, hidden), nn.GELU(), nn.Linear(hidden, hidden), nn.GELU())
        self.out = nn.Linear(hidden, n_actions * n_quantiles)
        taus = (torch.arange(n_quantiles, dtype=torch.float32) + 0.5) / n_quantiles
        self.register_buffer("taus", taus)                              # QR-DQN quantile midpoints

    def forward(self, rec):
        q = self.out(self.net(rec))
        return q.view(-1, self.n_actions, self.n_quantiles)              # (B,A,Nq)

    def derive_V(self, q_dist, actor_logits):
        pi = torch.softmax(actor_logits, dim=-1).unsqueeze(-1)          # (B,A,1)
        V_dist = (pi * q_dist).sum(dim=1)                                # (B,Nq)
        return V_dist, V_dist.mean(dim=-1)                              # (B,Nq),(B,)


# ── full model (harness interface: init_states / rl_step / forward_rl_sequence) ─
State = torch.Tensor   # H1: (B, n_tokens, d_mem)


class RViTPlusJumpModel(nn.Module):
    def __init__(self, in_channels=3, image_h=50, image_w=50, patch_size=25,
                 d_model=512, d_mem=1024, tx_heads=8, n_actions=2, n_quantiles=51,
                 init_action_bias=None, seq_len=29, drop=0.1, n_mem=1, **_ignore):
        super().__init__()
        self.n_actions, self.n_quantiles, self.seq_len = int(n_actions), int(n_quantiles), int(seq_len)
        self.split_c3 = False; self.enc_layers = 1
        self.patch_embed = PatchEmbedCLS(in_channels, image_h, image_w, patch_size, d_model)
        self.n_tokens = self.patch_embed.n_tokens
        self.encoder = JumpEncoder(d_model, d_mem, tx_heads, n_tokens=self.n_tokens, drop=drop, n_mem=int(n_mem))
        self.d_model = d_model
        self.z_norm = nn.LayerNorm(d_model); self.h_norm = nn.LayerNorm(d_mem)  # norm SEPARATELY
        self.actor_head = MLPActor(self.encoder.rec_dim, n_actions, init_action_bias=init_action_bias)
        self.critic_head = QRCriticMLP(self.encoder.rec_dim, n_actions, n_quantiles)

    def init_states(self, batch_size, device=None, dtype=torch.float32) -> State:
        return self.encoder.init_states(batch_size, self.n_tokens, device=device, dtype=dtype)

    def _run_heads(self, rec):
        # norm Z_cls (512) and H1_cls (d_mem) SEPARATELY so the larger-magnitude H1 can't swamp Z
        rec = torch.cat([self.z_norm(rec[:, :self.d_model]), self.h_norm(rec[:, self.d_model:])], dim=-1)
        actor_logits = self.actor_head(rec)
        q_dist = self.critic_head(rec)
        V_dist, V_scalar = self.critic_head.derive_V(q_dist, actor_logits)
        return actor_logits, q_dist, V_dist, V_scalar

    def rl_step(self, x_t, prev_states, attn_biases=None, prev_c3_specialists=None, return_attn=False):
        X = self.patch_embed(x_t)
        states, rec, aw = self.encoder.forward_step(X, prev_states, return_attn=return_attn)
        actor_logits, q_dist, V_dist, V_scalar = self._run_heads(rec)
        out = {"new_states": states, "new_c3_specialists": {}, "actor_logits": actor_logits,
               "critic_q_dist": q_dist, "V_dist": V_dist, "V_scalar": V_scalar}
        if return_attn: out["attn"] = aw
        return out

    def forward_rl_sequence(self, x_video, return_decoder=False, attn_biases_per_frame=None):
        B, T = x_video.shape[:2]
        states = self.init_states(B, device=x_video.device, dtype=x_video.dtype)
        a_s, q_s, vd_s, vs_s, st_s = [], [], [], [], []
        for t in range(T):
            X = self.patch_embed(x_video[:, t].contiguous())
            states, rec, _ = self.encoder.forward_step(X, states)
            st_s.append(states)
            a, q, vd, vs = self._run_heads(rec)
            a_s.append(a); q_s.append(q); vd_s.append(vd); vs_s.append(vs)
        return {"actor_logits_seq": torch.stack(a_s, 1), "q_dist_seq": torch.stack(q_s, 1),
                "V_dist_seq": torch.stack(vd_s, 1), "V_scalar_seq": torch.stack(vs_s, 1),
                "states_seq": st_s, "final_states": states, "recons": []}
