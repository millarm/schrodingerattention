# D1 repair static review — exact frozen version

## Verdict: CHANGES REQUIRED

This was a static-only review. I did not import or execute the implementation, run tests, load checkpoints, perform model inference, launch production, or write the accounting ledger.

Reviewed exact bytes:

- handoff: `15ea2f8632068f7a6f62435e16f8203c7233d8dd9bcbc3ca891f0a4409acafc9`
- source: `e1751fa198a747bfc68a788e6dc8bf61e40b8001048bf6b5145ee17951623fd2`
- watchdog: `08deac45b82de6f3636d9f61dabf226d13135e257af6a84ff64313c838d2eb7a`
- tests: `671e15f2b5c1f61bda60f40a43abfddadd22e6317de699532da2d618b1cdd7ac`
- approved plan: `370650b044b51eab8c331b54718e0af85be9dfa75758bab695e23cc4312d2a31`
- recovery approval: `36431d4b7ac2686fa3282d5de419e1ce3d3a55db1a75b5e065e2acf7448378bb`

## Blocking findings

### 1. An uncertain watchdog fallback can be promoted to a successful producer-owned attempt

`d1_watchdog.py:218-242` classifies every stage-D row with the owner output path as an `owned` row. That includes the watchdog's own `UNCERTAIN_FAILURE` fallback created at lines 220-225. On a later reconciliation, a caller can supply an `attempt.json` copied from that fallback row with status changed to `COMPLETE`, plus an `output-manifest.json` containing only the hash of `attempt.json`; reconciliation then returns success. The literal test at `tests/test_difficult_problem_solving_d1.py:296-309` explicitly constructs and accepts this promotion.

This violates the approved distinction between the actual `OwnedAttempt` charge and the one terminal uncertain fallback. It also permits watchdog success without validating the actual D1 result, complete cell index, endpoint artifacts, or their manifest entries.

Required repair:

- Give fallback rows an identity/class that cannot be mistaken for an `OwnedAttempt` row, and exclude them from owner candidates.
- Treat an existing uncertain fallback as permanently non-successful and non-reconcilable into a producer success.
- For an actual owner, require the exact owner row/attempt identity and a complete, internally consistent terminal artifact set. At minimum validate the terminal attempt status and manifest binding for the required D1 outputs, rather than accepting an `attempt.json`-only manifest.
- Reverse the current synthetic-promotion assertion and add literal negatives for fallback-plus-forged-attempt, incomplete manifest, altered `d1.json`, and altered/incomplete cell index.

### 2. Review authorization is authenticated by a loose substring, not an unambiguous verdict

`d1_watchdog.py:136-145` trusts the decision record's verdict field and merely searches the review text for a success word and the three hashes. It does not parse a unique verdict declaration or bind the review to an expected review location/type. A changes-required review that mentions the success word in discussion can therefore authorize a command if the separately written decision record claims a successful verdict. The test at `tests/test_difficult_problem_solving_d1.py:311-330` only exercises a freely created text file and does not cover a negative-verdict document containing that word.

Required repair:

- Bind each phase to its designated review artifact (or a comparably strict approved path/type contract).
- Parse one unambiguous machine-readable verdict field and reject conflicting/multiple verdicts; do not use substring presence.
- Add a literal negative test using a changes-required review that contains the success term elsewhere and a decision that falsely labels it successful.

### 3. The production fallback debit omits the watchdog's disclosed finalization allowance

`execute()` computes `charged_seconds = elapsed_seconds + FINALIZATION_ALLOWANCE` at lines 282-284, but passes only `elapsed_seconds` to `reconcile_production()` at line 295. When no producer charge exists, lines 220-225 append that smaller value. The development path records the disclosed allowance, while the production fallback silently does not. The fallback test calls reconciliation directly with `.2` and never checks the terminal charge contract.

Required repair:

- Pass the already computed `charged_seconds` into the fallback reconciliation (while retaining measured elapsed separately), or document and enforce one consistent approved accounting rule for both paths.
- Add an execute-level production fallback test asserting exactly one row and exact agreement among terminal evidence, fallback row, allowance, and envelope.

## Non-blocking observations

The exact source materially improves the requested producer contract: it compares the retained/current pair bindings, preserves K=32 raw attempts separately from greedy evidence, writes immutable endpoint files plus compact shared indexes, prevents selection from copying raw bags into the final report, and keeps the 296-second inner limit inside the external 300-second production envelope. The literal owner failure tests and the 120-second development preflight are also directionally correct. These improvements do not close the three watchdog boundary failures above.

No smoke, suite, or production command is authorized by this review.
