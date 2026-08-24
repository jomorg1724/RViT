"""Does the mem-noise baruni critic ENCODE value? Reward = cue value (V_L=5 vs V_S=1), so the critic V MUST
scale with value or something is broken. Measure critic V_scalar (mean over stimulus frames) per value pair,
and decode the QUERIED value {V_L vs V_S} from memory. This separates value-in-critic (must exist) from
value-directed-attention (already shown absent) and from relative-value behaviour (already shown absent)."""
import numpy as np, torch
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import cross_val_score
import baruni_core as C
from baruni_memnoise_test import load_mn


def vids_for(vq, vd, B):
    return C._tens([C.make_trial(vq, vd, int(np.random.choice(C.ACTIVE)), int(np.random.rand() < 0.5), 8.0)
                    for _ in range(B)]).to(C.DEVICE)


def main():
    m, it = load_mn(); print(f"mem-noise crossattn1 iter={it}\n")
    print("critic V_scalar (mean over stimulus frames t3..T), by value pair (queried/distractor):")
    Vs = {}
    for name, (vq, vd) in C.PAIRS.items():
        with torch.no_grad():
            v = m.forward_rl_sequence(vids_for(vq, vd, 250))["V_scalar_seq"][:, 3:].mean().item()
        Vs[name] = v
        print(f"   {name} (q{vq:.0f}/d{vd:.0f}):  V={v:.3f}")
    print(f"\n   queried-value effect  V(LL)-V(SS) = {Vs['LL']-Vs['SS']:+.3f}   V(LS)-V(SL) = {Vs['LS']-Vs['SL']:+.3f}")
    print(f"   (if the critic encodes value, high-queried LL/LS > low-queried SS/SL)")

    # decode the QUERIED value (V_L vs V_S) from memory at a stimulus frame
    X, y = [], []
    for lab, vq in ((1, C.V_L), (0, C.V_S)):
        with torch.no_grad():
            cell = m.forward_rl_sequence(vids_for(vq, C.V_S, 200), return_cell=True)["cell_seq"][:, 6].reshape(200, -1).cpu().numpy()
        X.append(cell); y += [lab] * 200
    X = np.concatenate(X); y = np.array(y)
    acc = cross_val_score(LogisticRegression(max_iter=400, C=0.5), X, y, cv=4, scoring="balanced_accuracy").mean()
    print(f"\n   decode QUERIED value (V_L vs V_S) from memory @t6: {acc:.2f}  (chance 0.50 — is value represented at all?)")


if __name__ == "__main__":
    main()
