# Runtime evidence 004 — seed 2201 production pair

Date: 2026-09-27. Operator: Luna (`gpt-6-luna`). This handoff records the
single authorized first pair only. No 2202 owner was launched and no scientific
outcomes are interpreted here.

## Authority and identity

Astra accepted exact Sol PASS in `reviews/10-platform-implementation.md`
(SHA-256 `5771da86fbc7ec3631938a1cec8968bd0c0f2eeb1cfa3bedf6574905f8d76048`)
via `platform-production-acceptance.md` (SHA-256
`9a3652845efefac6b4e5793cd05705b50b0e1166ffac7b360e404b767e41bc5f`). Both
decisions and start records bind the full frozen 17-hash authority inventory
in that review. Principal code/science hashes:

| File | SHA-256 |
| --- | --- |
| `execution/update_efficiency/command.py` | `e228b53fb52f3a944e6e523e9ce3340c5abb3c02cc16ad2e07729972b1877d84` |
| `execution/update_efficiency/watchdog.py` | `ad5e3030ce148283c2576fa5fb376c512a8f7474bcc5e62e8e2d4e6d749900b2` |
| `execution/update_efficiency/study.py` | `a62a37248421660f94edce139a7e9ca471890bab8c0ba4463edd8ffb6c396204` |
| `tests/test_update_efficiency.py` | `4d5d9dbf1058b439383311e0ece0f73ba310b7fcbe67a3c63e0a0490fbe86fb5` |
| `execution/update_efficiency/plan-v3-saturation.md` | `d4ce6e3c6e4c0a7eac46aa96b2a01f442abeed573c3b78e95a2edb874caca6ae` |
| `execution/update_efficiency/spec-03-saturation.md` | `dcca6fa6c3ba0d322a8278d6003c77249c692a1224f37a3a2bad547530285a67` |
| `execution/update_efficiency/driver-accounting-clarification.md` | `7ab55e8e05ca950597e9c7f09c948a8edbd2756f04854d1dc19851dba82c58c6` |

The six input IDs came from hash-verified COMPLETE `prepare-001` metadata only;
`prepared.json` and final-test payloads were not opened. The accepted source
`schrodinger/route_policy_experiment.py` hash was verified as
`10cfc1a9a5e21856fd4e80f7c81b7b9243c104d452f10fc2a0062d4b4998036b`. Its
literal `FROZEN_CONFIG` was parsed using stdlib AST/literal evaluation, and the
accepted canonical JSON SHA-256 yielded config hash
`870f62c96a8b0ed994d3c4d795514bf6fd513c0c771ba32750542b667155fe90`. No
study/model/training module was imported for decision preparation.

Frozen input identities:

| Input | SHA-256 |
| --- | --- |
| `prepared_sha256` | `10e5f96a98b4dcb944cf81b65eb43eb4ed5a8c8211bf9d1f55af2f0bc4814e49` |
| `training_selected_hash` | `8879d863f1780a40821f518f9ec42bfc9cdd73d203cd872104c1acde52572618` |
| `validation_selected_hash` | `dcaeb083dd23fbf2b74bc6fe54de274315f07e307bbb7839952a61734b1fe68c` |
| `test_selected_hash` (metadata only; payload unopened) | `3c9dd9e5e560cb032e31c77ed22831c153f51f7b1e1654546399e0b6ccdb3a5a` |
| `manifest_sha256` | `305a9dd782befa9209942a2f52ebc0ba31d9d7ca61c913ecfb69fa5cca466395` |
| `frozen_source_hash` | `bf7efbddb88bff06029369cba071d79f17340d701928b7f527baa6df7e517329` |

## Commands and terminals

Both launches ran from `/Users/gmh-company/codex/schrodinger` through the
reviewed one-shot driver. Decisions are immutable and retain the exact EOF,
review path/phase/hash, 17 hashes, config/input identity, frozen plan/spec and
clarification.

| Mode | Exact command | Decision SHA-256 | Driver process session / terminal |
| --- | --- | --- | --- |
| Softmax | `.venv/bin/python -m execution.update_efficiency.command --decision execution/update_efficiency/attempts/platform-production-2201-softmax-decision.json --seconds 350 --seed 2201 --mode softmax` | `d8157fa1f2051168be1e1eae78a82406be117c38197eb4c595ed280e3bbf0340` | tool session `81477`, exit 0, driver `driver-c2b725a4-23ed-4201-8145-cdb48977326f` COMPLETE |
| Schrödinger | `.venv/bin/python -m execution.update_efficiency.command --decision execution/update_efficiency/attempts/platform-production-2201-schrodinger-decision.json --seconds 550 --seed 2201 --mode schrodinger` | `bc6d11955aee6e0cd8f63920997f092d6b69ab48aeddf74f181b6bfc1d6fa7d7` | tool session `3193`, exit 0, driver `driver-2595404c-a19d-4164-8860-d50b9e56744c` COMPLETE |

Driver stdout/stderr and start, child-terminal, and terminal records remain in
each driver owner. The softmax outer driver terminal charge is
169.09182437486015 seconds; Schrödinger is 350.5678028750699 seconds. Both
children exited 0, were not timed out, and have `cleanup_verified=true`.
Each cleanup log is 130 bytes and contains two `killpg(pgid, 0)` ESRCH absence
proofs for its exact direct-child PGID (20302 and 21179 respectively). No
Darwin `ps` fallback was required during these production runs. Both driver
reservations were released; `driver.lock` is absent.

## Owner integrity and pairing

The softmax owner is `attempts/update-efficiency-2201-softmax-16000`, UUID
`4a439b42-be8a-4b1f-a3a9-68ead5bdaa26`. Its attempt/result/index statuses are
COMPLETE. Its result has seed 2201, mode softmax, 16,000 updates, and the exact
13-point grid `0, 1200, 2000, 2400, 3600, 4000, 4800, 6000, 8000, 10000,
12000, 14000, 16000`. The 179-entry output manifest matches all on-disk owner
files; result/index, score, and checkpoint bindings were rechecked.

The Schrödinger owner is `attempts/update-efficiency-2201-schrodinger-16000`,
UUID `d68b1535-fcc9-4e0d-bcee-8e02cfe6e3a5`. Its attempt/result/index statuses
are COMPLETE. It has the same exact 16,000-update grid and a fully matching
179-entry manifest and result/index/score/checkpoint closure.

Pair identity was independently checked from the two owner results without
using measured outcomes as a gate. Seed/modes are `(2201, softmax)` and
`(2201, schrodinger)`. Both owners match on `shared_initial_digest`
`ced35b599a1d161a24e726c4e6288cac9e17fbfae64a7cc1fb18eddf4487d0fa`, config
hash, all six input IDs, source hashes, full bank identity, and training support
hash `b3feead79ea397f3b1be56ac1b601428cedf620157e2740a93cc15946f00ccc3`.
All 16,000 batch digests match exactly. The bank has 1,024 rows, selected and
record hash `dcaeb083dd23fbf2b74bc6fe54de274315f07e307bbb7839952a61734b1fe68c`,
candidate hash `9ad349ba3bdf88e5e1e442bc464573c52f9fe8316be173e3168ae703b25e55ad`,
and q hash `7d1821813be8dec4c2f48717383606bac0f95e2bd7be11578957e17ce668b951`.

## Charges and ledger

The two immutable B owner charges are:

| Mode | Owner elapsed | Complete owner charge | Driver-overhead row | Ledger owner-row status |
| --- | ---: | ---: | --- | --- |
| Softmax | 167.14780987496488 s | 171.14780987496488 s | none | `FINALIZATION_UNCERTAIN` |
| Schrödinger | 348.6548173748888 s | 352.6548173748888 s | none | `FINALIZATION_UNCERTAIN` |

Each owner charge includes its recorded 2-second startup and 2-second
finalization allowances. In both cases the external driver charge was lower
than the owner charge, so there was no uncovered overhead to append. The
immutable ledger row's `FINALIZATION_UNCERTAIN` is the accepted
`OwnedAttempt` lifecycle: the row is appended before the final owner artifacts;
the subsequent COMPLETE owner terminal, matching UUID, closed manifest, and
driver validation establish completion. No ledger row was modified.

Ledger sequence:

| Snapshot | SHA-256 | Rows | B stage total |
| --- | --- | ---: | ---: |
| Before softmax | `b32f5312f59b91857f8ed886e20be393a9d0c953234c57ff028aa237df4d77ab` | 154 | 2286.76600491805 s |
| After softmax | `5a0143b0553750be3d45d24fb837cdffb9a9a1d783b30aebf19e11ca17bb29b8` | 155 | 2457.913814793015 s |
| After Schrödinger | `c3129133e0a9d2bad1ab5e98b620115b63debe3c9eb964e7d0cd43cf48e01b0d` | 156 | 2810.5686321679036 s |

Combined pair charge is **523.8026272498537 seconds**. Final A/B/C/D stage
totals are 884.3443774547214 / 2810.5686321679036 / 0 / 694.6458445000296
seconds; qualified global debit is 5312.562451375654 / 7200 seconds. No
manual ledger adjustment, retry, or duplicate launch occurred.

## Stop point

The first 2201 pair is complete with terminal and integrity evidence. This
runtime acceptance authorizes no 2202 launch. Astra must record its separate
resource-only second-pair gate before any later owner decision. No scientific
conclusion is made in this operational record.
