# Three-way checkpoint diagnosis — frozen before inference

User authorization: “Do the next check”, 2026-09-19. Astra specifies; Terra
implements a small additive job/tests; Sol reviews specification, exact code and
results. No retraining, second seed, model/data changes or test-set access.
Preserve prior artifacts. Starting global debit1746.700972463049/7200 seconds.
New diagnostic ceiling120 seconds: development≤15, one job≤74 (70-second owned
deadline plus4-second allowances), audit≤15, contingency16. One process, unique
`threeway-diagnosis-001`, actual existing D ledger, explicit terminal exit.

## Outcome-blind cohorts

A = seen training maps and original selected training start/goal problems.
B = the SAME training maps but map-specific unseen goal cells: a goal must be
absent from **every saved RouteState.goal on that canonical map**, not merely
absent from selected start/goal pairs. Verify zero exact (canonical,current,goal)
overlap against the complete saved training-state set for all B DAG states.
An unseen goal may have appeared on other maps; do not call it an unseen spatial
token. All A DAG states must be in that complete saved set. C = held-out routine
validation maps and their original selected problems, with canonical maps absent
from all training maps. No mixed/test maps enter this new construction.

Use the first12 canonical-byte-sorted training maps in each I/L family; pair by
family/rank with the12 canonical-byte-sorted routine validation maps of that
family. These24 map triplets are fixed; no replacement maps if support is poor.
For B, enumerate free goal cells absent from the complete per-map training goal
set; for each goal use accepted BFS/count/q, retaining every free nonterminal
start at exact shortest distance14,15,16. No learned output is consulted.

Route matching within each triplet:

1. Bin A/B/C candidates jointly by (exact route length, count of q>0 at start).
2. Sort each bin's unique problems by SHA256 of
   `b"goaldiag-route-v1\\0" + canonical + start.to_bytes(2,"big") + goal.to_bytes(2,"big")`,
   then (start,goal) as a collision tie-break.
3. Per-bin quota is min(2, countA, countB, countC). Traverse sorted bin keys in
   round-robin rounds, one row/bin/round up to that quota, stopping after6 rows
   per cohort. Identical bins/counts/order of quotas apply to A/B/C. If fewer
   than3 rows/cohort are available, exclude the entire triplet.

State matching within retained route triplets:

4. Form the union of every selected route's nonterminal shortest-path-DAG states,
   deduplicating (canonical,current,goal), with exact completion-weighted q.
5. Bin by (exact remaining distance, count of q>0). SHA-rank using accepted
   serialize_candidate, with (goal,current) tie-break. Apply the same joint
   quota/round-robin rule, cap32 states/cohort (per-bin cap2). Do not subsequently
   call a selector that destroys these exact bin quotas. If fewer than8 states
   per cohort survive, exclude the triplet, including its route rows.
6. Require at least8 retained triplets in EACH family. Otherwise write
   MATCHED_SUPPORT_INSUFFICIENT and stop before model inference; no fallback,
   rematching seed or cohort enlargement. Persist all candidates' supply counts,
   quotas, retained identities, exclusions and cohort hashes BEFORE predictions.

Construct matched ScoreBanks with all retained selected states (no further SHA32
downsampling). Every cohort has exactly equal joint-stratum counts/weights within
each matched map triplet. Score within-map means then equal-map means; retain
family and per-map values. A/B are same maps; C is rank-paired within family, not
claimed identical geometry. Report actual row/map denominators.

## Fixed measurements

Reuse accepted softmax checkpoints1000,4000,8000 and their common initial identity;
reuse the reviewed diagnostic checkpoint guard and accepted model/evaluators.
Verify exact checkpoint owner hashes and prepared/source/config/input identity
before inference. CPU runtime remains2 intra-op/1 inter-op. No optimizer.

At each checkpoint/cohort: exact teacher CE/KL/Brier/nonoptimal mass on the fixed
matched state bank; greedy and T1/K32 exact shortest-route success on the matched
route problems. Use existing common-uniform rules seed1701, replicate0; splitcode0
for A/B,1 for C. Save per-state scores and per-problem routes. All cohorts are
routine-family; report routine aggregation, not an absent80/20 mixture.

Record remaining-distance/optimal-action counts, teacher-entropy distributions and
shortest-path multiplicity of route problems. Matching first-action branching is
NOT full branching/geometry/difficulty control. New B pairs were not selected
under the original routine Mnovel=0 condition; do not make a novelty causal claim.
Use complete saved support only for existing evaluator consistency; do not enumerate
all new route signatures or infer exposure from signature membership.

The matched support is a retrospective diagnostic population, not an unbiased
estimate of all train/validation tasks. One trained seed remains one replication
unit; no p-values/independent-seed claims. Existing mixed-composition findings stay
separate context, not a fourth matched cohort.

## Compact literal verification

Tests must exercise: deterministic unequal-supply joint quotas with exact equal
bin counts across3 cohorts; exclusion of unsupported bins/triplets; repeated calls
give identical selections; map-specific goal exclusion uses a suffix-only saved
goal even if no original pair names it; same coordinate on another map does not
make a goal seen here; A full-state overlap/B zero overlap checks. Include a real
open12x12 BFS/q example (reuse prior diagnosis helpers/fixture) so matching is not
tested solely with fake q. Reuse accepted owner/checkpoint safety, do not rebuild
a framework. One focused test invocation, charge once; Sol PASS before one job.

Final: concise `threeway_baseline_diagnosis.md` with confirmed findings versus
hypotheses, remaining matching limitations and all hashes/compute. No automatic
next experiment or modification follows from the findings.
