"""Summarise Stage 1b (C4, C3, Δt = 0.25) against the rules in stage1b-spec.md."""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

RESULTS = Path(__file__).resolve().parent / "results"
SOLVED = 0.95
EXPERIMENTS = {
    "A: C4": ("c4", ("softmax", "c1", "c4_magnitude", "c4_real", "c4_wick", "c4_dephased"), 0.05),
    "B: C3": ("c3", ("softmax", "c1", "c3_classical"), 0.05),
    "C: Δt 0.25 (exploratory)": ("c1", ("softmax", "c1_phasefree", "c1_wick", "c1_dephased"), 0.25),
}
GROUPS = (("order", 2, 16), ("parity", 3, 16), ("exclude", 2, 12))


def load() -> dict:
    runs: dict = defaultdict(dict)
    for path in RESULTS.glob("*.json"):
        r = json.loads(path.read_text())
        key = (r["probe"], r["k"], r["length"], r.get("dt_init", 0.05))
        runs[key][(r["variant"], r["seed"])] = r
    return runs


def final_scalar(run: dict, name: str) -> list[float]:
    values = run["curve"][-1].get(name)
    return [x for layer in values for x in layer] if values else []


def compare(runs: dict, probe: str, target: str, control: str, seeds: list[int]) -> tuple[str, bool]:
    if probe == "parity":
        both = [s for s in seeds if (target, s) in runs and (control, s) in runs]
        solved = lambda v, s: runs[(v, s)]["curve"][-1]["accuracy"] >= SOLVED  # noqa: E731
        wins = sum(solved(target, s) and not solved(control, s) for s in both)
        losses = sum(solved(control, s) and not solved(target, s) for s in both)
        target_solves = sum(solved(target, s) for s in both)
        ok = len(both) == 10 and wins - losses >= 3 and target_solves >= 5
        return f"{wins}–{losses} discordant, target solves {target_solves}/{len(both)}", ok
    both = [s for s in seeds if (target, s) in runs and (control, s) in runs]
    diffs = [100 * (runs[(target, s)]["window_accuracy"] - runs[(control, s)]["window_accuracy"]) for s in both]
    mean = sum(diffs) / len(diffs) if diffs else float("nan")
    positive = sum(d > 0 for d in diffs)
    ok = len(diffs) == 5 and positive >= 4 and mean >= 1.0
    return f"{mean:+.2f} pp, {positive}/{len(diffs)} positive", ok


def main() -> None:
    runs = load()
    for name, (target, controls, dt_init) in EXPERIMENTS.items():
        print(f"\n# Experiment {name}\n")
        passed_probes = []
        for probe, k, length in GROUPS:
            group = dict(runs.get((probe, k, length, dt_init), {}))
            if dt_init != 0.05:  # softmax is unaffected by dt_init; reuse its 0.05 runs
                for key, run in runs.get((probe, k, length, 0.05), {}).items():
                    if key[0] == "softmax":
                        group[key] = run
            if not any(v == target for v, _ in group):
                continue
            seeds = sorted({s for v, s in group if v == target})
            print(f"## {probe} (k={k}, L={length}, Δt init {dt_init})\n")
            print("| Variant | Window accuracy | Solved (final ≥ 0.95) | Final Δt (range) | Final λ (range) |")
            print("|---|---:|---:|---|---|")
            for variant in (target,) + controls:
                rows = [group[(variant, s)] for s in seeds if (variant, s) in group]
                if not rows:
                    continue
                window = sum(r["window_accuracy"] for r in rows) / len(rows)
                solved = sum(r["curve"][-1]["accuracy"] >= SOLVED for r in rows)
                dts = [x for r in rows for x in final_scalar(r, "dt")]
                lams = [x for r in rows for x in final_scalar(r, "lambda")]
                dt_text = f"{min(dts):.3f}–{max(dts):.3f}" if dts else "n/a"
                lam_text = f"{min(lams):.3f}–{max(lams):.3f}" if lams else "n/a"
                print(f"| {variant} | {100 * window:.2f}% | {solved}/{len(rows)} | {dt_text} | {lam_text} |")
            print(f"\n| {target} against | Result | Beats? |\n|---|---|---|")
            oks = []
            for control in controls:
                text, ok = compare(group, probe, target, control, seeds)
                oks.append(ok)
                print(f"| {control} | {text} | {'yes' if ok else 'no'} |")
            verdict = all(oks)
            if verdict:
                passed_probes.append(probe)
            print(f"\n{target} beats every control on {probe}: {'YES' if verdict else 'NO'}\n")
            if target == "c3":
                lams = [x for s in seeds if ("c3", s) in group for x in final_scalar(group[("c3", s)], "lambda")]
                interior = sum(0.05 < x < 0.95 for x in lams)
                print(f"Learned λ in (0.05, 0.95): {interior}/{len(lams)} heads\n")
        print(f"**Probes where {target} beats every control: {passed_probes or 'none'}**")


if __name__ == "__main__":
    main()
