# Fresh-pair analysis handoff — correction revision

## Exact version

- `analyze.py` SHA-256: `cbf8d19b31b429a91e48ad3dba2e2079ab0245d9811c92ad9e0e851bc8ffa3dd`
- `test_seed_replication_analysis.py` SHA-256: `e86471ce240f6548cc6b438880ba9db2821dc2e2c3f2b6b4e7625da877e9e76e`
- Frozen plan SHA-256: `b58b88ae15712bca2b027ccb1ab3fc90bef4e9b2a5d94dc8dba43d61fbcb679e`
- Reviewed wrapper SHA-256: `15e67019ac27ef24d2a138e09209db0360270b157f56f99bb3ba652729f7cd5b`

## Contract coverage

`analyze.py` only accepts seeds 1702--1705 and derives each owner as
`replication-SEED-MODE-8000`.  It delegates the literal original-budget/global/
carry assertion and prospective C-to-B transfer to the frozen reviewed wrapper,
then owns `replication-SEED-analysis` at stage D and sets the bounded 120-second
alarm (the accepted owner retains its four-second allowances).

Before scoring, it requires each owner terminal `COMPLETE`, hashes every used
manifest member, checks prepared/source/config/input identities, verifies final
seed/mode/update, independently validates each initial checkpoint/state, proves
the non-null shared initial digest from shared tensors, and verifies all 8,000
paired minibatch digests.  It never invokes the old seed-1701 checkpoint helper.

Each consumed owner now also proves its persisted training authority: the exact
reviewed wrapper path/hash, frozen replication-plan bytes/hash, installed and
original resource tables plus hash, exact fresh seed/mode decision bytes/hash,
authorized module argv, and accepted prepared/source provenance.  These evidence
hashes are retained per model in the pair result.  Analysis provenance now names
and hashes every direct helper dependency, including `paired_behavior/job.py`
and `threeway_diagnosis_job.py`.

Stored full-validation event adapters are reused for 1k/2k/4k/8k, preserving
raw proper and greedy/K32 rows and event/order bindings.  The 8k output adds
per-state and per-map paired measures, greedy outcomes, valid-route raw/normalized
sets, and the fresh primary SA-minus-SM Q delta.  The retained historical
all-invalid permutation qualification is explicit.

Frozen ABC support is hash-bound to
`2bcde9c3823a41cc0a0ac7c4383ef1323658ca47b5b7a53336f4f4e2adf9babc`.
Both fresh models score all A/B/C cohorts at 8k; every rollout passes the current
seed and replicate 0, with split 0 for A/B and split 1 for C.  Cohort quality
uses routine Q (not a nonexistent A/B/C mixture).  QC consumes stored SM/SA T1
and makes exactly two new SA K32 calls, at .75 and 1.25, with fixed lower-T
tie breaking and the predeclared mixture/stratum tolerances.

## Focused test evidence

` .venv/bin/python -m pytest -q tests/test_seed_replication_analysis.py `
completed with `12 passed` in pytest `18.87s`, full retained tool wall `19.2s`.
The bounded suite now covers actual-1702 event/hex adapters, persisted authority
and checkpoint scalar/source mutation rejections, frozen 24-triplet/144-route/
768-state ABC cohort counts, both-model A/B/C assembly and every fresh-seed
rollout split, QC calls, and a composed required-output assertion.  The prior
full-wall `19.9s` run (11 passed/1 failed) corrected the literal frozen state
count from 192 to 768.  Both correction rows are append-once stage-A EOF entries;
post-correction totals are A `466.80181791697106`, B `1211.9967508759814`, C
`0`, D `263.75339900007907`, global `2865.555565046031`.

No analysis job, final-test access, selection, or additional training was run.
