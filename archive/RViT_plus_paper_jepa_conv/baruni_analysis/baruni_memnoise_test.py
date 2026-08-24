"""Run the Baruni RELATIVE-VALUE reproduction on the mem-noise crossattn1 checkpoint (the whole point of the
noise). Signature = acc(LS) > acc(LL)≈acc(SS) > acc(SL): same stimulus discriminated better when its value is
high RELATIVE to the distractor. Earlier non-noise model was flat/absolute — does the noise recover relative?"""
import os, shutil, time, numpy as np, torch, torch.nn as nn
import baruni_core as C
from model import RViTPaperModel

SRC = "/Users/jonathanmorgan/AttentionManuscript/battery_sweep_results/baruni_memnoise/baruni_crossattn1_mn05/rvit_plus_rl_latest.pt"
SNAP = "/private/tmp/claude-501/-Users-jonathanmorgan-AttentionManuscript/e9d3f8f2-ea15-45cb-80f5-91a5ff313074/scratchpad/baruni_mn_snap.pt"


def snapshot():
    for _ in range(5):                                   # copy may catch a mid-write; retry
        shutil.copy(SRC, SNAP)
        try:
            ck = torch.load(SNAP, map_location="cpu", weights_only=False); return ck
        except Exception:
            time.sleep(3)
    raise RuntimeError("could not read a clean checkpoint snapshot")


def load_mn():
    ck = snapshot(); sd = ck["model_state_dict"]
    m = RViTPaperModel(cell="xlstm", feedback="crossattn1", n_quantiles=5, seq_len=C.T, jepa_n_heads=4,
                       jepa_proto_dim=256, frame_repeat=1, d_mem=128, conv_frontend=True, n_actions=3,
                       init_action_bias=[0.0, -1.0, -1.0])   # mem_noise defaults 0 -> deterministic eval
    if "front.out_norm.bias" in sd and not isinstance(m.front.out_norm, nn.LayerNorm):
        m.front.out_norm = nn.LayerNorm(128)
    r = m.load_state_dict(sd, strict=False); m.eval()
    assert not r.missing_keys and not r.unexpected_keys, (r.missing_keys, r.unexpected_keys)
    return m, int(ck.get("iter", -1))


def main():
    print(f"baruni_core T={C.T} QF={C.QF} V_L={C.V_L} V_S={C.V_S} ACTIVE={C.ACTIVE}")
    m, it = load_mn(); print(f"mem-noise crossattn1  iter={it}\n")
    print(f"{'tilt':>4s}  {'LS':>6s} {'LL':>6s} {'SS':>6s} {'SL':>6s}   {'LS-SL (relative idx)':>20s}")
    for tilt in (4.0, 6.0, 8.0):
        accs = {}
        for name, (vq, vd) in C.PAIRS.items():
            accs[name] = C.behavior(m, vq, vd, tilt=tilt, B=250)["acc"]
        ri = accs["LS"] - accs["SL"]
        print(f"{tilt:4.0f}  {accs['LS']:6.3f} {accs['LL']:6.3f} {accs['SS']:6.3f} {accs['SL']:6.3f}   {ri:+20.3f}")
    aH, aL = C.attn_by_cell(m, C.V_L, C.V_S, C.ACTIVE[0])
    print(f"\nattn (LS): high-value cell stim={aH[3:8].mean():.3f}  low-value cell stim={aL[3:8].mean():.3f}  "
          f"(diff={aH[3:8].mean()-aL[3:8].mean():+.3f} — value-directed attention?)")
    print("\nRelative-value signature = LS highest, SL lowest, LL≈SS between. Positive relative idx = recovered.")


if __name__ == "__main__":
    main()
