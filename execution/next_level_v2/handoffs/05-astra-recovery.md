# Astra recovery handoff — user-authorized implementation ownership

Scientific design unchanged. Production inventory/model/training not run.
The prior runner/test incompleteness is addressed directly, with32 focused tests
passing in1.01s (command exit0, full tool wall1.705386875s). Exact command:
`.venv/bin/python -m pytest tests/test_productive_diversity_data.py tests/test_productive_diversity_runner.py -q`.

Five recovery checks:01–03 each exit1 (one tiny-fixture failure),04 exit0/16passed,
05 exit0/32passed. All command subprocess time and full tool-wrapper difference
are append-only charged:7.558861291s new full wall total. Conservative cumulative
budget debit167.630706627s includes the historical150s allowance, not measured time.
Every command returned explicit exit; none yielded or was relaunched.

## Closed findings and executable evidence

- `_validate_stratum` independently verifies oracle length/M/novelty, exact
  map/family/problem counts, canonical identity/split separation and quotas.
  Nine parameterized corruption cases plus five real-oracle challenge boundary
  failures assert rejection. Real composed routine-as-challenge callback is
  rejected at the correct challenge stage, not an earlier unrelated error.
- `test_real_composed_success` reaches all four strata without replacing
  run_rung: genuine8x8 geometry, orientation gate, q, all-DAG suffix support,
  valid routine AND valid challenge records, exact hashes and strict artifacts.
  Internal selection injection uses a deliberately tiny one-component task,
  two problems/map and M>=1; production defaults remain three/four components,
 16/map and16<=M<=256. This tests composition, not experimental feasibility.
  A bounded<=49-placement unit-fixture construction finds a genuinely partial
  novel support; it is neither a production pool nor a model outcome.
- Actual run_rung deadline after inventory retains a per-rung stage summary,
  parent outcome/count linkage, manifest and completed artifact. Scientific
  failures remain distinct from technical errors and only permitted codes tryB.
- Rejections are injected/local; ownership-race preserves foreign output.
  Mandatory attempt-log failure raises after exactly-one FAILED charge/cleanup.
  Signal handler/old timer restoration is asserted. Files use exclusive creation.
- Manifest binds all specs/reviews, protocol, helpers, sources/tests; effective
  config includes N, pool seed, family codes, exact split allocations. Tests
  independently recompute every input/output hash. Historical source/ledger
  hashes remain unchanged in the regression.
- All four strata receive the identical bounded cache; a separate oracle call
  counter verifies actual signature cache reuse, not merely accepted kwargs.

## Exact implementation identity for Sol

Runner567cb0ceff9107ca9fd2a3999d6126b9ec0c94559db860e73dbdd91670e4d98f
Tests b62bd8f2bbfc94d2ec114579de4f8a5e0addf4d59d490f3955b32b2f238f6f9e
Pure engine unchanged e2e2b93a72afac114f68c1add3881aaa89898dbeb1f6a22c2ac00cf3a8faae09
Pure tests unchanged93ba9890c72b6e63300ab247aa85d0bb8cedbe84c552f0d56b67e401134db471

Sol must independently PASS this version before a production launch. The
historical blocker and all prior failed reviews are preserved, not overwritten.
