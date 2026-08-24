"""Analysis harness for the trained BARUNI model (conv repo). Tests reproduction of Baruni, Lau &
Salzman (2015, Nat Neurosci; doi:10.1038/nn.4141): attentional BEHAVIOUR is controlled by RELATIVE
value, while sensory (V4) coding tracks ABSOLUTE value. Task: two diagonal stimuli (S1=0, S4=3), a
coloured VALUE cue on BOTH (red=5/green=3/blue=1), the QUERIED location revealed LATE (t>=query_frame);
the model reports the queried cell's tilt class (2-AFC, Discrete(3): wait / report class0 / report
class1). Value pair = (queried value, distractor value): LS/SL/LL/SS. CPU, thread-capped."""
import os, sys, glob, numpy as np, torch, torch.nn as nn
torch.set_num_threads(3)
_ROOT = "/Users/jonathanmorgan/AttentionManuscript/RViT_plus_paper_jepa_conv"
sys.path.insert(0, _ROOT)
from model import RViTPaperModel
from envs import make_env

T = 11; ACTIVE = (0, 3); QF = 8                 # 2 stimuli on the diagonal; query revealed at t>=8
V_L, V_S = 5.0, 1.0                             # large / small value (red / blue cue)
CK = "/Users/jonathanmorgan/AttentionManuscript/battery_sweep_results/pod1/ckpt"
DEVICE = os.environ.get("RVIT_DEVICE", "cpu")
FIGS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "figs"); os.makedirs(FIGS, exist_ok=True)
# value-pair conditions: (queried_value, distractor_value)
PAIRS = {"LS": (V_L, V_S), "LL": (V_L, V_L), "SS": (V_S, V_S), "SL": (V_S, V_L)}


def load(fb):
    d = f"{CK}/baruni_{fb}"; p = os.path.join(d, "rvit_plus_rl_latest.pt")
    if not os.path.exists(p):
        g = sorted(glob.glob(d + "/*.pt")); p = g[-1]
    ck = torch.load(p, map_location="cpu", weights_only=False); sd = ck["model_state_dict"]
    m = RViTPaperModel(cell="xlstm", feedback=fb, n_quantiles=5, seq_len=T, jepa_n_heads=4,
                       jepa_proto_dim=256, frame_repeat=1, d_mem=128, conv_frontend=True, n_actions=3,
                       init_action_bias=[0.0, -1.0, -1.0])   # 3-action (wait/report0/report1); overwritten by ckpt
    if "front.out_norm.bias" in sd and not isinstance(m.front.out_norm, nn.LayerNorm):
        m.front.out_norm = nn.LayerNorm(128)
    r = m.load_state_dict(sd, strict=False); m.eval()
    assert not r.missing_keys and not r.unexpected_keys, (r.missing_keys, r.unexpected_keys)
    m.to(DEVICE); return m, int(ck.get("iter", -1))


def make_trial(vq, vd, queried, cls_q, tilt):
    """queried cell: value vq, class cls_q (tilt sign), |tilt|. Distractor: value vd, random class."""
    e = make_env("baruni", T=T, curriculum=False); e.reset()
    other = ACTIVE[1] if queried == ACTIVE[0] else ACTIVE[0]
    e.val = {queried: float(vq), other: float(vd)}
    e._val2color = {v: c for c, v in e.color_values.items()}
    e.queried = int(queried)
    e.cls[queried] = int(cls_q); e.orientations[queried] = e.BOUNDARY + (tilt if cls_q == 1 else -tilt)
    dc = int(np.random.rand() < 0.5)                      # distractor: random class, same |tilt|
    e.cls[other] = dc; e.orientations[other] = e.BOUNDARY + (tilt if dc == 1 else -tilt)
    fr = [e._next_observation().copy()]
    for _ in range(1, T):
        o, _, _, _ = e.step(0); fr.append(o.copy())
    return np.stack(fr)


def _tens(v):
    return torch.from_numpy(np.stack(v).astype(np.float32)).permute(0, 1, 4, 2, 3).contiguous()


def behavior(m, vq, vd, tilt=8.0, B=300):
    """Over random queried cell + class: accuracy (among declared), declare rate, report latency."""
    vids, truth = [], []
    for _ in range(B):
        q = int(np.random.choice(ACTIVE)); c = int(np.random.rand() < 0.5)
        vids.append(make_trial(vq, vd, q, c, tilt)); truth.append(c)
    with torch.no_grad():
        lg = m.forward_rl_sequence(_tens(vids).to(DEVICE))["actor_logits_seq"].cpu().numpy()   # (B,T,3)
    truth = np.array(truth); corr = decl = 0; lat = []
    for b in range(B):
        rep = -1
        for t in range(T):
            a = int(lg[b, t].argmax())
            if a in (1, 2) and t >= QF:
                rep = a - 1; lat.append(t); break
        if rep >= 0:
            decl += 1; corr += int(rep == truth[b])
    return dict(acc=corr / max(decl, 1), declare=decl / B, rt=(float(np.mean(lat)) if lat else np.nan))


def attn_by_cell(m, vq, vd, queried, tilt=8.0, B=96):
    """Mean attention allocated TO the queried cell and TO the distractor, per timestep."""
    vids = [make_trial(vq, vd, queried, int(np.random.rand() < 0.5), tilt) for _ in range(B)]
    with torch.no_grad():
        a = m.forward_rl_sequence(_tens(vids).to(DEVICE), return_attn=True)["attn_seq"].cpu().numpy().mean(0)  # (T,4,K)
    K = a.shape[2]
    def loc(i):
        keys = [i, 4 + i] if K == 8 else [i]
        return a[:, :, keys].sum(-1).mean(1)                # (T,) attention to location i
    other = ACTIVE[1] if queried == ACTIVE[0] else ACTIVE[0]
    return loc(queried), loc(other)                          # (queried, distractor) attention time-courses
