# A2a banks and route-metrics implementation handoff

Status: ready for Sol exact review. This implementation is pure/additive; it
does not generate production banks, perform model scoring, profile, train, or
authorize A2b.

## Exact hashes

- Accepted model, unchanged: `schrodinger/route_policy.py`
  `95cb7463693c7ac696d9034eaf16a155c0363f38e819cbe56c00408d49b170c4`.
- New metrics: `schrodinger/route_policy_metrics.py`
  `a471ae2c40973cb15584f924061b3ace24ef5af3b1e31702b79056055f317e34`.
- New tests: `tests/test_route_policy_metrics.py`
  `c49b01afcca4ab0fa9cea4811f2ca92005b943817b2176011447d58b86c940c2`.

## Public interface and assertion map

- `ScoreCandidate`, `ScoreBank`, `serialize_candidate`, `record_hash`,
  `q_array_hash`, `training_bank`, `heldout_bank`, and `probe_bank` (metrics
  lines 21–107) implement fixed serialization, rank selection, candidate/selected
  IDs, little-endian contiguous float64 q hash, saved-DAG versus held-out BFS-q
  candidates, and fixed probes.
- `proper_scores`, `weighted_proper`, `relative_improvement` (lines 112–141)
  implement local legal CE/KL/Brier/entropies/nonoptimal mass, q-positive-only
  arithmetic, equal states/map then equal maps/stratum and 0.8/0.2 mixture,
  explicit routine/challenge outputs, with zero-reference improvement `None`.
- `rollout_uniforms`, `choose_action`, `greedy_action`, `verify_route`,
  `rollout`, `route_metrics` (lines 142–184) implement PCG64 streams, N/E/S/W
  ties, inverse-CDF final-legal tail, first-goal/16-stop route validation and
  separate Q/U/V/duplicate metrics. `LogitCache` lines 198–204 keys values by
  caller-supplied model/checkpoint/intervention identity plus map/goal/current.
- `choose_temperature`, `quality_temperature`, and `entropy_temperature` (lines
  186–215) persist target/direction and enforce nonincreasing quality by default
  versus nondecreasing entropy, with correct direction-specific bisection/grid
  fallback, every observed intermediate violation, and non-eager cached evaluation.

Literal tests:

- `test_serialization_bank_qhash_and_probes` lines 8–13 asserts exact candidate
  bytes, deterministic rank result, IDs/hashes, and an actual less-than-32 map.
- `test_heldout_dedup_q_and_real_accepted_route` lines 14–25 asserts repeated-goal
  dedup, verifies an exact shortest route on a genuine accepted frozen validation
  problem, and independently checks a hand-verifiable free-board branch q
  `(0,.5,.5,0)` (including illegal/nonoptimal zeros), 143 deduplicated nonterminal
  candidates, and selected little-endian q-array SHA256
  `54d38f25271b98f027a31aa0cd911dbeddd90c15f62103b0aaad57582cf9e30e`.
- `test_proper_weighting_and_na` lines 22–26 asserts irreducible CE/KL, q==p
  Brier zero, illegal probability zero/illegal-q failure, exact 0.8/0.2 equal-map
  mixture, and zero-reference NA.
- `test_streams_actions_routes_and_cache` lines 27–34 asserts deterministic
  split-keyed streams, N/E/S/W ties and inverse-CDF tail, un-repaired valid and
  invalid attempts, U_novel `.2` versus repeated V_novel `.4`, per-attempt Q/U
  denominators, duplicate rate, and changed checkpoint cache identity.
- `test_temperature_all_branches` lines 39–45 asserts physically correct quality
  nonincrease and entropy nondecrease directions, direction/target persistence,
  endpoint and intermediate quality-increase fallback, unbracketed ineligibility,
  and one-call-per-temperature caching.

## Focused test and accounting

Final command: `.venv/bin/python -m pytest -q tests/test_route_policy_metrics.py`.
Direct-exit UUID `7e00924a-02a6-4ef4-afee-215e40f5ce07` at
`2026-09-19T12:38:49Z`, exit 0, charged `1.266825916` seconds (`5 passed in
1.17s`). All A2a attempts are append-only in [the stage ledger](../ledger.jsonl),
including the two initial test failures. Starting A/global `39.654096212` /
`962.657693465`; current A/global `51.450107917` / `974.453705170` seconds.
One immediately prior result was lost by this agent's reporting-wrapper typo; its
full outer 1.4-second wall is conservatively charged as `UNKNOWN_OUTPUT_CHARGED`
without a pass claim, followed by the retained passing command above.

## Limitations deliberately retained

- No production bank serialization/output exists yet.
- No logits/model inference, cached checkpoint data, or training support is read.
- No temperature is fitted on test data and no train/profile/pilot command ran.
- A2b harness work remains blocked on Sol exact review.
