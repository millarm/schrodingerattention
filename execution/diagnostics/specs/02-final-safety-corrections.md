# Bounded revision 2 — residual safety and traceability only

Sol revision1 closed the main metric, numerical, data-identity and trace findings.
Do not refactor them or add scientific scope. The remaining cause is incomplete
implementation of explicit acceptance criteria: between-stage checks were
mistaken for an interrupting deadline, and reconstructed provenance/aggregate
flags were mistaken for exact requested records. This specification makes the
remaining behavior concrete. No checkpoint-analysis run is authorized yet.

Terra must finish these three groups and hand off all evidence together:

1. **Interrupting deadline.** On this supported macOS main-thread CPU CLI,
   install a real elapsed timer (e.g. SIGALRM/setitimer) at the remaining
   cumulative budget minus 30s reserve. Its handler raises a dedicated timeout
   exception, letting Attempt persist failed/partial status and release its
   owned lock in finally. Disarm and restore the previous signal handler in
   finally on success/failure. Keep cooperative batch/stage guards as well.
   Test an actual post-processing function that deliberately consumes time
   past a tiny configured deadline and prove interruption and failed record;
   a guard-only test is not equivalent. No broad unbounded performance test.
2. **Exact attempt identity and complete failure accounting.** Use
   `sys.orig_argv` for the actual original Python invocation, retain
   sys.executable separately. Charge a declared conservative 2s interpreter
   startup allowance plus measured elapsed command time to every CLI attempt,
   including rejected preflight/race cases; include allowance in cap checks.
   Catch actual O_EXCL/output-mkdir race failures, not only exists prechecks.
   Never remove another owner's lock or overwrite any output. Record rejected
   attempts in unique O_EXCL-created failure records outside requested output;
   append ledger entries under an independent advisory file lock so a denied
   contender cannot interleave JSON with the active owner. Tests verify the
   race path, nonzero charge, exact argv, and lock/output preservation.
3. **Small traceability completion.** Add each direct cell's local_small flag
   (`mean < .01 and p95 < .05`). Include diagnostic tests, both correction
   specs, frozen plan, original plan review, implementation reviews and handoff
   files in input manifest; no circular self-hash requirement. Retain current
   summaries/raw schema otherwise. Verify manifest membership and cell flags
   with explicit tests rather than assertions in handoff prose.

Record actual test commands/exits, exact final code/test hashes, diagnostic
ledger total, and all three regression mappings. Up to 30 additional seconds
of bounded tests authorized. No full analysis, no original file edits. Stop
editing at complete handoff for Sol review. If still unresolved after this
second revision, Astra must identify the residual cause and issue a new bounded
specification or report a genuine blocker; no required check may be waived.
