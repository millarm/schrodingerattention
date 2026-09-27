# Narrow platform cleanup recovery

2026-09-27. Astra specification under the user's role amendment and repair request.
Science remains `plan-v3-saturation.md` and `spec-03-saturation.md` unchanged.

## Scope and authority

Luna may add `execution/update_efficiency/watchdog.py`, change only the watchdog
import and exact authority/review-path bindings in `command.py`, and extend
`tests/test_update_efficiency.py`. Luna writes a handoff and later approved
runtime records/decisions. Preserve historical shared `d1_watchdog.py`, study
science, accepted models, plans, ledger history and old reviews. Use new review
paths `reviews/09-platform-static.md` and `reviews/10-platform-implementation.md`.
Bind this specification and agent protocol in the driver's authority inventory
alongside the new watchdog; preserve the existing full scientific inventory.

No project imports, test execution or training during implementation/static
review. Read-only source/host documentation inspection and hashing are allowed.
Sol first reviews this specification; implementation may proceed concurrently,
but must resolve all specification findings before exact static review.

## Required cleanup behavior

Use a study-local stdlib supervisor derived from the accepted supervision seam,
preserving new-session process groups, total monotonic deadline including TERM/
KILL grace, direct-child wait/reap, durable logs, timeout status, and fail-closed
driver reservation/accounting behavior. No shared-module monkeypatching.

Normal killpg(pgid,0) ESRCH proves absence; successful probe means present.
On Darwin ONLY, EPERM permits a separate, bounded `/bin/ps -axo pid=,pgid=`
enumeration. An empty *matching group* in a successful complete process-table
snapshot can prove absence; EPERM alone cannot. Check exit status, nonempty
well-formed rows, positive numeric IDs, no duplicate PIDs, and presence of the
supervisor's own PID and expected PGID as a visibility sanity check. Reject
empty/malformed/truncated/error/timeout output, unsupported platforms and any
uncertainty. Use exact numeric PGID equality; zombies count as present until
reaped. Record which probe established cleanup and retain fallback snapshots
or equivalent durable evidence in the returned child terminal/logs.

Do not use individual PID killing as a new first-line mechanism: retain group
TERM/KILL. If a group signal returns EPERM, independently enumerate. Absence
can mean the signal raced with final exit; any member still present is a
capability failure. This narrow fix addresses false inability to confirm an
already-empty group and cannot silently substitute inability to kill a live
group. No process other than the owned group may be signaled.

Bound every enumeration by the remaining monotonic deadline and reap its helper
on timeout. Cleanup cannot succeed after the supplied deadline. Preserve the
original exception when defensive cleanup also fails; keep failed cleanup false.
Parent wait/reap is mandatory in addition to group absence. No fixture-only
relaxation or accepting recorded child reaping as the full group proof.

Failure finalization still attempts immediate best-effort SIGKILL to the owned
group if the deadline has already expired; expiry must not skip termination.
No unbounded helper communicate/wait is allowed, including exception paths.
Reserve helper kill/reap time within its envelope, recheck time after enumeration
and before returning successful cleanup, and retain uncertainty if helper reaping
cannot be confirmed. Group absence does not claim that this supervisor itself
reaped descendants; it must reap its direct child and independently prove absence.

## Required tests and acceptance

Keep the real parent/descendant test with durable readiness and parent reaping.
It must exercise the production supervisor and assert actual complete group
absence. Add deterministic tests for Darwin EPERM+empty valid table success;
live matching member fails absence; unrelated PGID is not a match; malformed,
empty, duplicate, missing-self, command error and timeout fail closed; non-Darwin
EPERM remains failure; TERM/KILL EPERM with live members fails; deadline exhausted
never proves cleanup. Cover normal ESRCH and existing driver accounting/lock
retention failures. The helper timeout must be bounded and reaped. Independent
Sol reviews both the equivalence argument and exact implementation.

After fresh exact static-safety PASS and Astra acceptance, Luna may run ONE
10-second smoke and ONE 30-second suite using the reviewed driver, bound current
EOF decisions, one process, actual immutable terminal records and append-only
A charges. These are within remaining A81.934066958259790, not extra budget.
Any failure stops runtime and returns to Astra/Sol; no automatic retry. Sol
must then issue exact implementation PASS from the completed evidence before
Astra authorizes production 2201 SM350 then SA550. The frozen second-pair1.5x
resource gate and all existing integrity checks remain required; no owner retry.
Each tool session must reach explicit terminal state; no duplicate launches.

Report source hashes, all commands and outcomes, true cleanup evidence, ledger
before/after and total charges. Sol records limitations and PASS/CHANGES REQUIRED/
BLOCKED. No scientific conclusion can follow from this capability repair alone.
