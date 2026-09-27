# Bounded driver closure (same Block A, no scientific change)

The first handoff and its continuation ended as incomplete checkpoints. Root
cause: the implementer treated a partial static checkpoint as a turn endpoint;
the production/accounting seam remains unfinished. This sub-block isolates that
seam. It is not a review-cycle waiver or execution authorization.

Terra changes only `command.py` and its driver-specific tests now. Preserve the
plan, spec, decisions and scientific study implementation. No imports or runtime.
Finish all six items before returning; do not return another partial checkpoint
unless an actual tool, capability or authority blocker prevents an edit.

1. Exact fixed command kinds: smoke10 seconds with one named test; suite30 with
   the test file; production200 with one fixed seed/mode/4000 owner. Validate
   finite envelopes and bind exact argv, cwd, authority/source hashes, designated
   review path/hash/phase and unique machine PASS. Reject unknown kinds.
2. Reserve under one exclusive study lock; check both experiment locks and
   current ledger EOF after acquiring it. Verify the frozen147-line prefix,
   single exact inherited carry and unique finite rows. Enforce new-study totals
   A100/B1600/D100 and global/stage ceilings, not merely old stage headroom.
3. Reuse reviewed pure supervision, including descendant cleanup. All setup,
   cleanup and finalization lie inside the envelope; disclose a bounded allowance.
   Write start, logs and terminal records even for failed/exception children.
4. A commands append exactly one runtime EOF charge on success OR failure, with
   terminal evidence. Release reservation after certain charge and cleanup so an
   inspected repeat is possible; retain it when accounting/cleanup is uncertain.
5. Production reconciles the actual owner UUID and unique owner charge on every
   path, even nonzero child exit or missing output manifest. An already-charged
   FAILED owner is accounted failure, never double charged. Missing charge gets
   one permanent uncertain fallback including allowance, never success. COMPLETE
   requires bound attempt/result/index and all referenced endpoint file hashes.
6. Literal static tests exercise exact decision negatives, named command shapes,
   envelope/prefix/carry/EOF uniqueness, successful/failed test charge, timeout
   descendant cleanup, complete owner, failed charged owner without manifest,
   missing-owner permanent fallback. Small synthetic artifacts/children only.

Write a complete driver-only assertion map with hashes. Astra will then dispatch
the separately bounded remaining scientific composition tests before full Sol
static review. No testing or production is authorized by this sub-block.
