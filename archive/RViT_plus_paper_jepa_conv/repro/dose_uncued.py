"""Proper dose-response: hit rate on an UNCUED change (cue S1, change at S4) vs stimulation strength on
the CHANGE location, swept consistently from natural (bias 0) to full (bias +100 = the hard clamp used
in Fig 5). Δ=18°. Both conv variants. Saves data_dose_conv.npz."""
import os, sys, numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import repro_core as C
BIAS=[0,1,2,3,4,6,10,20,100]; MAG=18.0; CHG=3; CUE=0; B=300
out={}
for fb,snap in [("crossattn1","/Users/jonathanmorgan/rvit_plus_checkpoints/paper_jepa_conv_d128/rvit_plus_rl_latest.pt"),
                ("affine_ew","/Users/jonathanmorgan/rvit_plus_checkpoints/paper_jepa_conv_affine_ew/rvit_plus_rl_latest.pt")]:
    m,IT=C.load(snap,fb); K=C.attn_maps(m,0,1.0,"red",0,-1,B=8).shape[-1]
    hits=[]
    for b in BIAS:
        clamp=None if b==0 else {str(k):float(b) for k in C._loc_keys(K,CHG)}
        p=C.press_times_clamp(m,CUE,1.0,"red",1,CHG,MAG,clamp,5,B); hits.append(float((p>=5).mean()))
    out[fb]=hits; print(f"[dose conv {fb}] iter={IT} hit vs bias {BIAS}: {[round(x,2) for x in hits]}")
np.savez(os.path.join(os.path.dirname(os.path.abspath(__file__)),"data_dose_conv.npz"),bias=BIAS,mag=MAG,**out)
print("saved data_dose_conv.npz")
