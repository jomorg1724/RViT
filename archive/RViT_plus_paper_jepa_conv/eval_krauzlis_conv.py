"""Re-evaluate the trained Krauzlis models on the CORRECT conv env (2-stimulus: cued + 1 diagonal foil,
2 blank; correct-withhold on a foil change IS rewarded). Earlier analysis used the grid9 4-active env by
mistake (out-of-distribution). Measure declare@cued-change vs declare@foil-change vs correct-rejection,
plus the oracle ceiling on THIS env. CPU."""
import numpy as np, torch
from envs import make_env
from model import RViTPaperModel

POD1 = "/Users/jonathanmorgan/AttentionManuscript/battery_sweep_results/pod1/ckpt"


def load_k(fb):
    f = f"{POD1}/krauzlis_{fb}/rvit_paper_krauzlis_final.pt"
    ck = torch.load(f, map_location="cpu", weights_only=False)
    mk = {k: v for k, v in ck.get("model_kwargs", {}).items()}
    m = RViTPaperModel(**mk); m.load_state_dict(ck["model_state_dict"], strict=True); m.eval()
    return m, int(ck.get("iter", -1))


def make_trial(e, cond, mag):
    """cond: 'cued' (change at cued), 'foil' (change at foil), 'none' (no change). Returns (T,H,W,3)."""
    e.reset()
    if cond == "none":
        while e.change_true != 0: e.reset()
    else:
        while e.change_true != 1: e.reset()
        e.change_index = e.cue_index if cond == "cued" else e.foil_index
        e.orientation_change = float(mag)
    fr = [e._next_observation().copy()]
    for _ in range(1, e.n_logical):
        o, _, _, _ = e.step(0); fr.append(o.copy())
    return np.stack(fr)


def declare_rate(m, e, cond, mag, B=250):
    vids = np.stack([make_trial(e, cond, mag) for _ in range(B)]).astype(np.float32)
    V = torch.from_numpy(vids).permute(0, 1, 4, 2, 3).contiguous()
    with torch.no_grad():
        act = m.forward_rl_sequence(V)["actor_logits_seq"].argmax(-1).numpy()   # (B,T)
    press = np.full(B, -1)
    for t in range(act.shape[1]):
        h = (act[:, t] == 1) & (press < 0); press[h] = t
    return float((press >= 5).mean())


def oracle_ceiling(N=6000):
    e = make_env("krauzlis", T=7, min_change_time=5, max_change_time=5, curriculum=False)
    cor = 0
    for _ in range(N):
        e.reset(); rep = (e.change_true == 1 and e._is_reportable_change())
        done = False; r = 0; t = 0
        while not done:
            _, r, done, _ = e.step(1 if (rep and t >= e.change_time) else 0); t += 1
        cor += (r > 0)
    return cor / N


def main():
    print(f"conv KrauzlisEnv oracle ceiling = {oracle_ceiling():.3f}  (curriculum advances at 0.85)")
    for fb in ("crossattn1", "affine_ew"):
        m, it = load_k(fb)
        e = make_env("krauzlis", T=7, min_change_time=5, max_change_time=5, curriculum=False)
        print(f"\n=== krauzlis {fb} (iter {it}) on the CORRECT conv env ===")
        for mag in (26.0, 45.0, 64.0):
            hc = declare_rate(m, e, "cued", mag); hf = declare_rate(m, e, "foil", mag)
            print(f"  mag {mag:4.0f}: declare@CUED-change={hc:.2f}  declare@FOIL-change={hf:.2f}  selection(cued−foil)={hc-hf:+.2f}")
        cr = 1.0 - declare_rate(m, e, "none", 45.0)
        print(f"  correct-rejection (withhold on no-change) = {cr:.2f}")


if __name__ == "__main__":
    main()
