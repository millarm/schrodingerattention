# 03b proposal-status model definitive review

**Verdict: BLOCKED.** The redesign fixes the original global overwrite for the
three exercised one-/two-proposal completion cases, and provenance closure is
sound. However, frozen interruption semantics across retained proposals remain
incorrect, and two mandated literal regressions do not assert their complete
requirements. Production must not launch.

## Exact frozen version

- Runner `schrodinger/productive_diversity_v3_runner.py`:
  `eaeca121f8abe6e30fc66656b68112b810223faf39cdcb7cb48bbbaff8e15f4b`
- Tests `tests/test_productive_diversity_v3_runner.py`:
  `46f14d562a5b5e66a7ffd7aa53f87b9ab3c8bc5f185ddba308f7210c5efcc00e`
- 03b spec `execution/next_level_v3/specs/03b-proposal-status-model.md`:
  `780088dc9d56262becb7d8f4007614b208944722e9a86852841a5add304d6422`
- Handoff `execution/next_level_v3/handoffs/03b-proposal-status-model.md`:
  `d1bcb9c5c8e866abb59d0b38f1c4b3eca8eb4e92c60fc248e50b38ee69c832e9`
- Historical blocker `execution/next_level_v3/reviews/15-runner-closure.md`:
  `4d3eac5019be675103fd223fc3f7358f4fa0d51bf2b5e1b787aaa49275028587`

The acknowledged tests-first deviation and ledger overcharge correction are
procedural history; they do not alter the technical verdict.

## Substantive blocker: interrupted active proposal is derived incorrectly

When selection raises before returning a result, `execute_pipeline` sets
`active` to `ranking.retained[0]` unconditionally
(`productive_diversity_v3_runner.py:416`). That is correct only while the first
proposal is active. The frozen design explicitly permits:

1. proposal 1 completes a scientific failure and its future callbacks;
2. proposal 2 begins (or is next) and execution is interrupted; and
3. proposal 1 must remain resolved while proposal 2 receives the first-missing
   `NOT_COMPLETED_UNKNOWN` status.

Current `ProposalStatuses.finalize(active, interrupted=True)` skips every
non-active proposal without resolving its missing states (`runner.py:64-79`).
With `active` incorrectly fixed to proposal 1, an interruption during proposal 2
therefore finalizes proposal 1 as though it were active, leaves proposal 2's
first-missing/later-stage distinction underived, and also leaves wholly
unattempted later proposals as `NOT_COMPLETED_UNKNOWN` rather than explicitly
separate/unattempted. This violates 03b lines 36-41 and would make a production
timeout after scientific advancement unauditable.

The required correction is architectural but bounded: the transition helper,
not `execute_pipeline`'s first-ranked fallback, must derive the active/next
proposal from ordered proposal-local observations. A fully resolved scientific-
failure proposal stays unchanged; the first unresolved attempted/next proposal
gets one `NOT_COMPLETED_UNKNOWN` stage and later `NOT_EVALUATED`; later untouched
proposals are explicitly unattempted. Add a literal real regression: first
proposal scientific failure, then interrupt proposal 2 before its first callback
(and preferably after its training callback as the complementary state), with a
third retained proposal proving unattempted separation.

Per the authorized 03b terms, this substantive gap ends the local correction
loop and requires a parent role decision or a newly authorized bounded redesign.

## Incomplete literal acceptance assertions

The three requested real integrations exist, but two do not assert their full
frozen contracts:

- `test_03b_real_valroutine_three_is_scientific_failure` asserts only training
  `COMPLETE` and aggregate validation-routine failure
  (`tests/test_productive_diversity_v3_runner.py:338-346`). It does not assert
  the required I-family failure evidence, L-family `NOT_EVALUATED`, or exact later
  validation-mixed/test-routine/test-mixed `NOT_EVALUATED` statuses. The helper
  stores only an aggregate stage string and artifact link; family-level outcomes
  survive inside the artifact, but the test never verifies them.
- `test_03b_first_window_training_failure_then_real_second_pass` asserts the first
  training failure and all stages COMPLETE for proposal 2 (`tests/...:349-358`),
  but not proposal 1's exact four future `NOT_EVALUATED` stages or empty future
  work for the passing proposal.

The true between-callback interruption regression is correctly constructed: it
persists real training, raises before the next callback, and asserts training
`COMPLETE`, validation-routine `NOT_COMPLETED_UNKNOWN`, and only later stages
`NOT_EVALUATED`, plus the exact training artifact hash (`tests/...:361-374`).

## Verified closures

- `ProposalStatuses.observe` decodes the accepted training, held-out, and explicit
  `NOT_EVALUATED` callback shapes; only OK becomes COMPLETE, declared scientific
  outcomes are retained, unknown outcomes raise, and successful artifact hashes
  are proposal/stage linked (`runner.py:43-63`).
- The real one-proposal scientific failure, first-proposal failure then real
  second PASS, and one-proposal between-callback deadline all reach their claimed
  high-level outcomes without whole-result mocking.
- Unknown callback rejection and normal early-PASS unattempted-proposal handling
  are directly tested (`tests/...:377-381`).
- Runtime provenance now requires fixed runner/data/helper/tests/plan/protocol,
  dynamically includes every current v3 spec/review, includes all three fixture
  JSON files, and hashes exact bytes (`runner.py:285-296`). The real manifest test
  constructs the exact expected path set and recomputes every hash
  (`tests/...:384-392`). At production invocation the dynamic review inventory
  will include this review without another runner edit.
- Previously accepted stage/result write-fault, compact CLI, PASS corruption,
  budget, ownership, and immutable-artifact behavior remain unchanged.

## Independent checks and charge

Static source/test/spec/handoff and SHA-256 inspection only. No tests, generation,
production, or model command was run. Independent compute charge: **0 seconds**.
The reported conservative cumulative debit remains 540.193791294 seconds; this
review adds no compute charge.
