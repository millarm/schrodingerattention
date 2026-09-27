# Review 18 — v3 dataset results

**Verdict: PASS — reviewed scientific stop (`DATASET_CONSTRUCTION_FAILED`).**  The
saved run is suitable for reporting the frozen construction's failure.  It is not
a complete benchmark, a learning result, or evidence that the domain is
impossible.

## Exact reviewed evidence

- Production manifest SHA256:
  `26ddf4277f1c8e3ab63505cd93c7a643c4b76bf9eaf1cf4c9705f3d629e82464`.
- Independent audit SHA256:
  `f26d8fbeec322746865b41cc9712cf7cfd6bc3572918fb62afe09174caff4e60`
  (`execution/next_level_v3/audits/feasibility-001-audit.json`).
- Audit instrument SHA256:
  `981d9fd0b1c2d4860c193b3504006fc1c9599d6c6e1afe8bd10d622e995573d5`.
- Post-audit ledger SHA256:
  `c2812c96c8a3e457cdc68403c3e498bd296b199a7ceefc9149273b44e6133563`.
- The attempt is `COMPLETE`, has no runner error, binds the expected manifest,
  and records the dataset outcome rather than a timeout.  Every manifest source
  and output hash matched.  The inventory has 768 unique IDs and canonical maps,
  exactly 256 per family.  Re-ranking the saved inventory reproduced the complete
  ranking and retained windows 12–14, 14–16, and 16–18 in order.
- Saved support hashes, selected-row metadata, stage counts, and cross-stage
  identity disjointness all passed for all three proposals.  No pool or proposal
  was regenerated during review.

## Frozen outcomes and shortfalls

| proposal | completed useful prefix | first failed requirement |
|---|---|---|
| 12–14 | training 1024; routine validation 384 | mixed validation 0/8 maps (0/128 pairs); all 256 candidates exhausted at length 12 |
| 14–16 | training 1024; routine validation 384; mixed validation 128; routine test 1536 | mixed test 25/32 maps (400/512 pairs), short by 7 maps/112 pairs; 223 maps rejected, with length-14 exhaustion dominant |
| 16–18 | training 1024 | routine validation I-family 9/12 maps (144/192 pairs), short by 3 maps/48 pairs; L-family and later stages were not evaluated |

The strongest partial construction therefore contains 8 mixed validation maps
and 25 disjoint mixed test maps: 33 maps and 528 qualifying novel pairs.  This is
narrow oracle-level novelty supply only.  It does not satisfy the frozen complete
dataset gate and cannot support the planned architecture comparison.

## Independent recomputation and limits

The bounded audit independently recomputed BFS distances, exact route counts,
and novelty counts for a deterministic stratified sample of 60 saved pairs,
including successful stages and failed prefixes.  All 60 matched.  It also
recomputed 32 sampled training q-target states across all proposals; all matched.
This is sampled oracle validation, not a full replay of every route fact.  Full
artifact metadata/count/hash/disjointness checks and exact saved-inventory
ranking were exhaustive.

The audit command exited 0 after 16.505706541 seconds and charged that whole
duration plus a conservative 3-second startup/static-inspection allowance under
unique ledger ID `7d48aa97-9022-4048-b68e-99fe710d2d18`.  Post-audit operational
debit is 745.131573627 seconds of 7200; the v3 ledger debit is 301.747054625
seconds.  The audit remained below its 120-second cap.

## Final-report check

The substantive counts and interpretation in `execution/next_level_v3/final_report.md`
(pre-update SHA256
`b5ed1ace3dd9e85446b9e6e97002072556f27e95234790c108368164f5fea527`)
are accurate, including the distinction between useful partial supply and a
complete benchmark.  Before freezing that report, replace its two stale
audit-pending statements with this PASS/audit hash and update the budget from
725.625867086 seconds (282.241348084 v3) to 745.131573627 seconds
(301.747054625 v3).  A future larger *prespecified* candidate pool is a reasonable
recommendation; this review does not authorize generation, resampling, threshold
relaxation, or neural training.
