# D0 recovery implementation handoff

Frozen plan SHA-256: `c31c3ee84131ec4e96dbbd42e073a4ec96be63a0b3fc65058a18275714c035fe`.

Reviewed recovery version:

- `execution/difficult_problem_solving/analyze.py`: `1697265245fe1626a270dc033e282877b01a5f3f3091f16da6dd032c336496b1`
- `tests/test_difficult_problem_solving.py`: `f6177b7c9e97f1de0fb93a43162425d1aa1fc7ac9ed40fd7f49c5269bf881a7e`

Before any edit, the blocked version was copied byte-for-byte to
`execution/difficult_problem_solving/blocked-02/`:

- `analyze.py`: `63ecc9c8106c4b313053e0d79fce141fba6629224bd72e0c88f616c6cd761fe7`
- `test_difficult_problem_solving.py`: `299b3b2770f0c9b1c7beab2a63c0f6c48a143d8d504e9c256556ce78e5120e05`
- old `handoff.md`: `04972ee9fd657968e35831a5b1ab47cd62f9fc4b257a247e32456be91e68b6aa`

## Delivered recovery scope

1. `run` accepts an internal test-only retained-bag/owner-metadata seam while
   the production path remains fixed to the reviewed owners and validation
   adapter.  The focused fixture uses the real `OwnedAttempt`, a temporary
   truthful initialized ledger and unique output.  It verifies a COMPLETE
   `d0.json`, `attempt.json`, and `output-manifest.json`; independently injects
   failure writing `d0.json` and failure during output-manifest finalization,
   asserting both raise and cannot return success.
2. The retained 1702 route test retains the stale-digest mutation check and adds
   a reversed problem list with its event digest recomputed.  The latter reaches
   the adapter's dataset-order/identity verification and raises there.
3. The composed exact 4-seed x 32-map x 16-problem fixture varies seed effects,
   exercises both/SM-only/SA-only/neither outcomes, asserts an explicit empty
   fixed geometry bin has zero support and null metrics, and rejects an unknown
   family.  It uses only synthetic retained attempt rows.
4. Aggregates now emit solved-only `c` and `u` count distributions plus explicit
   zero accounting/support.  Each seed/stratum now emits `sa_minus_sm` for
   empirical Q, all bag pass/U-per-K/U-per-M values, duplicate concentration,
   and all prefix pass/Q/U values.  Differences are null if either conditional
   input is null; no zero substitution occurs.
5. This record is the complete recovery evidence inventory.  No production D0
   command was launched; no model inference/training/checkpoint loading,
   final-test access, new samples, cohorts, or model calls occurred.

## Literal assertion map

| Review-02 residual group | Focused assertion(s) |
| --- | --- |
| Owned output / late failures | `test_owned_d0_success_and_late_output_finalization_failures`: records the actual attempt `stage == D`, transparently observes a real `setitimer` override `<=56`, uses fixed output name, actual COMPLETE d0/attempt/manifest, injected `d0.json` write exception, and injected `file_manifest` finalization exception |
| Recomputed route-order negative | `test_real_retained_event_interface_without_inference_or_test_loader`: recomputed `_event_digest` on reversed route problem list and expects `dataset order` rejection |
| Varied composed fixture | `test_shared_assembly_four_seed_exact_panel_paired_bins_and_gate`: distinct seed deltas, all four outcomes, empty length-16 challenge bin null, unknown family rejection |
| Solved-only and paired fields | same assembly test: solved-only zero/distribution fields and non-null paired Q/bag/prefix fields; implementation's `delta` preserves null conditionals |
| Truthful accounting/handoff | four exact test attempts and their unique EOF ledger IDs below; this handoff lists the exact reviewed hashes |

## Commands and charges

All commands were direct exits, not sessions and not yielded/relaunched.  They
are appended exactly once to `execution/model_training_comparison/ledger.jsonl`.

| Ledger ID | Command result | Charged seconds |
| --- | --- | ---: |
| `d0-recovery-test-failed-20260920-01` | exit 1; 6 passed, 1 failed; wall `11.858253583` | 11.858253583 |
| `d0-recovery-test-failed-20260920-02` | exit 1; 6 passed, 1 failed; wall `11.044943291` | 11.044943291 |
| `d0-recovery-test-passed-20260920-01` | exit 0; `7 passed in 10.83s`; wall `10.945310917` | 10.945310917 |
| `d0-recovery-test-passed-20260920-02` | exit 0; `7 passed in 10.82s`; wall `10.932665416` | 10.932665416 |
| `d0-recovery-owned-seam-passed-20260920-03` | exit 0; `1 passed in 5.78s`; wall `5.896201833` | 5.896201833 |

Recovery development charge is `50.677375040` seconds.  The approved prior
development debit `32.4` seconds is included once, yielding cumulative D0
development `83.077375040` seconds and `16.922624960` seconds under the
100-second D0 development ceiling.  The approved pre-recovery global debit
`4188.869097296127` plus these five charges yields global
`4239.546472336127/7200` seconds, leaving `2960.453527663873` seconds globally.
No owned stage-D charge was incurred.  The ledger's broader historical stage-A
total is intentionally not recast as this D0-only debit.

Ready for exact-version Sol review.  Source and tests are frozen after the final
passing command.
