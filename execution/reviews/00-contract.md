# Sol review — experiment contract draft v1

## Version inspected

`execution/experiment_contract.md`, SHA-256
`24860006a0933804d43260a08ba903849b487b77b381dff0af36c72c0e8e443b`.

Original constraints checked against `agent_execution_protocol.md`,
`early_experiment_plan.md`, and `schrodinger_attention_research_proposal.md`.

## Verdict

**CHANGES REQUIRED**

The contract is close to freezeable and its learning-adequacy guard is a
reasonable conservative addition. The following issues must be corrected
before implementation or comparative runs.

## Required findings

### 1. The parameter-count requirement is internally ambiguous

Location: **Models and optimizer**, sentence requiring exact equality and
parameter counts.

The Schrödinger model has eight additional trained scalars at the declared
two layers and two heads (`dt` and `gamma` per head), while the baseline does
not. Consequently, “verify exact equality and parameter counts” can mean
either equal counts (currently impossible) or exact equality only for
corresponding initial tensors plus reporting both counts. This could lead the
implementer to add an unapproved baseline mechanism or to claim a false exact
match.

Required correction: state explicitly that corresponding shared tensors must
be bitwise equal at initialization, state how the SA-only scalars are treated,
and require both exact total/trainable counts and the disclosed difference.
Do not add baseline computation merely to hide the negligible mismatch.

### 2. The two-of-three rule strengthens the approved gate

Location: **Endpoints and frozen gate**, accuracy and sample-efficiency gate
definitions.

The approved plan requires a mean improvement of at least 0.03 or a mean
sample reduction of at least 20%, with the signal appearing in at least two
paired seeds. Draft v1 instead requires the *full threshold* (0.03 or 20%) in
at least two individual seeds. That is a materially stricter scientific gate,
despite the draft saying the original thresholds are unchanged.

Required correction: define “signal” in the two-of-three seeds as a paired
improvement in the qualifying direction (`SA - baseline > 0` for accuracy;
fewer examples for sample efficiency), while retaining the threshold on the
three-seed mean. If Astra intends the stricter rule, it is a protocol-level
gate change and must be returned for user approval.

### 3. Dataset sampling and evaluation identities are not fully frozen

Location: **Data**, especially eligible-pair sampling and “condition offsets
documented in config.”

The contract freezes eligibility and balance but does not say how eligible
query pairs are distributed within each split, how training chooses the
homogeneous distractor-count batch, or what the test condition offsets are.
Those choices affect which examples define the endpoints and are currently
left to implementation after contract review. The requirement to record
dataset hashes only after generation does not independently freeze the choice.

Required correction: specify uniform (or other exact) eligible-pair sampling,
the exact training distractor-count schedule/distribution at batch level, and
the exact validation/test seed-to-condition mapping. Require the fixed
evaluation hashes to be generated and recorded before any training or
comparative metric is inspected. The concrete PRNG implementation/version may
live in the Block 2 specification/config, but it must be frozen and reviewed
before dataset-dependent execution.

### 4. Effective scalar initialization needs an unambiguous definition

Location: **Models and optimizer**, `dt`/`gamma` parameterization.

“Initialized dt=0.05; gamma=0.1” is ambiguous between initialization of the
raw trainable variables and initialization of their transformed effective
values. These interpretations produce substantially different effective
values (`0.256...` vs `0.05` for `dt`).

Required correction: state that 0.05 and 0.1 are either raw or effective
values and, if effective, require inverse-transform initialization within a
declared numerical tolerance.

## Independent checks performed

- Recomputed the contract SHA-256 shown above.
- Enumerated all 66 unordered pairs: the holdout rule yields 13 held-out and
  53 seen pairs; every key has 8 or 9 seen partners, so individual-key train
  coverage is feasible.
- Recomputed token lengths from the grammar: `7 + d`, yielding 9, 10, 11,
  and 15 for the declared distractor conditions.
- Checked that excluding held-out pairs for both operations blocks reversed
  XOR leakage and operation-mediated pair leakage.
- Checked that fixed sinusoidal positions avoid an untrained-position confound
  at length 15.
- Checked that literal effective `dt=0` recovers ordinary softmax probabilities
  independent of phase and that the specified row evolution orientation
  matches the plan.
- Checked checkpoint selection, final-test isolation, equal-update pairing,
  equal-time slack disclosure, COPY veto, learning-adequacy guard, and the
  four-hour accounting boundary for obvious asymmetric treatment.

## Checks not yet verifiable

- Dataset identity, balance, disjointness, and paired stream equality require
  the Block 2 generator and frozen hashes.
- Parameter equality/counts, numerical tolerances, timing behavior, and
  deterministic replay require implementation.
- The profile-derived update count cannot be reviewed until profiling output
  and its pre-results decision record exist.

## Non-blocking observations

- The one-hour profile projection criterion is substantially more conservative
  than the four-hour hard cap and may produce an inconclusive screen, but it is
  symmetric and predeclared.
- The equal-time result is checkpoint-discretized rather than exactly
  time-matched; the required slack reporting and label restriction describe
  this honestly.
- CPU peak RSS is an appropriate explicitly qualified proxy in this runtime.

---

# Sol re-review — experiment contract draft v2

## Version inspected

- `execution/experiment_contract.md`, SHA-256
  `2a49643fa9ec08b50a7b6c24edb55fe1c8e80eee62956c71a9b0a4f9f444d5b2`.
- Binding PRNG detail in `execution/specs/02-harness.md`, SHA-256
  `aa44ea9851324c1fce460f7d95fae35edb7a18c44d54f5a8810fd4994ed21266`.

## Verdict

**PASS**

Draft v2 resolves all four required findings from the draft-v1 review. The
contract is sufficiently explicit to freeze before implementation and before
any comparative metric is inspected. This verdict incorporates the Block 2
specification's frozen use of NumPy `Generator(PCG64)` and per-update training
`SeedSequence([100000 + seed, update_index])`; changing that PRNG rule or its
seed mapping invalidates the relevant dataset/reproducibility portion of this
review.

## Resolution of required findings

1. Corresponding shared tensors now require bitwise-equal initialization;
   exact total/trainable counts and the accepted eight-scalar SA difference
   must be disclosed without adding inert baseline computation.
2. The approved gate is restored: the 0.03/20% threshold applies to the paired
   mean, while at least two seeds need only improve in the qualifying
   direction.
3. Eligible pairs are sampled uniformly; orientation and batch-level
   distractor sampling are explicit; evaluation seeds and condition mapping
   are exact; fixed hashes must be recorded before training. The reviewed
   Block 2 PRNG rule completes the deterministic sampling definition.
4. `dt=0.05` and `gamma=0.1` are explicitly effective initial values, with
   inverse-transform raw initializers and a `1e-7` verification tolerance.

## Independent checks performed

- Recomputed both v2 hashes shown above.
- Rechecked the revised gate language against the approved early plan and
  confirmed that it preserves the mean thresholds and two-of-three paired
  direction requirement.
- Evaluated the declared transforms algebraically:
  `0.5 * sigmoid(log(0.1/0.9)) = 0.05` and
  `pi * tanh(atanh(0.1/pi)) = 0.1`, up to floating-point rounding.
- Checked that independent condition seeds and cell-level rejection sampling
  are compatible with exact operation/label balance, and that global split
  duplicate/overlap rejection remains required.
- Checked that per-update `SeedSequence` isolates paired batch generation from
  model RNG consumption and makes a batch independently reproducible by seed
  and update index.
- Rechecked parameter fairness, held-out reversal exclusion, positional
  extrapolation, validation/test isolation, timing endpoints, intervention,
  COPY veto, and learning-adequacy handling; no new blocking ambiguity was
  found.

## Checks not yet verifiable

- Actual generated dataset hashes, balance, split disjointness, and paired
  stream identity remain Block 2 implementation checks.
- Bitwise initialization equality, total parameter counts, numerical behavior,
  timing, and deterministic replay remain implementation checks.
- Profile-derived `N` remains reviewable only after profiling evidence and its
  pre-results decision record exist.

## Non-blocking observations

- Evaluation rejection sampling consumes a data-dependent number of PRNG
  draws, but it is deterministic under the frozen generator/version and does
  not create cross-model asymmetry because fixed evaluation arrays are shared.
- The conservative profile rule and learning-adequacy guard may yield an
  `INCONCLUSIVE` screen; the contract states that outcome without converting it
  into evidence against the mechanism.
