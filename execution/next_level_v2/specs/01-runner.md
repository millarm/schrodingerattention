# Stage0 runner: narrow second implementation block

Dependent on Sol acceptance of the pure-data engine; no scientific changes.
Allowed new schrodinger/productive_diversity_runner.py and
tests/test_productive_diversity_runner.py, additive pure-engine plumbing only if
necessary and explicitly reviewed. No old edits, model code or production run.

Compose accepted engine in frozen order: inventory, training, validation routine,
validation challenge, test routine, test challenge. Cache shared exact support/
oracle results as appropriate. Default counts and seeds are the accepted dataset
contract; injected tiny fixtures are explicitly test-only, not CLI options.
Assert unique maps across splits,16 problems per selected map, exact split/family
counts, exact length quotas and q, routine/challenge novelty predicates. Any
unexpected invariant bug is a technical error, not permission to continue B.
The exhaustive B-eligible scientific failure classes are exhausted bounded
family/map supply, frozen selection/eligible-pair supply under the routine/
challenge predicates, frozen length-flow infeasibility, and missing selected
training orientation coverage. Technical/not-B: malformed components, canonical
family/identity collision, BFS M versus enumeration mismatch, q/count/cardinality
mismatch after allegedly successful allocation, serialization/runtime/deadline/
budget errors or any unclassified exception. Final summary distinguishes these.

CLI: .venv/bin/python -m schrodinger.productive_diversity_runner --output PATH.
Default execution/next_level_v2/compute.lock and ledger.jsonl only; output unique.
Reuse existing verified append_ledger with explicit new path. Prefer narrow
subclass/copy of accepted Attempt behavior with v2 paths/config, no mutation of
old module globals.900s stage/global7200s; prior ledger charges included, startup
allowance2s, reserve30s for serialization/exit/audit. Deadline overrides in tests
may only tighten, never extend available budget. Test ledgers/locks isolated.

One parent attempt owns lock and charge across up to two rungs; immutable A/B
subdirectories preserve each rung. All output files created once, no rewrites.
Write checkpoints of completed artifacts before expensive later stages so a
deadline/error retains inventory/selection/training evidence, not just empty
failure. Candidate pool inventory stores canonical walls, family, candidate
pairs, trial/rejection counts, selection RNG/permutations. Training split and
states/support persist as soon as complete; subsequent strata likewise. Catch
deadline/errors only to finalize truthful summary/manifest then re-raise for
nonzero exit. Construction stop is successful execution with scientific FAIL.

Each rung summary records stage statuses (unreached=NOT_EVALUATED), scientific
outcome and exact observed/required counts. Parent summary identifies selected
rung or stopping failure. Manifest binds source (new engine/runner plus imported
old helper), tests, plan/contracts/reviews, frozen effective config, Python/numpy,
argv/executable/thread environment, each artifact hash and parent/rung linkage.
No circular hashes: manifest excludes itself and attempt completion record;
attempt binds manifest hash. Serialization strict JSON and stable list records
for flow/capacities/tuple keys, bytes hex except sorted length-prefixed support.bin.
Record both supplied support hash and actual file hash consistently. Do not
silently stringify sets or truncate lists needed for replay.

After explicit exit0 and Astra/Sol audit only may next stage be considered.
Tests: actual injected tiny CLI-style main exit/completion record, PASS ladder
stopsA, scientificAfail/Bpass and bothfail retain evidence, technicalAfail stops
withoutB, output exists/lock exists, interrupted stage with retained completed
artifacts, exhausted budget, exactly-once chronological UUID ledger, hashes and
JSON/cardinality validation, unchanged old ledger/source. Focused tests within
remaining150s cumulative development allowance; no real pools. Handoff includes
full commands/results and exact module/test hashes. Return complete block for
Sol independent review, not incremental placeholders. Production launch is Astra's.
