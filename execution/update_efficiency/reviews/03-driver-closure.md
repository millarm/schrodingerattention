# Sol static review — v3 driver closure

**Verdict: CHANGES REQUIRED.**

`DRIVER_REVIEW_VERDICT: CHANGES REQUIRED`

Static review only. I read the frozen driver, driver-relevant tests, handoff and
the six closure duties with v3 overrides. I did not import project code, run
tests/subprocesses/training, inspect scientific outcomes, or write the ledger.
`study.py` remains outside this sub-block and is not accepted here.

## Exact version reviewed

- `execution/update_efficiency/command.py`:
  `24daec613cd43ed8e49c5c358b05c94ea0bc520c2547c650bfd8379ea0d199f4`
- `tests/test_update_efficiency.py`:
  `9bf681ea7901fb92ed75a92f350d7cbe802ecaf4f4c54877be12e7f8af85a0ad`
- handoff `execution/update_efficiency/handoffs/03-driver-closure.md`:
  `2e93fcc27faafa2b73d850f184936e9d859aaad864e456232510a1d2df980dd7`
- v3 plan/spec:
  `d4ce6e3c6e4c0a7eac46aa96b2a01f442abeed573c3b78e95a2edb874caca6ae` /
  `dcca6fa6c3ba0d322a8278d6003c77249c692a1224f37a3a2bad547530285a67`
- driver-closure specification:
  `d60cdc6ea378f68b36f6fbaca3f7aa73fe2c1c0117e9ce8e4a61ec1e3fe36f8d`

The handoff's assertion map is not supported by literal branch coverage and in
several cases does not describe the source behavior.

## Required findings

### 1. B failure handling can double-charge a completed FAILED owner

On every supervision exception or non-success terminal, lines 89–98 append a
new `watchdog_uncertain_fallback` without first reading/reconciling the intended
owner UUID and checking whether the child already durably appended its normal
FAILED owner charge. A child can finalize a charged failure and exit nonzero;
the driver then adds a second charge for the same attempt/output. This directly
violates closure item 5 and can consume resource twice.

Required correction: use one reconciliation routine on **all** B exits. Bind the
expected owner output and UUID before launch; after cleanup, distinguish exactly
one matching COMPLETE/FAILED owner charge from no charge and ambiguous charge.
An existing valid FAILED owner charge is the accounted terminal failure and must
not receive a fallback. Append one permanent uncertain fallback only when the
specific owner charge is genuinely absent.

### 2. A fallback can masquerade as a valid owner charge

Lines 105–109 classify every stage-B row with the owner output as `owned`, with
no required kind, UUID, status, attempt identity or driver-session relation. A
previous `watchdog_uncertain_fallback` uses that same output. On a later launch,
that fallback can be the sole matching row and satisfy `len(owned)==1`, allowing
a COMPLETE artifact set to be accepted without its actual OwnedAttempt charge.
The code also does not reject an existing owner/fallback before relaunch, despite
the no-retry rule.

Required correction: permanently distinguish fallback rows from owner charges;
bind and compare the actual attempt entry ID/UUID and expected charge kind/status;
reject any pre-existing owner directory, terminal, reservation or fallback for
the fixed seed/mode owner before launch. A fallback is never promotable to a
successful owner charge.

### 3. Post-supervision B failures are unreconciled and strand the lock

Only the call to `supervise` is inside the exception handler. After a successful
child exit, missing terminal artifacts (line 102), malformed JSON, manifest
mismatch (104), ledger read failure, missing charge after fallback append, or an
ambiguous charge (109) raises outside any common finalizer. These paths leave
`driver.lock` in place. Several also omit a permanent fallback or fail to record
a driver terminal reflecting the reconciliation failure. The terminal record at
line 94 still describes child success, not final driver failure.

Session creation and `start.json` failure after reservation (lines 86–87), and
ledger validation failure inside `reserve` (60), can likewise strand the lock.

Required correction: place every post-reservation path under one exception-safe
terminal/finalization state machine. Record final driver status durably, reconcile
the owner/charge, and release only when cleanup and accounting are certain;
otherwise retain a clearly identified permanent reservation/failure artifact.
Do not leave an accidental lock with no explanatory terminal.

### 4. The declared envelope excludes setup and finalization and undercharges

The command parses the decision, hashes the complete authority inventory, reads
and hashes the ledger, validates the review and reserves resources before
`started` is set at line 86. `supervise` then receives a fresh full relative
deadline at line 88. Those setup costs are outside both the watchdog deadline
and recorded charge. A-stage charges are computed before their own append/fsync
and lock cleanup. B fallback rows are also computed before append/finalization.

Lines 92/97 declare a one-second `finalization_allowance_seconds` field but do
not add that allowance to `charged_seconds`; the missing-charge fallback at line
107 does not even declare it. This is metadata without accounting effect.

Required correction: start the envelope clock before driver setup and pass only
the remaining deadline to supervision. Include bounded cleanup, reconciliation,
artifact writes, ledger append/fsync and terminal finalization in the reserved
and charged amount, using an explicit conservative allowance where exact
post-append measurement cannot be recorded. Clamp/check the charge against the
reserved envelope; a nominal allowance must be arithmetically included.

### 5. Reservation is not atomic with the required checks

The two experiment locks are checked before acquiring `driver.lock` (lines
57–59), leaving a race in which another experiment can start between the check
and reservation. The reviewed decision's ledger SHA is checked at line 83 before
reservation, but after acquiring the lock `reserve` validates only the historical
prefix/totals; it does not require the current EOF to equal the decision-bound
SHA. A ledger append between those operations silently changes the authorized
starting state.

The new-study `used` predicate on line 60 is also parenthesized incorrectly:
every row tagged `study==update_efficiency_v3` is counted regardless of stage,
while the stage condition applies only to the output-path alternative. This can
make A, B and D consumption contaminate each other. It is conservative in some
states but does not enforce the literal per-stage A100/B1800/D100 allocations.

Required correction: acquire the exclusive study reservation first, then check
both experiment locks, exact decision-bound EOF, prefix/carry/UUID validity and
all global/stage/new-study totals under that reservation. Apply `stage==stage`
to every row counted toward the selected new-study stage. Make all validation
exceptions enter the explicit reservation-finalization policy.

### 6. Production authority accepts only the driver review

`review_ok` requires path `reviews/03-driver-closure.md` and phase `driver` for
all command kinds, including production (lines 50–53, 85). Consequently a
production decision can satisfy the driver without binding the later mandatory
exact full implementation PASS. This sub-block intentionally excludes the
scientific runner, so its review cannot authorize a 16k owner.

Required correction: smoke/suite may bind the designated static-safety review
when eventually authorized, but production must bind the exact final
implementation review/path/hash/phase and full frozen source/test authority.
There must be no machine-readable driver-only PASS token usable for production.

### 7. COMPLETE validation does not bind the full owner or endpoint set

Lines 101–104 require four files but verify manifest entries only for
`attempt.json`, `result.json` and `index.json`. They do not bind the attempt UUID
to a ledger row or decision, validate the manifest's complete declared file set,
or walk every endpoint/checkpoint hash referenced by the result/index. A
syntactically COMPLETE attempt with three matching top-level hashes can therefore
pass while an endpoint is missing, altered or unbound.

Required correction: validate the intended owner/UUID and exact terminal
identity, manifest completeness, result/index identity, and every referenced
endpoint/checkpoint path and SHA-256 before success. Reject extra/missing grid
endpoints and any path escaping the owned directory. The later scientific review
may add semantic checks, but the driver must enforce the bound durable artifact
closure promised by spec item 5.

### 8. Literal driver tests cover only surfaces and one rejection

The only current driver tests are:

- direct timeout coverage of `supervise` (lines 72–75), which does not execute
  `main` or any accounting/finalization branch;
- a constants/hash-shape assertion (89–94); and
- one mocked A over-allocation rejection (96–102).

There is no literal execution of reviewed decision validation; exact argv/root/
review phase; prefix, carry, EOF and UUID rejection; successful or failed A
charge; setup failure; child exception/nonzero/timeout through `main`; descendant
cleanup plus accounting; COMPLETE B owner; already-charged FAILED B owner;
missing-charge fallback; fallback non-promotion; duplicate/ambiguous owner rows;
missing/corrupt manifest/index/endpoint; or lock release/retention semantics.
The test named by the smoke command tests only the helper timeout, not the driver
closure.

Required correction: add the six closure specification's small synthetic branch
tests. They may mock children/artifacts and must not run scientific code, but must
invoke the actual driver orchestration/reconciliation paths. The assertion map
must cite each exact test and branch rather than infer coverage from source prose.

## Closed or directionally correct portions

The v3 constants, named seed set, 16000-update decision fields, SM350/SA550
envelopes, A100/B1800/D100 and A1000/B4100/C0/D800 tables are present. The driver
uses a literal workspace assertion, fixed stdlib command shapes, the accepted
watchdog's process-group supervision helper, durable JSON replacement, prefix
hash/carry/finite-charge checks and append-time UUID rejection. These pieces do
not close the accounting, authority and test gaps above.

No smoke, suite or production command is authorized from this version. Terra
should revise only the driver and driver-specific tests for these findings;
scientific runner acceptance remains the separately pending sub-block.

