# Paired training and behavior — completed core result, auxiliary work blocked

Schrödinger attention learns and takes a measurably different path in this
single paired run. At 8,000 updates it has better route success than softmax,
but costs about 3.27× as much measured training-core time and does **not** show
higher valid novel yield. This is exploratory evidence, not a replicated
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

## Limits and remaining work

There is only one training seed; correlated problems, states and samples do not
supply independent architecture replications. Same-temperature comparisons have
different quality. Raw route rows omit start/goal and rely on the audited fixed
dataset/evaluator order; state comparisons have exact saved ID/q alignment.

The additive analysis implementation failed independent review. It was **not
launched**. Frozen A/B/C architecture-transfer scoring and the proposed modest
temperature control have not run. Training's PASS is independent of that
auxiliary blocker. Historical failures and source versions remain preserved.

Evidence: `plan.md`, `plan-command-review.md`, `training-review.md`,
`read-only-behavior.md`, `readonly-behavior-review.md`, and `analysis-review.md`.
Sol also independently recomputed greedy route validity with zero mismatches;
this corroborates order but cannot prove permutations among all-invalid groups.
One SA resume command completed
in session 23567 with explicit exit 0; owned runtime 188.72458 seconds plus four
seconds of allowances. No further training is planned.

Final operational debit: 1993.276966420030/7200 seconds
(209.177770957999 added this cycle, including 6.6 seconds of final behavior audit).
Remaining original budget: 5206.723033579970 seconds. Training and the bounded
read-only comparison are accepted; auxiliary A/B/C and temperature inference
remain NOT RUN pending a separately authorized implementation recovery.
