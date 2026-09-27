# Re-scoped correction after two revision cycles: output ownership

The protocol's two-revision limit has been reached. Astra identifies the
remaining cause: the attempt exception path confuses an existing output path
with an output directory successfully created by this attempt. Previous tests
covered O_EXCL lock contention but not the independent output-mkdir race.
This is a concrete ownership-state bug, not a reason to waive no-overwrite or
expand the diagnostic. All other Sol residual groups are closed provisionally.

Revised bounded specification (Terra code/tests, Sol re-review, Astra accepts):

- Track output ownership separately from lock/file-descriptor ownership.
  Set the output-owned flag only after this attempt's mkdir succeeds.
- Write `output/attempt.json` only when output-owned is true. If mkdir loses
  a race, retain the other directory and every existing byte; record rejection
  only through the unique external rejected-record path and charged ledger.
- Place descriptor close, owned-lock unlink and signal restoration in an
  unconditional finally around all exception-path logging. A failed log write
  cannot skip cleanup. Never unlink an unowned lock.
- Regression 1: inject output creation with a sentinel attempt.json between
  lock acquisition and mkdir; assert sentinel bytes unchanged, owner lock
  cleaned, charged unique external rejection and no inappropriate write.
- Regression 2: after successful output creation, inject attempt-record write
  failure during an enter/deadline failure; assert owned lock/descriptor/timer
  cleanup and failed ledger status. Retain existing success/timeout tests.

Only touch the new Attempt ownership/error path, its tests, and diagnostic
handoff/ledger. No metric, source-input, scientific-plan or broad safety
refactor. Up to 15s bounded tests; no full analysis. Complete both regressions
and exact hashes in one handoff. Sol independently checks this specific fix
and regression impact; no execution before PASS.
