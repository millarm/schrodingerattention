# Records-only accounting closeout (no additional computation)

The append-only ledger remains unchanged at10.071845336s. After freeze, Terra
recovered these tool-result durations not yet represented in that ledger:

| Historical check | Exit | External wall seconds |
| --- | ---: | ---: |
| Preliminary SubtaskA,6 passed | 0 |0.615321333|
| Invariant check,6 passed/1 failed |1|0.644589667|
| Invariant check,6 passed/1 failed |1|0.584327792|
| Invariant check,6 passed/1 failed |1|0.589422500|

Additional observed durations total2.433661292s; ledger plus these is
12.505506628s. Original command start/end timestamps were unavailable. These are
late-recovered historical events, not newly executed checks, so no fabricated
chronological ledger entries or timestamps have been inserted.

Terra also reported a combined14-pass result wall0.726718916s as corresponding
to the existing SubtaskB ledger charge0.725237625s. This1.481291ms mismatch is
unresolved; do not treat either as independently verified exact provenance or
charge it as a second run. No successful rerun followed the final assertion edit.

The final exact total is therefore UNVERIFIED. For any authorized continuation,
conservatively reserve an additional150s (the entire authorized development-test
allowance) beyond the unchanged10.071845336s ledger: provisional budget debit
160.071845336s. This is a disclosed allowance, NOT measured compute and NOT an
assertion that150s ran. It covers the known missing durations without inventing
precision. Remaining Stage0 budget under that conservative debit is739.928154664s;
remaining7200s global budget7039.928154664s. No production dataset/models exist.
