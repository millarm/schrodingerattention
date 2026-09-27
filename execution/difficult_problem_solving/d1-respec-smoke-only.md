# Bounded respecification: one literal smoke test, static only

2026-09-20. The complete correction handoff remained incomplete after the one
consolidated correction boundary. Do not repeat its broad A/B/C request. The
observed root cause is failure to translate named test requirements into working
fixtures/assertions while changing runner and watchdog simultaneously. There is
no evidence of a runtime budget failure: no approved recovery test has run.

Choose one smallest independently checkable implementation deliverable before
any further recovery decision: replace only
`test_actual_evaluator_counter_and_common_uniform_warm_cache` and its local smoke
fixture. Do not change production source, watchdog, other tests, ledger or science.
This is static implementation only. No imports, tests, model/checkpoint calls or
production launch. Terra remains implementer; Astra/Sol inspect the literal diff.

## Exact fixture and assertions

- Use the accepted Problem shape with a 144-byte all-zero 12×12 map, start0,
  goal1, length1, exact M1, Mnovel absent/None, one map/family identity. Inspect
  ACTIONS and use its east action index, not a guessed index.
- Deterministic callable returns batched four-action logits with the east action
  uniquely certain (other actions minus infinity); this is a stub, not a neural
  checkpoint. Wrap it with actual `CountingModel`.
- Call the accepted evaluator at K32, seed1702, splitcode1, replicate0, T1 with
  an empty cache. Assert exactly one model invocation, exactly one batch state,
  32 one-action east routes, every route valid, total32 generated actions, Q1,
  and U_valid1/32. Assert against those constants, not a recomputation equated
  to itself. The accepted evaluator should stop paths at goal.
- Re-evaluate identical problem/seed/T with the returned cache: assert zero
  additional forwards/states and byte-identical ordered routes. Repeat at T0.5
  with the same cache/uniform identity; deterministic logits preserve these
  routes and add no forwards.
- Compute actual `_uniform_digest` for this problem and seed1702 twice and
  seed1703 once: assert equal for repeats and unequal for different seeds.
  Assert the temperature changes do not change the seed/problem sampling keys.
- No monkeypatch of the accepted evaluator, its logits path, route verifier or
  counters. No full512 metadata fixture, serialized output, ledger or owner is
  needed for this one smoke.

## Acceptance and hard boundary

Return exact test-file hash and a short line-to-assertion map. No claim of test
execution or full repair. Astra inspects fixture correctness statically, and root
may ask Sol for the same narrow check. If this simple explicit task is again
returned incomplete/placeholder, stop for an implementer-capability decision;
do not issue another near-identical continuation.

If complete, it proves only that this bounded test was implemented. Remaining
tiny orchestration/binding/owner tests, source QC verification/compact selection,
and watchdog safety/accounting still require separate bounded closure and full
exact-version static PASS. The smoke must NOT be run merely because its own
function is complete. Fresh120 s tests and300 s D1 stay unspent and unchanged.
