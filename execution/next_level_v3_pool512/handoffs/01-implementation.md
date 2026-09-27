# Pool512 implementation handoff

## Scope and result

Added only `schrodinger/productive_diversity_v3_pool512.py` and
`tests/test_productive_diversity_v3_pool512.py`; appended development records to
the new pool512 ledger.  No production invocation, full pool-512 generation, or
training was performed.

The local `execute_pipeline` is the accepted runner orchestration copied at the
configuration boundary.  It imports the accepted `Attempt`, `ProposalStatuses`,
save, PASS validation, and data algorithms; it does not mutate base globals,
delegate to base `execute_pipeline`, or rewrite a manifest after the fact.  Its
primary `manifest.json` records `pool.limit=512`, `n=12`, and
`max_trials=200000`.

## Frozen hashes

- Module: `1a7fcf6040c76097051a7be7e4ef2da52a3e3883c7e53b2089918ee090633463`
- Focused test: `a9286b5331219f8fb90ba67f14ba6ae9552a9502cca3b2005da4488f6cc6ac4e`
- New ledger after recorded development: `204114a46cfdf8eb8e0ebe37109586236a6818d491184e658a660b25bfa004af`

`_source_hashes()` is the exact base immutable source set plus the new module,
test, amendment, all pool512 specs/reviews, old v3 ledger, and original
feasibility manifest.  It deliberately excludes the mutable pool512 ledger.

## Literal acceptance assertions

1. A stubbed default generator call is exactly
   `pool_family(family, n=12, limit=512, max_trials=200000)`.  Separate real
   limit-2 and limit-4 calls for all three families assert exact 2/4 observed
   counts, old-map subset inclusion, and equality of the shared draw-prefix.
2. The genuine existing eight-map fixture reaches `FIRST_FULL_DATASET_PASS` via
   the new pipeline.  Its primary manifest has literal limit 512 and the exact
   expanded provenance path set and hashes; saved fixture pool artifacts contain
   I8=3, L8=3, mixed=2 (total 8), explicitly distinct from the configured 512.
3. A temporary valid new ledger yields stage/global priors
   `301.747054625`/`745.131573627` and actual `ext.deadline_seconds()` of
   `1146.252945375`; missing and duplicate carries raise.  Rejection output and
   charging use temporary new paths, not the old ledger.
4. A real scientific held-out supply failure preserves the accepted scientific
   status, and an injected post-training `Deadline` preserves the accepted
   incomplete-status summary and `DEADLINE_FAILED` outcome.

The fixture test captures and rechecks bytes/hashes for old data, runner, plan,
protocol, old ledger, and original feasibility manifest; all remain unchanged.

## Development evidence

All focused commands were:

` .venv/bin/python -m pytest -q tests/test_productive_diversity_v3_pool512.py`

- Existing scaffold record: `1.00426525s`, ledger UUID
  `0a225405-ebaa-4779-8954-9a418f6e9baf` (2 passed).
- Local orchestration record: `1.1467155s`, ledger UUID
  `467b07fd-646e-4d42-a5e4-8a591a960bd4` (4 passed).
- Acceptance closure record: `1.444657667s`, ledger UUID
  `f2a2b166-1d35-4ac7-a45f-1d95d98c5e1a` (4 passed in 1.26s).

Total new development wall: `3.595638417s`.  The final focused command passed;
no subsequent source, test, or production action occurred.

## Timestamp clarification

The `recorded_at_utc` values `2026-09-16T12:00:00+00:00` and
`2026-09-16T13:10:00+00:00` on the two implementation records are invalid future
timestamps.  They were manually entered during record creation, not obtained
from a clock tool.  The retained full tool results establish execution and append
order and their exact walls (`1.1467155s`, then `1.444657667s`), but do not retain
an exact UTC timestamp.  The requested clock tool was unavailable in this
environment.  Ledger row `5cce6ec4-8a96-47bc-8caf-6d2e32f7a5b9` is a zero-charge
clarification at the current UTC supplied by the records-audit instruction;
existing charged rows remain unchanged.
