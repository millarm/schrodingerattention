# Science S1 handoff — pure estimators

This is the completed S1 pure-estimator milestone from
`spec-05-science-completion.md`. S2 actual owner/trainer/evaluator composition
is explicitly pending and was not edited or authorized here.

## Exact version

- `execution/update_efficiency/study.py`:
  `aba07b035dec2bdc65432d4aa59a86ed08aeea74b2799c7bebccac5f781fa233`
- `tests/test_update_efficiency.py`:
  `464d7795cc26fde117cbab583e27748c4cb25125b74ce721464aea3059860c15`
- frozen accepted driver remains:
  `3adda02c82b2eb6a059d890b967950c6718e7406e64dd99fdcfe2dab47f38b4f`

## Pure estimator / assertion map

- `validate_scoring_points` enforces the exact 13-point v3 grid and finite Q,
  KL, Brier, entropy and supplied challenge-Q values.
- `q_plateau` builds every needed 2k M mean (4000 through 16000), raw G values,
  sustained terminal suffix, temporary plateau/rebound, censoring, and negative
  deterioration labels. `test_v3_grid_finite_and_q_plateau_known_values_and_rebound`
  asserts flat, rising, falling, rebound, exact low-gain equality, duplicate,
  missing and nonfinite cases.
- `ce_plateau` validates exact 1..16000 IDs, emits literal 100-update blocks and
  2k means, requires a positive denominator, and uses the same suffix logic.
  `test_ce_blocks_windows_denominators_and_suffixes_are_literal` asserts exact
  block/mean values and bad denominator/identity rejection.
- `quality_milestone`, `milestones`, `fragility_flags`, and
  `milestone_comparison` keep crossing separate from fragility, retain lag and
  irregular intervals, exact/tolerant sensitivity, and censored comparisons.
  `test_milestones_thresholds_irregular_lag_and_censoring` covers both milestones,
  threshold equality, initial/isolated/final behaviors, flags and censoring.
- `early_contrast`, `validate_pair_identity`, and `aggregate_all` implement fixed
  two-mode C, full 16000 digest/seed/mode/config/input identity, and descriptive
  two-seed summaries without df3 inference. Covered by
  `test_fixed_contrast_two_seed_summary_and_full_pair_identity`.

## Scope and static statement

The driver and every driver-test function were preserved. No imports, tests,
subprocesses, model/data loads, runtime calls, training, evaluation, smoke,
suite, production command, or ledger write occurred. S2 is the separate pending
composition milestone and needs Astra dispatch after read-only consistency check.
