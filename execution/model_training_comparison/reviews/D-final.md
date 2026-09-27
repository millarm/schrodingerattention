# D independent final-results audit

## Verdict: PASS

The completed exploratory study is internally coherent, stops at the frozen usability gate, and supports the limited conclusions in `final_report.md`. It does **not** establish a Schrödinger novelty, usability, or creativity advantage.

### Artifact and provenance checks

- Independently verified all entries in the output manifests for the three softmax continuation attempts and six equal-time evaluations: zero missing or mismatched files.
- Every audited result binds source hash `bf7efbddb88bff06029369cba071d79f17340d701928b7f527baa6df7e517329`, prepared hash `10e5f96a98b4dcb944cf81b65eb43eb4ed5a8c8211bf9d1f55af2f0bc4814e49`, dataset manifest `305a9dd782befa9209942a2f52ebc0ba31d9d7ca61c913ecfb69fa5cca466395`, and the same frozen training/validation/test identities.
- Resume arguments form the exact intended chain: update 1,000 hash `329fcd95...` starts the 2,000 attempt; update 2,000 hash `24b25c98...` starts 4,000; update 4,000 hash `af2d6912...` starts 8,000. All preserve the original softmax initial checkpoint hash `5bf5f49d...` and shared initial identity.
- Result hashes match `raw_summary.json`: softmax 2,000 `9411cc4d...`, 4,000 `f9e0cfc5...`, 8,000 `ad76ab4e...`; equal-time softmax 200/400/700 `6cf17d81...`/`139f15e5...`/`e6a28b38...`; equal-time Schrödinger 100/200/300 `7725c809...`/`e9be9ea8...`/`01f717bc...`.
- Frozen summary artifacts reviewed: `raw_summary.json` SHA-256 `3c25d33ee35cc988780c44a5740a8f2fea0ad6d7c6f7167529b6daa92da0990b`; `learning_curves.svg` `56213df4a26d0dc14789209fec5e17eb5eb4a1771634e52c0d0dcb4d7c81fc6d`; pre-review `final_report.md` `92b8c9b7009190e626fbb62eabc28c18579e79251a7b899904e0b0f6faa5d4cd`.

### Scientific stop and censoring

Softmax validation at 2,000, 4,000, and 8,000 updates has greedy quality `0.5364583`, `0.5364583`, and `0.5385417`, with T=1 quality `0.2713542`, `0.2959798`, and `0.3422526`. Thus neither mandatory `0.80` greedy nor `0.70` T=1 gate passes by the maximum authorized update. The prescribed stop at 8,000 is correct despite remaining budget.

The 80%/70% crossings are right-censored beyond 8,000 for softmax and beyond the observed 1,000 updates for Schrödinger. The 90%-quality operating point, power pilot, confirmatory seeds, quality-matched comparisons, and model-bearing test evaluation remain `NOT_EVALUATED`. The report handles these as absent evidence rather than failures or imputed crossing times.

### Equal-time evidence

The six new evaluations use exactly the checkpoint selections frozen in B1. At the best-matched final target, softmax update 1,000 at `4.7501107493` core seconds is compared with Schrödinger update 300 at `4.7270147420` seconds (0.49% Schrödinger slack): T=1 quality `0.2116699` versus `0.0989095`, and Brier `0.1723926` versus `0.2280114`. Earlier coarse selections retain their required slack disclosures, including the initial Schrödinger checkpoint at c/4. There is no interpolation.

These validation-only, one-seed results descriptively favor softmax in measured compute efficiency. They do not justify an equivalence claim, a general architectural ranking, or a creativity claim. Schrödinger nonetheless exhibits genuine learning from initialization; its mechanism is measurably active, but no downstream benefit is established.

### Report check and limitations

`final_report.md` accurately distinguishes equal-update from equal-time evidence, validation from unreleased test data, continuation from paired exposure, and mechanism activity from benefit. It correctly discloses the missing fixed training-bank proper-score curves and avoids treating minibatch training CE as a controlled generalization comparison. Its recommendation is explicitly a future proposal, not work authorized or performed in this cycle.

The replication unit is one paired seed. No multi-seed uncertainty estimate or confirmatory inference is possible. All novelty numbers are descriptive validation metrics under the frozen sampler.

### Budget

Independent final audit charge: `4.5` seconds, UUID `1F2698BF-62E3-4D0C-877B-106361643492`. Post-audit operational debit is `1721.887721588062` of `7200` seconds; stage D is `99.43380220909603` seconds and remaining global capacity is `5478.112278411938` seconds. The scientific stop is not resource exhaustion.
