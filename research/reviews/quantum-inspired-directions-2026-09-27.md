# Quantum-inspired transformer components: revised plan

2026-09-27, revision 2. The goal is to build **general-purpose transformer
components** taken from quantum mechanics, not quantum methods for the map
problem. Each component must work on any token sequence, derive its operators
from token content alone, and drop into a standard block in place of softmax
attention. The 12×12 route-policy benchmark is used only as the first test
bed, with its current 13-token representation left unchanged. No component
may use the grid, the map graph or the oracle.

Numbers come from committed artifacts or from the self-contained scripts in
the appendix. No repository model was trained or evaluated for this document.

## 1. What the early-learning diagnostic established

- **No early SA advantage.** Over the fixed 800–2,000 window, mean ΔQ is
  −0.05 pp, with opposite per-seed signs. The Q slope favours softmax in both
  pairs.
- **Held-out optima depend on the seed.** Sampled KL/Brier minima are at
  700–900 updates for seed 2201 and 2,600 for seed 2202.
- **The KL rise comes mostly from concentration within the oracle's support.**
  The within-support term B increases in all four 800→2,000 contrasts.
- **The current SA is nearly inert.** Δt stays at 0.046–0.068 against an
  initial 0.05 and a cap of 0.5. Setting dt=0 changes the policy by only about
  0.005 TV, and greedy actions disagree about 0.8% of the time.

## 2. Why the current component cannot be very different from softmax

Four properties of `schrodinger/attention.py` together explain the inert
result. Each points to a generic change in the architecture.

| Property of the current design | Consequence | Generic change (§4) |
|---|---|---|
| H = (S + Sᵀ)/2√L keeps only the symmetric part of the scores | Directional (query→key versus key→query) information is discarded. H is real, so it preserves time-reversal symmetry. | C1 |
| Phase = γ·S, so within a row ψ₀ = p^(1/2+iγ) up to a global phase | The complex state is a function of the softmax distribution and carries no new information | C2 |
| With real H and zero phase, the first-order term in Δt vanishes | Evolution acts only at order Δt², which fits the optimizer leaving Δt at its initial value | C1, C2 |
| Born weights \|ψ\|² are row-stochastic and applied to real values | Outputs stay in the convex hull of the values. Any full-support row is reachable by softmax, so a head gains no per-row expressive range. | C4 |

The first-order claim was checked numerically (appendix A). With zero phase
and random 13×13 scores, doubling Δt quadruples TV under the current real
symmetric H. Under the complex Hermitian H of C1, it doubles. At Δt=0.05,
C1's H moves attention about 9× more (TV 0.036 against 0.004).

## 3. Controls every component must beat

A result counts as quantum-specific only if it beats softmax and all three
classical twins below. Each twin is trained independently, with the same
parameter count and the same block.

| Twin | Construction | What it isolates |
|---|---|---|
| Imaginary-time (Wick) twin | Replace e^(−iΔtH) with row-normalised e^(−ΔtH) on real amplitudes | Interference and unitarity; keeps the same operator |
| Fully dephased twin | Same H, with the density matrix forced diagonal (a classical Markov mixing step) | Coherence |
| Phase-free twin | All learned phases fixed at 0 (and for C1, the antisymmetric part of H set to 0) | Signed or complex cancellation |

Also report equal-update and equal-compute results together. The appendix B
note explains why the twins are needed: on a structured problem, a classical
propagator can match a quantum one exactly.

## 4. Components, ranked by expected information per unit of cost

All components are drop-in replacements for the attention module in
`schrodinger/attention.py`. They use the same interface and the same Q/K/V
projections unless stated otherwise. Parameter budgets are matched with the
existing α/β-style scalars where needed.

### C1. A Hermitian Hamiltonian from the full score matrix (smallest change)

H = [(S + Sᵀ) + i(S − Sᵀ)] / (2√L). The antisymmetric part becomes the
imaginary part, so H is Hermitian and U = e^(−iΔtH) stays exactly unitary.

- **What is new.** Directional information re-enters the evolution. Time
  reversal is broken, so evolution acts at first order even with zero phase
  (appendix A). The change is one line.
- **Cost.** The same as the current component. Using `torch.linalg.eigh` on
  the Hermitian H is cheaper and more exactly unitary than `matrix_exp`.
- **Evidence it is working.** Δt leaves its initial value, and dt=0 policy TV
  rises clearly above 0.005.

### C2. A complex query–key channel (phase from content)

Make the query and key projections complex: z_ij = q_i† k_j / √d. The
magnitude channel gives p = softmax(Re z). The phase channel is φ_ij = Im z_ij,
so ψ₀ = √p ⊙ e^(iφ). The Hamiltonian is then C1's H built from Re z, or a
separate learned Hermitian projection.

- **What is new.** The phase now carries information that p does not, which
  removes the degeneracy. This is the component-level version of "complex
  attention", with interference applied through U.
- **Twin.** The same with the imaginary parts of q and k set to 0.
- **Cost.** About one extra Q/K projection. Budget it against a wider softmax
  baseline.

### C3. Coherence-controlled attention (a Lindblad dephasing knob)

Evolve a density matrix: dρ/dt = −i[H, ρ] − κ(ρ − diag ρ), with a learned rate
κ ≥ 0 per head. The attention weights are diag ρ(Δt).

- **What is new.** It interpolates between the coherent component (κ=0) and a
  classical Markov mixing step (κ→∞) *inside one model*. The learned κ
  diagnoses itself: a finite, head-specific κ means the network uses
  coherence, and κ at its maximum means it doesn't. The physics analogue is
  environment-assisted transport, where transfer peaks at intermediate
  dephasing (Plenio & Huelga 2008; Rebentrost et al. 2009; check before
  citing).
- **Cost.** For a pure-dephasing Lindbladian, vec(ρ) has L² components. At
  L=13 that is one 169×169 exponential per head and example, which is
  feasible on CPU. For longer sequences, use a few Trotter steps (evolve, then
  dephase).
- **Twins.** κ fixed at 0 (coherent C1/C2) and κ fixed large (dephased).

### C4. Amplitude-level value mixing (measuring an observable)

Mix values *before* measurement: out_i = Σ_j ψ_ij v_j, with complex ψ from
C1/C2 and complex values (or real values with 2d real and imaginary output
channels). More generally, out_i,c = ψ_i† O_c ψ_i for learned Hermitian
observables.

- **What is new.** Contributions from different keys can cancel, so the
  output can leave the convex hull of the values. A single head can express
  signed, pairwise (XOR-like) interactions between keys. By §2, the current
  component cannot.
- **Twin.** The same readout with real, non-negative amplitudes (√p weights):
  bilinear, but with no cancellation.
- **Risk.** Output scale is no longer bounded by the values, so it needs
  LayerNorm or norm control before the residual.

### C5. Entangled heads (speculative)

Give two heads a joint amplitude over key pairs (L² components) and use their
measured marginals as the two heads' attention. Head correlations become a
learned resource. The built-in diagnostic is the entanglement entropy: zero
means the model reduced to two independent heads. The control is a product
state with the same parameters. Pursue this only if C1–C3 show that coherence
is used.

### Causal-compatibility requirement (all components)

The current benchmark is bidirectional, but a transformer component must
eventually run causally. Symmetrising a masked score matrix breaks causal
semantics (paper, appendix E). The candidate here: each query i evolves in its
own prefix subspace using H restricted to [:i, :i]. Computed with a Krylov
(Lanczos) approximation, this costs O(kL²) per query rather than O(L³). The
first causal check should be a small autoregressive toy task, run after the
bidirectional stages.

## 5. Test plan

### Stage 0: unit checks (no training)

For each component: Hermiticity, unitarity, and trace or row normalisation;
reduction to softmax at Δt=0; reduction of each twin to its definition;
finite float64 gradients; and first-order sensitivity to Δt (appendix A
extended). Also time the forward/backward pass at L = 13, 64 and 256.

### Stage 1: generic mechanism probes (minutes of CPU)

These are small synthetic sequence tasks with no connection to the map, built
to separate the mechanisms. Use one or two layers, d=32, several seeds, and
run every component against softmax and all three twins.

- **Signed pairwise interaction:** output the XOR or parity of two marked
  tokens (tests C4 and C2).
- **Exclusion:** attend to token A unless token B is present (tests
  destructive interference in C1/C2).
- **Associative recall with distractors** (tests C3's coherence against
  dephasing).
- **Direction-sensitive relation:** decide whether A comes before B (tests
  C1's antisymmetric part).

Carry a component into Stage 2 only if it beats all of its twins on at least
one probe, with that probe chosen in advance per component.

### Stage 2: the map benchmark as test bed

- Use the unchanged `RoutePolicy` backbone and 13 row tokens, swapping only
  the attention module. Keep the same data, optimizer and budget.
- Use fresh seed pairs. Start with 3–4 pairs as a variance pilot, then size
  the study from a precision target.
- Primary endpoints: window-averaged validation KL and Brier over a
  predeclared early window. Q is the companion endpoint, also
  window-averaged. Report the 8k endpoint as secondary. Report equal-compute
  results beside equal-update ones.
- Mechanism readouts: learned Δt, κ and phase scale; dt=0 policy TV;
  phase-scramble TV; and Wick-swap TV at fixed weights.
- Success: a component beats softmax **and** all three twins on the primary
  endpoint, **and** its mechanism readouts show the quantum part is in use
  (Δt moved, κ finite, or phase TV clearly above 0.005).

### Stage 3: confirmation

Only after Stage 2 succeeds: a preregistered fresh-seed confirmation that
touches the reserved final-test split exactly once. Then the causal variant
on a small language-modelling task.

**Stopping rule.** If no component beats its twins in Stage 1, or none
survives Stage 2, write a bounded negative result. That result says: with
content-derived operators, interference adds nothing to a transformer
attention step beyond what classical mixing already provides.

## 6. What was dropped from revision 1

Revision 1 proposed grid-graph quantum walks and Aharonov–Bohm phases on map
edges. Both inject the task's structure into the model, so they answer a
different question (quantum *algorithms* for planning) and are out of scope
for this architecture study. What survives from them is generic: the idea of
complex Hermitian couplings (now C1/C2) and the mandatory classical twins
(appendix B).

## Appendix A: evolution acts at first order under a Hermitian H

```python
import numpy as np, scipy.linalg as sl
rng = np.random.default_rng(0); L = 13
S = rng.normal(0, 2, (L, L)); p = np.exp(S - S.max(1, keepdims=True)); p /= p.sum(1, keepdims=True)
born = lambda H, dt: np.abs(np.sqrt(p) @ sl.expm(-1j * dt * H).T) ** 2   # zero phase
Hs = (S + S.T) / (2 * np.sqrt(L))                  # current component
Hh = Hs + 1j * (S - S.T) / (2 * np.sqrt(L))        # C1
for name, H in (("real symmetric", Hs), ("Hermitian C1", Hh)):
    tv = [0.5 * np.abs(born(H, dt) - p).sum(1).mean() for dt in (1e-3, 2e-3, 0.05)]
    print(name, "TV at dt=0.05: %.4f, ratio when dt doubles: %.2f" % (tv[2], tv[1] / tv[0]))
# real symmetric: 0.0038, ratio 4.00 (second order); Hermitian C1: 0.0356, ratio 2.00 (first order)
```

## Appendix B: why the classical twins are mandatory

This check uses task structure on purpose. It is a caution, not a proposal. On
random 12×12 maps with route length 14–16, a zero-parameter quantum walk on
the true grid graph reaches KL ≈ 0.011 to the oracle at t=1. The classical
heat kernel on the same graph reaches ≈ 0.010, and it is more robust at larger
t (0.185 against 0.806 at t=8). A module that looks strong can be strong for
entirely classical reasons, so every component above is judged against twins
that keep its operator and remove only the quantum ingredient. The script is
in revision 1 of this file (commit b1c97c5).
