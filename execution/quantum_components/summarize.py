"""Summarise Stage 1 probe results against the pass rule in stage1-spec.md."""

from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path

RESULTS = Path(__file__).resolve().parent / "results"
CONTROLS = ("softmax", "c1_phasefree", "c1_wick", "c1_dephased")


def main() -> None:
    runs: dict[str, dict[str, dict[int, dict]]] = defaultdict(lambda: defaultdict(dict))
    for path in sorted(RESULTS.glob("*.json")):
        result = json.loads(path.read_text())
        runs[result["probe"]][result["variant"]][result["seed"]] = result
    for probe, variants in runs.items():
        print(f"\n## {probe}\n")
        print("| Variant | Window accuracy (mean over seeds) | Per seed | Window CE | Final Δt (layer-0 heads) |")
        print("|---|---:|---|---:|---|")
        for variant, seeds in variants.items():
            accuracy = [seeds[s]["window_accuracy"] for s in sorted(seeds)]
            ce = [seeds[s]["window_ce"] for s in sorted(seeds)]
            dt = seeds[min(seeds)]["curve"][-1].get("dt")
            dt_text = ", ".join(f"{x:.3f}" for x in dt[0]) if dt else "n/a"
            print(f"| {variant} | {100 * sum(accuracy) / len(accuracy):.2f}% | "
                  f"{' '.join(f'{100 * a:.1f}' for a in accuracy)} | {sum(ce) / len(ce):.4f} | {dt_text} |")
        if "c1" not in variants:
            continue
        print("\n| C1 minus | Mean paired difference (pp) | Seeds positive | Passes |")
        print("|---|---:|---:|---|")
        passes = []
        for control in CONTROLS:
            if control not in variants:
                continue
            common = sorted(set(variants["c1"]) & set(variants[control]))
            diffs = [100 * (variants["c1"][s]["window_accuracy"] - variants[control][s]["window_accuracy"])
                     for s in common]
            mean = sum(diffs) / len(diffs)
            positive = sum(d > 0 for d in diffs)
            ok = positive >= 4 and mean >= 1.0 and len(diffs) == 5
            passes.append(ok)
            print(f"| {control} | {mean:+.2f} | {positive}/{len(diffs)} | {'yes' if ok else 'no'} |")
        print(f"\nC1 passes {probe}: {'YES' if passes and all(passes) else 'NO'}")


if __name__ == "__main__":
    sys.exit(main())
