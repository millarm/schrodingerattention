# Review 00 — model-training comparison plan

**Verdict: CHANGES REQUIRED (two bounded specification corrections).**

Reviewed `model_training_comparison_plan.md` SHA256
`1474790785dc9a39c6e706d59f78d00dc4cc43b05870b25e5b905bff12f380fd`
against the accepted pool512 dataset/result and inherited v2/v3 scientific
criteria.  This is a plan-only review; no implementation, tests, profiling, or
training were run.

## Findings

1. **The quality estimand used by stopping, temperature matching, controls, and
   noninferiority is not defined explicitly.**  Section7 defines distinct-route
   `U_valid/32` and repeated-novel `V_novel/32`, but never defines the repeated
   valid-attempt quantity used as “quality.”  Elsewhere the plan uses T1 quality,
   a reachable90% quality point, matched quality, mixture quality, and routine /
   mixture / challenge quality bounds.  These must all be frozen as the same
   attempt-mass estimand—normally `V_valid/K`, the number of attempts that are
   exact valid shortest completions divided by K, with repeats included, followed
   by problem→map→stratum0.8/0.2→seed weighting.  State explicitly whether greedy
   is the corresponding one-attempt indicator and that `U_valid/K` cannot be
   substituted.  Bind the uniform-legal and initialization comparisons to the
   same K, RNG/common-uniform, aggregation, and stratum definitions.  Also spell
   out that the challenge headroom quantity is `U_valid/M` if that inherited
   normalized coverage is intended.  Without this, gates can change meaning by
   implementation choice.

2. **The fixed sampled-state bank is not byte-level reproducible yet.**  The rank
   expression `SHA256("route-score-v1", canonical bytes, goal, current)` does not
   specify concatenation/domain encoding or a collision tie-break.  Freeze the
   exact byte serialization (tag encoding, fixed-width/endian integer fields and
   no ambiguous concatenation), define the candidate set as the deduplicated
   union of `(goal,current)` states induced by the split's selected problems with
   `current != goal` and finite reachability to that goal, and order by
   `(digest, goal, current)` before taking32.  Hash both the ordered candidate
   inventory and selected bank, persist actual per-map counts, and apply the stated
   equal-state-within-map weighting when fewer than32 exist.  Use the same frozen
   rule for training, validation, and test while preserving the no-test-release
   boundary.  This closes selection ambiguity without reverting to exhaustive
   scoring.

## Items otherwise accepted

The paired seed1701 diagnostic through1,000 updates is an honest exploratory
amendment and remains subject to technical/resource stops.  The later
baseline-selected exposure T is prospectively disclosed, uses no SA advantage to
choose T, and defines a baseline-adequate-exposure comparison rather than equal
convergence.  Continuing SA from its exact1,000-update checkpoint is appropriate.

The paired minibatch streams, shared-base initialization, active8-vs8 scalar
count, identical optimizer policy, legal-only action mask, verifier denominators,
common rollout uniforms, validation-only operating points, fresh main seeds,
checkpoint censoring, equal-time slack disclosure, and separation of local SA
probes from propagated/full-path effects are fair and leakage-conscious.  Normal
training excludes expensive matrix-invariant probes while fixed scheduled probe
banks remain outside the timing loop; finiteness checks remain in training.

The five-pilot/four-replicate variance add-back and ten-pair main inference retain
the accepted limited power interpretation.  Failure to establish equivalence is
not equated with equality, and incomplete cohorts remain inconclusive.  The plan
properly separates SA usability, dynamics, novelty, and mechanism conclusions.

Budget arithmetic is consistent: prior debit923.003597253 leaves
6276.996402747 seconds; A400+B2000+C2200+D1300+reserve376.996402747 equals that
remainder.  The two prospective forecasts include training, checkpoint,
evaluation, rollout, aggregation, serialization, and audit work, so actual
feasibility can be decided without changing seeds or science.  No execution is
authorized by resolving these plan-text findings.
