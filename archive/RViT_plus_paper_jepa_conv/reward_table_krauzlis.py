"""Reward truth table for the conv KrauzlisEnv — step the env through every (trial type × action plan)
and print the actual reward the env pays. This directly verifies the reward function is correct
(vs. asserting it). Δ=45 (suprathreshold), averaged over trials since cue location / other Gabors vary."""
import numpy as np
from envs import make_env

N = 600
CONDS = ["none", "cued", "foil"]
PLANS = {
    "wait_all":      lambda t: 0,                 # never declare → times out at T
    "declare_at_5":  lambda t: 1 if t >= 5 else 0,  # declare on the change frame (valid timing)
    "declare_early": lambda t: 1 if t >= 3 else 0,  # declare before the change (premature)
}
EXPECT = {
    ("none", "wait_all"): ">0 (correct rejection)", ("none", "declare_at_5"): "0 (false alarm)",
    ("none", "declare_early"): "0 (false alarm)",
    ("cued", "wait_all"): "0 (miss the target)", ("cued", "declare_at_5"): ">0 (HIT)",
    ("cued", "declare_early"): "0 (premature)",
    ("foil", "wait_all"): ">0 (correct withhold)", ("foil", "declare_at_5"): "0 (declared a distractor)",
    ("foil", "declare_early"): "0 (premature/distractor)",
}


def force(e, cond):
    while True:
        e.reset()
        if cond == "none":
            if e.change_true == 0: return
        else:
            if e.change_true == 1:
                e.change_index = e.cue_index if cond == "cued" else e.foil_index
                e.orientation_change = 45.0
                return


def run(e, plan):
    total = 0.0; t = 0; done = False
    while not done:
        _, r, done, _ = e.step(plan(t)); total += r; t += 1
    return total


def main():
    e = make_env("krauzlis", T=7, min_change_time=5, max_change_time=5, curriculum=False)
    print(f"{'trial':6s} {'action plan':14s} {'mean reward':>11s}   expected")
    print("-" * 70)
    for cond in CONDS:
        for pn, pf in PLANS.items():
            rs = []
            for _ in range(N):
                force(e, cond); rs.append(run(e, pf))
            mr = float(np.mean(rs))
            flag = "" if (mr > 0) == (">0" in EXPECT[(cond, pn)]) else "  <-- UNEXPECTED"
            print(f"{cond:6s} {pn:14s} {mr:11.3f}   {EXPECT[(cond, pn)]}{flag}")
    # oracle vs always-wait, spelled out
    print("\nAlways-wait pays on: no-change (CR) + foil-change (correct withhold) → high baseline.")
    print("The ONLY thing always-wait loses is the cued-change HIT — which is the thing the model must learn.")


if __name__ == "__main__":
    main()
