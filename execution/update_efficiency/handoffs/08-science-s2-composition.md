# Science S2 handoff — owned trainer/evaluator composition

This completes the S2 composition scope in
`spec-05-science-completion.md`; it does not authorize runtime.  Historical
handoffs and the accepted driver were preserved.

## Frozen source set

- `execution/update_efficiency/study.py`:
  `b34ed709022be48ef2b02d608a8da190bff98e73a7caea6a2558ae1ba2500f15`
- `tests/test_update_efficiency.py`:
  `4b6a50617c388c76f6b9890d48eb382cd7d367ffcb12b63b75a3aeba170c4113`
- frozen `execution/update_efficiency/command.py` (unchanged):
  `3adda02c82b2eb6a059d890b967950c6718e7406e64dd99fdcfe2dab47f38b4f`
- `spec-05-science-completion.md`:
  `fa9b05907af7399c8ca4b841d7d1217aae91b97d7d7e2f6d12cfab2aa5165364`
- v3 authority: `plan-v3-saturation.md`
  `d4ce6e3c6e4c0a7eac46aa96b2a01f442abeed573c3b78e95a2edb874caca6ae`,
  `spec-03-saturation.md`
  `dcca6fa6c3ba0d322a8278d6003c77249c692a1224f37a3a2bad547530285a67`,
  and `decisions.md`
  `77affe9064fd016e2391c0b1f6ac67a8aac9d69b4f6d7af06c36f90ee3e798c4`.

`study.source_hashes()` delegates to the accepted driver's
`authority_hashes()`, so the result binds the same study, driver, tests,
plan/spec/decision and accepted-dependency byte inventory as the launcher.

## S2 implementation and literal test map

- `run` admits only the frozen seed/mode/16000/13-point production contract.
  Its private two-endpoint schedule is keyword-only and unreachable from the
  CLI.  It begins the `OwnedAttempt` before retained-metadata reads, runtime
  setup, loaders, model initialization, training, evaluation, or writes.
- The runner uses accepted `paired_models`, `optimizer`,
  `MapBalancedSampler`, and `scheduled_training(validation=None)`; it saves
  raw proper/rollout data in each one-write score endpoint and compact hashed
  endpoint references in result/index.  Production summaries retain Q/CE
  plateau, milestones, fragility, and support identity.
- The initial checkpoint payload and file digest are checked separately.  Each
  saved checkpoint is validated against the preceding digest: update 100 is
  therefore bound to the initial *file* digest, not a self-parent.  The final
  digest is also bound to the trainer's returned final checkpoint digest.
- `test_s2_actual_short_owner_training_restores_both_modes_and_exact_endpoints`
  uses a real accepted two-update train/restore/evaluate/serialize/owner path
  for both modes, with legal 144-byte routine and challenge problems.  It
  asserts exactly endpoints 0/2, actual restored identities, initial→1→2
  parent hashes, raw proper/rollout endpoint content, result/index/manifest
  hashes, one-write endpoint count, one owner charge per mode, and a final-test
  loader spy that remains untouched.  Only metadata/load boundaries are mocked;
  no production payload or test loader is opened.
- `test_s2_endpoint_write_failure_has_one_charge_and_durable_failed_owner`
  injects the final score write failure and asserts exactly one charge, durable
  `FAILED` terminal, and retained endpoint-0 evidence.
- `test_s2_final_manifest_failure_has_one_charge_and_durable_failure_evidence`
  injects accepted final-manifest failure and asserts exactly one charge,
  durable `FAILED_ARTIFACT` terminal and `finalization_error.json` without a
  false complete manifest.
- `test_s2_checkpoint_identity_mutation_is_refused_inside_one_failed_owner`
  mutates the saved final checkpoint identity before validation, asserts refusal
  inside that same owner, one charge, and a durable failed terminal.

## Scope limits and no-runtime statement

No tests, imports, subprocesses, model/data loads, training, evaluation,
smoke/suite/production command, or ledger writes were executed while making
this handoff.  The listed actual-runtime tests are static code pending Sol's
full-static gate.

The runner deliberately owns one bound mode at a time.  Cross-owner launch
order and the conditional second-pair resource gate remain Astra/driver
orchestration concerns; this S2 implementation neither infers an outcome nor
creates a retry, additional seed, or extension authority.
