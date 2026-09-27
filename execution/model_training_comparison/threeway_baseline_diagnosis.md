# Three-way baseline diagnosis — complete; independent audit PASS

2026-09-19. The trained baseline performs best on seen pairs, next on new goals
on familiar maps, and worst on unseen routine maps at 8,000 updates. This is a
descriptive one-seed result, not a causal decomposition or Schrödinger comparison.
No training, model changes or test-set access occurred.

## Matched check

All 24 fixed triplets passed (12 I and 12 L); no exclusions. Each cohort has
144 routes and 768 nonterminal DAG states: six routes and 32 states per map.
Actual joint distance/optimal-action-count quotas are equal across A/B/C within
each triplet. Metrics average within map, then equally across maps. Cohorts and
hashes were saved before predictions.

- A: original training pairs; all DAG states occur in saved training.
- B: the SAME maps, with goals absent from every saved training state on that
  map, including suffix supervision; zero exact training-state overlap. Goal
  coordinates can have appeared on other maps.
- C: original routine validation pairs on unseen maps, rank-paired by family.

## Results

Lower KL/Brier are better. Route success requires an exactly shortest valid route.
T1 is sampled success at temperature 1 with 32 samples/problem, not pass@32.

| Updates | A KL | B KL | C KL | A T1 success | B T1 success | C T1 success |
|---|---:|---:|---:|---:|---:|---:|
| 1,000 | 0.23060 | 0.19937 | 0.18820 | 22.92% | 28.78% | 25.15% |
| 4,000 | 0.15447 | 0.16326 | 0.19050 | 40.06% | 42.95% | 34.05% |
| 8,000 | 0.12007 | 0.16656 | 0.24118 | 54.99% | 48.33% | 39.15% |

| At 8,000 updates | A: seen pairs | B: new map-specific goals | C: unseen maps |
|---|---:|---:|---:|
| Brier | 0.06352 | 0.09011 | 0.12614 |
| Nonoptimal action mass | 5.08% | 6.12% | 8.03% |
| Greedy exact-route success | 82.64% | 67.36% | 59.03% |

From 4,000 to 8,000 updates, A improves on both proper scores. B is mixed:
KL worsens slightly (0.16326→0.16656), but Brier improves (0.09151→0.09011).
C worsens on both KL and Brier (0.10898→0.12614), while its T1 route success
improves and greedy success falls (61.81%→59.03%). All three cohorts' sampled
success increases across the trajectory. More training therefore did not simply
harm overall performance; proper distribution fit and route behavior differ.
At 1,000 updates B/C outperform A on several metrics: the final transfer gap
emerges later rather than being constant throughout learning.

## Interpretation and limits

The final A→B→C gaps are consistent with specialization to supervised map/goal
combinations and limited unseen-map transfer. New goals are not an absolute
failure, and even seen pairs retain substantial sampled errors. Exact 14–16-step
success compounds local errors. Neither these findings nor the prior diagnosis
identifies a unique causal representation or optimizer defect.

Matching controls distance and immediate optimal-action count, not full geometry
or branching. Mean route solution counts are A 95.30, B 372.69, C 91.63 (maxima
256/3,820/248). B was not selected under the original Mnovel=0 restriction.
State teacher entropies are close (0.28135/0.28057/0.28196), but this does not
remove route-level differences. The observed drops cannot causally rank goal
versus map limitations. These are retrospective subsets and one trained seed;
many maps/samples do not substitute for independent training replications.
Mixed-composition evidence remains separate. No novelty or creativity claim follows.

## Evidence and execution

Frozen spec: `threeway-diagnosis-spec.md`. Narrow role approval:
`threeway-astra-approval.md`. Exact implementation PASS:
`threeway-astra-implementation-review.md`. Blocked versions and prior closeout
remain unchanged under `threeway-blocked-version/`; historical reviews are retained.

Source SHA256: `7b2a53d37bcae421fbd82ba3c174c0f9f812a051f583faceb8fc6ef7095620ef`.
Five focused tests passed. Exactly one command ran:
`.venv/bin/python -m execution.model_training_comparison.threeway_diagnosis_job`.
Session 61203 was polled to explicit exit 0, never relaunched.

Immutable outputs: `threeway-diagnosis-001/`; terminal `attempt.json` is COMPLETE,
with `output-manifest.json` binding raw files. The neutral ledger charge status
is resolved by that terminal record, not rewritten. Results SHA256:
`46ca7f60bca1ec2a5224d479623b0b69385f36f9acb69e55f3da895c444b9720`.
Pre-inference support SHA256:
`2bcde9c3823a41cc0a0ac7c4383ef1323658ca47b5b7a53336f4f4e2adf9babc`.
Raw checkpoint/input identities, state scores and route attempts are retained.

Independent results audit: **PASS**, `threeway-results-review.md`. It verified
manifests, matching/exposure identities, checkpoint identities, finite scores,
equal-map aggregation and exact rollout denominators without further inference.

Final new diagnostic debit is 37.398222998982/120 seconds:
4.742717833 development, 23.155505165982 owned runtime plus four seconds of
startup/finalization allowances, one disclosed summary/accounting allowance,
and 4.5 seconds of independent audit. Cumulative debit is
1784.099195462031/7200 seconds, leaving 5415.900804537969 seconds. This diagnostic
is closed; no further experiment or training is authorized by this result.
