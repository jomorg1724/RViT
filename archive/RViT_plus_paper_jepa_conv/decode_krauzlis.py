"""Did the always-wait Krauzlis model learn the task STRUCTURE in its perception/memory, even though its
actor never declares? Decode from the memory cell: (a) 3-way {no-change, cued-change, foil-change} at the
post-change frame, and (b) the CUE location {TL vs BR} after the cue. High decodability ⇒ the substrate
learned to see+localize+remember (a pure actor/exploration collapse, task is sound & learnable). Low ⇒ the
perception itself failed. Δ=45. CPU/MPS."""
import numpy as np, torch
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import cross_val_score
from envs import make_env
from model import RViTPaperModel

POD1 = "/Users/jonathanmorgan/AttentionManuscript/battery_sweep_results/pod1/ckpt"


def load_k(fb):
    f = f"{POD1}/krauzlis_{fb}/rvit_paper_krauzlis_final.pt"
    ck = torch.load(f, map_location="cpu", weights_only=False)
    m = RViTPaperModel(**ck["model_kwargs"]); m.load_state_dict(ck["model_state_dict"], strict=True); m.eval()
    return m


def collect(m, N=900, mag=45.0):
    e = make_env("krauzlis", T=7, min_change_time=5, max_change_time=5, curriculum=False)
    vids, y3, ycue = [], [], []
    for _ in range(N):
        cond = np.random.choice([0, 1, 2])              # 0 none, 1 cued, 2 foil
        while True:
            e.reset()
            if cond == 0 and e.change_true == 0: break
            if cond != 0 and e.change_true == 1:
                e.change_index = e.cue_index if cond == 1 else e.foil_index
                e.orientation_change = mag; break
        fr = [e._next_observation().copy()]
        for _ in range(1, e.n_logical):
            o, _, _, _ = e.step(0); fr.append(o.copy())
        vids.append(np.stack(fr)); y3.append(cond); ycue.append(0 if e.cue_index == 0 else 1)
    V = torch.from_numpy(np.stack(vids).astype(np.float32)).permute(0, 1, 4, 2, 3).contiguous()
    with torch.no_grad():
        cell = m.forward_rl_sequence(V, return_cell=True)["cell_seq"].numpy()   # (N,T,4,d_mem)
    return cell, np.array(y3), np.array(ycue)


def dec(cell, y, t):
    X = cell[:, t].reshape(len(y), -1)
    return float(cross_val_score(LogisticRegression(max_iter=400, C=0.5), X, y, cv=4,
                                 scoring="balanced_accuracy").mean())


def main():
    for fb in ("crossattn1", "affine_ew"):
        m = load_k(fb); cell, y3, ycue = collect(m)
        print(f"\n=== krauzlis {fb} — decode from MEMORY (actor is always-wait) ===")
        print(f"  cue location (TL vs BR) @t=4  : {dec(cell, ycue, 4):.2f}   (chance 0.50 — did it remember the cue?)")
        print(f"  3-way none/cued/foil  @t=6    : {dec(cell, y3, 6):.2f}   (chance 0.33 — did it see+localize the change?)")
        # is a cued change linearly separable from no-change / from foil?
        m_cn = y3 != 2; m_cf = y3 != 0
        print(f"    cued vs no-change   @t=6    : {dec(cell[m_cn], (y3[m_cn]==1).astype(int), 6):.2f}   (chance 0.50)")
        print(f"    cued vs foil        @t=6    : {dec(cell[m_cf], (y3[m_cf]==1).astype(int), 6):.2f}   (chance 0.50 — the localization the task needs)", flush=True)


if __name__ == "__main__":
    main()
