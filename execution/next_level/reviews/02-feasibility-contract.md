# Stage 0 feasibility-contract review

## Verdict: PASS

The Stage 0 contract is scientifically consistent with the accepted next-level plan and sufficiently deterministic for implementation. It freezes geometry, canonical identities, candidate construction, split ownership, seeded selection, bin matching, complete supervised suffix support, novelty feasibility, failure semantics, and compute safety before any inventory outcome is visible.

This PASS authorizes only the separately supervised Stage 0 implementation/tests described by the contract. It does not establish that the requested maps, joint-bin flows, or novelty stratum exist, and it does not authorize model construction, pilot training, paired training, or later evaluation.

## Exact documents reviewed

- Stage 0 contract: `execution/next_level/specs/00-feasibility-contract.md`, SHA-256 `a97ec73d2b4612f7c3e5a28415922dc3925f5d852f9dbf11ebc3a74b03df58ef`
- Authorized plan: `next_level_learning_plan.md`, SHA-256 `7ebe049dcdbeeffea8933242fe90fcd794698741869c6e7102726d4496279464`
- Accepted plan review: `execution/next_level/reviews/01-plan-revision.md`, SHA-256 `8a4ca134ffd378e38afb1b225032c3607aedcd97b2b5fe548001a6612bfc5421`

## Scientific and deterministic checks

- The two-component triomino geometry, row-major coordinate/action encoding, explicit eight D4 transforms, lexicographically minimal canonical wall bytes, global inventory order, and canonical selected orientation make map identity reproducible. Split exclusion occurs at canonical-map level, so changing start/goal or reversing a route cannot leak a map across splits.
- Exact BFS distance and dynamic suffix counts define candidates and `q`; route replay independently verifies legality, first goal arrival, final goal, and shortest length. Exhaustive small-grid comparison and dynamic-versus-enumerated tests provide an appropriate independent oracle check without running the full inventory before implementation review.
- Map selection is seeded and completed before bin feasibility or novelty is inspected. No replacement, retry, novelty ranking, quota relaxation, or model-outcome selection is permitted. Insufficient family inventory and infeasible joint flow have explicit stopping outcomes.
- The two median marginals, tie convention, four joint cells, Hamilton remainder allocation, deterministic Edmonds–Karp insertion/traversal order, per-map capacity 16, and seeded within-map/cell ranks fully determine the requested 16 problems per selected map. Tied medians may produce unequal empirical marginal bins, but this is disclosed rather than retrospectively repaired.
- Training support includes every shortest suffix from every nonterminal state in the union of supervised DAGs, not only original-start or sampled routes. D4 plus reversal action-byte canonicalization, length preservation, global deduplication, sorted binary representation, and hashing match the accepted conservative novelty definition.
- `M_novel` counts distinct exact test routes whose signature is absent from the full training suffix support. The IL gate remains at least 256/512 qualifying problems over at least 16 maps; novelty never affects selection, and failure stops before any model is constructed.
- The required artifacts retain complete inventory/eligibility evidence, selected maps/problems, bins/flows, supervised state/`q` records, exact support, and per-problem route/novelty records. Earlier scientific failures are represented as `NOT_EVALUATED`, not misleading zeroes.

## Safety and scope checks

- Implementation is additive and limited to one feasibility module, its tests, and new next-level records. It explicitly excludes model, optimizer, sampling, and later-stage scaffolding.
- The fresh-output and owned-lock design, independent next-level ledger, advisory append locking, two-second startup allowance, rejected/failed-attempt charging, 600-second Stage 0 deadline with 30-second reserve, and 7,200-second global ceiling are appropriate. Scientific-gate failure remains distinct from compute failure.
- The required full command-result capture, yielded-session polling to an observed exit code, single invocation, and no file-existence completion inference directly address the prior procedural failure mode.
- The next gate remains conditional: Terra implementation/tests, independent implementation review, Astra acceptance, one explicitly authorized inventory invocation, confirmed exit, then independent arithmetic/oracle/support audit. A reviewed Stage 0 PASS is required before any pilot specification.

## Review boundary

This was a document-only review. No geometry enumeration, candidate generation, flow solve, suffix enumeration, feasibility inventory, data artifact, model construction, or training was performed. Counts, runtime, and the novelty gate remain genuinely unknown until the approved implementation passes review and the single Stage 0 invocation is authorized.

