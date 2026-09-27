# Stage0 correction C2 — attempt safety and final integration

Activate only after C1 scientific pipeline fixtures pass. No model/later-stage
work and no full6x6 inventory. Preserve the frozen scientific pipeline.

1. Record real start time on entry, end time on finalization, unique UUID entry
   ID, exact sys.orig_argv and executable/PID, stage name, measured elapsed,
   conservative startup2s, prior/cumulative stage/global charges and status.
   Every successful/failed/rejected compute attempt gets exactly one ledger
   entry. Advisory-lock read/check+append prevents duplicate IDs/interleaving.
2. Stage0 timer uses remaining600s after priorStage0 charges, currentelapsed,
   startup and30s finalization reserve; also check7200s total. SIGALRM/setitimer
   genuinely interrupts; restore handler and any prior timer in finally.
   Model-free fixture sleep of20ms must be interrupted by a shorter deadline.
3. Track owned lock and output separately. On output-mkdir race never write
   inside unowned output; unique rejected record outside it. Every entry error
   (including exhausted deadline after mkdir) is charged and persisted; record
   logging failure must not skip lock/FD/timer cleanup. No stale-lock clearing.
4. Attempt execution_status COMPLETE includes scientific feasibility failure;
   FAILED means exception/timeout, not a failed research gate. An attempt-record
   write failure must not leave ledger success. Preserve partial evidence and
   unavailable fields as NOT_EVALUATED. No artifact may be overwritten.
5. Tests for actual timeout and restoration, preflight rejects, atomic lock
   race, output-mkdir sentinel-preservation, entry deadline failure, required
   log write failure, unique/chronological/nonzero charged ledger records,
   cumulative exhausted budget, and fixture CLI full-output serialization.

Capture a full fixture CLI subprocess result and explicit exit status; this is
not a real6x6 run. Show tests inspect outcomes rather than only execute helpers.
<=20s additional tests. Final handoff maps all original contract criteria to
specific test/artifact code, hashes, commands/exits and ledger charges. Freeze
for Sol review. Do not call an incomplete CLI ready or launch real inventory.
