# Sol05 revision supplement

Current module SHA-256: `84f791992b81dbbebea66cba793f27481086b33335a2287359fd38d567e56e0a`.

Current tests SHA-256: `b0abb80bcef5b91db37eea7bdf31051793112c0a6753a2956a451433026181ce`.

Focused command exited 0 with 20 passed; final wall 0.787343083s is ledger UUID `101b02a1-d639-4ae3-8adb-a2704243bfb0`.

`test_validate_inventory_bad_n_endpoints_family_identity_M_length` covers bad n, family, duplicate identity, canonical mismatch and key/length mismatch. `test_rejected_map_preserves_prior_accepted_rows_and_noncommit` retains accepted first-length rows, does not commit, and proves no third length visit. `test_heldout_support_key_cache_and_challenge_boundaries` covers accepted endpoints and rejected 3/16, 13/16, 4/20 fractions. `test_orchestrator_stage_order_and_scientific_advance_isolated` spies one validation pass over two proposals and asserts exact cumulative exclusions.
