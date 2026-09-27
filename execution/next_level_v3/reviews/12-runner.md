# Block 3 runner review

**Verdict: CHANGES REQUIRED.** The runner has a useful safety skeleton and a
genuine injected-inventory success integration, but it does not yet satisfy the
frozen production evidence, failure-finalization, validation, or integration
requirements. Production must not launch.

## Exact frozen version

- Runner `schrodinger/productive_diversity_v3_runner.py`:
  `3d0278cf01f6de41e34e6447104c2fc5b63fae8deb2786b778ad4ab6b0a37a61`
- Tests `tests/test_productive_diversity_v3_runner.py`:
  `b7bf635f2e7d1999da72e54bd9f4854d4295afd3f0bfaa87f43ddae474d45db8`
- Spec `execution/next_level_v3/specs/03-runner.md`:
  `a6d08e81161ea963f3611e73fb67fa713311f7269772b25c7acbba870a50c1ef`
- Handoff `execution/next_level_v3/handoffs/03-runner.md`:
  `ac06a21c4d4ac233fdcd892766fe6c1e9519b8d85b3770cf8e843d7ffc0c40b1`

Accepted Block 2 data logic was not reopened.

## Material findings

1. **Technical/deadline exits cannot persist the mandated partial scientific
   record.** `execute_pipeline` is a straight-line function with no exception
   finalizer (`productive_diversity_v3_runner.py:281-312`). If pool, inventory,
   ranking, callback writing, selection, validation, or deadline fails, it writes
   neither a partial `summary.json` nor `manifest.json`; `Attempt.__exit__` writes
   only `attempt.json` (`:221-238`). Completed pool/stage files may remain on disk,
   but no truthful reached/failed/`NOT_EVALUATED` summary discovers and binds them,
   and the original error is absent from a dataset summary. This directly violates
   spec lines 23-25 and 78-82. The deadline test catches a synthetic signal inside
   the context (`tests/test_productive_diversity_v3_runner.py:112-121`), so the
   attempt actually closes normally and proves neither a FAILED attempt nor
   partial-artifact finalization.

2. **Manifest provenance/configuration is substantially incomplete.** The
   manifest records only n, one caller config, split counts, argv/executable, four
   source files, stage hashes, and result hash (`runner.py:241-246`, `:304-311`).
   It omits frozen families/shape counts, all seeds, pool bounds/trials, shortlist
   rules/cap, all ranking windows and quota candidates, support/novelty semantics,
   stage/global budget constants and prior debits, Python/numpy/runtime/thread
   facts, imported `route_feasibility` helper, runner/data tests, the plan and the
   accepted contract/spec/review chain, fixture inputs for the injected test, and
   hashes for pool, inventory, and ranking artifacts. This fails spec lines 37-42
   and 68-76. The tests merely check that a manifest exists and that attempt has a
   nonempty manifest hash (`tests/...:155-158`); they do not assert exact config,
   sources, runtime, inputs, outputs, or hash reproduction.

3. **The effective configuration can misreport and misvalidate the selected
   proposal.** Production supplies a placeholder default quota `(6,5,5)`
   (`runner.py:286`), while `run_ranked_proposals` correctly replaces it with the
   selected proposal's actual `window` and `quota`. Afterward `_validate_pass`
   receives the placeholder config (`:301-302`), and the manifest saves that same
   placeholder (`:304-305`) rather than the selected proposal values. A selected
   `(5,6,5)` or `(5,5,6)` proposal would therefore be reported as `(6,5,5)`.
   Validation checks only the *set* of lengths and distinct-map totals
   (`:265-278`); it never checks exact per-map/per-length quota counts, training
   32-map-per-family counts, row family linkage, n/map/canonical identity, M, or
   routine/challenge novelty predicates. Consequently the runner-side guard does
   not meet the spec's “defects cannot fabricate PASS” requirement (lines 44-51).

4. **The raw-capacity integration test injects the result it claims to test.**
   `test_raw_capacity_failure_persists_truthful_result` passes
   `rank_fn=lambda ...: {"retained": ()}` and an assembler that returns the
   eight-record success fixture even though the injected pools are empty
   (`tests/...:161-168`). It does not execute real pool→assemble→rank and cannot
   validate a genuine raw-capacity failure or input coherence. The agreed test
   boundary requires a real tiny pool→assemble→rank capacity failure. The positive
   test's injected inventory/ranking/count seam is allowed and does run the real
   eight-map Block 2 selection and callback writes (`:124-158`), but it does not
   substitute for the separate real capacity-failure composition.

5. **Required failure/write safety evidence is missing.** There is no integration
   that interrupts `execute_pipeline` after at least one artifact/stage and asserts
   FAILED attempt, original error, partial summary/manifest, completed output
   hashes, future `NOT_EVALUATED`, lock/timer cleanup, and exactly one ledger row.
   There is no pool/stage/result/manifest/summary exclusive-write fault test, no
   rejection-artifact write-failure test, and no proof that such mandatory write
   failures charge once and propagate. The existing log-failure test covers only
   `attempt.json` (`tests/...:101-109`). Callback cache/profile data is not
   inspected, so cache reuse/profile completeness is also unproved.

6. **CLI completion does not print the full execution result.** `main` discards
   the return value of `execute_pipeline` (`runner.py:315-320`). Although success
   stores `result.json`, the frozen contract explicitly requires the full result
   to be printed and stored so the externally observed command/session can be
   reconciled (spec lines 26-27). Add strict JSON stdout on normal completion;
   failures must remain nonzero and retain their on-disk partial evidence.

## What is correctly implemented

- `_prior` distinguishes global carry from new stage debit, rejects duplicate
  IDs and invalid debits, and requires exactly one frozen carry for the production
  ledger (`runner.py:71-105`). Deadline calculation uses the minimum remaining
  stage/global budget minus startup and finalization reserves, with tightening-
  only override (`:145-154`).
- O_EXCL output/lock ownership, local rejection paths, timer restoration, owned-
  lock cleanup, exactly-once ledger append, and mandatory attempt-log propagation
  are represented and have focused unit coverage (`:108-238`; tests lines 31-121).
- Successful straight-line execution writes pools, inventory, ranking, per-stage
  callback artifacts, result, manifest, and compact summary exclusively. The
  injected eight-map integration uses real `run_ranked_proposals` rather than a
  mocked whole PASS.

## Independent checks and charge

Static source/test/spec/handoff and SHA-256 inspection only. No test, generation,
production, or model command was run. Independent compute charge: **0 seconds**.
This is an implementation readiness verdict, not a dataset-feasibility outcome.
