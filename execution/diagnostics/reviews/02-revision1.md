# Checkpoint diagnostic revision 1 review

## Verdict: CHANGES REQUIRED

Revision 1 closes most of the first review: direct and propagated traces remain correctly separated; downstream raw values and distribution tails are present; NaN, probability, row-sum, and TV rejection is strict; retained checkpoint/evaluation identity and content validation is substantive; trace identities are asserted on actual batches; and list-to-array conversion and parameter caching are improved. Three bounded execution/readout corrections remain before the one full run.

## Exact revision reviewed

- Correction specification: `execution/diagnostics/specs/01-review-corrections.md`, SHA-256 `a9a50cd426048d0ee5cdd31a12767a179f15c6a8022a08425cfe20df0e4b3453`
- Handoff: `execution/diagnostics/handoffs/02-revision1.md`, SHA-256 `6f6b07d967e0a5ee0f5b1d5ac9d5ff77ad45480e4194a655c3441b962ac9742e`
- Implementation: `schrodinger/checkpoint_diagnostic.py`, SHA-256 `cc79222d106248dedf27106141f3656024dfceb87e961a70572b26a681fc73fd`
- Tests: `tests/test_checkpoint_diagnostic.py`, SHA-256 `eb3636f9a3f2b9c7f53bd15bd2885b8e049bc4ff3b4879a3127a83d206b9048e`
- Plan: `checkpoint_diagnostic_plan.md`, SHA-256 `b160517e6a6c8d707fe50d392b3953dac447b99d74eeda2893a53c15dfd66b16`
- Prior review: `execution/diagnostics/reviews/01-implementation.md`, SHA-256 `9961ce9c450eb613df10256d1d638f38f5fe16f0fba422744a7fda087f229b1b`
- Handoff-declared ledger identity: `daa27192b758d35c9535c056a056e3c538dfd46f5549f39ed2c95f5ea79618b3`

## Remaining required corrections

1. **Enforce the ceiling during a single expensive stage.** `Attempt.guard()` is called between aggregation, compressed writes, JSON/CSV serialization, and plotting, but none of those operations can be interrupted if it alone crosses the remaining deadline. The new regression merely ages the timer and invokes a guard after a bounded list allocation; it does not test interruption of post-processing. Implement the correction specification's hard elapsed deadline/watchdog (or an actually bounded equivalent) around every potentially long stage, retaining the 30-second reserve and a failed/partial record. Test a deliberately blocked or slow stage that is interrupted before the ceiling.

2. **Make attempt provenance and accounting exact across startup and races.** `main()` records `[sys.executable, *sys.argv]`, which is not the original invocation and can omit the actual `-m` launcher semantics; use the original process argv where available. Timing begins only after Python imports and no conservative startup allowance is charged. The separate `exists()` checks also race the atomic acquisition: a competing output/lock created between preflight and `Attempt.__enter__` raises without a rejection or ledger record. Rejected attempts are always charged zero despite being attempts under the diagnostic ceiling. Record exact original argv, conservatively include unobservable startup, charge real rejection elapsed time, and wrap atomic-acquisition failures so every attempted command is recorded without modifying another process's output or lock.

3. **Emit the specified decision and manifest identities.** `_frozen_flags()` emits only the global `uniformly_local_small` boolean; it does not emit the promised local-small result for every direct cell, so larger cells cannot be identified from flags without reapplying the threshold. Add an explicit `locally_small` field to each cell or an equivalently complete keyed flag list. The successful-run input manifest includes the implementation but omits the diagnostic test, correction specification, prior review, and handoff identities required by the correction record. Include these exact identities so the full result identifies the implementation gate it passed.

## Independent checks

- Read the complete revision source, test file, correction specification, plan, and handoff; traced all six original finding groups through the actual run path.
- Verified that `_validate_inputs` delegates to `validate_batch`, which enforces per-operation label balance in addition to the explicit operation counts.
- Ran `/usr/bin/time -p .venv/bin/python -m pytest -q tests/test_checkpoint_diagnostic.py`: **14 passed in 0.75 s**, explicit exit; whole-command elapsed **1.04 s**.
- Conservatively charge **1.3 s** for this independent test and hash check, separate from the original experiment ledger. The diagnostic ledger should therefore advance from the handoff's 16.7 s to **18.0 s** before further work.

## Not performed

- No full checkpoint diagnostic, training, sweep, or artifact regeneration was run.
- The handoff's repository-wide 62-test result was not independently rerun; the targeted suite is sufficient to establish the residual static failures above.

