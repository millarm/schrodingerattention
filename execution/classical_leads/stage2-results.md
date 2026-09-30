# Stage 2 results: the confirmed mechanism on the map benchmark

Spec: `stage2-spec.md` (committed in 5cc4369, before any Stage 2 run), with
Amendment 1 (budget) and Amendment 2 (a `wick_real` failure and per-comparison
pairs). Both amendments were written before any result was opened. Tables
come from `summarize_stage2.py`; raw outputs are in
`stage2_results/*.json`.

The setup: the unchanged `RoutePolicy`, whose softmax arm reproduces the
original model's initialisation and logits; the regenerated pool-512
training bank (hash-verified); 8,000 updates; and fresh seed pairs
3001–3012. The final-test split was never loaded.

## Verdict under the pre-set rule: `wick_linear` does not help

| Endpoint (wick_linear − softmax, 12 pairs) | Mean difference | 95% CI | p | Seeds favouring wick_linear |
|---|---:|---|---:|---:|
| **E1**: mean validation KL, updates 800–2,000 (lower is better) | +0.0002 | [−0.0126, +0.0130] | 0.98 | 7/12 |
| **E2**: mean T1/K32 Q, updates 4,000–8,000 (pp, higher is better) | **−0.85** | **[−1.52, −0.19]** | **0.017** | 2/12 |
| Brier, 800–2,000 | +0.0014 | [−0.0044, +0.0073] | 0.60 | 5/12 |
| Greedy Q, 4,000–8,000 (pp) | −1.37 | [−2.81, +0.07] | 0.061 | 4/12 |
| Challenge pass@32, 4,000–8,000 (pp) | −0.18 | [−0.78, +0.42] | 0.53 | 7/12 |
| **Equal compute:** E1 KL | +0.0030 | [−0.0101, +0.0162] | 0.62 | 6/12 |
| **Equal compute:** E2 Q (pp) | **−2.06** | **[−2.72, −1.40]** | < 0.001 | 0/12 |

For KL and Brier, a seed favours `wick_linear` when its difference is
negative. The summariser's raw "diff > 0" counts for those rows are 5/12 and
7/12.

- **Neither primary endpoint improves.** Calibration (E1) is unchanged.
  Route quality (E2) is **worse** by 0.85 pp. Its interval lies entirely on
  the harmful side, which is the spec's "significant harm" condition, and it
  would survive Holm at α = 0.05. By seed, E2 differences are −2.63, −1.48,
  −1.17, −0.78, −0.69, −1.99, +0.65, −1.57, +1.06, −0.35, −0.22 and −1.07 pp.
- **At equal training compute it is clearly worse:** −2.06 pp, in all 12
  pairs. `wick_linear` costs 251 s of training core time per run, against
  204 s for softmax (1.23×).
- **The correction is active, not inert.** On the 128-state validation
  probe, `wick_linear`'s attention differs from same-score softmax by a mean
  TV of 0.45, and the policy moves by 0.14–0.17 TV against Δt = 0. Δt ended
  at 0.16–0.29, so here the optimizer *did* move it, unlike on the probes. So
  the null result is not a case of the mechanism being switched off. It
  substantially changes the attention, and that change does not help this
  task.
- **Learning curves** (mean Q over 12 seeds): softmax 26.4 / 29.9 / 30.6 /
  37.2% at 1k / 2k / 3k / 8k updates, against 25.7 / 29.8 / 30.5 / 36.0% for
  `wick_linear`. The best mean validation KL is 0.294 (at 1,600 updates) for
  softmax and 0.289 (at 1,700) for `wick_linear`. That is a sampled-grid
  minimum only; E1 over its fixed window shows no difference.

## Secondary arm: `wick_real` is numerically unstable

- **4 of 12 runs failed technically:** seeds 3005 and 3012 hit the
  non-finite-gradient guard; seeds 3006 and 3010 produced invalid
  probabilities or logits during evaluation. The cause is e^(−ΔtH) growing
  exponentially for large negative eigenvalues of H, in float32. Per the
  spec, these runs are reported and not replaced.
- **On the 8 completed pairs** there is no difference on any endpoint: E1
  −0.0011 [−0.025, +0.023]; E2 −0.10 pp [−1.42, +1.22]. At equal compute it
  is −3.98 pp (0/8), because it costs 404 s against 204 s.
- The 8 completed seeds are a survivor subset, so the result is conditional
  on the run not diverging.

## Interpretation

1. **The probe result does not transfer to the map benchmark.** The same
   mechanism that solved 3-bit parity in 30/30 and 18/20 seeds, against 4/30
   and 0/20 for softmax, gives no calibration benefit here. It slightly
   reduces route quality at equal updates, and more at equal compute. As fixed
   in advance, the main Stage 2 finding is that **the mechanism helps on
   synthetic parity only.**
2. **This fits the literature caveat.** The probe gains came on a task that
   single-layer softmax is known to find hard (parity or high-sensitivity
   functions). The map policy uses 2 layers, and its difficulty is
   generalisation to held-out maps, not a three-way interaction that one layer
   cannot express. A query–key–key correction targets the first kind of
   difficulty, so it has nothing to fix here, and it disturbs attention that
   softmax already learns well.
3. **There is no quantum-specific effect anywhere in the programme.** Across
   Stage 1, Stage 1b, Stage D and Stage 2, every gain that appeared was
   reproduced or beaten by a classical twin. The one confirmed mechanism is
   classical, and it does not help the real task.

## Limits

- **One benchmark,** with a heavily reused validation panel. A null or
  negative result on it does not rule out benefits elsewhere, for example
  deeper models or tasks that need multi-way interactions.
- **Δt initialisation (0.25) was carried over from the probes, not tuned.**
  A smaller Δt might avoid harming route quality. But tuning it on this
  panel would be outcome-driven, and it would need its own spec and a fresh
  split.
- **Twelve pairs.** The E2 harm is small (below 1 pp) and should be read as
  "no benefit, possibly a small cost", not as a precise effect size.
