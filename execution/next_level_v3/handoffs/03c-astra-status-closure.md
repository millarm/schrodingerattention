# Astra narrow runner correction handoff

User-approved exception2026-09-16; Terra inactive. Frozen source:

- Runner SHA256 `6fa238c1192527cb9b470c22229ac9356d73402b7422d9d2f5a097aac6f3faf9`.
- Test SHA256 `72e8ef684dd82c9845a22f31b0871f7693d9b1a9b0d79024c242344d5e9eaea7`.
- Unchanged accepted data SHA256 `4aa4779877781f2b0211397c3938185ad6ec5154040fecdef3d9f7eac7e84f08`.

Tests-first exact command `.venv/bin/python -m pytest -q tests/test_productive_diversity_v3_runner.py`
returned33pass/2fail, exit1, full wall4.22484525s (tool chunkbb130e).
Only the two new real second-proposal interruption variants failed. Corrected
same command returned35pass, exit0, full wall3.814176125s (chunke922e9).
No yielded sessions and no production invocation. Both charged once at ledgerEOF.
Current conservative debit548.232812669s, new-v3 debit104.848293667s.

`ProposalStatuses.finalize(interrupted)` now derives a copy from ordered callback
observations; no external active/first-ranked parameter or mutation of observed
states. Scientific failures resolve their proposal; a full PASS or failed write
terminates traversal. First unresolved proposal receives one UNKNOWN missing
callback; all other missing stages are NOT_EVALUATED. A normal return never
fabricates COMPLETE. Existing artifact hashes and callback decoder unchanged.

Assertion mapping:

- `test_03b_real_valroutine_three_is_scientific_failure`: entire stage map,
  I failure plus nonempty real evidence/selected rows, L NOT_EVALUATED.
- `test_03b_first_window_training_failure_then_real_second_pass`: exact four
  first-proposal future NE, second all COMPLETE, exactly two proposal records,
  exactly five second-stage artifacts and no second unvisited stage.
- `test_03c_real_first_failure_second_interrupted_third_unattempted`: two genuine
  oracle cases before/after second training callback, all three exact stage maps,
  first I supply failure, third empty artifact map, all artifact byte hashes,
  correct second artifacts, DEADLINE_FAILED/FAILED attempt, exactly one charge,
  owned lock removed. Only callback injection and internal ranking/count seam;
  no mocked scientific outcome.
- All previous provenance, stage/result faults, CLI, budget, real pipeline
  and one-proposal regressions continue passing.

Sol exact-version review required. No accepted scientific source or criteria
changed; old reviews/blockers preserved. Next step only if PASS: single frozen
production run then bounded spec04 results audit and dataset-only stop.
