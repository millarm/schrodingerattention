# Recovery B / overall Block 2 review

**Verdict: CHANGES REQUIRED.** The real composed-success fixture is valid and
materially closes Recovery B's positive path, but the remaining frozen Block 2
acceptance matrix and handoff evidence are incomplete. No production launch is
authorized.

## Exact frozen version

- Module `schrodinger/productive_diversity_v3_data.py`:
  `4aa4779877781f2b0211397c3938185ad6ec5154040fecdef3d9f7eac7e84f08`
- Tests `tests/test_productive_diversity_v3_data.py`:
  `4f7b69b24e9e256fd501dc28b951ad854bbdca469dcfb28d93634ac2fbaf9e84`
- Recovery B spec `execution/next_level_v3/specs/02c-composed-fixture.md`:
  `3a0b3cff0356662794dc1d72ce64025096b648de958e794f1c4e8c19bdf9d37b`
- Handoff `execution/next_level_v3/handoffs/02c-composed-fixture.md`:
  `6f8ba57f4c163763fb52dd3e2321c79d1ce9352a47a5f81949c0bed77bb1179f`
- I8 fixture: `dc0e76fc9b992a6c4e6acc53c0fa6be7b28605491b00bc2bf55513f01350950d`
- L8 fixture: `b804bb2a1e9a7dbdac60aa8bc8012941f1e85297f09d4e068c5b839a103ec653`
- mixed fixture: `b9839045acf41109292ac18dbb528f276d3f0c9ee0f70c3a1f2ba819827759f4`

Recovery A remains accepted by Sol08 and was not reopened.

## Findings requiring correction

1. **Expected M evidence is not frozen or asserted completely.** The composed
   test recomputes every pair's distance and M while loading fixtures
   (`tests/test_productive_diversity_v3_data.py:21-24`), and the implementation
   verifies those recomputed values against itself. It never asserts the selected
   rows' M values against independent frozen expected constants. The L8 and mixed
   JSON happen to contain extra M fields that the loader ignores; the I8 fixture
   contains only endpoint pairs. The handoff gives no geometry/pair table and no
   actual M table despite spec02c lines 25-26 and 45-46 requiring saved route
   counts and actual M/Mnovel. Freeze expected `(length, M)` for all nine distinct
   family pair definitions (or an equivalent complete table) and assert every
   selected row. Keep the already asserted mixed Mnovel values 89/35/60 per map.

2. **The explicitly required remaining negative matrix is not complete.** The
   new revision adds only the composed-success test. Existing tests cover stored
   M bounds/length/family/identity metadata, challenge boundaries, cache keys,
   and failed-map noncommit. They do not exercise:

   - a real on-use BFS **distance** mismatch and a real on-use BFS **count/M**
     mismatch raising `SelectionTechnicalError`;
   - actual held-out leakage prevention by presenting an otherwise eligible map
     whose identity is already excluded and asserting `EXCLUDED`, no oracle
     visit, and no commit;
   - first-full-PASS stopping with a third retained proposal that would fail if
     evaluated;
   - a technical training or held-out defect with a later retained proposal,
     proving the exception aborts rather than advancing; and
   - preservation of the completed failed proposal's evidence when a later
     proposal succeeds.

   These are literal acceptance requirements in spec02c lines 38-43 and original
   spec02 lines 44-49. Positive split disjointness and mocked cumulative exclusion
   arguments do not replace the leakage-negative selector regression; one-proposal
   technical-error tests do not prove non-advancement; and the existing two-
   proposal success test does not assert its failed first proposal evidence or
   have a third proposal against which to prove stopping.

## Positive composed fixture verified

- `_recovery_b_records` constructs exactly eight distinct n12 records from the
  three hashed fixtures and recomputes oracle facts without monkeypatching
  selection, orientations, BFS/routes, signatures, q, support, or eligibility
  (`tests/...:15-32`).
- The real orchestrator reaches `FIRST_FULL_DATASET_PASS`; selected groups cover
  training, both validation strata, and both test strata with three shared
  lengths and quota one (`:33-40`). Canonical identities are pairwise disjoint.
- Passing the real training orientation gate establishes I-H/I-V and all four L
  orientations for the actually selected homogeneous maps.
- Routine rows have zero novelty. Both mixed maps have exact Mnovel 89, 35, and
  60 at lengths 12, 13, and 14, respectively; with frozen M 148, 84, and 140 these
  are strictly within the unchanged partial-novelty bounds (`:40-41`).
- Independently rebuilt all-route suffix support equals the saved support, every
  saved q equals the independent `q_target`, q is normalized, and a distance-one
  state is present (`:42-47`).
- Exact enumerated route sets are compared between every base/variant map for all
  fixture endpoints (`:48-53`), so routine equivalence is demonstrated rather
  than assumed.

## Independent checks and charge

Static code, fixture, test, handoff, and SHA-256 inspection only. No tests, route
enumeration, generation, production, or model command was run. Independent
compute charge: **0 seconds**. The valid tiny fixture is software evidence only
and does not establish production feasibility.
