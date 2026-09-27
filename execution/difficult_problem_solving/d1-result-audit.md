# D1 result and accounting audit

## Verdict: PASS — result accepted, scientific advantage not established

This is a read-only audit of the one-shot owner `execution/model_training_comparison/difficult-d1-repair-001`. The audited `d1.json` SHA-256 is `1af6ca7ab440995cbfdc608e979c293382b7e32119038aae81be3540354fec1f`; the current ledger SHA-256 is `1340ee945d663e22c7a4fa7bd232c9832b90babe20d3d91662967116d232c3f9`.

## Artifact integrity

- The owner attempt is `COMPLETE`; `attempt.json` SHA-256 is `8b948ddf148e59344b83b5eb90cc17c5058968b12fbd559395f347e732c27c86`.
- All 58 entries in `output-manifest.json` exist and match their recorded SHA-256. There are no unmanifested owner files other than the manifest itself and no unsafe manifest paths.
- `cell-index.json` is `COMPLETE` and its exact 40-cell list equals `d1.json.cells`. The grid is exactly 4 seeds × 2 modes × 5 temperatures, with unique identities, K=32, splitcode 1, replicate 0, 16 reused cells, and 24 new cells.
- Every indexed cell hash, all 8 greedy hashes, all 4 shared-binding hashes, and the panel hash match. Each compact cell points to the shared panel/binding/greedy evidence and contains 512 problem result rows with exactly 32 string routes each.
- The shared panel has 512 unique problem identities, 32 maps × 16 problems, and the required 12 `IIIIIIII` / 12 `LLLLLLLL` / 8 `IIIILLLL` map-family split.

## Selection and paired outcomes

I independently reapplied the frozen rule: eligibility requires both Q values to remain within 0.02 of SM T=1; maximize challenge pass@32, then challenge Q within `1e-12`, then choose the lowest temperature. All reported winners and metrics match recomputation:

|Seed|SM selected|SA selected|SM routine/challenge Q|SA routine/challenge Q|SA−SM hard pass@32|
|---:|---:|---:|---:|---:|---:|
|1702|T=1.00|T=0.75|0.435872 / 0.176758|0.492432 / 0.186035|−0.031250|
|1703|T=1.00|T=1.00|0.432129 / 0.131592|0.424805 / 0.157959|+0.0390625|
|1704|T=1.00|T=1.00|0.445231 / 0.150391|0.426758 / 0.170898|+0.0390625|
|1705|T=1.00|T=0.75|0.439372 / 0.170410|0.551432 / 0.160645|−0.015625|

Every selected candidate clears both floors; the narrowest SA margin is `0.0015266927083333326` on routine Q for seed 1704. Each production winner is unique at the pass and challenge-Q stages, so the final lowest-temperature tie breaker was not invoked by these data. Its deterministic order is nevertheless explicit in the frozen implementation and covered by the accepted literal suite.

The tuned paired hard pass@32 deltas are exactly `[-0.03125, +0.0390625, +0.0390625, -0.015625]`, mean `+0.0078125`. The raw T=1 SA−SM deltas are `[-0.0078125, +0.0390625, +0.0390625, +0.0390625]`, mean `+0.02734375`. Thus tuning does not produce a consistent per-seed SA advantage: tuned SA wins two seeds and loses two.

The 4×8 tuned challenge-map contrast matrix is present and each seed's eight-map mean exactly reproduces its reported paired delta. Recomputed uncertainty matches the report: sample SD `0.036643873123620545`, seed half-width `0.05830857372338685`, full width `0.1166171474467737`; the reported map interval is `[-0.017578125, 0.037109375]`. Both uncertainty summaries cross zero, so D1 does not establish a reliable SA improvement.

## Quality, coverage, and route variation

Across selected seeds, mean routine Q is `0.438151` SM versus `0.473857` SA; mean challenge Q is `0.157288` SM versus `0.168884` SA. Mean challenge pass@32 is `0.513672` SM versus `0.521484` SA. These averages are descriptive over four paired seeds and do not override the interval crossing zero.

Metric definitions were checked in `route_policy_metrics.py`: `U_valid` is unique valid routes divided by K; `valid_headroom` is unique valid routes divided by the full valid-solution count M; `coverage` is unique novel routes divided by the novel-solution count Mnovel. For selected challenge cells:

- all-valid solution-set coverage (`valid_headroom`) averages `4.2393%` SM versus `4.6231%` SA;
- strict novel-solution coverage averages `3.9546%` SM versus `4.7027%` SA;
- `U_valid` averages `11.1755%` SM versus `11.2488%` SA;
- duplicate rate averages `4.5532%` SM versus `5.6396%` SA, while invalid rate averages `84.2712%` SM versus `83.1116%` SA.

Routine `U_valid` averages `32.9610%` SM versus `33.8562%` SA; routine novel coverage is correctly null because no novel-solution denominator applies there. Route variation is therefore mixed: SA has slightly greater mean unique-route and solution-set coverage, but also greater duplication, and the per-seed coverage/U_valid direction is not uniform. Valid retained routes corroborate route order; as disclosed in the result, all-invalid within-map permutations remain indistinguishable.

## Forecast scope

The result correctly reports `D2_FORECAST_DEFERRED/NO_GO`. All essential D2 cost categories remain missing and the retained D1 timings are explicitly not scaled into a D2 forecast. No D2 conclusion or authorization follows from this audit.

## Accounting and watchdog audit

- The production decision binds the exact accepted source/test/watchdog hashes, implementation review SHA-256 `a6f8737ea1f5735cadf8a0c36a0a5adba928291fbb4d746b525999f65fbd69aa`, and pre-run ledger SHA-256 `a1bdef8039c66547d8019898d683b4780bf4daa2ccb7b26648c03c7b9ff81683`.
- The watchdog result is `COMPLETE`: exit code 0, no timeout, verified process-group cleanup, no envelope overrun, no finalization-allowance overrun, and empty stdout/stderr.
- Exactly one ledger row owns this output, UUID `901eaeae-d0c5-414d-ba54-383f9a487c07`. Its charge is `172.06155891693197s` = measured owner elapsed `168.06155891693197s` + 2s startup allowance + 2s finalization allowance. The row's `FINALIZATION_UNCERTAIN` append status is reconciled by the manifest-bound `COMPLETE` attempt. No watchdog fallback or duplicate debit exists.
- The pre-run 146-line ledger hashes exactly to the decision-bound value; appending the single owner row produces the current 147-line ledger hash above. Entry IDs remain unique.
- Current qualified totals are stage A `860.0010003299705s`, B `2286.76600491805s`, C `0s`, D `694.6458445000296s`, inherited carry `923.003597253s`, global `4764.416447001049s`. Remaining headroom is D `705.3541554999704s` and global `2435.583552998951s`.
- `experiment.lock` and the watchdog reservation are absent. The authorized one-shot production attempt has now been consumed; this audit does not authorize a rerun.

## Limitations

I recomputed the paired deltas, selection floors/winners, 4×8 map inputs, seed mean/SD/t-width, coverage summaries, manifest hashes, and ledger arithmetic using read-only inspection. I did not re-execute the fixed-seed PCG64 map bootstrap, so its reported quantiles are accepted as manifest-bound output of the reviewed implementation rather than independently regenerated here. I did not run tests, import model code, load checkpoints, perform inference or training, execute D2, or mutate the ledger.
