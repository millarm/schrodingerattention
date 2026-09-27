# Early-learning final results and provenance review

2026-09-27. Reviewer: GPT-6 Sol. **Verdict: PASS for the bounded descriptive results at the exact hashes below.** This is a read-only scientific/results audit; I did not rerun inference, import neural code, train, or modify the report/source/ledger.

## Exact authority and output identities

`results.md` SHA-256: `9f8681ff4c4fde64ab36f5e1d842f72a7e7f5d54b13a79b7bb8088b7e9924a9e`. `runtime-evidence-003.md` SHA-256: `372bfc794d4b42f854885ae0ac5d1be961b72502e9dc21e3919a15e41f8533ba`. `attempts/final-paired-summary.json` SHA-256: `c2091f89171a8ab2aa3f3733c33234ec7f05ad92cb288cd7026384d857a394ba`. `reviews/06-implementation.md` SHA-256: `da7c0d8851a8682b640a41f0f6b48f5b89916e486599df623b8db30fb50174da`. `production-acceptance.json` SHA-256: `f265dc796a6d819b1f74182861a5fe2d89be3b905b0b1d3877638d8d2d356caf`. The acceptance binds that implementation review and this exact 25-entry source map, which matches every owner/audit decision and the final summary:

| Source key | SHA-256 |
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

## Four-owner and D provenance

The fixed order is 2201 softmax, 2201 SA, 2202 SA, 2202 softmax. Their decision SHA-256 values respectively are `4151e2d1aa32a6734e80efca3c49e2aa4167e13c61a154ef8bea72f93526e325`, `ee0bc0bbcd099d9a9e51964e889960e113012ba73736435d642a81db0e54e9e7`, `9a495086971c495480f9a731499a6b4780d127bd178f339375b1b407e9fe79c3`, and `b8b072dceec4b66071d1e516e6162ac6b9c2068449513aaed96b3280fbd708d4`. The respective output-manifest SHA-256 values are `6ce0a9f144c506f69aba89108637fc84cc546c7a0b8dc93723fa9fd06db399bf`, `29f91ad7735b145f5c50197db5aa75c1e0083c4d6a516f4088c7245907159f6c`, `6fa8c027504b4f523f0443582e2b53dba3ed188b3314a77eacc0becd97c03971`, and `14e70c0b02cbc27fea87c04daadb3f8fd6e636d2bde22365ac8a0e3d19dcaedf`. I checked each decision's creation-time ledger EOF against an actual prefix of the append-only ledger; each driver session binds its decision SHA, source map and ledger EOF. I independently checked all 124 original checkpoint file hashes against the frozen inventory, all 124 score-file hashes against their indices, and all 158 per-owner manifest entries including sizes and hashes. All four `result.json`, `index.json`, `attempt.json` and driver terminals are COMPLETE; child exits are zero, not timed out, and cleanup verified with two absent-process-group observations each. No owner retry or residual lock appears.

The four legacy `OwnedAttempt.finalize` ledger `attempt_charge` rows say `FINALIZATION_UNCERTAIN` because that provisional status is appended *before* terminal/artifact finalization and never rewritten. It cannot itself prove success. Here each unique charge UUID and exact amount matches its later COMPLETE owner `attempt.json`; each COMPLETE result/index and full manifest hashes bind the output; and the separate driver terminal independently verified that identity, child exit and cleanup, with a corresponding ACCOUNTED overhead UUID. No `FAILED_LEDGER`, `FAILED_ARTIFACT`, duplicate charge or missing owner terminal was observed. This combination resolves the provisional-label ambiguity for these four attempts without altering the ledger or treating an actual uncertain finalization as complete.

The D decision SHA-256 is `e029c8e663237a8ab67985bf81694d3d122c9dfb87c555290e23bfc57c4098b9`; it binds the post-owner ledger EOF `16f721802e595be126033dfed503d2746543b1b73ae2c4530d9be75240435e63`. Its capability session binds that decision and source map. The COMPLETE audit terminal binds the final-summary SHA above and the unique stage-D charge UUID `847f7e2c-60ad-4a20-837f-1842baa58469`; its child process group is absent in two cleanup observations. The final ledger SHA-256 is `0f4968676d291b5087c23eb2726bd9775f15e2e0bd18eff2fc6472a2df108551`; historical ledger SHA-256 remains `ddfe5b2df043d940b1dcbf30ed367483abac1a5935863d123a1e9c6267229da2`.

Stage A charged `18.360494249965996` seconds, B externally charged `820.0813823339995` seconds (including owner `817.6300303339958` plus overhead), and D charged `3.9114650001283735` seconds. The actual fresh-ledger debit is `842.3533415840939` seconds of the 1,800-second cap. Each stage is below A120/B1440/D240; there is no inherited debit.

## Independent scientific checks and interpretation

I independently recomputed, from each raw score file without running a model, the original-weight proper KL, Brier, policy/teacher entropy, and nonoptimal mass against all 124 point records; rollout/greedy Q also match. The final audit counts are exactly four owners, 124 points/greedy evaluations, 16 reused and 108 new proper/Q cells, and 14 fixed SA probes. Every owner has 31 ordered checkpoints and 31 statewise comparisons (30 adjacent plus 800→2,000); group weights, counts and additive/component closures hold to `1e-10`. The primary 800–2,000 windows have 13 points; independently recomputed means and OLS slopes match the report. Paired quantities are equal-seed, descriptive SA-minus-softmax differences, not pseudo-replicated map/checkpoint uncertainty. The report's sampled KL/Brier minima are exact and unique on the observed grid: 2201 softmax 900, 2201 SA 700, and both 2202 modes 2,600. They are not continuous or post-window minima claims.

Independently recomputing 800→2,000 from paired state rows gives ΔKL/ΔA/ΔB as reported: 2201 softmax `+0.012666610/−0.001232056/+0.013898666`; 2201 SA `−0.005512219/−0.011144586/+0.005632367`; 2202 SA `+0.026928059/+0.001964599/+0.024963460`; 2202 softmax `+0.028945014/+0.000762130/+0.028182884`. Each of the four legal-argmax transition groups' signed contributions and counts match raw states. Thus conditional-within-oracle-support divergence (the `B` component) increases in all four endpoint contrasts, whereas support-mass (`A`) changes in both directions; for 2201 SA the larger negative A outweighs positive B, yielding improved net KL. Nonoptimal mass falls in all four endpoint contrasts. These are descriptive decompositions, not evidence that architecture caused the changes or that Q gains are solely confidence artifacts. The 14 fixed-weight probe files reproduce the report's snapshot-average TV/norm/disagreement values (128 candidates each); they are not trained ablations or independent replications.

The report avoids p-values, population intervals, calibration and causal claims, correctly limits conclusions to two existing seed pairs, and does not touch final-test data. Two nonblocking wording improvements for any separately authored closeout: replace “a single listed checkpoint tie” with “a unique sampled minimum” (there is no tie), and say explicitly that ΔB rises in all four 800→2,000 contrasts while ΔA is mixed and the 2201 SA net KL improves. The existing signed component table already contains these facts, so neither wording point invalidates the frozen report or this PASS.

RESULTS_REVIEW_VERDICT: PASS
