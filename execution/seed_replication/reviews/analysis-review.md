# Independent fresh-pair analysis implementation review

**Analysis SHA-256:** `c89803b10f24e998ceb6801102da676ce206df2dccc82a5c7674b0fa7da76dd9`  
**Tests SHA-256:** `c1b8ef9aba114de89be2231412c43f1d59f3aa5f084214c17131200291c717b8`  
**Handoff SHA-256:** `c19f924a92ff26340d1c1d82026aa64e596a8cd436009c6364df4f1bbbeb263d`  
**Analysis-spec SHA-256:** `f0835e17e3b7be5b6536abb0e587786516e05d080aa35ce777d640c47511eb72`

**Verdict: CHANGES REQUIRED**

The main scientific path is correctly scoped: it uses retained 1k/2k/4k/8k full-validation events without repeating that inference, validates shared initial tensors and all 8,000 paired batch digests, scores both fresh models on the frozen A/B/C support, forwards the fresh seed to rollout calls, makes exactly the two additional SA quality-control calls, applies the frozen match tolerances, and preserves the accepted route-order limitation. The following frozen-spec requirements remain materially incomplete.

## Required corrections

1. **Bind the actual training-wrapper authority of each input owner.** `_owner_record` checks `input_ids` and parameter count, while `_checkpoint` checks seed/mode/update/config/source. It never checks the owner's `wrapper_provenance`, replication-plan hash, resource-table hash/table, actual decision hash, or expected command authorization. Merely hashing the currently imported wrapper into the analysis output does not prove that either consumed owner was produced by that reviewed wrapper. Validate the persisted owner provenance against the reviewed wrapper/plan/resource identities and the exact seed/mode decision file, and retain those evidence hashes in the analysis result.

2. **Complete the analysis-source provenance set.** `source_hashes` binds `analyze.py`, the training wrapper, the plan, and `execution/paired_behavior/analysis.py`, but the job directly imports scientifically relevant adapters and cohort construction from `execution/paired_behavior/job.py` and `_exact_bank` from `execution/model_training_comparison/threeway_diagnosis_job.py`. Bind these exact helper files too (and name each path/hash), rather than presenting a partial helper hash as complete provenance.

3. **Implement the literal negative and composed evidence required by `analysis-spec.md`.** The five tests do not currently demonstrate:
   - rejection of wrong seed/mode/update or mutated owner/checkpoint identity;
   - rejection of altered wrapper/decision/resource provenance;
   - frozen A/B/C counts and both-model A/B/C result assembly;
   - fresh-seed forwarding to every A/B/C model rollout (the only rollout spy covers QC);
   - unchanged scalar/config/source bindings;
   - a composed result containing the required primary stored-event delta, paired 8k metrics, A/B/C outputs, and QC status.

   Add bounded fixtures/assertions for those exact behaviors. The real 1702 retained-event adapter test is useful, but it establishes only event decoding/order, pair initialization and batch-prefix compatibility; it does not establish the missing analysis assembly and provenance gates.

## Accounting note

The handoff reports the focused test wall as a stage-D charge even though the frozen plan assigns development/tests to stage A. The supervisor has stated that a proper stage-A charge will be appended while retaining the original D charge conservatively. The correction must be visible at ledger EOF before acceptance; do not rewrite or subtract the original entry.

No tests, inference, or training were run for this review because seed-1703 training was active. The existing source and outputs remain frozen pending correction; no analysis job is authorized by this verdict.
