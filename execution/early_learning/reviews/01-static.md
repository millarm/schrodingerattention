# Block 1 independent static implementation safety review

2026-09-27. Reviewer: GPT-6 Sol. Verdict: **CHANGES REQUIRED** for this exact version. The implementation is not yet ready for the 10-second smoke and 60-second targeted suite. I did not import the neural modules, run tests, score checkpoints, initialize the new ledger, or touch the 200,000-update hold.

## Exact `command.authority_hashes()` inventory

The values below were computed by a read-only standard SHA-256 command from the exact files named in `command.py:76-96`.

| Key | SHA-256 |
| --- | --- |
| command | `216a6423c2d2f1e4bd28c8e26d5885cc7e0bc96fd41f049fb16d0a880c869588` |
| study | `f25da978a21d2576a0fc47300b84624aa1eb6392fda58c59a85422ba9fbf373c` |
| tests | `39a54b13710c6769abaf9f308d1042e8c021335ca23fcd5224a678848d54dc90` |
| inventory | `0ccf9c4ae4201d8ccbe9037785a2efc2eb4b9b9246bc7fdbec8fd09d2d769d5b` |
| plan | `fcfc12a9a250a85391259cbff3bd2bd62a8a429e8b0a1615944ad40682f9be5f` |
| spec | `b0bf16e0caaf1407fd72c148622b73826f998885fb124be77da24cdd88be90cc` |
| methodology_review | `c4f796a0333a7d28c33508507595a81fe07c26af9fd763f57c446ca038b2a113` |
| methodology_acceptance | `694caa52e7a762acdae645cebe869f9cd9b2f6b95895851bd1efd21c1945c0db` |
| research_refocus | `05b11395c7c0fd518cd80672ed1835aed1555102c090a74cfe4ff43023ff41b0` |
| protocol | `983a63fd480510994721d980ee866f08e3cba6b767fcbadd5cef7491d437d1c5` |
| accepted_driver | `e228b53fb52f3a944e6e523e9ce3340c5abb3c02cc16ad2e07729972b1877d84` |
| watchdog | `ad5e3030ce148283c2576fa5fb376c512a8f7474bcc5e62e8e2d4e6d749900b2` |
| accepted_model | `95cb7463693c7ac696d9034eaf16a155c0363f38e819cbe56c00408d49b170c4` |
| accepted_experiment | `10cfc1a9a5e21856fd4e80f7c81b7b9243c104d452f10fc2a0062d4b4998036b` |
| accepted_data | `676b8de313fb9c667497b307704b21f137ac55a18e1e19c81be399d3f02e4bb7` |
| accepted_evaluation | `fd5cd438e0fbd103857933418008a7c5936b379488857ac6bfa7370aa8ad18ec` |
| accepted_metrics | `a471ae2c40973cb15584f924061b3ace24ef5af3b1e31702b79056055f317e34` |
| attention | `e1ce15be10caf4b2165191f9835256602f4f7b8bd11bffa94f676eac40b0fd6a` |
| feasibility | `da36b0150c0b255b7e5482d7dc016505054d9632c8fb3a21d06c2d201bfedbf4` |

## Required bounded corrections

1. `tests/test_early_learning.py:97-104` constructs a one-checkpoint entry and `training={}` but expects `_audit_checkpoints` to reach a checkpoint-file hash error. The function reads `result["input_ids"]["frozen_source_hash"]` and `result["training"]["initial_hash"]` at `study.py:261-263` and requires the full 31-point grid before opening a file. This test fails for the wrong reason. Supply the minimal valid full-grid metadata and replace only one expected checkpoint hash, or exercise an earlier hash verifier directly.
2. The composed fixture scores `validation.problems[:2]` (`study.py:348`) while the first two retained validation problems are both routine (verified from original `score-0.json`). `evaluate_rollouts` therefore has no challenge stratum, yet the new-cell path reads `rollout["strata"]["challenge"]["Q"]` (`study.py:446-449`), producing `KeyError`. Use a tiny private panel with at least one routine and one challenge problem, and a tiny proper bank with both strata. Preserve the production 512/1,024 panel unchanged.
3. `command.py:293-343` starts an external pytest child without installing the driver's SIGTERM-to-exception handler; only the production branch installs it at line 539. If the driver is interrupted in the background, its process may exit while its separately grouped child persists outside the watchdog cleanup path. Install the handler before either watchdog call and add one targeted interrupted/timeout descendant cleanup assertion using the accepted watchdog fixture; no broad test suite is needed.
4. In `_run_check`, a ledger append that reaches disk but reports a later failure leaves `accounted=False`; the exception path at `command.py:318-326` writes a new charge with a new UUID. A successful second append can double charge and release the lock on `accounted=True`. The analogous `inference_audit` exception path at lines 417-425 can do the same. Use one preassigned charge identity per external attempt, reconcile the ledger after uncertain append, and never mark accounting resolved or release a reservation when uniqueness cannot be proven. Apply the same certainty rule to owner overhead/fallback reconciliation where needed.
5. `make_owner_decision` and `make_audit_decision` hardcode `astra_accepted: True` (`command.py:251`, `284`); `_review_ok` then treats that self-asserted field as Astra acceptance (`command.py:185-186`). Bind production/audit authority to a distinct exact-version Astra acceptance artifact or verified decision that names the implementation review and current hashes. The methodology acceptance artifact is for the earlier planning gate and does not satisfy this later gate.
6. The targeted suite lacks a tiny mechanism-probe path. Its only composed inference fixture is a softmax checkpoint at update 100, while probes apply only to SA at seven fixed updates. Add a tiny SA probe fixture or focused accepted probe call with a few candidates, checking finite numerical fields, expected record counts, and no model mutation under inference mode. Keep it within the 60-second suite; the production 128-state panel remains untouched.
7. `_run_audit` executes its entire D-stage audit in the driver process (`command.py:346-438`) with no timer or external watchdog. It checks elapsed time only after summary construction at lines 405-407. A stalled or simply slow audit can exceed its 240-second envelope and the hard 1,800-second allocation before the check runs. Put the audit work under a real external deadline that includes finalization, and retain its durable failure charge and reservation if completion is uncertain.

## Findings that do not block repair scope

The source module is standard-library only until its authenticated, externally bounded study child starts. The study calls `configure_runtime()` for two CPU threads and uses `torch.inference_mode()` around model scoring and probes. I found no optimizer, backward, `train_step`, `scheduled_training`, final-test loader, or checkpoint mutation in the new path. Inventory entries bind all 31 checkpoint hashes for each owner; the owned audit validates the 100-update parent chain, and score reuse checks checkpoint and raw-metric lineage. The 31-point means/slopes, sampled ties and descriptive paired spreads follow the reviewed methodology. The resource caps, zero carry, fixed order and two-GiB gate are present. Runtime cleanup, charge certainty and duration remain unverified until the corrections above and bounded checks pass.

DRIVER_REVIEW_VERDICT: CHANGES REQUIRED
