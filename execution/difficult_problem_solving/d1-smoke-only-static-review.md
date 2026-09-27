# Independent Sol static review of the D1 evaluator-smoke test

**Test-file SHA-256:** `99049e972e0d58d55cfe122591b30d5ca5b88b6edcf58ea70b1f87267c485958`

**Narrow verdict: PASS — the named smoke-test function implements its bounded static specification.**

Reviewed against:

- `d1-respec-smoke-only.md`: `2a11788107d22ac0676c1f51b490dafb177cd51183ae89d301ce3efd8694d5a0`
- `d1-smoke-only-handoff.md`: `20c7a327e3e19e9cf84b30ad39574880309c9426097ab600af29faad8ed99d0f`
- unchanged `d1.py`: `b881a7068ab9f82b92220bc87b3d166a78d8c482fd5044e1c61bde322792d5b0`
- unchanged watchdog: `96aa33a1fc6268276d6d0879545b9d974b14fd73d2452d5b1e22e519e5815bf2`

This was a static inspection only. I ran no imports, tests, evaluator calls,
checkpoint loads, inference, production command, final-test access, or ledger
write.

The function uses the accepted `Problem` shape with a 144-byte all-open map,
routine family, start 0, goal 1, shortest length 1, exact M=1, and Mnovel=None.
It derives east from `ACTIONS`. Its deterministic callable returns a correctly
batched four-action tensor with only east finite and is wrapped by the real
`CountingModel` before calling the accepted evaluator.

For the cold K32 call, the literal assertions correctly require one deduplicated
model invocation, one batch state, 32 ordered one-byte east routes, all valid,
32 total generated actions, routine Q=1, and U_valid=1/32. These values follow
the evaluator's active-route batching and stop-at-goal behavior rather than a
self-comparison.

The two subsequent calls use the returned cache with the identical identity and
sampling inputs. The combined zero counter deltas prove that neither warm T1 nor
warm T0.5 adds a forward or batch state; both assert the same ordered byte routes.
Because `_uniform_digest` is defined only by problem and sampling identity, its
repeat equality and seed-1702/1703 inequality correctly establish stable common
sampling keys independent of temperature.

No correction is required to this one function. This PASS certifies only its
static implementation. It does not certify the rest of the test file, production
source, watchdog, accounting, owner/failure paths, or full repair, and it does not
authorize running even this smoke test. All previously recorded broader blockers
remain until separately corrected and exact-version reviewed.
