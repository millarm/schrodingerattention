# D1 implementation contract — 2026-09-20

## Approval and boundaries

User explicitly approved `d1-approval-and-resource-proposal.md` on 2026-09-20.
This prospectively authorizes D1 charged maximum 300 s, cumulative investigation
development 140 s, and stage caps A700/B3500/C300/D1400, global 7200 unchanged.
Development already charged 83.077375040 s; remaining 56.922624960 s.
Global starting debit 4282.233080711118 s. Preserve the original plan SHA
`c31c3ee84131ec4e96dbbd42e073a4ec96be63a0b3fc65058a18275714c035fe`.
No D2/test loader or payload, training, new checkpoints, seeds, samples beyond
the specified grid, or modified model/evaluator/data/metrics source.
Astra specifies; Terra alone implements/tests; Sol reviews this contract and
the exact implementation before production. Root coordinates separate Sol task.

## Small additive implementation

Create `execution/difficult_problem_solving/d1.py` and a separate narrow test
file outside the frozen `test_route_policy*` glob. Reuse accepted OwnedAttempt,
serializer, checkpoint/owner binding, validation loader, evaluator and metrics;
do not build a new runner framework. Resolve paths from `__file__`, not CWD.
Expose pure selection/forecast helpers and one injectable orchestration seam for
synthetic tests. No training or test-release imports/calls are necessary.

### Inputs and provenance

Obtain identical input_ids metadata from manifest-bound COMPLETE retained
replication analysis/owner artifacts, require agreement across all seeds/models,
and pass these IDs directly to narrow checkpoint/owner validators. Never call
`_prepared_ids`, `load_final_test`, test-selection helpers, or deserialize the
prepared payload: prepared.json contains sealed test rows. Its published hash
may be checked only with opaque streaming SHA-256, never JSON parsing. Composed
tests must explicitly forbid those paths too. Read original source hash, load complete
validation only, assert 512 distinct ordered problems, 24 routine maps and eight
challenge maps with 16 problems/map, and freeze explicit canonical/start/goal/
family/map IDs. Reuse training support through its accepted hash-bound loader;
do not regenerate support. Use seeds 1702–1705 and only final 8000 checkpoints.
Reuse replication `_checkpoint`/owner authority to bind model/config/input/
initial/final identity; do not invoke its whole analysis/training command.

Bind all four immutable `replication-SEED-analysis/analysis.json` files to their
output manifests and COMPLETE owners, their accepted analysis-source identity,
input IDs, seed, checkpoint hashes and retained event bindings. Retain source
paths/hashes once, not repeated per route. Exactly reuse SM T1 and SA T0.75/T1/
T1.25 per seed; retain bound greedy records from original final events. Verify
stored grid temperature and seed/splitcode=1/replicate=0/K32 evidence against
the accepted producer and ordered problem list. Historical raw records have no
independent start/goal IDs: document producer/event/dataset-order binding and
all-invalid permutation limitation rather than invent independent proof.
Reused records must remain identifiable as reused, with original measured time
not counted as newly consumed D1 time. An identity mismatch stops; no inference
replacement of a rejected reused endpoint.

### Exactly 24 new endpoints

Seed order 1702,1703,1704,1705. Within seed SM-first for 1702/1704, SA-first for
1703/1705. Missing temperatures ascending: SM .5,.75,1.25,1.5; SA .5,1.5.
Call accepted evaluate_rollouts on all 512 validation problems with K32,
seed=training seed, splitcode=1, replicate=0, unchanged support/verifier. All
five temperatures use the same existing per-problem/draw/step uniform scheme;
retain its construction and digest, explicit problem IDs and checkpoint identity.
Cache reuse across missing temperatures is allowed only within one checkpoint
identity; record cold versus incremental inference and end-to-end timing, and
never present a warm-cache endpoint as standalone cold latency. No extra greedy
inference: positive temperature preserves argmax, so reuse bound greedy output.
Use the same empty-cache-then-reuse policy for each architecture/checkpoint,
with ascending missing temperatures. Retain forward-call/batch-state counts via
a read-only outer model proxy or removable forward hook, and actual generated
action counts from retained routes; do not edit the accepted evaluator. Historical
counts unavailable from retained records remain unavailable, not invented.

Retain every candidate's raw attempts, map/stratum metrics and timing. The exact
40-cell grid (16 reused +24 new) must be complete before selection succeeds.
For each seed, reference both routine and challenge Q to that seed's SM T1.
Candidate eligible iff both Q values >= reference minus .02. Select maximum
challenge pass@32; among values within 1e-12 of maximum select highest challenge
Q (same 1e-12 tolerance), then lower temperature. No mixture objective. SM T1
must qualify; no eligible SA candidate is a control-failure/no-go, not retuning.
Freeze selected T, candidate/config/checkpoint/support/RNG hashes. Report four
paired selected differences plus all candidates, not significance from tuning.

### Validation-only forecast and uncertainty

Reuse retained proper-bank and greedy measurements where their exact operation
and cardinality are bound. Profile validation-bank construction only if needed
for missing cost evidence, charging all work to D1. No test payload/oracle access.
Known static D2 counts are eight model endpoints, each 2048 problems (1536 routine
+512 challenge), at selected T K32 plus greedy and accepted proper-score bank.
Use actual measured validation operations/cardinalities and conservative scaling
to these counts, charging cache construction, categorical sampling, verification,
bank setup/scoring, loading, output I/O/finalization; apply 1.5× to the entire
prospective work. Keep each cost cell/source/scaling factor explicit. Reused
warm-cache cost cannot replace a cold-cache bound. If any essential measurement
or scaling bound is unavailable, label forecast unsupported/no-go, never zero.
No added model probes or test inspection solely to rescue a forecast. D2 go
requires forecast <=420 s and reserved audit capacity; it still does not grant
D2 authority. Report actual K32 latency only, not inferred equal-time curves.

Hold selected temperatures fixed. For the four selected challenge pass@32 seed
contrasts report mean, sample SD(ddof=1), half-width 3.182446*SD/sqrt(4), and full
95% width twice that value. For map uncertainty use NumPy PCG64 seed91703 and
2000 resamples of eight challenge map IDs with replacement; the same resample
applies to both architectures and every seed. Recompute each seed's equal-map
contrast then their four-seed mean. Use NumPy quantile method='linear' at .025
and .975 and report endpoints/full width. Emit a separate approximate32-map
width equal to this map width*sqrt(8/32), explicitly conditional on fixed
selection and iid/exchangeable maps; never scale the four-seed interval. No
power or new-map-evidence claim. Preserve negative/null results.

## Ownership, charge and failures

Install the approved runtime stage table narrowly in this entrypoint while
checking expected original table; do not alter replication provenance or old
module bytes. Record amendment/approval/spec/review hashes and actual argv in
new owner `difficult-d1-001`. Use existing owned lock/fail-if-exists/output
manifest/ledger semantics. Cap timer at remaining D1 allocation minus existing
startup/finalization allowance (initially 296 s), and global/stage headroom.
All setup after begin, failure and profiling counted; no automatic retry.
Preserve partial candidates incrementally for a truthful resource stop. Never
mark complete selection/forecast on a partial grid. Explicit exit/session and
terminal owner evidence required. Final report/audit charged separately within
unchanged remaining audit allocation, not hidden as inference.

## Literal acceptance tests and handoff

One focused synthetic test command; total tests/failures <=remaining 56.922624960
s, timeout bounded prospectively. No actual model inference in tests. Cover:

1. Exact grid partition16/24; seed/model/T/K/split/replicate forwarding, cache
   separation and complete ordered IDs; greedy reuse/no extra call.
2. Both separate Q floors, no eligible SA, maximum-pass rather than maximum-Q,
   both tie levels within1e-12, lower-T final tie, no missing/duplicate cells.
3. Actual retained analysis interface read-only: raw hex-string attempts,
   manifests/input/seed/checkpoint/producer identity. Negative hash/seed/T/order
   binding mutations rejected; acknowledge historical order limitation.
4. Synthetic composed owned success writes JSON/manifest, all40 records and
   selection/forecast; injected late write/finalization failure is non-success
   with ledger/lock cleanup under accepted owner semantics. No model/test loader
   invoked; explicit forbidden-call guards on composed seam.
5. Forecast cardinalities/scaling/1.5×, missing-cost no-go, >420 no-go, cold-cache
   accounting; literal workspace paths, proposed stage table and300s cap.
6. Known-count synthetic forward invocations, summed batch-state counts, and
   generated actions summed from every retained route length; cache reuse
   changes forward counts without changing common-uniform route identity.
   Historical unavailable counts are null, not zero. Literal seed-SD/width and
   shared-map bootstrap/linear-quantile assertions (including32-map scaling
   only on map width) with fixed selected temperatures.

Handoff lists exact file hashes, assertions/test names, commands/exit/full elapsed
charges, known limitations and remaining budget. No broad completeness claims
without literal assertions. At most two bounded correction cycles; no scope or
role substitution. Sol exact-version PASS precedes the single production run.
