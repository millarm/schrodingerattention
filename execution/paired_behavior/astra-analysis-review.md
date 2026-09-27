# Independent review — Astra paired-behavior analysis recovery

## Verdict: PASS

Exact reviewed artifacts:

- `analysis.py`: `1d7d2339c382fd4cea6b76b84a5ca6074ca01561a7fb2c9df9e76fee1fc0758a`
- `job.py`: `8d695dc4383024b85db06eb03d25937d786787b32610dea42905c3e48c5bef92`
- tests: `f6671c15b064055ce1c73baca2c3d6cab2d7aac4a6ff75cf082a6043d8e87c9e`
- recovery approval: `58fec1fa8e4bcf06a1b39524b899a090d00821b2d9eb8c5828ec9d1b42f1ba22`
- handoff: `e30e393094537b0bbf0f2afa95ba6cc856bd7f23c1b33b523de1c1721eb44df9`
- governing plan: `be5e5fea4fd5f2ee0e4cb3013637127b9437409bef6d6fa993f06777e65b39be`

The narrowly authorized recovery closes all five findings from `analysis-review.md` without changing training, cohorts, sampling, thresholds or scientific scope.

### Closure checks

- Actual retained canonical maps and routes are decoded from direct hexadecimal strings. The literal fixture loads a real immutable softmax event and passes it through both adapters.
- Each event is bound to an owner-manifest-verified result, prepared/source identities, and a stable whole-event digest. Every route is replayed against the expected problem's exact map/start/goal oracle and must reproduce the stored validity flag. The output retains the honest limitation that historical route records omit start/goal, so immutable producer/dataset order plus oracle corroboration cannot prove permutations among groups whose routes are all invalid. A same-map post-load permutation is rejected by the event binding.
- Route comparison retains raw valid/intersection/architecture-only/novel sets and the required per-problem Q, pass@K, U_valid, U_novel and V_novel metrics, with map/stratum/frozen-mixture summaries and both-empty Jaccard NA.
- Exact aligned p/q state rows now retain per-state softmax and Schrödinger CE, KL, Brier, nonoptimal mass, entropy, TV, argmax and q-optimality; equal-map, stratum and mixture summaries include all required proper and uncertainty measurements.
- Frozen support is checked against expected SHA-256 `2bcde9c3...`. The existing softmax A/B/C result is checked against expected `46ca7f60...`, exact support equality and each softmax checkpoint hash. Its literal rows/q are paired with the newly evaluated Schrödinger rows, and both raw sides plus explicit proper/greedy/T1 deltas are retained. Cohorts are deserialized verbatim at 768 states and 144 routes per arm; no selection or reconstruction occurs.
- The quality-control block reuses retained T=1 and performs exactly the two authorized new Schrödinger rollout evaluations at temperatures 0.75 and 1.25. It preserves the fixed mixture/stratum tolerances and tie rule and reports every grid point. This remains an approximate validation-only descriptive control, not the original confirmatory gate.
- Checkpoint, shared-initialization and 8,000-batch-digest guards remain intact. The job uses the existing owner and ledger, a 296-second timer plus four owner allowances, a fresh output name, and no test-set path or training operation. The output directory and owner lock are currently absent.

This PASS authorizes exactly one command:

`.venv/bin/python -m execution.paired_behavior.job`

It must be launched once, polled to an explicit terminal result, and never relaunched after a yield. Any identity, route-binding, nonfinite, timeout, artifact or ledger failure stops the analysis rather than relaxing the plan. One trained seed remains exploratory and cannot establish a general architecture advantage, equivalence or creativity.

Static review only; no independent tests, inference or ledger charge.
