# Independent fresh-pair analysis correction review

**Analysis SHA-256:** `cbf8d19b31b429a91e48ad3dba2e2079ab0245d9811c92ad9e0e851bc8ffa3dd`  
**Tests SHA-256:** `e86471ce240f6548cc6b438880ba9db2821dc2e2c3f2b6b4e7625da877e9e76e`  
**Handoff SHA-256:** `240c36133a20d274d9e372654a6eccd99061c414588b21bf786ab3fd0e524ffe`

**Verdict: PASS**

All three findings in `analysis-review.md` are closed in the frozen version.

1. Each consumed owner is now bound to the exact reviewed wrapper and plan, original and amended resource tables/hash, seed/mode decision bytes/hash, authorized module argv, and accepted prepared/source provenance. Those authority hashes are retained separately for both models, in addition to checkpoint, initialization, manifest and 8,000-batch-prefix evidence.
2. The output provenance now names and hashes `analyze.py`, the replication wrapper and plan, `execution/paired_behavior/analysis.py`, `execution/paired_behavior/job.py`, and `execution/model_training_comparison/threeway_diagnosis_job.py`; the prior partial helper-source set is complete for the directly imported analysis helpers.
3. The bounded tests now exercise actual owner-authority mutations, final checkpoint seed/mode/update/source/config mutations, literal frozen cohort counts, both-model A/B/C assembly, fresh-seed/split forwarding across every cohort rollout, the exact two QC calls, actual retained 1702 event adapters, and a composed required-output record. The corrected count is 768 proper-score states and 144 routes per A/B/C cohort across 24 triplets.

The scientific behavior remains unchanged and correct: retained full-validation events supply the primary trajectories without repeated inference; only final checkpoints are loaded for A/B/C and two additional SA QC calls; the fixed temperature selection and quality tolerances are preserved; and the route-order limitation remains explicit.

The ledger visibly preserves the mistaken original stage-D `13.6s` charge as conservative overhead, appends its stage-A attribution, and separately records the failed `19.9s` and passing `19.2s` correction runs at stage A. No rows were rewritten or subtracted.

This exact version is approved for the four serialized, owned per-seed analysis jobs after each corresponding pair has completed. No tests, inference, or training were run during this static review because seed-1703 training was active.
