# Astra D1 repair: frozen static review target

2026-09-26. Narrow user-authorized implementation exception recorded in
`d1-astra-approval.md`. No Python import, test, checkpoint load, model call,
production invocation or ledger mutation has occurred in this recovery.
This is a request for independent **static safety review**, not a test-PASS claim.

## Exact bytes

|Artifact|SHA-256|
|---|---|
|`d1.py`|`e1751fa198a747bfc68a788e6dc8bf61e40b8001048bf6b5145ee17951623fd2`|
|`d1_watchdog.py`|`08deac45b82de6f3636d9f61dabf226d13135e257af6a84ff64313c838d2eb7a`|
|`tests/test_difficult_problem_solving_d1.py`|`671e15f2b5c1f61bda60f40a43abfddadd22e6317de699532da2d618b1cdd7ac`|
|Unchanged ledger|`7f62600c2ae6bd91a53cdcdc0769a4c6e2ab5fdd6523758592a68ec6e1f29782`|

Prior source/test/watchdog bytes are preserved under `d1-before-astra/`.
All accepted scientific helpers remain unchanged. D2/test/training remain forbidden.

## Implemented closure and literal tests

- The producer compares the manifest-bound retained pair against current accepted
  pair validation, retains support/RNG/config/checkpoint authority once per seed,
  corroborates every reused K32 bag using the accepted pure verifier, and keeps
  the historical all-invalid-order limitation explicit. QC-grid authority is the
  analysis manifest, not a newly invented historical event digest.
- Actual producer output is one immutable endpoint write plus a compact index;
  panel, four shared bindings and eight greedy files are separate hash-bound
  records. Selected results contain IDs/metrics, never copied raw bags.
- New counts come from the actual wrapper/evaluator; historical unavailable
  counts are null. Raw component times, endpoint times, bound greedy/proper
  evidence, loading and output-write time remain descriptive. The explicitly
  approved D2 forecast deferral is not presented as measured infeasibility.
- `test_actual_evaluator_counter_and_common_uniform_warm_cache` is the previously
  narrow-reviewed 144-byte adjacent-route smoke, preserved.
- `test_real_producer_dispatches_40_cells_once_under_sink` now exercises the real
  producer/run/owner/sink with ten actual Problems, accepted evaluator and a
  deterministic callable. It asserts the literal ordered 24 calls, 16 reuses,
  40 one-time cell writes, eight caches/greedy files, exact arguments, lock at
  every loader/evaluator, forbidden paths, serialization and compact selections.
- Both `test_actual_owner_endpoint_write_failure_is_charged_and_releases_lock`
  and `test_actual_owner_final_manifest_failure_is_not_success_or_double_charge`
  invoke the actual owner. The latter expects a charged artifact failure, not
  an extra fallback charge or successful output acceptance.
- Pair-binding parameterized negatives cover final hash/full identity including
  config/initial hash/owner authority/shared digest/batch prefix. Metadata tests
  read one real retained owner attempt through the accepted manifest adapter,
  then use small synthetic owner files for hash/seed/temperature mutations.
  Rebound same-map route permutation is checked by the real pure verifier.
  Selection tests cover both independent floors, no eligible SA, pass/Q/tolerance
  ties, lower temperature and distinct missing/duplicate grids.
- Watchdog tests cover copied qualified ledger prefix, unique EOF charges,
  cumulative 120-second refusal, actual child nonzero exit and inspected repeat,
  actual descendant timeout cleanup, append failure, missing-owner fallback,
  existing-owner failure/no double debit, exact decision/argv/review/authority,
  60-second concurrence, and launch exception terminal/accounting evidence.

## Watchdog/accounting procedure for review

The stdlib-only watchdog holds an exclusive accounting lock, validates the exact
143-line frozen prefix and administrative row, reserves the full requested
10/30/60/300-second envelope, and records exact decision/argv/hash/UTC metadata.
Child stdout/stderr stream to files; process-group TERM/KILL/reap is bounded.
Terminal evidence is durable before EOF accounting. Tests get one stage-A charge;
production uses the actual owner output/UUID charge or one uncertain fallback if
there is no owner charge. An existing failed owner with missing manifest remains
a charged STOP, never a duplicate debit.

A disclosed **1-second finalization allowance** is inside each existing command
envelope and fresh 120-second total, not new budget. Child deadline leaves that
second for terminal/ledger/result persistence. Actual elapsed through cleanup is
recorded separately; allowance overrun stops continuation. An accounted failed
test with verified cleanup releases only its reservation, preserving immutable
evidence so the already approved inspected correction/repeat is possible.
Uncertain cleanup/accounting retains the reservation and blocks relaunch.

After static PASS, root writes a hash-bound decision naming the exact review and
current ledger EOF, then runs the watchdog once for the 10-second smoke. A passing
smoke permits a separately recorded 30-second suite decision. No test is launched
by this handoff. An implementation review after actual test evidence remains
mandatory before a separately authorized one-shot 300-second production decision.

Qualified operational debit remains 4583.809008752118 seconds. Fresh development
120 seconds and production 300 seconds remain unspent. No historical timing has
been repaired or reinterpreted by this work.
