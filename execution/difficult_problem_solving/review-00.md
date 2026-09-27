# Independent D0 implementation review

**Implementation SHA-256:** `076d78f09a100934c043f0168e8bf04a14570bb707238202d3c00bdc182f08d2`  
**Tests SHA-256:** `9e2f035a550a245283309891b4349bb3f6dcc33d335c92769860fb42023730c0`  
**Handoff SHA-256:** `cd90402f06cfe74def76610d7bfba6fe485ab7d5ea565fddd012bf51c3b816a8`  
**Specification SHA-256:** `ba1a01a66dd7b711b0af6a7239d1a81bed758aaf1fffc7a79881da251be72f62`

**Verdict: CHANGES REQUIRED**

The primitive finite-bag formulas, prefix sensitivity, duplicate concentration, geometry calculation, equal-map helper, and strict same-map leave-one-out gate are directionally correct. The frozen implementation nevertheless omits material output and evidence required by the D0 contract.

## Required corrections

1. **Preserve seed and mode in every comparative summary.** `summaries(rows)` pools all four seeds within each mode, while its geometry branch pools both modes and all seeds together. This prevents the requested per-seed contrasts and makes geometry comparisons scientifically unusable. Emit routine/challenge and each fixed geometry bin by update × seed × mode, with per-seed SA−SM differences; then optionally aggregate the four seed-level values. Never average the two architectures into one geometry number.

2. **Complete the specified summaries and paired records.** For each stratum/bin retain equal-map summaries for bag pass, empirical `c/32`, expected distinct valid/K, expected distinct valid/M, duplicate concentration, solved support, and valid-route counts under both all-problem and explicitly solved-only denominators as applicable. At K32 save per-problem paired outcomes (`both`, `SM-only`, `SA-only`, `neither`), per-map gain/loss counts, and per-map `c/32` distributions—not just per-map mean pass used by the gate. Raw per-problem rows are useful but do not substitute for the contract's explicit paired summaries.

3. **Make bins and panel integrity literal.** Emit every predeclared category even when empty: lengths `14/15/16`, detour `0/2+`, and multiplicity `1-8/9-64/65+`, with zero support and null metrics. Before analysis, require exactly 24 routine and 8 challenge maps, exactly 16 problems per map, the expected family composition, and identical ordered keys for both modes/all seeds. Before the gate, require exactly 16 paired problems contributing to every seed × challenge-map × mode cell; an average over 15 silently missing problems must fail rather than pass.

4. **Retain exact problem identities and complete provenance.** A raw row currently stores only the positional `problem` index, map/family and derived geometry. Add canonical bytes/hex, start, goal, length and M (or an exact immutable problem-key hash plus the literal fields) so the claimed map/problem identity and canonical orientation are auditable. Bind the frozen D0 specification and approval hashes in addition to the accepted plan, implementation and helper hashes. Keep owner/event/result/input authority evidence without duplicating it unnecessarily per problem if a hash-indexed table is cleaner.

5. **Replace assertion-by-prose with literal integration/safety evidence.** The “composed” test uses two hand-built rows and hand-built bag summaries; it does not execute a real 4-seed × 8-map × 16-problem composition. Add a bounded genuine assembly fixture that exercises real metric calculation, per-seed/per-mode summaries, all fixed bin keys, paired outcomes/distributions and the final gate. Add negatives for missing/duplicated/reordered map/problem cells and event/result binding. Exercise the owned CLI seam to prove stage D, the unique `difficult-d0-001` output, the 56-second timer, durable terminal artifact/manifest behavior, and explicit prevention of model/checkpoint/final-test calls. Source-text absence alone is weaker than the required runtime guard evidence.

## Accounting and scope

The two reported focused runs (`5.3s` and `4.4s`) are correctly retained as separate stage-A charges and remain well within the 100-second development maximum. No production D0 run is authorized by this verdict. Corrections should stay within the additive D0 module/tests; no inference, training, final-test access, new framework, or scientific threshold change is needed.

No independent tests or compute were run for this review.
