# Sol independent platform cleanup static review

2026-09-27. Exact `gpt-6-sol` review under the prospective role amendment.

**Verdict: PASS for the specification and frozen static safety implementation.**

DRIVER_REVIEW_VERDICT: PASS

This verdict authorizes no import, test, smoke, suite, training, or ledger action by itself. Astra must accept this exact version before Luna may execute the separately specified bounded smoke and suite. Production still requires the later exact implementation review and Astra acceptance.

## Exact version and authority inventory

All entries are SHA-256 of the files inspected. The command's complete `authority_hashes()` inventory is included, including every current `route_policy*.py` match. The existing ledger was hashed read-only.

| File | SHA-256 |
| --- | --- |
| `agent_execution_protocol.md` | `983a63fd480510994721d980ee866f08e3cba6b767fcbadd5cef7491d437d1c5` |
| `execution/update_efficiency/decisions.md` | `b13b9cb8c4ee8283ea1db085a334cb541a9cb315d6c82d518c43499648f356c9` |
| `execution/update_efficiency/plan-v3-saturation.md` | `d4ce6e3c6e4c0a7eac46aa96b2a01f442abeed573c3b78e95a2edb874caca6ae` |
| `execution/update_efficiency/spec-03-saturation.md` | `dcca6fa6c3ba0d322a8278d6003c77249c692a1224f37a3a2bad547530285a67` |
| `execution/update_efficiency/driver-accounting-clarification.md` | `7ab55e8e05ca950597e9c7f09c948a8edbd2756f04854d1dc19851dba82c58c6` |
| `execution/update_efficiency/spec-09-platform-cleanup.md` | `4dc2ed2fb1b7bf182f924abfb571b4fd70eb891d476e8c171a8184740b216f67` |
| `execution/update_efficiency/capability-blocker.md` | `4b013fb287ac1c76ef899ec6a4939c15095b1428eb87f17a9f68811292cb5bbc` |
| `execution/update_efficiency/reviews/08-capability-closeout.md` | `9a29b857e806b1fdb443a91eeb5d27fb1110680e4fec2e062896b424fc1c97c0` |
| `execution/update_efficiency/handoffs/09-platform-cleanup.md` | `71153c045d15352e87e1633c96e3415d90754bd054fa50aa642fe6c8f2e35834` |
| `execution/update_efficiency/study.py` | `a62a37248421660f94edce139a7e9ca471890bab8c0ba4463edd8ffb6c396204` |
| `execution/update_efficiency/command.py` | `e228b53fb52f3a944e6e523e9ce3340c5abb3c02cc16ad2e07729972b1877d84` |
| `execution/update_efficiency/watchdog.py` | `ad5e3030ce148283c2576fa5fb376c512a8f7474bcc5e62e8e2d4e6d749900b2` |
| `tests/test_update_efficiency.py` | `4d5d9dbf1058b439383311e0ece0f73ba310b7fcbe67a3c63e0a0490fbe86fb5` |
| `schrodinger/attention.py` | `e1ce15be10caf4b2165191f9835256602f4f7b8bd11bffa94f676eac40b0fd6a` |
| `schrodinger/route_feasibility.py` | `da36b0150c0b255b7e5482d7dc016505054d9632c8fb3a21d06c2d201bfedbf4` |
| `schrodinger/route_policy.py` | `95cb7463693c7ac696d9034eaf16a155c0363f38e819cbe56c00408d49b170c4` |
| `schrodinger/route_policy_data.py` | `676b8de313fb9c667497b307704b21f137ac55a18e1e19c81be399d3f02e4bb7` |
| `schrodinger/route_policy_evaluation.py` | `fd5cd438e0fbd103857933418008a7c5936b379488857ac6bfa7370aa8ad18ec` |
| `schrodinger/route_policy_experiment.py` | `10cfc1a9a5e21856fd4e80f7c81b7b9243c104d452f10fc2a0062d4b4998036b` |
| `schrodinger/route_policy_metrics.py` | `a471ae2c40973cb15584f924061b3ace24ef5af3b1e31702b79056055f317e34` |
| `execution/difficult_problem_solving/d1_watchdog.py` (historical shared reference) | `2b3fed56e07da5a33c122afa10e9cc5b77df0df77ec492db0bfaf4887708a8c8` |
| `execution/model_training_comparison/ledger.jsonl` (read only) | `ffb377e0aaf76ce0c46f7d015f6d7f54976d9f9bcb84258fd6942e3116c3aaf5` |

## Specification and implementation findings

The bounded specification preserves the frozen scientific plan, budgets, one-owner launch order, and independent review gates. It introduces a platform-specific absence proof only for Darwin `killpg(pgid, 0)` EPERM; EPERM alone remains inconclusive. The local `/usr/share/man/man1/ps.1` describes `-a` as including other users' processes and `-x` as including processes without controlling terminals. `-o` selects the PID and PGID columns. Thus the prescribed `/bin/ps -axo pid=,pgid=` is a complete process selection for this purpose when the helper succeeds; the self PID/PGID check adds a visibility sanity check, not a substitute for successful enumeration.

In `watchdog.py:80-93`, normal ESRCH and successful `killpg` retain their former meanings. Darwin EPERM alone enters the bounded helper. The parser at lines 51-74 rejects unsuccessful status, stderr, empty or non-newline-terminated output, malformed or duplicate identities, nonpositive IDs, and missing/wrong supervisor identity. Exact PGID equality includes zombies. A valid table with no matching row is the independent absence proof. The helper communicates inside the remaining deadline with a reserved kill/reap margin; timeout invokes kill and bounded reap, and unconfirmed reap raises. Deadline checks before and after enumeration prevent late success.

`watchdog.py:129-215` keeps the workload in a fresh session and signals only that owned process group with TERM then KILL. Signal EPERM performs another absence probe; a live member raises capability failure. A successful cleanup requires both a reaped direct child and a final, in-deadline group absence probe. The child terminal carries probe evidence, and the JSONL log fsyncs each proof. On any exception, emergency SIGKILL is attempted against the owned group even if the deadline has expired, while the original exception is re-raised and the driver does not receive a verified terminal. The driver retains its reservation if supervision is uncertain.

`command.py:6,15,35-38,159` redirects only this study to the local watchdog, binds it plus the amended protocol and platform specification in the existing authority inventory, and changes the review paths. Its frozen scientific inventory and accounting paths remain. `tests/test_update_efficiency.py:442-538` statically covers valid and invalid Darwin tables, exact unrelated-group matching, helper timeout kill/reap, normal ESRCH, non-Darwin EPERM, signal EPERM with a live group, and expired deadlines. The retained real parent/descendant fixture at lines 243-282 requires actual parent reaping and a final group absence probe. Existing driver lock/accounting failure tests remain in the file.

No required correction arose in this static review.

## Nonblocking observations and verification limits

Every Darwin cleanup poll appends the full process table both to the in-memory terminal and an fsynced JSONL row. On a host with many processes this may materially shorten the small grace/deadline and enlarge the terminal. This fails closed on overrun, but the bounded smoke should record actual evidence size and timing before any production decision. Any compaction would require a new frozen source version and review.

The deterministic tests do not directly force an unreapable helper or a defensive cleanup failure; those branches are visibly fail closed and preserve the original supervisor exception. Their behavior is a remaining runtime qualification, not proof supplied by this static review. I performed read-only source, manual-page, and hash inspection only. I did not import project code, execute tests or subprocesses, launch training, or modify the ledger. Historical EPERM remains unresolved until the bounded runtime evidence demonstrates an actual complete-group proof on this host.
