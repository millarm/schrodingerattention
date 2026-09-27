# Independent final results review — four fresh paired seeds

**Verdict: PASS**

This review closes the frozen four-seed replication. It is an audit of retained artifacts and reporting, not a new model run or endpoint.

## Frozen report artifacts

- `final_report.md`: `8707ac9ff6c9142c5ab8bd07be4cf8d286098ee351a3acc15116d6e9fe368bce`
- `trajectories.md`: `a001b4e861dc6ecf16c41aca3ada6bec369f79b11085dfe68dc012e3176b68c5`
- `run-record.md`: `83b12b83dd3c30caebe6dde26ab213e2c0c2fe6025ed883da70cf4ece60f65ae`
- pre-signoff `status.md`: `8b9d688cdbe28dd5a0b4ef93086449a987213512de1b2efb106f8d85df57452b`

The four immutable analysis result hashes are:

- 1702 `eac3186ce22771a254259c959d75184e2c6c90111e73d58865015fdbfa6cb9c2`
- 1703 `41c8306a1b73a853890f7d50245e930d83f4ab60db16a41203b503acafee2fdb`
- 1704 `d396354ea75637bb4e6732695cb7bed6616a40a899bd785b357c030d1bc3a95c`
- 1705 `9674408dc4d0a8ec901fd0d50349c4c4a5198938094f91d922faa37e14ffd7a3`

Every analysis manifest entry independently matched its file. All eight training and four analysis attempts are terminal `COMPLETE`; the session record gives an explicit exit 0 for each; the shared lock is absent. No replacement, relaunch, final-test prediction, or extra model job was found.

## Primary recomputation

Fresh-seed SA−SM T1/K32 full-validation quality differences, in percentage points, are:

- 1702: `−2.5211588542`
- 1703: `−0.0585937500`
- 1704: `−1.0677083333`
- 1705: `+1.8522135417`

Independent arithmetic gives mean `−0.4488118490`, sample SD `1.8370849174`, range `[−2.5211588542, +1.8522135417]`, and one positive pair. With the frozen df=3 multiplier, `mean ± 3.182446 × SD / 2` is `[−3.3720236225, +2.4743999246]`. These exactly support the report's rounded values and its qualified conclusion: neither superiority nor equivalence is established with four pairs. Seed 1701 is correctly kept separate as discovery.

## Trajectories and secondary results

Independent extraction reproduces every reported 1k/2k/4k/8k mean quality and `U_valid/K` trajectory. In particular, all four 1k quality differences favor SA, while the fresh mean changes from SM/SA `27.3832/28.0957%` at 1k to `38.1978/37.7490%` at 8k. This is reported as a descriptive stage pattern, not a selected-checkpoint result.

At 8k the independently recomputed challenge means are:

- Q: SM `15.72876%`, SA `15.82031%`, difference `+0.09155 pp`;
- `U_valid/K`: SM `11.17554%`, SA `11.30371%`, difference `+0.12817 pp`;
- pass@32: SM `51.36719%`, SA `54.10156%`, difference `+2.73438 pp`, positive in 3/4 pairs.

Unseen-routine-map C averages are SM `45.41558%`, SA `45.02496%`, difference `−0.39063 pp`, with mixed signs. C and the mixed-composition full-validation challenge are correctly treated as distinct transfer settings.

The corrected solution-coverage language is accurate. Retained `valid_headroom = unique_valid/M` yields exact valid-solution fractions of SM/SA `13.148207/13.115778%` overall and `4.239293/4.630181%` on challenge. `coverage: null` refers instead to unavailable novel-solution coverage `unique_novel/Mnovel`; it is not all-solution coverage. Pass@32 remains finite-sampling task success, a separate quantity.

Other checked aggregates also match: the per-seed complementary greedy counts, duplicate rate/concentration, strict novelty, and the reported four-seed direction variability. The retrospective productive-valid-variation framing is clearly labeled, does not displace the primary endpoint, and does not turn these descriptive secondary patterns into a creativity or architecture claim.

## Pairing, controls, and provenance

Each analysis result retains the reviewed wrapper/plan/resource/decision evidence for both owners, accepted input/source/config identities, distinct initial/final checkpoint hashes, the shared-initial tensor digest, and an exact 8,000-update common batch-prefix digest. Both fresh models score all frozen A/B/C cohorts for every seed.

Each quality-control grid is exactly SA T=`.75,1,1.25` against paired SM T=1. T=1 is independently confirmed as nearest for every seed; only 1703 and 1704 satisfy the frozen mixture and both-strata tolerances. The report does not extend the grid, interpolate, select seeds, or make a same-quality claim for unmatched 1702/1705.

The result correctly distinguishes within-model valid diversity from between-model TV/disagreement and overlap, retains proper-score context, and discloses the historical all-invalid permutation/order limitation. Training-result flags are `test_model_predictions=false` for all eight owners; only immutable test-selection hashes are carried as dataset identity. No final-test scoring is claimed.

## Execution and budget

The ledger contains 128 unique entry IDs and no duplicates. Direct summation gives A `466.80181791697106`, B `2286.76600491805`, D `479.89767720810573`, totaling `3233.4655000431267`; adding the single inherited carry `923.003597253` gives `4156.469097296127/7200`, leaving `3043.530902703873`. All amended stage ceilings are respected. The retained D `13.6s` overcharge and its A correction are transparently preserved rather than rewritten.

Read-only audit commands comprised file/SHA/JSON inspection, one manifest-and-primary recomputation, one secondary/QC recomputation, ledger aggregation, and owner/lock checks. Their retained tool walls total approximately `9.66s`, within the already charged conservative 20-second reporting/audit allowance; no new ledger charge is needed. No inference, tests, training, or source/raw-artifact modification occurred.

The supervisor may now change only the pending-review/status and final budget wording to reflect this PASS. The substantive report is accepted as written.
