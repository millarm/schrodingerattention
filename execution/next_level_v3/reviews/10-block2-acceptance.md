# Block 2 correction-cycle 1 review

**Verdict: CHANGES REQUIRED.** One precise negative regression remains; all
other Sol09 findings are closed. Production remains gated, and the already
accepted Recovery A and genuine composed fixture are not reopened.

## Exact frozen version

- Module `schrodinger/productive_diversity_v3_data.py`:
  `4aa4779877781f2b0211397c3938185ad6ec5154040fecdef3d9f7eac7e84f08`
- Tests `tests/test_productive_diversity_v3_data.py`:
  `222edc7e152d1f2a1edbe15ac792f64d30a2423cc2c90010fd39f5323b4a4c09`
- Handoff `execution/next_level_v3/handoffs/02c-revision1.md`:
  `468ed4abd15b389e4f286c779e9d9f5654e9a96d9f7bb5bc1ab44b374edf2cf9`
- Prior review `execution/next_level_v3/reviews/09-composed-fixture.md`:
  `e432735d436f822cf911d391faf2e32395e6131bb7656a0b9415a50668c18436`

The three fixture hashes match Sol09 and the correction handoff.

## Remaining finding

`test_real_on_use_bfs_distance_or_count_mismatch_is_technical` does not exercise
an on-use BFS distance mismatch for its `index == 2` parameter
(`tests/test_productive_diversity_v3_data.py:58-64`). It increments the stored
distance from 12 to 13 while leaving the row under shortlist key 12. The initial
`validate_inventory_records` call rejects `d != length` at
`productive_diversity_v3_data.py:376-379`, before `build_training_support` can
reach cached BFS reproduction at lines 413-416. Thus the distance case proves
only the already-covered metadata key/length check. The `index == 3` count case
does pass metadata and reaches the real oracle mismatch, so count coverage is
valid.

Add one genuine distance-oracle case whose static metadata is internally valid
but whose real BFS distance differs—for example, place a real length-13 endpoint
pair under key 12 with stored `d == 12` and a valid-range M, then assert the
builder's BFS-on-use reproduction raises `SelectionTechnicalError`. The fixture
should make clear that metadata validation completed before the oracle defect.
No production source or scientific criterion needs changing.

## Verified Sol09 closures

- The test freezes and asserts complete family/length M values: I 21/28/28, L
  28/75/122, and mixed 148/84/140; mixed Mnovel remains 89/35/60 per map
  (`tests/...:28-43`). The same exact table is recorded in the handoff.
- The real count/M on-use mismatch raises technically (`tests/...:58-64`,
  `index == 3`).
- An already excluded eligible map records `EXCLUDED`, performs no route-oracle
  call, and cannot commit (`tests/...:67-71`).
- The three-proposal regression preserves first-proposal scientific-failure
  evidence, accepts the second, and makes any third evaluation fail immediately
  (`tests/...:344-356`).
- A technical training outcome with a later retained proposal raises and records
  only the first proposal attempt, proving no scientific advancement
  (`tests/...:359-364`).

## Independent checks and charge

Static source/test/handoff and SHA-256 inspection only. No test, route search,
generation, production, or model command was run. Independent compute charge:
**0 seconds**. This is an implementation-evidence correction, not a scientific
or feasibility result.
