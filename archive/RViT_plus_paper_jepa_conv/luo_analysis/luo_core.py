"""Analysis harness for the trained LUO-MAUNSELL models (conv repo). Tests reproduction of Luo &
Maunsell (2015/2018): reward moves the two SDT quantities INDEPENDENTLY — the 'sensitivity' session
(higher AVERAGE reward at the cued location, pixels identical) should raise d' at the cued location;
the 'criterion' session (asymmetric hit:CR ratio) should shift the criterion c, not d'. Task: 2×2
change-detection, white cue at one cell, change at the cued cell or elsewhere; Discrete(2) wait/declare
within a response window. We measure HR (declare within window on a change) and FA (declare on
no-change) → d' = z(HR)-z(FA), c = -½(z(HR)+z(FA)). CPU/MPS, thread-capped."""
import os, sys, numpy as np, torch, torch.nn as nn
torch.set_num_threads(3)
_ROOT = "/Users/jonathanmorgan/AttentionManuscript/RViT_plus_paper_jepa_conv"
sys.path.insert(0, _ROOT)
from model import RViTPaperModel
from envs import make_env
from scipy.stats import norm

T = 7; CHG = 5; CUE = 0; UNCUED = 3         # 2×2 cells; cue at TL(0), uncued change at BR(3)
CK = "/Users/jonathanmorgan/AttentionManuscript/battery_sweep_results/pod1/ckpt"
DEVICE = os.environ.get("RVIT_DEVICE", "cpu")
FIGS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "figs"); os.makedirs(FIGS, exist_ok=True)


def load(session, fb):
    import glob
    d = f"{CK}/luo_maunsell_{session}_{fb}"; p = os.path.join(d, "rvit_plus_rl_latest.pt")
    if not os.path.exists(p):
        g = sorted(glob.glob(d + "/*.pt")); p = g[-1]
    ck = torch.load(p, map_location="cpu", weights_only=False); sd = ck["model_state_dict"]
    m = RViTPaperModel(cell="xlstm", feedback=fb, n_quantiles=5, seq_len=T, jepa_n_heads=4,
                       jepa_proto_dim=256, frame_repeat=1, d_mem=128, conv_frontend=True, n_actions=2)
    if "front.out_norm.bias" in sd and not isinstance(m.front.out_norm, nn.LayerNorm):
        m.front.out_norm = nn.LayerNorm(128)
    r = m.load_state_dict(sd, strict=False); m.eval()
    assert not r.missing_keys and not r.unexpected_keys, (r.missing_keys, r.unexpected_keys)
    m.to(DEVICE); return m, int(ck.get("iter", -1))


def make_trial(session, ct, ci, mag):
    """cue at TL(0); ct=change present?; ci=change cell (CUE or UNCUED); mag=Δ (deg)."""
    e = make_env(f"luo_maunsell_{session}", T=T, min_change_time=CHG, max_change_time=CHG,
                 noise_multiplier=5.0, curriculum=False)
    e.reset()
    while e.change_true != ct:
        e.reset()
    e.cue_index = CUE
    if session == "sensitivity":                                  # re-apply the value knob for the fixed cue
        e.loc_value = np.full(e.n_stim, e.v_low, dtype=np.float32); e.loc_value[CUE] = e.v_high
    if ct:
        e.change_index = int(ci); e.change_time = CHG; e.orientation_change = float(mag)
    fr = [e._next_observation().copy()]
    for _ in range(1, T):
        o, _, _, _ = e.step(0); fr.append(o.copy())
    return np.stack(fr), e.response_window


def _tens(v):
    return torch.from_numpy(np.stack(v).astype(np.float32)).permute(0, 1, 4, 2, 3).contiguous()


def declare_rate(m, session, ct, ci, mag, B=400):
    """Fraction that DECLARE (action 1) within the response window [CHG, CHG+window]."""
    vids, win = [], 2
    for _ in range(B):
        v, win = make_trial(session, ct, ci, mag); vids.append(v)
    with torch.no_grad():
        act = m.forward_rl_sequence(_tens(vids).to(DEVICE))["actor_logits_seq"].argmax(-1).cpu().numpy()
    hi = min(CHG + win, T - 1)
    declared = ((act[:, CHG:hi + 1] == 1).any(axis=1))            # any declare in the window
    return float(declared.mean())


def sdt(hr, fa, n=400):
    hr = min(max(hr, 1 / (2 * n)), 1 - 1 / (2 * n)); fa = min(max(fa, 1 / (2 * n)), 1 - 1 / (2 * n))
    zh, zf = norm.ppf(hr), norm.ppf(fa)
    return zh - zf, -0.5 * (zh + zf)          # (d', criterion c)
