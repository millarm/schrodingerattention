# Sol static re-review — corrected v3 driver

**Verdict: CHANGES REQUIRED.**

`DRIVER_REVIEW_VERDICT: CHANGES REQUIRED`

Static review only. I read the complete frozen driver, driver-specific tests,
correction handoff, v3 specification, historical `03-driver-closure.md`, and
`03a-driver-clarification.md`. I did not import project code, run tests or
subprocesses, execute training, or write the ledger. `study.py` remains outside
this sub-block and is not accepted.

## Exact version reviewed

- `execution/update_efficiency/command.py`:
  `2fe115c6f2dd4eb2852cb419cb3c0caa0e3fa3139c3fd074752dc78511ed0ad1`
- `tests/test_update_efficiency.py`:
  `39e8456819c1ae675972ab05468becd522733bdc25b56c2c72b3d0f24a9952ce`
- `execution/update_efficiency/handoffs/04-driver-correction.md`:
  `64145e04eb535fb19d23ae0bd2db5c75645a2080dab7d28ee83dd5cee2bc067d`
- v3 plan/spec:
  `d4ce6e3c6e4c0a7eac46aa96b2a01f442abeed573c3b78e95a2edb874caca6ae` /
  `dcca6fa6c3ba0d322a8278d6003c77249c692a1224f37a3a2bad547530285a67`

## Required residual findings

### 1. Static-safety authority is bound to the historical failed review

`DRIVER_REVIEW` still names `reviews/03-driver-closure.md` (command line 14).
That preserved historical file contains exactly
`DRIVER_REVIEW_VERDICT: CHANGES REQUIRED`, while `review_ok` requires exactly one
`DRIVER_REVIEW_VERDICT: PASS` for smoke and suite (lines 45–49). Therefore no
honest decision can authorize either bounded test command from this corrected
version. Changing the historical review would destroy review history and is not
permitted.

Required correction: bind smoke/suite to the designated review of the current
exact corrected version (the next review path/hash/phase), preserving 03 and 04
unchanged. Production must continue to require the later exact implementation
PASS. Add a literal test proving the historical CHANGES REQUIRED review cannot
authorize static safety and the designated current PASS can.

### 2. A supervision exception is incorrectly treated as cleanup-certain

After reservation, line 128 sets `cleanup_certain=True` before supervision.
The variable is replaced with the watchdog's `cleanup_verified` only if
`supervise` returns (line 133). If `supervise` itself raises, the exception path
appends an A failure charge or reconciles B and the `finally` block releases the
reservation whenever accounting succeeds, even though no cleanup evidence was
received. This contradicts the retain-on-uncertain-cleanup rule and the handoff's
claim.

The new A exception test actually expects `lock.exists()`, but the reviewed
source will unlink it because both `accounted` and the stale
`cleanup_certain=True` are true. Thus the claimed literal suite is internally
inconsistent and would detect this defect when eventually run.

Required correction: treat setup-before-child as cleanup-certain, switch to
cleanup-uncertain immediately before entering supervision, and set certainty
only from an explicit returned watchdog terminal. An exception from supervision
must retain the durable reservation unless the reviewed helper supplies separate
verifiable cleanup evidence. Cover the same behavior for A and B.

### 3. Ambiguous or mismatched normal owner charges can still be double-charged

`reconcile_owner` filters normal rows only by the UUID resolved from
`attempt.pending.json`/`attempt.json` (lines 85–92). If no UUID artifact exists,
or if it resolves UUID X while the ledger already contains an `attempt_charge`
for the exact owner output under UUID Y, `owned` is empty and the function appends
a fallback. That creates a second charge despite an existing normal owner charge;
the existing row is ambiguity/corruption, not proof of absence.

Required correction: first collect **all** normal stage-B owner rows for the
exact output. Append a fallback only when that set is empty and no prior fallback
exists. If UUID evidence is absent while a normal row exists, UUIDs disagree, a
normal row has a different UUID, or more than one normal row targets the owner,
record/retain an accounting ambiguity without appending another charge. When one
UUID is resolved, require the total normal-owner set to be exactly that one row.
Add literal missing-UUID-with-existing-charge, mismatched-UUID, and multiple-row
tests; the current tests cover only the clean FAILED row, wholly missing charge,
and pending/final UUID disagreement.

### 4. Envelope overrun is recorded but can still be reported COMPLETE

Starting the clock before parsing and passing a reduced child deadline are good
corrections. `charge(started)` also arithmetically includes the one-second
allowance. However, neither A nor B success checks that the accountable charge
fits the reserved owner envelope or the remaining caps. An A child can return
success after setup/cleanup/finalization consumes more than 10/30 seconds and the
driver will append the full overrun charge with status COMPLETE and print
COMPLETE. For B, the accepted normal owner row is never checked against the
SM350/SA550 envelope, and the driver does not establish that its owner charge
covers the external accountable duration/allowance before reporting success.

This violates `03a`: actual usage must never be clamped, but an overrun must be
retained as failed resource evidence and prohibit continuation. Required
correction: preserve the full charge, explicitly compare it with the reserved
envelope and applicable current caps, and make any overrun a terminal resource
failure. For a normal B owner, define and verify how the accepted owner charge
covers the external startup/cleanup allowance; do not add a duplicate normal
charge. Add deterministic clock/charged-row tests for A and B overruns.

### 5. Exact decision EOF validation still uses two filesystem snapshots

Inside the acquired study reservation, line 56 checks
`decision.ledger_sha256 == sha256(LEDGER)`, then line 57 calls `ledger_rows()`,
which reopens and rereads the file. A concurrent central-ledger append between
those reads can make totals come from a different EOF than the decision-bound
hash. The study lock does not establish that unrelated accepted ledger writers
honor it.

Required correction: under the central ledger's append lock, read one immutable
byte snapshot and derive both the full EOF SHA and parsed prefix/carry/UUID/totals
from that same snapshot, or otherwise prove equivalent atomicity. Add a literal
mutation-between-hash-and-parse rejection test. The current prefix test checks a
duplicate UUID but not this TOCTOU condition.

### 6. The claimed real-hash artifact mutation test is not real and is likely false

The driver fixture globally monkeypatches `command.sha256` to return `"f"*64`.
`_complete_owner` consequently writes the same synthetic digest for every
manifest, score and checkpoint, and `validate_complete` recomputes that same
synthetic digest. `test_driver_complete_rejects_missing_corrupt_and_escaped_endpoint`
then expects `validate_complete` to raise merely because hashes are “non-binding
to real bytes,” but no checked value differs under the monkeypatch. The fixture
appears complete and internally equal, so the expected rejection is unsupported.

Required correction: use the real streaming SHA implementation for artifact
closure tests. First prove the complete synthetic owner passes, then mutate one
score, checkpoint, manifest entry, result/index binding, endpoint grid and an
escaped reference separately and prove each actual checked path fails. Keep
authority hash stubbing separate from artifact hashing rather than replacing the
shared `sha256` function globally.

## Prior findings now closed in source

The correction makes substantial progress:

- new-study usage is stage-scoped and v3 cap constants are correct;
- the study reservation is acquired before experiment-lock checks and validation
  exceptions remove the fresh lock;
- normal charged FAILED owners are not automatically given a fallback;
- fallback rows are excluded from the normal-owner filter and pre-existing owner
  history is rejected before launch;
- post-child artifact/reconciliation exceptions enter a common terminal path;
- production requires a distinct future implementation-review phase rather than
  the driver-only phase;
- COMPLETE validation binds terminal UUID, result/index, exact 13-point grid,
  closed manifest, score/checkpoint hashes and owner-contained references;
- tests now invoke `main` across several A/B success and failure branches rather
  than relying only on helper prose.

Those closed portions remain subject to eventual authorized execution. They do
not overcome the six residual correctness/evidence findings above.

No smoke, suite or production command is authorized from this version. Preserve
the historical reviews; correct only the driver and driver-specific tests, then
freeze a new exact version for static re-review. Scientific runner/composition
review remains separately pending.

