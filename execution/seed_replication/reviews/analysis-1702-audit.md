# Static audit — seed 1702 analysis output

**Verdict: PASS (first-output audit; not the final four-seed statistical review)**

## Immutable output

- `analysis.json` SHA-256: `eac3186ce22771a254259c959d75184e2c6c90111e73d58865015fdbfa6cb9c2`
- `attempt.json` SHA-256: `449a29b2b13d721c341555445ebe835fed75e5621efe73086ab5240a024ca9ff`
- `output-manifest.json` SHA-256: `02d54607791624fc5deee68d7970e2706a311e79e93baab6f2c65f51484ce092`
- reviewed analysis source: `cbf8d19b31b429a91e48ad3dba2e2079ab0245d9811c92ad9e0e851bc8ffa3dd`

The manifest entries for `analysis.json` and `attempt.json` match the independently observed file hashes. The owned attempt is terminal `COMPLETE`, stage D, with `45.02631954103708s` elapsed and a single `49.02631954103708s` charge including the accepted allowances.

## Identity and shape checks

The result binds seed 1702, the accepted prepared/source/manifest and train/validation/test selection hashes, reviewed wrapper and plan, exact softmax and Schrödinger decision hashes, amended resource-table hash, distinct initial/final checkpoint hashes, the common shared-initial tensor digest, and one exact 8,000-update paired batch-prefix digest. Final checkpoint identities have the expected seed, mode, update 8000, source, config and input IDs.

Stored full-validation summaries are present at 1k/2k/4k/8k. The 8k record contains the primary difference, paired state metrics, route-set metrics and retained raw route summaries required for final aggregation. A/B/C each contain fresh softmax and fresh SA results with 768 proper-score states and 144 problems per model; no discovery-model substitution is present. The output also binds every reviewed direct helper source and states the historical all-invalid route-order limitation.

## Numerical checks

- Full-validation primary SA−SM T1/K32 quality: `-0.025211588541666663` (−2.5212 percentage points).
- A: SM `0.5753038194444444`, SA `0.5831163194444444`, difference `+0.0078125`.
- B: SM `0.48784722222222215`, SA `0.498046875`, difference `+0.010199652777777846`.
- C: SM `0.4420572916666667`, SA `0.42816840277777773`, difference `-0.01388888888888895` (−1.3889 points).

The quality-control target is SM T1 `0.38404947916666665`. SA qualities are `.43115234375` at T=.75, `.358837890625` at T=1, and `.29132486979166666` at T=1.25. T=1 is correctly selected as nearest, but its absolute mixture gap is `.02521158854166665 > .02`; therefore `matched=false` is correct and seed 1702 supports no quality-controlled novelty claim.

The output shape and identities are suitable for the later frozen four-seed aggregation. This audit does not interpret between-seed statistics and does not authorize outcome-dependent changes to the remaining fixed sequence.

Only static file/hash/JSON reads were used; no Python, tests, inference, or training were run while seed-1704 training was active. No ledger row was appended concurrently.
