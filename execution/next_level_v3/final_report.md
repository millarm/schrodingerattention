# 12×12 dataset feasibility — bounded construction failed

Status: production completed; **Sol PASS for the reviewed scientific stop** in
[review18](reviews/18-dataset-results.md). This is not a passing dataset gate.

The single frozen production run completed normally (exit0), but none of the
three predeclared proposals supplied every required split. **No complete accepted
dataset was produced, and no neural training or architecture comparison ran.**
This is failure of the frozen sampled-pool/selection construction, not proof that
a suitable12×12 dataset cannot exist.

## What was built

768 canonical maps:256 each with eight I obstacles, eight L obstacles, or four of
each. Each12×12 map has24 wall cells. Raw joint capacity passed. All12 window/quota
combinations were ranked before training-support/novelty selection; retained
windows were12–14,14–16,16–18, each with per-map length quotas6/5/5. Length variety
is three matched lengths per proposal, while spatial/compositional complexity
increases over the earlier8×8 construction. There are no neural outcomes involved
in selecting these windows.

| Route lengths | Training | Routine validation | Novel validation | Routine test | Novel test |
|---|---:|---:|---:|---:|---:|
|12–14|1024/1024|384/384|0/128|Not evaluated|Not evaluated|
|14–16|1024/1024|384/384|128/128|1536/1536|400/512|
|16–18|1024/1024|144/192 I; L not evaluated|Not evaluated|Not evaluated|Not evaluated|

Counts are committed problem pairs,16 per map. Unvisited stages are not failures
and are not presented as completed datasets. Failed prefixes and all successful
earlier stages remain saved per proposal, without selecting a favorable duplicate.

The14–16 proposal supplies meaningful but limited oracle-only evidence:8 mixed
validation maps plus25 disjoint mixed test maps—33 maps,528 pairs—satisfy the
strict per-problem novel-solution requirement against the exact all-training-
suffix support. It misses the novel-test target by7 maps/112 pairs. These are
qualifying *solution opportunities*, not generated model outputs, learned
originality, calibrated uncertainty or an attention-architecture benefit.

## Reproducibility and interpretation

The runner correction used the user-authorized Astra implementation exception;
Sol independently accepted the exact source before production in
[review17](reviews/17-astra-runner.md). Prior blockers and all old experiments
remain preserved. Accepted core data logic, seeds, quotas and novelty thresholds
were unchanged. Real-fixture35-test runner evidence is software validation, not
production feasibility evidence.

[Production process record](production_execution_record.md) preserves the one
command, live session24756 and explicit exit0. Runtime175.393054417s plus2s
startup allowance was charged once. Manifest SHA256:
`26ddf4277f1c8e3ab63505cd93c7a643c4b76bf9eaf1cf4c9705f3d629e82464`.
The output directory is [feasibility-001](attempts/feasibility-001/summary.json).
It retains pools, full inventory/ranking, proposal-stage evidence, result,
manifest and completed attempt. No timeout, relaunch, pool refill or live budget
extension occurred.

Final conservative operational debit:745.131573627s of7200s (12.42 minutes),
including historical allowances; this is not all measured new compute.
New-v3 debit301.747054625s includes the2.999554s retained arithmetic allowance.
Audit charged16.505706541s measured in-script plus3s conservative startup/inspection
allowance, within its120s cap. Remaining operational budget6454.868426373s is
unused; stopping is mandated by the scientific gate, not resource exhaustion.

The independent audit found zero errors in source/output hashes, all selected-row
metadata/counts, support hashes, cross-split disjointness, and exact re-ranking of
the saved inventory. All60 deterministically sampled route/novelty facts and32
sampled q-target states matched independent recomputation, including failed
prefixes. This is sampled oracle verification, not replay of every route fact or
regeneration of training support. Raw audit SHA256:
`f26d8fbeec322746865b41cc9712cf7cfd6bc3572918fb62afe09174caff4e60`.
[Audit evidence](audits/feasibility-001-audit.json) and [independent review18](reviews/18-dataset-results.md)
record coverage and limits. All256 mixed maps failed length12 supply in the first
proposal; the14–16 proposal rejected223 remaining mixed-test maps, predominantly
at length14. Longer16–18 lengths instead fell short of routine I-family supply.

## Decision

Stop at the predeclared dataset gate. Retain the useful partial construction, but
do not promote it to a complete benchmark or proceed to neural learning. A future
user-approved iteration could test a larger prespecified12×12 candidate pool
while preserving novelty/quality gates and disjoint selection. This is a
recommendation, not authorization to generate more maps or relax thresholds.
