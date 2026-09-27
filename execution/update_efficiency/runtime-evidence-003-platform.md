# Runtime evidence 003 — platform cleanup repair

Date: 2026-09-27. Operator: Luna (`gpt-6-luna`). This record covers only the
review-authorized stage-A smoke and suite. It makes no production or scientific
claim.

## Authorization and frozen source

Astra accepted the exact Sol static PASS in
`platform-static-acceptance.md` (SHA-256
`5f8b1fef7fed504451b8ff19ffd896bc35eb959adde722d1b510b69e375b18a8`). The
review used was `reviews/09-platform-static.md` (SHA-256
`9654feb97c88aa2efc43ae9f3f1ec1597a537466b2d1f5a2a18fea543d1fd965`). The
driver-verified authority inventory contained 17 hashes for both decisions.
The exact source hashes were:

| File | SHA-256 |
| --- | --- |
| `execution/update_efficiency/command.py` | `e228b53fb52f3a944e6e523e9ce3340c5abb3c02cc16ad2e07729972b1877d84` |
| `execution/update_efficiency/watchdog.py` | `ad5e3030ce148283c2576fa5fb376c512a8f7474bcc5e62e8e2d4e6d749900b2` |
| `tests/test_update_efficiency.py` | `4d5d9dbf1058b439383311e0ece0f73ba310b7fcbe67a3c63e0a0490fbe86fb5` |
| `execution/update_efficiency/plan-v3-saturation.md` | `d4ce6e3c6e4c0a7eac46aa96b2a01f442abeed573c3b78e95a2edb874caca6ae` |
| `execution/update_efficiency/spec-03-saturation.md` | `dcca6fa6c3ba0d322a8278d6003c77249c692a1224f37a3a2bad547530285a67` |
| `execution/update_efficiency/spec-09-platform-cleanup.md` | `4dc2ed2fb1b7bf182f924abfb571b4fd70eb891d476e8c171a8184740b216f67` |
| `agent_execution_protocol.md` | `983a63fd480510994721d980ee866f08e3cba6b767fcbadd5cef7491d437d1c5` |

The complete per-decision inventories are preserved in the durable decision
files listed below and in each driver's `start.json`.

## Commands and outcomes

Both commands ran from `/Users/gmh-company/codex/schrodinger` using the reviewed
driver and the exact static review path/hash.

| Authorized command | Decision SHA-256 | Exit / result | Captured pytest output |
| --- | --- | --- | --- |
| `.venv/bin/python -m execution.update_efficiency.command --decision execution/update_efficiency/attempts/platform-smoke-decision.json --seconds 10 --seed 2201 --mode softmax` | `d3c8a54abf29ec8382b0bc407df88657af6f07303268f1178fd438562e44ac4b` | exit 0; driver `COMPLETE` | `1 passed in 0.49s` |
| `.venv/bin/python -m execution.update_efficiency.command --decision execution/update_efficiency/attempts/platform-suite-decision.json --seconds 30 --seed 2201 --mode softmax` | `2b9ceebe5c2646f2948a690593e4b25d4180c885bd60159d023bf4eaaf20c2ed` | exit 0; driver `COMPLETE` | `42 passed in 3.23s` |

Each decision was preflighted by importing only the reviewed command module and
asserting that its 17 authority hashes, current ledger EOF, and review binding
matched. Smoke bound ledger EOF
`ffb377e0aaf76ce0c46f7d015f6d7f54976d9f9bcb84258fd6942e3116c3aaf5`; suite
bound the post-smoke EOF
`758dc272c83fccb33c6e79cd5461ddbc72394ee9927439e5a66171af6e8142e8`.

## Durable supervisor evidence

The smoke owner is
`attempts/driver-999dcae7-177a-41ae-9967-65145bac501b`. Its child terminal
records PID/PGID 18086, exit 0, no timeout, and verified cleanup. Two final
`killpg(pgid, 0)` ESRCH proofs establish group absence; the direct child was
reaped. The captured evidence log is 130 bytes, stdout 98 bytes, stderr 0.
Its durable terminal says COMPLETE and records a charge of
1.6837607501074672 seconds including the one-second allowance. The A ledger
charge is 1.68274779105559 seconds, status COMPLETE, with no resource overrun.
The slight terminal-vs-ledger difference reflects finalization after the
append-only charge.

The suite owner is
`attempts/driver-17fb6073-0690-4b1b-ad9e-658063ac5e0a`. Its child terminal
records PID/PGID 18331, exit 0, no timeout, and verified cleanup. Two final
`killpg(pgid, 0)` ESRCH proofs establish group absence; the direct child was
reaped. The captured evidence log is 130 bytes, stdout 99 bytes, stderr 0.
Its durable terminal says COMPLETE and records a charge of
4.595999749843031 seconds including the one-second allowance. The A ledger
charge is 4.594696291955188 seconds, status COMPLETE, with no resource overrun.
The complete inner parent/descendant fixture evidence, source hashes, PIDs,
readiness records, parent reap record, and six group-probe/signal entries are
copied to
`attempts/driver-17fb6073-0690-4b1b-ad9e-658063ac5e0a/watchdog-descendant-fixture-evidence.json`
(SHA-256 `4a456714771ced79241f0c3336952d87f5d3834cdcf32ab2acac8310e4d605f5`).
That fixture confirms parent PID 18346 reaped descendant PID 18347 after group
SIGTERM, and the final ESRCH probes established absence of PGID 18346.

On both outer supervisors and the inner real descendant fixture, ordinary
`killpg` probes/signaling worked; the Darwin `ps` fallback was not invoked.
Therefore actual process-table snapshot size and enumeration timing are
not applicable (zero ps evidence bytes). This run verifies real group
termination and ESRCH absence on this host, while it does not demonstrate a
runtime EPERM-to-`ps` fallback path.

Both durable `terminal.json` files are COMPLETE. `execution/update_efficiency/driver.lock`
is absent. The outer child terminal and evidence logs are under the owner paths
above; stdout/stderr are retained there as raw logs.

## Ledger and charges

No manual ledger edits occurred. The driver appended exactly two A
`attempt_charge` rows:

| Snapshot | SHA-256 | Rows | Stage A total |
| --- | --- | ---: | ---: |
| Before smoke | `ffb377e0aaf76ce0c46f7d015f6d7f54976d9f9bcb84258fd6942e3116c3aaf5` | 152 | 878.0669333717107 s |
| After smoke | `758dc272c83fccb33c6e79cd5461ddbc72394ee9927439e5a66171af6e8142e8` | 153 | 879.7496811627663 s |
| After suite | `b32f5312f59b91857f8ed886e20be393a9d0c953234c57ff028aa237df4d77ab` | 154 | 884.3443774547214 s |

Combined new-study A charge: **6.277444083010778 seconds**. The qualified
global debit moved from 4782.482380042790 to 4788.759824125801 seconds. B, C,
and D totals did not change. Both envelopes were reserved and released
normally. No retry or production launch occurred.

## Limits and handoff

The static review's noted limitation remains: repeated Darwin polling can
create large full-table evidence logs; this runtime did not exercise Darwin
fallback. The smoke and suite qualify the reviewed implementation for these
bounded commands only. They do not authorize production. Sol must review this
exact implementation and runtime evidence, including the limitation, before
Astra can make a separate production decision.
