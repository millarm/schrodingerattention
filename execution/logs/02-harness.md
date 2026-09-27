# Block 2 harness log

Smoke, profile, and full pytest all exited 0. Final pytest: 27 passed in 0.89 seconds (3.0 seconds conservatively charged including startup).

Final SMOKE is non-measured: four updates/model and 16 examples/condition. Fixed-batch loss decreased: softmax 0.721679 to 0.699578; Schrödinger 0.721672 to 0.699577. It exercises validation, checkpoint save/reload equality, final condition metrics, and dt=0 evaluation.

Throughput-only profile used five warmups and 20 timed steps/model without quality-based choices: softmax 24686.87 examples/s; exact 5375.89 examples/s. In-process elapsed: smoke 0.146209s, profile 0.458757s, final smoke 0.139713s. See compute_ledger.jsonl.
