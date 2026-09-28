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

Pending (queue running).
