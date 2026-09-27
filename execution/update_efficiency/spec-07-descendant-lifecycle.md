# Bounded descendant-lifecycle fixture respecification

Root authorized this proof-preserving fixture-only respec under the existing
user launch request. Read `reviews/07b-permission-outcome.md` and both raw
EPERM attempts; historical results stay unchanged. The cause is not established.

Terra may change ONLY `test_driver_watchdog_descendant_fixture` and its tiny
fixture helper, if needed, in `tests/test_update_efficiency.py`. Accepted driver,
watchdog, study, science, production deadlines and ledger must not change.
Do not run tests while implementing. No mock of group probing/signalling or
cleanup result; no treating EPERM as gone or skipping the assertion.

Replace the 50ms launch/kill race with a controlled genuine two-process lifecycle:

1. Start an actual child in the launched parent's process group. Both processes
   record PID/readiness through private durable fixture files (not pipe buffers).
   Parent records child PID and installs a SIGTERM handler before readiness.
2. Child readiness is synchronized before parent signals complete readiness.
   On group SIGTERM the parent waits/reaps its own actual child, records its
   return code/reaped identity durably, then exits. Keep handler work bounded;
   parent/child have finite defensive lifetimes, no stray indefinite sleepers.
3. Call the unchanged real watchdog with at most a TWO-second total deadline,
   enough to establish readiness and allow its built-in grace; no deadline
   extension or new polling after it returns. Directory exists before call.
4. Assert readiness evidence, distinct actual parent/child PIDs, child belongs
   to launched group, real child exit/reaping record and parent exit, watchdog
   timed_out=true and cleanup_verified=true. Verify group absence via unchanged
   accepted group probe. Never infer cleanup solely from invented metadata.

Record complete static handoff, exact test hash, unchanged driver/watchdog/study
hashes and literal assertion map. Sol exact static PASS is required before ONE
new 30-second full-suite attempt under normal scoped permissions, within A100.
No other tests/source changes; no production until full implementation PASS.
If EPERM/cleanup remains unprovable after that attempt, stop as a capability
blocker; no waiver, extra retries or automatic wider redesign.
