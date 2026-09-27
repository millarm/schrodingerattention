# Prospective external-overhead accounting clarification

Proposed before any runtime; requires Sol acceptance before use. This clarifies
review04 finding4 within unchanged study/global/stage/envelope limits. It does
not change science, historical charges, accepted OwnedAttempt or its records.

The accepted owner creates one immutable normal B charge C, including its
existing2-second startup and2-second finalization allowances. The external
driver measures E=elapsed since before driver setup plus its disclosed1-second
finalization allowance. Reconcile the actual owner UUID first, never a fallback.

If a unique valid normal owner charge exists, record uncovered overhead
`H=max(0,E−C)`. If H>0, append exactly ONE separate EOF stage-B
`kind=driver_overhead` row for H, linked to the owner UUID and unique driver
session. If H=0 append no overhead row. Thus total accounted usage is
`C+H=max(C,E)`, not C+E. The owner row/artifacts are never rewritten, and an
overhead row can never qualify as a normal owner charge or a successful owner.
All rows count toward the same B1800, stageB4100 and global7200 ceilings.

If no normal owner charge exists, use the single permanent uncertain fallback
for E and NO overhead row. Ambiguous/mismatched existing owner rows are an
accounting stop, never reason to append a second owner/fallback. No relaunch.

Compare total accounted amount with the exact reserved SM350/SA550 envelope and
current stage/global/study caps. Preserve all actual charge even if overrun;
overrun is resource failure, never COMPLETE/continuation. Clock measurement for
H/fallback occurs just before EOF finalization; the1-second allowance covers
append/fsync/terminal/reservation operations. Failure to durably finalize retains
uncertainty and reservation. Do not claim an allowance is measured elapsed.

Literal tests: C≥E gives no row; C<E adds only the difference once; repeat
reconciliation cannot duplicate overhead; overhead cannot satisfy owner lookup;
fallback never receives overhead; over-envelope C or E fails with full charge
retained; existing charged FAILED owner uses the same arithmetic without a
duplicate owner/fallback. Tests use deterministic clocks and small ledger files.
