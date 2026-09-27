# User-authorized Astra status closure

2026-09-16: user explicitly approved Astra implementation with Sol independent
review. Terra inactive. Prior03b/Sol16 blockers preserved. Fixed scientific plan,
accepted data module, quotas, seeds and thresholds unchanged. Operational debit
starts540.193791294s; existing7200total/1600stage/180development/120audit/30finalization
limits unchanged. Single frozen production run only after exact-version PASS.

Replace external first-ranked active fallback with helper-derived status from
ordered retained proposals and observed callbacks. Finalization is a pure derived
copy, not mutation of observations. On interruption, completed scientific failures
remain resolved and their missing future callbacks mean NOT_EVALUATED. The first
unresolved attempted-or-next proposal has one first-missing callback UNKNOWN and
later missing callbacks NOT_EVALUATED. Later untouched proposals are all
NOT_EVALUATED. An actual failed write remains FAILED with later work NOT_EVALUATED.
A fully complete successful proposal terminates selection, so result-write failure
cannot invent an interrupted later proposal. Normal returns preserve observations
and classify missing/unattempted callbacks NOT_EVALUATED, never COMPLETE.

Tests before code correction: complete exact family/future assertions in the two
existing literal03b tests. Add real three-proposal fixture regressions: window14
scientific training failure, then window12 interrupted before its training callback
and after persisting that callback; window16 remains untouched. Use genuine oracle
selection and only callback wrappers to inject interruption, not fabricated results.
Assert entire per-proposal stage maps, prior family failure evidence, artifact hashes,
FAILED attempt, one ledger entry and lock cleanup. Preserve all existing regressions
and exact input/output provenance assertions. Run focused red then corrected tests,
charge exact elapsed walls once. Sol reviews source/test hashes before production.

After acceptance: one unique immutable production attempt; retain full tool result
and poll its session to explicit exit. Independent bounded audit follows spec04;
stop with reviewed dataset outcome including prescribed scientific/resource stop.
No rescuing a failed dataset by new pools, seeds, proposals or relaxed thresholds.
