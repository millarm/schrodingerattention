# Fresh paired-seed wrapper handoff

## Frozen identities

- Plan SHA-256: `b58b88ae15712bca2b027ccb1ab3fc90bef4e9b2a5d94dc8dba43d61fbcb679e`
- Wrapper SHA-256: `15e67019ac27ef24d2a138e09209db0360270b157f56f99bb3ba652729f7cd5b`
- Prepared fixture: `execution/model_training_comparison/prepare-001/prepared.json`
- Production root and ledger: `execution/model_training_comparison/` and its
  existing `ledger.jsonl`.

## Literal assertion map

`train.py` accepts only seeds `1702,1703,1704,1705`, modes `softmax` or
`schrodinger`, and exactly `8000` fresh updates; the module CLI exposes only
`--seed`, `--mode`, and `--decision`.  It validates the plan bytes and every
decision binding: approved/pilot seam permission, replication command, fresh
run kind, requested seed/mode, update count, plan/config/prepared/manifest
hashes, and the resource table.

Before installing the authorized prospective transfer it literally asserts the
accepted table `A700/B2000/C1900/D1300`, global cap `7200`, and carry
`923.003597253`; it then installs only `A700/B3500/C400/D1300`.  The original
pilot CLI and its seed-1701 guard were not edited.

The owned output is derived as `replication-SEED-MODE-8000`; `OwnedAttempt`
provides fail-if-exists and the shared root lock.  The call directly uses the
accepted paired-model, optimizer, map-balanced sampler, scheduled-training,
heldout/probe, checkpoint/evaluation cadence seams, with `resume=None`.
The result preserves the accepted provenance/input/shared-initial-digest/
parameter-count/result shape and adds separate wrapper, decision, and resource
hash/table provenance plus the actual module argv.  It verifies an owned
`attempt.json` has `COMPLETE` status before reporting success.

## Focused test evidence

The completed test command was:

` .venv/bin/python -m pytest -q tests/test_seed_replication_train.py `

It passed `12` tests in `1.03s`; the retained full tool wall was `1.9s` and
also checked module help and source/plan hashes.  Coverage includes seed 1702
and 1703 forwarding, exact mode/update and `resume=None`, rejected 1701/1706
and invalid modes, decision binding failures, actual prepared fixture binding,
literal resource/global/carry contract, output ownership naming, provenance,
and repository-local default paths.  An earlier full-wall `0.8s` failed run
found the initial default-path bug (10 passed/2 failed); it is retained as a
stage-A `FAILED` ledger row.  Both rows are append-once EOF records in
`execution/model_training_comparison/ledger.jsonl` with UTC timestamps.

No training, model inference, final-test access, or analysis ran.
