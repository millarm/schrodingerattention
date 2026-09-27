# Exact implementation acceptance and inference authorization

2026-09-27. Astra accepts Sol's exact implementation PASS in
reviews/06-implementation.md and the 16 passing targeted tests. The adjacent
production-acceptance.json binds the review SHA and all 25 source identities.

Luna may now execute the four fixed inference owners sequentially: 2201 softmax,
2201 SA, 2202 SA, 2202 softmax. Each decision must be fresh, bind current ledger
EOF and the acceptance JSON, and use the reviewed external watchdog. Per-owner
envelopes remain 300 seconds for softmax and 360 for SA, within stage B 1,440.
Proceed to the next owner only after COMPLETE, accounted charge, verified cleanup
and no reservation lock. Stop on any failure or uncertainty; no automatic retry.

After all four owners complete, Luna may run the one reviewed 240-second stage-D
audit under the same acceptance and a fresh decision. Preserve raw artifacts,
checkpoints, failures and all accounting. Freeze outputs for Sol results review;
do not call the scientific result accepted before that review.

The independent 1,800-second cap remains unchanged; stage A has used
18.360494249965996 seconds. No training, final-test access, calibration, tuning,
new seeds or 200k continuation is authorized.
