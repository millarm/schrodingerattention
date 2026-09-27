# D1 owned-producer correction handoff — static only

| Artifact | SHA-256 |
| --- | --- |
| `execution/difficult_problem_solving/d1.py` | `463f31c7268e410d9eb9adc4a9242213df226aa1330a9b46d92276afe15edf27` |
| `tests/test_difficult_problem_solving_d1.py` | `93e6bef322a1b32317538027cfbfa1fdb2bc63b8d4817f1eda52a0469e11cca2` |
| unchanged `execution/difficult_problem_solving/d1_watchdog.py` | `96aa33a1fc6268276d6d0879545b9d974b14fd73d2452d5b1e22e519e5815bf2` |

The accepted smoke function is unchanged. The owned producer test at lines
51–100 now invokes actual `run` without ready-made cells, actual `OwnedAttempt`,
producer, sink, index reader, compose and report. The only test-process boundary
replacements are the explicitly permitted decision/runtime/tiny-validator ones.
Lines 76–80 strictly enforce all 40 exact grid keys, 16 reuse cells and ordered
ten-ID panel after lossless JSON list→tuple normalization. Lines 87–100 assert
the complete owner report/index, 40 unique durable cell writes, eight greedy
files, absent cumulative partial file, literal 24-call seed/mode/checkpoint/T/K/
split/replicate/support/ordered-ID sequence, eight cache identities, default
512-reader rejection and explicit 10-reader override success.

No tests, imports, inference, checkpoint loads, ledger writes, timers, or
production were run. The endpoint-write and final-manifest failure cases remain
unimplemented in this snapshot, so it is not a completed block, static PASS, or
smoke authority.
