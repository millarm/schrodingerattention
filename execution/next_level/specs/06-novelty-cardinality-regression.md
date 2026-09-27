# Narrow regression correction: persist every selected problem

Sol found `_novel_records` appended outside its row loop, retaining only the
last problem per split. That would force an artificial novelty-gate failure.
No real inventory was run. This is an implementation regression, not data.

Terra fixes only append indentation and adds end-to-end exact assertions:
validation32, ID32 and IL16 records for the existing tiny injected fixture;
record map/start/goal identities equal the selected problem identities in each
split with no omissions/duplicates; M equals route count and signature count;
gate arithmetic reads the entire persisted IL record list. No other refactor.
<=5s focused tests; full inventory still forbidden. Complete handoff with hashes
then Sol independently verifies only this regression/closure before a run.
