# Production profile 001 — runtime gate for Sol review

Prepare-001 session34159 and profile-001 session12385 were each launched once,
polled to explicit exit0. Canonical attempt statuses COMPLETE and output manifests
are retained. No weights are reused from profiling seed1699. No test inference.

- Profile result SHA256: e2073da106b4ad32e0dd5f9ded915dbd7ee60fe737a24e6d87abb7ada2f0bafb
- Profile output-manifest SHA256: af6c7b796b1c6723dcd531a97b827075a0bfd61613378dc30267c653b48db635
- Decision SHA256: 8cb2e46771f5c0f04a590cb31e6d97d0e53611408dca086936170f6e6b71a007
- Prepared SHA256: 10e5f96a98b4dcb944cf81b65eb43eb4ed5a8c8211bf9d1f55af2f0bc4814e49

Owner charges: prepare11.824842792004347, profile16.916736540966667 seconds,
each including explicit startup/finalization allowances. Global1333.405415169971;
A410.401817916971. Remaining global5866.594584830029, A289.598182083029.

Actual profile: both models70540 parameters;5warmup+20measured each;96validation
problems on6maps;64training+128validation probe states. Hermiticity maximum0,
unitary4.76837158203125e-7, row3.5762786865234375e-7, below frozen thresholds.
Profile end-to-end12.907836832979228 seconds. Separate artifact/ledger overhead
and charged allowances remain recorded; do not equate this with entire tool time.

## Prospective tighter work-unit forecast (no source/data/science change)

The retained automated bound is3231.807160494587 seconds, of which
2553.8047955953516 is77 conditional decoding candidates each costed as an entire
endpoint (currentgreedy/currentT1/owninitial/uniform/proper). That overcounts
three unrelated rollout operations per candidate. Preserve this original bound.

For a reviewed alternative, cost every one of the same77 candidates as a full
fresh K32 rollout PLUS a proper-score bank pass, using the maximum measured
seconds/problem across BOTH architectures and all three families, then the same
1.5 factor and512 physical problems. No cache discount. Maximum K32 rate is
0.013818565124893212; maximum proper rate0.00018377734340901952.
All original serialization, setup, checkpoint, seven-endpoint/model, probe,
ledger, tracing,120audit and30finalization costs remain unchanged. No quality
outcome is consulted. This is a resource-only unit correction, not reduced work.

Sol should independently verify manifests, exact accepted source/input identity,
exclusive timings, numerical results, budget and arithmetic. Approve this bounded
forecast or identify an omission before any paired1701 command. If accepted,
authorize both unchanged1000-update models under B2000, softmax then SA. Preserve
the original automated bound alongside the independently reviewed alternative;
all later learning/temperature/power/cohort gates still apply. No pilot test scores.
