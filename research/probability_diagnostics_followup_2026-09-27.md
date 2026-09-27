# What worsening KL does and does not establish

2026-09-27. Follow-up to the
[reviewer's response](https://github.com/millarm/schrodingerattention/pull/1#issuecomment-5858424227)
and the [early-learning refocus](early_learning_refocus_2026-09-27.md).
This document qualifies the interpretation using existing saved scores.
It introduces no new model evaluations or claim of a confirmed mechanism.

## Two observations from the saved pilot scores

At 16,000 updates, weighted policy entropy ranges from 0.377889 to 0.395602
nats. The oracle entropy is 0.372289 nats on the same scoring bank. Entropy
has fallen since 1,200 updates, but remains above the oracle average in every
run. This does not demonstrate uniform overconfidence. Average entropy also
cannot establish whether individual states are well calibrated.

The saved `proper.weighted.nonoptimal_mass` values show that probability
assigned outside the oracle's action support decreases in every run:

| Seed / model | Outside-support mass at 1,200 | At 16,000 |
| --- | ---: | ---: |
| 2201 softmax | 9.4264% | 6.9304% |
| 2201 Schrödinger | 9.2937% | 7.0336% |
| 2202 softmax | 8.6620% | 7.4286% |
| 2202 Schrödinger | 8.6718% | 7.0083% |

These are the existing map- and stratum-weighted measurements, not unweighted
state averages. They come from the four owners' saved `score-1200.json` and
`score-16000.json` files under
[the update-count pilot](../execution/update_efficiency/attempts/).

KL and Brier still worsen over this interval. Consequently, the aggregate
observations alone do not identify the source of the deterioration. Larger
errors on a subset of states and a poorer distribution among oracle-supported
actions are both possible. The proposed diagnostic will measure these patterns.
It will not assume that falling entropy, rising KL, or rising route success
alone explains the others.

## Additions to the early-learning diagnostic

For each fixed comparison, retain the identity and original weight of every
state. Define an action as oracle-supported when its oracle probability is
positive. Take the policy argmax over legal actions using the evaluator's
existing deterministic tie rule. An off-oracle action is not necessarily an
illegal action.

Partition states into four exhaustive transition groups:

1. The argmax stays on oracle support.
2. It moves from on support to off support.
3. It moves from off support to on support.
4. It stays off support.

Report each group's prevalence, conditional mean KL change, and additive
contribution to the full weighted KL change. Empty groups have zero
contribution and an undefined conditional mean. Preserve negative contributions
and require the four contributions to reconstruct the full change.

A complementary decomposition separates two sources of teacher-relative KL.
For one state, let `q` be the oracle distribution, `p` the policy, and
`m = sum(p[a] for a where q[a] > 0)`. When `m > 0`,

```text
KL(q || p) = -log(m) + KL(q || p conditioned on oracle support).
```

The first term measures loss of probability from oracle support; the second
measures disagreement within that support. Both use probabilities already
available from proper scoring. Aggregate mean outside-support mass and mean
`-log(m)` need not change in the same direction, so the latter must be measured
rather than inferred from the table above. Numerical validation and exact
weighted reconstruction are required.

These additions use the same checkpoints, state bank, and inference budget.
Their interpretation remains descriptive; neither transition groups nor this
identity establish a causal explanation. The methodological amendment fixes
the comparison points and implementation tests before dense scoring starts.

## Sample-size planning

The review now acknowledges that its power table depends on a standard
deviation estimated from only four seed pairs. We will not adopt its point
sample-size estimates as reliable requirements. A future confirmation design
should state a precision target, assess uncertainty in the seed-level variance
for the actual endpoint, and show sensitivity to that uncertainty. The current
two-pair diagnostic cannot provide a precise replication-variance estimate.

The 200,000-update continuation remains on hold. No conclusion here authorizes
new training, a learning-rate sweep, or access to the final-test split.
