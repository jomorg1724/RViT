"""PROOF that the colour VAE sees the value cue and the grayscale VAE does not.
Render the CUE FRAME (t=1, NOT the blank t=0) with the SAME stimulus, varying only cue colour;
encode through each front-end + its matching VAE encoder; report token differences across colours."""
import os, sys, numpy as np, torch
torch.set_num_threads(3); sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from vae_frontend import VAEPatchFrontEnd
from envs import make_env

def cue_frame(color, seed=7):
    e=make_env("vda4",T=7,min_change_time=5,max_change_time=5,noise_multiplier=5.0,curriculum=False)
    np.random.seed(seed); o=e.reset()                           # SAME stimulus each call (fixed seed)
    e.change_true=0; e.cue_index=0; e.cue_color=color; e.proportion=1.0   # force no-change; only colour varies
    o,_,_,_=e.step(0)        # advance to t=1 → the CUE frame (cue shown at t=1, not blank t=0)
    return o.astype(np.float32)

frames={c:cue_frame(c) for c in ["red","green","blue"]}
print("raw-pixel |red-blue| at cue frame:", round(float(np.abs(frames['red']-frames['blue']).sum()),1),
      "(>0 ⇒ cue IS coloured in the input)")

def tokens(front, ckpt, color):
    blob=torch.load(ckpt, map_location="cpu", weights_only=False)
    front.load_pretrained(blob["encoder_state"], freeze=True); front.eval()
    x=torch.from_numpy(frames[color]).permute(2,0,1).unsqueeze(0)
    with torch.no_grad(): return front(x,1)[0,:, :128]   # the VAE part of each token (B removed)

GRAY=os.path.expanduser("~/rvit_plus_checkpoints/paper_vae/vae.pt")
COLOR=os.path.expanduser("~/rvit_plus_checkpoints/paper_vae_color/vae_color.pt")
for name, ckpt, inch in [("GRAYSCALE VAE", GRAY, 1), ("COLOUR VAE", COLOR, 3)]:
    if not os.path.exists(ckpt): print(f"{name}: {ckpt} not found — skip"); continue
    f=VAEPatchFrontEnd(in_channels=inch)
    tk={c:tokens(f,ckpt,c) for c in ["red","green","blue"]}
    rb=float((tk['red']-tk['blue']).abs().sum()); rg=float((tk['red']-tk['green']).abs().sum())
    seesvalue = rb>1e-3
    print(f"{name:14}: token |red-blue|={rb:.4f}  |red-green|={rg:.4f}  → "
          f"{'SEES the value cue ✓' if seesvalue else 'VALUE-BLIND (colours identical) ✗'}")
