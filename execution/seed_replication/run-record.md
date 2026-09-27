# Serialized production session record

Exact commands are frozen in `commands.md`. Every yielded session is polled to
explicit terminal exit before the next launch; original owner/ledger artifacts
retain actual argv, source/input/decision hashes and charges. No silent reruns.

| Seed/model | Session | Terminal exit | Charged seconds |
|---|---:|---:|---:|
|1702 softmax|64939|0|168.94484995800303|
|1702 Schrödinger|42209|0|281.38246870896546|
|1703 Schrödinger|7663|0|280.89634979201946|
|1703 softmax|57814|0|170.28971295902738|
|1704 softmax|17038|0|171.25604483298957|
|1704 Schrödinger|48988|0|281.43470833299216|
|1705 Schrödinger|55077|0|281.8973453750368|
|1705 softmax|34754|0|169.89144254202256|

Seed 1702 complete: T1 quality SM 0.38404947916666665, SA 0.358837890625;
SA−SM −2.521158854166665 percentage points. Greedy SM 0.5828125, SA 0.5703125.
Core training SM 39.57725138642127 s, SA 127.67855511314701 s. This is one
fresh pair, not the four-pair replication estimate.

Historical launch note: seed 1703 Schrödinger, session 7663, launched after the exclusive
focused analysis test window (5 PASS, 13.6 s). Global operational debit before
this launch is 2545.559215254012 s, including an extra conservative 13.6 s
allowance because the test was initially attributed to D and its proper A charge
was appended without rewriting/subtracting the original row. This extra amount
is not a second measured test execution. The complete remaining fixed sequence
plus analysis/audit reserves still fits the frozen budgets.

1703 SA exited 0, COMPLETE. Next is 1703 softmax after the exclusive consolidated
analysis-correction test window. Before that test, operational debit is
2826.455565046031 s; all remaining fixed work retains the forecast reserve.

Consolidated analysis tests finished: failed fixture assertion 19.9 s, then
12 PASS 19.2 s; both charged A once. Global debit 2865.555565046031 s before
launching 1703 softmax, session 57814 (running). No test/training overlap.

1703 pair complete: T1 quality SM 0.372021484375, SA 0.371435546875;
greedy SM 0.5703125, SA 0.5640625. Global debit 3035.845278005058 s before
launching first accepted analysis (1702), session 55025. Training 1704/1705 remain
fixed regardless of these outcomes. No concurrent compute.

1702 analysis session 55025 exited 0 COMPLETE, charge 49.02631954103708 s.
Its C sampled-quality difference is −1.388888888888895 pp; fixed temperature
control unmatched, nearest T1. Global debit 3084.871597546095 s before launching
1704 softmax, session 17038. Analysis final interpretations await independent audit.

Sol first-output audit PASS: `reviews/analysis-1702-audit.md`. 1704 softmax then
exited 0 COMPLETE. Global debit 3256.127642379085 s before 1704 Schrödinger
launch, session 48988 (running). Fixed remaining runs, three analysis jobs and
final independent audit remain within their conservative reserves.

1704 pair complete: T1 Q SM 0.38626302083333336, SA 0.3755859375;
U_valid/K SM 0.285400390625, SA 0.27911783854166666. Greedy SM
0.5692708333333334, SA 0.53125. Global debit 3537.562350712077 s before
1705 Schrödinger launch, session 55077. This is the last fixed seed, not an
adaptive stopping decision. Final 1705 softmax and three remaining analyses are
reserved along with independent audit/reporting.

1705 SA session 55077 exited 0 COMPLETE. Final training command 1705 softmax
launched once, session 34754; pre-launch global debit 3819.459696087114 s.
No technical or budget stop. Three analysis jobs and independent audit remain.

All eight training commands completed with explicit exit 0. 1705 T1 Q SM
0.38557942708333337, SA 0.4041015625; U_valid/K SM 0.28644205729166666,
SA 0.30052083333333335. Global debit 3989.351138629137 s before launching
1703 analysis, session 64033. No further training is authorized or planned.

## Analysis completion and accounting

|Seed|Session|Terminal exit|Charged seconds|
|---|---:|---:|---:|
|1702|55025|0|49.02631954103708|
|1703|64033|0|49.00954408297548|
|1704|17088|0|48.861761417007074|
|1705|22862|0|49.246653167007025|

All twelve production jobs are COMPLETE, explicit terminal exit 0, with unique
immutable outputs. No new model compute remains. Final operational debit after
the conservative 20 s read-only reporting/audit allowance is 4156.469097296127 s.
The allowance is not a measured inference run. Final independent review PASS:
`reviews/final-results-review.md`; its bounded read-only checks fit the allowance.
All authorized fixed work is complete, with no further model compute planned.
