# A2b2b — final command wiring and measured profile

After A2b2a acceptance, complete route_policy_experiment.py and focused command
tests under the existing full A2b specification. No new runner framework. Reuse
accepted evaluator, metrics, adapter and safety/core semantics. Full CLI commands
are prepare, smoke, profile, train, evaluate, all owned immutable attempts with
actual approved input roots/hashes; test fixtures may override roots only in tests.

prepare materializes banks through accepted bank builders and saves literal
IDs/candidates/q hashes and configuration. It may build oracle test banks but
must not run a model on test. train supplies real scheduled evaluator/probes to
core, saves initial/every100/final checkpoints with truthful cumulative times and
parent chain, and obeys explicit supervisor decisions. test evaluate refuses
without the full final-release identities specified in A2b. No implicit release.

Implement exact smoke/profile1699 and 1.5x all-work cost forecast from full A2b.
The profile remains five warmup plus twenty measured updates per model and the
fixed six validation maps. No test scores, configuration reduction or reuse of
profile weights. Save complete timings including setup/IO and Python sampling,
not merely step medians. Fixed source/config/input hashes and successful attempt
artifact are mandatory; ledger charge rows alone never prove completion.

Literal tests cover command safety/release refusal, actual tiny complete smoke,
accepted cached evaluator wiring, forecast arithmetic/missing-stratum conservative
rule, separate phase/end-to-end timing, and complete artifact/provenance identities.
Target <=20 seconds focused tests inside existing A400. Complete final combined
handoff A2b2-implementation.md maps the entire inherited A2b checklist to evidence.
Sol exact full-harness PASS precedes Astra's one unique production smoke/profile
authorization. Actual cost forecast requires separate Sol audit before seed1701.
