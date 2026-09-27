# Independent audit — read-only paired-behavior supplement

## Verdict: PASS WITH EXPLICIT LIMITATION

Reviewed supplement SHA-256: `4dbec01609e99e83fe7a1635edb8c382947c9b16cda0159e685d3e20655a3aef`.

This bounded supplement is a valid summary of already-retained validation records. It does not execute or rehabilitate the blocked analysis job, does not add inference, and does not cover the frozen A/B/C or temperature-control blocks.

### Independent checks

- Verified the owner-manifest hash of every source result used at updates 1,000, 4,000 and 8,000.
- All 1,024 fixed proper-score rows per checkpoint have exact matching softmax/Schrödinger canonical, map, family, goal, current and q identities against the bound held-out bank. The reported state comparisons therefore have exact row alignment.
- Independently recomputed the greedy 512-problem joint counts. At update 8,000 they are 215 both solve, 50 softmax-only, 65 Schrödinger-only and 182 neither. Re-verifying every retained greedy route against the expected canonical/start/goal yields zero disagreements with stored validity in either architecture.
- Independently recomputed equal-map, fixed 80/20 policy TV and argmax disagreement at all three checkpoints. At 8,000 they are `0.0968940797` and `0.11328125`. The 118 raw argmax disagreements divide into 89 both q-optimal, 17 softmax-only optimal, 10 Schrödinger-only optimal and 2 neither.
- Independently recomputed the update-8,000 valid-route sets from all 32 attempts/problem. There are 69 both-empty problems; conditional equal-map Jaccard is `0.3159959214`; weighted mean intersection/softmax-only/Schrödinger-only distinct routes is `4.16094`/`4.13594`/`4.90885`.
- Raw route recomputation matches the accepted evaluator aggregates: softmax versus Schrödinger `U_valid/K=0.2592773/0.2834310`, `U_novel/K=0.008984375/0.0087890625`, `V_novel/K=0.01372070/0.01259766`, quality `0.3422526/0.3716634`, pass@32 `0.8479167/0.8463542`, and known-valid fraction `0.959911/0.966105`.
- Stored proper-score summaries support the stated update-8,000 entropy, KL and Brier values and the routine/challenge qualification. These remain validation-only one-seed descriptions.

### Binding limitation

Saved route-problem records contain map ID and family but omit canonical/start/goal. Their within-map order therefore cannot be proven from record identifiers alone. The supplement correctly relies on the immutable accepted evaluator's output-order contract plus the hash-bound validation dataset, rather than claiming map/family equality proves order. The exact-verifier audit gives strong corroboration—zero stored-validity mismatches—but cannot mathematically rule out a permutation among groups whose routes are all invalid. This limitation does not apply to the state results, whose identities and q are explicit.

### Interpretation

At 8,000 updates Schrödinger has higher observed overall valid-route quality and more distinct valid routes, but slightly lower unique/attempt-level novel-valid yield and essentially unchanged pass@32. Quality is unmatched, the novelty differences are small, and there is one trained seed. The result supports behavioral difference in this run, not useful diversity, creativity, or a general architecture advantage. Argmax disagreement frequently reflects two different q-optimal actions rather than one architecture being correct.

The blocked production analysis remains blocked. A/B/C transfer comparisons, the two new quality-control temperatures, and a fully identity-bearing route adapter are `NOT_RUN`/`NOT_EVALUATED` here.

### Accounting

Independent audit charge: `6.6` seconds, UUID `9B62E090-2ACA-4BAC-B822-747143F48DB2`. Post-audit global debit is `1993.27696642003` of `7200` seconds.
