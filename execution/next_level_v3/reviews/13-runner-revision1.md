# Block 3 runner revision 1 review

**Verdict: CHANGES REQUIRED.** The honest raw-capacity integration, selected-
proposal quota use, partial failure skeleton, and budget reserve are improved,
but material provenance, failure-finalization, validation, and CLI requirements
remain incomplete. Production must not launch.

## Exact frozen version

- Runner `schrodinger/productive_diversity_v3_runner.py`:
  `9ebfec7e2999e7b18f6f8054038a1bd9a3778b517faa763ab752429ef744e9bd`
- Tests `tests/test_productive_diversity_v3_runner.py`:
  `0a10f9dd231bab835781e306e70578bea983cb1f185f968066e64a738bef887f`
- Revised spec `execution/next_level_v3/specs/03-runner.md`:
  `807b71193a55680f0bf4bec84306696f5c909c6bcdc64cd96396f515e3979e15`
- Handoff `execution/next_level_v3/handoffs/03-revision1.md`:
  `7befbbf7b8b8864b985e05d199acc098ea7cdf7bf9c3d458b1cda741f2273021`
- Prior review `execution/next_level_v3/reviews/12-runner.md`:
  `c729f9e684f9408ae2cda14d6723139c9c0dbf30c0acf5a2e5f0845461cdb625`

## Remaining material findings

1. **Failure finalization does not preserve the original error when finalization
   itself fails, and required write-fault evidence is absent.** `execute_pipeline`
   catches the scientific/technical error, but a manifest or summary write error
   in its `finally` block is unconditionally re-raised (`runner.py:333-364`),
   replacing the original exception. No test injects pool/stage/result/manifest/
   summary or rejection-artifact write failure, despite the handoff's broad
   “multiple writefault guards” claim. The only mandatory-write test remains the
   `attempt.json` log failure (`tests/...:101-109`). Preserve the original error
   as primary while recording/chaining any finalization failure, charge once, and
   add literal exclusive-write fault cases at least for a stage/result write and
   partial manifest/summary finalization. Rejection-log failure must likewise be
   shown to charge once, clean only owned state, and propagate nonzero.

2. **Partial stage reporting is still generic and tested only before selection.**
   The summary stores reached filenames plus the string “all stages not represented
   by completed callbacks” (`runner.py:356-358`), not structured proposal/stage
   completed/failed/`NOT_EVALUATED` status. The deadline test interrupts while
   fetching the second pool (`tests/...:185-203`); it proves early partial files,
   FAILED attempt, one charge, and cleanup, but not preservation of completed
   proposal-stage callbacks, failed prefixes/profiles, or future stage status.
   Add an interruption after at least one real stage callback and assert the
   partial manifest/summary identifies proposal, completed stage artifact/hash,
   failure/error, and structurally `NOT_EVALUATED` future stages.

3. **Manifest configuration/provenance remains incomplete and essentially
   unasserted.** Effective config still omits `POOL_SEED`, `SHORTLIST_SEED`, and
   all split seeds, as well as the literal per-family shape composition and
   shortlist/ranking seed semantics (`runner.py:340-348`). `_source_hashes`
   includes only review12 and omits the accepted Block 1/2 specs/reviews and the
   current/future runner acceptance chain (`:242-248`), despite the frozen
   requirement to bind plans/contracts/reviews. Runtime provides Python/numpy,
   PID, and three optional thread environment values but no platform/CPU/runtime
   identity. The success test still asserts only manifest existence and a truthy
   attempt field (`tests/...:155-158`); it does not recompute the manifest hash,
   compare attempt binding, verify exact source/input/output hashes, or assert
   selected effective config and budget/runtime fields. Use a deterministic
   complete provenance inventory (including the final accepted review without a
   source-edit cycle) and exact assertions over every required category.

4. **Runner-side PASS validation still trusts unverified stage/result structure.**
   The revised guard correctly uses returned proposal window/quota and validates
   row inventory linkage, exact per-map quotas, training counts, M, novelty, and
   leakage (`runner.py:255-305`). But it does not verify that the returned proposal
   is one of the retained ranked proposals, that each stage result outcome is
   `OK`, or that stage wrapper families are exactly the expected I/L/mixed family
   sequence. Selected rows are flattened without checking wrapper-family agreement
   (`:298-300`). There are no corruption regressions exercising the advertised
   count/quota/family/identity/M/novelty protections. Pass `ranking` into the
   guard, validate proposal/stage structure, and add bounded literal mutations
   proving each guard category cannot fabricate PASS.

5. **The CLI still prints the full scientific result, contrary to the clarified
   compact-output contract.** `main` serializes all of `result` (`runner.py:369-375`),
   which includes large q/support/evidence structures on success. Revised spec
   lines 89-94 require only strict JSON containing outcome, output path, and
   manifest hash. Print that compact object after the `Attempt` closes; keep the
   full result exclusively in immutable `result.json`. Add a CLI seam/assertion
   for the exact compact keys and no output on failure.

6. **Cache/profile persistence is not asserted.** Real selection callback files
   should retain profiles with calls/routes/cache hit/miss counts and elapsed
   time, while omitting only the live cache object. The positive integration only
   counts five proposal files (`tests/...:144-158`) and never inspects their
   scientific fields, strict nonstring q encoding, or profile counters. Assert at
   least training and held-out stage artifacts contain complete selected/evidence/
   support-or-q/profile data and that manifest hashes reproduce their exact bytes.

## Verified closures and resource decision

- `test_real_tiny_pool_assemble_rank_capacity_failure` now uses actual PoolResult
  maps followed by real `assemble_global_inventory` and `rank_proposals`, and
  obtains a genuine raw-capacity failure (`tests/...:173-182`). The old injected-
  ranking test remains redundant but does not invalidate this honest integration.
- `_validate_pass` now derives window/quota from the selected result rather than
  the placeholder config and adds substantive row/quota/novelty guards.
- Early interruption now produces a partial manifest/summary, FAILED attempt,
  one ledger row, and lock cleanup; this is useful but not the required post-stage
  case.
- The new 120-second independent-audit reserve is **approved**. It is prospective
  headroom, not a new charge or cap increase. The deadline correctly computes
  `min(stage remaining, global remaining) - 2 startup - 30 finalization - 120
  audit`; with stage prior 10 seconds the asserted 1438 seconds is exact
  (`runner.py:146-155`; tests lines 56-65). The reserve stays inside the frozen
  1600-second dataset and 7200-second global caps.

## Independent checks and charge

Static source/test/spec/handoff and SHA-256 inspection only. No test, generation,
production, or model command was run. Independent compute charge: **0 seconds**.
This remains an implementation-readiness verdict, not a scientific outcome.
