# Sol independent two-pair closeout review

2026-09-27. Exact `gpt-6-sol` read-only review of the completed fixed 2201/2202 pilot.

**Verdict: CHANGES REQUIRED in the scientific transcription and interpretation.**

The four production owners, source identity, cleanup, ledger, resource-only gate, and numerical values inspected below are valid. The current deliverable omits prespecified stagewise and acquisition quality reporting. No new run, model import, evaluation, source edit, or ledger action is needed. Luna owns the transcription correction; Astra owns the interpretation correction. This review does not authorize any further runtime.

## Exact records reviewed

| Record | SHA-256 |
| --- | --- |
| `execution/update_efficiency/runtime-evidence-004-2201-production-pair.md` | `326244f94a7d915d8a190277586484ca5120c448c8084770bf7be7faecac3ff2` |
| `execution/update_efficiency/runtime-evidence-005-2202-and-pair-summaries.md` | `8ff910238e556d35bd224669a5540421cfe87b1517452ba7b3ef1c3219d1d8f9` |
| `execution/update_efficiency/runtime-evidence-006-two-pair-scientific-transcription.md` (corrected exact-30 version) | `a6a283d3500254af261952dbc4121da3e257a86c1183285cdab9638e488e0d08` |
| `execution/update_efficiency/scientific-closeout.md` (draft) | `d6985872aff78d0d10c208145750c5d27683ff5cf021cb2c6bc73accc2b0340b` |
| `execution/update_efficiency/platform-production-acceptance.md` | `9a3652845efefac6b4e5793cd05705b50b0e1166ffac7b360e404b767e41bc5f` |
| `execution/update_efficiency/second-pair-resource-gate.md` | `a9ce35aaf2974bc79fbfce052caad93e8b783cb2b1f778208d1fd542a4efcaeb` |
| `execution/update_efficiency/reviews/10-platform-implementation.md` | `5771da86fbc7ec3631938a1cec8968bd0c0f2eeb1cfa3bedf6574905f8d76048` |
| `execution/update_efficiency/plan-v3-saturation.md` | `d4ce6e3c6e4c0a7eac46aa96b2a01f442abeed573c3b78e95a2edb874caca6ae` |
| `execution/update_efficiency/spec-03-saturation.md` | `dcca6fa6c3ba0d322a8278d6003c77249c692a1224f37a3a2bad547530285a67` |
| `execution/update_efficiency/command.py` | `e228b53fb52f3a944e6e523e9ce3340c5abb3c02cc16ad2e07729972b1877d84` |
| `execution/update_efficiency/watchdog.py` | `ad5e3030ce148283c2576fa5fb376c512a8f7474bcc5e62e8e2d4e6d749900b2` |
| `execution/update_efficiency/study.py` | `a62a37248421660f94edce139a7e9ca471890bab8c0ba4463edd8ffb6c396204` |
| `execution/model_training_comparison/ledger.jsonl` (158 rows, final EOF) | `ddfe5b2df043d940b1dcbf30ed367483abac1a5935863d123a1e9c6267229da2` |

Owner `result.json` hashes, in launch order: 2201 softmax `53665a21c0d4db741d3aee3196dae7a682f5866f006b0b7db308cd326a407884`; 2201 Schrödinger `990f7d32950d53b6b2ba1c58a47ea3a721e21d0242686ebcc776eff2afb5941a`; 2202 Schrödinger `6b11f3558f9fa9772efa2bcd41e9fd7219ff9b9ac2d019a9a7f48366c51432a9`; 2202 softmax `b3dd6a06253a3c3eb9931a1213c39a89533c21bb6d5053fe58328b636ee8845b`. The four immutable production decision hashes in the same order are `d8157fa1f2051168be1e1eae78a82406be117c38197eb4c595ed280e3bbf0340`, `bc6d11955aee6e0cd8f63920997f092d6b69ab48aeddf74f181b6bfc1d6fa7d7`, `4b4b9ff0246a3cf9bfb1b65ab9cb60bd8c4d4c9ad359957e807fe732f213f2e6`, and `c0f49190aa425fcba8430a831e949735d32577135f6266a2ca7ddda57649b902`.

## Required corrections

1. Frozen `plan-v3-saturation.md:95-103` requires per-seed `ΔQ(u)=Q_SA−Q_SM` in percentage points at all five requested early points, 8000, and follow-on stages, with both fixed curvature values and their range. Evidence 006 contains the four raw Q curves and only paired differences at 8000/16000; the draft closeout likewise omits the stagewise paired table. Add the per-seed paired differences across the full 13-point grid (or at least every prespecified requested point) and state the C range **+0.3931 to +3.0868 percentage points**. The existing C values and mean are correct.

2. Frozen `plan-v3-saturation.md:115-119` requires proper/challenge quality at each milestone acquisition, plus the fixed fragility and mixed labels. Add an acquisition table tied to each reported threshold/owner, or deduplicated by owner and acquisition update with an explicit threshold mapping, including Q, proper KL and Brier, and challenge Q. The saved 2202 softmax score at update 12000 has KL **0.4147427023078981 nat**, so both its exact and tolerant 38.198% acquisitions carry the `KL > 0.40` fragility flag; this does not change their crossing updates. At update 4800, mean paired Q gain is **+0.96923828125 percentage points** while mean KL is worse for Schrödinger by **0.03406037815281315 nat**, exceeding the prespecified +0.02 conflict margin. Thus the positive stage-4800 Q gain must be described as **mixed**. The draft correctly labels the positive final-16000 gain mixed; retain that label. At 2400 the mean challenge gap is below -2 pp, but mean paired Q gain is negative, so the positive-gain mixed rule does not apply there.

3. Update the final interpretation consistently with those fixed-stage and acquisition findings. The primary milestone signs, exact-threshold sensitivity, no observed Q/CE plateau, and two-seed limitation remain as currently stated. Do not alter the thresholds or infer a new result from the reporting correction.

## Checks independently completed

All four `result.json` records have COMPLETE status, the exact 13 updates through 16000, and 16000 batch digests. Within each seed, the full digest arrays and shared initial digest match between modes; config, six input IDs, source hashes, bank identity, and training-support hash match within and across seeds. The shared initial digests differ between seeds. Every one of the four 179-entry manifests matches the 179 on-disk member file hashes with no extra owner file beyond the manifest. Each index result hash and point list matches its result, and all 52 score-to-checkpoint hashes match. The four driver terminals are COMPLETE, child exit 0 without timeout, and carry two exact-PGID ESRCH absence proofs apiece; reservations are released. The real Darwin EPERM-to-`ps` branch was not exercised, as already qualified in review 10.

The ledger's first 154/155/156/157/158 rows hash respectively to `b32f5312f59b91857f8ed886e20be393a9d0c953234c57ff028aa237df4d77ab`, `5a0143b0553750be3d45d24fb837cdffb9a9a1d783b30aebf19e11ca17bb29b8`, `c3129133e0a9d2bad1ab5e98b620115b63debe3c9eb964e7d0cd43cf48e01b0d`, `969a143bf0a7f6860800c1a19c0462685c85ca9e39ad9876909700ecab92a5d6`, and final EOF above. Four distinct UUID-matched B rows charge 171.14780987496488, 352.6548173748888, 370.69515879196115, and 171.895634500077 seconds exactly once, with no driver overhead or fallback row for these owners. The 1.5× second-pair forecast was 256.7217148124473 SM + 528.9822260623332 SA = 785.7039408747805 seconds; each was below its 350/550 ceiling and their sum below remaining B allocation 1276.1973727501463 and stage capacity 1289.4313678320964. Final stage A/B/C/D totals 884.3443774547214 / 3353.1594254599418 / 0 / 694.6458445000296 and qualified global debit 5855.153244667692/7200 match the ledger; all caps hold. The gate record contains no model outcome criterion.

I independently compared all **156** saved Q/KL/challenge-Q score cells to evidence 006, recomputed every CE 100-update block and 2k mean from each 16000-point saved CE curve, and recomputed milestone acquisition/confirmation/intervals, paired differences, grid ratios and conservative bounds, Q 4k smoothed gains, 8k-to-16k gains, and C. The corrected exact-30% seed-2202 difference is **0 updates, ratio 1.0**; evidence 006 now states it correctly. All four Q and CE plateau statuses are RIGHT_CENSORED at 16000. Only 2201 Schrödinger's final Q window qualifies, with a negative gain of -0.19477 pp preceded by a +1.20605 pp window, so there is no final-two confirmation. All final CE relative gains exceed 0.5%. The final mean paired Q advantage for Schrödinger is +1.835123697916663 pp while mean KL is worse by 0.020861117351470337 nat, so the draft's final mixed interpretation is correct. The two-seed pilot does not establish that 16000 is enough for saturation.

No project module was imported and no tests, training, new evaluation, or ledger mutation were performed for this review. Re-review the corrected exact transcription and draft interpretation before accepting a final closeout verdict.
