# 512-map pool expansion — complete dataset constructed

Status: **production PASS and independent results-review PASS**. The complete
dataset is ready under the frozen construction contract; see
[Sol results review](reviews/02-results.md).

The single frozen expansion to 512 canonical maps per family produced a complete
dataset on the 14–16 route-length window. No neural training or attention-model
comparison was performed: this is benchmark construction, not evidence of learned
creativity, useful uncertainty or architecture advantage.

| Split | Maps | Problem pairs |
|---|---:|---:|
| Training (homogeneous I/L) | 64 | 1,024 |
| Routine validation | 24 | 384 |
| Mixed challenge validation | 8 | 128 |
| Routine test | 96 | 1,536 |
| Mixed challenge test | 32 | 512 |
| Total | 224 | 3,584 |

Each map contributes 16 problems with length quotas 6/5/5 at lengths 14/15/16.
The 40 mixed challenge maps provide 640 problems with multiple exact valid shortest
solutions; each problem satisfies at least 4 structurally novel solutions and a
novel-solution fraction between 1/4 and 3/4 relative to complete training-suffix
support. This describes oracle solution opportunities, not model-generated novelty.
Routine problems have no novel solution signatures under that same definition.

## Controlled expansion and retained history

Only the pool target changed from 256 to 512 per family; 12×12 geometry, eight
components, streams, 200,000-trial cap, global-ID algorithm, shortlist cap of 64,
length windows, ranking, split
counts and scientific gates stayed fixed. Larger pools changed global sorted IDs,
shortlists and training support, so this is a new frozen construction, not simply
adding seven missing maps to the prior partial dataset. Prior source/plans/protocol,
ledger and raw artifacts were preserved unchanged.

All 1,536 maps were obtained within the cap. The full original ranking was run anew.
12–14 failed mixed-validation supply; 14–16 passed every gate; 16–18 was not evaluated
after the first complete PASS. No favorable duplicate run, pool refill or tuning.
See [process record](production_execution_record.md) and
[raw summary](attempts/feasibility-001/summary.json).

Primary manifest SHA256:
`305a9dd782befa9209942a2f52ebc0ba31d9d7ca61c913ecfb69fa5cca466395`.
Sol reviewed the exact new implementation before generation in
[implementation review](reviews/01-implementation.md). Original Astra/Terra/Sol
roles were maintained; one fresh-context same-model Terra completed a previously
partial scaffold. Two development-record UTC fields were manually entered
incorrectly; an append-only clarification marks them invalid. Actual command
order/wall durations remain supported. Production UTC/exit evidence is generated
by the runner and unaffected; no old records or charges were rewritten.

## Budget and audit

Final conservative operational debit: 923.003597253 seconds of 7,200 (15.38 minutes);
cumulative dataset-stage debit: 479.619078251 seconds of 1,600. This iteration used
177.872023626 seconds including allowances: development 3.595638417 seconds,
production 148.691623834 seconds plus 2 startup, audit 20.584761375 seconds plus 3
startup/inspection. Prior allowances remain included, so operational totals are
not all newly measured compute. The remaining overall budget of 6,276.996402747 seconds
is unused; this dataset-only request does not authorize model experiments.

The independent retained-artifact audit completed with exit code 0 and zero errors.
It verified inclusion of all 256 old canonical maps and equal 16-row draw prefixes
in each new 512-map pool, exact source/output hashes, saved-inventory ranking, all selected-row
metadata/quotas, cross-split disjointness, support hashes, and required split
counts. An exhaustive metadata pass also checked pair uniqueness and stored
routine/challenge novelty predicates for all 3,584 selected rows. All 60 sampled
route/novelty facts and 32 sampled q-target states matched
independent recomputation, including failed-prefix evidence. Oracle validation
was sampled, not an exhaustive replay of every route or reconstruction of all
training support. No pools/proposals were regenerated.

[Raw audit](audits/feasibility-001-audit.json) SHA256:
`2930e1f90c3df0a1a40e5da661f3bf6fc98f3741549b74020469b7ca762115a0`.
Independent review SHA256:
`81fa7253e5e69d5b478227fab5355a098c18ed9d0b4d40155445f9a69e030110`.

## Decision boundary

Stop after independent dataset review. A successful dataset gate makes a future
baseline learnability pilot possible; it does not show usable learning, productive
diversity or an advantage over softmax. Such model experiments require the next
explicit execution authorization and their frozen learning/power/runtime gates.
