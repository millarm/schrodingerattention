# D1 minimal repair static handoff

No import, test, model/checkpoint load, inference, training, payload parsing,
production command, or ledger mutation was performed after this repair approval.
The only read-only static command was `shasum -a 256` over the listed files.

Reviewed authority: plan
`370650b044b51eab8c331b54718e0af85be9dfa75758bab695e23cc4312d2a31`,
plan review PASS, and recovery approval
`36431d4b7ac2686fa3282d5de419e1ce3d3a55db1a75b5e065e2acf7448378bb`.

Static hashes:

- `d1.py` `f0264265e6817055659f962f3f2abc770e61f2352de41f18905de0eaacfc6842`
- `d1_watchdog.py` `f618206aff58a22c16f589063c63e7133e5ad38341cddd6c705de0ba06e25f3c`
- `test_difficult_problem_solving_d1.py` `6b5dc7f4675e444e386be501e75d150618ef713f34d86fd5419b1993936a465f`

Static changes: the production path retains the D1 metadata/identity checks and
now writes immutable `cells/<seed>-<mode>-<temperature>.json` endpoint files
once, followed by a compact `cell-index.json`; final selections reference cell
IDs.  Available timing is retained as D1 evidence and an incomplete D2 bound is
explicitly deferred/no-go.  The watchdog is external to D1 imports, records
unique ID/argv/cwd/hashes/UTC/monotonic duration, captures stdout/stderr, and
terminates and reaps the exact child process group on timeout.

Assertion map for the planned next test phase: existing test groups cover
grid/selection, retained binding negatives, owned failures, forecast, and
counter/interval arithmetic; the planned smoke must exercise accepted evaluator
and `CountingModel`; the planned suite must exercise the real orchestration with
injected dependencies, 16 reuse/24 new/40 cells, endpoint files/index, lock,
forbidden paths, and owner failure paths.  This is an implementation handoff,
not a claim that those tests were executed or passed.

Required watchdog commands after independent static acceptance are bounded to
10 s smoke then 30 s suite.  The caller must retain and poll the launch session
to explicit exit and append any measured charge only through runtime EOF
accounting.  No D1 production is authorized by this handoff.
