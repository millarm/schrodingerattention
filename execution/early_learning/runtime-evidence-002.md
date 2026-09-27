# Early-learning bounded runtime evidence 002

Date: 2026-09-27. This records the single targeted-suite attempt authorized
after the name-resolution correction. It supersedes neither the earlier smoke
nor the failed first suite; all three records remain preserved. No production,
audit, training, final-test or 200k activity occurred.

## Exact bindings

- Sol repair static review:
  `reviews/05-runtime-repair-static.md`, SHA-256
  `a2ce7b1ae548ab10c5a9c7bc1ce8b236e9ec3cbbf397eff3d6a90ce003a3f74b`.
- Repair spec `spec-04-runtime-name-resolution.md`, SHA-256
  `85b098f095abd0e4a968b409fe2fda250c6fea7a07cf6b264adf389548f1cc4f`.
- Corrected `study.py` SHA-256
  `2b1c7ad3baf31e0956ec33b572e5ae2cb202bbb85be051b3ef4198896d050fd5`.
- Decision: `attempts/decision-suite-repair.json`, SHA-256
  `b4bc7e7263782a6489d596d3de980f6c34b01d4a61743df899c71f55b96b7600`.
  It bound the current 25-entry source inventory, including command
  `4dd38b42996cd6963814bf13d249e00c484f33b301afc49ed5e2ead115817841`,
  study `2b1c7ad3baf31e0956ec33b572e5ae2cb202bbb85be051b3ef4198896d050fd5`,
  tests `feee0a7421699ee164cb7327cdc7652015fe94b9117c0d0b1f01e769eb2b2476`,
  and inventory `0ccf9c4ae4201d8ccbe9037785a2efc2eb4b9b9246bc7fdbec8fd09d2d769d5b`.
- Fresh ledger EOF at decision creation:
  `d21a4cb767c7c6e7790e118a695b9150881a7aa4c9443d817e0b0a24a262280e`.
- Historical ledger SHA-256 remained the bound
  `ddfe5b2df043d940b1dcbf30ed367483abac1a5935863d123a1e9c6267229da2`.

## One authorized targeted-suite attempt

Command: `.venv/bin/python -m execution.early_learning.command --decision execution/early_learning/attempts/decision-suite-repair.json`

- Driver exit: 0. Pytest result: `16 passed in 7.17s`.
- Session: `attempts/driver-check-1ada5aa9-55d2-4e5a-91d6-36c48056aec5`.
- Terminal: `COMPLETE`; charge entry
  `99645469-ddc8-4c1e-a92f-f343453bbef6`; charged/external
  `8.403675792040303` seconds; `cleanup_verified: true`.
- Cleanup evidence records `killpg_zero_esrch`, process group 61565 absent
  (two observations). The driver reservation lock was released and is absent.
- New early-learning ledger SHA-256:
  `8465ae6b744276e358579e9ccb05d9b4d75d24bef82abb4bc2b8d4dbfd26dc48`.

Stage A's three charges (successful smoke, failed first suite, successful
repair suite) total `18.360494249965996` seconds of the 120-second cap. The
first failed suite and its durable evidence were preserved unchanged. This
successful suite does not authorize production: next gate is Sol's exact
implementation/evidence review and a distinct Astra acceptance. No retry or
other action is authorized by this record.
