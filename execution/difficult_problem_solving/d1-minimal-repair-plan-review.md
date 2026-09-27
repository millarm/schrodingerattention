# Independent Sol review of the minimal D1 repair plan

**Plan SHA-256:** `370650b044b51eab8c331b54718e0af85be9dfa75758bab695e23cc4312d2a31`

**Verdict: PASS — this is a bounded, scientifically valid repair plan suitable for user approval. No execution is authorized by this review.**

This was a static plan review only. I ran no tests, Python imports, checkpoint
loads, model calls, inference, training, final-test access, or ledger mutations.
The blocked implementation, tests, ledger, closeout, and failure review remain
preserved.

## Minimality and blocker closure

The plan reduces recovery to three coherent changes rather than another runner
rewrite: complete the input/selection bindings, replace cumulative whole-output
serialization with immutable per-cell writes plus a small index, and replace the
weak fixtures with literal bounded tests. These are the smallest coupled changes
that address the observed evidence failures and make one D1 measurement plausible.

It closes the six groups from `d1-failure-review.md`:

1. **Terminal exact-version evidence:** an external watchdog records command ID,
   hashes, argv/cwd, UTC and monotonic timing, stdout/stderr, session ID, timeout/
   exit, process-group termination, and reaping. A yield remains one running
   command and cannot trigger a relaunch.
2. **Support and endpoint identity:** metadata-only IDs, accepted owner/checkpoint
   cross-checks, exact config/final identities, canonical complete-support digest,
   validation-family counts, and RNG digests are all frozen. The plan correctly
   clarifies my earlier audit wording: accepted `load_training` already verifies
   its dataset; the missing requirement is retaining that accepted identity and a
   canonical digest of its complete signature support, not substituting unrelated
   matched-triplet support.
3. **Greedy and retained-route evidence:** separate bound raw greedy records per
   model and the accepted pure stored-route verifier replace the paired summary
   and map/family-only check. The independently rebound valid-route/order negative
   is detectable while the all-invalid permutation limitation remains explicit.
4. **Forecast evidence:** available rollout/greedy/proper timing cells and their
   identities/cardinalities must be extracted rather than blanked. Any unavailable
   complete D2 bound is truthfully labeled `D2_FORECAST_DEFERRED/NO_GO`; the plan
   does not turn missing evidence into zero or a measured runtime failure.
5. **Literal tests:** the accepted evaluator and real counter wrapper are exercised;
   the owned orchestration dispatches the exact 16/24/40 partition with tiny bags;
   binding, selection, both floors, all tie levels, cache/RNG behavior, route/action
   counts, distinct endpoint-write and final-manifest failures, bootstrap math,
   stage caps, lock state, and forbidden paths receive concrete assertions.
6. **Frozen provenance:** plan, approval/amendment/reviews, source, inputs, config,
   support, checkpoints, panel, RNG, cells, and greedy identities are explicitly
   bound without parsing the sealed prepared payload.

The per-endpoint write-once design is a targeted response to the source-visible
quadratic amplification: it preserves all 40 raw cells and full attempts without
repeatedly serializing the growing collection. The plan correctly labels this as
a plausible, testable cause rather than a demonstrated diagnosis.

## Scientific validity and authority

The scientific comparison is unchanged: seeds 1702--1705, final 8k checkpoints,
the full ordered 512-problem validation panel, both architectures, the fixed five
temperatures, K32/common uniforms, 16 exact reuses plus 24 missing endpoints, two
per-seed softmax-T1-relative Q floors, and the frozen pass/Q/lower-temperature
selection rule. No checkpoint, seed, model, data, verifier, threshold, or endpoint
is dropped to make the repair fit. Incomplete production retains partial cells but
cannot select from them.

The proposed forecast deferral is an explicit, scientifically safe narrowing of
the prior implementation deliverable: D1 may report the symmetric tuned validation
comparison while D2 remains a no-go until a separate complete forecast and release
authorization exist. It must be approved by the user because it amends the prior
D1 implementation contract. It does not weaken the D1 comparison or authorize
test access.

## Test, budget, and accounting boundaries

The test procedure is externally bounded and confidence-gated: at most 10 seconds
for smoke, then 30 seconds for one suite; a 60-second suite is available only after
successful smoke, measured valid progress, and explicit Sol concurrence. There is
one correction batch and one repeat, with all development/setup/failures capped at
120 charged seconds. The user's conditional “up to 10x” is correctly not treated
as a blanket command, stage, cumulative, or global expansion.

The damaged ledger is preserved at hash
`770d3490766d0ec2e40a796ee8f896b4f1fbc3e7647c00d145cf4010dfc7d7c0`.
The plan neither rewrites history nor double-charges the ambiguous 30.2-second
reports. Its 300-second administrative uncertainty debit is transparently an
operational reserve, not measured usage, an upper bound, or restored confidence.
The proposed A1000/B3500/C0/D1400 transfer, fresh 120-second allowance, qualified
global basis, and administrative reserve all require explicit user acceptance.
If the user does not accept that qualified basis, compute remains blocked.

After those approvals, repair still requires Terra implementation, exact-version
handoff, independent Sol PASS, and a fresh unused owner/lock preflight before one
300-second D1 launch. No retry is automatic. D2, final-test access, training, and
new samples remain unauthorized.

No changes are required to this plan. The next step is user review of the explicit
accounting/resource proposal and D2-forecast deferral; PASS here is not execution
authority.
