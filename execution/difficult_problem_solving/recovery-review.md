# Independent Sol review of the D0 recovery

**Verdict: PASS — exact reviewed version is eligible for the single authorized D0 production run.**

Exact bytes inspected:

- `execution/difficult_problem_solving/analyze.py`: `1697265245fe1626a270dc033e282877b01a5f3f3091f16da6dd032c336496b1`
- `tests/test_difficult_problem_solving.py`: `f6177b7c9e97f1de0fb93a43162425d1aa1fc7ac9ed40fd7f49c5269bf881a7e`
- `execution/difficult_problem_solving/recovery-handoff.md`: `d0a365d27318c825edb2d6964f9d7b2401848c12af2452c133880ed75f0f80bf`
- frozen scientific plan: `c31c3ee84131ec4e96dbbd42e073a4ec96be63a0b3fc65058a18275714c035fe`

This was a static source/artifact review only. I ran no tests, model calls,
checkpoint loading, training, inference, final-test access, production command,
or additional delegation. A passing test count was not used as acceptance.

## Review-02 closure

1. **Owned success and late-failure evidence is now present.**
   `run` uses the real `OwnedAttempt` at fixed stage `D` and fixed output
   `difficult-d0-001`, bounds the already-owned timer to at most 56 seconds,
   performs the real assembly and JSON write, and returns only after context
   finalization. `test_owned_d0_success_and_late_output_finalization_failures`
   drives that path with synthetic retained bags and a temporary initialized
   ledger. It checks a COMPLETE `d0.json`, `attempt.json`, and
   `output-manifest.json`, stage `D`, the observed timer bound, an injected
   `d0.json` write failure recorded as FAILED, and an injected manifest
   finalization failure that raises `ArtifactError` and leaves explicit failure
   evidence. Neither late failure can return success.

2. **The route-order negative is independently rebound.**
   The retained-1702 test preserves the stale-digest rejection and separately
   reverses the saved problem rows, recomputes `_event_digest` over the mutated
   event, and requires `_storedroutes` to reject it with `dataset order`. Thus
   this negative reaches identity/order validation instead of succeeding only
   because the old binding is stale.

3. **The composed fixture has the required variation and rejection coverage.**
   The exact 4-seed x 32-map x 16-problem fixture assigns different outcome
   patterns by seed. Literal assertions establish all four K32 categories
   (`both`, `sm_only`, `sa_only`, `neither`), nonidentical seed deltas, a fixed
   empty challenge length-16 cell with zero support and null metric, and rejection
   of an unknown family. Assembly and metric calculations are real; the gate and
   summaries are not patched.

4. **Solved-only distributions and paired deltas are explicit.**
   Each aggregate emits all-problem zero counts, solved support, solved-only `c`
   and `u` count distributions, and solved-only bag-U summaries. Each
   seed/stratum emits SA-minus-SM empirical Q; bag pass, U/K, and U/M for every K;
   duplicate concentration; and prefix pass, Q, U/K, and U/M for every K. The
   shared delta function returns null whenever either conditional input is null,
   so absent conditional support is not imputed as zero.

5. **The handoff and accounting are complete for this recovery.**
   The handoff records the reviewed hashes, preserved blocked-version hashes,
   literal assertion map, all five recovery ledger IDs, direct exits, failures,
   passes, and charges. Static ledger inspection found each listed ID exactly
   once with the stated charge and outcome. The five charges total
   `50.677375040` seconds; with the approved prior D0-development debit of
   `32.4` seconds this is `83.077375040/100`, leaving `16.922624960` seconds.
   The stated global debit `4239.546472336127/7200` is arithmetically consistent.
   No owned stage-D D0 charge or production result is claimed.

## Scientific and execution checks

The retained-bag pass formula and expected-distinct formula implement the frozen
hypergeometric estimands, including impossible combinations as zero and the K32
identities. Distinct routes are counted from exact valid route bytes; empirical Q,
duplicate concentration, prefix sensitivity, and U/K and U/M denominators match
the contract. Aggregation gives equal weight to available problems within each
map and then equal weight to maps. Geometry validates positive M and nonnegative
even detour and preserves all fixed bins, including empty cells.

The gate is limited to challenge K32 at update 8000, requires the exact four
seeds and common eight-map support, counts strictly positive seed deltas, and for
each deletion removes the same map from both modes and all seeds before averaging
the four seven-map contrasts. Zero therefore fails as specified. The production
path uses only validation data and accepted retained owners/events, loads each
owner once, contains no final-test loader or checkpoint/model load, and records
the historical all-invalid route-order limitation. PASS authorizes only the one
already approved D0 run; it does not authorize D1, D2, final-test release, a
retry, or any scientific conclusion before results audit.

No required corrections or non-blocking implementation observations remain for
this exact version.
