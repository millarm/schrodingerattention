# Narrow analysis recovery — exact review requested

Approval: `astra-recovery-approval.md`; scientific plan unchanged.
Source hashes:

- analysis.py: `1d7d2339c382fd4cea6b76b84a5ca6074ca01561a7fb2c9df9e76fee1fc0758a`
- job.py: `8d695dc4383024b85db06eb03d25937d786787b32610dea42905c3e48c5bef92`
- tests: `f6671c15b064055ce1c73baca2c3d6cab2d7aac4a6ff75cf082a6043d8e87c9e`

All five prior review items addressed. Direct hex decoding retained. Event
checksum binds within-map order to immutable manifest-verified original records
and prepared input identities; every route's validity is corroborated against
the exact distance/movement oracle. This does NOT create independent historical
start/goal identifiers; the approved all-invalid permutation limitation remains
explicit in output. Negative same-map mutation breaks the event checksum.

Raw valid/novel sets, normalized Q/pass@K/U_valid/U_novel/V_novel are retained
with equal-map summaries. Aligned state CE/KL/Brier/nonoptimal mass are computed
from retained p/q and included per-state/per-map/stratum. Frozen support and old
SM ABC results are checked against their exact accepted hashes, support equality
and checkpoint hashes. SM rows/q are checked against frozen banks, stored with
new SA results, and explicit paired proper/route differences emitted. No cohort
selection or SM full-validation inference occurs. QC still uses only two new
SA temperatures, with frozen selection/tolerances.

Eight tests pass (4.157104125 seconds full wall). Prior failed test is charged
with a disclosed five-second allowance; code and tests fixed before this review.
The real ABC fixture uses saved SM probabilities as an identity comparator,
not new SA inference, and asserts zero paired deltas and exact 768/144 counts.

Proposed one command: `.venv/bin/python -m execution.paired_behavior.job`.
Owned original root/ledger, fresh name `paired-behavior-analysis-001`, 296-second
deadline plus four seconds owner allowances. Source frozen pending Sol PASS.
Cumulative debit: 2002.434070545030/7200; no production analysis has run.
