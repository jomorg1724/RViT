"""Does the Krauzlis critic KNOW declaring a cued change is worth +1? Read the per-action Q (QR-DQN mean
over quantiles) for wait vs declare at the decision frames, by trial type. Splits the diagnosis:
  Q(declare)>Q(wait) on cued-change but actor P(declare)=0  -> ACTOR not following its critic (policy bug)
  Q(declare)<=Q(wait) on cued-change                        -> CRITIC never learned declaring's value (exploration)
Δ=45. CPU."""
import numpy as np, torch
from envs import make_env
from model import RViTPaperModel

POD1 = "/Users/jonathanmorgan/AttentionManuscript/battery_sweep_results/pod1/ckpt"


def load_k(fb):
    f = f"{POD1}/krauzlis_{fb}/rvit_paper_krauzlis_final.pt"
    ck = torch.load(f, map_location="cpu", weights_only=False)
    m = RViTPaperModel(**ck["model_kwargs"]); m.load_state_dict(ck["model_state_dict"], strict=True); m.eval()
    return m


def trials(cond, B=250, mag=45.0):
    e = make_env("krauzlis", T=7, min_change_time=5, max_change_time=5, curriculum=False)
    vids = []
    for _ in range(B):
        while True:
            e.reset()
            if cond == "none" and e.change_true == 0: break
            if cond != "none" and e.change_true == 1:
                e.change_index = e.cue_index if cond == "cued" else e.foil_index
                e.orientation_change = mag; break
        fr = [e._next_observation().copy()]
        for _ in range(1, e.n_logical):
            o, _, _, _ = e.step(0); fr.append(o.copy())
        vids.append(np.stack(fr))
    return torch.from_numpy(np.stack(vids).astype(np.float32)).permute(0, 1, 4, 2, 3).contiguous()


def main():
    for fb in ("crossattn1", "affine_ew"):
        m = load_k(fb)
        print(f"\n=== krauzlis {fb} — critic Q(action) + policy at decision frames (t=5, t=6) ===")
        print(f"{'trial':6s} {'t':>2s} {'Q(wait)':>8s} {'Q(declare)':>11s} {'Q(decl)-Q(wait)':>15s} {'P(declare)':>11s}")
        for cond in ("none", "cued", "foil"):
            V = trials(cond)
            with torch.no_grad():
                out = m.forward_rl_sequence(V)
                q = out["q_dist_seq"].mean(-1)                    # (B,T,A) mean over quantiles = Q(s,a)
                p = torch.softmax(out["actor_logits_seq"], -1)    # (B,T,A)
            for t in (5, 6):
                qw, qd = float(q[:, t, 0].mean()), float(q[:, t, 1].mean())
                pd = float(p[:, t, 1].mean())
                print(f"{cond:6s} {t:>2d} {qw:8.3f} {qd:11.3f} {qd-qw:15.3f} {pd:11.3f}")


if __name__ == "__main__":
    main()
