"""
RViT+ "recur" — a SINGLE recurrent cross-attention transformer. No LSTM, no separate memory
module, nothing else. The recurrent state H *is* the transformer's residual stream:

  per frame, given the new percept X (4 patch tokens) and the carried state H:
    Q = W_Q(H)                      (the state queries)
    K = W_K([X ‖ H]) ,  V = W_V([X ‖ H])      (keys/values from BOTH percept and state)
    H ← H + W_O(softmax(QKᵀ/√d)·V)            (residual on H)
    H ← H + FFN(LN(H))                        (the usual transformer FFN sublayer)
    H_new = LN(H)                             (one extra OUTPUT LayerNorm — bounds the recurrence
                                               so the state can't explode across frames)
  H_new is BOTH the next frame's state and the readout fed to the actor and the critic.

No VAE, no conv: 4 raw 25×25 patches → per-patch MLP → d_model. Colour (value) + proportion
(validity) cues. d_model = d_mem = 512. Conceptually H is a point whose recurrence is a bounded
(LayerNorm'd) cross-attention map; the percept reshapes it each step (drift), and a frame where
H attends hard to a changed patch moves it sharply (a jump)."""
from __future__ import annotations
from typing import List, Optional
import torch
import torch.nn as nn


class PatchEmbed4(nn.Module):
    """4 patches → d_model, conv-free / VAE-free, + learned positional. No CLS (H queries)."""
    def __init__(self, in_ch=3, image_h=50, image_w=50, patch_size=25, d_model=512):
        super().__init__()
        self.patch_size = patch_size
        self.gh, self.gw = image_h // patch_size, image_w // patch_size
        self.n_tokens = self.gh * self.gw                      # 4
        self.d_model = d_model
        pdim = in_ch * patch_size * patch_size
        self.proj = nn.Sequential(nn.Linear(pdim, d_model), nn.GELU(), nn.Linear(d_model, d_model))
        self.norm = nn.LayerNorm(d_model)
        self.pos = nn.Parameter(torch.zeros(1, self.n_tokens, d_model)); nn.init.normal_(self.pos, std=0.02)

    def forward(self, x):
        if x.dim() == 4 and x.shape[-1] == 3 and x.shape[1] != 3:
            x = x.permute(0, 3, 1, 2)
        B, C, H, W = x.shape; p, gh, gw = self.patch_size, self.gh, self.gw
        x = x.reshape(B, C, gh, p, gw, p).permute(0, 2, 4, 1, 3, 5).contiguous()
        patches = x.reshape(B, gh * gw, C * p * p)             # (B,4,pdim) row-major [TL,TR,BL,BR]
        return self.norm(self.proj(patches)) + self.pos        # (B,4,d_model)


class RecurCrossAttn(nn.Module):
    """One recurrent cross-attention block. Q from H; K,V from [X‖H]; residual H; FFN; output LN."""
    def __init__(self, d_model=512, n_heads=8, n_tokens=4, drop=0.1):
        super().__init__()
        self.h = n_heads; self.dh = d_model // n_heads; self.d = d_model
        self.norm_h = nn.LayerNorm(d_model)                    # pre-LN on the state
        self.W_Q = nn.Linear(d_model, d_model)
        self.W_K = nn.Linear(d_model, d_model)
        self.W_V = nn.Linear(d_model, d_model)
        self.W_O = nn.Linear(d_model, d_model)
        self.type_emb = nn.Parameter(torch.zeros(2, 1, d_model))   # [percept-type, state-type] on K/V
        self.pos = nn.Parameter(torch.zeros(1, n_tokens, d_model)) # shared patch position (X & H)
        nn.init.normal_(self.type_emb, std=0.02); nn.init.normal_(self.pos, std=0.02)
        self.norm_ff = nn.LayerNorm(d_model)
        self.ffn = nn.Sequential(nn.Linear(d_model, 4 * d_model), nn.GELU(),
                                 nn.Dropout(drop), nn.Linear(4 * d_model, d_model))
        # VARIATIONAL bottleneck (replaces the forced output LayerNorm): project H to a Gaussian
        # latent q(z|H)=N(μ,σ²) and SAMPLE z (reparameterised). z is H_new — fed to the heads AND
        # carried as the next state. A KL(q‖N(0,I)) penalty (small β, set in the trainer) keeps the
        # latent continuous and bounded instead of a hard norm. The sampling is the diffusion noise.
        self.norm_pre = nn.LayerNorm(d_model)                  # stabilise the encoder input
        self.W_mu = nn.Linear(d_model, d_model)
        self.W_logvar = nn.Linear(d_model, d_model)
        self.drop = nn.Dropout(drop)

    def _mha(self, q, k, v):
        B, Nq, _ = q.shape; Nk = k.shape[1]
        q = q.view(B, Nq, self.h, self.dh).transpose(1, 2)
        k = k.view(B, Nk, self.h, self.dh).transpose(1, 2)
        v = v.view(B, Nk, self.h, self.dh).transpose(1, 2)
        aw = torch.softmax(torch.matmul(q, k.transpose(-1, -2)) / (self.dh ** 0.5), dim=-1)  # (B,h,Nq,Nk)
        out = torch.matmul(aw, v).transpose(1, 2).reshape(B, Nq, self.d)
        return out, aw.mean(1)                                  # (B,Nq,d), (B,Nq,Nk) head-mean

    def forward(self, X, H_prev, return_attn=False):
        Hn = self.norm_h(H_prev) + self.pos                    # pre-LN state + position
        kv = torch.cat([X + self.type_emb[0] + self.pos,       # percept tokens
                        Hn + self.type_emb[1]], dim=1)         # state tokens   → [X‖H] keys/values
        out, aw = self._mha(self.W_Q(Hn), self.W_K(kv), self.W_V(kv))
        H = H_prev + self.drop(self.W_O(out))                  # RESIDUAL on H
        H = H + self.ffn(self.norm_ff(H))                      # FFN sublayer
        # variational bottleneck → sampled latent (the new state / readout)
        h = self.norm_pre(H)
        mu = self.W_mu(h); logvar = self.W_logvar(h).clamp(-8.0, 8.0)
        z = mu + torch.exp(0.5 * logvar) * torch.randn_like(mu)            # reparameterise
        kl = -0.5 * (1.0 + logvar - mu.pow(2) - logvar.exp()).sum(dim=(-2, -1))   # (B,) per sample
        return z, kl, (aw if return_attn else None)


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
        self.register_buffer("taus", (torch.arange(n_quantiles, dtype=torch.float32) + 0.5) / n_quantiles)

    def forward(self, rec):
        return self.out(self.net(rec)).view(-1, self.n_actions, self.n_quantiles)

    def derive_V(self, q_dist, actor_logits):
        pi = torch.softmax(actor_logits, dim=-1).unsqueeze(-1)
        V_dist = (pi * q_dist).sum(dim=1)
        return V_dist, V_dist.mean(dim=-1)


State = torch.Tensor   # H: (B, n_tokens, d_model)


class RViTPlusRecurModel(nn.Module):
    def __init__(self, in_channels=3, image_h=50, image_w=50, patch_size=25,
                 d_model=512, d_mem=512, tx_heads=8, n_actions=2, n_quantiles=51,
                 init_action_bias=None, seq_len=29, drop=0.1, **_ignore):
        super().__init__()
        assert d_model == d_mem, "recur variant uses d_model == d_mem (single state width)"
        self.n_actions, self.n_quantiles, self.seq_len = int(n_actions), int(n_quantiles), int(seq_len)
        self.split_c3 = False; self.enc_layers = 1; self.d_model = d_model
        self.patch_embed = PatchEmbed4(in_channels, image_h, image_w, patch_size, d_model)
        self.n_tokens = self.patch_embed.n_tokens
        self.block = RecurCrossAttn(d_model, tx_heads, self.n_tokens, drop)
        rec_dim = self.n_tokens * d_model                     # flatten H_new → heads
        self.actor_head = MLPActor(rec_dim, n_actions, init_action_bias=init_action_bias)
        self.critic_head = QRCriticMLP(rec_dim, n_actions, n_quantiles)

    def init_states(self, batch_size, device=None, dtype=torch.float32) -> State:
        return torch.zeros(batch_size, self.n_tokens, self.d_model, device=device, dtype=dtype)

    def _run_heads(self, H_new):
        rec = H_new.flatten(1)                                # (B, n_tokens*d_model)
        actor_logits = self.actor_head(rec)
        q_dist = self.critic_head(rec)
        V_dist, V_scalar = self.critic_head.derive_V(q_dist, actor_logits)
        return actor_logits, q_dist, V_dist, V_scalar

    def rl_step(self, x_t, prev_states, attn_biases=None, prev_c3_specialists=None, return_attn=False):
        X = self.patch_embed(x_t)
        H_new, _kl, aw = self.block(X, prev_states, return_attn=return_attn)
        actor_logits, q_dist, V_dist, V_scalar = self._run_heads(H_new)
        out = {"new_states": H_new, "new_c3_specialists": {}, "actor_logits": actor_logits,
               "critic_q_dist": q_dist, "V_dist": V_dist, "V_scalar": V_scalar}
        if return_attn: out["attn"] = aw
        return out

    def forward_rl_sequence(self, x_video, return_decoder=False, attn_biases_per_frame=None):
        B, T = x_video.shape[:2]
        H = self.init_states(B, device=x_video.device, dtype=x_video.dtype)
        a_s, q_s, vd_s, vs_s, st_s, kl_s = [], [], [], [], [], []
        for t in range(T):
            X = self.patch_embed(x_video[:, t].contiguous())
            H, kl, _ = self.block(X, H)
            st_s.append(H); kl_s.append(kl)
            a, q, vd, vs = self._run_heads(H)
            a_s.append(a); q_s.append(q); vd_s.append(vd); vs_s.append(vs)
        return {"actor_logits_seq": torch.stack(a_s, 1), "q_dist_seq": torch.stack(q_s, 1),
                "V_dist_seq": torch.stack(vd_s, 1), "V_scalar_seq": torch.stack(vs_s, 1),
                "kl_seq": torch.stack(kl_s, 1),                # (B, T) per-step KL for the β·KL loss
                "states_seq": st_s, "final_states": H, "recons": []}
