# Stage 0 contract — dataset/oracle feasibility only

Status: ACCEPTED — Sol PASS in reviews/02-feasibility-contract.md.
No dataset outcomes inspected. This
freezes implementation-level selection ambiguities before computation; it does
not alter the approved scientific design. Stage0 cap600 elapsed CPU seconds,
including tests/failed attempts/audit; overall new experiment cap7,200s.

## Geometry and canonical identity

Coordinates (r,c) use0..5, cell index6r+c. Cardinal actions N,E,S,W are0,1,2,3.
Enumerate all in-board connected three-cell sets; I has three collinear cells,
L is the other connected triomino. Combine two nonoverlapping components with
no orthogonal cross-adjacency. Their union has exactly two components of three.
Classify II,LL,IL, independent of order. Do not add a connected-free-space filter;
individual problems must have reachable goals, as the plan states.

D4 transforms are the identity and three clockwise rotations of (r,c), plus
those four applied after reflection c->5-c. Encode a wall map as36 row-major
bytes,0 free/1 wall. Its lexicographic minimum over D4 is the canonical map.
Deduplicate by those bytes and sort lexicographically. Store every selected
map in canonical orientation, with an integer ID assigned from the global
sorted inventory. These IDs never depend on selection or model results.

## Oracle and problem candidates

For every canonical map and free goal, BFS gives exact distance. Dynamic suffix
counts C(goal)=1 and C(s)=sum C(next) for distance-decreasing neighbors give
the number of shortest routes. Candidate ordered (start,goal) pairs have
4<=distance<=10 and4<=C(start)<=64. Sort pairs by (start,goal). A map is eligible
if it has at least16 candidate pairs. Do not rank or filter by novelty.

Exact independent verifier: replay action sequence, reject illegal moves,
reject departure after first goal arrival, require final goal and route length
equal BFS distance. Enumerate shortest routes in N,E,S,W DFS order only for
selected problems. q=C(next)/C(s) for improving actions and0 otherwise; verify
enumerated count and equal complete-route probability1/M on fixtures.

## Fixed seeded selection

Use NumPy PCG64(SeedSequence([split_seed,family_code,phase])) with family codes
II=0,LL=1,IL=2 and phases map-permutation=0,problem-ranks=1. Split seeds are
41001 train,41002 validation,41003 IDtest,41004 ILtest. For each split/family,
freshly permute its sorted eligible map inventory after excluding prior splits'
maps. Select the first required32/32 train,4/4 validation,8/8 IDtest,32 IL maps.
No retry or alternative map search if later bin quotas fail. Store permutation
and selected IDs so selection is reconstructible. If supply is insufficient,
record exact requested/available counts and stop this gate without training.

For training, walk selected maps in global-ID order. Use the family-specific
problem-ranks RNG stream to permute each sorted candidate list, take first16,
then store chosen pairs sorted. This fixes1,024 training problems.

## Training-derived bins and exact matching

Use two marginal equal-frequency bins each for distance and log2(M), producing
four joint cells. Boundaries are NumPy quantile(training_values,.5,method='linear').
The lower bin includes values <=boundary; upper bin >boundary. Ties remain
unsplit, so empirical bin counts need not be exactly equal. Report boundaries
and counts. No outcome-dependent extra bins or bin merging.

For each validation/IDtest/ILtest split, set four joint-cell quotas by multiplying
training joint fractions by the required split problem count, taking floors,
then distributing remaining slots by descending fractional remainder with
lexicographic (distance_bin,logM_bin) ties. This is Hamilton allocation.

Selected maps still each contribute exactly16 problems. Solve a deterministic
integer flow: source->map capacity16, map->jointcell capacity available candidate
count, jointcell->sink capacity allocated quota. Edges/maps/cells are inserted
in lexicographic order; use deterministic Edmonds–Karp BFS augmenting paths.
If maxflow is less than the required total, record capacities/quotas and stop
as BIN_MATCH_INFEASIBLE. Do not replace maps, relax quotas or resample.
Within each map/cell, rank candidates by the split/family problem-ranks RNG
(walk maps then cells lexicographically), choose exactly the allocated flow,
and store pairs sorted. This matches bins without model or novelty selection.

## Strict support and novelty gate

For each selected training problem enumerate every shortest route and every
suffix beginning at each nonterminal state on those routes. The union of these
states equals the supervised DAG. Deduplicate (map,current,goal) states and
canonical route signatures. D4 applies to displacement vectors; reversal
reverses action order and negates every displacement. Signature is the least
of16 transformed action byte strings, preserving length. Empty terminal suffix
is excluded because terminal states are not supervised. Persist sorted support
as length-prefixed bytes (one byte length then action bytes); hash exact file.

For every selected test problem enumerate its M exact shortest routes. Count
M_novel as the number of distinct exact routes whose canonical signature is
absent from the entire training suffix support (several exact routes may share
a signature and still each count once as distinct solutions to that problem).
Compute the same labels for validation descriptively without using them for
selection. Gate: at least256/512 IL problems have M_novel>=4, across at least16
IL maps. On failure, report FEASIBILITY_FAILED_NOVELTY and STOP. This does not
test model creativity or learning; no model should have been constructed.

## Terra implementation scope and required tests

Add only `schrodinger/route_feasibility.py`, `tests/test_route_feasibility.py`,
and execution/next_level artifacts. No old sources/checkpoints/reports changed;
no model/harness implementation, optimizer, training, temperature sampling or
later-stage scaffold. Standard library and existing NumPy suffice.

Expose pure geometry/oracle/canonicalization/selection/support helpers and one
Stage0 CLI. Tests use small fixtures and explicit toy selection inventories,
not the full6x6 inventory before implementation PASS. Cover D4 map invariance,
D4+reversal signatures, distinct-map split exclusion, BFS vs an independent
small-grid exhaustive shortest-route search, dynamic vs enumerated counts,
q normalization/uniform completion probabilities, all suffixes in support,
positive/zero novelty fixtures, seeded replay, median ties/Hamilton allocation,
flow feasible/infeasible and per-map counts, verifier wrong/colliding/long routes,
deadline/failure records, output/lock ownership/no-overwrite including races.

Reuse the validated ownership/deadline design concept additively; do not import
or write the old diagnostic ledger/rejection directories. Cumulative ledger is
execution/next_level/ledger.jsonl, entries unique IDs, append once under advisory
lock, chronological timestamps. Charge full commands plus declared startup
allowance2s, including rejects/failures. Tests write only temporary ledgers.
CLI acquires O_EXCL lock execution/next_level/compute.lock and fresh output;
owned-output flag controls any in-directory writes. Install interrupting600s
stage deadline minus already chargedStage0 and30s finalization reserve; also
enforce overall7,200s. Log success, scientific-gate failure or compute failure
distinctly, with status/elapsed/argv/PID/source/input/output hashes. Restore
timer and release only owned locks in finally; preserve all failed artifacts.

Outputs: runtime/input/source manifest, complete canonical-map inventory with
eligibility counts, split/problem/bin records, training supervised-state/q
records, sorted signature support, per-problem M/M_novel/route-signature records,
gate summary and command/attempt record. If an earlier gate fails, write its
exact evidence and mark later metrics NOT_EVALUATED, not zero. JSON/NPZ/binary
formats are sufficient; no spreadsheet formatting or new dependencies.

First Terra implementation/tests (<=60s charged), Sol review, Astra acceptance;
then Astra explicitly authorizes ONE full feasibility invocation into a fresh
attempt. Caller prints `text(r)` for the full exec result, stores session_id,
polls to explicit exit_code and never relaunches on yield. After confirmed exit,
Sol independently audits gate arithmetic and representative raw oracle/support
evidence. Only reviewed feasibility PASS allows a new bounded pilot spec.
