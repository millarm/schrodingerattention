# Luna handoff — spec-09 platform cleanup

## Exact version for static review

This handoff binds the following source version:

| File | SHA-256 |
| --- | --- |
| `execution/update_efficiency/command.py` | `e228b53fb52f3a944e6e523e9ce3340c5abb3c02cc16ad2e07729972b1877d84` |
| `execution/update_efficiency/watchdog.py` | `ad5e3030ce148283c2576fa5fb376c512a8f7474bcc5e62e8e2d4e6d749900b2` |
| `tests/test_update_efficiency.py` | `4d5d9dbf1058b439383311e0ece0f73ba310b7fcbe67a3c63e0a0490fbe86fb5` |

Authority/scientific inventory hashes at handoff:

| Authority | SHA-256 |
| --- | --- |
| `execution/update_efficiency/plan-v3-saturation.md` | `d4ce6e3c6e4c0a7eac46aa96b2a01f442abeed573c3b78e95a2edb874caca6ae` |
| `execution/update_efficiency/spec-03-saturation.md` | `dcca6fa6c3ba0d322a8278d6003c77249c692a1224f37a3a2bad547530285a67` |
| `execution/update_efficiency/driver-accounting-clarification.md` | `7ab55e8e05ca950597e9c7f09c948a8edbd2756f04854d1dc19851dba82c58c6` |
| `execution/update_efficiency/decisions.md` | `b13b9cb8c4ee8283ea1db085a334cb541a9cb315d6c82d518c43499648f356c9` |
| `schrodinger/attention.py` | `e1ce15be10caf4b2165191f9835256602f4f7b8bd11bffa94f676eac40b0fd6a` |
| `schrodinger/route_feasibility.py` | `da36b0150c0b255b7e5482d7dc016505054d9632c8fb3a21d06c2d201bfedbf4` |
| `agent_execution_protocol.md` | `983a63fd480510994721d980ee866f08e3cba6b767fcbadd5cef7491d437d1c5` |
| `execution/update_efficiency/spec-09-platform-cleanup.md` | `4dc2ed2fb1b7bf182f924abfb571b4fd70eb891d476e8c171a8184740b216f67` |

## Changes

- Added a study-local stdlib watchdog and redirected the driver to it. The
  shared D1 watchdog is unchanged.
- Bound the driver's watchdog, protocol/spec authority hashes, and new static
  and implementation review paths while retaining its prior scientific
  inventory.
- Added deterministic watchdog cases for Darwin EPERM snapshots, table
  validation, group matching, command failure/timeout, non-Darwin EPERM,
  ESRCH, and TERM/KILL EPERM with a live matching process. Kept the existing
  production-supervisor parent/descendant test and driver accounting/lock tests.

## Static equivalence reasoning

`killpg(pgid, 0)` success remains positive presence evidence and ESRCH remains
absence evidence. Only Darwin EPERM enters `/bin/ps -axo pid=,pgid=`. That
fallback requires a successful helper exit, empty stderr, nonempty newline
terminated records, strict positive PID/PGID pairs, unique PIDs, and the
supervisor PID with its actual PGID. Matching is exact numeric PGID equality;
any listed member, including a zombie, means present. The helper has a bounded
`communicate` timeout with part of the deadline reserved for kill/reap, and its
reap status and the deadline are checked before accepting a snapshot.

The production workload continues to run in a fresh session. TERM then KILL
remain process-group signals. Signal EPERM triggers an independent absence
probe and succeeds only if that probe establishes the group is empty; a live
member is a capability failure. Direct child wait/reap is required in addition
to group absence. Cleanup proof and fallback process-table rows are retained in
the successful child result and `cleanup-evidence.jsonl`. Failure finalization
attempts a best-effort SIGKILL only against the owned PGID, does not mark
cleanup verified after deadline expiry, and re-raises the original exception
even if defensive cleanup fails.

Static reviewer attention requested: repeated Darwin polls currently persist
each complete process-table snapshot, so a prolonged cleanup interval could
increase evidence volume and consume some of the remaining deadline. Assess
whether compact repeated-snapshot references are needed while retaining an
auditable final absence snapshot. I did not execute these paths.

## Commands and status

Read-only inspection used `rg --files`, `rg -n`, `sed`, `wc -l`, and
`shasum -a 256` for scoped source, prior review, protocol and authority files.
No import, test, training, smoke, suite, ledger mutation, or runtime command was
run. No outcome is claimed for the new tests. The host's `/usr/share/man/man1/ps.1`
was separately inspected by Astra for `-a`, `-x`, and `-o pid=,pgid=` semantics.

Status: implementation frozen for exact Sol static-safety review. Smoke and
suite remain unauthorized until fresh exact Sol PASS and Astra acceptance.
