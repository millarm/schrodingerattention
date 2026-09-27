# Refocus on early learning

2026-09-27. This addendum responds to
[PR #1](https://github.com/millarm/schrodingerattention/pull/1) and the user's
decision to stop the 200,000-update continuation. The historical reports and
their recorded hashes are preserved.

## Decision

The 200,000-update extension is on hold. No continuation training, inference,
tests, or batch coordinator had launched. Its additional compute debit is zero.
The [hold decision](../execution/long_horizon_200k/hold-decision.md) revokes
the previous launch authority and preserves the unfinished implementation.

The next investigation focuses on the first 3,000 training updates. Saved
checkpoints every 100 updates allow a denser examination without new training.
Its specification and independent review precede new model evaluation.

## What the saved scores show

Validation KL measures disagreement with the oracle action distribution;
lower is better. Across all 13 scored checkpoints in each of the four pilot
runs, the lowest KL occurs at 1,200 updates.

| Seed / model | KL at 1,200 | KL at 16,000 | Increase |
| --- | ---: | ---: | ---: |
| 2201 softmax | 0.288876 | 0.407384 | 41.0% |
| 2201 Schrödinger | 0.296852 | 0.447383 | 50.7% |
| 2202 softmax | 0.287663 | 0.454984 | 58.2% |
| 2202 Schrödinger | 0.284178 | 0.456706 | 60.7% |

In every run, Brier score also worsens and policy entropy falls between these
checkpoints, while sampled valid-route frequency Q increases. These values
come from the saved `score-1200.json` and `score-16000.json` files under the
[four pilot owners](../execution/update_efficiency/attempts/); the minimum was
checked across all 52 score files. No new model evaluation produced this table.

The earlier statement that "8,000 updates was too early" needs qualification:
it described the chosen Q plateau rule. It did not establish that longer
training improved generalization or agreement with the oracle distribution.
The late comparisons measure route performance alongside worsening proper
scores, which makes them a poor basis for a general learning-efficiency claim.

Two qualifications guide the next experiment:

- 1,200 was the first scored checkpoint after initialization. It is the best
  **observed** KL checkpoint, not an established optimum or precise onset of
  overfitting. The saved earlier checkpoints can locate that transition.
- Lower entropy and worsening proper scores support the concern about
  sharpening and overfitting. They do not establish that every improvement in
  valid routes is caused solely by confidence. Greedy routes and independently
  calibrated comparisons can help distinguish the explanations. KL against an
  oracle distribution is also not a direct measurement of calibration alone.

## Questions for the early-learning block

1. When do KL and Brier improve, flatten, and begin to worsen for each model?
2. Does Schrödinger improve faster over a fixed early window, across both
   seeds, when measured by proper scores as well as valid routes?
3. Do improvements in sampled routes coincide with changes in greedy routes,
   policy entropy, and attention behavior?
4. Is the early Schrödinger advantage consistent across nearby checkpoints,
   rather than dependent on one favorable checkpoint?

Here "learning gradient" means the change in a measured score per training
update. Local slopes and fixed-window averages will be reported together with
the raw curves. Checkpoints from the same run are correlated measurements;
they cannot be treated as independent training seeds or forced into a monotone
curve that hides deterioration.

The first block uses existing models and the existing validation panel as an
exploratory diagnostic. Temperature or checkpoint selection on that panel
cannot also supply an unbiased confirmation score. Calibration and learning-rate
tuning need a separate split, and confirmation needs a frozen design with fresh
seeds. The final-test split stays untouched during this diagnostic.

The review's early sign pattern is a useful hypothesis. Its selection after
examining earlier results, and its mix of 1,000- and 1,200-update checkpoints,
prevent treating it as a confirmed advantage. Likewise, the available evidence
does not establish that architecture differences exist only in early training.

Mechanism ablations, additional training maps, and learning-rate comparisons
remain later questions. They will be specified after this smaller diagnostic
shows which early behavior needs explanation.
