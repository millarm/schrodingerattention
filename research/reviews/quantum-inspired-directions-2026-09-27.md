# Quantum-inspired directions that could show real novelty

2026-09-27. Scope: a response to the accepted early-learning diagnostic
(`execution/early_learning/results.md`, `scientific-closeout.md`, Sol results
PASS), followed by proposals. All proposals are restricted to ideas taken from
quantum mechanics. Every number here comes from committed artifacts or from
the self-contained script in the appendix. No repository model was trained or
evaluated.

## 1. What the early-learning diagnostic changes

**The early SA advantage is gone.** Over the fixed 800–2,000 window, mean ΔQ is
−0.05 pp, and the per-seed signs are opposite. The Q slope favours softmax in
both pairs. The 6/6 first-checkpoint sign pattern in the critical review (§3)
should now be read as checkpoint noise. The dense curves are the better
evidence.

**Held-out optima depend on the seed.** Sampled KL/Brier minima are at 700–900
updates for seed 2201 and 2,600 for seed 2202. No single stopping point exists.

**The KL rise comes mostly from concentration within the oracle's support.**
The within-support term B increases in all four 800→2,000 contrasts. The
support-mass term A is mixed. Of the two explanations offered in the critical
review, concentration dominates.

**In these models, evolution barely affects the policy.** This is the result
that matters most for what follows:

- **Δt hardly moves.** It starts at 0.05, and by 3,000 updates it is only
  0.046–0.068 in every layer, head and seed. Its cap is 0.5. Adam takes steps
  of roughly the learning rate whenever a gradient has a consistent sign, so
  Δt staying put means the optimizer finds no consistent benefit in more
  evolution. γ moves more: up to about 0.69 on one head of seed 2201.
- **Switching evolution off changes little.** Setting dt=0 changes the
  full-policy TV by only about 0.005 on average. Greedy actions disagree about
  0.8% of the time. Attention TV is about 0.03.

For the route task, then, SA as implemented behaves as softmax plus a small
perturbation. Combined with the two structural facts below, this explains the
null results. It also shows that more seeds of the *same* module are unlikely
to find anything.

### Two structural reasons the current module cannot be very different

1. **The phase carries no new information.** Within a row, ψ₀ = p^(1/2+iγ) up
   to a global phase (critical review §4). The complex state is a fixed
   function of the softmax distribution.
2. **Born-rule attention has the same per-row expressive range as softmax.**
   A = |ψ₁|² is row-stochastic, so every output is still a convex combination
   of the values. Any full-support row distribution A can also be produced by
   softmax with scores log A. At the level of a single row, SA can only change
   *how* A depends on the input, never *which* outputs are reachable. The only
   new input-dependence it adds is the shared operator H, built from the
   symmetrised row-token scores.

Real novelty therefore needs at least one of these:

- phases that carry information p does not;
- an operator H that encodes real structure of the task;
- a readout that escapes the convex hull;
- a built-in measure of whether coherence is being used at all.

## 2. Mandatory controls for any "quantum" effect

Quantum-style modules invite false attribution, as the numerical test below
shows. A result should count as quantum-specific only if it survives all three
classical twins, each trained independently with the same parameter count:

| Twin | Construction | What it removes |
|---|---|---|
| Imaginary-time (Wick) twin | Replace e^(−iΔtH) with the normalised e^(−ΔtH) and use real amplitudes | Interference and unitarity; keeps the same propagator and structure |
| Fully dephased twin | Same H, with the density matrix forced diagonal every step (a classical random walk) | Coherence |
| Phase-free twin | γ = 0, or edge phases = 0 | Any signed or complex cancellation |

For each twin, report the effect on held-out proper scores and Q, and give the
equal-compute comparison next to the equal-update one.

## 3. A calibration point: the quantum walk on the true grid does well, but not because it is quantum

The route task *is* a graph problem. Let A be the adjacency matrix of a map's
passable cells. The continuous-time quantum walk amplitude is
⟨g|e^(−itA)|n⟩ = Σₖ (−it)ᵏ/k! · (Aᵏ)_gn. To leading order in t, its magnitude
from a neighbour n at shortest distance d is t^d/d! times the number of
shortest paths from n to g. That count is exactly the quantity that defines
the oracle's teacher distribution. Neighbours that are not optimal are one
power of t further down.

The appendix script builds random 12×12 maps with 25% obstacles and draws
240 problems with route length 14–16. It then scores **zero-parameter**
policies p(a) ∝ |⟨g|U(t)|n_a⟩| against the oracle. The classical twin
(normalised heat kernel e^(t(A−λ_max))) is scored the same way:

| t | Quantum walk KL | Quantum walk: argmax on an optimal action | Heat kernel KL | Heat kernel: argmax on an optimal action |
|---:|---:|---:|---:|---:|
| 0.5 | 0.041 | 1.00 | 0.274* | 0.99 |
| 1 | **0.011** | 1.00 | **0.010** | 1.00 |
| 2 | 0.052 | 1.00 | 0.033 | 1.00 |
| 4 | 0.285 | 0.92 | 0.094 | 1.00 |
| 8 | 0.806 | 0.62 | 0.185 | 1.00 |

\*At t=0.5, heat-kernel entries at distance 14–16 are close to float64
round-off, so this value reflects numerical precision, not the method.

The trained 70k-parameter models reach a held-out KL of about 0.27–0.30 at
their best. A propagator on the correct graph, with no parameters, reaches
about 0.01. **But the classical twin matches it, and it is more robust at large
t.** The quantum walk degrades as the wavefront passes the goal and
interference scrambles the signal.

Conclusions:

- Nearly all of the attainable gain on this task comes from *structure*: the
  right Hamiltonian. Tokens that are grid rows force the network to learn the
  graph.
- A grid-Hamiltonian SA would look impressive against the current softmax
  baseline for reasons that have nothing to do with quantum mechanics. §2 is
  not optional.
- My own prior expectation, that ballistic quantum spreading would help on long
  routes, is refuted by this test.

(Quantum-walk graph networks already exist, for example Dernbach et al.,
"Quantum walk neural networks". Check this and every other citation before
use.)

## 4. Proposals, ranked by chance of showing a quantum-specific effect

### P1. A learned coherence knob (Lindblad dephasing)

Evolve a density matrix instead of a pure state:
dρ/dt = −i[H, ρ] − κ(ρ − diag ρ), with a learned dephasing rate κ ≥ 0 per head.
The attention weights are A = diag ρ(Δt). κ = 0 is the current coherent SA;
κ → ∞ is a classical random walk on the same H.

- **Why it could be novel.** In quantum transport, transfer efficiency often
  peaks at *intermediate* dephasing. This is environment-assisted quantum
  transport (Plenio & Huelga 2008; Rebentrost, Mohseni et al. 2009). If a
  trained network settles on a finite, non-trivial κ, it is using coherence.
  If κ runs to its maximum, the quantum part is dead weight. In both cases the
  model *reports on itself*, which none of the current probes can do.
- **Cost.** For L = 13, vec(ρ) has 169 components, and one 169×169 matrix
  exponential per head and example is feasible on CPU. With a grid-cell
  Hamiltonian, use a few Trotter steps instead.
- **First test.** Train with κ learned, on the same seeds and budget. The
  primary readout is the learned κ distribution across heads and seeds, plus
  held-out KL against the fully dephased twin.

### P2. Aharonov–Bohm phases to control route diversity

Put learned Peierls phases on grid edges, H_nm = −e^(iθ_nm) for adjacent cells
(equivalently, a learned flux Φ per plaquette), in a grid-cell quantum walk or
attention layer. Two routes around an obstacle pick up a relative phase equal
to the enclosed flux. Tuning Φ makes route *classes* interfere constructively
or destructively.

- **Why it fits this benchmark.** The challenge split is defined by
  *structurally novel* shortest routes, which are essentially different route
  classes. The original hypothesis was about productive diversity. Flux gives
  a physically meaningful handle that redistributes probability between route
  classes without changing route length, and it has **no positive-weight
  classical twin**: a heat kernel cannot cancel paths.
- **First test (zero training).** On the existing challenge validation maps,
  sweep a uniform flux in a zero-parameter walk. Measure how the probability
  mass across canonical route classes, pass@32 and valid headroom change,
  compared with the heat kernel and the Φ=0 walk. Train Φ only if flux can
  move mass between valid classes without losing Q.

### P3. Readout through an observable, to escape the convex hull

Replace output = |ψ|²V with an expectation value: output_c = ψ†O_cψ, with
learned Hermitian O_c built from values and keys (for example
O_c = V_c V_cᵀ + a learned off-diagonal term). Cross terms
√(p_j p_k)·cos(φ_j − φ_k)·O_jk can be negative. A single head can then
represent pairwise interactions (XOR-like) and produce outputs outside the
convex hull of the values. By §1, the current module cannot do either.

- **Twin.** The same bilinear readout with real, non-negative amplitudes (γ=0).
  It has cross terms, but no cancellation.
- **First test.** A parity/XOR family where one-layer convex attention
  provably fails, followed by the route task. The initial XOR screen (+2.02 pp
  for SA) is weak but relevant.

### P4. A phase channel that carries its own information

This is the minimal change that removes degeneracy (1). Use
ψ₀ = √p ⊙ e^(iφ(x_k)), with the phase from its own projection of the key
tokens, not from the scores. Optionally, make H query-dependent
(H_i = K diag(q_i) Kᵀ/√d) instead of shared across rows.

- **Twin.** φ ≡ 0, with the same parameters.
- **Success signal.** Δt leaves its initial value; dt=0 policy TV rises
  clearly above the current 0.005; and held-out KL beats the twin. If Δt
  still sits at initialisation, interference is not useful on this task in
  this parameterisation, and that is a clean negative.

### P5. Entangled heads (lower priority)

Give two heads a joint state on keys⊗keys (169 amplitudes), so that the
measured marginals are correlated. The control is a product state with the
same parameters. The entanglement entropy of the learned state is a built-in
diagnostic: zero means the model reduced to two independent heads. This is
speculative, and only worth doing if P1 or P4 shows that coherence is used.

## 5. Suggested order and stopping rule

1. **Zero-training, hours:** P2's flux sweep on existing challenge maps,
   against the heat kernel and the Φ=0 walk, extending the appendix script. If
   flux cannot move valid-route mass between classes, drop P2.
2. **Inference only, on existing SA checkpoints:** two fixed-weight probes
   beside the dt=0 probe. First, a Wick swap (e^(−iΔtH) → normalised
   e^(−ΔtH)). Second, phase scrambling: keep |ψ₀| and randomise the phases. If
   both change the policy as little as dt=0 does, record that the current
   module is inert on this task and stop working on it.
3. **Small trained study:** P1 and P4 on 2–3 seed pairs with all three §2
   twins, using proper-score endpoints averaged over a window. Continue only
   if κ settles at an intermediate value or Δt moves, *and* held-out KL beats
   every twin.
4. Only after step 3 is positive, preregister a fresh-seed confirmation, and
   P3 on a task family where the convex hull provably matters.

Stop and write a bounded negative result if no quantum-specific effect survives
the twins at step 3. That outcome is informative too: interference, as a
mechanism, adds nothing on this planning task beyond structure a classical
propagator already captures.

## Appendix: zero-parameter quantum walk against the heat kernel

Run with numpy. It uses random maps, not the repository benchmark, so the
numbers show a mechanism only and are not a benchmark result.

```python
import numpy as np
from collections import deque
rng = np.random.default_rng(1); N = 12
def grid():
    free = rng.random((N, N)) > 0.25
    idx = {(r, c): i for i, (r, c) in enumerate((r, c) for r in range(N) for c in range(N) if free[r, c])}
    A = np.zeros((len(idx),) * 2)
    for (r, c), i in idx.items():
        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            j = idx.get((r + dr, c + dc))
            if j is not None: A[i, j] = 1
    return A
def bfs(A, g):  # shortest distance and shortest-path count to goal
    n = len(A); d = np.full(n, -1); cnt = np.zeros(n); d[g] = 0; cnt[g] = 1; q = deque([g])
    nb = [np.nonzero(A[i])[0] for i in range(n)]
    while q:
        u = q.popleft()
        for v in nb[u]:
            if d[v] < 0: d[v] = d[u] + 1; q.append(v)
            if d[v] == d[u] + 1: cnt[v] += cnt[u]
    return d, cnt, nb
ts = [0.5, 1, 2, 4, 8]; kl = {(k, t): [] for k in ("qw", "heat") for t in ts}
for _ in range(40):
    A = grid(); lam, V = np.linalg.eigh(A); n_prob = 0
    for _ in range(200):
        g = rng.integers(len(A)); d, cnt, nb = bfs(A, g)
        cand = np.nonzero((d >= 14) & (d <= 16))[0]
        if not len(cand): continue
        s = rng.choice(cand); legal = nb[s]
        q = np.array([cnt[a] if d[a] == d[s] - 1 else 0 for a in legal], float); q /= q.sum()
        for t in ts:
            sc = {"qw": np.abs((V * np.exp(-1j * t * lam)) @ V[g])[legal],
                  "heat": np.clip(((V * np.exp(t * (lam - lam.max()))) @ V[g])[legal], 1e-300, None)}
            for k, v in sc.items():
                p = np.clip(v / v.sum(), 1e-12, None); p /= p.sum()
                kl[(k, t)].append(np.sum(q[q > 0] * np.log(q[q > 0] / p[q > 0])))
        n_prob += 1
        if n_prob == 6: break
for k in ("qw", "heat"): print(k, [round(np.mean(kl[(k, t)]), 3) for t in ts])
```
