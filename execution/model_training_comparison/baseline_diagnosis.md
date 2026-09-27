# Baseline learning/generalization diagnosis

Status: complete; [independent Sol diagnosis audit PASS](diagnosis-results-review.md). No training,
fixes, dataset changes or test release. The completed comparison is unchanged.

## Diagnosis in brief

The baseline is learning, but three problems coexist: **incomplete fitting of
whole training routes, a late generalization gap on these banks, and a population
mismatch between training-DAG and broader-state validation scoring.** The original
broad bank remains a valid broader-state generalization endpoint, not incorrect
scoring. There is no evidence of a dead optimizer or
obvious coordinate/masking bug. The exact architectural cause remains unproven.

At 8,000 updates, even **training** routes achieve only 51.37% valid shortest
solutions per sampled attempt, below the frozen 70% target. Held-out routine maps
achieve 39.36%, and mixed-composition challenge maps 13.67%. Thus fixing only
held-out generalization would not yet make this baseline usable.

## New controlled-eligibility evidence

One inference-only job rescored the same four saved softmax checkpoints. Training
uses its original 2,048 fixed DAG states; validation uses a new, deterministic
1,024-state bank drawn from shortest-path DAGs of its selected problems. Both use
32 states/map and equal-map weighting; routine and challenge remain separate.

| Updates | Training DAG KL | Routine validation DAG KL | Original broad routine KL | Mixed validation DAG KL |
|---:|---:|---:|---:|---:|
| 0 | 1.00728 | 0.98617 | 0.85704 | 0.98629 |
| 1,000 | 0.20421 | 0.19561 | 0.30054 | 0.56823 |
| 4,000 | 0.14249 | 0.18291 | 0.29417 | 0.58320 |
| 8,000 | 0.10071 | 0.19376 | 0.34718 | 0.66695 |

Lower KL(q||p) is better; it removes irreducible teacher entropy.

- At 1,000 updates there is no unfavorable seen-versus-routine DAG gap in these
  banks. By 8,000, training fit improves strongly while routine DAG validation
  plateaus/slightly worsens. This is consistent with late overfitting or limited
  transfer, not proof of a particular cause.
- Directly comparing the broad bank to training DAG states enlarges the observed
  gap: at 8,000 its
  routine KL is 0.34718, versus 0.19376 after aligning state eligibility. These
  are different selected state populations, so their difference is not a causal
  estimate of how much one design choice harmed training.
- A meaningful gap survives alignment: training versus routine DAG Brier is
  0.05310 versus 0.10159 at 8,000. Teacher entropies are almost identical
  (0.27982 versus 0.27942 nats); average remaining distances are similar
  (7.75 versus 7.85 steps). Matching these means does not match all distributions.
- Mixed challenge KL worsens from 0.56823 to 0.66695 while training improves.
  This stratum combines unseen obstacle composition and novelty-based selection;
  the extra difficulty cannot be attributed to composition alone.

The original bank sampled all reachable cells for selected goals, whereas training
samples saved DAG states. Before selecting 32/map, those pools contain 55,054
states on 32 validation maps versus 32,946 on 64 training maps. The new bank aligns
the eligibility rule, **not** maps, goals, geometry or every difficulty variable.

## Why decent one-step fitting still gives poor routes

At 8,000, the directly measured results are:

| Route population | Greedy success | T1/K32 valid attempt yield |
|---|---:|---:|
| Seen training problems | 79.00% | 51.37% |
| Held-out routine | 62.24% | 39.36% |
| Held-out mixed challenge | 20.31% | 13.67% |

Training pass@32 is 97.36%: most seen problems produce at least one correct route
among 32 samples, but individual draws are unreliable. That does not meet the
predeclared quality requirement.

An exact shortest route requires 14–16 consecutive optimal moves. Any
non-distance-decreasing move irreversibly fails the criterion, even if the model
later reaches the goal. Residual local errors can therefore cause substantial
route failure; exposure bias *after* the first error is not required to explain
this metric. Do not multiply a bank-average probability and present it as an
empirical success probability. Actual rollouts above already measure the outcome.

On the fixed DAG banks, probability mass on nonoptimal actions at 8,000 averages
4.39% for training, 7.40% for routine validation and 15.46% for challenge. Those
are state-bank averages, not the rollout visitation distribution.

## What the evidence does not establish

Across all 80 retained optimizer summaries, gradient norms range 0.503–2.714,
42.5% are clipped, and update/weight ratios remain 0.00163–0.00352. Every parameter
group has a positive sampled minimum gradient norm. This argues against an
obviously stopped/dead optimizer, but does not prove the learning rate, clipping
or capacity is adequate.

Code inspection preserves all walls/current/goal coordinates in 12 rows of
36 features, projected to 64-dimensional tokens. The legal mask excludes only
walls/edges, and the exact teacher/verifier are consistent. No obvious information
loss or masking bug was found. However learned absolute row positions and
column-specific input weights impose no spatial equivariance or local planning
structure. A weak spatial inductive bias is a plausible hypothesis, not a
diagnosed root cause; neither insufficient depth nor memorization is proven.

All findings are retrospective and descriptive from **one trained seed**. States,
maps and 32 sampled attempts are not independent training replications. No claim
about Schrödinger advantage, calibration of whole-route confidence, or creativity
follows from this baseline diagnosis.

## Smallest next validation experiment — proposed, not executed

Before another architecture comparison, freeze a three-way checkpoint-only
baseline check: (1) seen maps/seen goal pairs, (2) seen maps/new goal pairs, and
(3) unseen routine maps, all with the same DAG eligibility, matched remaining
distance/branching strata and exact route verifier. This separates reliance on
particular goal/state combinations from map transfer more directly. Keep mixed
composition separate. Then replicate the surviving diagnosis on another training
seed before changing the spatial encoding or optimizer. Do not simply train
longer: the observed later fitting gains did not improve aligned validation fit.

## Evidence and budget

- [Accepted specification](baseline-diagnosis-spec.md),
  [spec review](diagnosis-spec-review.md),
  [implementation PASS](diagnosis-implementation-review.md).
- [Immutable raw diagnostic](baseline-diagnosis-001/baseline_diagnosis.json) includes
  checkpoint/input/source hashes, exact selected states/q, per-state score arrays,
  bank properties and all training rollout attempts. Owner file manifest retained.
- Command: `.venv/bin/python -m execution.model_training_comparison.baseline_diagnosis_job`.
  Exactly one launch, session 57420, polled to explicit exit 0; owner COMPLETE.
  Existing model/data/evaluator sources and all completed-study artifacts unchanged.
- Focused tests: 2 passed, charged 0.574304 seconds. Owned diagnostic elapsed
  17.438946874987 seconds plus 4 seconds disclosed startup/finalization allowances.
  Summary allowance: 2 seconds. Independent final audit: 0.8 seconds.
  Final diagnostic debit 24.813250874987 of the authorized 120 seconds;
  global debit 1746.700972463049 of 7,200, leaving 5453.299027536951 seconds.
  No pending compute, additional inference, fixes or training.
