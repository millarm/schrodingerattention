# Independent Sol review of the D1 implementation contract

**Contract SHA-256:** `8e44c9a39e707a393ddf7c02578dabda20b8d09cb334367c732fcbe98fff0711`

**Verdict: CHANGES REQUIRED — do not start implementation against this version.**

This was a static contract/interface review only. I ran no implementation,
tests, inference, model calls, checkpoint loads, training, or final-test access.
The approved D1 science and resource amendment are otherwise represented
faithfully: four fixed seeds and 8k checkpoints, complete validation support,
the symmetric five-temperature grid, exact 16/24 reuse/new partition, common
uniforms, two per-seed Q floors, deterministic selection order, 300-second D1
cap, 140-second cumulative development cap, amended stage table, validation-only
D2 forecast, and no D2 authority.

## Required corrections

1. **Close the final-test payload access path explicitly.**
   Lines 27--33 require accepted prepared identities and reuse of replication
   checkpoint/owner binding, but do not state how identities may be obtained.
   The accepted `schrodinger.route_policy_experiment._prepared_ids` helper reads
   and JSON-parses all of `prepare-001/prepared.json`; that 132 MB artifact
   contains the sealed `test` payload as well as its metadata. Calling it would
   contradict lines 11 and 80 even if the returned test rows were ignored.
   Require a metadata-only route: obtain the identical `input_ids` dictionaries
   from manifest-bound COMPLETE replication-analysis/owner artifacts, require
   agreement across all seeds/models, and pass those IDs into the narrow owner/
   checkpoint validators. If the prepared file itself must be bound, permit only
   an opaque streaming SHA-256 comparison to the already authorized digest—never
   JSON parsing or access to its `test` member. Explicitly forbid `_prepared_ids`,
   `load_final_test`, prepared-payload deserialization, and test-selection helpers
   in production and composed tests. Retaining the already published test hash as
   opaque provenance is not permission to inspect its payload.

2. **Define the interval-width and map-bootstrap calculation exactly.**
   Lines 93--97 give the t critical value, resample count, and RNG seed, but leave
   “expected interval width” and “shared-map bootstrap variation” underspecified.
   Freeze the statistic and output: selected temperatures are held fixed; the
   seed interval uses the four selected challenge pass@32 contrasts, sample SD
   with `ddof=1`, and full 95% width
   `2 * 3.182446 * SD / sqrt(4)` (also retain mean and half-width). For the map
   calculation, resample the eight challenge map IDs with replacement, use the
   same resample for both architectures and all four seeds, recompute each seed's
   equal-map contrast and then the four-seed mean, and state the quantile rule for
   the descriptive 95% interval/width. State whether the optional 8-to-32-map
   square-root projection is emitted; if emitted, apply it only to the map-width
   quantity and label the fixed-selection and iid-map assumptions. Add literal
   synthetic assertions for these calculations. These quantities remain
   descriptive and cannot themselves authorize D2.

3. **Make forward/action accounting testable acceptance evidence.**
   Lines 61--64 require new-endpoint forward-call, batch-state, and generated-
   action counts, but none of the literal acceptance items requires their values
   to be checked. Add a synthetic known-count assertion proving that the outer
   proxy/hook counts every model forward invocation and total states in its
   batches, that generated actions are summed from all retained route lengths,
   that cache reuse changes forward counts without changing the common-uniform
   route identity, and that unavailable historical counts remain null/explicitly
   unavailable rather than zero. This is necessary evidence for the D2 forecast's
   operation accounting and the plan's compute-fairness boundary.

## Non-blocking observations

- The accepted analysis records do not embed seed/split/replicate/K inside each
  raw temperature result. Binding those facts through the manifest-bound producer
  source, top-level seed/checkpoint identity, fixed call site, temperature field,
  and exact ordered route rows is acceptable, provided the report distinguishes
  producer-bound evidence from independently stored per-row identity.
- The specified cold-then-incremental cache policy is scientifically fair for
  outputs because cache contents are checkpoint-bound logits and the uniform
  stream is temperature-independent. Timing must continue to distinguish cold
  and warm endpoints, as the contract already requires.
- A rejected retained endpoint must remain an integrity stop; it must not be
  regenerated under the 24-new-endpoint allowance.

After the three bounded corrections, the contract can return for exact-hash Sol
review. No change to the grid, thresholds, seeds, resource caps, or D1-only
authorization is requested.
