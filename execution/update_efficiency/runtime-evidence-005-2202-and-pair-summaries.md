# Runtime evidence 005 — seed 2202 and paired recorded summaries

Date: 2026-09-27. This continues
[`runtime-evidence-004-2201-production-pair.md`](runtime-evidence-004-2201-production-pair.md).
The second-pair authority is Astra's `second-pair-resource-gate.md`, SHA-256
`a9ce35aaf2974bc79fbfce052caad93e8b783cb2b1f778208d1fd542a4efcaeb`. The
accepted implementation review remains `reviews/10-platform-implementation.md`,
SHA-256 `5771da86fbc7ec3631938a1cec8968bd0c0f2eeb1cfa3bedf6574905f8d76048`.
Both fresh immutable decisions bound that review and its full 17-hash source
inventory. Sources remain frozen.

## Commands and owner terminals

| Mode | Exact command | Decision SHA-256 | Tool session / driver owner | Result |
| --- | --- | --- | --- | --- |
| 2202 Schrödinger | `.venv/bin/python -m execution.update_efficiency.command --decision execution/update_efficiency/attempts/platform-production-2202-schrodinger-decision.json --seconds 550 --seed 2202 --mode schrodinger` | `4b4b9ff0246a3cf9bfb1b65ab9cb60bd8c4d4c9ad359957e807fe732f213f2e6` | tool session `16108`; `driver-4eca72f6-77cb-4b43-885d-67180a9a3ad0` | exit 0; COMPLETE |
| 2202 softmax | `.venv/bin/python -m execution.update_efficiency.command --decision execution/update_efficiency/attempts/platform-production-2202-softmax-decision.json --seconds 350 --seed 2202 --mode softmax` | `c0f49190aa425fcba8430a831e949735d32577135f6266a2ca7ddda57649b902` | tool session `15280`; `driver-359fc554-b247-42f7-af7f-9c27a405b780` | exit 0; COMPLETE |

The 2202 Schrödinger owner is
`attempts/update-efficiency-2202-schrodinger-16000`, UUID
`f18fda75-45ff-408e-b125-1e12ec2c9af4`. Its attempt, result and index are
COMPLETE, with seed/mode 2202/Schrödinger, 16,000 updates, the exact 13-point
grid, and a fully closed 179-file output manifest including result/index,
scores and checkpoint bindings. Its outer child PID/PGID was 22786; exit 0,
not timed out, direct child reaped, and `cleanup_verified=true`. The 130-byte
cleanup log has two ESRCH absence proofs for PGID 22786.

The 2202 softmax owner is
`attempts/update-efficiency-2202-softmax-16000`, UUID
`c1af6a2c-836a-4893-bedc-b48ede5884d4`. Its attempt, result and index are
COMPLETE, with seed/mode 2202/softmax, 16,000 updates, the exact grid and a
fully closed 179-file output manifest. Its outer child PID/PGID was 24066;
exit 0, not timed out, direct child reaped, and `cleanup_verified=true`. The
130-byte cleanup log has two ESRCH absence proofs for PGID 24066.

No Darwin `ps` fallback was needed. The `driver.lock` is absent. The immutable
B ledger charge rows have status `FINALIZATION_UNCERTAIN`, the accepted
pre-finalization status emitted before terminal artifacts; matching UUIDs,
COMPLETE owner artifacts and driver validation establish completion. No ledger
row was changed. Neither owner has a fallback row or driver-overhead row.

## Complete pair identity check

All four fixed owners were rechecked: each has COMPLETE driver and owner
terminals, unique UUID-matched B charge, the exact grid, a closed 179-file
manifest, and verified cleanup. For each seed, softmax and Schrödinger match on
the shared-initial digest, 16,000 batch digests, config hash, input IDs, source
hashes, complete bank identity, and training-support hash. The same config,
input, source, bank and training-support identities also match across seeds.
The per-seed shared-initial digests are:

- 2201: `ced35b599a1d161a24e726c4e6288cac9e17fbfae64a7cc1fb18eddf4487d0fa`
- 2202: `bc45ada0dea9f1a31f5a11961fc53abcef945a06c6790e0085cfcef68ff8ce8e`

The exact input/config hashes are recorded in runtime evidence 004 and the
four immutable decisions. The full 17-file source inventory is recorded in
the accepted implementation review and repeated in every decision/start record.

## Exact values transcribed from saved summaries

The following entries transcribe each owner's existing `result.json` summary
and its saved `score-8000.json`/`score-16000.json`. No new evaluation or
estimator was run. Plateau confirmations are `null` because each saved status
is `RIGHT_CENSORED`.

| Seed / mode | Q plateau status / confirmation | CE plateau status / confirmation | Tolerant 30% milestone status / update / confirmation | Tolerant 38.198% milestone status / update / confirmation |
| --- | --- | --- | --- | --- |
| 2201 softmax | RIGHT_CENSORED / null | RIGHT_CENSORED / null | ACQUIRED / 2000 / 2400 | ACQUIRED / 6000 / 8000 |
| 2201 Schrödinger | RIGHT_CENSORED / null | RIGHT_CENSORED / null | ACQUIRED / 3600 / 4000 | ACQUIRED / 8000 / 10000 |
| 2202 Schrödinger | RIGHT_CENSORED / null | RIGHT_CENSORED / null | ACQUIRED / 2000 / 2400 | ACQUIRED / 10000 / 12000 |
| 2202 softmax | RIGHT_CENSORED / null | RIGHT_CENSORED / null | ACQUIRED / 3600 / 4000 | ACQUIRED / 12000 / 14000 |

Each checkpoint cell is `Q / KL / challenge Q` as recorded:

| Seed / mode | Update 8000 | Update 16000 |
| --- | --- | --- |
| 2201 softmax | 0.3816080729166667 / 0.37053917348288573 / 0.16259765625 | 0.3985514322916667 / 0.4073837601192799 / 0.147705078125 |
| 2201 Schrödinger | 0.3948893229166667 / 0.37432028808331375 / 0.14404296875 | 0.40900065104166666 / 0.447383435837588 / 0.158935546875 |
| 2202 Schrödinger | 0.36888020833333335 / 0.37438273858842147 / 0.1484375 | 0.415234375 / 0.456706166254046 / 0.1630859375 |
| 2202 softmax | 0.36549479166666665 / 0.3934873109196884 / 0.166015625 | 0.3889811197916667 / 0.45498360726941345 / 0.170166015625 |

## Ledger and stop point

Ledger EOF before the 2202 pair was
`c3129133e0a9d2bad1ab5e98b620115b63debe3c9eb964e7d0cd43cf48e01b0d` (156
rows). After Schrödinger it was
`969a143bf0a7f6860800c1a19c0462685c85ca9e39ad9876909700ecab92a5d6` (157
rows). Final EOF after softmax is
`ddfe5b2df043d940b1dcbf30ed367483abac1a5935863d123a1e9c6267229da2` (158
rows).

The seed-2202 owner charges are 370.69515879196115 seconds for Schrödinger
(elapsed 366.69515879196115) and 171.895634500077 seconds for softmax (elapsed
167.895634500077), each including its two-second startup and two-second
finalization allowances. Combined seed-2202 charge is 542.5907932920382
seconds. Across the two authorized pairs, four B owner charges total
1066.3934205418918 seconds. Final stage totals A/B/C/D are
884.3443774547214 / 3353.1594254599418 / 0 / 694.6458445000296 seconds; the
qualified global debit is 5855.153244667692 / 7200 seconds. No retry,
replacement, manual ledger edit, extra seed, or horizon extension occurred.

This record ends the authorized 2201/2202 pilot operation. It does not
authorize additional runs or make a research conclusion.
