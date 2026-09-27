# A2b2a — complete evaluator and mechanism probes

Logical subdivision of A2b2, no new science/resources. Terra creates additive
schrodinger/route_policy_evaluation.py and tests/test_route_policy_evaluation.py.
Accepted model/data/metrics/core remain unchanged. This module has no production
CLI or output/ledger ownership. Use accepted load_training/load_validation and
ScoreBank helpers as real data sources; callers supply immutable models, bundles,
banks, support and stream identity. Temporary test fixtures may use a small
subset of the actual accepted data, never invent a production manifest/bank.

Implement these complete interfaces (exact function names are Terra's choice):

1. Batched missing-state logits cache keyed by explicit checkpoint/model/mode/
   intervention identity and canonical map/goal/current. Batch all active missing
   states per rollout step, not one forward per action. Model only sees 36 numeric
   row features and locally legal masks; q/support never influence actions.
   Common frozen uniforms and deterministic greedy ties; stop on first goal or
   16 moves. Reuse A2a exact verifier/metrics. Return raw action attempts and
   per-problem/per-map/per-stratum/0.8-0.2 outputs, including U/V novel/valid,
   duplicates/invalids/coverage/NA values and correctly weighted known-valid mass.
   Own-initial, uniform-legal, temperature and dt0 calls share streams. Multiple
   temperatures may reuse raw logits but still time each categorical rollout.
2. Proper-score evaluation on supplied fixed banks, batched inference, exact
   A2a weighting and per-state arrays. No test release logic here: runner controls
   access and must never call evaluator on test before explicit release.
3. Bounded probes via temporary read-only hooks/reconstruction, with hooks always
   removed. For each layer/head on the SAME normal-SA hidden states compute
   evolved A vs unscaled softmax(S) row TV (all rows and CLS separately),
   attention AV and projected-sublayer absolute/relative RMS differences. Return
   raw sample values and mean/p50/p95/max/head summaries; zero RMS denominator NA.
   Compute ||dt H||_2 and relative phase dispersion. Define the latter here as
   RMS of wrapped phase differences to the first key within each query row,
   atan2(sin(phi_j-phi_0),cos(phi_j-phi_0)); it is descriptive, not a new gate.
   Normal-vs-full-path dt0 final policy TV, signed CE/KL/Brier differences and
   greedy disagreement are separate from local differences. Scheduled numerical
   Hermitian/unitary/row abort thresholds remain exactly frozen. No autograd
   graphs or permanent model mutation. Per-stratum arrays follow probe-bank IDs.
4. Timings for cache inference, categorical rollout, verifier/uniqueness, proper
   scoring, mechanism/numerical probes and total end-to-end, without overlapping
   phase sums or claiming cache eliminates Python cost. Serialization is runner's
   responsibility, and its time is added there.

Literal tests: cached versus uncached batched predictions/actions/metrics on a
small real selected route fixture; forward-call count proves batching and no
cross-checkpoint reuse; same uniforms across temperatures/interventions; exact
local-versus-propagated dt0 distinction; zero-evolution same-score TV near zero;
probe numerical tolerances/head+CLS distributions; no lingering hooks or model
parameter changes; initial/uniform controls; complete timing/metric keys and NA
denominators. Keep small enough for <=20-second focused test target, all actuals
charged stage A. No production bank build, profile or pilot.

Complete handoff A2b2a-implementation.md and Sol exact subset PASS are required.
Afterward A2b2b supplies CLI/authorization/provenance/banks/profile/forecast using
this evaluator and accepted core. No partial evaluator is a finished harness.
