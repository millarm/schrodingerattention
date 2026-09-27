# Amendment 1: where held-out KL changes

2026-09-27. Prospective Astra amendment after the user's request to read and
incorporate the reviewer's follow-up:
https://github.com/millarm/schrodingerattention/pull/1#issuecomment-5858424227.
No new early-learning inference has run. Preserve plan.md and its previous
review; this amendment adds secondary arithmetic diagnostics and qualifies the
interpretation. The original grid, windows, two paired seeds, evaluations and
fresh 1,800-second cap are unchanged. No extra model calls, training, calibration,
final-test access or 200k work is authorized. Runtime is held pending amendment
review and correction of the existing static implementation findings.

## Interpretation

Lower mean policy entropy over training does not by itself establish
overconfidence, and entropy near the oracle's mean does not establish calibration
or agreement with its distribution. The reviewer withdrew the blanket
“increasingly overconfident” wording. Saved aggregate nonoptimal action mass
also falls from 1,200 to 16,000 in all four owners. A harmful redistribution on
some states remains a hypothesis, not an established global increase in wrong
action mass. Retain all raw KL, Brier, entropy, Q and greedy series, and add the
already computed nonoptimal_mass series. No causal attribution follows from
any single diagnostic below. The power table remains exploratory because the
four-pair variance estimate is uncertain; confirmation still needs a separate
precision design, fresh seeds and a frozen assessment procedure.

## Fixed state identity and weights

Use every one of the same 1,024 proper-score states. Match checkpoints by
(canonical map bytes, map_id, family, goal, current), rejecting duplicates,
missing states, altered oracle q or inconsistent legal masks. The ordered bank
hash remains bound to the original evidence. Oracle support is S_i={a:q_ia>0},
with no probability cutoff. An action outside that support can still be legal.

Derive legal masks with the accepted legal_mask function and retain them once
in the owner bank metadata. Legal argmax uses the largest saved policy
probability among legal actions, ties resolved by the first legal action in
the accepted order: up, right, down, left. Do not infer legal masks from q>0
or from nonzero p, and do not classify argmax by the largest q action alone.

For each state i in map m and stratum s, use exactly
w_i = a_s / (number of maps in s) / (number of bank states in m),
where a_routine=0.8 and a_challenge=0.2. Require both strata and sum w_i=1.
Compute counts from the fixed bank, never separately within a transition group.
This is the existing equal-state-within-map, equal-map-within-stratum weighting.

## Four exhaustive argmax transition groups

For every adjacent pair (0,100), ..., (2900,3000), and the fixed pair (800,2000),
classify each state by whether its legal policy argmax lies in oracle support
at the earlier and later checkpoint: on→on, on→off, off→on, off→off.
No selected worst-state list, deleted states, favorable checkpoint pair or
monotonic smoothing replaces these fixed comparisons.

For each group g report its unweighted state count, weighted prevalence
W_g=sum_{i in g} w_i, signed additive contribution
C_g=sum_{i in g} w_i (KL_i,later−KL_i,earlier), and conditional weighted mean
C_g/W_g when W_g>0, otherwise null. Empty groups have zero count, prevalence
and additive contribution. All four groups remain in the report. Require
sum_g W_g=1 and sum_g C_g=weighted_KL_later−weighted_KL_earlier.
Also show routine/challenge contributions using their original mixture weights.
Do not renormalize a group and mistake its conditional mean for its contribution.

## Exact support-mass and within-support decomposition

For each checkpoint/state define m_i=sum_{a in S_i} p_ia. With normalized q,
KL(q_i||p_i) = −log(m_i) + KL(q_i||p_i/m_i on S_i).
Use saved finite per-state KL and saved probabilities; calculate support cost
A_i=−log(m_i), and within-support term B_i=KL_i+log(m_i). This avoids taking
logs of rounded/underflowed individual probabilities to reconstruct the KL.
Validate finite normalized p, oracle support, and m_i>0. Do not silently clamp
zero mass or omit invalid states. If exported p cannot support this arithmetic,
mark that checkpoint's decomposition unavailable and report the reason; the
original KL remains valid and no new model evaluation is authorized to repair it.

Report weighted A and B at each checkpoint, their adjacent and 800→2000 changes,
and their additive group contributions under the same transition partition.
Require A+B to reconstruct saved KL before and after weighting; also require
ΔA+ΔB=ΔKL. Preserve small floating-point residuals and tolerance diagnostics;
do not force numerical closure by altering a component. Save state IDs, masks,
weights, group labels and component values for independent audit.

These components measure loss of probability on oracle support versus
redistribution within that support. They do not measure calibration, prove a
training mechanism, or imply every off-support choice produces an invalid
complete route. Group comparisons are descriptive of the fixed panel; states
and adjacent checkpoint pairs are not independent training replications.
