# Runtime safety capability blocker — no production training

2026-09-27. The approved bounded repair path has been exhausted. Stop all new
tests and training pending user direction; no safety waiver or automatic retry.

Independent Sol closeout audit: `reviews/08-capability-closeout.md`, SHA
`9a29b857e806b1fdb443a91eeb5d27fb1110680e4fec2e062896b424fc1c97c0`.
Verdict: runtime safety gate BLOCKED; no implementation or production PASS.

## What is complete

Sol accepted the v3 scientific contract, driver, pure estimators, and exact
model/owner/checkpoint/evaluator composition. The final full suite passed26
tests, including both real two-update model paths and failure/accounting checks.
No fresh production seed has trained. This is not a negative scientific result.

## Remaining blocker and evidence

The sole failure is `test_driver_watchdog_descendant_fixture`: the host/tool
path returns `PermissionError: EPERM` when the unchanged accepted watchdog
probes process-group absence using `os.killpg(pgid,0)` and then attempts its
defensive group SIGKILL. Normal permission escalation did not resolve an earlier
instance. A separately reviewed final fixture respec replaced the50ms race with
a2s lifecycle, durable readiness, and parent-owned child reaping. That final
authorized attempt still failed at the group-probe boundary.

- Decision `suite-decision-004.json`, exact Sol reviews06 and07c.
- Tool session27236 was polled to explicit exit1; no duplicate launch.
- Immutable owner `attempts/driver-d54acc18-5583-4058-84f2-8b77aa44ff28`.
- Pytest26 passed/1 failed in3.08s. Outer child exit1, not timed out,
  cleanup_verified=true. No driver reservation remains.
- The fixture's observed durable proof: parent PID14118, PGID14118; child
  PID14119, parent14118, PGID14118; both readiness records present. Reaped record
  is exactly `{"pid":14119,"reason":"SIGTERM handler","returncode":-15}`.
  These observations establish child termination/reaping, NOT independently
  verified absence of the entire group; that required probe still failed.
- Original proof location:
  `/private/var/folders/sr/3vzptsv10h36bf9jhq3bpg3h0000gp/T/pytest-of-gmh-company/pytest-202/test_driver_watchdog_descendan0/proof/`.
  A compact transcription is saved separately; raw traceback remains in owner stdout.

Exact frozen hashes: study `a62a37248421660f94edce139a7e9ca471890bab8c0ba4463edd8ffb6c396204`;
tests `5fb793d5794836462d0b145cc0d613ef4c0c3b3f29ac28ec1c30cdd75e2378c6`;
driver `3adda02c82b2eb6a059d890b967950c6718e7406e64dd99fdcfe2dab47f38b4f`;
watchdog `2b3fed56e07da5a33c122afa10e9cc5b77df0df77ec492db0bfaf4887708a8c8`.

## Accounting and authority

Final suite stage-A charge4.395713374949992s. Five unique test attempts total
18.065933041740210/100s new development. Qualified global debit
4782.482380042790/7200s, retaining historical administrative300s uncertainty.
Current ledger SHA `ffb377e0aaf76ce0c46f7d015f6d7f54976d9f9bcb84258fd6942e3116c3aaf5`.
No budget exhaustion, production model run, final-test release, or scientific
endpoint occurred. All failed attempts remain charged once in chronology.

Next decision: use a host/execution path that permits independently verified
process-group cleanup, or authorize a separately reviewed platform-specific
safety implementation with equivalent cleanup evidence. Neither option is
implemented or authorized by this report. Do not reinterpret EPERM as success.
