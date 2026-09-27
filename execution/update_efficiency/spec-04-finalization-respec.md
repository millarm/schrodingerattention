# Bounded respecification: two driver residuals only

2026-09-27. Parent directs this repair under protocol section6's explicit
bounded-respecification option after two revision cycles. This is not an Astra
implementation exception, scientific amendment, budget extension or runtime
authorization. Astra specifies; the same sole Terra implements; Sol independently
reviews. Preserve `blocker.md` and reviews03–05 as historical evidence.

## Root cause and boundaries

Sol05 found two specific residuals: the deterministic overrun fixture takes the
wrong control-flow branch, and the release predicate conflates an already
reconciled normal owner charge with completed overhead/terminal durability.
Prior fixes improved ordinary paths but did not represent these failure states.

Change ONLY the relevant orchestration/finalization lines in `command.py` and
the corresponding driver tests in `tests/test_update_efficiency.py`. No refactor
of unrelated helpers, authority paths, ledger schema, production science or
`study.py`. The frozen baseline driver/test hashes are
`0afe1034a5446e9970e9520861a07528f551885d97190409c45713d452fd0e33` /
`90cb6d2d014d55da43f95badfaf1d4f382e25946b63f47dbb9dea597be856b48`.
The overhead arithmetic clarification remains unchanged.

## R1: literal overrun branches

Split the existing combined test into isolated fixtures. Use a deterministic
mutable clock, not an exhausted iterator leaking into the next case.

1. Post-child overrun: setup leaves positive time; a spy proves supervision was
   called once with a positive remaining allowance. The successful child stub
   advances the clock beyond the envelope before returning clean exit. Assert
   one FAILED A charge with actual full elapsed+allowance (not clamped), true
   `resource_overrun`, FAILED driver terminal and no printed COMPLETE.
2. Setup exhaustion: advance before child launch; prove supervision was never
   called. Record full charge and explicit resource-overrun failure in the A
   row/driver terminal, with no COMPLETE. This closes the same reporting contract
   for the actual branch the old fixture accidentally exercised.
3. Keep the existing B watchdog-exception/retained-lock evidence independent of
   the overrun clock fixture. Do not weaken its cleanup-uncertainty assertion.

## R2: distinct durable finalization certainty

Normal owner reconciliation alone is NOT enough for release. Represent these
states explicitly (names are Terra's choice): completed required accounting,
verified child cleanup, and durably completed final driver terminal. Release
requires all three and no latched accounting/finalization uncertainty.

- A required B overhead append must return successfully before accounting can
  be marked certain. On append/write/flush/fsync exception, retain uncertainty
  and reservation. Never let the exception path recertify accounting merely by
  finding the pre-existing normal owner charge again.
- Do not retry an uncertain overhead append or rewrite/repair ledger history.
  A write-then-raise is uncertain even if bytes are visible afterwards. Preserve
  the normal owner/artifacts and any visible overhead row without double debit.
- Final terminal writing must succeed before lock release. If a required final
  terminal write fails, latch finalization uncertainty and retain reservation;
  best-effort failure evidence cannot turn that execution into COMPLETE.
- Clean successful runs and clean, durably accounted failed-child runs retain
  their existing release behavior. Do not turn ordinary failure into success.

Literal tests must invoke actual `main` orchestration with tiny synthetic owner
fixtures and assert exact row counts, retained lock, no COMPLETE and no retry:
(a) required overhead append raises before write; (b) overhead writes then raises
as a flush/fsync-durability failure; (c) final terminal write fails after otherwise
successful accounting. Include A and B final-terminal coverage if the common
predicate handles both. Existing happy-path/clean-FAILED-owner tests remain
unchanged as regressions. No real scientific fixture or model calls are needed.

## Closure gate

No imports, tests, subprocesses, inference or ledger writes before Sol's exact
static PASS. Terra returns ONE complete two-item handoff with source/test hashes,
literal assertion map and no-runtime statement. Sol reviews only this respec and
regression consequences, without reopening closed scope. If the same defects
recur after this bounded respec, stop with a true blocker for user direction;
no automatic further loop or role substitution. Full science/composition remains
a separately unimplemented/unaccepted block even after this driver repair.
