# V2 Stage 0: frozen dataset-only construction (ACCEPTED)

No models, training or pilot scaffolding in this block. This supplements the
scientific plan with deterministic choices before outcomes. Ceiling900 elapsed
CPU seconds inclusive tests and audit, charged also to the7200s global v2 cap.
No edits to earlier code or artifacts. Astra specifies; Terra implements; Sol
reviews implementation before one production ladder command.

## Pool and order

Board n=8 everywhere. Reuse verified pure geometry, BFS/counts, route enumeration,
signature, Hamilton and residual-flow helpers from route_feasibility additively.
Do not call old candidate/support/pipeline/Attempt defaults that encode6x6,
old family names, old quotas or old ledger paths. Signature operates on action
strings and has no board-size argument; all geometry/oracle calls explicitly8.

Rung A index0 families/codes III:0, LLL:1, IIL:2, ILL:3; rung B index1
IIII:0, LLLL:1, IILL:2. Enumerate all individual triomino placements using
triominoes(8); sort each I/L list by sorted cell tuple. For every family use
PCG64(SeedSequence([80000,rung_index,family_code])). Each trial draws one
placement index per letter in family order, independently with replacement.
Reject overlap first, then orthogonal touching of different components, then
duplicate D4-canonical wall bytes. Record rejection counts and total trials.
Stop at256 distinct maps or100000 trials per family. Never refill after selection.
Sort all retained canonical byte strings globally; assign increasing map IDs.
Walls are positions of ones in canonical bytes; no free-cell connectivity filter.
Reconstruct orthogonally connected wall components in the canonical frame to
audit kind/orientation: I horizontal/vertical, L by its missing2x2 corner.
Selected training maps must collectively include both I orientations and all
four L orientations, making the plan's primitive/rotation support claim explicit.
Missing coverage is a scientific construction failure; malformed components or
family/count inconsistency are technical errors, never permission to try B.

For each map enumerate all reachable ordered start/goal pairs with BFS using8;
retain A distances6..14 or B8..18 and16<=M<=256. Sort by(start,goal,distance,M).
Disconnected/unreachable pairs are not candidates. Inventory each family even
if another family is scarce, subject to deadline. Partial work is NOT_EVALUATED.

## Selection, lengths and family allocations

Split seeds A train81001/validation81002/test81003; B82001/82002/82003.
Each family map stream PCG64(SeedSequence([split_seed,family_code,0])); each
family problem stream same seed with final1. Streams are initialized once per
family/split and consumed continuously in sorted map-ID, ascending length order.
Map eligibility is at least16 qualifying pairs. Eligible maps sorted by ID,
permuted once; take first required count. Exclude all earlier split map identities.
No swapping maps after a flow failure; selection failure means construction
failure, not impossibility of any alternative dataset.

Exact counts, in both rungs: train32 maps per homogeneous family; validation
routine12 per homogeneous family; test routine48 per homogeneous family.
A challenge validation4 each IIL/ILL and test16 each. B challenge validation8
IILL and test32 IILL. Every selected map supplies exactly16 problems.

Training uses all eligible pairs. Select maps first, then Hamilton uniform
integer-length quotas totaling1024 across9(A) or11(B) lengths, descending
fractional remainder then ascending length ties. Represent flow bins as(length,0).
Run the accepted deterministic residual flow globally across all64 maps with
map capacity16. Require total1024 and all column quotas satisfied, else fail.
Within each selected map/length, permute its sorted eligible pair list using
continuous family problem stream and take the allocated count. Final selected
records sorted(map_id,start,goal). Each length consequently has at least16.

Build exact deduplicated supervised shortest-DAG states from selected problems,
q from completion counts; terminal states excluded. Training exclusion support
is every nonempty suffix of every selected shortest route: this is exactly all
shortest completions from every supervised DAG state. Canonicalize D4/reversal
action strings, preserving length; translation is implicit in action strings.
Save sorted length-delimited signatures and hash. Do not truncate enumeration.

For held-out maps, enumerate candidate routes and count signatures absent from
training support. Routine eligibility requires M_novel=0; challenge requires
M_novel>=4 and .25<=M_novel/M<=.75. No architecture data is available/used.
Select validation routine then challenge, then test routine then challenge.
For each stratum Hamilton-scale the actual training length proportions to its
384/128/1536/512 total; residual flow globally across that stratum's selected
maps with16/map; select pairs by the fixed streams as above. Rounding is the
only histogram difference allowed. Preserve quotas, capacities, allocations,
permutations, eligibility counts and rejection reasons for audit.

## Gates, artifacts and bounded execution

One production invocation attempts A. Only a scientific construction failure
(bounded supply, frozen novelty-eligible selection, length-flow infeasibility or
missing training orientation coverage) permits B in the same
owned process with separate immutable rung records. Runtime/error/budget failure
stops, not B. First PASS stops the ladder. Both construction failures stop the
iteration with reviewed feasibility failure; no training or relaxed criteria.
Never use a deadline exception as evidence that the full candidate pool failed.

Persist per-rung inventory, selection, selected splits, training states/q,
support, per-problem novelty, summary and exact source/config/input/runtime/output
hash manifest. Summaries identify which gates ran and which are NOT_EVALUATED.
Failure outputs must retain completed evidence. Write parent attempt completion
record, elapsed charge and separate v2 append-only UUID ledger once. True time
chronology; account startup overhead conservatively. Strict JSON (no NaN/sets/
tuple keys), unique output dir, owned O_EXCL lock, fail-if-exists, interrupting
deadline/global budget check. Reuse accepted safety concepts narrowly; all
paths explicit v2 so tests/production cannot touch old ledgers. Any test fixture
uses its own temporary ledger. No production compute before Sol PASS.

## Finishable implementation handoff

First Terra block: pure pool/candidate/selection/support/novelty/flow engine plus
small exact fixtures; no CLI or models. Second block: minimal artifact/attempt
wrapper reusing accepted safety code, integration test and production CLI. Each
completed block goes through one independent Sol acceptance gate. Do not return
partial scaffolding as complete. Avoid full old-suite repeats after narrow edits
unless shared behavior changed; preserve hashes of old source.

Allowed new files: schrodinger/productive_diversity_data.py,
tests/test_productive_diversity_data.py, and records under
execution/next_level_v2. No old implementation/test edits. Pure interfaces should
accept injected small inventory/selection sizes for exact tests while production
defaults remain frozen; fixtures are explicitly nonproduction. Permitted checks
are py_compile and focused pytest using .venv/bin/python, with timeout120s per
command and150s cumulative implementation-test ceiling within Stage0. Save full
command result/exit evidence and exact file hashes in each completed handoff.
No trial inventory or production pool for development tests. Integer/count/
signature/identity assertions exact; q probabilities sum within1e-12 and agree
with independent completion counts within1e-12. Requested numerical budgets
are elapsed compute, not time spent reasoning or editing documents.

Core regression requirements: explicit8x8 beyond cell35, component-count/touch
rejections and D4 identity, reproducible seeded streams, continuous per-family
problem RNG, Hamilton nonuniform evaluation proportions, reverse-edge flow,
all-DAG suffix support versus independent tiny brute force, exact M_novel and
ratio endpoints, family split counts, no cross-split map identity, first-PASS
ladder stopping and no B after technical failure. Wrapper regression: strict
JSON/cardinality/manifest, temporary ledger isolation, existing-output/lock/
deadline/budget guards, exactly-once chronological charge, actual tiny injected
CLI exit/completion record. Test production-scale generation is not authorized.
