# Independent Sol D0 results audit

**Verdict: PASS — the frozen D0 report faithfully represents the saved retained-data result.**

Exact artifacts audited:

- `execution/difficult_problem_solving/d0_report.md`: `ec49398b66df4da0d6a52747965c7a00b402dd523a32d7ca5a9105eaa1685828`
- `execution/model_training_comparison/difficult-d0-001/d0.json`: `7ee658f515bb272285d9339c5e5cb4c16b10c9da71482005a2c624211c6814fc`
- `execution/model_training_comparison/difficult-d0-001/attempt.json`: `d336b8fbdb0c79152f34dc0e233620e1f756ea16f8189b298e4ea1712ceebfe6`
- `execution/model_training_comparison/difficult-d0-001/output-manifest.json`: `00d58e9016c4107fda45e69342192a108cdb64c45f0631e1c5138815c377fa5c`
- reviewed implementation: `1697265245fe1626a270dc033e282877b01a5f3f3091f16da6dd032c336496b1`
- frozen scientific plan: `c31c3ee84131ec4e96dbbd42e073a4ec96be63a0b3fc65058a18275714c035fe`

This was a read-only results audit. I ran no tests, implementation code, model
calls, inference, training, checkpoint loading, final-test access, or D0 rerun,
and made no implementation edits. Seven compact/static shell inspections were
used. Conservatively summing their displayed command walls gives `12.0` seconds,
within the remaining 19 seconds of the already charged 20-second reporting/audit
allowance. No new ledger charge was appended.

## Integrity, ownership, and provenance

The output manifest binds `d0.json` and the terminal `attempt.json` to the exact
hashes above. The attempt is `COMPLETE`, stage `D`, has no error, records elapsed
`18.68660837499192` seconds and charged `22.68660837499192` seconds, and uses the
single immutable output `difficult-d0-001`. The append-only ledger contains the
production UUID and the conservative audit allowance exactly once; all 141 ledger
IDs are unique. Independent summation gives `3359.229483458119` seconds of ledger
charges plus the `923.003597253` carry, or `4282.233080711119/7200` globally.
The ledger's deliberately neutral `FINALIZATION_UNCERTAIN` attempt-charge row is
resolved by the subsequently written, manifest-bound terminal `attempt.json`.

`d0.json` is `COMPLETE`, declares no model calls, new samples, or test access,
and contains exactly updates 1000/2000/4000/8000. It binds eight accepted owners:
softmax and Schrödinger for each seed 1702--1705. Saved source, plan, spec,
approval, replication-analysis helper, and retained-route helper digests all
match the current reviewed bytes. The top-level gate exactly equals the gate
inside the saved 8000-update result.

## Independent result reconstruction

The frozen D0 gate is correctly reported as **PASS**. The four challenge K32 seed
deltas are `-0.78125`, `+3.90625`, `+3.90625`, and `+3.90625` percentage points,
so exactly three of four are strictly positive. The eight same-map deletion
means are all strictly positive:

- map 220: `+3.5714286` pp
- map 344: `+1.5625` pp
- map 386: `+2.4553571` pp
- map 786: `+2.9017857` pp
- map 951: `+2.4553571` pp
- map 1077: `+3.125` pp
- map 1242: `+2.6785714` pp
- map 1288: `+3.125` pp

These reproduce the report's `+1.5625` to `+3.5714` pp range and apply the same
map deletion to both models and all seeds. Challenge map effects comprise five
positive, one negative, and two zero cells. The reported gains/losses per map and
the per-seed both/SA-only/SM-only/neither counts match `paired_k32`; each seed's
four cells sum to 128 problems. Map 344 contributes net seven of the aggregate
net 14 problem-seed successes, as stated.

The independently averaged hypergeometric pass curve at K=1/2/4/8/16/32 is:

- softmax: `15.7288`, `23.8246`, `32.2006`, `39.4941`, `45.6685`, `51.3672`%
- Schrödinger: `15.8203`, `24.1731`, `33.1345`, `41.2876`, `48.1578`, `54.1016`%

The resulting deltas and the prefix-order deltas reproduce the report after its
declared rounding. K1 is the empirical valid fraction and K32 is observed bag
success; intermediate K values are correlated rarefactions of the same retained
bags, not new samples.

On the 512 challenge problem-seed cells per architecture, the raw saved rows give
softmax 263 solved, 2,577 valid draws, and 1,831 distinct valid routes, versus
Schrödinger 277 solved, 2,592 valid draws, and 1,852 distinct valid routes. The
all-problem U/K and U/M and the model-specific solved-only U/K, U/M, and duplicate
concentration values all match the report. Re-pairing raw rows and balancing
problems within map then maps within seed gives shared-solved distinct-route means
of `7.877785669` for softmax and `7.809566649` for Schrödinger, with shared support
62/52/50/58 and all eight maps in every seed. Thus the report correctly separates
broader success coverage from route variety and does not turn model-specific
conditioning into a causal claim.

All predeclared challenge geometry cells match, including their denominators and
conditioning: detour support 6 maps/12 problems and 8/116; lengths 14/15/16 with
48/40/40 problems across eight maps; multiplicity 1--8 empty at 0/0; and the
9--64 and 65+ bins at 8/55 and 8/73. Their reported pass values and deltas agree
after rounding. The 1000/2000/4000/8000 challenge pass and distinct-valid/K rows
also agree exactly with the saved summaries and are properly described as reused,
descriptive training-stage trajectories rather than checkpoint selection.

## Interpretation and authority boundary

The title and conclusions are appropriately limited. D0 supports a post-hoc
diagnosis that the retained SA bags cover somewhat more challenge problems and
that this mean is not dependent on one indispensable map. It does not demonstrate
increased route multiplicity on problems both models solve, statistical
significance, architecture superiority, general planning ability, creativity,
or robustness to fresh training seeds/maps. The four reused seeds, eight repeatedly
analyzed validation maps, selected mixed-composition population, equal-draw rather
than equal-compute comparison, temperature-control alternative, and historical
all-invalid route-order caveat remain material limitations.

PASS validates this D0 artifact and the report's recommendation to **request**
D1 approval. It grants no authority for D1, D2, final-test release, additional
training, new samples, or inference. No required report correction remains.
