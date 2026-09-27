# Agent Execution Protocol

Status: APPROVED — user authorized execution on 2026-09-15.

## Prospective role amendment — 2026-09-27

The user explicitly assigns current and future planning/supervision to
`gpt-6-astra`, implementation AND operation to `gpt-6-luna`, and independent
review to `gpt-6-sol`. Terra is inactive for new work. These exact assignments
supersede role names/model identifiers in the legacy protocol below and in
previously frozen study plans, without rewriting historical evidence or changing
scientific plans. One Astra, one Luna, and one Sol may be active alongside the
parent. Astra specifies and accepts; Luna edits code/tests and operates approved
commands; Sol independently reviews. All existing review gates and budgets remain.

The user's accompanying "Fix this up" authorizes a bounded reviewed repair of
the update-efficiency platform cleanup blocker. It does not waive cleanup proof,
permit unreviewed runtime, increase resources, or change scientific endpoints.

## Cycle-specific authorization, 2026-09-16

For productive-diversity v2 only, the user explicitly authorized switching
implementation to Astra. Astra now specifies, implements and supervises this
cycle; Sol remains the independent reviewer with mandatory PASS before execution.
Terra is inactive. This exception does not change scientific thresholds, resource
limits, prior results or any other cycle's historical role assignments.

For productive-diversity v3, the user explicitly restored the Terra/Sol strategy
on2026-09-16: Astra supervises/specifies only, Terra implements/tests, Sol reviews
independently. The v2 Astra implementation exception has ended.

This document defines how subagents will execute
[the early experiment plan](early_experiment_plan.md), based on
[the research proposal](schrodinger_attention_research_proposal.md).
Saving or reviewing this protocol does not authorize implementation or training.
No execution agents should be started until the user approves these rules and
authorizes execution.

## 1. Roles and model assignments

| Role | Model | Responsibility |
| --- | --- | --- |
| Supervisor | Astra (`gpt-6-astra`) | Specify each implementation, delegate work, resolve review findings, authorize runs within the approved budget, and decide whether results satisfy the plan. |
| Implementer | Terra (`gpt-5.6-terra`) | Implement Astra's written specifications, run required checks, and provide reproducible evidence. |
| Reviewer | Sol (`gpt-5.6-sol`) | Independently inspect each completed implementation and its tests, check scientific validity, and issue a written review. |

The parent conversation dispatches Astra as the supervising subagent and relays
progress and user decisions. Astra directs Terra and Sol as its subagents. The
parent does not bypass Astra's specifications or Sol's review.

Use explicit model assignments when spawning agents; do not silently substitute
another model. If a required model is unavailable, report the limitation and
ask the user to choose a replacement before continuing the affected role.

Give each agent a self-contained handoff with the approved protocol, experiment
plan, relevant specification, files, and prior findings. Do not assume that a
fresh agent has inherited conversation context. Use a fresh-context spawn when
needed to select the specified model explicitly.

Keep one Astra, one Terra, and one Sol active at most, alongside the parent.
Reuse those agents for subsequent work blocks. Additional delegation requires
a change to this protocol approved by the user.

## 2. Mandatory work cycle

Every implementation follows this sequence:

1. **Astra specifies.** Write a bounded work specification with acceptance
   criteria before Terra starts editing.
2. **Terra implements.** Make the scoped changes and execute the required checks.
3. **Terra hands off.** Record changed files, commands, results, limitations,
   and the exact version to review.
4. **Sol inspects.** Read the implementation and specification, verify the
   evidence, and independently run targeted checks where useful.
5. **Terra revises if necessary.** Astra resolves specification questions;
   Terra fixes implementation findings. Sol reviews the resulting changes.
6. **Astra accepts.** Accept only after Sol passes the current version and all
   acceptance criteria have evidence. Then start the next dependent block.

An implementation is not complete merely because Terra reports success or its
tests pass. It requires Sol's inspection and Astra's recorded acceptance.

Astra writes specifications and decisions; Terra owns implementation and test
edits; Sol writes reviews. Astra and Sol should describe required code fixes
and return them to Terra rather than silently implementing them themselves.

## 3. Required handoff records

Create the following records after execution is approved:

```text
execution/
  status.md
  experiment_contract.md
  specs/01-<block>.md
  handoffs/01-<block>.md
  reviews/01-<block>.md
  decisions.md
```

Each Astra specification must contain:

- Objective and the relevant part of the experiment plan.
- Files Terra may create or change, interfaces, and explicit exclusions.
- Exact behavior, configuration, and assumptions.
- Tests and measurable acceptance criteria, including numerical tolerances.
- Permitted commands, resource limits, and required output artifacts.

Each Terra handoff must contain:

- Summary of the implementation and changed files.
- Commit identifier if available, otherwise file hashes for the reviewed files.
- Commands run, exit status, and links to actual test or run output.
- Deviations, unresolved questions, and known limitations.

Each Sol review must contain:

- The exact implementation version inspected.
- Verdict: `PASS`, `CHANGES REQUIRED`, or `BLOCKED`.
- Findings with file locations, consequences, and required corrections.
- Checks independently performed and checks that could not be verified.
- Any non-blocking observations, kept distinct from required corrections.

`status.md` records each block as `SPECIFIED`, `IMPLEMENTING`, `IN REVIEW`,
`REVISING`, `ACCEPTED`, or `BLOCKED`, with links to its evidence. Astra records
acceptance and experiment decisions in `decisions.md`.

## 4. Execution blocks

### Block 0 — Freeze the experiment contract

Astra inspects the available runtime and hardware and writes
`experiment_contract.md`. Resolve these details before implementation or
inspection of comparative results:

- Token representation, vocabulary, COPY semantics, label balance, and query
  and fact ordering.
- How fixed sequence lengths coexist with varying distractor counts; for
  example, batches with a single length and separate longer evaluation batches.
- Training, validation, and final test splits, including exclusion of reversed
  versions of held-out XOR key pairs and coverage of individual keys.
- Model dimensions, positional representation for longer inputs, parameter
  sharing at initialization, and paired data streams.
- Phase and evolution-time parameterization, initial values, and bounds.
- Optimizer, schedule, batch size, seed list, evaluation frequency, and stopping
  rules; any tuning must have a declared, equal allowance for both models.
- Primary generalization endpoint, secondary endpoints, and exact definitions
  of a material COPY regression and a meaningful `dt = 0` intervention effect.
- Numerical tolerances, timing procedure, budget allocation, and artifact names.

Sol reviews the contract for ambiguity, leakage, and unfair comparisons. Astra
resolves findings and freezes the contract before Terra implements it. This
preparatory review is additional to the required implementation reviews.

### Block 1 — Attention modules and numerical correctness

Terra implements conventional and exact Schrödinger attention plus the plan's
numerical tests. Sol checks tensor axes, the transpose used for row-state
evolution, Hermiticity, unitarity, probability normalization, gradients, and
equivalence to softmax at `dt = 0`.

Exit: Sol passes the implementation and Astra accepts the numerical evidence.

### Block 2 — Dataset, tiny models, and measurement harness

Terra implements the deterministic generator, two-layer classifiers, training
entry point, evaluation, logging, and checkpoints. Sol checks split leakage,
label generation, longer-input handling, matched initialization and data,
per-operation metrics, timing, and reproducibility.

Exit: Sol passes the implementation and Astra accepts a bounded smoke run that
exercises training, evaluation, checkpoint loading, and the intervention.

### Block 3 — Run the approved comparison

Following acceptance of the harness, Astra directs Terra to execute the frozen
three-seed paired comparison within the resource cap. Preserve configuration,
runtime versions, raw curves, checkpoint references, failed runs, and logs.

Sol audits completeness, comparability, metric calculations, and the `dt = 0`
evaluation. Any implementation change during this block returns through the
specification, implementation, and review cycle before affected runs continue.
Results produced by superseded code must be identified explicitly.

Exit: reviewed results exist for the specified comparison, or the cap is
reached and missing measurements are recorded.

### Block 4 — Review results and make the research decision

Terra produces the results table, learning curves, and reproducible summaries
as specified by Astra. Sol verifies them against raw results. Astra writes the
final interpretation and stop/continue recommendation using the frozen gate.

The report must distinguish sample efficiency from wall-clock efficiency and
include paired seed differences, variability, overhead, intervention results,
and limitations. Missing runs, failure to learn, or invalid measurements may
require an `INCONCLUSIVE` result rather than a negative scientific conclusion.

## 5. Scientific and resource rules

- Preserve the plan's three-percentage-point accuracy and 20% sample-efficiency
  screening thresholds, paired-seed requirement, and COPY/intervention checks.
  Freeze endpoint selection before results are inspected.
- Do not change seeds, splits, thresholds, or hyperparameters to improve an
  emerging result. Record any necessary amendment, its reason, and which
  comparisons it invalidates. Changes to the scientific gate require user review.
- Treat three seeds as an early screening result. A `dt = 0` intervention tests
  dependence on evolution; on its own it does not prove useful interference
  or rule out other architectural effects.
- Set a hard ceiling of four device-hours for the initial experiment, including
  profiling, smoke training, failed training attempts, and measured runs.
  On CPU, use four elapsed compute-hours as the ceiling. Record actual hardware.
- Profile a small workload before allocating the remaining budget. Run one
  training job at a time. Astra may reduce the configuration before measured
  runs, consistently for both models, as allowed by the plan.
- Define equal-update and equal-time comparisons in the contract. They may
  reuse logged runs if those runs cover both endpoints; otherwise allocate
  separate runs within the same total cap. Never imply measured FLOP or energy
  equality from wall-clock timing alone.
- Hardware incompatibility or insufficient runtime budget is a feasibility
  finding. Do not silently change the scientific mechanism to make it run.
- Paid cloud resources, additional compute budget, and expansion to deferred
  research require user approval. The initial execution approval covers routine
  local implementation, tests, and runs described here.

## 6. Shared workspace and review discipline

- Only Terra edits implementation files. Freeze those files during Sol's review.
  Any later implementation edit invalidates the affected part of that review.
- Preserve existing user files and unrelated changes. Keep specifications,
  reviews, logs, and results traceable without requiring a Git repository.
- Scope fixes to findings and acceptance criteria. Astra may clarify routine
  details within the approved experiment; material scope changes return to the user.
- If a finding remains unresolved after two revision cycles, Astra must identify
  the cause and issue a revised bounded specification or report a blocker.
  Do not loop indefinitely or waive a required check.
- Astra provides concise progress updates through the parent, including accepted
  blocks, important findings, consumed budget, and decisions needing user input.

## 7. Completion and approval boundary

The initial execution is complete when the accepted implementation, numerical
checks, available experiment results, Sol reviews, and Astra's research decision
are linked in `execution/status.md` and handed back to the user.

A positive result authorizes a recommendation for the next research block; it
does not automatically authorize approximations, additional tasks, extra seeds,
language-model training, or scaling.

**Current action: execute the approved protocol. User approval recorded on 2026-09-15.**

## Cycle-specific v3 runner exception — 2026-09-16

After Sol16 blocked the remaining runner status model, the user explicitly
approved Astra implementing that narrow fix and its tests. Astra is supervisor
and implementer only for the remaining v3 runner correction and necessary reviewed
runtime corrections in this fixed dataset cycle. Terra is inactive. Sol remains
the independent exact-version implementation and results reviewer. This exception
does not alter historical role assignments, accepted data logic, scientific gates,
seeds, or budgets. Production requires Sol PASS; this request ends after reviewed
dataset feasibility, with no neural implementation or training.
