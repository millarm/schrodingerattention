# Block A revision: two-pair bounded16k saturation pilot

Read `plan-v3-saturation.md`; it supersedes plan-v2/spec-02 before execution.
Terra stays paused until Sol protocol PASS/Astra dispatch. Same allowed files,
roles, accepted source exclusions, metadata lineage and literal safety tests as
spec-02; this document supplies exact scientific/resource replacements.

- Seeds2201/2202 only; order2201SM→SA,2202SA→SM. Horizon16000 both modes;
  grid0/1200/2000/2400/3600/4000/4800/6000/8000/10000/12000/14000/16000.
  The five percentage points remain fractions of8000, not16000.
- Full16000 paired batch-prefix and shared-initial identity checks, unchanged
  accepted trainer/checkpoint interval100, validation=None then13 owned scores.
- Implement plan-v3 Q rolling means/gains, terminal suffix low-gain confirmation,
  temporary plateaus/rebounds/censoring, and trainingCE100-block/2k-window relative
  gains exactly. No early stopping, no milestone feedback to training.
- Two-seed summaries only: no df3 interval, no four-pair screen. Keep both
  per-seed values/ranges; no statistical replication claim. Preserve fixed C and
  common quality milestones/guards exactly as plan-v3.
- Pure tests: linear/rising/flat/falling Q examples; threshold equality; terminal
  pair vs earlier transient/rebound; invalid/nonfinite grids and CE denominator;
 100-block/2k aggregation with literal known values; target/censoring/intervals;
  wrong/missing/duplicate seeds and full-prefix mutation refusal.
- Owner names/CLI/decisions/checkpoint validation say16000 and bind plan-v3/spec-03,
  not superseded scientific authority. Runtime stagecapsA1000/B4100/C0/D800;
  new-studyA100/B1800/D100. Production envelopesSM350/SA550; smoke10/suite30.
  Reserve entire exact envelope under one lock; startup/cleanup/finalization
  included. No future extension permission inferred from global headroom.
- Driver closure six-item spec-01a remains, with these replacements overriding
  its old4000/200/B1600 constants. Reuse accepted pure watchdog; no duplicated
  broad framework. UUID/manifest reconciliation required on all exit paths.
- Complete actual run/owner/checkpoint/evaluator/serializer fixture and both
  owner failure paths plus forbidden-loader/mutation tests remain mandatory.
  No imports/tests before exact static safety PASS. No placeholders.

Bound implementation into driver completion then science/composition completion;
no broad partial-handoff loops. Original files and reviews preserved. Sol exact
implementation PASS precedes any production. Astra owns sessions/launch; no
production delegated by this specification.
