# Independent training-only audit — paired Schrödinger continuation

## Verdict: PASS

The single reviewed Schrödinger resume completed successfully and preserves the exact paired-training lineage required for later exploratory analysis.

Reviewed immutable artifacts:

- result: `eaee8a5f693742ac482b066f3fbdffe3615096583eb1736d3fb43f00a78417d3`
- output manifest: `2b942eb0d7f94262b7c320943a0c28eb249dc5eeaec331d673627b3bb52d7209`
- terminal attempt: `4c4183a3f71b02a94b73f452db99508dc4d4a8c0c2a30a43e2d87dc44ceb84b8`

### Independent checks

- Every output-manifest entry exists and matches its SHA-256. The terminal attempt is `COMPLETE`; the neutral ledger charge status is accounting, not an incomplete run.
- The resume begins at the accepted seed-1701 Schrödinger update-1,000 checkpoint `61850806...`, retains source `bf7efbdd...`, the accepted configuration/prepared/data identities, initial checkpoint `0ef4eb59...`, and initial model identity `ebfcd400...`.
- Concatenating the original Schrödinger updates 1–1,000 with the resumed updates 1,001–8,000 yields exactly 8,000 unique update rows. Every one of their batch digests equals the corresponding digest in the concatenated softmax 1,000/2,000/4,000/8,000 history: zero missing updates and zero mismatches.
- All 81 Schrödinger checkpoints from initial through update 8,000 form an exact 100-update hash chain. Every checkpoint retains the expected seed, mode, update, source and initial identity. The final file hash `a7e6050a...` equals the result's final checkpoint hash.
- Sampler states are exactly equal between softmax and Schrödinger at every saved checkpoint from update 0 through 8,000. All 40 shared initial tensors are byte-equal; architecture-specific initial model hashes remain correctly distinct.
- Scheduled resumed events are exactly 2,000, 4,000 and 8,000. At 8,000, the retained validation mixture has greedy quality `0.5671875` and T=1 quality `0.3716634115`; the corresponding softmax values are `0.5385417` and `0.3422526`. These are descriptive one-seed differences, not evidence of a general advantage.
- Schrödinger cumulative training-core time is `126.8511663` seconds versus softmax `38.8204422` seconds. Historical wall attempts were not run under a perfectly isolated timing schedule, so equal-update paired evidence is primary and wall-time comparison remains descriptive.

This PASS covers the completed training lineage only. The additive behavior-analysis implementation and any further inference remain separately review-gated. No test release or confirmatory architecture claim is authorized.

Independent read-only audit charge: `3.9` seconds, UUID `C39AEC5D-80A0-44E1-B9FD-8B2283B495C3`. Post-audit global debit is `1981.68696642003` of `7200` seconds.
