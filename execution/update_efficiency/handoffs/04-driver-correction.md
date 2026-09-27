# Driver correction handoff

Static driver-only correction for the v3 saturation pilot.  No tests, imports,
subprocesses, model calls, ledger writes, smoke, suite, or production commands
were executed in this handoff.

## Reviewed files

- `execution/update_efficiency/command.py` — SHA
  `2fe115c6f2dd4eb2852cb419cb3c0caa0e3fa3139c3fd074752dc78511ed0ad1`.
- `tests/test_update_efficiency.py` — SHA
  `39e8456819c1ae675972ab05468becd522733bdc25b56c2c72b3d0f24a9952ce`;
  only driver-specific synthetic additions were made.

## Assertion map

- `test_driver_main_a_success_failed_and_exception_charge_once`: invokes `main`
  for successful, nonzero, and supervision-exception A paths; asserts exactly
  one charged terminal and the release/retain distinction.
- `test_driver_main_timeout_descendant_and_accounting` and
  `test_driver_watchdog_descendant_fixture`: exercise the main timeout/accounting
  branch and the reviewed watchdog's actual small child/descendant cleanup
  fixture (for later authorized execution only).
- `test_driver_main_b_complete_failed_and_missing_charge_reconciliation`:
  invokes production orchestration for COMPLETE owner closure, charged FAILED
  owner without a manifest, and missing-charge permanent fallback.
- `test_driver_b_fallback_nonpromotion_and_artifact_negatives`: checks fallback
  non-promotion, malformed/disagreeing UUID records, and escaped paths.
- `test_driver_ledger_prefix_carry_uuid_and_review_authority_negatives`:
  checks prefix/carry/duplicate UUID refusal and that a static driver review
  cannot satisfy production review authority.
- `test_driver_complete_rejects_missing_corrupt_and_escaped_endpoint`: checks
  artifact-closure refusal and escaping endpoint guard.

## Implementation closure

`command.py` binds all source authority including `route_feasibility.py`; takes
the study lock before experiment locks, decision EOF/prefix/carry/UUID/cap
checks; starts the envelope before setup; and charges the explicit one-second
allowance arithmetically.  It records reservation/session terminals, releases
only with both accounting and cleanup certainty, and retains a durable
reservation record otherwise.

Production rejects pre-existing owners/fallbacks before launch, discovers the
actual UUID from pending/final owner artifacts after launch, matches one normal
`attempt_charge`, and never promotes fallback rows.  A matching charged FAILED
owner is not charged again.  Missing owner charges receive exactly one permanent
fallback.  COMPLETE requires terminal/result/index identity, exact 13-point
grid, manifest closure, score/checkpoint hashes, and every path/hash reference
under the owner directory.  Production authority is restricted to the later
`04-implementation.md` implementation PASS and cannot use the driver-only PASS.

## Static evidence

Commands performed were only source inspection, `shasum`, line counting, and
patch application.  No executable verification has been performed; Sol must
inspect this exact version before any authorized runtime work.
