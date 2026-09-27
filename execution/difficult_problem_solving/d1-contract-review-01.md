# Independent Sol re-review of the D1 implementation contract

**Contract SHA-256:** `f36ab859b0eb8f7c5e120605a4963bb5ba8c48428a481345695f3b058efa76ad`

**Verdict: PASS — Terra may implement this exact contract; production still requires exact-version implementation PASS.**

This was a static contract/interface review only. I ran no implementation,
tests, inference, model calls, checkpoint loads, training, prepared-payload
deserialization, or final-test access. The prior `CHANGES REQUIRED` review is
preserved at `d1-contract-review.md`.

## Closure of prior findings

1. **Final-test payload boundary: closed.** Lines 27--39 now require identical
   metadata-only `input_ids` from manifest-bound COMPLETE retained artifacts,
   pass those IDs directly to the narrow validators, and explicitly prohibit
   `_prepared_ids`, `load_final_test`, test-selection helpers, and prepared JSON
   deserialization. Only opaque streaming SHA-256 of `prepared.json` is permitted.
   The same forbidden-path guards are required in composed tests.

2. **Uncertainty calculations: closed.** Lines 99--108 hold selected temperatures
   fixed and define the four-seed mean, sample SD with `ddof=1`, t half-width and
   full width. They also freeze NumPy PCG64 seed 91703, 2,000 shared resamples of
   eight challenge maps, same resample across both models and all seeds, the
   per-seed/equal-map then four-seed statistic, linear 2.5/97.5% quantiles, full
   width, and map-only `sqrt(8/32)` projection with the required assumptions.
   Lines 145--147 require literal deterministic assertions.

3. **Forward/action accounting evidence: closed.** Lines 67--70 retain new-run
   forward-call, batch-state, and generated-action counts and preserve unavailable
   historical counts as unavailable. Lines 142--147 require known-count synthetic
   assertions, route-length action summation, cache-count changes without RNG-route
   changes, null rather than zero historical values, and integration with the
   forecast/uncertainty checks.

## Contract assessment

The corrected contract is scientifically complete and fair for D1. It fixes four
seeds, final 8k checkpoints, the complete ordered 512-problem validation panel,
both architectures, all five temperatures, K32, common uniforms, exact 16 reused
plus 24 new endpoints, symmetric cache policy, and retained greedy reuse. It binds
retained endpoints through COMPLETE owners, manifests, producer source, event and
checkpoint identities, preserves the historical route-order limitation, and makes
any mismatch an integrity stop rather than replacement inference.

Eligibility uses both challenge and routine Q floors relative to the same seed's
softmax-T1 reference. Selection is maximum challenge pass@32, then challenge Q
within the frozen tolerance, then lower temperature; all 40 candidates remain in
the output. No eligible SA candidate is a control no-go. There is no mixture
objective or favorable subgroup selection.

The forecast is validation-only, includes all declared D2 operation classes and
cardinalities, applies 1.5x to the entire prospective cost, distinguishes cold
from warm cache costs, treats missing essential measurements as unsupported/no-go,
and cannot grant D2 authority. The ownership section enforces the approved
300-second D1 maximum, 140-second cumulative development ceiling, amended stage
table, existing global cap, one immutable owner, bounded timer, partial-artifact
truthfulness, no retry, and separate audit accounting.

No required corrections or non-blocking contract observations remain for this
exact version. This PASS authorizes only Terra's bounded D1 implementation and
synthetic tests. It does not authorize the D1 production run before exact-version
Sol implementation PASS, and it does not authorize D2, final-test access,
training, new checkpoints, or any additional samples outside the fixed D1 grid.
