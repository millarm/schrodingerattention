# Block10: isolated 200k continuation implementation

2026-09-27. Astra specification. The binding scientific/resource plan is
plan-v4-200k.md. Status SPECIFIED; no training authority yet.

## Scope

Luna may create execution/long_horizon_200k/{command.py,study.py,batch.py},
tests/test_long_horizon_200k.py and corresponding handoff/runtime records.
Copy and narrowly adapt accepted update_efficiency command/study behavior,
import its watchdog unchanged, and call accepted scheduled_training unchanged.
Do not edit existing model/trainer/data, old driver/study/tests, historical
ledger or old run artifacts. Astra owns plans/acceptance, Sol owns reviews.

The isolated ledger uses new allocation A300/B21000/C0/D300 and global21600,
zero inherited carry. Initialization records allocation and historical EOF/debit
as provenance only. Scope accepted OwnedAttempt resource constants to these
values inside the new process and restore them; do not change source globals
on disk. Driver ledger parser, decisions and budget checks must agree exactly.
Account successful, failed, timeout, smoke/suite and external overhead charges;
reuse accepted no-duplicate/fallback/reservation safety.

## Resume and artifact contract

Bind each original owner result/index/manifest and initial/16k checkpoint hashes
in the immutable decision. Validate original COMPLETE status, manifest hashes,
seed/mode/config/input/bank/shared-initial identity, complete1..16k curves and
all old score bindings. Pass accepted resume_identity and original initial path
to scheduled_training, with updates200000 and validation=None. It must produce
curves16001..200000, first saved checkpoint16100 parented to original16k hash,
and every100 checkpoint through200000 with the exact chain. Combine original
and continuation CE/batch digests for estimators/pair validation, but preserve
explicit original lineage and don't pretend old updates consumed new budget.
Reference historical files only through explicitly validated immutable lineage;
do not weaken arbitrary-path rejection for other output references.

New scores are18000,20000,...,200000; complete assembled grid includes original
13 points. Use existing estimator formulas with horizon-dependent suffixes and
strict complete-grid validation, plus fixed16k/100k/180k→200k endpoint changes.
The owner output manifest covers every new output file; original references
have separately bound hashes and ownership. All decisions hash the full new
sources plus accepted dependencies, plan/spec and exact Sol review.

## Tests and acceptance

Static safety/protocol Sol PASS precedes runtime. One externally bounded10s
smoke and one60s targeted suite are allowed after static acceptance, within A300.
Meaningful tests: deterministic uninterrupted versus split/resumed optimizer,
model, RNG/sampler and batch stream equivalence (tensor equality when deterministic,
otherwise explain and freeze≤1e−7 before production); reject tampered checkpoint,
resume identity/lineage and historical ledger; extend plateau/rebound/censoring
through200k; exact complete combined stream; budget/reservation and timeout
descendant cleanup with explicit terminals; coordinator fixed order, resource
gate and fail-stop using stubs. Reuse proven watchdog behavior, no broad retesting.
Smoke/suite decisions require new exact static review hash; production requires
new exact implementation PASS and Astra acceptance. Bound every imported test
or neural verification; stdlib-only read-only inspection may run uncharged.

## Operation

Implement a sequential batch coordinator with durable status/terminal artifacts,
exclusive reservation, explicit process identity, and source-hash validation.
It invokes only approved per-owner drivers, never overlaps compute, never retries,
and validates COMPLETE/cleanup/accounting before advancing. New owner decisions
bind the current new-ledger EOF immediately before each owner. Freeze all source
and authority hashes before batch launch; do not mutate those documents mid-run.
Check12GiB free, budgets and first-pair resource gate as defined in plan.
Allow background execution with stdout/stderr retained under the new study;
report exact command, PID/session, initial progress and artifacts to Astra/root.

Deliver handoff with hashes, commands/results and unresolved limitations. Sol
reviews exact implementation and tests; Astra accepts before production. Later
audit verifies all four200k owners, common stream hashes, endpoints, charges,
cleanup, immutable old ledger, and raw-versus-summary agreement.
