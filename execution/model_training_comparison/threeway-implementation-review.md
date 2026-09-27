# Independent implementation review — three-way checkpoint diagnosis

## Verdict: BLOCKED

Exact reviewed artifacts:

- `threeway_diagnosis_job.py`: `410a285f6acd63b19da78e33caad621612e598f21786c62ccd372e7faf53caed`
- `tests/test_threeway_diagnosis.py`: `1cb8dfee092facf07bab29a78a1396e592287cc07752e38e90804bea3c4b5a82`
- handoff: `4e3974660878deb461c393004c3e9334cd0910466acddcf0cb622ce37654ad61`
- governing specification: `577a8ada24fa6708281d730bb291a78a89967f87aefc484e1c90449ac8325b5c`

The scientific construction is substantially present: map-local unseen goals use the complete saved goal set, A/B overlap is checked against complete saved states, route bins use direct exact start q, state banks retain every jointly selected row without secondary downsampling, fixed map ordering and the ≥8/family gate are implemented, only updates 1,000/4,000/8,000 are scored, and owner/checkpoint/evaluator reuse is appropriately bounded. However, the exact frozen version fails required evidence/provenance acceptance and is not safe to launch.

## Blocking findings

1. **The pre-inference support artifact makes a false scientific-status claim on the success path.** At `threeway_diagnosis_job.py:85`, `pre["status"]` is unconditionally `MATCHED_SUPPORT_INSUFFICIENT`; line 86 persists it before inference, and only line 87 branches on the actual family counts. Therefore a support-sufficient construction that proceeds to model inference still retains an immutable `matched_support.json` declaring insufficiency. This violates the requirement for truthful outcome-blind support evidence before predictions and would leave contradictory primary artifacts.

2. **Persisted “quotas” are not necessarily the quotas actually used after the global cohort cap.** `_joint` records `min(cap,countA,countB,countC)` at lines 37/42, but lines 38–41 can truncate later bins once the total reaches 6 or 32. With enough supported bins, `matching.*.quotas` can claim more selected rows than the retained identities contain. The identities make post-hoc reconstruction possible, but the specification explicitly requires the actual joint quotas to be persisted; a capacity-before-global-cap table labeled as final quotas is not truthful evidence.

3. **The literal acceptance tests do not execute the required real successful construction.** The open-grid test at `tests/test_threeway_diagnosis.py:8–18` calls real DAG/BFS helpers but never asserts any completion-weighted q. Its `Problem(0,25,length=14,M=1)` metadata is deliberately inconsistent with the real open-grid distance/path count, so it does not validate a genuine matched route record. The only `match_triplet` test asserts a failure (`lines 20–25`), while the quota-success test calls `_joint` directly on synthetic `ScoreCandidate`s (`lines 27–35`). No test demonstrates a successful composed route→DAG-state match, direct all-selected `ScoreBank`, exact start-branching bin, and retained equal joint counts. The frozen specification expressly requires real BFS/q evidence and the final handoff claims this behavior.

These are not requests for optional hardening or a wider framework. They are direct failures of the frozen persistence and literal-verification contract. Per the parent-imposed final-cycle boundary, this review does not propose another local correction loop.

## Gate decision

Do **not** launch `threeway-diagnosis-001` from this version. No scientific construction outcome has been observed: this is an implementation/evidence blocker, not matched-support insufficiency and not evidence against the diagnosis hypothesis.

Static review only; no test execution or ledger charge.
