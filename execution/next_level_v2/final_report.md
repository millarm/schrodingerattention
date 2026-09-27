# Productive-diversity v2 — dataset construction stopped before learning

Status: COMPLETE — Sol results review08 PASS; prescribed scientific stop accepted.

**Outcome: DATASET_LADDER_FAILED.** Both predeclared8x8 constructions failed
their fixed length-matching allocations. This is not a model failure, a novelty
comparison, or evidence for/against creativity. No neural model was initialized,
trained, sampled or compared in this iteration.

## What actually ran

After the user authorized Astra implementation ownership on2026-09-16, the
runner was repaired and independently accepted by Sol (review07;32 focused
tests passed independently). The frozen scientific thresholds were unchanged.
One production process executed the default A→B dataset ladder in
`attempts/feasibility-001`; session8329 was polled to explicit exit0. RungB ran
only because A returned a declared scientific construction failure, not because
of a timeout or crash. No duplicate command or alternate selection was launched.

| Construction | Completed evidence | Frozen gate that failed |
| --- | --- | --- |
| A:8x8, three components |1,024 canonical maps;1,024 selected training problems on64 maps;21,612 unique supervised DAG states;10,728 suffix signatures and complete I/L orientation coverage | Routine validation:378/384 required problem slots can be allocated |
| B:8x8, four components |768 canonical maps; all three family pools reached256 maps | Training selection:784/1,024 required problem slots can be allocated |

The exact shortages are visible in the saved flow capacities:

| Gate / shortest length | Required quota | Available on frozen selected maps | Allocated by full constrained flow |
| --- | ---: | ---: | ---: |
| A routine validation /14 |42|36|36|
| B training /16 |93|80|37|
| B training /17 |93|42|2|
| B training /18 |93|20|0|

“Available” counts eligible start/goal problems before the16-problems-per-map
constraint. B's per-map competition further reduces the simultaneous allocation.
A's other length quotas were all filled. B's length8–15 quotas were filled.

## Interpretation and limits

The richer grid provides a sizeable candidate and training-data space, but the
frozen random map selection cannot satisfy the specified length balance. The
result establishes infeasibility for these selected maps/quotas—not that no
feasible8x8 dataset exists. Choosing different maps, quotas, lengths or another
rung would be a new scientific design, not a harmless runtime recovery.

Neither rung reached challenge evaluation; final test construction, baseline
learnability, power, quality–diversity curves, matched softmax comparison and
dt0 intervention are **NOT_EVALUATED**. In particular, the experiment did not
measure whether the larger domain has enough qualifying novel solutions or
whether Schrödinger attention produces a small useful novelty gain. RungA's
saved “training” artifacts are oracle supervision data, not trained weights.

The plan required stopping when both dataset rungs failed. We stopped without
relaxing matching, resampling maps or selecting a favorable result. A concise
capacity table is the relevant result here; a learning/diversity plot would
misrepresent stages that never ran.

Sol independently verified all manifest hashes, replayed both saved maximum
flows, replayed A/B training-map selection and B raw capacities, and checked
routine eligibility on A's24 selected validation maps. It did not regenerate
the pools or fully replay the eligibility permutation over unused A maps;
review08 states this verification boundary explicitly. No alternate selection
was attempted during the audit.

## Provenance and resources

- Production elapsed266.122563125s plus2s startup allowance, charged268.122563125s.
- Final conservative cumulative debit443.384519002s of7,200s,
  including the separately disclosed150s historical accounting allowance.
  This debit is not a claim of443.385s measured compute. It includes Sol's
  results audit charge4.3918795s once; see ledger.jsonl and accounting_closeout.md.
- Results review08 SHA-256:
  a4df295b5c5400f3cd6fcb5293d0aae850cb32c9d93b4f750b51a2e8130fd128.
- Parent manifest SHA-256:
  d8347db12a8a184f3fdec430eeef71585bbc51e5e1c66a75fb335695b61e50e3.
- Raw parent summary SHA-256:
  17bd6459610f445e1c2d1608826f71c1f0164afcea8f720de4c16d5b71ae49ab.
- A suffix-support SHA-256:
  336ddd6c1171612baea3768b7f4b3e751adb407a68dbf7b8ac8d54e932801d94.

Frozen plan: ../../productive_diversity_v2_plan.md. Raw immutable evidence:
attempts/feasibility-001/{A,B}/ and its parent summary/manifest/attempt records.
All historical experiments, blockers and rejected reviews remain preserved.
