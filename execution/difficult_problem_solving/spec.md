# D0: bounded additive retained-data analysis

Implement only `execution/difficult_problem_solving/analyze.py` and
`tests/test_difficult_problem_solving.py`; preserve all accepted source/raw files.
No new general runner framework. Reuse reviewed owner/serialization/resource
installation and retained-event adapters where sound. CLI has no arbitrary seeds,
checkpoint list or test option: fixed seeds 1702–1705, updates 1000/2000/4000/8000,
both modes, full validation only, K=1/2/4/8/16/32. No model calls/checkpoint loads.

Load each training owner once, validate COMPLETE/output manifest/result SHA and
accepted producer-authority/input identities (reviewed replication `_owner_record`
is reusable without `_checkpoint`). Bind each event using accepted event digest
and original result SHA; reuse `_storedroutes` T1 adapter for exact ordered 512
problems ×32 attempts and verifier corroboration. Cache owner parsing across four
updates; never re-run model evaluation. Validate all events, all same 8 challenge
maps ×16 and 24 routine maps ×16, exact problem IDs/canonical orientation and M.
Use `load_validation`, never `load_final_test`. Historical all-invalid order
limitation must remain in output/report. Input manifests/producer/plan/helper/code
hashes and command arguments recorded. Copy no old source or ledger constants.

For each problem's 32 saved attempts, define c valid draws, route counts n_j for
valid raw byte routes, u number of those distinct routes. For each K:
bag pass=1−choose(32−c,K)/choose(32,K); expected distinct valid=
Σ_j[1−choose(32−n_j,K)/choose(32,K)], divided by K and by exact M. Impossible
choose terms are zero. Prefix sensitivity uses first K saved attempts and computes
observed pass, Q, u/K, u/M. Save raw c, u, c/32, u conditional on c>0 (null if
zero), duplicate concentration Σ(n_j/c)^2 (null if c=0), valid-route count
distribution and zero counts. These are finite-bag descriptive estimates, not
independent K replicates or new draws. Keep valid-only and all-problem denominators.

Aggregate within map then equal maps for each routine/challenge stratum; optional
80/20 mixture clearly secondary. For every update/seed, pair problem keys and
save K32 both/SM-only/SA-only/neither, per-map gain/loss and c/32 distributions;
retain per-problem data and per-seed differences. No map/sample pseudoreplication.
Predefined one-axis geometry bins, not selected intersections: length14/15/16,
detour shortestlength−Manhattan 0/≥2, M1–8/9–64/≥65. Validate detour nonnegative
even integer, exact M positive. Save all bin/map/problem counts and null metrics
for empty bins. Within a bin aggregate available problems equally per map, then
maps equally, showing support; do not equate bin comparisons with controlled
causal difficulty. No SA-favorable failure cohort.

Gate uses ONLY challenge K32 at8000: all integrity checks true; ≥3 of4 pairedseed
differences strictly positive; for each of the8maps delete that SAME map from
both architectures/all seeds, recompute per-seed equal means over remaining7maps,
then average the4 differences. Every leave-one-map-out mean must be >0; zero
fails. Save all8 raw values, all4 seed deltas, booleans and overall gate. Do not
read the gate from prior report or soften on failure. PASS only recommends D1;
the actual D0 job never invokes another stage.

One owned immutable output `execution/model_training_comparison/difficult-d0-001`,
original authoritative ledger/shared lock and reviewed resource table A700/B3500/
C400/D1300. Set alarm ≤56 seconds so existing4-second startup/finalization
allowances fit total60. Check remaining global/stage allocation; no retry if
yielded or automatic attempt replacement. Full JSON output includes metrics,
gate, provenance, scope flags no model/test access. Owner writes manifest/attempt
record and charges actual wall plus allowances on all exit paths. A technical
failure is not a scientific gate failure. Use `.venv/bin/python -m
execution.difficult_problem_solving.analyze` after exact Sol PASS only.

Acceptance tests (focused, all attempts charged A, cumulative≤100 s):
1. Hand-calculated allinvalid/allvalid/repeatedvalid/mixed bags, K1/K32 identities,
   impossible combinatorial terms, duplicate denominator and prefix distinction.
2. Equal-map weighting on unequal counts; all empty bins explicit; correct geometry
   for known 12×12 coordinates and M boundaries.
3. Gate fixtures show same-map deletion across all seeds, exactly-zero failure,
   seed-direction threshold and a concentrated gain that fails leave-one-out.
4. Real retained1702 event interface, direct-hex routes and fixed identities;
   negative event/hash/order mutation; no inference/test-loader allowed in test.
5. Composed synthetic4seed×8map×16problem gate/summary and required output fields,
   with real metric calculations (no patched gate/aggregation). CLI-owned seam
   asserts stageD, unique output,56-second alarm and no model/test functions.

Provide ONE complete handoff with exact code/test hashes, actual full command
results/explicit exits, line-to-test checklist and total charges. No broad source
hardening or optional features. Sol exact review is mandatory before one production
run. Two correction cycles then concrete bounded respecification/blocker.
