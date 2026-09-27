# Early-learning handoff — bounded runtime name-resolution correction

Status: one-expression correction candidate frozen for Sol's exact repair
review. The authorized smoke passed; the single authorized targeted suite then
failed on a NameError and was durably charged with cleanup verified. The
runtime record remains at `runtime-evidence-001.md`; no retry was run. This
correction changes only the aggregate component-change weight reference from
the undefined `row` to the paired state `a`. No tests were rerun in this cycle.
The 200k extension remains on HOLD and was not touched.

The implementation reuses the accepted model/evaluator, watchdog, and owned
attempt lifecycle. New statewise arithmetic uses only already-saved p, KL,
nonoptimal-mass, q and stable IDs. It binds accepted legal masks and original
equal-state/map/stratum weights once per owner, validates weighted `1-m` against
saved nonoptimal mass, reports all four legal-argmax transition groups for all
30 adjacent pairs and 800→2,000, and computes the exact `A=-log(m)` and
`B=KL+log(m)` decomposition without clipping or a small-mass cutoff. A zero
exported p on any positive-q action makes the checkpoint decomposition
unavailable, even when total support mass is positive. Both SD outputs remain
descriptive sample SDs with denominator n−1.

The D audit now runs in a separate watchdog-owned child. External check/audit
charges use one preassigned ledger UUID and reconcile uncertain appends by that
same identity; reservations remain when accounting, cleanup or terminal
durability is uncertain. A failed terminal write/fsync permanently marks its
attempt uncertain; a later readable failure terminal cannot release the
reservation. Existing overhead rows must match the attempt's preassigned UUID
and all amount/identity fields. Every transition group's A+B residual, even
for empty groups, is checked against the 1e-10 tolerance. Production/audit
decisions require an external Astra
JSON acceptance artifact with `verdict`, `implementation_review_path`,
`implementation_review_sha256`, and the exact `source_hashes` dictionary. That
future artifact itself is deliberately not in the source inventory; its SHA is
bound into each decision. Astra should create it only after Sol's exact-version
implementation PASS and the authorized bounded runtime checks.

The composed runtime fixture is intended to score one new softmax checkpoint
using two validation problems (one per stratum) and four proper rows (two per
stratum), while preserving the production 512/1,024 panels. A separate tiny SA
probe test uses two candidates (one per stratum), checks finite record counts,
and checks model non-mutation. A focused accepted-watchdog timeout test verifies
the separately grouped descendant is reaped. These tests are authored but not
run; static PASS and Astra authorization remain required before them.

The final summary's `owners[].points[]` retains the full plot-ready raw curves;
owner statewise checkpoint and transition tables retain each state ID, q,
legal mask, weight, p, KL, support mass, group and decomposition values, with raw
detail file references. No confirmation, calibration, causal or population
inference claim is added.

## Exact source inventory (SHA-256)

| Authority key / file | SHA-256 |
| --- | --- |
| command.py | `4dd38b42996cd6963814bf13d249e00c484f33b301afc49ed5e2ead115817841` |
| study.py | `2b1c7ad3baf31e0956ec33b572e5ae2cb202bbb85be051b3ef4198896d050fd5` |
| test_early_learning.py | `feee0a7421699ee164cb7327cdc7652015fe94b9117c0d0b1f01e769eb2b2476` |
| inventory.json | `0ccf9c4ae4201d8ccbe9037785a2efc2eb4b9b9246bc7fdbec8fd09d2d769d5b` |
| plan.md | `fcfc12a9a250a85391259cbff3bd2bd62a8a429e8b0a1615944ad40682f9be5f` |
| spec-01-dense-scoring.md | `b0bf16e0caaf1407fd72c148622b73826f998885fb124be77da24cdd88be90cc` |
| reviews/00-methodology.md | `c4f796a0333a7d28c33508507595a81fe07c26af9fd763f57c446ca038b2a113` |
| methodology-acceptance.md | `694caa52e7a762acdae645cebe869f9cd9b2f6b95895851bd1efd21c1945c0db` |
| amendment-01-statewise-kl.md | `51563625cc2b171f4e70757fbe05eb8cacf050ab1f47e9d3b07eeae790490842` |
| spec-02-corrections-and-kl.md | `2aef1209f183b1b702fae8d353d328fe02aeaa0fd7bc449385d651aebe83b4da` |
| reviews/02-amendment-methodology.md | `6ead804a56dbd23f4b3e797984108c4f7d8c931785b4980dd5962f30a4942959` |
| amendment-acceptance.md | `e84d5ecca402da7970eef6429c9dee9c029d47b201b443c16562348baa34e812` |
| spec-03-final-static-correction.md | `3433ac04e2f91c2711ed5f66f3fc9af1ebaeb7a4b0d8f8a9239b98a98dd80ac9` |
| reviews/03-static-rereview.md | `e31002f2845636ad9ee8672c5f80c088b1ca19883b7e2c2cea7f1ab963198715` |
| reviews/01-static.md | `42d06106676e7c53acb0e91c1cc54cd6ef2cc092ea4616f6bcf204321d3f974f` |
| research/early_learning_refocus_2026-09-27.md | `05b11395c7c0fd518cd80672ed1835aed1555102c090a74cfe4ff43023ff41b0` |
| agent_execution_protocol.md | `983a63fd480510994721d980ee866f08e3cba6b767fcbadd5cef7491d437d1c5` |
| update_efficiency/command.py | `e228b53fb52f3a944e6e523e9ce3340c5abb3c02cc16ad2e07729972b1877d84` |
| update_efficiency/watchdog.py | `ad5e3030ce148283c2576fa5fb376c512a8f7474bcc5e62e8e2d4e6d749900b2` |
| route_policy.py | `95cb7463693c7ac696d9034eaf16a155c0363f38e819cbe56c00408d49b170c4` |
| route_policy_experiment.py | `10cfc1a9a5e21856fd4e80f7c81b7b9243c104d452f10fc2a0062d4b4998036b` |
| route_policy_data.py | `676b8de313fb9c667497b307704b21f137ac55a18e1e19c81be399d3f02e4bb7` |
| route_policy_evaluation.py | `fd5cd438e0fbd103857933418008a7c5936b379488857ac6bfa7370aa8ad18ec` |
| route_policy_metrics.py | `a471ae2c40973cb15584f924061b3ace24ef5af3b1e31702b79056055f317e34` |
| attention.py | `e1ce15be10caf4b2165191f9835256602f4f7b8bd11bffa94f676eac40b0fd6a` |
| route_feasibility.py | `da36b0150c0b255b7e5482d7dc016505054d9632c8fb3a21d06c2d201bfedbf4` |

The table is the exact `command.authority_hashes()` inventory (paths relative
to the workspace except early-learning-local paths). Recompute it after any
code, test, inventory or authority-document change. The handoff is informative
and is not an authority-hashed source.

## Runtime repair review scope

The exact correction instruction is `spec-04-runtime-name-resolution.md`; the
prior bounded runtime record is `runtime-evidence-001.md`. Their SHA-256 hashes,
and the corrected study source hash, are recorded after static validation below.
The 60-second suite has not been rerun; that requires Sol static PASS and a
separate Astra acceptance. The completed smoke is not to be repeated.

- `study.py`: `2b1c7ad3baf31e0956ec33b572e5ae2cb202bbb85be051b3ef4198896d050fd5`
- `spec-04-runtime-name-resolution.md`: `85b098f095abd0e4a968b409fe2fda250c6fea7a07cf6b264adf389548f1cc4f`
- `runtime-evidence-001.md`: `54cce71aba1f9bec66e5be2641d18ab8848096f960a5687dcdb2a0db44d4cc14`

## Static check run

`python3 -c 'import ast,json,pathlib; fs=[pathlib.Path("execution/early_learning/study.py"),pathlib.Path("execution/early_learning/command.py"),pathlib.Path("tests/test_early_learning.py")]; [ast.parse(p.read_text(),filename=str(p)) for p in fs]; d=json.loads(pathlib.Path("execution/early_learning/inventory.json").read_text()); assert len(d["owners"])==4 and all(len(o["checkpoints"])==31 for o in d["owners"]); print("AST and inventory structure OK")'`

No pytest command, `py_compile`, module import, inference, training or ledger
initialization was run. The next authorized step is Sol static review of this
exact version; no runtime phase begins without corrected static PASS and a
separate Astra acceptance decision.
