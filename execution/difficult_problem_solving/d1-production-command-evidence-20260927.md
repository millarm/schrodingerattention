# D1 production command and accounting evidence

Single command: `.venv/bin/python -m execution.difficult_problem_solving.d1_watchdog --decision execution/difficult_problem_solving/d1-production-decision-20260927.json --record-dir execution/difficult_problem_solving/d1-production-20260927-001`.

Unused owner, experiment lock and watchdog reservation were checked before launch.
Launch returned session20736/chunk`8d7993`, wall1.003652417 s and empty output.
That exact session was polled repeatedly, never relaunched. Final poll returned
exit_code0/chunk`26d372`, with complete watchdog result. Owner and watchdog both
COMPLETE; all40 cells persisted. No timeout, process-group cleanup verified,
empty stdout/stderr and no finalization-allowance overrun.

The authoritative charge is the unique actual OwnedAttempt row
`901eaeae-d0c5-414d-ba54-383f9a487c07`: measured168.06155891693197 s plus
2-second startup and2-second finalization allowances = **172.06155891693197 s**.
The watchdog measured169.04029454197735 s and completed its accounting checks at
169.24389074998908 s. Its170.04029454197735 s allowance-inclusive outer envelope
is **not an additional charge**: the larger existing owner debit was reconciled.
No fallback was appended. The historical ledger prefix remains unchanged.

Post-production ledger SHA
`1340ee945d663e22c7a4fa7bd232c9832b90babe20d3d91662967116d232c3f9`.
Qualified global debit4764.416447001050 s before independent result audit;
stageD694.645844500030 s. Fresh development remains8.545879331999458/120 s.
The existing30-second independent audit allowance remains available.

Result SHA `1af6ca7ab440995cbfdc608e979c293382b7e32119038aae81be3540354fec1f`.
The owner output manifest binds attempt/result/index/panel/bindings/greedy/cells.
D2 and final-test access did not occur; no further production is authorized.
