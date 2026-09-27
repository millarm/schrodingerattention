# Sol consolidated full-static safety review

**Verdict: CHANGES REQUIRED.**

`DRIVER_REVIEW_VERDICT: CHANGES REQUIRED`

Static review only. I read the protocol, v3 plan/specification, science-completion
specification, complete frozen study source and tests, S2 handoff, accepted
trainer/evaluator interfaces, driver review schema, and prior bounded driver
PASS. I did not import project code, run tests/subprocesses/models/data loaders,
inspect final-test payloads, or write the ledger. Ledger SHA-256 remains
`1340ee945d663e22c7a4fa7bd232c9832b90babe20d3d91662967116d232c3f9`.

Because this file does not contain the exact machine token
`DRIVER_REVIEW_VERDICT: PASS`, it cannot authorize the 10-second smoke or
30-second suite through `command.review_ok`.

## Exact reviewed source inventory

- study `b34ed709022be48ef2b02d608a8da190bff98e73a7caea6a2558ae1ba2500f15`
- driver `3adda02c82b2eb6a059d890b967950c6718e7406e64dd99fdcfe2dab47f38b4f`
- tests `4b6a50617c388c76f6b9890d48eb382cd7d367ffcb12b63b75a3aeba170c4113`
- watchdog `2b3fed56e07da5a33c122afa10e9cc5b77df0df77ec492db0bfaf4887708a8c8`
- plan `d4ce6e3c6e4c0a7eac46aa96b2a01f442abeed573c3b78e95a2edb874caca6ae`
- v3 spec `dcca6fa6c3ba0d322a8278d6003c77249c692a1224f37a3a2bad547530285a67`
- science-completion spec
  `fa9b05907af7399c8ca4b841d7d1217aae91b97d7d7e2f6d12cfab2aa5165364`
- accounting clarification
  `7ab55e8e05ca950597e9c7f09c948a8edbd2756f04854d1dc19851dba82c58c6`
- decisions `77affe9064fd016e2391c0b1f6ac67a8aac9d69b4f6d7af06c36f90ee3e798c4`
- handoff `5b3bf7ab0d26d0ff9f18b1d3664036d5c88c53e93c715043138e3b1cba6bcaad`
- prior driver-respec PASS
  `6338e14aa23bf488178d0a441119a7db0ed550e522b1ec5ad3474f983fabc2bc`
- accepted dependencies: attention
  `e1ce15be10caf4b2165191f9835256602f4f7b8bd11bffa94f676eac40b0fd6a`;
  feasibility `da36b0150c0b255b7e5482d7dc016505054d9632c8fb3a21d06c2d201bfedbf4`;
  policy `95cb7463693c7ac696d9034eaf16a155c0363f38e819cbe56c00408d49b170c4`;
  data `676b8de313fb9c667497b307704b21f137ac55a18e1e19c81be399d3f02e4bb7`;
  evaluator `fd5cd438e0fbd103857933418008a7c5936b379488857ac6bfa7370aa8ad18ec`;
  experiment `10cfc1a9a5e21856fd4e80f7c81b7b9243c104d452f10fc2a0062d4b4998036b`;
  metrics `a471ae2c40973cb15584f924061b3ace24ef5af3b1e31702b79056055f317e34`.

`study.source_hashes()` delegates to the driver's full authority inventory, so
the intended decision/result provenance model is compatible with the launcher.

## Blocking findings

### 1. The recorded `entropy` is policy entropy, not required teacher entropy

`study._score_metrics` lines 254–257 maps `entropy` to
`proper["weighted"]["entropy_p"]`. In the accepted proper-score implementation,
`entropy_p` is the model policy entropy, while `entropy_q` is the exact teacher
entropy. The v3 plan expressly requires teacher entropy at every scored stage.
Consequently the compact metrics, finite-metric validation, plateau/milestone
inputs and any report consuming `metrics.entropy` would mislabel the wrong
scientific quantity even though the raw proper artifact happens to retain both.

Required correction: record teacher entropy from `weighted["entropy_q"]` under
an unambiguous field such as `teacher_entropy`; optionally retain policy entropy
under a separate `policy_entropy` name. `validate_scoring_points` and literal
tests must require the teacher field and reject a nonfinite/missing teacher
entropy independently. The real two-mode fixture must assert the compact value
equals the accepted raw proper weighted teacher entropy.

### 2. Actual pair validation does not validate the stored configuration or full data identities

Production owners store `config_hash` (run result line 298), but
`validate_pair_identity` lines 208–214 compares a key named `config`. For two
actual owner results, both `.get("config")` values are absent/`None`, so the
comparison silently passes and no configuration identity is validated. The
test hides this mismatch by fabricating records with a `config` dictionary that
the runner never emits.

The same pair validator omits the emitted `source_hashes`, validation-bank
identity, and training-support identity, despite the S2 requirement to bind
source/input/support/validation identities across owners. `training_support_hash`
exists only inside each production summary, and the validator neither requires
nor compares it. Thus a cross-owner pair can pass with mismatched current source,
validation q/bank identity or support while sharing only input IDs and batch
digests.

Required correction: make the validator consume the actual owner schema and
require finite/typed identities. At minimum compare exact `config_hash`,
`input_ids`, `source_hashes`, `bank` (selected/candidate/q/record hashes and row
count), production training-support hash, shared initial digest, seed/opposite
modes, and all 16000 batch digests. Add mutation tests for every actual field;
do not fabricate a parallel `config` field.

### 3. The prespecified two-seed curvature screen and useful-learning guards are absent

The plan freezes a descriptive curvature screen: `abs(mean C)>=1pp` and the
same sign in both pairs. `aggregate_all` lines 216–220 reports values, mean and
range only; it never calculates the materiality threshold, same-sign condition,
or screen result. No literal test covers boundary equality, opposite signs or
the combined screen.

The plan also requires every positive paired Q gap at a reported stage to be
accompanied by the paired mean KL gap and challenge-Q gap, with `mixed` labeling
when KL is worse by more than .02 nat or challenge Q is worse by more than 2 pp.
No source function or test computes these fixed stagewise paired summaries or
their exact inclusive/exclusive margins. `fragility_flags` is a different
single-model absolute diagnostic and cannot substitute for the paired
useful-learning guard.

Required correction: add pure aggregation over the exact ordered two seeds and
13 stages. It must retain per-seed Q/KL/challenge gaps, calculate equal-seed means,
label only positive mean-Q stages according to the frozen `>.02` and `>2pp`
rules, and expose both raw and guarded interpretation without suppressing
negative/curved stages. Extend the two-seed contrast summary with the exact
material/same-sign screen. Tests must cover exact boundary values, each guard
independently, both signs, opposite signs and `abs(mean C)==1`.

### 4. Common-quality pair tables are not completed by the pure aggregation seam

Single-model milestone extraction and `milestone_comparison` are individually
coherent, but `aggregate_all` accepts arbitrary `{seed, contrast_pp}` records and
does not require or produce the two fixed threshold comparisons for both seeds.
It therefore cannot guarantee that the final two-seed result retains all
observed/censored/anomalous 30% and 38.198% pair outcomes, as required by the
plan; a caller may omit them entirely and still obtain an accepted aggregate.

Required correction: require the exact ordered seed records to contain both
tolerant milestones (with exact-threshold sensitivity retained separately),
derive/validate per-threshold paired comparisons, and emit all two seed rows
without a completer-only summary. Literal tests must include observed, censored,
final-unconfirmed and initial-anomaly cases for each fixed milestone. This is a
pure result-contract correction, not a request for a new cross-owner execution
framework; Astra may continue to own launch order and the resource gate.

## Accepted static portions

The following portions are scientifically and structurally consistent in this
version, subject to later authorized execution:

- exact two-seed, 16000-update and 13-point constants preserve the five requested
  fractions of the original 8000 denominator;
- Q plateau uses only the exact 2k subgrid, correct three-point M and 4k-separated
  G, terminal suffix confirmation, temporary rebound, censoring and deterioration;
- CE plateau requires exact updates 1..16000, finite CE, literal 100-update
  blocks, 2k means, positive denominators, relative gain and the same suffix rule;
- milestone thresholds, adjacent confirmation, irregular lag, intervals,
  initial anomaly, isolated passes and final-unconfirmed handling match v3;
- the owner begins before metadata/load/runtime/model/training/scoring work and
  uses accepted paired models, optimizer, map-balanced sampler,
  `scheduled_training(validation=None)`, evaluator and serializer seams;
- all saved 100-step checkpoints are walked in sequence from the initial file
  digest, scoring restores only fixed saved checkpoints, and the final digest is
  compared with the trainer return;
- metadata comes from named COMPLETE retained owners; no prepared JSON or
  final-test payload is opened by the runner; validation q/order, selected hash,
  bank hashes and canonical map bytes are retained;
- score files keep raw proper/route outcomes once, while result/index use compact
  hashed references compatible with the driver's COMPLETE validator;
- the actual short fixture uses both modes, routine and challenge problems, the
  accepted trainer/checkpoint restore/evaluator/serializer/owner path, and a
  production-inaccessible two-endpoint schedule;
- endpoint-write, final-manifest and checkpoint-identity failures remain inside
  one owner and are specified to retain one charge plus durable failure evidence;
- cross-owner execution order and the objective second-pair resource gate remain
  appropriately in Astra/driver orchestration rather than a new runner framework.

## Non-blocking test observation

The actual S2 fixture spies on final-test loaders and source inspection confirms
no `_prepared_ids`, prepared-payload or final-test call. It does not separately
spy on `_prepared_ids`, but the reviewed runner has no reference to that symbol.
Adding such a negative spy would strengthen regression evidence; it is not a
separate blocker once the four required scientific corrections above are made.

No smoke, suite or production is authorized. Terra should make one bounded
science-only correction to `study.py` and its scientific tests; the accepted
driver and its tests must remain frozen. A new exact static review is required
before any runtime.
