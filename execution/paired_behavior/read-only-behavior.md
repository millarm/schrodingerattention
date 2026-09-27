# Read-only paired behavior supplement — audit PASS with route-order limitation

Independent audit: `readonly-behavior-review.md`. Exact verifier checks found
zero mismatches in retained greedy validity labels. This corroborates—but does
not replace—the disclosed order contract, especially for all-invalid groups.

No model inference or blocked analysis job was run for these calculations.
An inline read-only calculation (explicit exit 0, tool wall 0.653286334 seconds)
loaded immutable owner-manifest-verified results at 1,000/4,000/8,000 updates.
Exact proper-score state rows, including q, were equal across architectures;
greedy and K32 route cardinalities and map/family order were checked.

Route records omit start/goal: within-map order is supplied by the audited
immutable evaluator and bound dataset contract, not independently proved by
map_id equality. This residual binding limitation is explicit. State TV does
have exact saved state-ID/q alignment. No claim that this replaces blocked
production analysis or executes the frozen A/B/C/temperature components.

| Updates | Both solve | SM only | SA only | Neither | Mean policy TV (80/20) | Argmax disagreement (80/20) |
|---|---:|---:|---:|---:|---:|---:|
| 1,000 | 198 | 46 | 41 | 227 | .0639034 | 9.7917% |
| 4,000 | 236 | 28 | 43 | 205 | .0722797 | 10.0000% |
| 8,000 | 215 | 50 | 65 | 182 | .0968941 | 11.3281% |

Greedy counts are raw counts across 512 problems, not the 80/20 mixture.
At 8,000 the mixture proportions are both43.9583%, SM-only9.8958%,
SA-only12.7604%, neither33.3854%. Of 118 raw argmax disagreements among1,024
states,89 choose two q-optimal actions,17 favor onlySM's optimal action,
10 favor onlySA's,2 neither. Thus disagreement is often among multiple valid
options, not necessarily improved decisions.

Sampled valid-route-set Jaccard, with both-empty NA and within-map conditional
means followed by80/20 weighting: .3917013/.3788984/.3159959 at1k/4k/8k.
Both-empty problem counts:85/70/69 of512. At8k weighted distinct valid routes
perproblem are intersection4.16094, SM-only4.13594, SA-only4.90885. These are
finite-K32 observed sets, not complete policy supports or creativity measures.

At8k U_valid/K32 is SM.2592773 vsSA.2834310; U_novel/K32 is
SM.008984375 vsSA.0087890625; V_novel/K32 is SM.01372070 vsSA.01259766.
SA produces more observed distinct valid routes but not more valid novel yield
in this endpoint. Known-valid proportions are95.9911% vs96.6105%; pass@32
84.7917% vs84.6354%. These retain the reviewed evaluator's training-support
definition and mixture aggregation; unequal quality remains a confound.

SA entropy at8k is.4166121 vsSM.4304223; oracle entropy.3722895.
Smaller average entropy alone is not calibration. SA mixture KL/Brier are
.3834391/.1597537 vsSM.3955592/.1618029, but challenge KL is worse
(.6220274 vs.5890637), whereas routine KL is better(.3237920 vs.3471831).
This is not uniformly better generalization across strata.
