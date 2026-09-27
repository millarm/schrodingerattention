# Block 2 implementation blocker audit

**Verdict: BLOCKED — not safe to launch production.**

This is an implementation blocker, not a scientific construction outcome. No
production pool, proposal, dataset, or model was run in this review, and the
partial code cannot establish feasibility or infeasibility under the frozen v3
criteria. Block 1's prior acceptance is unaffected.

## Frozen version reviewed

- `productive_diversity_v3_plan.md`: `982674c12fba12bfa4338ae49f76234777af0a287c76de2e062bb4125385d601`
- `execution/next_level_v3/specs/00-dataset-contract.md`: `4d41b6574b557ffb175e55cee04e6a7c4f67b78d660ac2b19de5ab6bf259e039`
- `execution/next_level_v3/specs/02-support-and-lazy-selection.md`: `1e8a6f5592948229906bfd732cbc267919acd354ef420670828fa9b720ecb86e`
- `execution/next_level_v3/specs/02a-fixture-closure.md`: `be016140c1f64b9e665cb5e7ec6c00830074206cfb7d8500bef7aad3f45e826d`
- `schrodinger/productive_diversity_v3_data.py`: `ae168422cd3fa0e897f9eb8b9995e7bef431fb5d4d57206b82e00b70be43da8c`
- `tests/test_productive_diversity_v3_data.py`: `b93185cdb6b3989e390327ade310f9d1630cd92c0737133dac84326d18ab29c3`
- stale handoff inspected only as provenance: `execution/next_level_v3/handoffs/02-selection.md`: `27543486382ab5e8fc862eedaff7067037b22c7dcfb7f61f2e50e71e8472b07b`

The handoff records older module/test hashes (`922876c5...` and `1979e6a7...`),
so its passing-test statement is not evidence for the frozen version above. Its
claim of a routine held-out success is also contradicted by the current test.

## Blocking findings

1. **The composed fixture is not split-disjoint and its routine result is not a
   valid held-out success.** The training selection uses the only I map
   (`tests/test_productive_diversity_v3_data.py:194-205`), then routine selection
   scans the same records with `excluded_identities=set()` (`:210-213`). It can
   therefore select the training identity. This directly violates spec02 lines
   39-49 and spec02a lines 22-24. The regression must use a genuinely distinct
   routine identity and assert pairwise identity disjointness across training and
   all four held-out strata.

2. **Required training orientation coverage is neither present in the fixture
   nor enforced by production logic.** `_i8_components` constructs only
   horizontal I components and `_l8_components` repeats one L missing-corner
   orientation (`tests/...:25-30`). `training_orientation_coverage` merely returns
   sets (`schrodinger/productive_diversity_v3_data.py:341-362`); neither
   `build_training_support` nor the orchestrator calls it (`:373-466`). The
   completed composition must contain I-H/I-V and all four L orientations, and
   selected training maps must be gated with the frozen scientific orientation
   outcome rather than silently accepted.

3. **The proposal orchestrator is still an explicit training-only placeholder.**
   `run_ranked_proposals` executes only `build_training_support` and returns
   `FIRST_PROPOSAL_TRAINING_PASS` (`schrodinger/...:455-466`); its test expressly
   expects only the `training` callback (`tests/...:220-223`). It never constructs
   validation-routine, validation-challenge, test-routine, and test-challenge in
   the frozen order, never enforces cross-split identity exclusion, never returns
   a full successful dataset, and does not preserve reached/unreached stage
   records. Advancement is also not explicitly limited to the declared
   scientific outcomes. Spec02 lines 22-37 and 51-55 remain unimplemented.

4. **Held-out validation and audit evidence are incomplete.** The selector checks
   route tuple length and the stored distance field only (`schrodinger/...:430-436`),
   but does not independently reproduce BFS distance/count or validate selected
   row family/map/canonical linkage. Excluded and raw-ineligible maps are skipped
   without evidence (`:424-426`), and maps left after early quota completion are
   absent rather than recorded `NOT_EVALUATED` (`:450-452`). Thus the required
   scanned prefixes, rejections, selected rows, and untouched-map evidence in
   spec02 lines 22-29 and the technical mismatch rules in lines 47-54 are not
   satisfied.

5. **The declared support-dependent eligibility cache is dead state and the
   cache evidence contract is incomplete.** `ProposalOracleCache.eligibility` is
   allocated (`schrodinger/...:294`) but never read or written; `profile` omits
   its size/hit/miss counters (`:332-334`). Consequently there is no implementation
   or regression proving exact-support-hash separation and same-support hits as
   required by spec02 lines 8-12 and 47. The pair cache also stores full route
   tuples rather than the specified auditable pair-signature entries; whichever
   representation is retained must meet the frozen bound and expose exact
   counters without weakening route/M verification.

6. **The acceptance and negative-test matrix is substantially unfinished.** The
   frozen tests contain one partial three-map composition and no assertions for:
   lazy rejected-map non-commit plus length early-stop; all four split strata and
   their disjointness; independent all-DAG support reproduction; support-hash
   cache separation/hits; exact challenge fractions at 1/4 and 3/4 and rejection
   outside them or below four novel routes; technical M/count/length/family/
   identity defects; or first full PASS versus scientific-only proposal
   advancement. These are explicit acceptance requirements at spec02 lines 39-49,
   not optional coverage additions.

## Partial work observed

The frozen source contains useful bounded primitives: proposal-local BFS/route/
signature caches, exact training M reproduction and normalized q construction,
all enumerated nonempty suffix signatures, and a lazy per-map commit structure.
Those pieces do not compensate for the invalid composed fixture, absent
orientation gate, incomplete held-out evidence, and missing full orchestrator.

## Independent checks and charge

Static inspection and SHA-256 verification only. No tests, inventory generation,
route search, production command, or model work was run. Independent compute
charge: **0 seconds**.

Production authorization must remain withheld until a complete frozen
implementation and current-hash handoff pass independent review. The present
BLOCKED verdict must not be reported as evidence that the v3 construction itself
lacks feasible datasets.
