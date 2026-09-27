# D1 static correction — 2026-09-27

All three exact Sol findings are addressed for static re-review. No runtime,
imports, tests, model work or ledger mutations occurred. Scientific source
`d1.py` is unchanged from the first Astra static handoff.

|Artifact|SHA-256|
|---|---|
|`d1.py`|`e1751fa198a747bfc68a788e6dc8bf61e40b8001048bf6b5145ee17951623fd2`|
|`d1_watchdog.py`|`2b3fed56e07da5a33c122afa10e9cc5b77df0df77ec492db0bfaf4887708a8c8`|
|`tests/test_difficult_problem_solving_d1.py`|`a66d67d1b6a89633e1daeda97d7c0c839848ce9cdc618f1724eee02efa17f842`|
|Unchanged ledger|`7f62600c2ae6bd91a53cdcdc0769a4c6e2ab5fdd6523758592a68ec6e1f29782`|

1. Watchdog fallback uses its own `watchdog_uncertain_fallback` kind. Any prior
   fallback remains permanently unsuccessful, even if a forged COMPLETE attempt
   and manifest appear later. Actual owner reconciliation requires the accepted
   owner row class/UUID/allowances and matching terminal identity. COMPLETE
   additionally verifies bound D1 result, complete 40-cell index, 512-row panel,
   provenance, four shared bindings and eight greedy artifacts, plus every cell
   hash/reference. Existing charged artifact failure remains a STOP without a
   second debit. Tests reverse the former promotion assertion and add missing
   manifest, altered result, altered index and rebound incomplete-index negatives.
2. Review authority is restricted to designated static/implementation paths.
   Exactly one machine-readable `D1_REVIEW_VERDICT: PASS` field is mandatory;
   conflicting human verdict headings, duplicate fields, wrong phases/paths or
   missing exact hashes are rejected. Tests include CHANGES REQUIRED containing
   the word PASS elsewhere, duplicate declarations and an undesignated PASS file.
   Sol's new review must include that exact machine-readable declaration if PASS.
3. Execute passes its already computed charged total (measured elapsed plus the
   disclosed within-envelope finalization allowance) to production fallback.
   The execute-level test runs a tiny failing child and asserts one fallback,
   exact terminal/ledger/allowance equality and no reservation release/retry.

Sol's prior review is preserved byte-identically at
`d1-astra-static-review-00-blocked.md`, SHA
`e311d8c3baa355a8e7bac39309c73120d2ab43ff0e4d909c207d9ce3d5f646e7`.
This handoff makes no passing-test claim. Await exact static PASS before the
bounded named smoke. Fresh 120-second development and 300-second D1 remain unspent.
