# Sol independent platform implementation review

2026-09-27. Exact `gpt-6-sol` review of the frozen implementation and the one authorized 10-second smoke plus one 30-second suite.

**Verdict: PASS for the exact implementation and recorded runtime gate.**

IMPLEMENTATION_REVIEW_VERDICT: PASS

This review is not a production launch decision. Astra must separately accept this exact review and source version before Luna may execute the fixed 2201 owner sequence under the existing envelopes and resource gate.

## Exact source and authority inventory

The 17 rows below are the complete `command.py` authority inventory in both immutable decisions and both driver start records. Current local file hashes match each value. The static review binds the same version.

| Authority key / file | SHA-256 |
| --- | --- |
| `accepted_route_policy.py` / `schrodinger/route_policy.py` | `95cb7463693c7ac696d9034eaf16a155c0363f38e819cbe56c00408d49b170c4` |
| `accepted_route_policy_data.py` / `schrodinger/route_policy_data.py` | `676b8de313fb9c667497b307704b21f137ac55a18e1e19c81be399d3f02e4bb7` |
| `accepted_route_policy_evaluation.py` / `schrodinger/route_policy_evaluation.py` | `fd5cd438e0fbd103857933418008a7c5936b379488857ac6bfa7370aa8ad18ec` |
| `accepted_route_policy_experiment.py` / `schrodinger/route_policy_experiment.py` | `10cfc1a9a5e21856fd4e80f7c81b7b9243c104d452f10fc2a0062d4b4998036b` |
| `accepted_route_policy_metrics.py` / `schrodinger/route_policy_metrics.py` | `a471ae2c40973cb15584f924061b3ace24ef5af3b1e31702b79056055f317e34` |
| `attention` / `schrodinger/attention.py` | `e1ce15be10caf4b2165191f9835256602f4f7b8bd11bffa94f676eac40b0fd6a` |
| `clarification` / `execution/update_efficiency/driver-accounting-clarification.md` | `7ab55e8e05ca950597e9c7f09c948a8edbd2756f04854d1dc19851dba82c58c6` |
| `decisions` / `execution/update_efficiency/decisions.md` | `b13b9cb8c4ee8283ea1db085a334cb541a9cb315d6c82d518c43499648f356c9` |
| `driver` / `execution/update_efficiency/command.py` | `e228b53fb52f3a944e6e523e9ce3340c5abb3c02cc16ad2e07729972b1877d84` |
| `feasibility` / `schrodinger/route_feasibility.py` | `da36b0150c0b255b7e5482d7dc016505054d9632c8fb3a21d06c2d201bfedbf4` |
| `plan` / `execution/update_efficiency/plan-v3-saturation.md` | `d4ce6e3c6e4c0a7eac46aa96b2a01f442abeed573c3b78e95a2edb874caca6ae` |
| `platform_spec` / `execution/update_efficiency/spec-09-platform-cleanup.md` | `4dc2ed2fb1b7bf182f924abfb571b4fd70eb891d476e8c171a8184740b216f67` |
| `protocol` / `agent_execution_protocol.md` | `983a63fd480510994721d980ee866f08e3cba6b767fcbadd5cef7491d437d1c5` |
| `spec` / `execution/update_efficiency/spec-03-saturation.md` | `dcca6fa6c3ba0d322a8278d6003c77249c692a1224f37a3a2bad547530285a67` |
| `study` / `execution/update_efficiency/study.py` | `a62a37248421660f94edce139a7e9ca471890bab8c0ba4463edd8ffb6c396204` |
| `tests` / `tests/test_update_efficiency.py` | `4d5d9dbf1058b439383311e0ece0f73ba310b7fcbe67a3c63e0a0490fbe86fb5` |
| `watchdog` / `execution/update_efficiency/watchdog.py` | `ad5e3030ce148283c2576fa5fb376c512a8f7474bcc5e62e8e2d4e6d749900b2` |

Additional exact records inspected: `reviews/09-platform-static.md` `9654feb97c88aa2efc43ae9f3f1ec1597a537466b2d1f5a2a18fea543d1fd965`; `platform-static-acceptance.md` `5f8b1fef7fed504451b8ff19ffd896bc35eb959adde722d1b510b69e375b18a8`; smoke decision `d3c8a54abf29ec8382b0bc407df88657af6f07303268f1178fd438562e44ac4b`; suite decision `2b9ceebe5c2646f2948a690593e4b25d4180c885bd60159d023bf4eaaf20c2ed`; `runtime-evidence-003-platform.md` `42f796214430f29deb4e8c1421d0f9a0e98bb269d0a0a64a4e35b7a3bf0facf3`; retained inner fixture transcription `4a456714771ced79241f0c3336952d87f5d3834cdcf32ab2acac8310e4d605f5`; final central ledger `b32f5312f59b91857f8ed886e20be393a9d0c953234c57ff028aa237df4d77ab`.

## Runtime and cleanup audit

Astra's static acceptance bound the single smoke then single suite. The decisions specify the exact reviewed command, 10/30-second envelopes, seed 2201, mode softmax, working directory, static review path/phase/hash, full 17-hash inventory, and the ledger EOF current at each launch. Each driver's `start.json` repeats its decision path, argv, hashes, and bound EOF. The smoke and suite decision inventories are byte-equivalent after canonical JSON ordering.

The smoke owner `driver-999dcae7-177a-41ae-9967-65145bac501b` has stdout `1 passed in 0.49s`, empty stderr, child PID/PGID 18086 with exit 0, `timed_out=false`, `cleanup_verified=true`, two logged `killpg_zero_esrch` absence proofs, and a `COMPLETE` terminal. The suite owner `driver-17fb6073-0690-4b1b-ad9e-658063ac5e0a` has stdout `42 passed in 3.23s`, empty stderr, child PID/PGID 18331 with exit 0, the same absence proof structure, and a `COMPLETE` terminal. Both outer children were directly waited/reaped by the reviewed supervisor before it returned verified cleanup.

I independently checked the surviving raw pytest fixture files in `pytest-204/test_driver_watchdog_descendan0` against the copied owner record. `parent-start.json` and `parent-ready.json` match exactly (PID/PGID 18346, child PID 18347); `child-ready.json` identifies parent 18346 and shared PGID 18346; `reaped.json` records child 18347, return code -15, and the parent's SIGTERM handler. Their SHA-256 values match the copy. The raw 379-byte `cleanup-evidence.jsonl` also matches SHA `99cc341ae8da3c28e7386441457ed3b33aae0f9477a6eb1bc09d91e70dd3c505`: it records a live group, group SIGTERM, two further live probes, then two ESRCH absence probes. This is actual parent/descendant group termination and whole-group absence evidence; the parent's reap record alone was not used as absence proof.

The earlier EPERM blocker was not repeated in these runs. Actual Darwin EPERM-to-`ps` fallback was **not** exercised: all real absence proofs used normal ESRCH, while the 42 passing tests include deterministic valid/invalid `ps` fallback and failure-path cases. The specification requires the real fixture to use the production supervisor and prove complete group absence, plus deterministic fallback coverage; it does not require an injected real EPERM from the host. The recorded evidence therefore satisfies this gate while leaving real fallback latency and process-table volume unmeasured. Any future EPERM with live members or uncertain enumeration still fails closed under the reviewed code.

## Ledger and limits

The central ledger has 154 newline-terminated rows and final SHA `b32f5312f59b91857f8ed886e20be393a9d0c953234c57ff028aa237df4d77ab`. Its first 152 rows hash to the presmoke EOF `ffb377e0aaf76ce0c46f7d015f6d7f54976d9f9bcb84258fd6942e3116c3aaf5`; its first 153 rows hash to the suite-bound EOF `758dc272c83fccb33c6e79cd5461ddbc72394ee9927439e5a66171af6e8142e8`. The last two rows are unique `COMPLETE` stage-A charges of 1.68274779105559 and 4.594696291955188 seconds, each once for its distinct owner, with `resource_overrun=false`. Their sum is 6.277444083010778 seconds. The stage-A total is 884.3443774547214 seconds; the qualified global debit is 4788.759824125801/7200. The small owner terminal charge differences occurred after the ledger appends and do not add another debit. `driver.lock` is absent.

I performed read-only source, record, raw-file, hash, and ledger-prefix checks. I did not import project code, rerun tests, launch a subprocess or training owner, or write the ledger. No required correction remains. Production remains conditional on Astra's separate acceptance and the frozen per-owner budgets, integrity checks, launch order, and second-pair gate.
