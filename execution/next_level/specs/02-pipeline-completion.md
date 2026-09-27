# Stage0 completion substep B — executable gate and isolated safety

Activate only after Astra accepts substep A's completion for integration.
The frozen Stage0 contract remains authoritative. No full6x6 run until complete
code/test review by Sol. No models, training or later harness.

Replace the inventory-only CLI with the full deterministic feasibility pipeline:

1. Persist full map inventory/eligibility; select exact train/validation/ID/IL
   map counts without retry. Persist selection permutations and IDs.
2. Select training pairs from continuously consumed per-family RNG streams,
   derive two median boundaries and four joint proportions; persist them.
3. Select evaluation problems using Hamilton quotas, true deterministic residual
   flow and continuously consumed per-family/cell permutation ranks. Persist
   quotas/capacities/flow and selected pair records. Stop on deficient supply or
   flow with exact evidence, later metrics NOT_EVALUATED.
4. Persist deduplicated supervised states with four-action q vectors. Enumerate
   every selected training-route suffix into the canonical exclusion support;
   write sorted length-prefixed support bytes and exact hash. Persist test and
   validation per-problem route/signature/M/M_novel records, using only support
   membership, never changing selections after novelty is known.
5. Compute the strict >=256 qualifying IL problems and >=16 qualifying IL maps
   gate. A scientific failure is a successfully completed feasibility test,
   not a runtime crash: summary outcome FEASIBILITY_FAILED_NOVELTY or supply/bin
   failure, attempt execution_status COMPLETE. No training on failure.
6. Isolated robust attempt wrapper: fresh output/O_EXCL lock, separate flags for
   owned lock/output, interrupting timer to600s stage remaining minus30s reserve
   and7200s global cap, finally cleanup even if record writing fails. Charge
   startup2s plus elapsed for success/failure/rejection; record actual orig_argv,
   executable/PID/start/end/source+contract+plan hashes. Log rejected attempts
   outside unowned output, never overwrite it. Unique IDs and locked append-only
   JSONL ledger; no manual insertion at earlier context lines. No old ledger use.
7. Save command/runtime/source manifest and hash output artifacts. Add fixture
   tests for scientific failure semantics, novelty threshold arithmetic,
   deterministic pipeline selection, required artifact/schema membership,
   deadline interruption, output-mkdir and lock races, failure-log cleanup and
   cumulative accounting. Pure-fixture integration may inject small inventories
   but CLI exposes no option to change scientific thresholds/counts.

Budget <=30s additional tests; add exact/conservative command charges. Full
Stage0handoff must map every original contract output and test to evidence,
with code/test hashes and known limitations. Do not call an inventory-only or
unlocked CLI complete. Freeze at handoff for Sol; no fullinventory run yet.
