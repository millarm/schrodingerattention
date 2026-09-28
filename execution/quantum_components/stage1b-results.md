# Stage 1b results

Spec: `stage1b-spec.md` (committed in 0f7e51c, before any C3 or C4 run).
Tables: `summarize_b.py`. Raw results: `results/*.json`. Experiments ran in
the specified order, A → B → C.

## A. C4 (amplitude-level value mixing): does not pass

**Verdict under the pre-set rule: C4 fails on its designated probe (parity) and
on both secondary probes.**

| Probe | softmax | c1 | **c4** | c4_magnitude | c4_real | c4_wick | c4_dephased |
|---|---:|---:|---:|---:|---:|---:|---:|
| parity, solved / 10 | 1 | 3 | **6** | 6 | 6 | 6 | 6 |
| parity, window accuracy | 60.07% | 66.14% | **80.09%** | 80.09% | 80.09% | 80.14% | 80.08% |
| order, window accuracy (5 seeds) | 94.35% | 96.07% | **99.91%** | 99.91% | 100.00% | 99.89% | 99.99% |
| exclude, window accuracy (5 seeds) | 73.14% | 73.14% | 73.14% | 73.14% | 73.14% | 73.14% | 73.14% |

- **Parity:** C4 beats softmax (5–0 discordant seeds) and C1 (3–0). Against
  every C4 twin it is 0–0 discordant: the same seeds solve.
- **Order:** every C4 variant is near 100%. C4 is +5.6 pp against softmax,
  but positive in only 2/5 seeds (the others are at the 100% ceiling for
  both), so it fails the rule. Against its twins it is ±0.1 pp.
- **Exclude:** every variant and seed sat at the 0.731 heuristic plateau. The
  recalibrated setting escaped on calibration seed 999 at about 2,250 steps,
  but on none of seeds 0–4 within 3,000 steps. Calibrating on one seed was not
  enough, so exclude is uninformative again.

### What actually produced the gain

Δt stayed at 0.035–0.064 in every variant, close to its initial 0.05. At
Δt ≈ 0 every C4 variant reduces to the same classical readout,
out = Σ_j √p_j v_j, with coefficients √p instead of p. The twins differ from
C4 only through evolution, which the optimizer did not use. So the large gain
over softmax is **not quantum**. It comes from the square-root readout shared
by C4 and all its classical twins.

That readout has a simple classical interpretation:
√p_j = exp(S_j / 2) / √Z. The output is therefore softmax at temperature 2,
multiplied by an input-dependent gain Σ_j √p_j, which ranges from 1 (sharp
attention) to √L (uniform attention). Softmax normalisation throws away how
many keys a query attends to. The √p gain keeps that information, which is
plausibly why parity and order become easier. This is a known kind of
limitation of normalised attention, and it is fixable classically.

### Follow-up (exploratory, not preregistered)

A direct test is a `sqrt_softmax` baseline, out = Σ √p_j v_j with no
evolution at all. It is cheap (softmax speed). It will be added after the
Stage 1b queue finishes, so the attention module isn't edited while queued
jobs are importing it. If it matches C4, the attribution above is confirmed.

## B. C3 (Trotterised dephasing knob): does not pass

**Verdict under the pre-set rule: C3 beats all of its controls (softmax, c1 =
coherent twin, c3_classical) on none of the three probes, so it does not carry
forward.**

| Probe | softmax | c1 (λ = 0) | **c3 (learned λ)** | c3_classical (λ = 1) |
|---|---:|---:|---:|---:|
| order, window accuracy (5 seeds) | 94.35% | 96.07% | **96.02%** | 94.96% |
| parity, solved / 10 | 1 | 3 | **3** | 2 |
| parity, window accuracy | 60.07% | 66.14% | **64.19%** | 62.26% |
| exclude, window accuracy (5 seeds) | 73.14% | 73.14% | 73.14% | 73.14% |

- **order:** +1.66 pp against softmax (2/5 positive); −0.06 against c1;
  +1.05 against c3_classical (2/5).
- **parity:** 2–0 discordant against softmax, 0–0 against c1 and 2–1 against
  c3_classical. C3 solves only 3/10, below the 5/10 floor.
- **exclude:** the floor again (see A).

### The λ readout was uninformative

The spec's second condition, learned λ in (0.05, 0.95) for at least 80% of
heads, is met (50/50 heads). **It is met vacuously.** λ started at 0.5 and
ended at 0.385–0.523, so it barely moved. Δt again stayed at 0.047–0.068, and
with that little evolution, dephasing changes the weights by almost nothing,
so λ gets almost no gradient. The criterion should have required λ to *move*
from its initial value, not just to end up in the interior. This is recorded
as a design error in the spec, not as evidence that the network uses
coherence.

C3 cost about 4× C1 per step (K=2 density-matrix substeps).

## C. Δt initialised at 0.25 (exploratory, outcome-motivated)

This experiment is a description, not a gate. It uses seeds 0–4, with softmax
taken from its Δt-independent runs.

| Probe | softmax | c1 | c1_phasefree | **c1_wick** | c1_dephased |
|---|---:|---:|---:|---:|---:|
| parity, solved / 5 | 1 | 2 | 2 | **5** | 1 |
| parity, window accuracy | 60.17% | 70.10% | 66.79% | **100.00%** | 61.58% |
| order, window accuracy | 94.35% | 100.00% | 98.36% | **100.00%** | 95.42% |
| final Δt range | n/a | 0.238–0.270 | 0.239–0.333 | 0.240–0.281 | 0.233–0.262 |

- **C1 still does not beat its twins.** On parity it is 0–3 discordant against
  the imaginary-time twin. On order it ties that twin at 100%, and is +1.6 pp
  against phase-free and +4.6 pp against dephased, but positive in only 2/5
  seeds each.
- **The imaginary-time twin solves parity in every seed**, 4–0 discordant
  against softmax, and is the best variant on both probes. With 5 seeds and an
  outcome-motivated setting, this is a lead, not a result.
- **Δt moves little from wherever it starts** (0.05 in Stage 1, 0.25 here).
  The optimizer does not tune the evolution time. In practice its
  initialisation is a fixed hyperparameter, and it matters.

**What "imaginary-time" means here.** The twin replaces e^(−iΔtH) with
e^(−ΔtH), then renormalises. That removes unitarity, but with C1's complex
Hermitian H the propagator and amplitudes are still complex, and the |·|²
readout still combines complex terms. It is a non-unitary, score-derived
mixing operator, **not** a classical stochastic kernel. Whether the gain needs
the complex (antisymmetric) part of H is open. The phase-free version of this
operator (real symmetric H) is the natural test.

## Overall Stage 1b conclusion

1. **No quantum-specific benefit.** None of C1, C3 or C4 beats its twins under
   its pre-set rule. Where a quantum variant does well, a twin without
   unitarity or interference does as well or better.
2. **The optimizer does not use the quantum knobs.** Δt and λ stay close to
   initialisation in every run, so the "coherence" parameters behave as
   fixed hyperparameters, not learned ones.
3. **Two non-quantum attention changes look genuinely useful on these
   probes:**
   - **The √p readout (C4 at Δt ≈ 0):** parity 6/10 solved, against 1/10 for
     softmax (5–0 discordant; two-sided sign-test p ≈ 0.06).
   - **Imaginary-time score-operator mixing at Δt = 0.25:** parity 5/5
     against 1/5 (exploratory).

   Both keep information that softmax normalisation discards. Neither needs
   anything quantum.
4. **Exclude remained a floor** on every evaluation seed. It needs a
   multi-seed calibration before it can be used.

A decomposition study of both leads should be specified before any further
runs: √p against softmax(S/2) against softmax × gain, imaginary time with
real against complex H, and sigmoid attention as the standard unnormalised
baseline. It needs 20–30 seeds, a literature check, and then the unchanged
map benchmark.
