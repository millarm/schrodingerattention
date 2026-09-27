# Update/saturation study: implementation blocked before runtime

2026-09-27. Sol's definitive bounded driver review is BLOCKED:
`reviews/05-driver-final.md`, SHA
`75360e3cd7ac2df4f9b7991a66c13852f33989111f66bc77e1a79bd5d4c0a6a8`.
No smoke, tests, imports, training, inference or ledger mutations occurred for
this study. This is an implementation/evidence failure, not a scientific result.

## Accepted scientific design

`plan-v3-saturation.md` and `spec-03-saturation.md` have independent Sol PASS.
They preserve the requested original8k-fraction points, propose up to two fresh
paired16k runs, distinguish validation-Q plateau from sampled training-CE plateau,
and predeclare censoring, rebounds, common-quality milestones and curve divergence.
No threshold, seed, dataset or budget change is needed to resolve this blocker.

## Exact remaining driver defects

1. The deterministic A-overrun test advances the clock past its envelope before
   child supervision, then expects a marker from a different branch. It does
   not exercise or prove the claimed successful-child overrun handling. Separate
   setup exhaustion and post-child overrun fixtures are required.
2. Accounting is marked certain before a required uncovered-overhead EOF append
   is durably complete, and lock release lacks durable final-terminal certainty.
   An overhead append/fsync failure or final terminal write failure can therefore
   release the reservation. A small explicit certainty/terminal state correction
   plus literal injected-failure tests is required.

Ordinary UUID/fallback, source/review identity, endpoint closure, single-snapshot
ledger and real-hash tests materially improved and are recorded in Sol's review.
They do not waive the two defects. No new unstructured patch cycle is dispatched.

## Preserved version and remaining work

- Driver SHA`0afe1034a5446e9970e9520861a07528f551885d97190409c45713d452fd0e33`.
- Tests SHA`90cb6d2d014d55da43f95badfaf1d4f382e25946b63f47dbb9dea597be856b48`.
- Driver handoff SHA`607b1c2db05a573fa0eed0fd71dcba55d2b2b92a8c73bb63774673dc0d31461e`.
- Scientific draft `study.py` remains the OLD unaccepted single-target draft,
  SHA`79d3114ee643dabb509b06037b86e1a743dc2ebaba5c3a1019b74302d3a4e5ba`.

After driver recovery, the accepted16k science/composition block still must be
implemented and independently reviewed:13-point scoring, Q/CE plateau estimators,
two-seed summaries, actual owned tiny integration and failure tests. Closing only
the two driver findings does NOT make the study training-ready.

## Budget and next authority boundary

Central ledger unchanged SHA
`1340ee945d663e22c7a4fa7bd232c9832b90babe20d3d91662967116d232c3f9`.
Qualified debit4764.416447001050/7200, remainder2435.583552998950. The historical
administrative300s remains nonmeasured/non-proven. New A100/B1800/D100 allocations
are unspent. This is not resource exhaustion.

Protocol permits a genuinely new bounded respecification of the exact two driver
defects, or an explicit user-approved narrow implementation-role exception with
Sol retained as independent reviewer. Astra has not substituted roles or launched
around the failed gate. Parent receives this concrete blocker to choose recovery;
no model/science/resource expansion or automatic rerun is inferred.
