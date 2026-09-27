# Independent Sol static review of fresh-Terra D1 repair

**Verdict: CHANGES REQUIRED — do not run smoke, suite, or production from these bytes.**

Exact artifacts reviewed:

- `execution/difficult_problem_solving/d1.py`: `4b1a7039e90313d8034c1ea51ac77772aafa6bcb5bfbac330f7368689c08ff26`
- `execution/difficult_problem_solving/d1_watchdog.py`: `7d828ba7a1a560ca9461bb299c04f49c30fffb55eaf24a8b083b82851cb7edad`
- `tests/test_difficult_problem_solving_d1.py`: `7353a855f4323391338d574d6ee2c2ec66069178bceb0e6069b4bec6d9627672`
- `execution/difficult_problem_solving/d1-fresh-terra-static-handoff.md`: `e7dcd39ee0d8801b3b8a6872922ae51a2ba08ad2823293c3294f2b1c6aa9c9b8`
- approved plan: `370650b044b51eab8c331b54718e0af85be9dfa75758bab695e23cc4312d2a31`
- recovery approval: `36431d4b7ac2686fa3282d5de419e1ce3d3a55db1a75b5e065e2acf7448378bb`
- prior static review: `b248aafd5448f02bb5e9c80e7967fcd44d2267b143de2c0e50a00c8c9916c511`

This was a static review only. I ran no tests, imports, model calls, checkpoint
loads, inference, production command, final-test access, or ledger mutation.

## Required single-batch corrections

### A. Complete the scientific and artifact bindings

1. `retained_metadata` checks that `analysis.json` has a `pair` object but then
   discards it. `produce_cells` validates only final checkpoint hash and seed.
   Cross-check the manifest-bound retained pair against current `validate_pair`
   for both models: final/initial checkpoint hashes, full checkpoint identity and
   config, input/source IDs, initial/shared digest, and accepted owner authority.
   Persist those bindings once and reference them from cells.
2. The accepted training loader is appropriate, and the complete-support digest
   is now computed. However `training_identity` will normally be null because the
   returned dataset does not expose the guessed `identity`/`input_ids` attributes,
   and validation does not require it. Bind the accepted training selected/source
   identity from the common metadata and loader provenance explicitly; require it
   and the support digest in every indexed cell/shared provenance.
3. `bound_greedy` correctly uses `_storedroutes`, but retained K32 endpoints still
   receive only a map/family comparison. Corroborate route validity/order for all
   16 retained cells through the accepted pure stored-route verification logic,
   including the analysis-bound SA 0.75/1.25 rows. Preserve the all-invalid caveat.
4. Historical forward/batch/action counts must be null/unavailable, not zero as
   currently emitted. Record why they are unavailable. Keep new endpoint counts
   measured.
5. Store the ordered panel and shared provenance once and reference a panel hash
   from cells; do not repeat 512 IDs in all 40 files. Verify all eight greedy
   files and their index hashes in `load_indexed_cells`, and require exactly 40
   cell IDs plus eight model/seed greedy IDs before marking the index COMPLETE.
6. After replacing `out['cells']` with the compact index, also replace each
   selected full cell with a cell-ID reference plus the declared selected metrics
   (pass, both Q values, U_valid/K and coverage). The current `selected` objects
   still duplicate eight complete raw bags into `d1.json`, contrary to the plan.
7. Timing labels remain conflated: `cold_cache_seconds`/`incremental_cache_seconds`
   contain whole endpoint elapsed time. Retain separate endpoint elapsed and raw
   cache-inference fields, plus available greedy/proper, loading and output-write
   timing/cardinality evidence. List missing forecast cells explicitly under the
   approved `D2_FORECAST_DEFERRED/NO_GO` result.
8. Replace the boolean `--reviewed-production` gate with an exact decision record
   created after final implementation PASS. Validate that record against source,
   tests, watchdog, plan, recovery approval, exact review, command, owner name,
   and ledger prefix/addendum before any model/checkpoint work. A boolean is not
   an exact-version production authorization. Bind that decision in the owner.

### B. Make the focused tests literal and small

1. The evaluator smoke is not reachable as written. Fixture canonical maps are
   32 bytes, while accepted features require a 144-byte 12x12 map, and `P` lacks
   `length`, `M`, and `Mnovel`, which accepted route metrics consume. Correct the
   fixture with legal 144-byte maps and complete problem metadata. Its route-count
   and RNG assertions are also tautologies. Assert known expected forward
   invocations/batch sizes and exact generated-route totals; compare the same
   uniform digest/routes across relevant model/temperature calls and prove a
   changed seed changes the digest. Keep the warm-cache fewer-forward assertion.
2. The producer fixture also fails before its advertised assertions: `result()`
   omits per-problem `map_id`/`family` required by the retained-row check; the
   class-body assignment `class Validation: problems=problems` shadows the
   enclosing local and is not a reliable fixture binding; and its all-valid route
   metadata is not realistic. Fix these direct errors. The test still uses a full
   512-problem/32-attempt object in every cell,
   contrary to the approved tiny orchestration fixture. Add an injected prevalidated
   small-panel seam for orchestration while retaining the separate exact 512-panel
   metadata test. Record and assert all 24 evaluator calls and exact seed/T/K/
   split/replicate/support/order arguments, eight cache identities, lock presence
   before every loader/evaluator, eight separate greedy records, one cell write,
   and forbidden prepared/test/training-entrypoint paths. Do not merely count files.
3. The selection fixture sets `challenge_pass = temperature` but asserts that
   softmax T1 is selected even though T1.5 is eligible and larger. Use deliberate
   metric values that separately prove each selection rule. Add the bounded real
   retained-artifact read and mutation negatives for manifest,
   seed, checkpoint, full config, temperature, and a recomputed-binding within-map
   valid-route substitution. The current test only reverses synthetic IDs. Add
   both independent Q-floor cases, maximum-pass versus Q, both 1e-12 tie levels,
   lower-temperature tie, and distinct missing and duplicate grid cases.
4. Add a real temporary-ledger `run`/CLI owner test. Separately inject a cell write
   failure and output-manifest/finalization failure; assert non-success, explicit
   terminal artifact/exit, exactly one charge, lock cleanup, partial index not
   selectable, and no COMPLETE report. This admitted gap remains mandatory before
   smoke authorization.
5. Add watchdog tests using tiny child commands: exact hash/cwd/argv rejection,
   10/30/60 concurrence rules, 120-second cumulative gate, timeout with a descendant
   process, durable records, one EOF test charge, production owner reconciliation,
   missing-owner fallback, and no double debit. These may use copied temporary
   ledgers only.

6. The write-once serializer is not compatible with real new endpoints.
   `_atomic_json` calls plain `json.dumps`, while accepted evaluator attempts carry
   route `bytes`; the first real endpoint/cell write will raise a serialization
   error. Use the accepted serializable adapter or one explicit reversible hex
   encoding before hashing/writing, and assert byte-route round-trip plus identical
   canonical hashes. Synthetic string routes currently hide this production fault.

### C. Fix reachable watchdog/accounting failures

1. Validate the exact frozen 143-line prefix hash and the single approved 300-second
   administrative addendum before any launch. Fully validate JSONL uniqueness,
   finite nonnegative charges, one carry, stage totals, and current EOF. The current
   watchdog trusts any parseable ledger with the same arithmetic.
2. Enforce the 120-second block using every row tagged to this recovery, not only
   `charge_owner == d1-watchdog`. Reserve the full prospective command envelope
   under an exclusive accounting lock, then re-read/revalidate immediately before
   append so concurrent launches cannot overspend or duplicate IDs.
3. Never charge `min(requested, elapsed)`. That undercounts timeout cleanup and
   launch/reap overhead. Enforce one overall monotonic deadline including TERM/KILL
   grace, and record the actual full elapsed charge. If a platform overrun occurs,
   charge it truthfully and stop further work.
4. Make the terminal record durable before attempting the ledger append, then
   durably record accounting success/failure. An append failure must leave an
   explicit terminal accounting-stop record and return nonzero; it must never
   permit a relaunch.
5. `_kill` reaps only the leader and does not verify that the process group is
   empty. Handle exit races, TERM the group, use bounded remaining deadline, KILL
   surviving group members, reap the leader, and verify no process-group member
   remains before recording terminal cleanup.
6. A 60-second concurrence cannot be authorized by mere existence of an arbitrary
   file. Parse a hash-bound Sol concurrence record naming exact source/test/
   watchdog hashes, command and 60-second envelope.
7. Production reconciliation currently searches for ledger key `owner`, but
   `OwnedAttempt` rows identify the output path and UUID; this path will report
   missing ownership even after a valid run. Require the unique expected output,
   terminal manifest-bound `attempt.json`, matching UUID/stage/output/charge in the
   ledger, and COMPLETE versus failure semantics. A child exit 0 with failed or
   ambiguous reconciliation must return nonzero.
8. Implement the approved single uncertain stage-D fallback keyed by watchdog UUID
   when the child terminates before any owner charge exists; if an owner row exists,
   append nothing. Re-read under the accounting lock so owner and fallback can
   never both be charged. Record the fallback as uncertain failure, never success.
9. Restrict argv by a hash-bound smoke/suite/production decision rather than
   accepting any remainder command supplied by the caller. Include exact watchdog,
   authority and decision hashes in start/result/ledger records.

## What is already sound

The approved A1000/B3500/C0/D1400 table, exact validation family counts, immutable
per-cell atomic writes, separate greedy files, common-uniform construction, 16/24
grid ordering, Q-floor/selection logic, shared-map uncertainty calculation, and
explicit D2 forecast deferral are directionally correct and should be preserved.

Return the corrected source, tests, watchdog and truthful exact-hash handoff as one
batch. Static Sol PASS is required before the 10-second smoke; test PASS and a
separate exact-version implementation review are required before the one D1 run.
No change to science, roles, approved budgets, D2 sealing, or final-test authority
is requested.
