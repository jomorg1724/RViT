"""Luo-Maunsell MECHANISTIC localization (the 2018 follow-up). Luo & Maunsell: sensitivity lives in
visual cortex (V4), criterion (+sensitivity) in LPFC. Model analog: is the SENSITIVITY effect carried
by an ATTENTION GAIN at the cued location (V4-like sensory stage), while the CRITERION effect is a
DECISION-level declare-bias (LPFC-like), NOT an attention gain? Measured on NO-CHANGE trials (cue at
TL) so attention reflects the top-down reward allocation, not a bottom-up change pull. Compute -> print."""
import os, numpy as np, torch, luo_core as C


def mechanism(session, fb, B=300):
    m, it = C.load(session, fb)
    vids = [C.make_trial(session, 0, -1, 18.0)[0] for _ in range(B)]        # no-change, cue@TL
    with torch.no_grad():
        o = m.forward_rl_sequence(C._tens(vids).to(C.DEVICE), return_attn=True)
        attn = o["attn_seq"].cpu().numpy()                                  # (B,T,N,K)
        logits = o["actor_logits_seq"].cpu().numpy()                        # (B,T,2)
    N, K = 4, attn.shape[-1]
    def loc(i):                                                             # attention TO location i
        keys = [i, N + i] if K == 2 * N else [i]
        return attn[:, :, :, keys].sum(-1).mean(2)                          # (B,T)
    a_cued = float(loc(C.CUE)[:, 3:7].mean())                               # stimulus epoch t3-6
    a_unc = float(loc(C.UNCUED)[:, 3:7].mean())
    declare_bias = float((logits[:, C.CHG, 1] - logits[:, C.CHG, 0]).mean())  # actor declare-logit @ change frame
    return it, a_cued, a_unc, a_cued - a_unc, declare_bias


def main():
    print(f"{'model':28s} {'α_cued':>7s} {'α_uncued':>8s} {'α_gain':>7s} {'declare_bias':>12s}")
    for session in ("sensitivity", "criterion"):
        for fb in ("crossattn1", "affine_ew"):
            it, ac, au, gain, db = mechanism(session, fb)
            print(f"{session+'_'+fb:28s} {ac:7.3f} {au:8.3f} {gain:+7.3f} {db:+12.3f}", flush=True)


if __name__ == "__main__":
    main()
