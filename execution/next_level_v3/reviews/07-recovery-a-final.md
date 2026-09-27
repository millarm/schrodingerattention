# Recovery A definitive review

**Verdict: BLOCKED pending bounded respecification.** The source implementation
of the two residual behaviors appears correct, but one explicitly required
acceptance assertion is still absent after the second correction cycle. Recovery
B and production remain unauthorized.

## Exact frozen version

- Module `schrodinger/productive_diversity_v3_data.py`:
  `4aa4779877781f2b0211397c3938185ad6ec5154040fecdef3d9f7eac7e84f08`
- Tests `tests/test_productive_diversity_v3_data.py`:
  `4fd16067e12e9b249ea210973ed95a75ae0dfdcb8af8aaf7a49f0adbc142b687`
- Handoff `execution/next_level_v3/handoffs/02b-revision2.md`:
  `41d897e2e66c4cd6ed54630c0d271775d4d4dfdd4e293769358d3a8c20e06e9a`
- Prior review `execution/next_level_v3/reviews/06-recovery-a-acceptance.md`:
  `5dc335aff3aca9d28862b0ef75d22ad23f3236c28bc8a50bfc1386517e8af220`

## Remaining blocker

The source now wraps each executed family result and appends an explicit
`{"family": future, "result": {"outcome": "NOT_EVALUATED"}}` record for an
unvisited family after an earlier family fails
(`productive_diversity_v3_data.py:513-524`). That is the requested behavior.

But `test_orchestrator_short_circuits_training_and_first_family` does not assert
that record. It checks only the overall failure outcome and that the held-out
call list is either empty or `["IIIIIIII"]`
(`tests/test_productive_diversity_v3_data.py:256-268`). It never examines
`out["evidence"][0]["stages"]["validation_routine"]`, the explicit family label,
or the L-family `NOT_EVALUATED` outcome. Thus the handoff's line 9 assertion
claim is not supported by the frozen test. The definitive prompt specifically
required the current-family-not-visited **record and actual assertion**, not
prose or source inspection alone.

Because two correction cycles have now been used, this should not trigger an
unbounded micro-correction loop. The concrete bounded respecification is one
regression assertion against the returned failed-stage record: executed I has
the scientific failure, unexecuted L is explicitly family-labelled
`NOT_EVALUATED`, no L selector call occurred, and later stages remain
`NOT_EVALUATED`. No scientific criterion or production behavior needs changing.

## Verified closure

- Literal metadata cases now cover start `-1`, start `144`, wall-cell start `0`,
  M `15`, and M `257`, in addition to n/family/identity/canonical/length defects
  (`tests/...:278-286`). These drive the actual validator checks.
- `test_unknown_training_outcome_aborts_before_heldout` supplies an unknown
  training outcome, expects `SelectionTechnicalError`, and asserts no held-out
  call (`tests/...:271-275`).
- The source's current-stage family wrapper/`NOT_EVALUATED` mechanism itself is
  present and does not change stage ordering or scientific advancement.

## Independent checks and charge

Static source/test/handoff inspection and SHA-256 verification only. No test,
generation, production, route-search, or model command was run. Independent
compute charge: **0 seconds**. This is an implementation-evidence blocker, not a
dataset-feasibility or scientific result.
