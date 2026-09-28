# Stage 1b specification: C4, C3 and the exploratory Δt = 0.25 check

2026-09-28. Written and committed before any C4 or C3 results existed. The
code is `schrodinger/quantum_components.py` (all tests pass), and the model
and training settings are as in `stage1-spec.md`. The three experiments run in
this order: (A) C4, (B) C3, (C) Δt initialised at 0.25.

## Changes to the probes

- **Exclude has been recalibrated, using softmax only on calibration seed 999**
  (the old L=16 setting was a floor).
  - L=16: stuck at 0.75 with 2 layers after 5,000 steps, and with d=64.
  - L=8: saturates (1.0 by step 2,500).
  - **L=12, 2 layers, 3,000 steps, evaluation every 250** (chosen): stuck on
    the heuristic plateau (0.731 on the held-out set) until about 2,250
    steps, then escapes to 0.999. Window accuracy is 0.807.
- **Parity (k=3, L=16, 1,500 steps) uses 10 seeds (0–9)**, and its endpoint is
  now the solve count, because Stage 1 showed outcomes are all-or-nothing. A
  seed counts as solved when final held-out accuracy is at least 0.95.
- **Order** keeps its Stage 1 settings (L=16, 600 steps,
  evaluation every 50) and seeds 0–4.
- Seeds 0–4 reuse the committed softmax and c1 results for order and parity.
  A rerun of `order c1 seed 0` reproduced the committed curve exactly.

## Variants

**C4 (amplitude-level value mixing).**

- `c4`: complex amplitudes from C1's unitary mix complex values.
- Twins, all with identical parameter counts:
  - `c4_magnitude`: the same amplitudes' magnitudes, so no cancellation.
  - `c4_real`: signed real coefficients, which can cancel classically.
  - `c4_wick`: imaginary time.
  - `c4_dephased`: classical transition.
- All C4 variants use √p coefficients at Δt = 0.
- Controls for C4: softmax, c1 and the four twins.

**C3 (Trotterised dephasing knob).**

- K = 2 substeps of dephase-then-evolve, with a learned per-head λ.
- K was reduced from 4 to 2 for speed before any C3 run; the substep order
  (dephase first) was fixed by a failing unit test before any run.
- Twins:
  - coherent (λ = 0), which is exactly `c1`;
  - `c3_classical` (λ = 1), a Markov chain.
- `c3` has 1 extra scalar per head (2 per layer).
- Controls for C3: softmax, c1 and c3_classical.

## Endpoints and pass rules

Comparisons are paired within each seed.

- **Parity:** C beats a control X if (seeds C solves and X does not) minus
  (seeds X solves and C does not) is at least 3, **and** C solves at least 5
  of 10.
- **Order and exclude:** window accuracy (second half of training). C beats X
  if the paired difference is positive in at least 4 of 5 seeds and the mean
  is at least 1 pp.

**C4:**

- **Designated probe: parity**, on the theory that signed pairwise
  interactions need outputs outside the convex hull.
- **C4 passes** if it beats every control on parity.
- Order and exclude are secondary.

**C3:**

- There is no probe designated on theoretical grounds, so C3 passes a probe if
  it beats all of its controls on it. There are three chances, and this
  multiplicity is disclosed.
- **C3 carries forward** only if it passes at least one probe **and** its
  learned λ ends in (0.05, 0.95) for at least 80% of heads across its seeds
  (the coherence knob settled away from both limits).
- The λ trajectories are reported in full whatever the outcome.

**Experiment C:** this is **exploratory and outcome-motivated**. It reruns
order and parity (seeds 0–4) with Δt initialised at 0.25 for c1,
c1_phasefree, c1_wick and c1_dephased; softmax is unaffected. It applies the
Stage 1 rules as a description, not as a pass or fail gate. It also reports
whether Δt moves.

## Environment

As in `stage1-spec.md`: Python 3.11, torch 2.14.0+cpu, 2 threads per process,
at most 2 processes at a time on 4 CPUs.
