# D1 temperature-controlled difficult-solving comparison

**D1 evaluation COMPLETE; independent result/accounting audit PASS.**
Four paired seeds, fixed8k checkpoints, validation only. All40 predefined
temperature cells are retained:16 exact historical reuses and24 new endpoints.
No training or final-test release occurred.

## Main result

After the frozen symmetric temperature search and both single-draw quality
floors, Schrödinger attention solves **52.15%** of challenge problems within32
draws versus **51.37%** for softmax: **+0.78 percentage points**, positive in
only2/4 seeds. The earlier unadjusted T1 difference was+2.73 points (3/4).
This does not establish a reliable difficult-solving advantage.

|Seed|Chosen T, SM / SA|Challenge pass@32, SM / SA|SA−SM, pp|
|---|---|---|---:|
|1702|1 /0.75|57.03% /53.91%|−3.125|
|1703|1 /1|49.22% /53.13%|+3.906|
|1704|1 /1|46.88% /50.78%|+3.906|
|1705|1 /0.75|52.34% /50.78%|−1.563|

Every selected endpoint meets both frozen floors: challenge Q and routine Q each
at least its paired softmax-T1 value minus2 percentage points. This is a pair of
noninferiority-style eligibility floors, **not exact matched quality or proven
equivalence**. At T1, SA1702 fails the routine floor and SA1705 fails the challenge
floor; selecting their cooler eligible endpoints reduces coverage. No hotter
softmax endpoint wins the frozen eligible objective on these seeds. Thus the
smaller gap is not evidence that hotter softmax alone reproduced the earlier gain.

|Equal-seed mean at selected T|Softmax|Schrödinger|SA−SM, pp|
|---|---:|---:|---:|
|Challenge pass@32|51.367%|52.148%|+0.781|
|Challenge single-draw Q|15.729%|16.888%|+1.160|
|Routine single-draw Q|43.815%|47.386%|+3.571|
|Challenge distinct valid routes /32|11.176%|11.249%|+0.073|
|Routine distinct valid routes /32|32.961%|33.856%|+0.895|
|Challenge valid-solution-set coverage|4.239%|4.623%|+0.384|

Productive variation is essentially unchanged on challenge problems. Distinct
valid routes/32 counts only exact legal shortest solutions, not random failures.
Valid-solution coverage divides distinct valid routes by the exact total number
of shortest solutions (`valid_headroom`); it is different from pass@32 problem
coverage and from strict training-signature novelty. Strict novelty remains
retained but is not the user's broader useful-variation target.

## Uncertainty and interpretation

The four-seed paired SD is3.664 percentage points. The descriptive95% t interval
for the mean difference is **[−5.050,+6.612] points**, using df3 and a small-sample
normality assumption. The fixed-selected-temperature shared-eight-map bootstrap
(2000 resamples, seed91703, linear quantiles) gives **[−1.758,+3.711] points**.
These are different uncertainty views, not independent replications. Neither
accounts for all temperature-selection optimism on this reused validation panel.

The challenge population is only8 selected mixed-composition maps×16 problems,
shared across seeds, with the historical novelty-based dataset selection. This
is not evidence about all difficult planning tasks. Temperature selection and
scoring used the same familiar validation panel: this remains exploratory, not
held-out confirmation or creativity proof. Common uniforms and32 draws are
matched, but inference wall time is not forced equal; prior training cost was
about3.22× higher for SA. Historical raw rows lack independent within-map
problem IDs; immutable source/order bindings and legal-route corroboration are
retained, with the all-invalid permutation limitation explicit.

## Runtime, scope and next gate

One owned run completed in168.062 measured seconds, charged172.062 including
the accepted startup/finalization allowances. The24 new endpoint elapsed times
sum to150.694 s (range5.796–6.945 s); they overlap their cache/sampling/verifier
components and must not be summed with those components. Initial setup was3.851 s;
endpoint/shared-artifact write timing was1.298 s before final report persistence.
Eight bound greedy timing records and proper-bank timing/cardinality records
(1024 states each) are retained. Historical forward/action counters are unavailable,
not zero. All raw cells, chosen IDs, RNG/support/checkpoint identities and exact
timing components remain in the manifest-bound owner.

**D2_FORECAST_DEFERRED/NO_GO** is the approved engineering/authorization status,
not a measured model-runtime failure. Complete non-overlapping2048-problem scaling
and its1.5× bound were deliberately deferred; there were no extra model calls to
fill that forecast. The rough32-map bootstrap-width projection is2.734 points,
conditional on exchangeable maps and fixed selections; it is not a power guarantee
and does not reduce four-seed uncertainty. No D2 or test access is authorized.

The current result does not justify claiming a robust coverage benefit. If further
work is desired, complete the bounded forecast and explicitly authorize an untouched
confirmation panel with the chosen settings fixed; do not retune on its outcomes.

## Evidence and accounting

- [Machine result](/Users/gmh-company/codex/schrodinger/execution/model_training_comparison/difficult-d1-repair-001/d1.json), SHA `1af6ca7ab440995cbfdc608e979c293382b7e32119038aae81be3540354fec1f`.
- [Implementation PASS](/Users/gmh-company/codex/schrodinger/execution/difficult_problem_solving/d1-repair-implementation-review.md); named smoke1/1 and focused suite28/28 passed before production.
- [Independent result/accounting audit PASS](/Users/gmh-company/codex/schrodinger/execution/difficult_problem_solving/d1-result-audit.md), SHA `ada20693ec3edb8381fc02948b645227263aa539f25a8a650fbbc81c6997cfec`.
- [Production terminal evidence](/Users/gmh-company/codex/schrodinger/execution/difficult_problem_solving/d1-production-20260927-001/result.json) and [session/accounting record](/Users/gmh-company/codex/schrodinger/execution/difficult_problem_solving/d1-production-command-evidence-20260927.md).

Final qualified operational debit: **4764.416447001050/7200 s**.
This includes the earlier administrative300-second uncertainty allowance, not
measured historical usage or a proven bound. Damaged historical ledger bytes were
preserved; the successful recovery appended only two development charges and one
production charge. No double watchdog production debit occurred. Independent
read-only results/accounting audit passed without further model execution or
ledger mutation. D1 is closed; no remaining work or D2 execution is authorized.
