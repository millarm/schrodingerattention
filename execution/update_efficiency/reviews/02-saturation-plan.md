# Sol independent protocol review — bounded saturation pilot

**Plan SHA-256:** `d4ce6e3c6e4c0a7eac46aa96b2a01f442abeed573c3b78e95a2edb874caca6ae`

**Specification SHA-256:** `dcca6fa6c3ba0d322a8278d6003c77249c692a1224f37a3a2bad547530285a67`

**Verdict: PASS.**

Static protocol review only. I read the complete v3 plan, v3 specification,
referenced driver-closure specification, prior lineage decision, accepted
trainer/evaluator interfaces and current status. I did not import project code,
run tests or training, inspect final-test payloads, modify scientific source, or
write the ledger. V3 supersedes v2 before runtime; neither v2 nor historical
30%-only authority permits execution.

## Scientific estimands and claim boundary

The plan directly resolves the user's two meanings without conflating them.
Updates 1200/2400/3600/4800/6000 remain 15/30/45/60/75% of the original fixed
8000-update reference schedule. The separate 10000–16000 checkpoints ask whether
learning continued beyond that reference. They are not rebased percentages and
do not retroactively alter the early-curve contrast.

The 16000 horizon is correctly described as a bounded censoring horizon, not
proof of global learning completion. “Saturation” is operational and
endpoint-specific. Validation route quality and sampled training-objective CE
have distinct estimators and may produce different endpoints; neither is allowed
to stand in for the other. Continued Q improvement with worsening proper score,
or Q stagnation with improving sampled CE, remains reportable rather than being
collapsed into a completion label.

This is explicitly a two-pair exploratory pilot (seeds 2201 and 2202), not the
superseded four-pair replication. Alternating order, fixed seeds, shared initial
tensors, matched 16000-update minibatch streams, equal seed weighting, complete
horizons and retrospective scoring preserve the paired design. The plan makes no
t/p-value claim, seed replacement, adaptive stopping or outcome-dependent second
pair release.

## Validation-Q low-gain estimator

The primary estimator is mathematically defined on the complete equally spaced
2k subgrid. For every declared window end, all required observations exist:
`M(8000)` uses Q4000/Q6000/Q8000 and `M(4000)` uses Q0/Q2000/Q4000;
subsequent windows advance by 2k through 16000. `G(u)=M(u)-M(u-4000)` compares
fixed smoothed means whose centers are 4k apart. The extra requested fraction
points cannot change this estimator or receive additional weight.

Requiring the terminal 14000 and 16000 windows to qualify makes the endpoint a
prospectively bounded, retrospectively confirmed terminal regime. Selecting the
first qualifying pair in the final uninterrupted suffix gives an unambiguous
onset/confirmation rule. A later failure turns an earlier pair into an explicitly
reported temporary plateau/rebound; failure of either terminal window produces
right-censoring rather than imputation at 16000. Overlap, smoothing and lack of
independence are disclosed, and no interpolation or precise within-window onset
is claimed.

The one-sided condition `G<=0.005` intentionally includes zero, small gains and
negative gains. The mandatory deterioration/stagnation label for negative gains
is essential: a qualifying negative window is an operational low-gain endpoint,
not successful convergence. Raw Q, M/G values, Q8000→Q16000 and last-window
gains keep this distinction auditable. Only seeds with observed endpoints in
both modes may contribute an SA−SM plateau-update difference; censored cases
remain in the headline table.

## Sampled training-CE estimator

The CE estimator is separately coherent. Per-update durable CE is first reduced
to declared 100-update blocks, then to nonoverlapping 2k means `B(u)` through
16000. Relative gain `R(u)=[B(u-2000)-B(u)]/B(u-2000)` is defined only for finite,
strictly positive denominators. The fixed 8000–16000 evaluation points and the
same terminal-suffix/rebound/censoring logic prevent an outcome-selected CE
plateau. Negative R is correctly retained as worsening rather than evidence of
successful optimization completion.

The plan also states the estimator's real limitation: minibatch CE is a sampled
map-balanced training objective, not exhaustive training-bank loss, and changing
teacher entropy/state draws can affect it. Thus its numerical threshold is not
presented as equivalent to held-out KL or route success.

## Early curve and common-quality endpoints

The fixed curvature contrast
`C=DeltaQ(3600)-[DeltaQ(1200)+DeltaQ(6000)]/2` uses equally spaced stages and is
zero for constant or linear architecture gaps. The two-pair material screen
requires absolute mean curvature of at least one percentage point and the same
sign in both pairs, while remaining descriptive. Positive C means a mid-stage
bulge, not general superiority; a constant useful advantage can have C=0. No
alternative favorable curvature or stage search is authorized.

The 30% and 38.198% common-Q milestones use the same lower one-point tolerance
for both architectures, preserve exact-threshold sensitivity separately, and
retain adjacent-pass confirmation, initial anomalies, isolated/nonmonotone
passes, interval resolution and right-censoring. A first pass at 16000 remains
unconfirmed. Censored values cannot be replaced by 16000 or dropped for a
completer-only headline. KL/challenge values and fragility flags annotate a
crossing but do not silently redefine it.

Because the combined scoring grid is intentionally irregular, “two consecutive
checkpoints” gives different confirmation lags (for example 400 updates from
2000 to 2400 versus 2000 updates late in training). This is a prespecified coarse
operational rule, not a duration-standardized stability estimator. The report
must show acquisition and confirmation updates/lag explicitly and must not rank
nearby milestone crossings with more precision than their stated
`(previous, acquisition]` intervals. This limitation does not affect the primary
2k-grid plateau estimator.

## Accepted-interface contract

The implementation remains feasible without accepted-source changes.
`scheduled_training(..., validation=None, updates=16000)` preserves optimizer
steps, sampler state, per-update batch digests and 100-update checkpoints while
omitting unrelated in-training probes. The initial checkpoint and every v3 grid
point are available on that cadence. After training, accepted
`evaluate_rollouts` supports the fixed full-panel T1/K32, split-1, replicate-0,
seeded common-uniform evaluation; accepted `evaluate_proper` supports the exact-q
bank and required equal-map/stratum mixture metrics.

Implementation acceptance must literally verify:

- owner absence and exact seeds/order; shared-initial identity and all 16000
  paired batch digests before accepting a pair;
- the complete, duplicate-free 13-point grid and every checkpoint's byte hash,
  seed, mode, update, source, accepted config, input IDs, initial identity and
  parent-chain identity;
- finite raw and aggregate scores, expected 512-problem/1024-state identities,
  frozen q/order/bank hashes and identical rollout RNG construction;
- exact 2k-grid Q inputs, terminal-suffix/rebound/censoring classification,
  literal 100-update CE blocks, 2k CE windows, positive denominators and
  deterioration labels;
- two-seed-only summaries, fixed C, milestone interval arithmetic and retention
  of every censored/anomalous outcome;
- production-inaccessible short test schedules/loaders, forbidden prepared/test
  access, one write per endpoint, durable partial artifacts, and one owner charge
  on every terminal/failure path.

The v3 specification correctly carries forward the six driver-closure duties
while replacing every obsolete 4k/8k resource and authority constant. Authority
must bind the v3 plan/spec and designated reviews; no superseded plan hash, owner
name or 4000/8000 command shape may authorize production. The scoped stage-table
override and `finally` restoration, exact ledger prefix/carry, locks, envelope
reservation, descendant cleanup, UUID reconciliation and permanent uncertain
fallback remain mandatory. Exact frozen implementation review is still required
before any runtime.

## Resource feasibility and launch gate

The arithmetic is consistent. From qualified debit
`4764.416447001050/7200`, the new A100/B1800/D100 allowances produce a maximum
qualified debit of `6764.416447001050`, leaving about 435.58 seconds explicitly
unallocated. Under caps A1000/B4100/C0/D800, the maxima are A960.001000330,
B4086.766004918 and D794.645844500, all within their prospective stage ceilings.
This is a resource-only D→B transfer inside the existing global cap, not a reset,
new carry or extension.

The two SM350/SA550 envelopes consume at most the exact B1800 allocation across
two pairs. Pair 2201 is a fixed ≤900-second minimal launch. Pair 2202 is released
only after both first-pair terminals and integrity checks, and only when 1.5 times
the observed complete per-mode charges fits both the remaining B allocation and
the same per-owner ceilings. Results, apparent curvature, plateau status and
milestone crossings are prohibited gate inputs. Failure of the forecast yields
a one-pair partial pilot without shortening horizon/grid, changing seeds or
retrying owners.

Historical costs make the attempt plausible but do not guarantee success;
doubling training and adding 13 post-training endpoints could still exceed an
owner envelope. The plan states that feasibility risk and does not treat unused
global headroom as authority. Runtime remains accounting metadata and no
equal-time or computational-superiority claim is produced.

## Bounded limitations

Two seeds cannot establish replicated architectural superiority, a reliable
population variance or global saturation. The validation population is reused,
the low-gain thresholds are pragmatic, smoothed Q windows overlap, CE is sampled,
and a rebound after 16000 cannot be ruled out. The protocol nevertheless answers
the authorized bounded questions without hiding censoring or conflicts. Any
additional seed, later horizon, alternative plateau threshold, final-test access
or mature-confirmatory claim requires a new prospective scientific and resource
amendment.

