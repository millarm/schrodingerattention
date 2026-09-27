# Review 02 — pool512 production results

**Verdict: PASS — complete dataset ready under the frozen construction contract.**

This is a dataset-readiness result only.  Neural learnability, usable productive
diversity, calibrated uncertainty, and an attention-architecture advantage remain
`NOT_EVALUATED`.

## Exact evidence

- Production manifest SHA256:
  `305a9dd782befa9209942a2f52ebc0ba31d9d7ca61c913ecfb69fa5cca466395`.
- Independent raw audit SHA256:
  `2930e1f90c3df0a1a40e5da661f3bf6fc98f3741549b74020469b7ca762115a0`.
- Audit instrument SHA256:
  `5f2e2f2c89ddcb987ca0162e75a465c00585524773d57746548c9791895f46e2`.
- Post-audit ledger SHA256:
  `f2f72464e19324945f80cf9eed3f656bbb20bd0208f7461d013effd4d940e3cf`.
- Production process record SHA256:
  `57a6d81532b0cb3bec0fa96f0df09b83e8d5c71e90b6c37f1bc3d0f8a092e540`.

The retained process used one session (`99474`) through explicit exit0, with no
relaunch.  Attempt status is `COMPLETE`, error is null, the lock is absent, and
the attempt/summary bind the expected manifest.  All manifest source and output
hashes matched.  The effective pool is exactly limit512, n12, max-trials200000.

## Expansion, ranking, and selected data

Each new family pool contains512 unique canonical maps (1536 inventory records,
1536 unique IDs/canonical identities).  For every family, all256 old canonical
maps are a subset of the new pool and all16 persisted common draw-prefix rows are
identical.  Production reached512 maps after38962 I-family trials,25404 L-family
trials, and31942 mixed-family trials, all below the unchanged200000 cap.

Exact reranking of the saved inventory reproduced the saved ranking and retained
windows12–14,14–16,16–18.  Proposal12 completed training and routine validation,
then failed mixed-validation supply.  Proposal14 (lengths14/15/16, quota6/5/5)
completed all five stages and was selected.  Proposal16 has no artifacts and all
stages are correctly `NOT_EVALUATED` after first PASS.

| selected proposal14 stage | maps | pairs |
|---|---:|---:|
| training, homogeneous I/L | 64 | 1024 |
| routine validation | 24 | 384 |
| mixed challenge validation | 8 | 128 |
| routine test | 96 | 1536 |
| mixed challenge test | 32 | 512 |
| **total** | **224** | **3584** |

All saved selected rows link to their inventory map and frozen shortlist.  Every
map has16 distinct pairs with the exact6/5/5 length quota; canonical map identities
are disjoint across stages.  Support hashes match for proposals12 and14.  A
supplementary exhaustive metadata pass (exit0) confirmed pair uniqueness and the
stored novelty predicate for every selected row: routine `Mnovel=0`; challenge
`Mnovel>=4` and `1/4 <= Mnovel/M <= 3/4`.  Thus the40 mixed maps/640 challenge
pairs are qualifying oracle opportunities, not claims that every route is novel.

## Independent oracle coverage and limitations

The bounded audit independently recomputed distance, exact route count, and
applicable novelty for60 deterministic stratified saved pairs.  Coverage includes
both proposals12/14, both homogeneous families, mixed challenge rows, all selected
lengths represented before the cap, and proposal12's last failed mixed prefix;
all60 matched.  It independently recomputed32 selected-proposal q states; all32
matched.

Full hashes, counts, row linkage, quota, uniqueness, predicate, support-hash, and
disjointness checks were exhaustive.  BFS/route/novelty and q recomputation were
sampled as stated, not a complete oracle replay.  No pool, inventory, ranking,
proposal, or selection was regenerated.

## Charge and report check

The audit completed exit0 in20.584761375 seconds and charged that full duration
plus a conservative3-second startup/static-inspection allowance under UUID
`92df8962-06c9-4791-ac88-caeb9de91e83`, timestamped by the process at
2026-09-16T11:19:11.955653+00:00.  Post-audit conservative totals are
923.003597253 operational seconds of7200 and479.619078251 dataset-stage seconds
of1600.  The earlier disclosed invalid development UTC fields remain preserved;
they do not affect these charges or result selection.

The substantive counts and interpretation in the pre-update
`execution/next_level_v3_pool512/final_report.md` (SHA256
`30ad5f1e7e31a05031dd610cb33906212f0363961507e3aa71b6360b084a15a7`)
are correct.  Before freezing it, replace `audit pending` and the pending budget
paragraph with this review/audit identity, sampled-coverage limitation, and final
totals above.  Construction PASS authorizes neither model training nor further
pool expansion; either requires a new explicit execution authorization.
