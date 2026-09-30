# Stage D results

Spec: `stage-d-spec.md` (committed in 629dc94, before any Stage D run). Tables
come from `summarize_d.py`; raw results are in `results/*.json`.

**Execution note.** A logging bug in `probes.py` (it read Δt from variants that
have none) crashed the first P1 readout jobs after two softmax runs. It was
fixed in d74b48c, which changes logging only, and the whole P1 readout batch
was rerun: 6 variants × 30 seeds. That rerun overlapped with the queued
operator jobs, so the `wick_linear` wall-clock times below are inflated by CPU
contention. Accuracy is unaffected, since runs are deterministic per seed.

## P1: confirmation probe (parity k=3, L=16, fresh seeds 100–129)

| Variant | Solved / 30 | Window accuracy |
|---|---:|---:|
| softmax | 4 | 58.38% |
| softmax_t2 | 0 | 50.24% |
| sqrt_softmax (L1) | 7 | 61.76% |
| maa_p2 | 8 | 73.34% |
| maa_p11 | 6 | 62.15% |
| sigmoid | 0 | 49.96% |
| **c1_wick (L2)** | **30** | **99.44%** |
| wick_real | 30 | 99.30% |
| wick_linear | 30 | 98.89% |

Primary tests (exact two-sided sign test on discordant seeds; Holm correction
across H1 and H2):

- **H1, sqrt_softmax > softmax: 5–2, p = 0.45. Not supported.** The Stage 1b
  signal (6/10 against 1/10) does not reproduce on fresh seeds.
- **H2, c1_wick > softmax: 26–0, p = 3.0 × 10⁻⁸. Passes on P1** and awaits
  replication on P2.

Decomposition (secondary):

- **D1**, sqrt_softmax against softmax_t2: 7–0, p = 0.016. Among these weak
  readouts, the L2-norm gain does better than plain temperature 2, which
  solves nothing. The overall L1 effect against softmax is still not
  established.
- **D2 and D3** (MAA p=2 and p=1.1): no difference from sqrt_softmax (1–2 and
  5–4). **L1 is no better than the published Mass-Aware Attention.**
- **D4**, sqrt_softmax against sigmoid: 7–0, p = 0.016. Sigmoid attention
  solved nothing.
- **D5 and D6**, c1_wick against wick_real and against wick_linear: 0–0 in
  both. **The complex (antisymmetric) part of H and the full matrix
  exponential are both unnecessary.** The minimal form works equally well:
  real H and the first-order propagator.
- **D7**, c1_wick against sqrt_softmax: 23–0, p ≈ 2 × 10⁻⁷.

### What L2 reduces to

With real H and a first-order propagator, the weights are

  a = √softmax(S),  a′ = a − Δt · a Hᵀ,  A = |a′|² / Σ|a′|²,
  H = (S + Sᵀ) / (2√L),  Δt ≈ 0.25 (not tuned by the optimizer).

The new ingredient is that each query's key weights are corrected by the
**key–key** score structure: the other rows of the same score matrix. That
is a cheap, one-layer form of two-hop interaction between keys. It needs
neither complex numbers, nor unitarity, nor a matrix exponential. Its closest
published relatives are multi-hop or diffusion attention (for example
Diffuser) and "attention on attention"-style corrections. Whether this exact
square-root, correct, square-and-normalise form has been described before
still needs a targeted literature check.

## P2: held-out probe (parity k=3, L=24, seeds 200–219)

| Variant | Solved / 20 | Window accuracy | Mean seconds/run |
|---|---:|---:|---:|
| softmax | 0 | 50.06% | 45 |
| softmax_t2 | 0 | 50.06% | 45 |
| sqrt_softmax | 2 | 54.13% | 45 |
| maa_p2 | 6 | 64.10% | 48 |
| maa_p11 | 0 | 50.35% | 58 |
| sigmoid | 0 | 49.99% | 43 |
| **c1_wick** | **18** | **88.63%** | 535 |
| wick_real | 18 | 88.56% | 295 |
| wick_linear | 17 | 88.32% | 78 |

- **H2 replicates: c1_wick > softmax, 18–0, p = 7.6 × 10⁻⁶.**
- **H1 fails again:** 2–0, p = 0.50.
- **D5 and D6 hold:** real H (0–0) and the first-order propagator (1–0) match
  the full complex exponential.
- **D2:** MAA p=2 (6/20) solved 4 more seeds than sqrt_softmax and none fewer
  (p = 0.125). On this probe the published MAA at temperature 1 does at least
  as well as the Born-rule √p readout.
- **Cost:** `wick_linear` is about 1.7× softmax per run and needs no matrix
  exponential. The exponential variants cost 6–12× softmax.

## Verdict

Primary hypotheses, per the pre-set rule: Holm-corrected on P1, then
replicated on P2.

| Hypothesis | P1 | P2 | Confirmed |
|---|---|---|---|
| H1: √p readout beats softmax | 5–2, p = 0.45 | 2–0, p = 0.50 | **no** |
| H2: imaginary-time score-operator mixing beats softmax | 26–0, p = 3.0 × 10⁻⁸ | 18–0, p = 7.6 × 10⁻⁶ | **yes** |

**What is confirmed, stated minimally.** On parity-type compositional probes,
a single attention layer does far better when its weights are computed as

  a = √softmax(S),  a′ = a − Δt · a Hᵀ,  A = |a′|² / Σ_j |a′_j|²,
  H = (S + Sᵀ) / (2√L),  Δt ≈ 0.25,

than with softmax. It solves 30/30 against 4/30 at L=16, and 17–18/20 against
0/20 at L=24. The mechanism is classical. The complex, antisymmetric part of
H, unitarity and the matrix exponential are all unnecessary, which rules out
every specifically quantum ingredient on these probes. What remains is a
first-order correction of each query's key weights by the key–key coupling
already present in the score matrix: a one-layer, two-hop interaction among
keys.

**What is not confirmed.**

- The √p (Born-rule) readout on its own. That is Mass-Aware Attention at
  p = 2, and it is no better than published MAA.
- Any quantum-specific effect.
- Anything beyond synthetic parity. The effect has not yet been shown on the
  map benchmark or on real data.

**Novelty status (not established).** The nearest published relatives are
multi-hop attention diffusion (Diffuser, arXiv 2210.11794), higher-order
attention with inner key/query attention (Nexus, arXiv 2512.03377) and
diffusion or heat-kernel attention (arXiv 2604.09560; SSRN 5953096). A quick
search did not find this exact square-root, correct, square-and-normalise
form. Before calling it new, a full literature review is needed, including
checking whether it is equivalent to a known second-order attention.

**Caveats.**

- Δt was fixed by its initialisation. The optimizer moved it by less than
  0.06 in every run, and it was not tuned; 0.25 is the value that happened to
  be tried.
- The probes are synthetic, 1-layer and d=32.
- P1 uses the discovery probe family (though with fresh seeds). P2 is the
  held-out probe.

## Next step (per the spec)

Stage 2 on the unchanged map benchmark is now authorised under the spec's
conditional rule. Its detailed spec (fresh seed pairs, window-averaged
KL/Brier/Q endpoints, equal compute, no final-test access) must be committed
before any Stage 2 run. The candidate is `wick_linear`, the cheapest form that
matched the full operator, with softmax as the baseline and `wick_real` as a
secondary.
