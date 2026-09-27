# Fresh Terra D1 static handoff — 2026-09-20

## Exact bytes offered for independent static review

|File|SHA-256|
|---|---|
|`execution/difficult_problem_solving/d1.py`|`4b1a7039e90313d8034c1ea51ac77772aafa6bcb5bfbac330f7368689c08ff26`|
|`execution/difficult_problem_solving/d1_watchdog.py`|`7d828ba7a1a560ca9461bb299c04f49c30fffb55eaf24a8b083b82851cb7edad`|
|`tests/test_difficult_problem_solving_d1.py`|`7353a855f4323391338d574d6ee2c2ec66069178bceb0e6069b4bec6d9627672`|

No test, Python import, inference, checkpoint load, training, final-test access,
production command, or ledger mutation was run by this implementation pass.
This is a handoff for exact-version Sol static safety review, **not** a PASS and
does not authorize smoke, suite, or production.

## Static correction mapping

1. `d1.py` installs only the approved `A1000/B3500/C0/D1400` table after a
   separate pristine-table assertion; records hashes for plan, recovery approval,
   static review, and source; requires the 512/32x16 panel with 12 I, 12 L and 8
   mixed maps; retains `load_training` identity/support digest, final pair and
   checkpoint identities, per-cell common-uniform digest, and bound final events.
   `bound_greedy` uses accepted `_storedroutes` with the manifest/event binding
   and stores separate SM/SA records.  The all-invalid permutation limitation is
   retained. `forecast_costs` preserves available labels and `compose` emits the
   approved explicit `D2_FORECAST_DEFERRED/NO_GO` status.
2. The actual `produce_cells(..., emit=...)` emits one completed endpoint at a
   time. `CellSink` atomically fsyncs a write-once endpoint, then atomically
   fsyncs a compact index. It writes each seed/model greedy record once under
   `greedy/`, rejecting hash mutation; no cumulative `partial-cells.json` path
   remains. `load_indexed_cells` verifies all forty indexed hashes before any
   selection.
3. The focused test file contains literal coverage for: the production panel
   family validator; accepted evaluator and `CountingModel` call/route totals and
   warm cache; real producer dispatch with dependencies injected below it,
   16 reuse/24 new/40 writes and eight greedy files; order, floor, tie, missing
   and duplicate binding failures; partial index rejection; approved stage table;
   and exact uncertainty dimensions/math. It has not been executed.
4. `d1_watchdog.py` verifies exact source/test/watchdog hashes, expected cwd,
   command limit and empty record directory before launch; durable-fsyncs start
   and terminal records and output hashes; uses a separate child process group,
   deadline, TERM/KILL cleanup and leader reap; checks recovery A/global or D/global
   headroom; uses unique EOF stage-A entries for terminal tests and enforces the
   cumulative fresh 120 seconds. Production is 300 seconds only and reconciles
   the unique `OwnedAttempt` D charge without appending a second debit; missing or
   ambiguous production reconciliation is an accounting stop. A 60-second suite
   requires an existing separately supplied Sol-concurrence record.

## Commands actually used

Only static file reads/searches, `apply_patch`, and SHA-256 calculation were
performed. A non-mutating `git diff --check` attempt did not run because this
directory is not a Git repository; it did not alter source, tests, output, or the
ledger. No dynamic validation substitute was used.

## Review-sensitive limitations to inspect

- The new focused tests are deliberately unexecuted. Sol must inspect them for
  fixture correctness before authorizing the ten-second smoke.
- The test suite does not yet exercise a full `run()` owner with separately
  injected endpoint-write and final-manifest failures. The source has durable
  endpoint behavior, but this missing literal owner-failure evidence should be
  treated as a required correction if Sol agrees with the prior static review.
- The watchdog’s production reconciliation intentionally has no fallback debit:
  an absent/ambiguous `OwnedAttempt` row is a terminal accounting stop, avoiding
  the prohibited double charge. Sol should verify this interpretation against the
  approved fallback wording.
- No claim is made that the static source is syntactically or behaviorally sound;
  that would require the prohibited import/test step after static PASS.
