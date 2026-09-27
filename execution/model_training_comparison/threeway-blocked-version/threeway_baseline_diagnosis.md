# Three-way baseline check — implementation blocked; no inference

2026-09-19. The requested check has **not produced a scientific result**. Sol
passed the outcome-blind specification but blocked the final implementation.
No new checkpoint evaluation, training, test-set access, or production attempt
occurred. The previous baseline diagnosis remains unchanged.

## Intended check

Compare original training pairs (A), map-specific unseen goals on the same
training maps (B), and unseen routine validation maps (C), using identical
distance/optimal-action-count quotas within fixed map triplets. B excludes every
goal appearing in the complete saved training-state set on that map, including
suffix supervision. Proper scores and exact route success at updates
1,000/4,000/8,000 were planned. Matching does not control all geometry,
shortest-path multiplicity, or selection differences; this remains one seed.

## Definitive blocker

The final independent review identified three frozen-contract failures:

1. `matched_support.json` always declares `MATCHED_SUPPORT_INSUFFICIENT`, even
   when sufficient support would allow inference. Status must reflect the actual
   gate result before checkpoint evaluation.
2. Persisted bin `quotas` are capacities before the global row cap, not the
   actual selected per-bin counts. Retained quotas must be derived from the
   selection and explicitly equal across A/B/C.
3. Tests lack a genuine successful composed match with exact completion-weighted
   oracle q and an all-selected matched bank. The existing open-grid fixture has
   inconsistent problem metadata; synthetic quota success and a failing composed
   match do not supply that evidence.

These are implementation/reporting/verification defects, **not evidence that
matched cohorts cannot be constructed** and not a result about generalization.
The bounded final correction and exact-version review are exhausted. No further
implementation, replacement, or run will occur under this attempt without a new
direction from the parent/user. A narrowly authorized implementation correction
with the same independent review is the remaining route to execution; no
scientific threshold change or new training is required.

## Preserved records and budget

- Frozen specification: `threeway-diagnosis-spec.md`, SHA256
  `577a8ada24fa6708281d730bb291a78a89967f87aefc484e1c90449ac8325b5c`.
- Specification PASS: `threeway-spec-review.md`.
- Final implementation BLOCKED: `threeway-implementation-review.md`.
- Unaccepted script SHA256:
  `410a285f6acd63b19da78e33caad621612e598f21786c62ccd372e7faf53caed`.
- Test SHA256:
  `1cb8dfee092facf07bab29a78a1396e592287cc07752e38e90804bea3c4b5a82`.
- Historical partial handoff: `threeway-partial-handoff-historical.md`; final
  unaccepted handoff: `threeway-implementation-handoff.md`.

New development charges total **3.806407958 seconds** (0.968819625 failed,
0.837588333 passed, and two retained 1.0-second tool-wall charges). Static reviews
charged zero. Two early rows were inserted mid-ledger; an appended chronology
clarification preserves them and counts them once. Operational cumulative debit:
**1750.507380421049 / 7200 seconds**, leaving **5449.492619578951 seconds**.
This stop is not budget exhaustion. No `threeway-diagnosis-001` production output
was created, so no scientific support-gate verdict is available.
