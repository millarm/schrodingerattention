# Independent results review — bounded baseline diagnosis

## Verdict: PASS

The immutable diagnostic result is complete, internally reproducible from its retained records, and supports the report's bounded scientific conclusions. One presentation correction is required in the records-only closeout: describe the original bank as a **valid broader-state generalization endpoint whose population is mismatched for a direct train-DAG comparison**, not as intrinsically “misleading.” This does not alter any result or conclusion about the observed mismatch.

Reviewed frozen artifacts:

- `baseline-diagnosis-001/baseline_diagnosis.json`: `04e891a7d0eed3d061603ce618c45c876967e22ecb153a076940c6fa1791aee1`
- `baseline-diagnosis-001/output-manifest.json`: `c1e512954b5450daf35250e655cc1a4170ad0f5db0f187d4cf8040c11c444a05`
- pre-review `baseline_diagnosis.md`: `a6f253a3d9dbfe35ff7e7370c08de22aaefa3d3aa88140091cb9617d189ba584`
- diagnostic implementation: `f65ba42a8260fe23160cdcb4744ae3cae70a842303f803ce13589df656659aea`

### Independent checks

- Every file in the owner output manifest exists and matches its SHA-256; the attempt reports `COMPLETE` and the single production command exited successfully.
- Checkpoint byte hashes are exactly the accepted softmax initial/1,000/4,000/8,000 identities: `5bf5f49d...`, `329fcd95...`, `af2d6912...`, and `3a6e06fc...`. The result binds the accepted frozen source, prepared data, dataset manifest, configuration, and shared initial state.
- Training contains 2,048 selected rows across 64 maps and DAG-aligned validation 1,024 rows across 32 maps, exactly 32 rows per map. All retained q rows are finite, nonnegative, normalized, and have the expected selected/candidate/q hashes. State-property counts exactly match selected-row counts.
- For all four checkpoints and both new banks, every raw CE/KL/Brier/entropy/nonoptimal-mass array is finite and has the exact selected-bank denominator.
- Independently recomputed equal-map KL summaries from raw rows match the stored values. At update 8,000: training `0.1007086867`, routine validation DAG `0.1937613974`, mixed challenge DAG `0.6669470641`, and stored broad routine `0.3471831241`.
- Update-8,000 training rollouts contain exactly 1,024 greedy attempts and 32,768 T=1 attempts over 1,024 problems/64 maps. Recomputed valid fractions match the stored routine summaries: greedy `0.7900390625`, T=1 `0.51373291015625`, and T=1 pass@32 `0.9736328125`. The absent challenge mixture remains null and is not used in the report.

### Interpretation

The evidence rules out neither optimization nor capacity limitations, but it does show active continued fitting: training-DAG KL improves from `0.20421` at 1,000 to `0.10071` at 8,000 while routine and mixed DAG-aligned held-out KL worsen after their earlier values. This is consistent with late overfitting or limited transfer; it does not prove either mechanism.

The broad-bank versus DAG-aligned difference establishes a population/eligibility mismatch, not a causal effect. A real held-out gap survives DAG alignment. Similar average entropy and remaining distance do not fully match goal, geometry, branching, or visitation distributions. The mixed challenge gap likewise cannot be attributed uniquely to obstacle composition because its selection and maps also differ.

Actual training rollouts demonstrate incomplete fitting of whole routes despite better one-step scores. Exact shortest-route success compounds decisions, but the report correctly uses measured rollouts and does not estimate success by multiplying bank-average probabilities. The spatial-inductive-bias discussion is explicitly a hypothesis. All evidence is retrospective and comes from one trained seed; states, maps, and rollout samples are not independent replications.

The proposed three-way matched-goal diagnostic is a future experiment only. This PASS authorizes no training, fixes, reruns, test inference, or dataset/model changes.

### Accounting

Independent audit charge: `0.8` seconds, UUID `CB9C483B-A2CF-48C3-983C-8A6120D03458`. Final diagnosis-task debit is `24.813250874987` of `120` seconds. Global operational debit is `1746.700972463049` of `7200` seconds.
