# Independent implementation review — bounded baseline diagnosis

## Verdict: PASS

Exact reviewed files:

- `execution/model_training_comparison/baseline_diagnosis_job.py`: `f65ba42a8260fe23160cdcb4744ae3cae70a842303f803ce13589df656659aea`
- `tests/test_baseline_diagnosis.py`: `8fac8662c66cea1d97a7ee90bbee89dc4dbe37e92b53445313a8a911a5f106ce`
- governing diagnosis specification: `cea244fa4653eaf8274e1a923abd2b469284cd15fac254b48099a44a367fad55`

The implementation satisfies the accepted bounded specification and is ready for its single inference-only production invocation.

### Verified behavior

- The DAG-aligned bank computes both start and goal distances, keeps exactly reachable nonterminal cells on a shortest start-to-goal DAG, unions repeated/overlapping problems by canonical map, map ID, family, goal, and current cell, and then uses the accepted deterministic 32-per-map bank selector. The literal open-grid fixture checks the exact five-cell DAG and the `east=1/3`, `south=2/3` start q.
- Selected q rows are normalized and assign no mass to illegal actions. Bank metadata retains candidate, selected, and q hashes, per-map counts, selected identities, and q values. State-property records retain distance, teacher entropy, and optimal-action count per map.
- All setup, checkpoint loading and validation, bank construction, inference, serialization, and owner finalization occur inside the owned attempt. The existing owner timer is shortened to at most 70 seconds and its cleanup/failure semantics are reused.
- Before inference, every checkpoint is bound to its actual owner-manifest byte hash, expected update, seed 1701, softmax mode, frozen configuration, source hash, prepared/input identities, and common initial identity. The initial state hash is independently recomputed. Wrong-update and owner-manifest substitution failures are exercised.
- The same fixed training and DAG-aligned validation banks are evaluated at updates 0, 1,000, 4,000, and 8,000. The broad comparator is loaded only from the matching immutable checkpoint event. Accepted proper-score weighting remains equal-map with routine/challenge separated where applicable.
- Update-8,000 training rollouts use all saved training problems, seed 1701, split code 0, and the accepted greedy and T=1/K=32 evaluators. Cache objects are removed before persistence; the training-only result is not forced into a validation 80/20 mixture.
- The result preserves raw per-row score arrays (excluding the reconstructive probability cache/output array), weighted summaries, raw per-problem rollout records, per-map/stratum aggregates, bank identities/q, checkpoint hashes and identities, timing, source/config/input hashes, and an owner-generated exact output manifest. JSON serialization is finite and uses the accepted serializer.

### Scope

This PASS authorizes exactly one fresh `baseline-diagnosis-001` invocation. It does not authorize training, checkpoint modification, test-set loading, threshold changes, reruns, or changes to the completed comparison. A concise interpretation document remains a post-result records task and must distinguish confirmed observations from hypotheses.

Static inspection only; no independent tests or ledger charge.
