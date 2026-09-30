"""Summarise Stage D against the tests fixed in stage-d-spec.md."""

from __future__ import annotations

import json
from math import comb
from pathlib import Path

RESULTS = Path(__file__).resolve().parent / "results"
SOLVED = 0.95
PROBES = {"P1": (16, list(range(100, 130))), "P2": (24, list(range(200, 220)))}
ORDER = ("softmax", "softmax_t2", "sqrt_softmax", "maa_p2", "maa_p11", "sigmoid", "c1_wick", "wick_real", "wick_linear")
PRIMARY = {"H1": ("sqrt_softmax", "softmax"), "H2": ("c1_wick", "softmax")}
DECOMPOSITION = {
    "D1": ("sqrt_softmax", "softmax_t2"), "D2": ("sqrt_softmax", "maa_p2"), "D3": ("sqrt_softmax", "maa_p11"),
    "D4": ("sqrt_softmax", "sigmoid"), "D5": ("c1_wick", "wick_real"), "D6": ("c1_wick", "wick_linear"),
    "D7": ("c1_wick", "sqrt_softmax"),
}


def sign_test(wins: int, losses: int) -> float:
    """Exact two-sided sign test on discordant pairs."""
    n = wins + losses
    if n == 0:
        return 1.0
    tail = sum(comb(n, i) for i in range(min(wins, losses) + 1)) / 2 ** n
    return min(1.0, 2 * tail)


def load() -> dict:
    runs = {}
    for path in RESULTS.glob("*.json"):
        r = json.loads(path.read_text())
        runs[(r["length"], r["variant"], r["seed"])] = r
    return runs


def solved(run: dict) -> bool:
    return run["curve"][-1]["accuracy"] >= SOLVED


def contrast(runs, length, seeds, a, b):
    common = [s for s in seeds if (length, a, s) in runs and (length, b, s) in runs]
    wins = sum(solved(runs[(length, a, s)]) and not solved(runs[(length, b, s)]) for s in common)
    losses = sum(solved(runs[(length, b, s)]) and not solved(runs[(length, a, s)]) for s in common)
    return wins, losses, len(common), sign_test(wins, losses)


def main() -> None:
    runs = load()
    primary_p = {}
    for probe, (length, seeds) in PROBES.items():
        print(f"\n## {probe} (parity k=3, L={length}, seeds {seeds[0]}–{seeds[-1]})\n")
        print("| Variant | Solved | Window accuracy | Final Δt (range) | Mean seconds/run |")
        print("|---|---:|---:|---|---:|")
        for v in ORDER:
            rows = [runs[(length, v, s)] for s in seeds if (length, v, s) in runs]
            if not rows:
                continue
            dts = [x for r in rows for layer in (r["curve"][-1].get("dt") or []) for x in layer]
            dt_text = f"{min(dts):.3f}–{max(dts):.3f}" if dts else "n/a"
            print(f"| {v} | {sum(map(solved, rows))}/{len(rows)} | "
                  f"{100 * sum(r['window_accuracy'] for r in rows) / len(rows):.2f}% | {dt_text} | "
                  f"{sum(r['seconds'] for r in rows) / len(rows):.0f} |")
        print("\n| Test | A vs B | A-only solves | B-only solves | Paired seeds | Sign-test p |")
        print("|---|---|---:|---:|---:|---:|")
        for name, (a, b) in {**PRIMARY, **DECOMPOSITION}.items():
            w, l, n, p = contrast(runs, length, seeds, a, b)
            if n:
                print(f"| {name} | {a} vs {b} | {w} | {l} | {n} | {p:.4f} |")
                if name in PRIMARY:
                    primary_p[(probe, name)] = (w, l, n, p)
    print("\n## Primary decisions\n")
    p1 = {h: primary_p.get(("P1", h)) for h in PRIMARY}
    ranked = sorted((v[3], h) for h, v in p1.items() if v)
    holm_pass = {}
    for rank, (p, h) in enumerate(ranked):
        threshold = 0.05 / (len(ranked) - rank)
        holm_pass[h] = p <= threshold and all(holm_pass.get(prev, False) for _, prev in ranked[:rank])
        if not holm_pass[h]:
            for _, rest in ranked[rank + 1:]:
                holm_pass[rest] = False
            break
    for h, (a, b) in PRIMARY.items():
        first = p1.get(h)
        second = primary_p.get(("P2", h))
        passes_p1 = bool(first) and holm_pass.get(h, False) and first[0] > first[1]
        passes_p2 = bool(second) and second[3] < 0.05 and second[0] > second[1]
        print(f"- {h} ({a} > {b}): P1 Holm pass = {passes_p1}; P2 replication = {passes_p2}; "
              f"**confirmed = {passes_p1 and passes_p2}**")


if __name__ == "__main__":
    main()
