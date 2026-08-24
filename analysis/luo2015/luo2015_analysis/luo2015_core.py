"""SDT read-out harness for the cue-free Luo & Maunsell 2015 task analogue.

The old harness is bound to the preliminary cued ``luo_maunsell_*`` tasks. This one
uses the paper-aligned ``luo2015_*`` environment and its active second-test check.

Protocol (from the vetted design review):
  * curriculum OFF; env.theta is set directly to the evaluated max-|Δ| bound.
  * roll out B change and B no-change trials; read the model's per-frame declare decision from
    forward_rl_sequence(V)["actor_logits_seq"].argmax(-1) (one forward pass over the pre-rendered
    T-frame video, exactly as vda_core.press_times does).
  * HIT/FA = declare during first-test frames 3--4.
  * CR = withhold from the unchanged first test and declare to the changed second test at frame 6.
  * Fixation breaks and second-test failures are excluded, matching the paper's SDT denominators.
  * d' = z(HR) - z(FA);  c = -0.5 (z(HR)+z(FA));  rates clamped to [1/(2N), 1-1/(2N)].
  * per-location breakdown (test_loc in {0,3}) for the sensitivity session's d'_high vs d'_low.

Run: python RViT_plus_paper_jepa_grid9/luo2015_analysis/luo2015_core.py <ckpt.pt> --task luo2015_sensitivity --mag 18
"""
import os, sys, glob, argparse
import numpy as np
import torch
import torch.nn as nn

_HERE = os.path.dirname(__file__)
_REPO = os.path.dirname(_HERE)
sys.path.insert(0, _REPO)
sys.path.insert(0, os.path.join(_REPO, "envs"))
from envs import make_env                                            # noqa: E402
from model import RViTPaperModel                                     # noqa: E402

DEVICE = torch.device("cpu")
T = 7
TEST_ONSET = 3
FIRST_TEST_END = 4
SECOND_TEST_ONSET = 6


# ── model loading (explicit checkpoint path; mirrors vda_core.load) ────────────
def load_model(ckpt_path, isz=50, dm=128, feedback="affine_ew"):
    if os.path.isdir(ckpt_path):
        p = os.path.join(ckpt_path, "rvit_plus_rl_latest.pt")
        if not os.path.exists(p):
            g = sorted(glob.glob(os.path.join(ckpt_path, "*.pt")))
            assert g, f"no .pt in {ckpt_path}"; p = g[-1]
        ckpt_path = p
    ck = torch.load(ckpt_path, map_location="cpu", weights_only=False)
    sd = ck["model_state_dict"]
    model_kwargs = ck.get("model_kwargs")
    if model_kwargs:
        m = RViTPaperModel(**model_kwargs)
    else:
        m = RViTPaperModel(
            cell="xlstm", feedback=feedback, n_quantiles=5, seq_len=T,
            jepa_n_heads=4, jepa_proto_dim=256, frame_repeat=1, d_mem=dm,
            conv_frontend=True, grid_rows=2, grid_cols=2, image_size=isz,
        )
    if "front.out_norm.bias" in sd and not isinstance(m.front.out_norm, nn.LayerNorm):
        m.front.out_norm = nn.LayerNorm(128)
    r = m.load_state_dict(sd, strict=False); m.eval(); m.to(DEVICE)
    assert not r.missing_keys and not r.unexpected_keys, (r.missing_keys, r.unexpected_keys)
    return m, int(ck.get("iter", -1))


# ── trial generation on the faithful env ──────────────────────────────────────
def _env(
    task,
    mag,
    spatial_grid_size=2,
    *,
    noise_multiplier=5.0,
):
    e = make_env(
        task, T=T, frame_repeat=1, curriculum=False, theta=float(mag),
        spatial_grid_size=int(spatial_grid_size),
        noise_multiplier=float(noise_multiplier),
    )
    return e


def _reset_to(e, change_true, test_loc=None, tries=2000):
    """reset until the trial has the requested change_true (and test_loc, if given)."""
    for _ in range(tries):
        e.reset()
        if e.change_true == change_true and (test_loc is None or e.test_loc == test_loc):
            return
    raise RuntimeError(f"could not sample change_true={change_true} test_loc={test_loc}")


def _rollout_video(e):
    return e.render_trial()


def _tens(vids):
    return torch.from_numpy(np.stack(vids).astype(np.float32)).permute(0, 1, 4, 2, 3).contiguous()


def gen_trials(task, mag, change_true, B, test_loc=None, spatial_grid_size=2):
    e = _env(task, mag, spatial_grid_size=spatial_grid_size); vids, tlocs = [], []
    for _ in range(B):
        _reset_to(e, change_true, test_loc)
        vids.append(_rollout_video(e)); tlocs.append(int(e.test_loc))
    return _tens(vids).to(DEVICE), np.array(tlocs)


def press_times(
    m,
    V,
    *,
    inject_memory_noise: bool = False,
    sample_actions: bool = False,
):
    with torch.no_grad():
        logits = m.forward_rl_sequence(
            V, inject_memory_noise=inject_memory_noise
        )["actor_logits_seq"]
        if sample_actions:
            act = torch.distributions.Categorical(logits=logits).sample()
        else:
            act = logits.argmax(-1)
        act = act.cpu().numpy()   # (B,T)
    press = np.full(act.shape[0], -1)
    for t in range(T):
        h = (act[:, t] == 1) & (press < 0); press[h] = t
    return press


# ── SDT ────────────────────────────────────────────────────────────────────────
def classify_trial(change_true: int, press_time: int) -> str:
    """Classify the first model declaration using the live environment's rules."""
    press_time = int(press_time)
    if press_time < 0:
        return "miss" if change_true else "second_test_miss"
    if press_time < TEST_ONSET:
        return "fixation_break"
    if press_time <= FIRST_TEST_END:
        return "hit" if change_true else "false_alarm"
    if change_true:
        return "miss"
    if press_time >= SECOND_TEST_ONSET:
        return "correct_rejection"
    return "fixation_break"


def _rate(x, n):
    lo, hi = 1.0 / (2 * n), 1.0 - 1.0 / (2 * n)
    return float(min(max(x, lo), hi))


def _dc(hr, fa, n_h, n_f):
    from statistics import NormalDist

    normal = NormalDist()
    zh = normal.inv_cdf(_rate(hr, n_h))
    zf = normal.inv_cdf(_rate(fa, n_f))
    return zh - zf, -0.5 * (zh + zf)


def summarize_sdt(change_press, no_change_press, change_locations, no_change_locations):
    change_press = np.asarray(change_press)
    no_change_press = np.asarray(no_change_press)
    change_locations = np.asarray(change_locations)
    no_change_locations = np.asarray(no_change_locations)
    change_outcomes = np.array([classify_trial(1, value) for value in change_press])
    no_change_outcomes = np.array([classify_trial(0, value) for value in no_change_press])
    valid_change = np.isin(change_outcomes, ("hit", "miss"))
    valid_no_change = np.isin(no_change_outcomes, ("false_alarm", "correct_rejection"))
    hit = change_outcomes == "hit"
    false_alarm = no_change_outcomes == "false_alarm"
    n_change = int(valid_change.sum())
    n_no_change = int(valid_no_change.sum())
    if n_change == 0 or n_no_change == 0:
        raise ValueError("no valid SDT trials after fixation/engagement exclusions")
    result = {
        "n_change": n_change,
        "n_no_change": n_no_change,
        "excluded_change": int((~valid_change).sum()),
        "excluded_no_change": int((~valid_no_change).sum()),
        "fixation_break_change": int((change_outcomes == "fixation_break").sum()),
        "fixation_break_no_change": int((no_change_outcomes == "fixation_break").sum()),
        "second_test_miss_change": int((change_outcomes == "second_test_miss").sum()),
        "second_test_miss_no_change": int((no_change_outcomes == "second_test_miss").sum()),
        "HR": float(hit.sum() / n_change),
        "FA": float(false_alarm.sum() / n_no_change),
        "premature_on_change": float(
            ((change_press >= 0) & (change_press < TEST_ONSET)).mean()
        ),
    }
    result["dprime"], result["c"] = _dc(
        result["HR"], result["FA"], n_change, n_no_change
    )
    for loc in sorted(set(change_locations.tolist()) | set(no_change_locations.tolist())):
        loc_change_all = change_locations == loc
        loc_no_change_all = no_change_locations == loc
        loc_change = loc_change_all & valid_change
        loc_no_change = loc_no_change_all & valid_no_change
        if loc_change.sum() == 0 or loc_no_change.sum() == 0:
            continue
        hr = float(hit[loc_change].mean())
        fa = float(false_alarm[loc_no_change].mean())
        dprime, criterion = _dc(hr, fa, int(loc_change.sum()), int(loc_no_change.sum()))
        result[f"loc{loc}"] = {
            "total_change": int(loc_change_all.sum()),
            "total_no_change": int(loc_no_change_all.sum()),
            "n_change": int(loc_change.sum()),
            "n_no_change": int(loc_no_change.sum()),
            "excluded_change": int((loc_change_all & ~valid_change).sum()),
            "excluded_no_change": int((loc_no_change_all & ~valid_no_change).sum()),
            "fixation_break_change": int(
                (loc_change_all & (change_outcomes == "fixation_break")).sum()
            ),
            "fixation_break_no_change": int(
                (loc_no_change_all & (no_change_outcomes == "fixation_break")).sum()
            ),
            "second_test_miss_change": int(
                (loc_change_all & (change_outcomes == "second_test_miss")).sum()
            ),
            "second_test_miss_no_change": int(
                (loc_no_change_all & (no_change_outcomes == "second_test_miss")).sum()
            ),
            "valid_fraction_change": float(loc_change.sum() / loc_change_all.sum()),
            "valid_fraction_no_change": float(loc_no_change.sum() / loc_no_change_all.sum()),
            "HR": hr,
            "FA": fa,
            "dprime": float(dprime),
            "c": float(criterion),
        }
    return result


def sdt(m, task, mag, B=400):
    """Return HR, FA, d', c overall and per test-location. B change + B no-change trials."""
    grid_rows = int(getattr(m.front, "grid_rows", 2))
    grid_cols = int(getattr(m.front, "grid_cols", 2))
    image_size = int(getattr(m.front, "image_size", 50))
    if (grid_rows, grid_cols, image_size) not in ((2, 2, 50), (4, 4, 100)):
        raise ValueError(
            "unsupported Luo model/display geometry: "
            f"grid={grid_rows}x{grid_cols}, image_size={image_size}"
        )
    Vc, tlc = gen_trials(
        task, mag, 1, B, spatial_grid_size=grid_rows
    )
    Vn, tln = gen_trials(
        task, mag, 0, B, spatial_grid_size=grid_rows
    )
    pc, pn = press_times(m, Vc), press_times(m, Vn)
    out = summarize_sdt(pc, pn, tlc, tln)
    out.update({"mag": mag, "B": B, "spatial_grid_size": grid_rows})
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("ckpt", help="checkpoint .pt or directory")
    ap.add_argument("--task", default="luo2015_sensitivity",
                    choices=["luo2015_sensitivity", "luo2015_criterion"])
    ap.add_argument("--mag", type=float, default=18.0, help="fixed change magnitude |Δ| (=env.theta)")
    ap.add_argument("--B", type=int, default=400)
    ap.add_argument("--feedback", default="affine_ew")
    a = ap.parse_args()
    m, it = load_model(a.ckpt, feedback=a.feedback)
    r = sdt(m, a.task, a.mag, a.B)
    print(f"[luo2015 SDT] {a.task}  ckpt-iter={it}  |Δ|={a.mag}  (B={a.B}/{a.B})")
    print(f"  HR={r['HR']:.3f}  FA={r['FA']:.3f}  d'={r['dprime']:.3f}  c={r['c']:.3f}  "
          f"(premature-declare on change={r['premature_on_change']:.3f})")
    for loc in (0, 3):
        if f"loc{loc}" in r:
            L = r[f"loc{loc}"]
            print(f"    test_loc={loc}: HR={L['HR']:.3f} FA={L['FA']:.3f} d'={L['dprime']:.3f} c={L['c']:.3f}")
    if r["HR"] in (0.0, 1.0) or r["FA"] in (0.0, 1.0):
        print("  [warn] HR or FA saturated at {0,1} -> pick a θ keeping both in ~(0.1,0.9) before trusting d'/c")


if __name__ == "__main__":
    main()
