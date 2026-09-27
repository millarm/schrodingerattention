# Block 2 revision 2 — residual correctness and acceptance evidence

Objective: resolve Sol's revision1 blockers without changing frozen scientific
settings. Same allowed files as revision1, uniquely versioned new evidence,
full current handoff. Read latest appended review before starting edits.

1. Evaluator must compute/store invariant maxima for each NORMAL condition and
   aggregate across normal validation/final evaluations; preserve these before
   dt0 intervention. Intervention diagnostics get separate fields. Final normal
   invariants cannot read last model diagnostics after intervention. Test with
   injected known differing normal/dt0 diagnostics to prove no overwrite.
2. Check all parameters immediately after optimizer, and evaluation logits and
   loss for finiteness. Abort with persistent failure and charged ledger. Test
   actual nonfinite evaluation and optimizer-produced bad parameter cases,
   verifying failures, ledger status, and preservation of available progress.
3. Shared INITIAL tensor digest must be computed once before first update and
   persisted identically in every checkpoint/final; any trained-state hash is
   separately labelled. Test identity invariant at step0 and trained checkpoint.
   Pair evaluation must enforce same seed/config/code/initial identity as well
   as evaluation arrays, and opposite expected modes; test mismatch rejection.
4. Before each training step/evaluation apply a conservative60-second upcoming
   operation reserve in addition to elapsed command+prior ledger. This leaves
   the contract's600-second hard-cap safety margin intact; it changes no
   scientific endpoint. Tests verify guard raises before operation would exceed
   available budget. Fixed60s reserve is conservative on this measured workload.
   Historical ledger cumulative fields are nonmonotonic after adding the base
   retroactively. Preserve history and provide a reconciled chronological ledger
   or clearly audited charge-total view; cap calculations use actual sum of
   charged entries. Include Sol revision1 review3.1s.
5. Add acceptance tests deliberately forcing blacklist rejection; all3 seed
   paired streams and reversed heldout-pair exclusion; two-mode/evaluate CLI
   path (test small settings okay) and correct/count recomputation. Existing
  33 tests do not cover these mandatory correctness requirements sufficiently.
6. Full clean current handoff SHA256 manifest covers code/config/tests/runtime/
   full evaluation artifact and manifest, fresh smoke/profile/102-step pair
   evidence, exact commands/exit codes. Historical hashes stay in labelled
   superseded section only; map all original and residual findings to evidence.

Run targeted tests plus full suite and fresh end-to-end evidence after source
finalized; <=600 additional compute seconds, same global cap. Before measured
runs, conservatively bring total prep charge to at least180s (or actual if
larger), explicitly labelling historical overhead allowance versus measured
time. Do not claim unmeasured historical time as exact actual elapsed. Freeze
for Sol review once all six residual groups have actual evidence.
