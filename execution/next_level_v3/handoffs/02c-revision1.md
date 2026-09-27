# Recovery B revision 1 handoff

Frozen source SHA-256: `4aa4779877781f2b0211397c3938185ad6ec5154040fecdef3d9f7eac7e84f08`.

Frozen test SHA-256: `222edc7e152d1f2a1edbe15ac792f64d30a2423cc2c90010fd39f5323b4a4c09`.

Fixture SHA-256: I8 `dc0e76fc9b992a6c4e6acc53c0fa6be7b28605491b00bc2bf55513f01350950d`; L8 `b804bb2a1e9a7dbdac60aa8bc8012941f1e85297f09d4e068c5b839a103ec653`; mixed `b9839045acf41109292ac18dbb528f276d3f0c9ee0f70c3a1f2ba819827759f4`.

Frozen expected table: I `(d12,M21),(d13,M28),(d14,M28)`; L `(d12,M28),(d13,M75),(d14,M122)`; mixed `(d12,M148,Mnovel89),(d13,M84,Mnovel35),(d14,M140,Mnovel60)`.

Focused command `.venv/bin/python -m pytest -q tests/test_productive_diversity_v3_data.py` exited 0: 32 passed in 1.10s; final wall 1.189840834s is included in ledger UUID `0d79bb5b-73aa-4a57-bab4-aee718f7e309`.

Negative assertion mapping: `test_real_on_use_bfs_distance_or_count_mismatch_is_technical` covers real distance/count mismatch; `test_excluded_map_never_calls_oracle_or_commits` covers leakage exclusion; `test_three_proposals_scientific_then_pass_stops_and_preserves_evidence` covers retained failed evidence, second PASS, and uncalled third; `test_technical_first_training_never_advances` covers technical abort before later proposal; `test_recovery_b_unmocked_eight_record_composition` asserts literal M table plus the real positive path.
