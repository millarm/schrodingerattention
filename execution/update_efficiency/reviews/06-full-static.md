# Sol consolidated full-static safety acceptance

**Verdict: PASS for the bounded static smoke/suite gate.**

`DRIVER_REVIEW_VERDICT: PASS`

Required decision phase: `static-safety`.

This is an exact-version static acceptance. I read the frozen v3 plan/spec,
science-completion specification, corrected study, complete tests, S2/correction
handoffs, accepted trainer/evaluator interfaces, driver authority contract and
prior driver-respec PASS. I did not import project code, run tests/subprocesses,
load models/data, inspect final-test payloads or write the ledger.

This PASS permits Astra to authorize only the externally bounded 10-second smoke
and 30-second suite through the accepted driver. It is not production acceptance:
production still requires runtime evidence, exact implementation review at
`reviews/08-implementation.md`, and Astra's separate acceptance.

## Exact accepted authority inventory

The following hashes are included literally for `command.review_ok` and bind the
same dictionary returned by `command.authority_hashes()`:

- study `a62a37248421660f94edce139a7e9ca471890bab8c0ba4463edd8ffb6c396204`
- driver `3adda02c82b2eb6a059d890b967950c6718e7406e64dd99fdcfe2dab47f38b4f`
- tests `5fb793d5794836462d0b145cc0d613ef4c0c3b3f29ac28ec1c30cdd75e2378c6`
- watchdog `2b3fed56e07da5a33c122afa10e9cc5b77df0df77ec492db0bfaf4887708a8c8`
- plan `d4ce6e3c6e4c0a7eac46aa96b2a01f442abeed573c3b78e95a2edb874caca6ae`
- v3 specification `dcca6fa6c3ba0d322a8278d6003c77249c692a1224f37a3a2bad547530285a67`
- accounting clarification
  `7ab55e8e05ca950597e9c7f09c948a8edbd2756f04854d1dc19851dba82c58c6`
- decisions `77affe9064fd016e2391c0b1f6ac67a8aac9d69b4f6d7af06c36f90ee3e798c4`
- attention `e1ce15be10caf4b2165191f9835256602f4f7b8bd11bffa94f676eac40b0fd6a`
- feasibility `da36b0150c0b255b7e5482d7dc016505054d9632c8fb3a21d06c2d201bfedbf4`
- route policy `95cb7463693c7ac696d9034eaf16a155c0363f38e819cbe56c00408d49b170c4`
- route-policy data `676b8de313fb9c667497b307704b21f137ac55a18e1e19c81be399d3f02e4bb7`
- route-policy evaluator
  `fd5cd438e0fbd103857933418008a7c5936b379488857ac6bfa7370aa8ad18ec`
- route-policy experiment
  `10cfc1a9a5e21856fd4e80f7c81b7b9243c104d452f10fc2a0062d4b4998036b`
- route-policy metrics
  `a471ae2c40973cb15584f924061b3ace24ef5af3b1e31702b79056055f317e34`

Additional reviewed records:

- science-completion spec
  `fa9b05907af7399c8ca4b841d7d1217aae91b97d7d7e2f6d12cfab2aa5165364`
- corrected-science handoff
  `995d82691f2151d199c4e02110d1afbc6100853425d6a1737da07c4bb40b172e`
- driver finalization-respec PASS
  `6338e14aa23bf488178d0a441119a7db0ed550e522b1ec5ad3474f983fabc2bc`
- post-evidence ledger prefix/current SHA
  `c9141df2296464aeb129fbfbbf311e8c7d1fe86fd839edc170dc08d5b3e770cb`

The preceding designated static PASS, before the bounded runtime-fixture
correction, had SHA-256
`34ed2d8aa335605ac0246489c4491573e82a190542a13da14956308f254fb9c0`.
Its accepted scientific and integration analysis is retained below; this
version changes only the exact tests/ledger authority and records the narrow
fixture review at `reviews/07-runtime-fixture-correction.md`.
The subsequent designated PASS with that first fixture correction had SHA-256
`4730c1799c9b9046da26408ca7bb3b57a9cbc7ea512844eefe002719fd8083c4`;
the present version advances only the test authority to the separately reviewed
descendant-lifecycle fixture.

The initial CHANGES REQUIRED review is preserved as
`reviews/06-initial-changes-required.md`, SHA-256
`f1884610ebea8fc408c3b8a3972ca6b665026b2cb790d82c315d9f995e94e39a`.
Its pre-archive designated-path SHA was
`3f254f396b5dbe8588865c17ca5e26b732f5f428e6f36d3c09ad85d82ca71c59`;
the patch-based archival move changed the file bytes, so the current archival
hash above is controlling.

## Scientific estimator acceptance

The pure estimators implement the frozen v3 contract:

- exact ordered 13-point grid and finite Q/KL/Brier/teacher-entropy/challenge
  metrics;
- Q rolling means and gains on only the equally spaced 2k subgrid, terminal
  qualifying suffix, confirmation, temporary rebound, censoring and explicit
  deterioration;
- exact updates 1..16000 for sampled CE, literal 100-update block means, 2k
  means, positive denominators, relative gains and the same terminal rule;
- tolerant and exact 30%/38.198% milestones with adjacent confirmation,
  irregular confirmation lag, interval, initial anomaly, isolated passes and
  final-unconfirmed/right-censored status;
- fixed early contrast in percentage points and an exact two-seed descriptive
  screen requiring `abs(mean C)>=1` plus the same nonzero sign in both pairs;
- all 13 per-seed Q/KL/challenge gaps and equal-seed means, with raw gaps retained
  and `mixed` applied only to positive mean Q when KL is worse by more than .02
  nat or challenge Q is worse by more than 2 percentage points. The 1e-12
  comparison tolerance protects numerical equality without altering raw values;
- four complete milestone tables (tolerant/exact × 30/38.198), each retaining
  both seed rows and their observed, censored, final-unconfirmed or anomalous
  outcomes rather than a completer-only summary.

Teacher entropy is now sourced from accepted `weighted.entropy_q`; policy entropy
is separately named from `weighted.entropy_p`. Finite validation requires teacher
entropy, and the actual short fixture compares the compact teacher value with the
raw accepted proper-score value.

## Pairing and provenance acceptance

Pair validation consumes the actual owner schema rather than a parallel fixture
schema. It requires and compares:

- exact seed and opposite modes;
- shared-initial digest and all 16000 batch digests;
- `config_hash`;
- exactly the six input IDs (`prepared`, training-selected,
  validation-selected, test-selected metadata, manifest and frozen source);
- the complete current source-hash dictionary;
- validation selected/candidate/q/record hashes and positive row count; and
- training support hash.

Tests deep-copy paired scores, bind each score's canonical bytes to its compact
owner hash, and mutate every identity family including every bank field and row
count. Stage guard boundaries, curvature materiality/sign, all milestone tables,
censored outcomes and initial anomalies have literal coverage.

## Owner/trainer/evaluator integration acceptance

The runner remains a single bound owner and begins `OwnedAttempt` before retained
metadata reads, runtime setup, loaders, initialization, training, evaluation or
writes. Production admits only seeds 2201/2202, the two modes, 16000 updates and
the fixed grid; the two-endpoint injection is keyword-only and unavailable from
the CLI.

It uses unchanged accepted `paired_models`, optimizer, map-balanced sampler and
`scheduled_training(validation=None)`, then walks every saved 100-step checkpoint
from the initial file digest. Every checkpoint binds seed, mode, source, accepted
config, input IDs, update, initial identity and preceding file digest; the final
digest is compared with the trainer return. Fixed checkpoints are restored and
scored after training using accepted full-panel T1/K32 split-1/replicate-0
rollouts and the exact-q proper bank.

The named COMPLETE metadata owners and frozen hashes are checked without opening
prepared JSON or a final-test payload. Rebuilt validation rows match retained
canonical/map/family/goal/current/q values in exact order, and bank/support/source
identities are persisted. Raw proper and route bags occur once per score file;
result/index contain compact hashed references compatible with driver closure.

The actual short fixture covers both modes, accepted real train/checkpoint
restore/evaluator/serializer/owner behavior, routine and challenge strata,
initial→update1→update2 parent hashes, exact endpoint count, raw/compact hash
binding, teacher/raw equality, one charge per owner, and an untouched final-test
loader spy. Endpoint-write, final-manifest and checkpoint-identity mutations are
specified to produce one charged durable failed owner with partial/failure
evidence and no false COMPLETE.

## Scope and next gate

No cross-owner launch framework was added. Astra retains fixed owner order and
the objective resource-only second-pair gate. No final-test, temperature search,
adaptive early stop, extra seed, post-result endpoint or budget extension is
authorized.

The smoke evidence passed. After the retained EPERM outcomes and the separately
reviewed proof-preserving lifecycle fixture in
`reviews/07c-lifecycle-fixture.md`, the exact corrected version is safe to enter
one normal-tool-scope, externally bounded 30-second suite attempt within stage
A. If descendant cleanup remains unproved, execution stops as a capability
blocker. This attempt remains evidence to inspect, not production authorization.
Any further
source/test/authority change invalidates this static acceptance and requires a
new exact review.
