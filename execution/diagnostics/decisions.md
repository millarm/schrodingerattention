# Diagnostic decisions

2026-09-15: User authorized plan and checkpoint-only execution, no retraining.
Sol reviewed plan and issued PASS (review SHA256
c7f7456ea24a5daf39d199e8e13daf6c62230e0db391440159571591657d9e48).
Astra freezes the plan's metrics, descriptive bands, inputs and execution
rules before new diagnostic results. Authorize Terra additive implementation
and bounded synthetic/selected-batch correctness tests only. No full checkpoint
diagnostic before Sol implementation PASS and Astra run authorization.
Charge Sol0.2s to separate900-second diagnostic ledger. Prior experiment
ledger/report remain unchanged. Old non-overlap failures cannot recur.

Implementation handoff correction: Terra twice stopped at partial scaffolding
(metric primitives, then a manifest-only CLI). Neither was submitted for Sol
review or accepted. The cause is premature handoff, not an accepted change of
scope. Astra reissued one bounded completion checklist covering the full frozen
trace, stratified raw measurements, checks, summaries/figure, immutable attempt
records, finally-safe lock, and budget accounting. Terra must complete this
same implementation before review; a manifest-only run is not a diagnostic.
No checkpoint-analysis attempt has been authorized or launched at this point.

Implementation acceptance: Sol's final scoped PASS (reviews/04-output-ownership.md,
SHA256 34d209a136376848cabca24652c72df4567ec62fbed2340d05d870bcbd1e290f)
closes the ownership issue and retains prior metric/numerical/input/safety
acceptances. Astra accepts source SHA256
0468355260054a29243a2348b76db664b2d07d9f0a368058e3631c8334c79374
and tests SHA256 40be7c2e56fc21cef19ab896c7a5d0640e0dce8ae569ef09249c1f5da42ecb8f.
Authorize exactly one all-seed invocation into fresh attempts/checkpoint-001,
after ledger includes final Sol1.4s (23.7s prior cumulative charge). Use normal
exclusive lock and deadline. If exec yields, poll its exact session ID until
explicit exit; do not relaunch or treat file existence as completion. No code
edits, training, sweeps or reruns authorized. Preserve failure artifacts if any.

Final acceptance: Sol results/report audit PASS WITH EXECUTION LIMITATIONS
(reviews/05-results.md SHA256
1e00c597820a58b56322e6211846bc8fe92ea1daed5c2b3b675596156ec5a649).
Raw data and all stratified summaries/flags reproduce exactly. Astra accepts
the retrospective conclusion: attention often changes appreciably; downstream
effects are mixed, with offsetting classification gains/losses and rare large
tails; no consistent useful benefit meets the frozen band. Original screen
remains INCONCLUSIVE. One analysis invocation only, 36.325s elapsed; total
charged81.22535483300308s/900s. No further training/analysis authorized.

Execution deviations are disclosed, not repaired by rerun: launch wrapper
discarded session metadata (completion verified via runner success plus exact
PID absence and released lock); manual ledger insertion made physical order
nonchronological (preserved with appended explanation). These limit execution
provenance but did not change or overwrite the immutable scientific outputs.
Final report status and budget were updated after Sol's substantive report
review; findings and interpretation are unchanged. Mutable status/decision
files naturally differ from their at-run manifest snapshots after closeout.
