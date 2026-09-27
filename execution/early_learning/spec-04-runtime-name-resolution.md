# Bounded runtime name-resolution correction

2026-09-27. The first accepted runtime suite found a new, concrete defect:
`study.py:251` refers to `row` inside a generator whose bound variables are
`a, b`. The analytic transition test failed before production scoring; the
other 15 tests passed. This is a runtime-discovered name-resolution error,
not an unresolved finding from the two completed static correction rounds.

Luna may change only this expression from `row["weight"]` to `a["weight"]`
in the aggregate A/B component-change sum, and update the handoff. The function
already verifies identical paired weights. Preserve the existing analytic test,
all failed-attempt evidence and ledgers. No scientific, fixture, driver, model,
data or resource change is authorized. Use AST/static inspection only, then
freeze hashes for Sol's exact repair review, including runtime-evidence-001.md.

After Sol static PASS and a distinct Astra acceptance, one new 60-second
targeted-suite attempt may be authorized. Do not repeat the successful smoke.
The new decision must bind the changed source hashes and fresh ledger EOF.
Stage A has used 9.956818457925693 of 120 seconds; all rerun cost stays within
the remaining allocation and the unchanged 1,800-second global cap. Any failure
must be durably charged and cleaned up, with no automatic retry.

Acceptance requires all 16 tests passing, verified cleanup and accounting, and
Sol's exact implementation/evidence PASS. Production remains unauthorized until
the separate Astra production acceptance. No training, final test or 200k work.
