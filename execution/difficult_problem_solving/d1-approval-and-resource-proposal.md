# D1 kickoff and prospective resource-only amendment

Date: 2026-09-20. User authorized “Kick off d1”. This authorizes D1 only,
not D2, test eligibility inspection, final-test payload access, or training.
Astra specifies/supervises, Terra implements, and Sol independently reviews.
The accepted investigation plan remains unchanged, SHA-256
`c31c3ee84131ec4e96dbbd42e073a4ec96be63a0b3fc65058a18275714c035fe`.

## Read-only feasibility finding

No implementation, tests, model calls, new samples, or final-test access have
been launched. Existing evaluator supports logit-cache reuse, but each new
temperature still incurs categorical rollout and exact route verification work.
The accepted seed-1702 artifacts retain a full 512-problem softmax T1 endpoint
time of approximately 6.5681 s and SA T0.75/T1.25 endpoint times of
7.524406417/7.455084875 s. Source:
`execution/model_training_comparison/replication-1702-analysis/analysis.json`.

Sixteen missing softmax endpoints and eight missing SA endpoints therefore cost
approximately 165 s at these observed rates, before input binding, checkpoint
loading, serialization, bank profiling, and finalization. A 1.5× allowance on
these endpoint costs alone is approximately 247.5 s. Cache reuse cannot safely
be assumed to remove the dominant sampling and verification costs. The current
180 s D1 ceiling is not a conservative execution bound. This is a resource
finding, not a scientific failure or evidence about temperature outcomes.

The ledger preflight confirms global debit 4282.233080711118 s, with A
549.879192956971, B 2286.76600491805, C 0, D 522.5842855830977, and the
single inherited debit 923.003597253. Investigation development has consumed
83.077375040/100 s, leaving only 16.922624960 s for implementation tests and
failed attempts. No additional measured experiment charge has been incurred.

## Proposed amendment — NOT YET APPROVED

Request a D1 ceiling of **300 charged seconds instead of 180**, and a cumulative
investigation-development ceiling of **140 instead of 100 seconds**. These are
hard prospective maxima, not a claim that the work will consume them or fit.
Use a prospective stage transfer of **100 seconds from unused C to D**:
A700/B3500/C300/D1400, retaining the original global 7200 s ceiling.

After current usage, reserve the remaining development 56.922624960 s, D1 300 s,
the unchanged hypothetical D2 420 s, remaining audit envelope 80 s (20 already
debited for D0), and untouched reserve 60 s. Future D work would then reach
1382.584285583098/1400 s. This neither uses D2 authority nor consumes its
allocation to fund D1. D2 remains separately unauthorized and must still pass
its original 420 s runtime gate. No live deadline may be extended.

All science remains fixed: seeds 1702–1705, 8k checkpoints, complete validation
panel, both architectures at T={0.5,0.75,1,1.25,1.5}, K32/common uniforms,
16 identity-exact reused endpoints and 24 missing endpoints. Select temperatures
only using both fixed Q floors (paired softmax T1 minus 0.02), then maximum
challenge pass@32, higher challenge Q, lower T, with 1e-12 ties. Reuse bound
greedy outputs because positive temperature does not change argmax. No grid,
verifier, dataset, source-model, seed, or endpoint reduction to fit resources.

If approved, the next action is a tight additive Terra implementation contract,
Sol contract review, bounded implementation/tests and exact-version Sol review,
then one owned D1 job. It must preserve all candidates and measured component
timings and produce a validation-only D2 forecast with 1.5× margin for all eight
2048-problem K32/greedy/proper-score endpoints, including setup and I/O. No test
payload or oracle is needed or authorized for this forecast. Interval-width
projections remain descriptive and conditional on the small validation panel.

Current disposition: **await user direction on this resource-only amendment;
do not launch implementation or production under an inadequately supported
180 s forecast.** D0 remains independently audited COMPLETE/PASS.
