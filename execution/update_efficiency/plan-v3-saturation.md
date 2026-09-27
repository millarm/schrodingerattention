# Early learning path and bounded training-saturation pilot

2026-09-27. Revised pre-result protocol for Sol review. The user clarified that
15/30/45/60/75% means fractions of the original8000-update reference schedule,
then requested training toward completion and whether8000 is too early. This
supersedes plan-v2 before any new runtime; historical plans/reviews/draft code
are preserved. Astra specifies, Terra implements, Sol independently reviews.
Exact implementation PASS remains required before any training.

Reference paper: `research/schrodinger_attention_research_paper.md`, SHA
`ed43f1705b0ea1dacf72b722dcb10c4a446e329f8a92375ec0ad0afbc15ed79e`.
Prior results are exploratory, not fresh replication. Historical fresh-seed
4k→8k Q gains were+4.195pp softmax/+3.883pp SA, while validation KL worsened.
Therefore neither8000 saturation nor general learning completion is established.

## Questions and fixed design

1. At the requested early fractions, how do the paired learning curves diverge?
2. By a bounded16000-update horizon, when do validation-Q gains become small?
3. Separately, when do sampled training-objective improvements become small?
4. How many updates reach the same common quality milestones?

No finite experiment establishes global learning completion. Saturation below
is an operational, endpoint-specific low-gain rule. Compute/wall cost is NOT a
scientific endpoint; resource limits still bound local execution.

|Item|Frozen specification|
|---|---|
|Fresh pairs|2201 and2202 only; no replacements. This is a TWO-pair exploratory pilot, not the superseded four-pair replication|
|Order|2201SM→SA,2202SA→SM; one compute process|
|Models/data/optimizer|All accepted sources/configuration unchanged; RoutePolicy70540parameters, batch64, AdamW lr.001, map-balanced stream, clip1|
|Pairing|Shared initial tensors and all16000 minibatch digests matched within seed|
|Maximum horizon|Both modes16000 updates, completed regardless observed plateau or target crossing; no adaptive early stop|
|Requested early points|1200/2400/3600/4800/6000 =15/30/45/60/75% of8000, never rebased to16000|
|Scoring grid|0,1200,2000,2400,3600,4000,4800,6000,8000,10000,12000,14000,16000|
|Extra points|2000/4000 support equally spaced gain windows;10000–16000 are separate saturation follow-on points|
|Evaluation|All512 validation problems T1/K32; exact same1024-state proper bank; split1/replicate0 and common uniforms|
|Aggregation|Equal problems/map, equal maps/stratum, mixture.8routine+.2challenge, equal seeds|
|Excluded|No test release/prepared JSON parsing, tuning, new representation/task, extra seeds, paid resources, temperature search or beyond16k continuation|

Use unchanged accepted trainer with validation=None, checkpoints every100; score
frozen grid after training in same owner. Evaluation has no optimizer feedback.
Save raw minibatch curves/checkpoints/proper scores/routes. No extra historical
model results count as new seeds. Reused validation maps limit generalization.

## Primary practical endpoint: sustained validation-Q low-gain regime

Use the equally spaced2k grid only for this estimator; extra early fractions
cannot increase weight or provide searched endpoints. Define

`M(u) = [Q(u−4000) + Q(u−2000) + Q(u)] / 3`,
`G(u) = M(u) − M(u−4000)` for u=8000,10000,12000,14000,16000.

A low-gain window has G(u)≤.005 (at most0.5 percentage point improvement across
the4k-separated smoothed means). Negative gains also qualify mathematically,
but MUST be labeled deterioration/stagnation rather than successful convergence.
Smoothing and overlapping windows are not independent observations.

To call the regime sustained through the bounded horizon, require the final two
windows14000 AND16000 to qualify. Find the earliest consecutive suffix of qualifying
window ends, with length≥2. Report its first window end and confirmation at the
next end, and use that confirmation update as the operational update-to-plateau.
Any earlier low-gain pair followed by G>.005 is a temporary plateau/rebound and
is reported but not the sustained endpoint. This is retrospectively confirmed
within a prospectively fixed16k run, not a claim the model could safely have
stopped at the first low-gain observation. Do not infer a precise onset inside
the smoothed window or interpolate. If the final two fail, plateau is right-
censored/not demonstrated by16000, NOT assumed to occur at16000.

Report raw Q, all M/G, per-seed plateau/censoring, and SA−SM update difference
only where both are observed. Missing/censored cases stay in the headline table.
Also report Q8000→Q16000 and the exact last-window gains, so the answer to
"was8000 too early?" is not reduced to a binary threshold. No t/p-value claim
from two seeds or treating checkpoints/maps/draws as training replications.

## Secondary optimization endpoint: sampled training-CE low-gain regime

From the accepted durable per-update minibatch CE curve, report100-update block
means, then define B(u)=mean CE over updates(u−2000,u] for u=2000,4000,...,16000.
Relative improvement R(u)=[B(u−2000)−B(u)]/B(u−2000), evaluated at
8000/10000/12000/14000/16000. Denominator must be finite and>0; otherwise mark
numerical/estimator invalidity, never silently pass. Low gain is R≤.005, i.e.
≤0.5% relative CE improvement per2k window. Apply the SAME final-two/suffix/
later-rebound rule; report worsening separately.

This is sampled map-balanced training objective, not exhaustive training-bank
loss. Different teacher entropy/state draws can affect CE; no direct numerical
equivalence to heldout KL is implied. Validation proper KL/Brier and challenge Q
are retained at every score to distinguish continued fitting, transfer plateau,
and worsening generalization. If Q plateaus while training CE improves, say so;
if Q rises while KL worsens, report that conflict rather than "learning complete".

## Prespecified early-curve divergence and common-quality updates

For each seed ΔQ(u)=SA−SM in percentage points. Report all requested five early
points,8000, and the follow-on stages. The fixed nonlinear contrast is
`C = ΔQ(3600) − [ΔQ(1200)+ΔQ(6000)]/2`.
It is zero for a constant/linear architecture gap on those equally spaced stages.
|mean C|≥1pp with the same sign in BOTH pairs is a descriptive material-curvature
screen, not statistical confirmation; show both values and range. Do not select
a different curvature or favorable stage after results. A later-minus-earlier
gap summary from plan-v2 may be omitted; this pilot avoids multiple searched
shape claims. Constant advantage can be useful even if C=0.

Common Q milestones30% and38.198% (historical softmax8k mean) retain the SAME
one-percentage-point lower tolerance for both modes: thresholds.29 and.37198.
Report exact-threshold sensitivity separately. First two consecutive scoring
points passing define acquisition at the first, confirmation at the second,
with interval(previous-grid,first-passing-grid]. Nonmonotonic/isolated passes
remain visible; first final16k pass is unconfirmed. Initial0 pass invalidates
an update-saving claim for that seed/threshold. Censoring is never imputed as16k.
For confirmed pairs give update difference, grid ratio and conservative bounds
[La/Us,Ua/Ls],∞if Ls0. No four-pair screen or completer-only headline mean.

Report proper/challenge values at acquisition; KL>.40nat or challenge Q<.08 are
fragility flags, not secretly different crossing thresholds. A positive paired Q
gain at a stage is described as mixed if mean KL is worse by>.02nat or challenge
Q worse by>2pp. These practical descriptive margins are not equivalence tests.
Neither route-quality parity nor this pilot establishes equivalent full policies.

## Qualified resource envelope and objective launch gate

Central ledger baseline SHA
`1340ee945d663e22c7a4fa7bd232c9832b90babe20d3d91662967116d232c3f9`;
qualified debit4764.416447001050/7200, remaining2435.583552998950. Administrative
300s historical uncertainty remains nonmeasured/non-proven. Preserve prefix/EOF;
no reset, additional carry or retrospective accounting correction.

New allocation staysA100/B1800/D100 =2000. Prospectively transferD600→B:
capsA1000/B4100/C0/D800, global7200 unchanged. Stage baselineA860.001000330,
B2286.766004918,D694.645844500. Maximum qualified debit6764.416447001050;
435.58 remains unallocated, not extension authority.

First fresh pair2201 has one SM350-second and one SA550-second owned envelope
(≤900 total, all startup/cleanup/finalization included). After BOTH explicit
terminals and integrity verification, second fixed pair2202 proceeds ONLY if
1.5×observed complete per-mode charges fit BOTH remaining B allocation and its
same per-owner350/550 ceilings. Gate uses resources/integrity, NEVER outcomes.
Otherwise stop with the completed one-pair exploratory result. No owner retry,
seed replacement, lower horizon/grid or beyond16k extension to rescue feasibility.

Prior8k owners169–171s SM/281–282s SA included repeated probes/controls omitted
here, while this design doubles training and uses13 single-policy endpoints.
Therefore feasibility is uncertain. This bounded pilot does NOT promise four
fresh pairs or mature saturation. More seeds/horizon require a new resource and
scientific amendment; no new global budget is requested by this protocol.

## Gates and deliverable

Sol protocol PASS → complete Terra static source/tests → Sol static safety PASS
→ externally bounded10s smoke/30s suite withinA100 → exact implementation PASS
→ Astra acceptance → first pair → objective resource gate → second if feasible
→ bounded independent audit. No implementation role substitution.

Final report leads with paired update counts/curves, validation plateau versus
training-objective plateau, censoring/rebounds, proper-score conflicts and
whether improvement continued beyond8k. Resource accounting is a separate
appendix, never a computational-superiority claim. Stop after audited bounded
outcome; no final-test access.
