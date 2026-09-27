# Early-learning production runtime evidence 003

Date: 2026-09-27. This records the four authorized sequential inference owners
and one authorized stage-D audit. All execution used the reviewed driver and
the `.venv/bin/python` runtime. This is runtime evidence for Sol's results
review, not a scientific acceptance or population-level inference.

## Authority and source bindings

- Sol exact implementation review:
  `reviews/06-implementation.md`, SHA-256
  `da7c0d8851a8682b640a41f0f6b48f5b89916e486599df623b8db30fb50174da`.
- Astra production acceptance:
  `production-acceptance.json`, SHA-256
  `f265dc796a6d819b1f74182861a5fe2d89be3b905b0b1d3877638d8d2d356caf`.
  The acceptance binds the review above and the exact 25-entry source map.
- Every production/audit decision below binds the same current 25-entry source
  map and its creation-time ledger EOF. The full maps are retained in each
  decision JSON. Critical identities: command
  `4dd38b42996cd6963814bf13d249e00c484f33b301afc49ed5e2ead115817841`, study
  `2b1c7ad3baf31e0956ec33b572e5ae2cb202bbb85be051b3ef4198896d050fd5`, tests
  `feee0a7421699ee164cb7327cdc7652015fe94b9117c0d0b1f01e769eb2b2476`, and
  inventory `0ccf9c4ae4201d8ccbe9037785a2efc2eb4b9b9246bc7fdbec8fd09d2d769d5b`.
- Historical ledger remained unchanged at SHA-256
  `ddfe5b2df043d940b1dcbf30ed367483abac1a5935863d123a1e9c6267229da2`.

## Fixed-order owners

| Owner | Decision SHA-256 | Input ledger EOF | Owner attempt UUID / seconds | External driver charge / seconds | Driver session / PID | Child PID/PGID | Manifest SHA-256 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 2201 softmax | `4151e2d1aa32a6734e80efca3c49e2aa4167e13c61a154ef8bea72f93526e325` | `8465ae6b744276e358579e9ccb05d9b4d75d24bef82abb4bc2b8d4dbfd26dc48` | `4f05111b-ec01-4f53-b496-97fca215b9a1` / 185.61877333396114 | 186.11553408298641 | `driver-be011105-c441-4003-9174-e4e7116ef679` / 62446 | 62447 | `6ce0a9f144c506f69aba89108637fc84cc546c7a0b8dc93723fa9fd06db399bf` |
| 2201 SA | `ee0bc0bbcd099d9a9e51964e889960e113012ba73736435d642a81db0e54e9e7` | `c615a3432e8e1613b08e2e945d9863924b5f2918be3ebc295f1f9c6ea4cf93be` | `2e7ffccb-ebe7-4e7f-b10d-b12787d85eb8` / 220.82609583390877 | 221.32878824998625 | `driver-8da4c100-05a8-4d64-b9b5-458d4b623122` / 63116 | 63119 | `29f91ad7735b145f5c50197db5aa75c1e0083c4d6a516f4088c7245907159f6c` |
| 2202 SA | `9a495086971c495480f9a731499a6b4780d127bd178f339375b1b407e9fe79c3` | `03a8ab530f25f9918e2aa96f58b0ed49bf3967ddfdf0fd770e0cb9248d8b4caf` | `b14024e8-58f2-4fa0-8e9f-8ae4a6531e3a` / 223.19162120809779 | 223.92598333396018 | `driver-9e00b2ee-3914-4e7e-a901-51c78a9df77e` / 63865 | 63867 | `6fa8c027504b4f523f0443582e2b53dba3ed188b3314a77eacc0becd97c03971` |
| 2202 softmax | `b8b072dceec4b66071d1e516e6162ac6b9c2068449513aaed96b3280fbd708d4` | `1aefd587c5bd079968bb9f820920cb9527ebc4bd74767aa3cdab4e73ecb97df6` | `96102301-07ce-4796-97ac-d728740a181a` / 187.99353995802812 | 188.71107666706666 | `driver-a616a63c-5ee1-4d84-9091-8449d32fc229` / 64606 | 64608 | `14e70c0b02cbc27fea87c04daadb3f8fd6e636d2bde22365ac8a0e3d19dcaedf` |

Each owner command was `.venv/bin/python -m execution.early_learning.command --decision <decision JSON>`, using the correspondingly named decision in `attempts/`. All four owner results, indices, manifests, and `attempt.json` files report COMPLETE; the owner charge UUID and amount match the ledger row. Each driver terminal reports COMPLETE, child exit code 0, no timeout, cleanup verified true, and external charge within its 300/360-second envelope. Cleanup evidence records `killpg_zero_esrch` twice for each listed child PGID. No retry occurred; owners ran only in the prescribed order.

The append-only ledger's four `attempt_charge` rows carry status
`FINALIZATION_UNCERTAIN`. This is the accepted `OwnedAttempt.finalize`
pre-finalization charge record: it is appended before terminal/artifact
finalization and is not rewritten. For each row, the exact same UUID and amount
appear in the subsequent durable owner `attempt.json` with status COMPLETE,
and the driver independently verifies the owner charge identity, amount,
result/index/manifest and COMPLETE terminal. Sol is asked to verify this
expected status distinction during results review; the original ledger rows
remain untouched. The four separate external-overhead rows are present with
status ACCOUNTED and their preassigned driver UUIDs.

## Paired audit

- Command: `.venv/bin/python -m execution.early_learning.command --decision execution/early_learning/attempts/decision-audit.json`.
- Decision SHA-256:
  `e029c8e663237a8ab67985bf81694d3d122c9dfb87c555290e23bfc57c4098b9`;
  input ledger EOF
  `16f721802e595be126033dfed503d2746543b1b73ae2c4530d9be75240435e63`.
- Audit session: `driver-audit-5a562bb0-ae9f-4864-93e4-0b33af929fbb`.
- Audit terminal: COMPLETE, charge UUID
  `847f7e2c-60ad-4a20-837f-1842baa58469`, charged/external
  `3.9114650001283735` seconds, cleanup verified true. Cleanup evidence reports
  process group 65335 absent twice.
- Output `attempts/final-paired-summary.json`, SHA-256
  `c2091f89171a8ab2aa3f3733c33234ec7f05ad92cb288cd7026384d857a394ba`;
  audit terminal contains the same summary hash. D-stage ledger charge is
  COMPLETE.

## Final accounting and stop state

- Final fresh-ledger SHA-256:
  `0f4968676d291b5087c23eb2726bd9775f15e2e0bd18eff2fc6472a2df108551`.
- Historical ledger remains at its original bound SHA above.
- External B charges sum to `820.0813823339995` seconds; owner B charges sum to
  `817.6300303339958` seconds. D charged `3.9114650001283735` seconds. These
  are within the fresh stage-B 1,440-second and stage-D 240-second envelopes.
- No `driver.lock` remains. All four owner and audit source artifacts are
  preserved. No training, final-test, new seed, calibration, tuning or 200k
  continuation was run. Sol's independent results review is the next gate;
  the results are not represented as scientifically accepted here.
