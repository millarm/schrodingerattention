# Stage 1 results: component C1

2026-09-27. Spec: `stage1-spec.md` (committed in e1c1a1d, before the main
runs). Raw results: `results/*.json`. The tables come from `summarize.py`.
There were 75 runs (3 probes × 5 variants × seeds 0–4), and all completed.

## Verdict: C1 does not pass. It does not carry into Stage 2.

Under the pre-set rule, C1 had to beat each of softmax and the three twins
in at least 4 of 5 seeds, by at least 1 pp on average. It failed that rule on
every probe, including its designated probe (order).

| Probe | softmax | **c1** | phase-free | imaginary-time (Wick) | dephased | C1 passes? |
|---|---:|---:|---:|---:|---:|---|
| order (designated) | 94.35% | 96.07% | 95.74% | 96.59% | 96.09% | no |
| parity, k=3 | 60.17% | 65.04% | 61.02% | 68.54% | 61.02% | no |
| exclude | 75.05% | 75.05% | 75.05% | 75.05% | 75.05% | no |

Values are window-averaged held-out accuracy, as the mean over seeds.

C1's paired differences:

- **order:** +1.72 pp against softmax (2/5 seeds positive); +0.33 against
  phase-free; −0.51 against Wick; −0.01 against dephased.
- **parity:** +4.87 pp against softmax (1/5 positive); +4.02 against
  phase-free and dephased; −3.50 against Wick.
- **exclude:** 0.00 against every control.

## Observations

- **Where the quantum variants help on order, the classical twins help just
  as much.** All four quantum variants average about 96%, against 94.35% for
  softmax, entirely because of seeds 0 and 1 (the other seeds reach 100%).
  The gain comes from the extra mixing step, not from interference or
  unitarity. The imaginary-time twin is the best variant.
- **Parity outcomes are all-or-nothing per seed.** At the final step, seeds
  that solve parity are at 100% and the rest are at chance. Softmax solves
  1/5, C1 2/5, the Wick twin 2/5 (plus one partial), and the phase-free and
  dephased twins 1/5 each. Five seeds cannot separate these. A window mean is
  also a poor endpoint for an all-or-nothing outcome: a future spec should use
  the solve rate over more seeds.
- **Exclude was a floor, and is uninformative.** Every variant and seed stayed
  exactly at the 0.75 majority-vote heuristic, with identical cross-entropy.
  The calibration mistake: I took softmax's 0.75 as "good difficulty" when it
  meant nothing learned the rule within the budget. The probe needs
  recalibrating, with more steps or a larger model, until softmax clearly
  exceeds 0.75 in some seeds, before it can separate components.
- **Δt still barely moves, even under C1.** Final Δt stays at 0.036–0.058
  against an initial 0.05 for every quantum variant on every probe. C1 removes
  the second-order suppression, so its Δt gradient is first order, and Adam
  would move raw Δt by about 1.5 over 1,500 steps if that gradient had a
  consistent sign. The optimizer still finds no consistent benefit in more
  evolution. This matches the route-model diagnostic.

## What this means for the plan

- C1 is closed as a standalone component. On these probes, restoring the
  antisymmetric part of the scores adds nothing that classical mixing doesn't
  already provide.
- **Exploratory, not preregistered:** the Δt initialisation (0.05) may keep
  every variant close to softmax. One cheap check would rerun order and parity
  with Δt initialised at 0.25 for all quantum variants and twins alike. It
  would be labelled outcome-motivated, and C1 still needs to beat its twins.
- Next components, per the plan's reasoning:
  - C4 (amplitude-level value mixing) is the one that can theoretically escape
    the convex hull, so it is the natural candidate for parity and a
    recalibrated exclude.
  - C3 (learned dephasing κ) gives a direct readout of whether coherence is
    used at all.
- Stage 2 (the map benchmark) waits until some component passes Stage 1.

## Cost

C1 and its twins ran about 4–5.5× slower than softmax per step (for
example, order: about 25 s against 5–7 s for 600 steps; parity: about 60 s against 13 s; exclude, 2 layers:
about 117 s against 21 s). That cost comes from one complex 17×17 matrix
exponential per head and example.
