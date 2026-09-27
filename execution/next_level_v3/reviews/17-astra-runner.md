# 03c Astra status-closure review

**Verdict: PASS.** The user-authorized Astra implementation closes every Sol16
status/provenance gap at the exact frozen version. The runner is eligible for the
single separately authorized production dataset invocation; this review itself
does not launch it.

## Exact frozen version

- Runner `schrodinger/productive_diversity_v3_runner.py`:
  `6fa238c1192527cb9b470c22229ac9356d73402b7422d9d2f5a097aac6f3faf9`
- Tests `tests/test_productive_diversity_v3_runner.py`:
  `72e8ef684dd82c9845a22f31b0871f7693d9b1a9b0d79024c242344d5e9eaea7`
- 03c spec `execution/next_level_v3/specs/03c-astra-status-closure.md`:
  `f84deaea0b5473ebed5484883c6e95dcc4ffcbac487424d9f470f26b3ad6fd19`
- Handoff `execution/next_level_v3/handoffs/03c-astra-status-closure.md`:
  `0bb1f2fd4aef4cb18952a16234d9f36be8e65a3fa5e2683492a478f3cc2e3b77`
- Historical blocker `execution/next_level_v3/reviews/16-status-model-final.md`:
  `ffdfac64b79949595271c7ba66c08a376efa852b99c36b875991d4d872296481`
- Accepted data module remains unchanged:
  `4aa4779877781f2b0211397c3938185ad6ec5154040fecdef3d9f7eac7e84f08`

## Status-model verification

`ProposalStatuses.finalize(interrupted)` now derives a fresh copy from ordered,
proposal-local callback observations (`productive_diversity_v3_runner.py:64-81`).
It no longer accepts an externally guessed active proposal and does not mutate
the observations:

- resolved scientific-failure proposals are preserved and traversal continues;
- the first unresolved attempted-or-next proposal receives exactly one first
  `NOT_COMPLETED_UNKNOWN` stage, with later missing stages `NOT_EVALUATED`;
- later untouched retained proposals remain wholly `NOT_EVALUATED`;
- a real stage write failure stays `FAILED` and terminates derivation; and
- normal returns turn only absent/unattempted callbacks into `NOT_EVALUATED`,
  without fabricating COMPLETE.

`execute_pipeline` initializes the helper from the ordered retained proposal IDs,
records actual callback artifacts/hashes, and invokes pure derivation using only
whether execution was interrupted (`runner.py:373-400`, `:418-430`). The former
first-ranked fallback is gone.

The two real three-proposal regressions are decisive
(`tests/test_productive_diversity_v3_runner.py:372-416`): proposal 14 reaches a
genuine training-supply failure; proposal 12 is interrupted either immediately
before its training callback or immediately after its real training artifact;
proposal 16 stays untouched. They assert the complete maps in both cases,
proposal-14 failure evidence/family, proposal-12 artifact presence or absence,
proposal-16 empty artifacts, all artifact byte hashes, DEADLINE_FAILED summary,
FAILED attempt, one ledger row, and lock cleanup. No scientific result is mocked.

## Literal scientific-case closure

- The real one-proposal held-out failure now asserts the entire five-stage map,
  I-family scientific failure with nonempty real evidence/selected rows, and
  L-family `NOT_EVALUATED` (`tests/...:338-351`).
- The real first-proposal failure then second PASS asserts proposal 14's exact
  training failure plus four future `NOT_EVALUATED` stages, proposal 12's five
  COMPLETE stages, exactly two proposal records, all five passing artifacts, and
  no false future work (`tests/...:354-369`).
- The prior one-proposal between-callback interruption remains exact and continues
  to bind its training artifact hash (`tests/...:419-432`).
- Unknown callback outcomes raise technically, and ordinary early-PASS untouched
  proposals are all `NOT_EVALUATED` (`tests/...:435-439`).

## Provenance closure

Mandatory fixed files fail if absent. Runtime discovery deterministically hashes
runner/data/helper, both tests, plan, protocol, every current v3 spec/review, and
all three fixture JSON files (`runner.py:285-298`). The real success integration
constructs the exact expected path set and recomputes every byte hash
(`tests/...:442-450`). Because reviews are discovered at invocation time, the
production manifest will include this accepted review without another source
change.

## Process and charge

The acknowledged implementation-before-tests deviation is transparently retained:
the later test matrix produced 33 pass/2 fail before the consolidated correction,
then 35 pass. It does not weaken the final exact-version evidence. Reported new
charge is 8.039021375 seconds and cumulative conservative debit is
548.232812669 seconds.

Independent review used static source/test/spec/handoff and SHA-256 inspection
only. No test, generation, production, or model command was run; independent
compute charge is **0 seconds**.
