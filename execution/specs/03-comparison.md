# Block 3 — frozen paired comparison

Prerequisite: Astra accepts harness after Sol PASS, and records profile-based
update count N before measured results. No implementation edits permitted in
this run block; any required code change returns through a bounded spec and
Sol review. Terra executes existing CLI with frozen config and required order.

Run seeds11,22,33 paired; baseline first for11/33, SA first for22. Use contract
N common updates, batch64, saved paired initialization/data. Verify baseline
and SA streamed-batch digest equality and effective config/hash before accepting
each pair. Save all step curves, validations, checkpoints, final per-condition
evaluation with count denominators and dt=0 intervention; evaluate latest
checkpoints under common pair training time T. If sample-efficiency gate could
qualify, evaluate SA first-target checkpoints with dt=0 to satisfy contract.
No hyperparameter/seed/split selection, no test-driven stopping. Keep final
test evaluation until each training run completes; never feed test outcomes
back into training. Record code hashes with every run.

Allowed writes: `execution/results/`, `execution/logs/03-*`, compute ledger,
`execution/handoffs/03-comparison.md`; no code/config edits. One training job
at a time and hard aggregate elapsed compute cap as contract. Check ledger
and projected remaining requirement before each job. Record failures and
superseded artifacts, abort on nonfinite values or numerical invariant failure.
Send Astra progress at least every minute while long jobs run; avoid waits
longer than60 seconds. Capture process exit code and raw output.

Acceptance: complete six-run common-update measurements, paired stream and
initialization evidence, equal-time checkpoint measurements with slack, all
required numerical/phase/throughput/memory metrics, runtime/config/code hashes,
and cap accounting; otherwise explicit missing-measurement list and feasibility
evidence. Sol independently checks raw artifacts/metric counts and comparability
before Astra accepts. Results are screening evidence, not publication claims.
