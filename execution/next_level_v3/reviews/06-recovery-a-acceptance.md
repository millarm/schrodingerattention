# Recovery A revision 1 review

**Verdict: CHANGES REQUIRED (Recovery A only).** The implementation is close,
but the bounded A acceptance evidence is not yet complete. Recovery B remains
explicitly deferred and production is not authorized.

## Exact frozen version

- Module `schrodinger/productive_diversity_v3_data.py`:
  `84f791992b81dbbebea66cba793f27481086b33335a2287359fd38d567e56e0a`
- Tests `tests/test_productive_diversity_v3_data.py`:
  `b0abb80bcef5b91db37eea7bdf31051793112c0a6753a2956a451433026181ce`
- Handoff `execution/next_level_v3/handoffs/02b-revision1.md`:
  `ff8e449146d2bc19997df86c009464bd1ddbaa8e35eea6f39706e510dda01ddf`
- Current-hash supplement `execution/next_level_v3/handoffs/02b-revision1-supplement.md`:
  `d519f21221d6f79843548ba08c166f9c9455ddc29eb38509d953553dfee41806`
- Prior review `execution/next_level_v3/reviews/05-recovery-a.md`:
  `e803f71e0e885aa2bb1a0fd50a8c1a7a09af09f08ef885c5b4dd77d037bcfa46`

The first handoff's test hash is superseded by the supplement; the supplement
correctly identifies the frozen test file and reported 20-test command.

## Remaining findings

1. **A failed multi-family stage still omits the unvisited family from its stage
   evidence.** In `run_ranked_proposals`, a held-out failure breaks the family
   loop immediately (`productive_diversity_v3_data.py:514-519`), stores only the
   results already executed (`:520`), and marks only later *stages* as
   `NOT_EVALUATED` (`:522-526`). For example, if validation-routine I fails,
   validation-routine L has no result or explicit `NOT_EVALUATED` record. The
   result rows also carry no explicit family wrapper when the selection is empty,
   so the partial stage is not self-identifying. Recovery A requires complete
   stage records. Record each family explicitly and mark the remaining family in
   the current stage `NOT_EVALUATED`; assert this exact first-family short circuit.

2. **The malformed-metadata regression still does not exercise the endpoint and
   M validation it claims.** `test_validate_inventory_bad_n_endpoints_family_identity_M_length`
   parametrizes only `n`, family, duplicate map ID, canonical bytes, and a
   key/distance mismatch (`tests/test_productive_diversity_v3_data.py:271-279`).
   It never supplies an out-of-range endpoint, wall endpoint, or M below/above
   16..256. The implementation contains those checks
   (`productive_diversity_v3_data.py:376-380`), but Recovery A explicitly requires
   malformed-metadata regressions. Add literal cases for both endpoint classes
   and M bounds. Also add the previously required unknown *training* outcome
   abort; the current parametrization tests an unknown held-out outcome only
   (`tests/...:256-268`).

## Verified closure of Sol05 source findings

- Global validation now runs once before the proposal loop, and training builders
  invoked by the orchestrator use the explicit already-validated seam
  (`productive_diversity_v3_data.py:489-502`).
- Rejected maps retain actual `accepted_rows` for prior successful lengths and
  commit no identity (`:454-484`); the regression asserts retained row identity,
  early stop, and non-commit (`tests/...:216-229`).
- Inventory records now carry `n`, and validation checks n12, family, identities,
  canonical/wall agreement, components, endpoint uniqueness/range/free-cell
  status, stored length, and M bounds (`productive_diversity_v3_data.py:216-224`,
  `:365-380`). This additive metadata does not alter the accepted direct geometry,
  pool, global canonical ordering, map-ID assignment, shortlist RNG, or ranking
  paths.
- Challenge tests now cover accepted exact 1/4 and 3/4 endpoints, 3/16 below four,
  13/16 above 3/4, and 4/20 below 1/4 (`tests/...:185-213`). The orchestration spy
  verifies one global validation call and cumulative exclusions on its full-pass
  path (`:232-253`).

## Independent checks and charge

Static inspection and SHA-256 verification only. No tests, generation, route
search, production, or model work was run. Independent compute charge: **0
seconds**. This verdict is limited to Recovery A implementation evidence and is
not a dataset-feasibility result.
