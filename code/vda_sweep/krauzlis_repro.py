"""Krauzlis attend-here/ignore-here reproduction (SC spatial selection). The KrauzlisEnv rewards ONLY a
change at the CUED location; a change elsewhere is a distractor to IGNORE. We measure spatial SELECTION
(declare on a cued change vs a distractor change vs no-change), then the causal SC-inactivation analog:
suppress the cued-location attention (α clamp) and ask whether SELECTION breaks — Zénon & Krauzlis (2012):
SC inactivation impairs target selection, not visual sensitivity. crossattn1 + affine_ew. MPS/CPU."""
import os, numpy as np, torch, torch.nn as nn
from pathlib import Path
import vda_core as C
from model import RViTPaperModel

POD1 = "/Users/jonathanmorgan/AttentionManuscript/battery_sweep_results/pod1/ckpt"
MAGS = [18.0, 30.0, 45.0]                       # sub- → supra-threshold change magnitudes
B, SEED = 300, 20250707


def load_k(task, fb, dm=128):
    f = f"{POD1}/{task}_{fb}/rvit_paper_{task}_final.pt"
    ck = torch.load(f, map_location="cpu", weights_only=False); sd = ck["model_state_dict"]
    m = RViTPaperModel(cell="xlstm", feedback=fb, n_quantiles=5, seq_len=C.T, jepa_n_heads=4,
                       jepa_proto_dim=256, frame_repeat=1, d_mem=dm, conv_frontend=True,
                       grid_rows=2, grid_cols=2, image_size=50)
    if "front.out_norm.bias" in sd and not isinstance(m.front.out_norm, nn.LayerNorm):
        m.front.out_norm = nn.LayerNorm(128)
    r = m.load_state_dict(sd, strict=False); m.eval(); m.to(C.DEVICE)
    assert not r.missing_keys and not r.unexpected_keys, (r.missing_keys[:3], r.unexpected_keys[:3])
    return m, int(ck.get("iter", -1))


def decl(m, ci, mag, ct=1, clamp=None, cf=1, B=B, videos=None):
    p = C.press_times_clamp(
        m,
        "krauzlis",
        C.TL,
        1.0,
        "red",
        ct,
        ci,
        mag,
        clamp=clamp,
        clamp_from=cf,
        B=B,
        videos=videos,
    )
    return float((p >= 5).mean())


def run_conditions(m, K, seed=SEED, B=B):
    """Compare natural and suppressed attention on identical trial batches."""
    supp = C.clamp_alpha(K, m.n_tokens, C.TL, 0.0)
    hc, hd, hc_s, hd_s = [], [], [], []
    for index, mag in enumerate(MAGS):
        cued_videos = C.make_video_batch(
            "krauzlis", C.TL, 1.0, "red", 1, C.TL, mag,
            B=B, seed=seed + 2 * index,
        )
        distractor_videos = C.make_video_batch(
            "krauzlis", C.TL, 1.0, "red", 1, C.BR, mag,
            B=B, seed=seed + 2 * index + 1,
        )
        hc.append(decl(m, C.TL, mag, B=B, videos=cued_videos))
        hc_s.append(decl(m, C.TL, mag, clamp=supp, B=B, videos=cued_videos))
        hd.append(decl(m, C.BR, mag, B=B, videos=distractor_videos))
        hd_s.append(decl(m, C.BR, mag, clamp=supp, B=B, videos=distractor_videos))

    no_change_videos = C.make_video_batch(
        "krauzlis", C.TL, 1.0, "red", 0, -1, MAGS[-1],
        B=B, seed=seed + 2 * len(MAGS),
    )
    fa = decl(m, -1, MAGS[-1], ct=0, B=B, videos=no_change_videos)
    return hc, hd, fa, hc_s, hd_s


def main():
    out = {"MAGS": np.array(MAGS), "seed": np.int64(SEED), "n": np.int64(B)}
    for fb in ("crossattn1", "affine_ew"):
        m, it = load_k("krauzlis", fb)
        K = 2 * m.n_tokens if fb == "crossattn1" else m.n_tokens
        hc, hd, fa, hc_s, hd_s = run_conditions(m, K)
        out[f"{fb}_hit_cued"] = np.array(hc); out[f"{fb}_decl_dist"] = np.array(hd)
        out[f"{fb}_hit_cued_supp"] = np.array(hc_s); out[f"{fb}_decl_dist_supp"] = np.array(hd_s)
        out[f"{fb}_fa"] = fa
        out[f"{fb}_iter"] = np.int64(it)
        sel = np.array(hc) - np.array(hd); sel_s = np.array(hc_s) - np.array(hd_s)
        print(f"=== krauzlis {fb} (iter {it}) — declare rate, MAGS={MAGS} ===")
        print(f"  BASELINE   hit@cued={['%.2f'%x for x in hc]}  declare@distractor={['%.2f'%x for x in hd]}  FA={fa:.2f}")
        print(f"             SELECTION index (cued−distractor) = {['%.2f'%x for x in sel]}")
        print(f"  SC-INACTIV hit@cued={['%.2f'%x for x in hc_s]}  declare@distractor={['%.2f'%x for x in hd_s]}")
        print(f"             SELECTION index (suppressed)       = {['%.2f'%x for x in sel_s]}", flush=True)
    output = os.path.abspath(os.path.join(C.FIGS, "krauzlis.npz"))
    np.savez(output, **out)
    print("[krauzlis] saved", flush=True)
    return Path(output).resolve()


if __name__ == "__main__":
    main()
