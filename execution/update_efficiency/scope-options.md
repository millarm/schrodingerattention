# Multi-milestone scope options — not a frozen protocol

2026-09-27: User superseded the single30% target before any new runtime. Await
clarification; no implementation/training/test launch. Historical evidence below
is exploratory and cannot supply fresh confirmation.

## Two interpretations requiring a user choice

1. **Absolute valid-route quality:**15%,30%,45%,60%,75% exact shortest-route
   success. Historical8k softmax mean is38.198%;45/60/75 are beyond observed
   baseline maturity and likely censored in a4k study. Report those honestly;
   reaching them is not guaranteed by more updates or the remaining budget.
2. **Fractions of a fixed softmax reference:**15/30/45/60/75% of historical38.198%
   correspond approximately to5.730/11.459/17.189/22.919/28.649% absolute Q.
   This measures progress toward that fixed reference, NOT these percentages
   of task mastery. Most lower targets probably cross before500; a500-update
   grid cannot resolve them. Reference must be frozen, not recomputed from new
   favorable checkpoints/seeds. A different intended reference needs definition.

## Retained early evidence (read-only extraction, no inference)

From COMPLETE `replication-SEED-MODE-8000/result.json`,
`result.events[update].routes.t1_k32.mixture.Q`, all at the same T1/K32:

|Seed|SM Q at0|SA Q at0|SM Q at500|SA Q at500|
|---|---:|---:|---:|---:|
|1702|0.0260%|0.0260%|26.1019%|26.1702%|
|1703|0.0570%|0.0570%|23.4587%|22.8271%|
|1704|0.0065%|0.0065%|22.5814%|23.3903%|
|1705|0%|0%|22.0459%|21.3997%|

Historical1k/2k/4k/8k mean SM Q is27.383/30.599/34.003/38.198%; SA
28.096/30.948/33.866/37.749% (`execution/seed_replication/trajectories.md`).
Seed1702 falls from26.10% at500 to24.47% at1000, so monotonicity and interpolation
would be unsupported. Nonlinear stage-dependent differences are plausible but
these observations do not establish a fresh architectural effect.

## Prospective design consequences, not yet selected

- Early grid must be denser if lower milestones are the target. Existing trainer
  stores100-step checkpoints, so0/100/200/300/400/500 can be scored additively.
  A50 checkpoint needs explicitly reviewed schedule instrumentation; do not
  pretend it is already saved. More endpoints cost resources even though runtime
  is not a scientific endpoint; resource feasibility must be reconsidered.
- Freeze milestone guards: a single stringent KL/challenge floor for all early
  targets can make distinct milestones collapse to the same guard-limited event.
  Decide whether target crossing is quality-only with separate guardrail reporting,
  or appropriately fixed target-specific guards; neither is silently inherited.
- Quantify nonlinear departure with predeclared paired Q differences across
  stages and changes in those differences (difference-of-differences), plus
  update-to-target intervals/ratios. A crossing/sign change alone is not proof of
  meaningful nonlinearity. Freeze a practical magnitude and replication rule;
  checkpoints/targets are correlated, not independent seed replicates.
- Preserve right-censoring, isolated-crossing disclosure and interval uncertainty.
  No selecting favorable target or grid after fresh results; no mature-equivalence
  claim from relative low targets. Four fresh seeds remain a modest exploratory
  screen on reused validation maps, not broad confirmation.

Next action: user clarification, revised concise scientific/resource protocol,
Sol PASS, then resume implementation. Existing source drafts remain unaccepted.
