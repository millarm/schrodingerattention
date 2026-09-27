# Updates to a common 30% competence target

Status: specified for independent protocol review; no production authorized until
exact implementation PASS. User authorized writing and launching a separate
update-count study on2026-09-27. Astra specifies/supervises, Terra implements,
Sol independently reviews under `agent_execution_protocol.md`. Earlier Astra
implementation exceptions do not apply. This study references
`research/schrodinger_attention_research_paper.md`, SHA
`ed43f1705b0ea1dacf72b722dcb10c4a446e329f8a92375ec0ad0afbc15ed79e`.

## Question and claim boundary

How many optimizer updates does each architecture require to attain the SAME
predeclared moderate competence level? Training batch size is64, so updates
map directly to64 sampled state exposures. CPU cost, wall time, FLOPs and energy
are NOT scientific endpoints or reasons to call either architecture better.
Elapsed local usage is retained solely for safe resource authorization.

This is an **early-learning milestone study**, not equivalence to mature8k
softmax performance (historical fresh-seed mean Q38.198%). The common30% target
and margins below are motivated by prior exploratory trajectories and frozen
before any new-seed results. Old seeds1701–1705 are not fresh evidence here.
The validation maps have been reused: fresh-seed results are conditional on that
known selected population, not untouched-map confirmation or broad planning skill.

## Frozen experiment

|Item|Specification|
|---|---|
|Fresh seeds|2201,2202,2203,2204; verify no prior owner/checkpoint before execution|
|Models|Accepted `RoutePolicy`, softmax and exact Schrödinger;70,540 parameters; no changes|
|Training|Same accepted training bundle, map-balanced sampler and AdamW configuration, batch64, lr.001, clip1, no tuning|
|Pairing|Identical shared initial tensors and all within-pair minibatch digests; seed changes initialization, batch stream and evaluation uniforms jointly|
|Order|2201 SM→SA,2202 SA→SM,2203 SM→SA,2204 SA→SM; one process at a time|
|Horizon|4000 updates/model, completed for both modes regardless earlier target crossing|
|Saved checkpoints|Initial plus every100 updates, via unchanged accepted trainer|
|Scoring grid|0,500,1000,1500,2000,2500,3000,3500,4000; identical for both modes|
|Validation|All512 existing validation problems (24 routine+8 mixed maps), existing deterministic1024-state proper-score bank; no new cohort|
|Route scoring|T1, K32, same accepted seed/split1/replicate0 uniform construction; exact shortest legal route success|
|Aggregation|Within problem then equal maps in stratum; overall Q=.8 routine+.2 challenge; equal seeds for architecture summaries|
|Temperature/search|None; no temperature tuning, verifier-guided actions, task/representation change or architecture search|
|Final test|Forbidden, including prepared JSON parsing and test-loader calls; historical IDs may be copied from bound metadata without opening payloads|

Accepted initial numerical tests and model implementation are reused. No new
mechanism ablation, diversity target, difficulty subset selection, or language
model experiment is part of this study. State proper scores use exact multi-
solution q; KL removes irreducible teacher entropy. No hard-label accuracy or
entropy proxy replaces the learning target.

## Common target, margins and guards

At a scored checkpoint, **both architectures use exactly the same criteria**:

1. Overall valid-route Q≥0.29: target0.30 with a one-percentage-point lower
   tolerance. Overshoot is allowed and reported; this is "at least target-level
   competence within tolerance", not a formal two-sided equivalence test.
2. Teacher-relative mixture KL(q||p)≤0.37: reference0.35 with0.02-nat tolerance.
3. Mixed-challenge valid-route Q≥0.08: reference0.10 with0.02 absolute tolerance.
4. Finite scores and accepted numerical/runtime integrity checks pass.

These practical diagnostic bands are new prospective choices, not previously
validated clinical/statistical equivalence margins. Raw Q, exact threshold0.30
crossing (sensitivity), KL, Brier, teacher entropy and routine/challenge Q are
retained at every grid point. Sensitivity cannot replace the primary result.
The challenge floor prevents a routine-only path to the target; it does not
make this a difficult-task superiority study.

## Primary estimator and censoring

Require two consecutive scored checkpoints to satisfy ALL target criteria.
For each seed/model let j be the earliest grid index≥1 with passing checkpoints
j AND j+1. The reported observed acquisition update is grid[j], confirmed at
grid[j+1]. This is a sustained two-observation operational definition, not proof
that unobserved intermediate updates passed. Grid0 passing is reported separately
as a target-not-learning anomaly and invalidates an update-efficiency benefit
claim for that pair (do not replace seed).

Report acquisition as interval(grid[j−1],grid[j]] and its confirmation update.
No interpolation and no assumption of monotonic training. If no qualifying pair
exists, report right-censored/unconfirmed by4000; a first passing final4000 point
is explicitly unconfirmed, not recorded as a failure to learn or a4000 crossing.
An earlier isolated crossing is retained as such, never silently promoted.

For pairs with confirmed acquisition in both modes report SA/SM upper-grid update
ratio and paired update difference, plus interval uncertainty. If SM interval is
(Ls,Us] and SA is(La,Ua], ratio bounds are[La/Us,Ua/Ls], upper∞ when Ls=0.
Avoid false precision from500-update resolution. A censored model gives bounds
only; do not substitute4000, drop the pair, or present a mean ratio of completers
as the four-pair primary result. The primary table includes ALL four paired seed
outcomes, counts of SA earlier/same-grid/later/unresolved, and acquisition intervals.

The smallest practically interesting effect is at least20% fewer updates, matching
the original programme's sample-efficiency motivation. A **promising early-update
signal**, not confirmation, requires all four pairs evaluable, SA earlier in at
least3/4, median upper-grid ratio≤0.8, and at least3/4 conservative interval upper
ratios<1. Otherwise report no resolved advantage or INCONCLUSIVE due to censoring/
grid resolution. Never interpret a failed screen as equivalence or impossibility.
Four pairs do not justify a strong significance claim; do not treat checkpoints,
states or route samples as independent training replications.

## Implementation and narrow launch

Use a NEW entrypoint under this directory. Do not modify accepted model/data/
trainer/evaluator sources or old CLI seed guards. Reuse `scheduled_training`
with `validation=None` to retain unchanged optimizer steps, curves and100-step
checkpoints without its unrelated repeated initial/uniform/mechanistic probes.
Then load the fixed scoring-grid checkpoints inside the SAME owned attempt and
call accepted `evaluate_proper` and T1/K32 `evaluate_rollouts`. Evaluation happens
after training; no model-selection feedback or adaptive early stopping occurs.
No repeated greedy or initial/uniform route controls are required in this
update-count question. Disclose this instrumentation difference from the paper.

Input IDs must come from manifest-bound COMPLETE retained owners, not `_prepared_ids`.
Load training/validation via their accepted hash-checking loaders; reconstruct
only the same deterministic validation scoring bank and verify its frozen hashes.
Persist exact source/config/data/checkpoint/initial/batch/evaluation identities,
all raw outcomes, target flags, and owner/session/exit records. Use unique attempt
names and owned locks; never relaunch a yielded process.

Stages: (A) accepted additive wrapper/tests; (B1) one fresh pair2201 through4000
as a technical launch, maximum400 charged seconds; (B2) remaining fixed three
pairs only if1.5× observed per-mode complete-attempt cost forecasts their runs
inside the remaining run allocation. B1 results are part of the primary four,
not a tunable pilot. Continuation uses resource/integrity only, NEVER whether SA
wins or either model hits target. If resources fail, report an explicitly partial
fresh-seed study; do not switch seeds, lower evaluation counts, alter model or
reduce horizons to manufacture completion. No fresh profile-training model is needed.

## Prospective resource amendment — no new global budget

Baseline ledger `execution/model_training_comparison/ledger.jsonl`, SHA
`1340ee945d663e22c7a4fa7bd232c9832b90babe20d3d91662967116d232c3f9`:
qualified debit4764.416447001050/7200; remaining2435.583552998950 seconds.
This includes an administrative300-second historical uncertainty allowance,
not measured usage or a proven historical bound. No reset/new carry is permitted.

|New study allocation|Maximum charged seconds|
|---|---:|
|A: implementation, bounded tests/setup/failures|100|
|B: all8 model training+fixed evaluation owners|1600 (200/model)|
|D: aggregation, independent audit, reporting allowance|100|
|Total new ceiling|1800|

Prospectively transfer400 of unused D capacity to B: capsA1000/B3900/C0/D1000,
global7200 unchanged. Existing A860.001000330 +100<1000; B2286.766004918+1600<3900;
D694.645844500+100<1000. Maximum qualified global6564.416447001050 leaves635.58
seconds unallocated; not authorization for an extension. Record amendment before
first charged command, preserve historical ledger bytes and append EOF only.

Historical measured step+endpoint costs suggest4k training and9 fixed evaluations
can fit200 seconds/model; this is planning evidence, not a guarantee. Exact fresh
resource feasibility is checked after the first fixed pair without changing science.
External independently supervised deadlines and durable terminal records are
required for tests and production. Every failed attempt counts. Numerical failure,
provenance failure or exhausted allocation stops; no automatic retry/extension.
Root receives full command return/session and explicit exit. CPU timing is only
accounting and is excluded from scientific efficiency tables/claims.

## Separate mature-quality successor — NOT launched here

If the user later seeks equivalence to historical8k softmax quality, freeze a
separate target (e.g.38.2% reference with a justified margin), fresh inference/
seed plan and bounded8k-or-longer horizon BEFORE its outcomes. Many4k noncrossers
would be expected at that stronger target and must be censored honestly. This
study cannot silently extend to8k, choose a favorable checkpoint, or claim mature
parity from the30% milestone. Additional work requires a reviewed resource and
scientific amendment, including explicit user approval when scope expands.

Deliverable: audited update-to-target table, all learning trajectories and a
concise report referencing the paper; clear early-target scope, censoring and
guardrails. No claim about wall-clock superiority or final-test generalization.
