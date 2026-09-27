# Block 3 definitive runner review

**Verdict: BLOCKED pending bounded respecification.** The second correction cycle
closes most Sol13 findings, but three direct acceptance requirements remain
unresolved. Production must not launch. This is an implementation/evidence
blocker, not a scientific outcome.

## Exact frozen version

- Runner `schrodinger/productive_diversity_v3_runner.py`:
  `f63bbf942625b37ffca6f48e3694c7e68c26a63be116d4ab57d4cb49ead19c12`
- Tests `tests/test_productive_diversity_v3_runner.py`:
  `02f2a7c50ddbc7e92c35a28853b65b5991c2ce74a7c00e6f6a6a69427fed90ef`
- Handoff `execution/next_level_v3/handoffs/03-revision2-final.md`:
  `7399ffc3db90b191b1b27efabb3496942a6652d5edbd14ca31f0bdfad53b9145`
- Runner spec `execution/next_level_v3/specs/03-runner.md`:
  `807b71193a55680f0bf4bec84306696f5c909c6bcdc64cd96396f515e3979e15`
- Results-audit spec `execution/next_level_v3/specs/04-results-audit.md`:
  `4ec5ef05b6179931d0b980fc8b1daa22b96e4cfbe748bc33677f04550a1e64fb`
- Prior review `execution/next_level_v3/reviews/13-runner-revision1.md`:
  `463b506593048cc5b203f0febe952445950a23b80a2eadd64027afffaa20e596`

## Remaining blockers

1. **Partial and successful summaries report false stage status.** Every summary
   hardcodes all five stages—including `training`—as `not_evaluated`, regardless
   of completed callback artifacts (`productive_diversity_v3_runner.py:371-375`).
   Thus the post-training deadline case simultaneously lists
   `proposal-12-training.json` under `completed` and `training` under
   `not_evaluated`; on full PASS it still labels every stage not evaluated. The
   new test asserts only that the list is nonempty
   (`tests/test_productive_diversity_v3_runner.py:272-275`), so it blesses the
   contradiction instead of checking truthful status. Derive structured stage
   status per attempted proposal from completed callbacks/result evidence:
   completed stages exactly once, the interrupted/failed stage identified, and
   only genuinely future stages `NOT_EVALUATED`; PASS must have an empty future
   list. Assert exact values in both post-training failure and success paths.

2. **The source/protocol manifest still does not bind the frozen review/spec
   chain.** `_source_hashes` remains a fixed nine-path tuple and includes only
   `reviews/12-runner.md` (`runner.py:243-249`). It omits accepted specs 01,
   02/02a/02b/02c/02d, results-audit spec04, reviews 00–11 and 13, and this final
   gate; it also silently skips any missing listed path via `if path.exists()`.
   That contradicts the required all-plans/contracts/reviews binding and prevents
   the future results audit from establishing the actual accepted version chain.
   Use a deterministic sorted inventory of the required source/helper/test/plan,
   all `execution/next_level_v3/specs/*.md`, and all
   `execution/next_level_v3/reviews/*.md` present at invocation; mandatory fixed
   inputs must fail if absent, not disappear silently. Assert exact path-set and
   byte hashes, including the eventual accepted runner review, in the real success
   integration.

3. **Stage/result exclusive-write faults remain untested.** The new finalization-
   fault regression parameterizes only `manifest.json` and `summary.json`, and
   only after an earlier pool error (`tests/...:278-290`). It correctly proves
   primary-error chaining for those two cases. It does not inject a proposal-stage
   or `result.json` write failure, which Sol13 explicitly required, so it does not
   prove that a normal pipeline write fault becomes the primary technical error,
   produces truthful partial manifest/summary and FAILED attempt, charges once,
   and releases the lock. Add one bounded parameterized test covering a stage
   artifact and `result.json`, with exact reached/output hash and stage-status
   assertions. The rejection-artifact and attempt-log fault cases are now
   adequately separate.

After two cycles, these should be handled by one narrowly documented
respecification rather than another open-ended correction loop. No scientific
criterion, data implementation, pool generation, or model scope needs changing.

## Verified closures

- Primary pipeline errors are re-raised with manifest/summary finalization errors
  chained as their cause; rejection-artifact failure charges once and cleans up.
- Post-training interruption preserves the real training artifact with q states
  and profile, produces a FAILED attempt and one ledger row; only its summary
  classification remains incorrect.
- Effective config now includes family composition, pool/shortlist/split seeds,
  selected quota, budget reserves, platform/CPU and thread environment. Manifest
  output hashes and attempt binding are recomputed in tests.
- PASS validation links the proposal to retained ranking and rejects non-OK stage
  outcomes, wrapper-family sequence, quota/inventory/n/identity/M/novelty and
  support-hash corruptions with literal genuine-result mutations.
- CLI stdout is now exactly compact strict JSON `{outcome, output,
  manifest_sha256}` on success and empty on failure.
- Serialized training and held-out callback artifacts are checked for support/q,
  profile/evidence, live-cache omission, and exact manifest output hashes.
- The approved 120-second audit reserve remains correctly subtractive within the
  unchanged 1600-second stage and 7200-second global caps.

## Independent checks and charge

Static source/test/spec/handoff and SHA-256 inspection only. No test, generation,
production, or model command was run. Independent compute charge: **0 seconds**.
