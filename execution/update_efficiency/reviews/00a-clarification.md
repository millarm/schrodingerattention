# Sol static clarification review

**Decisions record SHA-256:**
`c97556f38de6f443cfdfb28486839599d11b65801cd1cdabe5e7375066c2f034`

**Verdict: CONSISTENT WITH PLAN/SPEC PASS.**

Static clarification review only. I read `decisions.md`; I did not inspect or
execute implementation, import project code, run tests/training, inspect a
final-test payload, or write a ledger entry.

The decisions record closes the two literal acceptance details from
`reviews/00-plan.md` without changing the frozen science or expanding scope:

1. It fixes the canonical COMPLETE metadata lineage to
   `execution/model_training_comparison/prepare-001` and binds exact hashes for
   `result.json`, `output-manifest.json`, and `attempt.json`. It maps the nested
   retained provenance and bank-hash fields to the accepted input identities,
   while treating the test identity as copied metadata only and explicitly
   forbidding reads of `prepared.json` or test payloads.
2. It fixes validation q/order evidence to the named, hashed COMPLETE
   replication-1702 softmax result and limits its use to the update-0 validation
   proper rows. Exact row identity/order/q comparison plus the selected hash and
   derived candidate/q identities is an integrity cross-check of the already
   selected validation bank, not outcome-based cohort selection.
3. It constrains the prospective STAGES override to one command, requires a
   check of the imported original constants, and restores the imported table in
   `finally` on success or failure. The driver enforces the amended caps locally.
   That leaves accepted source and unrelated/future command policy unchanged.

The record also preserves the prospective seeds, target, first-pair technical
gate, global ceiling and no-outcome-dependent continuation rule. No new review
cycle is needed for these clarifications. Exact implementation and tests still
require the separately mandated frozen-version Sol review before production.

