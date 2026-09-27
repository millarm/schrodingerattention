# Bounded runtime NameError repair: static review

2026-09-27. Reviewer: GPT-6 Sol. **Verdict: PASS** for the exact corrected version below. The one-expression repair is safe to take through **one** fresh, externally bounded 60-second targeted-suite rerun after Astra acceptance. The successful smoke must not be repeated. This is not an implementation/evidence PASS or production authority. No tests, neural imports, inference, training, or ledger writes occurred in this review.

## Exact source and repair authority

I independently recomputed all 25 entries in `command.authority_hashes()` with a read-only SHA-256 command. Every digest below is 64 hexadecimal characters.

| Key | SHA-256 |
| --- | --- |
| command | `4dd38b42996cd6963814bf13d249e00c484f33b301afc49ed5e2ead115817841` |
| study | `2b1c7ad3baf31e0956ec33b572e5ae2cb202bbb85be051b3ef4198896d050fd5` |
| tests | `feee0a7421699ee164cb7327cdc7652015fe94b9117c0d0b1f01e769eb2b2476` |
| inventory | `0ccf9c4ae4201d8ccbe9037785a2efc2eb4b9b9246bc7fdbec8fd09d2d769d5b` |
| plan | `fcfc12a9a250a85391259cbff3bd2bd62a8a429e8b0a1615944ad40682f9be5f` |
| spec | `b0bf16e0caaf1407fd72c148622b73826f998885fb124be77da24cdd88be90cc` |
| methodology_review | `c4f796a0333a7d28c33508507595a81fe07c26af9fd763f57c446ca038b2a113` |
| methodology_acceptance | `694caa52e7a762acdae645cebe869f9cd9b2f6b95895851bd1efd21c1945c0db` |
| amendment | `51563625cc2b171f4e70757fbe05eb8cacf050ab1f47e9d3b07eeae790490842` |
| amendment_spec | `2aef1209f183b1b702fae8d353d328fe02aeaa0fd7bc449385d651aebe83b4da` |
| amendment_methodology_review | `6ead804a56dbd23f4b3e797984108c4f7d8c931785b4980dd5962f30a4942959` |
| amendment_acceptance | `e84d5ecca402da7970eef6429c9dee9c029d47b201b443c16562348baa34e812` |
| final_correction_spec | `3433ac04e2f91c2711ed5f66f3fc9af1ebaeb7a4b0d8f8a9239b98a98dd80ac9` |
| final_correction_review | `e31002f2845636ad9ee8672c5f80c088b1ca19883b7e2c2cea7f1ab963198715` |
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

The repair specification `spec-04-runtime-name-resolution.md` hashes to `85b098f095abd0e4a968b409fe2fda250c6fea7a07cf6b264adf389548f1cc4f`; `runtime-evidence-001.md` hashes to `54cce71aba1f9bec66e5be2641d18ab8848096f960a5687dcdb2a0db44d4cc14`. These two records are separately bound here; the current driver authority inventory remains the 25 entries above. The previous static review `04-static-final.md` hashes to `3e20ce123e807b82feb8d3cf69fc18746cb95ddd153ccb938d156280520d96e4`.

## Repair and failed-attempt evidence

The failed suite's traceback identifies `study.py:251`: `row["weight"]` inside a generator binding `(a,b)` and no `row`. The corrected expression is `a["weight"]*(b[component]-a[component])`. `statewise_transitions` already verifies paired state identity, q, legal mask and weight before this sum, so this uses the frozen earlier-state weight without changing the scientific formula. The command, tests, inventory, accepted dependencies and prior authority documents have unchanged hashes. No other runtime defect is evidenced by the first suite's result: 15 tests passed, one failed on this NameError.

The smoke's terminal is COMPLETE with `1.1512382079381496` seconds charged to A and verified cleanup. The suite's terminal is FAILED with `8.805580249987543` seconds charged to A; its cleanup evidence twice records the owned process group absent. The two ledger charge UUIDs match their respective terminal records and are unique. The new ledger EOF is `d21a4cb767c7c6e7790e118a695b9150881a7aa4c9443d817e0b0a24a262280e`, with A charges totaling about `9.956818457925693` seconds; the historical ledger remains at its frozen SHA. The driver reservation lock is absent. The original failed suite decision binds the previous study hash and ledger EOF, so it cannot authorize a rerun. A new decision must bind the corrected 25-source inventory, this review hash, and the fresh ledger EOF.

One bounded 60-second suite remains feasible within A120, with more than 110 seconds unspent before that attempt. A successful rerun still needs independently reviewed results and exact-version Astra acceptance before production.

DRIVER_REVIEW_VERDICT: PASS
