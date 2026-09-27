# Block1 — pure geometry, bounded inventory and proposal ranking

Implement only after Sol accepts plan/contract00. Terra owns code/tests; no
production pool, proposal support, held-out selection, runner or model yet.
Allowed new files schrodinger/productive_diversity_v3_data.py and
tests/test_productive_diversity_v3_data.py plus execution/next_level_v3 handoff/log
records. Do not edit older implementation/tests/ledgers.

Complete these pure interfaces (equivalent clear names acceptable): immutable
production config; direct_shape_placements(n); seeded bounded pool_family;
explicit-dimension BFS inventory and per-map/length shortlists; rank_proposals.
Every dimension propagated to old pure helpers explicitly. No hidden8 or6.
Production defaults exactly contract00: n12,8components, three families,256pool,
200000trials, M16..256, lengths12..20,64shortlist, frozen seeds/streams/ranking.
Small injected fixtures are internal API only. Placement cache stores immutable
tuples; audit family/component/canonical identity exactly.

Proposal ranking is pure and deterministic. Use Fraction or integer cross-products
for supply ratios and mean-M cost ties. Return JSON-convertible records (fraction
numerator/denominator explicitly) for all12 proposals, raw family counts,
infeasibility reasons, per-window winner, distinct-window rank and top3 retained.
Never enumerate route sequences or compute novelty just to rank. Ties and quota
order exactly contract00; no models or output-dependent alternatives.

Acceptance tests: direct placement sets match exhaustive helper atn3,4,5;
production n12 cardinalities240I/484L and cells>63; separation/rejection priority,
fixed draws/seed replay and canonical dedup; explicitn12 BFS/q oracle cells>63;
shortlist permutation once per map/length and exact cap/order; ranking with raw
capacity failures, exact ratio/mean-M ties, quota order, one winner/window and
three-window truncation. Test no route-enumeration call in ranking. No production
inventory or real default-size pool in development tests.

Run only focused tests/compile with .venv/bin/python; <=60s timeout per command,
<=180s cumulative v3 development tests (charged within1600s dataset stage).
Print/store full command result; preserve/poll any session to explicit exit;
one compute process. Append every failed/passing check once to NEW v3 ledger
with UUID, actual UTC chronology and elapsed/full-wrapper charge. The initial
carried debit443.384519002 is not a new compute run or entirely an allowance.

Handoff01-core.md must give exact source/test hashes, commands+exit statuses,
actual assertions, aggregate charge and any limitation. Return only a complete
bounded Block1; unfinished implementation is not a completion milestone. Sol
independently reviews it before Block2. No broad future-stage scaffolding.
