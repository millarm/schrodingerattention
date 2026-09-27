# Block2 — support-dependent joint selection (after Block1 PASS only)

Terra extends only the new v3 data module/tests; no runner or production data.
Implement the remaining pure dataset construction from frozen contract00 using
the already accepted inventory/ranked proposals. Do not regenerate/re-rank pools
after any support outcome. No older source edits or model scaffolding.

One bounded cache object per proposal: explicit n12,<=512 BFS entries,<=512
pair-signature entries,<=65536 action-string canonical signatures. Count exact
misses/routes/hits and measured oracle elapsed time. Reusing eligibility requires
the exact support hash; no cross-support reuse. Signature canonicalization is
geometry-free, but all BFS/enumeration/neighbors receive n explicitly.

Training: frozen map permutations and raw eligibility,32 maps/homogeneous
family; exact per-map length quota from first shortlist pairs. Validate selected
map identities/component orientations. Compute exact deduplicated shortest-DAG
states and completion-count q with cached counts (no unnecessary fresh BFS per
state). Enumerate all shortest selected routes, verify M, and canonicalize every
nonempty suffix; persist sorted length-prefixed support identity. Every selected
training length has64*q>=16 examples; no canonical single-answer supervision.

Held-out: exact validation-routine,validation-challenge,test-routine,test-challenge
order; independent frozen family/split stream initialized once. For each scanned
raw-eligible unexcluded map, visit lengths ascending and candidate shortlists in
frozen order. Accept first q eligible pairs; stop scanning that length at q.
Reject map immediately when a length exhausts without q. Commit identity only
when whole-map quota passes. Return exact evidence for scanned prefixes,
rejections, selected pairs and untouched NOT_EVALUATED maps; no global flow or
extra candidates outside the frozen shortlist. Novelty predicates remain strict.

The proposal orchestrator returns successful dataset or declared scientific
supply/orientation failure with all completed evidence. Each proposal gets its
own fresh support and output/evidence object. Runtime/oracle/count/hash defects
raise technical errors, never a next-proposal signal. Optional callback on
completed stages lets future runner persist artifacts before expensive work;
callbacks do not alter selection. First full PASS stops the ranked proposal list;
at most three distinct windows, no extra pools/quotas. Profile counters exposed.

Acceptance: oracle-backed internal tiny composed SUCCESS containing genuine
routine AND partial-novel challenge rows, not whole-stage fake PASS. Reuse the
v2 successful fixture pattern via additive new fixture adapted to n12 and cells
above63; internal small families/counts/length quotas are explicitly nonproduction,
and no predicate/q/oracle validation may be bypassed. Separately assert three-
length per-map proportions, raw training selection exact seeds/prefix, lazy
map rejection/length early stop, no committed identity on rejected map, every
split map disjoint, all-DAG support versus independent routes, normalized q,
support-key cache separation/hits, exact .25/.75 challenge endpoints and rejection
outside/belowMnovel4, M/count/length/family/identity mismatch technical, first
proposal PASS and scientific-only advancement. No real production pool in tests.

Every returned selected row must be linkable to inventory and retain n/family/
map/canonical/start/goal/length/M, plus Mnovel for evaluation. Use structured
exception/result types with explicit outcome and reached/unreached stages, not
string parsing. Preserve proposal selection/audit evidence even on ordinary
supply failure. Source stays frozen during Sol review.

Focused tests<=60s/command, remaining v3 development allowance180s cumulative;
charge every command once with full result/session completion in new ledger.
Handoff02-selection.md exact module/test hashes, commands/status, assertion map,
elapsed charges and honest fixture boundaries. Sol independent PASS required
before runner block. No claims of production feasibility from tiny fixtures.
