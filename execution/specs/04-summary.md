# Block 4 — reproducible summaries

Prerequisite: Astra acceptance of Block3 audit or explicit cap-limited outcome.
Terra may create `schrodinger/summarize.py`, `tests/test_summary.py` only if
needed to verify nontrivial aggregation, `execution/results/summary.json`,
`execution/results/summary.csv`, `execution/results/learning_curves.png`,
`execution/results/summary.md`, `execution/handoffs/04-summary.md`, and logs.
No measured raw artifacts or earlier implementation changes.

Binding audit amendment: Block3 retained equal-update endpoints are internally
coherent descriptive evidence, but controlled timing/equal-time comparison is
INVALID due unproven process non-overlap, duplicate launches and overwritten
attempt artifacts. Preserve raw timing/equal-time records with validity labels;
do not present throughput/overhead/equal-time quality as established comparative
efficiency. Mark those endpoints unavailable for scientific conclusions. No
reruns authorized. Report eight training attempts, failed pair and limitations
from03-run-provenance.md and Sol audit. Original frozen gate remains unchanged;
invalid timing and mean validation XOR<0.80 force INCONCLUSIVE independently.
Figure prioritizes examples axis; training-time plots if retained must clearly
say 'uncontrolled recorded clocks; comparison invalid' and never support claims.

Produce CLI reproducible aggregation from raw results. Include per-seed and
sample mean/SD ddof1 for per-condition per-op accuracies and CE; paired SA minus
baseline differences; matched-update timing ratio/throughput; separate equal
training-time checkpoint IDs, actual clocks/slack and metrics; end-to-end
timing/RSS caveats; first validation target examples90/95 with right censoring,
relative reduction only when all paired targets observed; effective dt/gamma
and numerical maxima; intervention deltas against corresponding SA weights.
Figure: validation XOR accuracy and CE against examples and training seconds,
show individual seeds, clear architecture legend, axis units, no smoothing
or interpolation used in gate. Report all predeclared screening checks as
booleans and the failure-to-learn/missing-evidence guard, not posthoc choices.
Astra owns final interpretation and research recommendation in a separate
final_report.md after Sol verifies summaries.

Validate aggregation against raw integer correct/total counts; include exact
source hashes and command. Sol independently recomputes key summary quantities
and reviews plotted data provenance. <=120 elapsed compute seconds and global
cap guard. Do not create tests that merely mirror obvious code; a small fixture
with hand-known paired mean/SD/censoring is warranted if aggregation complex.
Handoff exact code/result hashes, commands/exit codes and limitations.
