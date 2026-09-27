# Early-learning bounded runtime evidence 001

Date: 2026-09-27. This records the only authorized stage-A checks after Sol's
static PASS. The fresh early-learning ledger is the sole ledger modified; its
allocation is zero-carry. No production scoring, training, final-test access,
or 200k work was run.

## Authority and source binding

- Static review: `reviews/04-static-final.md`, SHA-256
  `3e20ce123e807b82feb8d3cf69fc18746cb95ddd153ccb938d156280520d96e4`.
- Historical ledger SHA-256 before and after checks:
  `ddfe5b2df043d940b1dcbf30ed367483abac1a5935863d123a1e9c6267229da2`.
- Fresh ledger allocation row: zero carried-budget debit; fresh cap A/B/C/D
  = 120/1,440/0/240 seconds; global 1,800 seconds.
- Both decision JSON files bind all 25 source hashes, identical to the 25-entry
  inventory in the static review. Decisions: `attempts/decision-smoke.json`
  (SHA-256 `2397dee6f94cded2f981fc781850b5d583bdd2ebf1ca6124162f0aee895fc2fa`)
  and `attempts/decision-suite.json` (SHA-256
  `d8ac36a3d7ec4932b342ed558ea7ce9d967abcfae549576092cf7d85e89e787f`). The
  bound source hashes include command `4dd38b42996cd6963814bf13d249e00c484f33b301afc49ed5e2ead115817841`,
  study `251cf73e83cc7455bc4ad54f62661e96dc3e27b8220422bff2ee9b2725060a59`,
  tests `feee0a7421699ee164cb7327cdc7652015fe94b9117c0d0b1f01e769eb2b2476`,
  and inventory `0ccf9c4ae4201d8ccbe9037785a2efc2eb4b9b9246bc7fdbec8fd09d2d769d5b`.
- Smoke bound ledger EOF:
  `17fb8a444af66bf66fe069fc5108eb5cd97a1b6649f834d280e5a26a74e628ae`.
  Suite was created only after smoke accounting and bound the resulting EOF:
  `0e2fbc0002244c0aeb97aee45d33af450bba7010b85b74d0bc10193f03255e44`.

## Smoke

Command: `.venv/bin/python -m execution.early_learning.command --decision execution/early_learning/attempts/decision-smoke.json`

- Driver exit: 0. Pytest: `1 passed in 0.03s`.
- Session: `attempts/driver-check-9125be6e-8e88-43c7-a215-0096e615d265`.
- Terminal: `COMPLETE`, charge entry `e79aa2dd-8de1-437d-bcd7-efb4bc2d40ec`,
  charged/external `1.1512382079381496` seconds, cleanup verified true.
- Cleanup evidence recorded `killpg_zero_esrch`, process group 59834 absent
  (two observations). The reservation was released.

## Targeted suite

Command: `.venv/bin/python -m execution.early_learning.command --decision execution/early_learning/attempts/decision-suite.json`

- Driver exit: 1; no retry was attempted.
- Session: `attempts/driver-check-c1b3a7c0-e8b8-4213-8377-8237641b03fc`.
- Terminal: `FAILED`, charge entry `40502f33-f60f-4037-8889-c84e19659853`,
  charged/external `8.805580249987543` seconds, cleanup verified true.
- Pytest result: 1 failed, 15 passed in 7.56s. The failure was
  `test_statewise_weighting_argmax_and_transition_partition`: a `NameError`
  at `study.py:251` (`row` referenced in a generator whose loop variable is
  `a, b`). Driver traceback ends with `RuntimeError: bounded acceptance check
  failed`.
- Cleanup evidence recorded `killpg_zero_esrch`, process group 59912 absent
  (two observations). The reservation is absent after accounted failure and
  verified cleanup; terminal and charge evidence remain durable.

## Ledger and stop state

Fresh ledger SHA-256 after the checks:
`d21a4cb767c7c6e7790e118a695b9150881a7aa4c9443d817e0b0a24a262280e`.
Recorded stage-A charges total `9.956818457925693` seconds, within the
120-second cap. Historical ledger remains unchanged at its bound SHA. No driver
reservation lock remains. Per the stop-on-failure instruction, the source is
unchanged after the failed suite, no check was retried, and no production,
inference, audit, training, final-test, or 200k action is authorized by this
evidence.
