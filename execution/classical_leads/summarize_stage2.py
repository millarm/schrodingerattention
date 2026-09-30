"""Summarise Stage 2 against the tests fixed in stage2-spec.md."""

from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np
from scipy import stats

RESULTS = Path(__file__).resolve().parent / "stage2_results"
SEEDS = list(range(3001, 3013))
E1_WINDOW = (800, 2000)
E2_WINDOW = (4000, 8000)


def load() -> dict:
    runs = {}
    for path in RESULTS.glob("stage2-*-u8000.json"):
        r = json.loads(path.read_text())
        runs[(r["arm"], r["seed"])] = r
    return runs


def window(points, key, lo, hi):
    values = [p[key] for p in points if lo <= p["update"] <= hi]
    return float(np.mean(values))


def endpoints(r) -> dict:
    return {
        "E1_kl": window(r["proper"], "kl", *E1_WINDOW),
        "E2_Q": window(r["rollouts"], "Q", *E2_WINDOW),
        "brier": window(r["proper"], "brier", *E1_WINDOW),
        "greedy_Q": window(r["rollouts"], "greedy_Q", *E2_WINDOW),
        "pass_at_32": window(r["rollouts"], "pass_at_k", *E2_WINDOW),
    }


def equal_compute(arm_run, softmax_run, key, points_key, lo, hi) -> float:
    """Arm metric interpolated at softmax's cumulative core seconds, minus softmax, over softmax's window."""
    arm_points = arm_run[points_key]
    xs = np.array([p["core_seconds"] for p in arm_points])
    ys = np.array([p[key] for p in arm_points])
    diffs = []
    for p in softmax_run[points_key]:
        if lo <= p["update"] <= hi:
            diffs.append(float(np.interp(p["core_seconds"], xs, ys)) - p[key])
    return float(np.mean(diffs))


def paired(diffs: list[float]) -> tuple[float, float, float, float, int]:
    d = np.array(diffs)
    n = len(d)
    mean = float(d.mean())
    sd = float(d.std(ddof=1)) if n > 1 else float("nan")
    t = mean / (sd / math.sqrt(n)) if n > 1 and sd > 0 else float("nan")
    p = float(2 * stats.t.sf(abs(t), n - 1)) if n > 1 and sd > 0 else float("nan")
    half = float(stats.t.ppf(0.975, n - 1) * sd / math.sqrt(n)) if n > 1 else float("nan")
    return mean, mean - half, mean + half, p, int((d > 0).sum())


def main() -> None:
    runs = load()
    missing = [(a, s) for s in SEEDS for a in ("softmax", "wick_linear", "wick_real") if (a, s) not in runs]
    print(f"Missing or failed runs: {missing or 'none'}\n")
    complete = [s for s in SEEDS if all((a, s) in runs for a in ("softmax", "wick_linear", "wick_real"))]
    print("| Arm | E1 mean KL 800–2,000 | E2 mean Q 4,000–8,000 | Brier | greedy Q | pass@32 | core s/run | final Δt range |")
    print("|---|---:|---:|---:|---:|---:|---:|---|")
    for arm in ("softmax", "wick_linear", "wick_real"):
        done = [s for s in SEEDS if (arm, s) in runs]
        eps = [endpoints(runs[(arm, s)]) for s in done]
        dts = [x for s in done for layer in runs[(arm, s)]["proper"][-1]["dt"] for x in layer]
        dt_text = f"{min(dts):.3f}–{max(dts):.3f}" if dts else "n/a"
        core = np.mean([runs[(arm, s)]["training_core_seconds"] for s in done])
        print(f"| {arm} (n={len(done)}) | {np.mean([e['E1_kl'] for e in eps]):.4f} | {100 * np.mean([e['E2_Q'] for e in eps]):.2f}% | "
              f"{np.mean([e['brier'] for e in eps]):.4f} | {100 * np.mean([e['greedy_Q'] for e in eps]):.2f}% | "
              f"{100 * np.mean([e['pass_at_32'] for e in eps]):.2f}% | {core:.0f} | {dt_text} |")
    for arm in ("wick_linear", "wick_real"):
        complete = [s for s in SEEDS if (arm, s) in runs and ("softmax", s) in runs]
        print(f"\n## {arm} minus softmax (paired over {len(complete)} seeds: {complete})\n")
        print("| Endpoint | Mean difference | 95% CI | p (two-sided paired t) | seeds with diff > 0 |")
        print("|---|---:|---|---:|---:|")
        results = {}
        for name, key, scale in (("E1 KL (lower better)", "E1_kl", 1), ("E2 Q (pp, higher better)", "E2_Q", 100),
                                 ("Brier (lower better)", "brier", 1), ("greedy Q (pp)", "greedy_Q", 100),
                                 ("pass@32 (pp)", "pass_at_32", 100)):
            diffs = [scale * (endpoints(runs[(arm, s)])[key] - endpoints(runs[("softmax", s)])[key]) for s in complete]
            mean, lo, hi, p, pos = paired(diffs)
            results[key] = (mean, lo, hi, p)
            print(f"| {name} | {mean:+.4f} | [{lo:+.4f}, {hi:+.4f}] | {p:.4f} | {pos}/{len(diffs)} |")
        eq_kl = paired([equal_compute(runs[(arm, s)], runs[("softmax", s)], "kl", "proper", *E1_WINDOW) for s in complete])
        eq_q = paired([100 * equal_compute(runs[(arm, s)], runs[("softmax", s)], "Q", "rollouts", *E2_WINDOW) for s in complete])
        print(f"| equal-compute E1 KL | {eq_kl[0]:+.4f} | [{eq_kl[1]:+.4f}, {eq_kl[2]:+.4f}] | {eq_kl[3]:.4f} | {eq_kl[4]}/{len(complete)} |")
        print(f"| equal-compute E2 Q (pp) | {eq_q[0]:+.4f} | [{eq_q[1]:+.4f}, {eq_q[2]:+.4f}] | {eq_q[3]:.4f} | {eq_q[4]}/{len(complete)} |")
        mech = {u: np.mean([runs[(arm, s)]["mechanism"][u]["policy_tv_dt0_mean"] for s in complete]) for u in ("2000", "8000")}
        att = {u: np.mean([np.mean(runs[(arm, s)]["mechanism"][u]["attention_tv_by_layer"]) for s in complete]) for u in ("2000", "8000")}
        print(f"\nMechanism: attention TV from softmax(S) {att['2000']:.4f} (2k) / {att['8000']:.4f} (8k); "
              f"policy TV vs Δt=0 {mech['2000']:.4f} (2k) / {mech['8000']:.4f} (8k)")
        if arm == "wick_linear":
            e1_improves = results["E1_kl"][0] < 0
            e2_improves = results["E2_Q"][0] > 0
            ps = sorted([(results["E1_kl"][3], "E1"), (results["E2_Q"][3], "E2")])
            holm = {}
            for rank, (p, name) in enumerate(ps):
                holm[name] = p <= 0.05 / (2 - rank) and (rank == 0 or holm[ps[0][1]])
            sig_improve = {"E1": holm["E1"] and e1_improves, "E2": holm["E2"] and e2_improves}
            harm = {"E1": results["E1_kl"][1] > 0, "E2": results["E2_Q"][2] < 0}  # CI entirely on harmful side
            helps = (sig_improve["E1"] and not harm["E2"]) or (sig_improve["E2"] and not harm["E1"])
            print(f"\n**Decision (spec rule): Holm-significant improvement {sig_improve}; "
                  f"significant harm {harm}; wick_linear helps = {helps}**")


if __name__ == "__main__":
    main()
