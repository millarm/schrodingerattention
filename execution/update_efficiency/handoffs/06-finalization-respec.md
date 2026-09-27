# Finalization respec handoff

Bounded implementation of `spec-04-finalization-respec.md`; only driver
orchestration/finalization lines and driver-specific tests changed. Historical
reviews, handoffs, `study.py`, scientific configuration, and the ledger remain
unchanged.

## Exact source set

- `execution/update_efficiency/command.py`:
  `3adda02c82b2eb6a059d890b967950c6718e7406e64dd99fdcfe2dab47f38b4f`
- `tests/test_update_efficiency.py`:
  `07f6aaf4823923296bd6ef00000ef94644b5c7132c6450e55141cca467b1e61f`
- unchanged accounting clarification:
  `7ab55e8e05ca950597e9c7f09c948a8edbd2756f04854d1dc19851dba82c58c6`

## Assertion map

- `test_driver_post_child_overrun_charges_full_failed_terminal` uses a mutable
  clock and supervision spy. Setup leaves a positive watchdog allowance; the
  clean child advances time past the envelope. It asserts one full 21-second A
  charge, FAILED status/terminal, overrun marker, and no COMPLETE path.
- `test_driver_setup_exhaustion_never_supervises_and_records_overrun` advances
  only after the clock start, proves the child is never launched, and asserts the
  full charged A failure plus durable failure reporting.
- `test_driver_b_watchdog_exception_retains_lock` remains independent and proves
  watchdog uncertainty retains the reservation.
- `test_driver_b_overhead_append_uncertainty_retains_without_retry` invokes
  production `main` with a tiny complete owner for both pre-write failure and
  write-then-raise overhead durability failure. It asserts retained lock, exact
  visible-row count, no fallback, and no retry.
- `test_driver_final_terminal_failure_retains_a_and_b_reservations` injects the
  final COMPLETE terminal failure after clean A and B accounting, asserting that
  the common release predicate retains both reservations.

## State-machine correction

The release predicate now requires: successful required accounting settlement,
verified child cleanup, and a durably completed final driver terminal, with no
latched finalization uncertainty. B reconciliation does not itself certify
accounting; only a successful `settle_owner` does. The exception path does not
retry or recertify a settlement already begun. A failed COMPLETE-terminal write
latches uncertainty; a best-effort FAILED terminal cannot release that lock.

## Static-only statement

No imports, tests, subprocesses, model/runtime calls, smoke/suite/production
commands, or ledger writes were performed. This handoff is for exact static Sol
review only.
