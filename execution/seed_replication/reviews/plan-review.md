# Independent plan review — four fresh paired seeds

**Plan SHA-256:** `30e5285beed46b35e6ae2e4530c18814e52150cf540e2b847a2971fbd0316606`

**Verdict: CHANGES REQUIRED**

The scientific design is otherwise acceptable. Seeds 1702–1705 are fixed before outcomes; the alternating within-pair order is block-balanced; both modes share each seed's initialization, batches, and decoding uniforms; seed 1701 remains explicitly separate discovery evidence; and the primary estimate is the four fresh paired full-validation T=1/K32 quality differences. Reporting the mean, sample SD, range, sign count, and the df=3 paired-t interval with an explicit weak-normality/small-n qualification is fair. The plan also correctly avoids map/sample pseudoreplication, p-values, selective replacement, confirmatory treatment of secondaries, and quality-matched novelty claims when the frozen temperature grid misses its tolerance.

## Required correction

1. **Freeze the stage attribution for every forecast component.** The global arithmetic is internally sufficient, but the amended stage ceilings are not enough to infer where costs are charged. After the transfer, the approximate remaining headrooms are A `288.598182083`, B `3019.226917583`, C `400`, and D `1049.846601`. The `2863.038494502` training forecast fits B, while the stated `496` analysis + `150` audits + `200` final contingency fits D; development `80` fits A. If analysis were instead charged to B, B would exceed its ceiling. Amend the plan to state the intended allocation explicitly (including where the 200-second contingency is reserved), and require the wrapper/owners to use those stages. This is a resource-accounting clarification only; it does not change the 7200-second cap or scientific design.

## Implementation-boundary notes

- Interpret “one compute job” as **at most one active compute process at a time**, not as permission to collapse the eight fixed model runs into an unauditable command. Each seed/mode output still needs its unique owner, immutable result/manifest, ledger charge, and explicit terminal exit.
- The additive entrypoint must fail closed on seeds outside 1702–1705, any update count other than 8000, mode mismatch, existing output/lock, inconsistent old ceilings/carry, or changed scientific arguments. It must install/pass the amended resource table without modifying or monkeypatching the accepted CLI/scientific source.
- Before the first launch, bind the wrapper, plan/amendment, accepted trainer/model/data, checkpoint-input contract, and command hashes. Confirm the selected seeds have no prior replication outputs or ledger owners; a failure does not authorize a substitute seed.

No training, inference, tests, or new-seed data generation were performed for this review.
