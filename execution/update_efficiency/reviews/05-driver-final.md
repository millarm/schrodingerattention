# Sol final bounded static review — v3 driver

**Verdict: BLOCKED.**

`DRIVER_REVIEW_VERDICT: BLOCKED`

This is the definitive driver verdict under the bounded correction limit. Static
review only: I read the complete frozen driver, tests, final-correction handoff,
accounting clarification, v3 specification and prior reviews. I did not import
project code, run tests/subprocesses/training, or write the ledger. `study.py`
remains intentionally outside this review and is not accepted.

## Exact version reviewed

- `execution/update_efficiency/command.py`:
  `0afe1034a5446e9970e9520861a07528f551885d97190409c45713d452fd0e33`
- `tests/test_update_efficiency.py`:
  `90cb6d2d014d55da43f95badfaf1d4f382e25946b63f47dbb9dea597be856b48`
- `execution/update_efficiency/handoffs/05-driver-final-correction.md`:
  `607b1c2db05a573fa0eed0fd71dcba55d2b2b92a8c73bb63774673dc0d31461e`
- `execution/update_efficiency/driver-accounting-clarification.md`:
  `7ab55e8e05ca950597e9c7f09c948a8edbd2756f04854d1dc19851dba82c58c6`
- v3 plan/spec:
  `d4ce6e3c6e4c0a7eac46aa96b2a01f442abeed573c3b78e95a2edb874caca6ae` /
  `dcca6fa6c3ba0d322a8278d6003c77249c692a1224f37a3a2bad547530285a67`

## Blocking findings

### 1. The literal A-overrun test cannot exercise the claimed branch

`test_driver_a_overrun_is_full_charged_failure_and_b_watchdog_exception_retains`
supplies monotonic ticks beginning `(0, 20, 20, ...)` for a 10-second command.
The first tick initializes `started`; the second is consumed while computing
`remaining` before supervision. `remaining` is therefore negative and the source
raises `TimeoutError("setup exhausted command envelope")` before calling the
mocked successful child or entering the A normal-terminal branch.

The exception-path A row at command lines 192–194 records the full charge but
does not contain `resource_overrun`. The test then asserts
`rows[0]["resource_overrun"]`, so the reviewed test cannot satisfy its own
assertion and does not prove that a successful child whose accountable
setup/cleanup/finalization crosses the envelope is converted to a charged FAILED
resource terminal.

This is not merely missing optional coverage: honest overrun handling was a
specific review-04 correction and the handoff cites this exact test as its literal
evidence. A valid deterministic sequence must leave positive time for supervision
and advance beyond the envelope only when `actual_charge` is computed, then
assert the complete full charge, FAILED status, overrun marker and no success
terminal. Setup-exhaustion should be a separate test with its own explicit
resource-overrun evidence.

### 2. Uncertain overhead/finalization can release the reservation

The prospective clarification requires: “Failure to durably finalize retains
uncertainty and reservation.” The source tracks only `accounted` and
`cleanup_certain` for release (line 200).

For B, `accounted=True` is set immediately after normal owner reconciliation and
**before** `settle_owner` appends any required `driver_overhead` row (lines
181–184). If that EOF append writes partially or raises during flush/fsync, the
exception path does not reset accounting certainty. With verified child cleanup,
the `finally` block removes `driver.lock`, even though the required `H=max(0,E-C)`
accounting row is of uncertain durability. The same release can occur when the
final session terminal cannot be durably written after otherwise successful
accounting: the fallback write is swallowed, yet `accounted && cleanup_certain`
still releases the reservation.

Thus `max(C,E)` is correct when every write succeeds, but the all-exit durability
contract is not closed. The driver needs a distinct durable-finalization/accounting
certainty state: normal owner reconciliation alone cannot certify a required
overhead append, and release must follow a durable final driver terminal. Literal
tests must inject overhead append/fsync failure and final-terminal write failure,
then prove the reservation is retained and no COMPLETE is emitted. Current tests
cover successful/deduplicated overhead only.

## Findings closed by this version

The final source materially closes the ordinary-path review-04 findings:

- smoke/suite authority points prospectively to `06-full-static.md`, production
  to `08-implementation.md`; historical and driver-only reviews cannot authorize
  runtime;
- cleanup certainty is reset before supervision and watchdog exceptions retain
  the reservation in the ordinary tested paths;
- reconciliation considers all normal rows for the exact owner and refuses
  absent/mismatched/multiple UUID evidence without adding a fallback;
- `C + max(0,E-C) = max(C,E)` accounts only uncovered external overhead, keeps
  overhead distinct from owner/fallback rows, and rejects ordinary B envelope
  overruns;
- reservation derives EOF hash, prefix, carry, UUID validity and totals from one
  append-locked byte snapshot; append validation uses its held descriptor;
- COMPLETE closure checks the exact grid, result/index/terminal identity, closed
  manifest, real score/checkpoint hashes, references and owner path containment;
- the real-SHA artifact test first validates a positive owner and then mutates a
  score, checkpoint, grid and escaping reference;
- the test suite now exercises real `main` branches, normal FAILED-owner reuse,
  missing-charge fallback, fallback non-promotion and owner-row ambiguity.

These improvements do not resolve the two final-cycle blockers above. Under the
specified bounded correction rule, do not start another unstructured revision
loop and do not authorize smoke, suite or production. Astra must record the
driver sub-block as blocked and either issue a newly bounded respecification with
explicit user/protocol authority or stop this study. No scientific conclusion is
affected because no study runtime occurred.

