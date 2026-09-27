# Block 3 narrow-closure review

**Verdict: BLOCKED.** The write-fault closure is correct and the provenance code
now discovers the runtime review/spec inventory, but the central stage-status
closure is not truthful for ordinary scientific failure or multiple proposals.
Production must not launch.

## Exact frozen version

- Runner `schrodinger/productive_diversity_v3_runner.py`:
  `06b941f169e6186df60d72544b0e2b311ffd9c4c869a8e457efc6f832af66041`
- Tests `tests/test_productive_diversity_v3_runner.py`:
  `cd2d0c044c9dfa664136b0dec0f9bfbbfbf3d8956057f08f670e5176ad8dea9d`
- Respecification `execution/next_level_v3/specs/03a-runner-closure.md`:
  `2c81ab82ac35e03223b767f56e7cc268fc9638e7101e7945611f1f883605f6a6`
- Handoff `execution/next_level_v3/handoffs/03a-runner-closure.md`:
  `eeec1a39f8d8f8397b18a2b4e93b168ccc25e4ac2aa4e1762b4ba0d9dcf2d1f9`
- Prior review `execution/next_level_v3/reviews/14-runner-final.md`:
  `ad2ab3eeefe50656c20e6a2d9b32e6664defb6ccb8bd2f5360c1c92f422f2fa9`

## Blocking status defect

The respecification requires one five-stage status map **per attempted proposal**,
with scientific-failure callbacks retaining their outcome, explicit future
`NOT_EVALUATED`, a first missing callback `NOT_COMPLETED_UNKNOWN`, and PASS having
all stages complete.

The frozen implementation does not provide that model:

- `stage_state` is one global five-key dictionary, not keyed by proposal
  (`productive_diversity_v3_runner.py:329-350`). Callbacks from a later retained
  proposal overwrite state from an earlier failed proposal, so a production run
  that advances across up to three windows cannot report each attempt truthfully.
- The callback assignment at line 336 evaluates to `"COMPLETE"` on both branches.
  It neither reads the nested training `result["outcome"]` nor held-out
  `results[*]["result"]["outcome"]`; scientific failures and explicit
  `NOT_EVALUATED` callbacks are therefore marked `COMPLETE`.
- If `run_ranked_proposals` returns normally—whether full PASS,
  `DATASET_CONSTRUCTION_FAILED`, or another prescribed scientific stop—lines
  373-374 replace every status with `COMPLETE`. Thus the most important possible
  production outcome, a completed scientific construction failure, would falsely
  report all five stages complete and erase proposal-level failure/advancement
  status.

The tests do not expose this. They assert one-proposal full PASS, a stage-artifact
write failure, a result-write failure after scientific completion, and a deadline
raised *during* validation-routine artifact writing
(`tests/test_productive_diversity_v3_runner.py:259-275`, `:317-335`). They do not
assert:

1. a real one-proposal scientific held-out failure retains its exact outcome and
   future `NOT_EVALUATED` states;
2. first-proposal scientific failure followed by second-proposal PASS preserves
   two separate proposal maps; or
3. a deadline raised after a completed training callback but before any next
   callback yields training `COMPLETE`, validation-routine
   `NOT_COMPLETED_UNKNOWN`, and only later stages `NOT_EVALUATED`.

This is not a cosmetic assertion omission: current source produces false summary
data for those cases. It directly blocks the results audit from distinguishing a
scientific stop from unvisited work.

Because this was the definitive 03a closure after the bounded two-cycle respec,
do not continue an ad hoc micro-fix loop. A new role decision or explicitly
approved bounded status-model respecification is required. The minimum correction
is proposal-keyed callback state whose transition function decodes actual Block 2
callback payloads, followed by the three literal cases above. No scientific
criterion or data-source change is needed.

## Provenance evidence limitation

The provenance implementation itself is now structurally correct: mandatory
fixed files fail if absent, and deterministic runtime globs include all current
v3 specs and reviews, so the eventual accepted review can be bound without a
source edit (`runner.py:243-253`). However, the success regression still asserts
only one source membership (`tests/...:247-252`), not the respecification's exact
expected path set and every source byte hash; it also does not assert the three
fixture JSON hashes requested for the injected fixture manifest. If a new bounded
status respec is authorized, these are evidence-only assertions to complete in
the same gate, not a change to the working provenance mechanism.

## Verified closure of write faults

The real eight-map parameterized integration now covers both a training-stage
artifact write failure and `result.json` write failure. It verifies the original
write error, absent failed artifact, technical summary, FAILED attempt, one ledger
charge, owned-lock cleanup, exact completed-output hashes, and the appropriate
technical-path stage state (`tests/...:317-335`). Primary-error chaining for
manifest/summary faults and rejection/attempt-log write handling remain accepted.

## Independent checks and charge

Static source/test/spec/handoff and SHA-256 inspection only. No test, generation,
production, or model command was run. Independent compute charge: **0 seconds**.
The approved 120-second future audit reserve remains unchanged.
