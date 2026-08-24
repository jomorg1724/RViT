"""DEFINITIVE Krauzlis eval — uses the EXACT training rollout (model.rl_step in the real env, actions
SAMPLED from the policy like ppo.collect_episodes), then reads out declare PROBABILITIES. First it
reproduces the training rolling/correct_rate (validation that the harness is faithful), then breaks the
policy down by trial type. Greedy (argmax) is also shown to expose the sampled-vs-greedy gap. CPU."""
import numpy as np, torch
from torch.distributions import Categorical
from envs import make_env
from model import RViTPaperModel

POD1 = "/Users/jonathanmorgan/AttentionManuscript/battery_sweep_results/pod1/ckpt"


def load_k(fb):
    f = f"{POD1}/krauzlis_{fb}/rvit_paper_krauzlis_final.pt"
    ck = torch.load(f, map_location="cpu", weights_only=False)
    m = RViTPaperModel(**ck["model_kwargs"]); m.load_state_dict(ck["model_state_dict"], strict=True); m.eval()
    return m


def rollout(m, env, N, greedy=False):
    """Faithful episode rollout (exactly ppo.collect_episodes' loop). Returns correct_rate, P(declared), mean_len."""
    cor = decl = 0; lens = []
    with torch.no_grad():
        for _ in range(N):
            obs = env.reset(); s = m.init_states(1); done = False; r = 0.0; L = 0; did = False
            while not done:
                x = torch.from_numpy(obs.astype(np.float32)).permute(2, 0, 1).unsqueeze(0).contiguous()
                st = m.rl_step(x, s); lg = st["actor_logits"][0]
                a = int(lg.argmax()) if greedy else int(Categorical(logits=lg).sample())
                obs, r, done, _ = env.step(a); s = st["new_states"]; L += 1; did = did or (a == 1)
            cor += (r > 0); decl += did; lens.append(L)
    return cor / N, decl / N, float(np.mean(lens))


def declare_prob(m, fb, cond, mag, B=250):
    """Mean softmax P(declare) at the post-change frames (t=5,6), controlled condition."""
    e = make_env("krauzlis", T=7, min_change_time=5, max_change_time=5, curriculum=False)
    vids = []
    for _ in range(B):
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
        vids.append(np.stack(fr))
    V = torch.from_numpy(np.stack(vids).astype(np.float32)).permute(0, 1, 4, 2, 3).contiguous()
    with torch.no_grad():
        lg = m.forward_rl_sequence(V)["actor_logits_seq"]          # (B,T,2)
    p = torch.softmax(lg, -1)[:, 5:, 1].max(1).values              # peak P(declare) in the response window
    return float(p.mean())


def main():
    for fb in ("crossattn1", "affine_ew"):
        m = load_k(fb)
        env = make_env("krauzlis", T=7, min_change_time=5, max_change_time=5, curriculum=False)  # theta=65, like training
        c_s, d_s, l_s = rollout(m, env, 1500, greedy=False)         # SAMPLED (as training)
        c_g, d_g, l_g = rollout(m, env, 1500, greedy=True)          # GREEDY (argmax)
        print(f"\n=== krauzlis {fb} — FAITHFUL rollout (theta=65, Δ~U(-65,65), like training) ===")
        print(f"  SAMPLED : correct_rate={c_s:.3f}  P(declared)={d_s:.3f}  mean_len={l_s:.2f}   <- compare to training rolling ~0.77-0.80")
        print(f"  GREEDY  : correct_rate={c_g:.3f}  P(declared)={d_g:.3f}  mean_len={l_g:.2f}")
        print(f"  P(declare) softmax, Δ=45:  cued={declare_prob(m,fb,'cued',45):.2f}  "
              f"foil={declare_prob(m,fb,'foil',45):.2f}  no-change={declare_prob(m,fb,'none',45):.2f}", flush=True)


if __name__ == "__main__":
    main()
