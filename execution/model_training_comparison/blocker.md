# Model training comparison — implementation blocker closeout

2026-09-19. **BLOCKED, not a scientific result.** The approved plan remains
unchanged. No production preparation, smoke/profile or measured paired training
ran. Small optimizer/evaluation fixtures were development tests only. We cannot
yet answer whether the route-policy SA model learns, follows a different learning
path, or improves valid novelty. This is not evidence against SA.

## Accepted work retained

| Component | Independent acceptance |
|---|---|
| Matched route models, immutable frozen-data adapter, numerics | reviews/A1a-01.md PASS |
| Banks, exact proper/route metrics, sampling and temperature helpers | reviews/A2a-01.md PASS |
| Isolated safety/training/checkpoint core at its reviewed version | reviews/A2b1-02.md PASS |
| Batched evaluator and identified local/full-path SA diagnostics | reviews/A2b2a-02.md PASS |

The accepted pool512 dataset and all original plans, sources and results remain
preserved. Subset acceptance does **not** accept the current combined runner.

## Definitive remaining blockers

Sol's [final review](reviews/A2b2b-02.md) identifies five material gaps after two
full-harness correction cycles:

1. No executing real `command_profile` or composed CLI-training regression.
   Helper/selector tests do not prove the launched workflow, serialization,
   scheduled events and resumed runs work together.
2. Profile accounting overlaps phases, uses clamped residual setup time and
   reads a guessed ledger location rather than timing the actual supplied
   ledger/finalization path. It cannot support the required resource gate.
3. Profile cost covers validation probes only, not separately identified
   training 64 + validation 128 probes; concatenation also loses split origin.
4. Profile outputs discard evaluator/probe/numerical/checkpoint evidence; the
   governing-source inventory and complete output hash manifest remain missing.
5. Fresh results omit the initial checkpoint **file** hash needed for an
   authorized resume, and required run-binding/substituted-initial negatives
   are not executed.

Root cause of the repeated incomplete handoffs: implementation repeatedly
completed helper paths and asserted selected shapes/counts while leaving the
real command composition and measured work unfinished. Passing test counts were
not sufficient acceptance evidence. Fresh same-model contexts and bounded
subtasks made progress, but did not close the final integration contract.

## Exact frozen identities

| Artifact | SHA256 |
|---|---|
| model_training_comparison_plan.md | 5ece45cdb11f860ae64933225f284297cff59aa544c6730b247138c660cc8ff0 |
| schrodinger/route_policy.py | 95cb7463693c7ac696d9034eaf16a155c0363f38e819cbe56c00408d49b170c4 |
| schrodinger/route_policy_data.py | 676b8de313fb9c667497b307704b21f137ac55a18e1e19c81be399d3f02e4bb7 |
| schrodinger/route_policy_metrics.py | a471ae2c40973cb15584f924061b3ace24ef5af3b1e31702b79056055f317e34 |
| schrodinger/route_policy_evaluation.py | fd5cd438e0fbd103857933418008a7c5936b379488857ac6bfa7370aa8ad18ec |
| Blocked route_policy_experiment.py | e9ea4858176a19c4ef267ea70592f69eb9795c3fc41eea787a40c74921d3bb7d |
| Blocked tests/test_route_policy_experiment.py | 7d44a67a5a62cb19df50d8bc8a85d3518b672eb92c232f1a5d397277ea92d728 |
| reviews/A2b2b-02.md | efb6cad47659f7b8d18f55b37fb99258c0d2c22745195fd5f2b60f60ef247022 |
| ledger.jsonl at closeout | e1475fe9bcc16a1838a6a4858a035281da44c593c5c338b83c21c53e0a73a890 |

## Accounting and next decision

Operational debit is **1212.003835837 / 7200 seconds**, including inherited
923.003597253 and this cycle's 289.000238584. Some earlier test charges are
explicitly conservative rounded allowances; one lost-output test is marked
unknown and not used as acceptance evidence. Do not relabel these as measured.
There are 5987.996164163 global seconds and 110.999761416 stage-A seconds left.
No budget increase is requested or implied. This stop is not resource exhaustion.

The proposed recovery is confined to the five integration findings above, with
one real composed command fixture and independent Sol acceptance before any
unique production profile. No model/data/scientific threshold change is needed.
Parent/user must choose whether to authorize a **narrow Astra implementation
exception with Sol still independent**, or another explicitly bounded Terra
attempt. Astra currently has no implementation exception and will not edit code
or launch unaccepted work. Any resource-only reallocation must be prospective,
reviewed and stay inside the existing global ceiling. After acceptance, the next
scientific action remains the unique profile/cost gate, then the approved first
paired diagnostic only if feasible.
