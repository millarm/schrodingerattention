# Recovery A independent review

**Verdict: CHANGES REQUIRED (Recovery A only).** Production remains gated on
Recovery B and later runner review regardless of this verdict.

## Frozen version

- Recovery specification `execution/next_level_v3/specs/02b-recovery.md`:
  `0db86f0ac7afeb42c4294be4d7168a1334d64baf276eb277ca768544915f171f`
- Handoff `execution/next_level_v3/handoffs/02b-recovery-a.md`:
  `1cd0d38ef71957677479ffde4fa0dbfaec93d08dd9aa5f2b87706cca46cb0b5f`
- Module `schrodinger/productive_diversity_v3_data.py`:
  `2c982f8921b5dba3385407bd41e8aef73d73e32a8ed8490de529fd74836802ee`
- Tests `tests/test_productive_diversity_v3_data.py`:
  `e60756178e20fc9b6ee44136043c96a4e9ebec54e5da94cad276f137da6c906b`
- Prior blocker review `execution/next_level_v3/reviews/04-block2-blocker.md`:
  `aec56e1873220505a8437b08653663876fede0472cf0450810e4f6af5f8ac8cb`

## Findings requiring correction

1. **Whole-inventory validation is not performed once before proposal
   selection.** `validate_inventory_records` is called inside
   `build_training_support` (`productive_diversity_v3_data.py:390-393`), and the
   orchestrator invokes that builder anew for every retained proposal
   (`:496-500`). Thus a three-proposal production attempt repeats the complete
   identity/canonical/component/shortlist traversal three times, contrary to
   Recovery A item 1's explicit one-time validation and “avoid repeating” rule.
   The full orchestrator must validate once before its proposal loop, while the
   directly callable builder may retain a safe validation seam without causing
   repeated production validation. A regression should count validation calls.

2. **Rejected-map evidence loses accepted row identities from earlier lengths.**
   `lazy_select_heldout` accumulates full accepted rows in local `pending`
   (`:452-477`), but evidence records only integer `accepted` counts (`:477`). If
   a later length exhausts, `pending` is discarded and those inspected/accepted
   pair identities are unrecoverable. This does not satisfy Recovery A item 4's
   requirement to preserve per-length selected rows and reasons. Evidence for
   every scanned length must retain the actual accepted row records while still
   making clear that no map identity was committed. The associated regression
   must exercise an earlier passing length followed by a failing length and
   assert both retained evidence and non-commit.

3. **The claimed required regression matrix is not present.** The current test
   file has no malformed-inventory test at all, no lazy evidence/non-commit/
   early-stop test, and no rejection cases just outside the 1/4–3/4 challenge
   interval or below four novel routes. `test_heldout_support_key_cache_and_challenge_boundaries`
   (`tests/test_productive_diversity_v3_data.py:185-204`) proves acceptance at
   exactly 1/4 and 3/4 plus cache reuse, but not boundary rejection. The isolated
   orchestrator test (`:207-236`) checks broad stage order and that training is
   excluded, but does not assert cumulative disjoint exclusions from each prior
   held-out stratum, current-stage short-circuit evidence, or an unknown training
   outcome abort. These are explicit Recovery A regressions at spec lines 47-51;
   the handoff's assertion-map claim is therefore materially overstated.

4. **Inventory metadata validation is incomplete relative to its own frozen
   checklist.** `validate_inventory_records` checks duplicate IDs/identities,
   family, reconstructed canonical bytes, components, `(start,goal)` uniqueness,
   stored length, and M bounds (`productive_diversity_v3_data.py:365-379`), but
   it neither requires/verifies an explicit declared `n == 12` field nor checks
   endpoint range/free-cell validity before rows are used. The assembled records
   currently omit `n` (`:216-223`). Recovery A item 1 requires exact declared
   n12 metadata and unique pair endpoints per length; add/validate the dimension
   linkage and reject out-of-grid or wall endpoints technically. Real BFS on use
   remains the required second line of validation.

## Correctly closed in this revision

- The orientation-deficient old fixture now truthfully returns
  `SCIENTIFIC_TRAINING_ORIENTATION_SHORTAGE`, and selected homogeneous maps are
  gated for both I and all four L orientations (`productive_diversity_v3_data.py:397-404`).
- Eligibility keys include support hash, raw wall bytes, n, start and goal; the
  cache is bounded and exposes hit/miss and size evidence (`:288-334`, `:443-466`).
- Inspected held-out pairs reproduce BFS distance and multiplicity (`:455-460`),
  and excluded/raw-ineligible/remaining maps receive distinct evidence classes
  (`:446-450`, `:482-484`).
- The training-only placeholder has been replaced by the frozen four-stage
  orchestrator with proposal-local cache/support, shared exclusions, scientific-
  only advancement, technical aborts, future-stage `NOT_EVALUATED` callbacks,
  and first-full-PASS stopping (`:487-527`). Its tests are correctly labeled as
  isolated orchestration tests rather than composition evidence.

## Scope and charge

Static source/test/spec/handoff inspection and SHA-256 verification only. No
tests, route search, inventory, production, or model command was run; independent
compute charge is **0 seconds**. Recovery B's genuine, orientation-valid,
split-disjoint composed fixture was intentionally not required for this A-only
verdict. This review makes no dataset-feasibility claim.
