# 03b proposal-status model handoff

Frozen runner SHA-256: `eaeca121f8abe6e30fc66656b68112b810223faf39cdcb7cb48bbbaff8e15f4b`.
Frozen test SHA-256: `46f14d562a5b5e66a7ffd7aa53f87b9ab3c8bc5f185ddba308f7210c5efcc00e`.

Final focused command was `.venv/bin/python -m pytest -q tests/test_productive_diversity_v3_runner.py`.
It exited 0: 33 passed in 3.57s, full wall `3.676722208s`. No production command ran.

Actual 03b evidence tests:

- `test_03b_real_valroutine_three_is_scientific_failure` exercises a real
  one-proposal held-out scientific failure.
- `test_03b_first_window_training_failure_then_real_second_pass` preserves the
  failed window 14 proposal and real window 12 PASS separately.
- `test_03b_real_training_callback_then_deadline_before_next_callback` persists
  actual training then asserts first missing stage UNKNOWN and later stages NOT_EVALUATED.
- `test_03b_proposal_status_helper_unattempted_and_unknown_payload` asserts
  unattempted retained proposal NOT_EVALUATED after early PASS and unknown callback rejection.
- `test_03b_manifest_has_exact_sources_reviews_specs_and_fixture_hashes` asserts
  fixed runner/data/helper/test/plan/protocol inputs, all current v3 specs/reviews,
  and the three recovery fixture byte hashes.

The model is proposal-keyed, binds callback artifact hashes, and leaves accepted
core data unchanged. Process deviation: the helper was implemented before the
specified tests-first baseline. The later test-only matrix truthfully recorded
31 passed/2 failed (unknown outcome and missing fixture provenance), followed by
the single consolidated source fix and final 33-pass verification.

03b ledger records: `03c7332f-1acb-43f1-bbfd-d4c892b0d102`,
`a3b61a02-1704-47d1-8b6b-527923b83592`, and
`2c2a32df-e879-4df5-a019-cf992e7f31aa`. The first aggregate is overstated by
`2.999554000`; the zero-charge correction record preserves history. Audited net
for those two charged aggregate rows is `20.183764875` seconds, not `23.183318875`.
