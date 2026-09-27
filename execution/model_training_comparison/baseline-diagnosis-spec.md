# Bounded baseline diagnosis — authorized 2026-09-19

Read-only model/data investigation, not a new training experiment. Existing study
and its gate stop remain unchanged. Astra specifies, Terra implements only an
additive small diagnostic script/tests, Sol independently reviews before execution
and audits the diagnosis. No test-set load/inference, no training, no model or
dataset edits. New compute ceiling120 seconds within existing remaining budget;
start global debit1721.887721588062. Reserve≤15 seconds development tests,
≤74 seconds owned production job (70-second deadline plus4s allowances),
≤15 seconds independent audit and16 seconds contingency. No rerun on yield.

## Single inference-only job

Use existing accepted RoutePolicy, oracle `_bfs`, `_q_from_oracle`, `_bank`,
training_bank, evaluate_proper/evaluate_rollouts, configure_runtime and OwnedAttempt.
Write only `baseline-diagnosis-001` unique output in the current execution root;
use its existing ledger, D stage, and shorten the owned timer to70 seconds.
Retain full command/session results and explicit exit before any later compute.

Checkpoints: softmax initial,1000,4000,8000 from their existing immutable attempts.
Verify file SHA against each owning output-manifest, expected seed1701/mode,
exact source/config/prepared/input identity and update. No optimizer step.

1. Training fixed bank: existing saved deduplicated DAG states, existing32-per-map
   SHA selection (2048 total). Compare checkpoint0/1000/4000/8000 on identical rows.
2. Validation DAG-aligned bank: for each selected validation start/goal problem,
   retain every nonterminal current cell satisfying
   `dist(start,current)+dist(current,goal)==dist(start,goal)`; union/deduplicate by
   canonical/map/goal/current. BFS distances and completion-weight q come from
   accepted oracle. Apply existing deterministic32-per-map SHA selection. This
   aligns the state eligibility rule, not the maps/goals or all distributions.
3. Preserve the existing broad held-out bank results from original checkpoints as
   a separate comparator. No new broad-bank inference needed. Summarize each bank's
   selected distance-to-goal, teacher entropy and number of optimal actions.
4. At8000 only, run existing greedy and T1/K32 training-problem rollouts on all1024
   saved training problems, same seed1701/common-uniform rules, splitcode0. Report
   routine stratum (there is no training challenge; do not use a null80/20 mixture).
   Compare to stored8000 validation routine and challenge separately. Keep raw
   per-problem outputs; no novelty claims are needed from this diagnostic.

Primary diagnosis: distinguish fitting on seen DAG states from routine-map
generalization, broad-bank eligibility mismatch and unseen mixed composition.
Use CE plus entropy-corrected KL/Brier/nonoptimal mass; do not infer route success
by multiplying bank-average probabilities. Any nonoptimal step irreversibly fails
the exact shortest-route criterion. One trained seed remains one replication unit.
No p-values, confidence intervals or causal explanation from these comparisons.

Save source/config/checkpoint/input hashes, selected candidate identities/q and
bank hashes, raw score arrays, per-map summaries, elapsed timing and file manifest.
Read frozen existing inputs only; reuse loader/hash validation. Keep script compact;
no framework, new model, report generator or CLI variants.

## Literal acceptance tests

Construct an open12x12 map, start0/goal25: the nonterminal shortest DAG is exactly
{0,1,12,13,24}; oracle start q has south2/3 and east1/3 in N/E/S/W order. A repeated
problem does not duplicate candidate rows. Verify goal is excluded and every
selected q sums to1, has zero illegal mass, and hashes/selection are deterministic.
Checkpoint substitution/wrong-update rejection must be exercised before inference.
Existing owner safety is reused, not reimplemented. One focused test invocation;
record actual elapsed/exit and charge once. Sol exact-version PASS precedes run.

Final artifact: concise `baseline_diagnosis.md`, confirmed findings separated from
hypotheses and the smallest next validation experiment. Preserve completed report.
