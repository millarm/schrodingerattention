# Productive-diversity v2 Stage 0 feasibility-results audit

## Verdict: PASS — reviewed scientific construction stop

The single authorized production command completed successfully and produced a valid `DATASET_LADDER_FAILED` result under the frozen contract. Rung A failed its fixed validation-routine length flow; rung B failed its fixed training length flow. These are declared scientific construction failures, so A correctly permitted B and B correctly ended the ladder. No challenge/test dataset, model, pilot, training, sampling, or architecture comparison was run.

The stop cannot be repaired by resampling or choosing alternate maps under this plan. It does not establish that every possible 8×8 construction is infeasible, nor does it provide evidence for or against either attention architecture.

## Immutable execution identity

- Output: `execution/next_level_v2/attempts/feasibility-001`
- Manifest SHA-256: `d8347db12a8a184f3fdec430eeef71585bbc51e5e1c66a75fb335695b61e50e3`
- Parent summary SHA-256: `17bd6459610f445e1c2d1608826f71c1f0164afcea8f720de4c16d5b71ae49ab`
- Rung A summary SHA-256: `65295a2d2a0b1726aded60b60017c92d7fed55ce9035964982d09f863bac11a4`
- Rung B summary SHA-256: `91e5d25ff0e4f3faf12f5c9c6a8084a1da9947ffd4ada29331eff4b4fa654078`
- Attempt record SHA-256: `8011a1eea138bd1ef4a61b31fe0ad8fe737b2f95b84a0230e7d02cde64dbc6d4`
- A support file SHA-256: `336ddd6c1171612baea3768b7f4b3e751adb407a68dbf7b8ac8d54e932801d94`
- Final report reviewed: `execution/next_level_v2/final_report.md`, SHA-256 `f5e35496c438486bc721958478b48135f1dc232dec2b22670b450699dd71764d`
- Post-audit ledger SHA-256: `f2006eff541e0dfdbc0116de268379969dc1d721b3f53fa256f9f74c5129f3aa`

The attempt records argv `.venv/bin/python -m schrodinger.productive_diversity_runner --output execution/next_level_v2/attempts/feasibility-001`, PID 39095, execution status COMPLETE, no error, elapsed `266.1225631249981s`, startup allowance `2s`, and charged `268.1225631249981s`. The manifest hash in the attempt and production ledger entry matches the immutable manifest. Reported orchestration evidence establishes one process, explicit exit 0, and no relaunch.

## Independent provenance and artifact checks

- Every manifest input hash was recomputed against the current frozen protocol, plan, source, tests, specifications, and reviews; all matched.
- Every noncircular manifest output hash under the attempt directory was recomputed; all matched. The attempt-to-manifest binding also matched.
- Strict parent/rung states are coherent: A inventory/training COMPLETE then validation routine SCIENTIFIC_FAILURE; B inventory COMPLETE then training SCIENTIFIC_FAILURE; all later stages NOT_EVALUATED. Parent status is COMPLETE with no selected rung and outcome `DATASET_LADDER_FAILED`.
- A contains 1,024 inventory maps, 1,024 selected training problems on 64 maps, 21,612 supervised DAG states, 10,728 unique support signatures, and the required I/L orientation coverage. Its deterministic training-map selection was replayed exactly from the saved inventory and frozen PCG64 streams.
- B contains 768 inventory maps. Its 64-map frozen training selection was replayed exactly from saved candidates and PCG64 streams; per-map/per-length raw capacities matched the saved certificate exactly.

## Independent flow-certificate replay

| Rung/gate | Required | Replayed maximum flow | Decisive long-length evidence |
|---|---:|---:|---|
| A validation routine | 384 | 378 | length 14 requires 42; selected maps contain only 36 eligible pairs; all 36 are allocated |
| B training | 1,024 | 784 | lengths 16/17/18 each require 93; raw availability is 80/42/20 and constrained-flow allocation is 37/2/0 |

The saved deterministic residual flow was independently recomputed from each saved capacity matrix and quota vector and matched exactly. A’s other length quotas are fully allocated. B’s length 8–15 quotas are fully allocated; competition for each map’s 16 slots prevents simultaneous use of all raw long-length candidates.

For A, the saved failure certificate identifies 24 validation-routine maps, excludes all 64 training identities, and each selected map was independently shown to contain at least 16 routine-eligible pairs by enumerating only until the sixteenth qualifying pair. This establishes feasibility of the selected maps and validates the reported capacities sufficiently for the flow replay.

## Explicit verification limits

I did not regenerate either finite pool, rerun frozen selection, search alternative maps, or enumerate routine eligibility for every unused A inventory map. Consequently, I do not claim a second full replay of the entire A held-out eligibility permutation. Exact all-map replay would add substantial route enumeration without changing the saved selected-map shortage certificate. The reviewed code hashes, full manifest hashes, exact A training/B training selection replays, bounded selected-map eligibility check, and deterministic flow replays support the reported outcome. This limitation does not license reselection within the frozen experiment.

Challenge eligibility, final held-out construction, baseline learnability, power, quality, productive diversity, matched softmax comparisons, and dt0 effects remain **NOT_EVALUATED**.

## Independent audit command and charge

The read-only audit returned explicit exit code 0 in full wall `2.3918795s`. It performed manifest/input/output hashing, exact A training and B training selection checks, saved-capacity flow replay, B raw-capacity reconstruction, and bounded A selected-map routine eligibility. No command yielded or was relaunched. With the conservative `2s` audit startup allowance, ledger entry `dd492f42-62cb-4e8b-902a-f8f33550b289` charges `4.3918795s` exactly once.

Post-audit conservative debit is **443.38451900200795s**, including the separately disclosed 150-second historical allowance. This remains below both the 900-second Stage 0 ceiling and 7,200-second global ceiling.

## Final-report check

The frozen-construction shortages, NOT_EVALUATED stages, and narrow interpretation in `final_report.md` are factually correct. Before closeout, Astra should change its status from “independent results audit pending” to passed and replace the pre-review debit with the post-audit value above. Those documentation updates do not alter raw results.
