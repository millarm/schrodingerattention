# Science correction for Sol full-static 06

This is the bounded science-only correction requested by
`reviews/06-full-static.md`.  `command.py` and all driver-test functions remain
unchanged.  No runtime authority is implied.

## Frozen source inventory

- `execution/update_efficiency/study.py`:
  `a62a37248421660f94edce139a7e9ca471890bab8c0ba4463edd8ffb6c396204`
- `tests/test_update_efficiency.py`:
  `7dbb7c3129646f89d1fd8c47ff92326d0b2875c33e4294510683e0cabc07ebcf`
- frozen driver `execution/update_efficiency/command.py`:
  `3adda02c82b2eb6a059d890b967950c6718e7406e64dd99fdcfe2dab47f38b4f`

## Exact correction map

1. `_score_metrics` records `teacher_entropy` from accepted
   `weighted.entropy_q`; optional `policy_entropy` is separately named from
   `weighted.entropy_p`.  `validate_scoring_points` requires finite teacher
   entropy.  The grid test covers missing/nonfinite teacher entropy, and the
   actual S2 fixture compares each compact teacher value to raw accepted proper
   `weighted.entropy_q`.
2. `validate_pair_identity` now consumes the emitted owner schema: `config_hash`,
   the exact six input IDs, source hashes, all four validation-bank hashes plus
   row count, training-support hash, shared initialization and all16000 batch
   digests.  The pair test mutates seed/mode/shared/config/input/source, every
   bank field/row count, support and batch prefix individually.
3. `aggregate_all` requires the exact two ordered owner-plus-score bundles and
   emits all13 stagewise two-seed Q/KL/challenge gaps, equal means and raw rows.
   Its `mixed` guard applies only to positive mean Q, with raw margins retained
   and a 1e-12 numerical equality guard around the strict .02 nat / 2 pp
   thresholds.  It also reports fixed C values, mean/range, materiality,
   same-sign and screen.  Literal tests cover equality at abs(mean C)=1 pp,
   same/opposite signs, exact margin boundaries, each strict guard, and a
   nonpositive-Q non-mixed case.
4. The same aggregate schema binds canonical endpoint bytes to compact owner
   score hashes, derives tolerant and exact 30%/38.198% tables for both seeds,
   and retains every per-seed mode milestone plus observed/censored comparison.
   Tests assert two rows in each of the four tables and retain observed,
   final-unconfirmed and initial-anomaly cases without a completer-only result.

No imports, tests, subprocesses, model/data loads, training/evaluation,
smoke/suite/production command, or ledger writes were executed during this
correction.  `reviews/06-full-static.md` is historical CHANGES REQUIRED and
unchanged; Sol must perform the designated re-review before any runtime.
