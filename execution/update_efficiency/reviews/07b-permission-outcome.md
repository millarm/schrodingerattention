# Sol escalated permission outcome

**Verdict: BLOCKED at the runtime-suite gate; production remains unauthorized.**

Static evidence diagnosis only. I did not execute tests or subprocesses, import
project code, change source, or write the ledger.

## Observed outcome

The explicitly permission-escalated retry still exits 1: 26 tests pass and the
sole failure is `test_driver_watchdog_descendant_fixture`. The accepted watchdog
receives `EPERM` from `os.killpg(pgid, 0)` while checking the descendant process
group, then receives `EPERM` again from its defensive group `SIGKILL`. The child
terminal is durable and reports exit 1, not timeout, with outer-driver cleanup
verified. Study, driver and tests remain exactly:

- study `a62a37248421660f94edce139a7e9ca471890bab8c0ba4463edd8ffb6c396204`
- driver `3adda02c82b2eb6a059d890b967950c6718e7406e64dd99fdcfe2dab47f38b4f`
- tests `a1d879c7cb73d4f9e3e9270476a920bcdafded59bfa402ee4a826ad83eaa9558`
- current post-attempt ledger `a1b6c3678335557debfba48b419ac582039e631c0ee1e1b20498120f98bfbb51`

The escalated result falsifies the narrower claim in review 07a that ordinary
permission escalation would supply the missing capability. The evidence supports
only this bounded statement: on the current host/tool execution path, inspection
and termination of the fixture's surviving process group is denied with EPERM.
It does not establish whether the denial originates in a remaining host policy,
process ownership/reparenting behavior, or another platform boundary.

## Capability blocker versus fixture timing

There is also an unresolved fixture hypothesis. The fixture grants only 50 ms
total. The watchdog reserves 20% grace, splits half of that for TERM, and can
therefore reach the group probe roughly 10 ms after signalling a leader plus its
sleeping descendant. A surviving or reparenting descendant at that instant may
expose host-specific group inspection/termination semantics. Static evidence
cannot decide whether this is a genuine required-capability blocker or a fixture
whose envelope is too short to demonstrate descendant reaping reliably.

That ambiguity is not grounds to waive the assertion, reinterpret EPERM as
success, or alter the accepted watchdog. All science and actual-owner tests pass,
but the required real descendant-cleanup safety evidence does not.

## Recommendation

Do not retry automatically and do not proceed to production. Further progress
requires explicit root/user direction choosing a bounded, separately reviewed
resolution: either run the unchanged assertion in an execution environment that
demonstrably permits process-group inspection and termination, or authorize a
new fixture/watchdog specification that preserves real descendant-cleanup proof
while providing a platform-appropriate envelope. Available budget does not cure
the capability/evidence gap.
