# Paired training and behavior — completed; independent final audit PASS

Schrödinger attention learns and takes a measurably different path in this
single paired run. At 8,000 updates it has better route success than softmax,
but costs about 3.27× as much measured training-core time and does **not** show
higher valid novel yield at the same temperature T=1. This is exploratory evidence, not a replicated
architecture advantage or proof of creativity.

## Equal training exposure

Sol's `training-review.md` independently passed all 8,000 paired batch digests,
81 checkpoint links, saved sampler states and 40 shared initial tensors.
Same data, optimizer, seed and 512,000 state exposures; no new test-set access.

| Updates | Softmax sampled success | Schrödinger sampled success | SA − SM |
|---|---:|---:|---:|
| 1,000 | 21.17% | 20.78% | −0.38 pp |
| 2,000 | 27.14% | 27.68% | +0.54 pp |
| 4,000 | 29.60% | 31.64% | +2.04 pp |
| 8,000 | 34.23% | 37.17% | +2.94 pp |

Success is exact shortest-route validity, T=1 and K=32, equal-map routine/challenge
80/20 weighting. At 8,000 greedy success is 53.85% versus 56.72%. Training-core
time is 38.82 versus 126.85 seconds. Timing is descriptive from sequential
historical runs, not a randomized benchmark or equal-time quality comparison.

## Different behavior, not uniformly better behavior

Read-only raw-record calculations independently audited PASS (with the explicit
route-order limitation below) find at 8,000:

- 215/512 greedy problems solved by both, 65 only by SA, 50 only by softmax,
  and 182 by neither. SA is not simply producing the same solutions more often.
- Mean action-probability TV is 0.0969; weighted argmax disagreement is 11.33%.
  Of 118 raw differing state choices, 89 are two different q-optimal actions.
- Observed valid route-set Jaccard is about 0.316, conditional on nonempty unions;
  69 problems have no valid samples from either model. Finite samples do not
  reveal complete policy supports.
- Distinct valid routes/K improve (.25928→.28343), but distinct valid novel
  routes/K do not (.008984→.008789); novel valid sample mass also decreases.

Mean predicted entropy is lower for SA (.41661 vs .43042), not higher. Both
exceed oracle entropy .37229. SA has slightly better mixture KL/Brier, but worse
mixed-challenge KL (.62203 vs .58906) and better routine KL (.32379 vs .34718).
Entropy alone is not calibrated uncertainty; these findings do not support a
blanket “more uncertainty produces more creativity” explanation.

## Frozen goal/map transfer comparison

The previously fixed A/B/C cohorts were reused without rebuilding or selection:
24 maps, 144 routes and 768 matched states per cohort. At 8,000 updates:

| Cohort | Softmax T1 success | SA T1 success | SA − SM | Softmax greedy | SA greedy |
|---|---:|---:|---:|---:|---:|
| A: seen pairs/maps | 54.99% | 55.47% | +0.48 pp | 82.64% | 79.17% |
| B: new map-specific goals | 48.33% | 51.02% | +2.69 pp | 67.36% | 72.22% |
| C: unseen routine maps | 39.15% | 44.53% | +5.38 pp | 59.03% | 68.75% |

SA's matched-state KL is lower in A/B/C (.10019/.15023/.19742 versus
.12007/.16656/.24118). The seen-pair greedy regression prevents a claim of
uniform improvement. At 1,000 updates all three sampled-success differences
slightly favor softmax; at 4,000 they favor SA by 1.69/0.52/2.99 pp. This is a
learning-path difference in this run, not merely a fixed output perturbation.
Geometry and path-multiplicity confounds across cohorts remain; do not causally
rank map versus goal bottlenecks from the sizes of these gains.

## Predeclared approximate quality control

| Policy | T1 or tested temperature | Sampled quality | Distinct valid novel routes / K |
|---|---:|---:|---:|
| Softmax reference | 1.00 | 34.23% | 0.8984% |
| SA | 0.75 | 44.21% | 0.9521% |
| SA | 1.00 | 37.17% | 0.8789% |
| SA | 1.25 | 29.82% | 0.8057% |

**Quality matching failed.** The closest predeclared point is SA T=1, still
2.94 pp above the softmax target, outside the 2 pp mixture tolerance. The grid
was not expanded. Although SA T=.75 has greater novel yield, its much higher
quality confounds interpretation. There is no quality-controlled novelty
advantage demonstrated by this experiment. These validation-only tolerances
are exploratory, not the original confirmatory experiment's quality gate.

## Mechanism and learning records

All per-update CE/batch/timing traces and 100-update gradient/parameter summaries
are retained in the immutable training owners. At the final SA update, gradient
norm is .9731 and update/weight ratio .001898; dt values range .0472–.0637.
This endpoint does not suggest a stopped optimizer, but it is not a causal
mechanism diagnosis.

Existing scheduled 128-state validation probes (no extra inference) show local
attention TV versus same-hidden-state softmax rising from .0411 at 1k to .0507
at 8k. Yet final output TV versus the SAME trained SA with dt=0 falls from
.0243 to .0175; final greedy action disagreement is 2.34%. At 8k dt=0 actually
lowers mean probe CE by .01757. Thus direct evolution is active but these small
probes do not establish it causes SA's training advantage. A same-trained-model
dt0 counterfactual is not independently trained softmax.

## Limits and completion

There is only one training seed; correlated problems, states and samples do not
supply independent architecture replications. Same-temperature comparisons have
different quality. Raw route rows omit start/goal and rely on the audited fixed
dataset/evaluator order; state comparisons have exact saved ID/q alignment.

The first additive analysis failed review and was not launched. Following an
explicit narrow user-approved Astra implementation exception, corrected code
passed `astra-analysis-review.md` and one analysis attempt completed. Frozen
A/B/C and both additional SA temperatures have now run. Historical failures,
blocked versions and the earlier partial report are preserved unchanged.

Evidence: `plan.md`, `plan-command-review.md`, `training-review.md`,
`read-only-behavior.md`, `readonly-behavior-review.md`, and `analysis-review.md`.
Sol also independently recomputed greedy route validity with zero mismatches;
this corroborates order but cannot prove permutations among all-invalid groups.
One SA resume command completed
in session 23567 with explicit exit 0; owned runtime 188.72458 seconds plus four
seconds of allowances. No further training is planned.

The sole analysis command `.venv/bin/python -m execution.paired_behavior.job`
used session 23277, polled to explicit exit 0. Immutable output:
`../model_training_comparison/paired-behavior-analysis-001/`; owner COMPLETE,
50.197826 seconds runtime plus four seconds allowances. Exact raw state/route
comparisons, old SM/new SA cohort results, identities and all grid outcomes
are manifest-bound there. No test-set release, additional seeds or extra training.

Independent final auxiliary audit: **PASS**, `auxiliary-results-review.md`.
It verified immutable identities, raw/normalized metrics, paired cohort deltas,
quality-match failure and the counterfactual sign. Final operational debit is
2065.331896587045/7200 seconds (281.232701125014 added this cycle, including
4.7 seconds of final audit). Original budget remaining: 5134.668103412955 seconds.
The requested exploratory comparison is complete; no further experiment is running.
