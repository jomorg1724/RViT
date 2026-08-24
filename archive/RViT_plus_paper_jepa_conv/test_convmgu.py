"""Verification for the ConvMGU 'visual-cortex' recurrence in the conv front-end. CPU, no training."""
import math, torch
from conv_frontend import ConvPatchFrontEnd, ConvMGU
from model import RViTPaperModel

torch.manual_seed(0)
B, T = 2, 7
ok = []
def check(name, cond, extra=""):
    ok.append(cond); print(f"[{'PASS' if cond else 'FAIL'}] {name} {extra}")

# 1. STATELESS back-compat: conv_recurrent=False → front(x,t) returns X:(B,4,140), subscriptable.
f0 = ConvPatchFrontEnd(in_channels=3, conv_recurrent=False).eval()
x = torch.randn(B, 3, 50, 50)
with torch.no_grad(): X0 = f0(x, 3)
check("stateless front returns X (B,4,140) tensor", isinstance(X0, torch.Tensor) and tuple(X0.shape) == (B, 4, 140))

# 2. RECURRENT shapes: stage1 → (X:(B,4,140), h:(B*4,64,13,13)); stage2 → (B*4,128,7,7).
f1 = ConvPatchFrontEnd(in_channels=3, conv_recurrent=True, conv_rec_stage=1).eval()
with torch.no_grad(): X1, h1 = f1(x, 0, None)
check("recurrent stage1 X shape", tuple(X1.shape) == (B, 4, 140))
check("recurrent stage1 state shape", tuple(h1.shape) == (B*4, 64, 13, 13), str(tuple(h1.shape)))
f2 = ConvPatchFrontEnd(in_channels=3, conv_recurrent=True, conv_rec_stage=2).eval()
with torch.no_grad(): _, h2 = f2(x, 0, None)
check("recurrent stage2 state shape", tuple(h2.shape) == (B*4, 128, 7, 7), str(tuple(h2.shape)))

# 3. MEASURED RETENTION at init ≈ target (the biased decay). f = σ(W_f x + U_f h); weights zero-init,
#    W_f.bias = logit(retain) → with any x,h, f ≡ σ(bias) = retain at init.
for r in (0.2, 0.3, 0.5):
    m = ConvMGU(64, retain=r)
    xx, hh = torch.randn(1, 64, 13, 13), torch.randn(1, 64, 13, 13)
    f = torch.sigmoid(m.W_f(xx) + m.U_f(hh))
    check(f"retention f≈{r} at init (data-independent)", abs(float(f.mean()) - r) < 1e-4 and float(f.std()) < 1e-5,
          f"mean={float(f.mean()):.4f} std={float(f.std()):.2e}")
    check(f"  bias == logit({r})", abs(float(m.W_f.bias[0]) - math.log(r/(1-r))) < 1e-5)
# bounded state: |cand|≤1 (tanh) ⇒ with h_prev in [-1,1], |h_new|≤1
m = ConvMGU(64, retain=0.3); h = torch.zeros(1, 64, 13, 13)
for _ in range(20): h = m(torch.randn(1, 64, 13, 13), h)
check("state stays bounded over 20 steps (|h|≤1.01)", float(h.abs().max()) <= 1.01, f"max={float(h.abs().max()):.3f}")

# 4. STATE zero at t=0 / carried t>0 (via forward_rl_sequence internal reset) + reset per episode.
def mk(**kw):
    return RViTPaperModel(n_actions=2, n_quantiles=5, seq_len=T, feedback="affine_ew", d_mem=128,
                          conv_frontend=True, conv_recurrent=True, conv_rec_stage=1, **kw).eval()
mdl = mk()
vid = torch.randn(B, T, 50, 50, 3)
with torch.no_grad():
    o_a = mdl.forward_rl_sequence(vid); o_b = mdl.forward_rl_sequence(vid)
check("forward_rl_sequence deterministic (per-episode reset, no leakage)",
      torch.allclose(o_a["V_scalar_seq"], o_b["V_scalar_seq"], atol=1e-5))
check("forward_rl_sequence output shape", tuple(o_a["actor_logits_seq"].shape) == (B, T, 2))

# 5. DIFFERENTIABILITY through the sequence path (BPTT into ConvMGU + reduce).
mdl_g = mk()
out = mdl_g.forward_rl_sequence(vid)
loss = out["V_scalar_seq"].sum() + out["actor_logits_seq"].pow(2).mean()
loss.backward()
g_mgu = [p.grad for p in mdl_g.front.conv_mgu.parameters() if p.requires_grad]
g_red = [p.grad for p in mdl_g.front.conv_reduce.parameters() if p.requires_grad]
check("ConvMGU grads exist + finite", len(g_mgu) > 0 and all(g is not None and torch.isfinite(g).all() for g in g_mgu))
check("conv_reduce grads exist + finite", all(g is not None and torch.isfinite(g).all() for g in g_red))
# gate weights are zero-init but should receive gradient (so the cell can learn a longer τ)
check("gate W_f.weight receives gradient (learnable τ)", mdl_g.front.conv_mgu.W_f.weight.grad.abs().sum() > 0)

# 6. ONLINE rl_step threads the 3-tuple state across an episode.
st = mdl.init_states(1)
check("init_states is 3-tuple (enc,t,conv=None)", len(st) == 3 and st[2] is None)
with torch.no_grad():
    for t in range(T):
        step = mdl.rl_step(torch.randn(1, 50, 50, 3), st); st = step["new_states"]
check("rl_step carries 3-tuple, conv_state non-None after step", len(st) == 3 and st[2] is not None)
check("online conv_state shape (1*4,64,13,13)", tuple(st[2].shape) == (4, 64, 13, 13))

# 7. PARAM delta > 0 vs non-recurrent.
base = RViTPaperModel(feedback="affine_ew", d_mem=128, conv_frontend=True, seq_len=T).eval()
n_base = sum(p.numel() for p in base.parameters()); n_rec = sum(p.numel() for p in mdl.parameters())
check("param count increased with recurrence", n_rec > n_base, f"+{n_rec-n_base:,}")

# 8. JEPA still builds + runs.
mj = mk(jepa_n_heads=4, jepa_proto_dim=256)
oj = mj.forward_rl_sequence(vid, return_cell=True)
check("JEPA cell_seq present", "cell_seq" in oj and tuple(oj["cell_seq"].shape)[:2] == (B, T))
check("jepa_logits runs", tuple(mj.jepa_logits(oj["cell_seq"]).shape)[:2] == (B, T))

# 9. two_lstm still builds + runs.
mt = mk(two_lstm=True, jepa_n_heads=4)
with torch.no_grad(): ot = mt.forward_rl_sequence(vid, return_cell=True)
check("two_lstm + conv_recurrent runs", tuple(ot["actor_logits_seq"].shape) == (B, T, 2))
check("two_lstm init_states 3-tuple", len(mt.init_states(1)) == 3)

# 10. CONFIG guard: conv_recurrent without conv_frontend raises.
try:
    RViTPaperModel(conv_recurrent=True, conv_frontend=False); check("guard raises", False)
except ValueError:
    check("guard: conv_recurrent requires conv_frontend raises ValueError", True)

print(f"\n==== {sum(ok)}/{len(ok)} checks passed ====")
