# Stage 2 specification: the confirmed mechanism on the map benchmark

2026-09-28. Written and committed **before any Stage 2 implementation run or
result**. Stage 2 is authorised by the conditional rule in
`stage-d-spec.md`: H2 was confirmed on P1 and P2 (`stage-d-results.md`).
Framing follows `literature-review.md`.

## Question

Does the confirmed attention correction improve the **unchanged** route-policy
model on the pool-512 map benchmark, relative to its softmax baseline, in
held-out calibration or route quality? The correction is a parameter-free
query–key–key correction of softmax:
a = √softmax(S), A ∝ (a − Δt·aHᵀ)², H = (S+Sᵀ)/2√L.

This is a test of transfer from synthetic parity to a real task in this
repository. It is not a test of anything quantum; Stage D showed the
mechanism is classical.

## Arms

All arms use the same `RoutePolicy` architecture:

- a 36→64 row embedding;
- a CLS token and learned positions (13 tokens);
- 2 pre-norm blocks, each with 2-head attention (width 64) and a 64→128→64
  GELU feed-forward;
- a final LayerNorm and a 4-action head.

Only the attention weight computation differs. The arms go in a new module,
`schrodinger/route_policy_variants.py`; the hash-pinned `route_policy.py` is
untouched. Attention comes from `schrodinger/quantum_components.py`.

| Arm | Attention | Role |
|---|---|---|
| `softmax` | softmax(S·e^α), values × e^β | baseline |
| `wick_linear` | the confirmed first-order correction, learned Δt per head initialised at 0.25 | **primary** |
| `wick_real` | the real-H matrix-exponential version, Δt initialised at 0.25 | secondary |

**Required equivalence tests, which must pass before any run:**

1. The variant module's `softmax` arm, loaded with the same weights,
   reproduces the original `RoutePolicy("softmax")` logits to 1e-6. So the
   baseline is the original model.
2. All arms have identical parameter counts and bit-identical shared
   initial tensors for the same seed.
3. At Δt = 0, both variant arms reproduce the softmax arm's logits.

## Data, training and evaluation (unchanged protocol)

- **Training data:** the pool-512 proposal-14 training bank (32,946 states;
  1,024 problems).
  - It is regenerated with `regenerate_route_data.py`.
  - The runner must check it with `verify_training_bank.py` before training:
    the `selected_hash` must equal `8879d863…2618`, or the run stops.
- **Optimiser:** AdamW, lr 1e-3, betas (0.9, 0.999), eps 1e-8, weight decay
  0.01, gradient clip 1.0, batch 64.
- **Sampling and loss:** batches from `MapBalancedSampler(states, seed)`;
  loss is cross-entropy against the oracle q. This is the original
  `train_step` logic, reused, not reimplemented.
- **Length:** 8,000 updates per run, 2 torch threads, 1 inter-op thread.
- **Validation:** the committed validation panel (512 problems; 1,024-state
  proper bank).
  - `evaluate_proper` (KL, Brier) every 100 updates, 0–8,000.
  - `evaluate_rollouts` at T = 1, K = 32 (overall Q with the 80/20
    routine/challenge mixture, challenge pass@32), plus greedy Q, at every
    200 updates up to 3,000 and every 1,000 from 3,000 to 8,000.
- **No final-test access.** `load_final_test` is not called.

## Seeds and pairing

Fresh seed pairs **3001–3012 (12 pairs)**; none of these seeds have been
used before. Within a pair, every arm is built after `torch.manual_seed(seed)`
and trained on the same `MapBalancedSampler(seed)` stream, so shared
initialisation and batch digests are identical. Test 2 checks this and each
run records it. With 12 pairs, a two-sided paired t-test at α = 0.05 has
about 80% power for a standardised paired effect of 0.9. That is modest, and
the report gives confidence intervals, not only verdicts.

## Endpoints

Per run, each endpoint is an average over a fixed window, not one
checkpoint, as the critical review recommended.

- **E1, primary (calibration):** mean validation KL over updates 800–2,000
  (13 points). Lower is better. The earlier diagnostic found held-out KL is
  best around here.
- **E2, primary (route quality):** mean overall T1/K32 Q over updates
  4,000–8,000 (5 points). Higher is better. This covers the regime of the
  original comparisons.
- **Secondary:**
  - mean Brier over 800–2,000;
  - mean greedy Q over 4,000–8,000;
  - mean challenge pass@32 over 4,000–8,000;
  - the full curves;
  - final Δt per head;
  - **equal-compute comparison**: the softmax curve re-indexed by measured
    training-core seconds, compared with `wick_linear` at equal cumulative
    core time;
  - mechanism readouts at 2,000 and 8,000 on the existing 128-state
    validation probe: mean TV between the arm's attention weights and
    softmax(S) at the same weights, and full-policy TV under Δt = 0.

## Tests and decision rule

For `wick_linear` against `softmax`:

- Take the per-pair differences in E1 and E2.
- Run a two-sided paired t-test on each, with **Holm correction across E1
  and E2**, family α = 0.05.
- Report the 95% paired confidence interval and the sign count for each.

**`wick_linear` is declared to help on the map benchmark** if both hold:

- at least one primary endpoint improves significantly after Holm;
- the other primary endpoint's 95% interval does not lie entirely on the
  harmful side (no significant harm).

`wick_real` against softmax is reported the same way, but is not part of the
decision.

**Interpretation, fixed in advance:**

- If the probe gains do not transfer, the report says so as the main
  Stage 2 finding. The mechanism then helps on synthetic parity only.
- Any benefit at equal updates is also stated at equal compute. No
  equal-compute advantage is claimed unless the re-indexed comparison shows
  one.
- The validation panel has been reused across many earlier studies, so a
  positive Stage 2 result is still not a confirmation. That would need a
  separately gated, preregistered final-test run under the repository's
  release rules.

## Budget and stopping

- **Estimated cost:** 36 runs × about 3–5 minutes each (training plus
  evaluations), about 2–3 CPU-hours, or about 1.5 hours of wall time on 2
  slots. A 5-hour wall-clock cap applies.
- A run that fails technically is reported, not replaced. The decision uses
  complete pairs only.
- If the equivalence tests fail, stop and fix before any run. No outcome is
  inspected before all 12 pairs complete.

## Implementation checklist (before the first run)

1. Write `schrodinger/route_policy_variants.py` and its tests (equivalence
   tests 1–3).
2. Write `execution/classical_leads/stage2_train.py`. It must:
   - verify the training bank hash;
   - reuse `train_step`, `evaluate_proper` and `evaluate_rollouts`;
   - write one JSON per arm and seed (curves, timings, initial and batch
     digests, Δt trajectory, mechanism readouts).
3. Run a 20-update smoke test of each arm on seed 9999 and check the outputs
   are well-formed. The smoke outputs are discarded and never analysed.
4. Commit all of the above, then start the 12-pair queue.

## Amendment 1 (2026-09-28, before any Stage 2 run; budget only)

The smoke runs (seed 9999, 200 updates, outputs discarded) showed that
evaluation dominates the cost:

- each T1/K32 plus greedy rollout point takes about 25–27 s;
- training takes about 0.02 s per update (softmax), 0.03 s (wick_linear)
  and 0.045 s (wick_real).

A full run is therefore about 12–15 minutes, and the 36 runs total about
8 CPU-hours, or about 4 hours of wall time on 2 slots, not about 1.5 hours.
**The wall-clock cap is raised from 5 to 7 hours.** No arm, seed, endpoint,
test or decision rule changes.

The smoke check also confirmed:

- all three arms share the initial-tensor digest and the batch-digest chain
  for the same seed;
- each arm has 70,540 parameters (the original model's count);
- the variant module's softmax arm reproduces the original `RoutePolicy`
  initialisation and logits (tests in `tests/test_route_policy_variants.py`);
- at initialisation, the correction moves attention by about 0.07–0.08 TV
  from softmax, and moves the policy by about 0.019 TV relative to Δt = 0.

The runner also serves the excluded, byte-hash-checked `inventory.json` to
`load_validation`, which needs it too.
