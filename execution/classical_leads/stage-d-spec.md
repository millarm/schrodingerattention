# Stage D specification: decomposing the two classical leads

2026-09-28. Written and committed **before any Stage D run**. The only Stage D
executions so far are softmax-only calibration runs on calibration seeds
900–904, listed below.

Stage 1b (`execution/quantum_components/stage1b-results.md`) found no
quantum-specific benefit, but it produced two leads:

- **L1, the √p readout.** Mixing values with √softmax(S) instead of
  softmax(S). Parity was solved in 6/10 seeds, against 1/10 for softmax.
- **L2, imaginary-time score-operator mixing** (`c1_wick` at Δt initialised to
  0.25). Parity was solved in 5/5 seeds, against 1/5 (exploratory).

Both leads came from the parity probe with seeds 0–9, so **those seeds and
that result cannot confirm them.** Stage D tests them on fresh seeds, on one
probe that was not used to find them, and against the published mechanisms
they resemble.

## Prior work that sets the comparison (checked 2026-09-28)

- **Mass-Aware Attention (MAA)**, Yu and Ha, arXiv 2607.22781, July 2026. It
  divides attention mass by its Lp norm rather than its L1 norm, so the output
  magnitude keeps how many keys contribute.
  - √softmax(S) is exactly MAA with p = 2 at temperature 2:
    √p_j = e^(S_j/2) / ‖e^(S/2)‖₂.
  - MAA recommends p ≈ 1.1, chosen by validation over {1, …, 1.3}. It reports
    that its gains disappear at p = 2 on its tasks.
  - **L1 is therefore not a new mechanism.** At most the new points are that a
    Born-rule argument lands on p = 2, and that p = 2 can help on
    compositional probes.
- **Sigmoid attention**, Ramapuram et al., ICLR 2025 (arXiv 2409.04431). The
  standard unnormalised replacement, with bias −log L.
- **Diffusion or heat-kernel attention**: diffusion-map views of softmax
  (arXiv 2604.09560), heat-kernel diffusion attention (SSRN 5953096) and
  multi-hop attention diffusion (Diffuser, arXiv 2210.11794).
  - L2 belongs to this family.
  - Its particular form may be distinctive: √p amplitudes evolved by e^(−ΔtH)
    with a complex Hermitian H that includes the scores' antisymmetric part,
    then squared and normalised.
  - L2's novelty depends on the complex part mattering, which D5 tests.

## Variants

All variants use the same `ProbeEncoder`, the same Q/K/V/O projections and the
same parameter count as softmax (tested). The code is in
`schrodinger/quantum_components.py`. Readout variants use softmax's α/β
scalars. Operator variants use α and a learned Δt initialised at 0.25; in
every earlier run Δt stayed close to its initial value.

| Variant | Weights / coefficients applied to V | Role |
|---|---|---|
| `softmax` | softmax(S) | baseline |
| `softmax_t2` | softmax(S/2) | temperature only (normalised √p) |
| `sqrt_softmax` | √softmax(S) = MAA p=2 at T=2 | **L1** |
| `maa_p2` | softmax(S)/‖softmax(S)‖₂ | MAA p=2 at T=1 |
| `maa_p11` | softmax(S)/‖softmax(S)‖₁.₁ | MAA's recommended setting |
| `sigmoid` | σ(S − log L) | standard unnormalised baseline |
| `c1_wick` | normalise \|√p · e^(−ΔtH)ᵀ\|², H complex Hermitian | **L2** |
| `wick_real` | same, H real symmetric (no antisymmetric part) | is the complex part needed? |
| `wick_linear` | same, with first-order propagator I − ΔtH | is the exponential needed? |

## Probes and seeds

- **P1, confirmation.** Parity, k=3, L=16, 1,500 steps, the settings in which
  the leads were found. **Fresh seeds 100–129 (30).** Endpoint: solved
  (final held-out accuracy ≥ 0.95).
- **P2, held-out probe.** Parity, k=3, **L=24**, 3,000 steps, evaluation
  every 250. **Fresh seeds 200–219 (20).** Same endpoint.
  - Calibrated on softmax only, calibration seeds 900–904: L=24 solves 1/5 at
    3,000 steps and 0/5 at 1,500.
  - The rule was the smallest budget in {1,500, 3,000} at which softmax
    solves at least 1/5.
  - Rejected settings: L=32 k=3 (softmax 0/5 at 3,000 steps) and L=32 k=2
    (5/5 by 1,500 steps).
- All other training settings are as in Stage 1: d=32, 2 heads, 1 layer,
  AdamW lr 1e-3, weight decay 0.01, clipping at 1.0, batch 128, 2,048
  held-out examples, 2 torch threads.

## Hypotheses and tests

Comparisons are paired within each seed, since shared initialisation and a
shared data stream are tested. Each test is an exact two-sided sign test on
the discordant seeds (A solves and B does not, against B solves and A does
not).

**Primary (P1), with Holm correction across the two, family α = 0.05:**

- **H1:** `sqrt_softmax` solves more seeds than `softmax`.
- **H2:** `c1_wick` solves more seeds than `softmax`.

**Replication (P2):** each primary hypothesis that passes on P1 must also show
more solved seeds than softmax on P2, with two-sided sign test p < 0.05. **A
lead counts as confirmed only if it passes both.**

**Decomposition** (secondary: reported with sign-test p-values on P1 and P2,
not used to gate):

- **D1** `sqrt_softmax` vs `softmax_t2`: does the L2 gain matter beyond the
  temperature?
- **D2** `sqrt_softmax` vs `maa_p2`: temperature within MAA p=2.
- **D3** `sqrt_softmax` vs `maa_p11`: against the published recommended setting.
- **D4** `sqrt_softmax` vs `sigmoid`.
- **D5** `c1_wick` vs `wick_real`: is the complex, antisymmetric part needed?
- **D6** `c1_wick` vs `wick_linear`: is the full exponential needed?
- **D7** `c1_wick` vs `sqrt_softmax`: which lead is stronger?

Also reported: window-averaged accuracy and cross-entropy, final Δt, and
wall-clock cost per variant.

**Interpretation rules, fixed in advance:**

- If D1 shows no difference, L1's gain is a temperature effect and not the
  magnitude, or count, channel.
- If `maa_p11` matches `sqrt_softmax`, L1 adds nothing beyond MAA.
- If D5 shows no difference, L2 is plain diffusion attention (real kernel)
  and the Hermitian construction adds nothing.

## Stage 2: the map benchmark (conditional)

Stage 2 runs only for a lead confirmed on both P1 and P2.

- **Feasibility is established.** The pool-512 training data (32,946 states,
  1,024 problems) was regenerated with the repository's frozen pipeline
  (`regenerate_route_data.py`). Pools, inventory and ranking match the
  committed manifest byte-for-byte. Validation and test files match their
  committed copies apart from a wall-clock `elapsed_seconds` field.
  `verify_training_bank.py` reproduces the training bank's `selected_hash`
  recorded by every committed route-policy run (`8879d863…`).
- **Design outline,** to be fixed in a separate spec committed before any
  Stage 2 run:
  - The unchanged `RoutePolicy` architecture, with only the attention module
    swapped, in a new module (`route_policy.py` stays hash-pinned).
  - The same data, optimizer, batch stream and evaluation.
  - Fresh seed pairs, sized from a precision target after a variance pilot.
  - Primary endpoints: window-averaged validation KL and Brier over a
    predeclared early window, plus window-averaged Q.
  - Equal-compute results reported next to equal-update ones.
  - No final-test access.

## Resources and stopping

- The estimated cost is about 8 CPU-hours: P1 about 2.3 h and P2 about 5.5 h.
  At 2 processes with 2 threads each, that is about 4 hours of wall time.
- If neither lead is confirmed, Stage D closes with a bounded negative result
  and Stage 2 does not run.
- A seed that fails technically is reported, not replaced.
