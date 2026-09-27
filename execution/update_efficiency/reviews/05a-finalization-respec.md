# Sol static review — bounded finalization respecification

**Verdict: PASS (driver scope only).**

`FINALIZATION_RESPEC_REVIEW_VERDICT: PASS`

This review is limited to the two residuals explicitly authorized in
`spec-04-finalization-respec.md` and their direct regression consequences. It
does not reopen closed helper scope, accept `study.py`, or authorize smoke,
suite, training or production. Static review only: no imports, tests,
subprocesses, runtime work or ledger writes were performed.

## Exact version reviewed

- respecification `execution/update_efficiency/spec-04-finalization-respec.md`:
  `ee4306d8186260bf12449dd4c13f56ce65776173fd60741eb108ea414bae9bdb`
- `execution/update_efficiency/command.py`:
  `3adda02c82b2eb6a059d890b967950c6718e7406e64dd99fdcfe2dab47f38b4f`
- `tests/test_update_efficiency.py`:
  `07f6aaf4823923296bd6ef00000ef94644b5c7132c6450e55141cca467b1e61f`
- handoff `execution/update_efficiency/handoffs/06-finalization-respec.md`:
  `e5a320a3c6f6c100b40ecafbdad2bc40abb6b6c12ffdf79f8a80691021d94aee`
- unchanged accounting clarification:
  `7ab55e8e05ca950597e9c7f09c948a8edbd2756f04854d1dc19851dba82c58c6`

Historical review `05-driver-final.md` remains preserved as the record that
triggered this explicitly authorized bounded respecification.

## R1 — literal overrun branches: closed

The old exhausted iterator is replaced by isolated mutable clocks:

- `test_driver_post_child_overrun_charges_full_failed_terminal` leaves a
  positive nine-second child allowance, proves supervision is called, advances
  time only inside the clean child stub, and then drives the normal A terminal
  through `actual_charge=21 > envelope=10`. It asserts one unclamped 21-second
  FAILED charge, `resource_overrun=true`, and no successful return.
- `test_driver_setup_exhaustion_never_supervises_and_records_overrun` advances
  on the remaining-time read, proves the child cannot be called, and verifies
  the separate exception branch records the same full 21-second FAILED charge
  with an explicit overrun marker.
- `test_driver_b_watchdog_exception_retains_lock` is independent of both clocks
  and continues to verify cleanup uncertainty plus permanent fallback retains
  the reservation.

The source supports these distinctions. Both the normal A terminal and the A
exception accounting path compute actual elapsed plus the one-second allowance,
check the exact envelope/current cap state, retain the full charge, and prevent
COMPLETE on overrun. There is no clamping or outcome reinterpretation.

## R2 — durable finalization certainty: closed

The release state now separates:

- `accounting_certain` — all required charge/overhead settlement returned;
- `cleanup_certain` — explicit watchdog cleanup verification or pre-child setup;
- `terminal_certain` — the final driver terminal was durably written; and
- latched `finalization_uncertain` — a failed COMPLETE-terminal write.

Release requires all three positive certainties and no finalization uncertainty.
Normal owner reconciliation no longer certifies accounting by itself.
`settlement_started` prevents the exception path from retrying or recertifying a
failed/uncertain overhead append.

The literal orchestration tests cover the required failure modes:

- `test_driver_b_overhead_append_uncertainty_retains_without_retry` runs actual
  production `main` with a complete synthetic owner for both an overhead append
  that raises before writing and a write-then-raise durability failure. The
  reservation remains, visible rows are exactly one/two as appropriate, no
  fallback is appended, and settlement is not retried.
- `test_driver_final_terminal_failure_retains_a_and_b_reservations` injects a
  failure only for the final COMPLETE terminal after otherwise successful A and
  B accounting. The failed COMPLETE write latches uncertainty; a best-effort
  FAILED terminal cannot restore certainty, and both reservations remain.
- Existing clean A/B successes and clean charged failures remain governed by the
  same release predicate and are unchanged regression coverage.

The prospective accounting rule also remains intact: a unique normal owner
charge C is reconciled first, uncovered driver overhead is
`max(0, E-C)`, and successful settlement accounts `max(C,E)` without rewriting
or duplicating the owner charge. The respecification did not alter science,
budgets, authority paths or ledger schema.

## Gate

The two review-05 blockers do not recur, so the bounded driver respecification
passes. This is not the `DRIVER_REVIEW_VERDICT: PASS` required by the runtime
authority path. `command.py` deliberately requires the future consolidated
`reviews/06-full-static.md` for smoke/suite and `reviews/08-implementation.md`
for production. The full scientific runner/composition and its tests remain
unimplemented/unaccepted in this review; no runtime is authorized.

