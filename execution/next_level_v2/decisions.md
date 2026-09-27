# V2 decisions

2026-09-15 — Astra accepted scientific plan and Stage0 dataset contract after
Sol PASS in reviews/01-plan-contract.md. Scientific reviewed hashes:
plan3eb46fa905793da806acf05cdafb02db96e6137d7c5d2dbe8c5c004b74f56dce;
contract81af0064d865ce7f16ddf16a4389349a4eb357be23fa6890bd49c7ac7696adba.
Subsequent title/status-only edits record acceptance without scientific changes.
No dataset/model outcomes exist. Authorize Terra pure engine block only, then
Sol review; wrapper follows separately. All prior results/source preserved.

Pure engine ACCEPTED after Sol03-pure-acceptance PASS, module
6c9c4099c1b98d486511087c3c50d72ab3b885e9b58ad019911b47741efb3ed5,
tests93ba9890c72b6e63300ab247aa85d0bb8cedbe84c552f0d56b67e401134db471.
Three review findings closed in one revision. Sol also accepted clarified
orientation/failure taxonomy and narrow runner spec01. Authorize runner block
only; production requires completed-runner Sol PASS and separate Astra launch.

2026-09-16 — User explicitly authorized Astra to implement this v2 cycle after
the recorded Terra implementation blocker. Sol remains independent; Terra is
inactive. Resume recovery under unchanged scientific criteria and conservative
continuation budget debit160.071845336s (historical ledger10.071845336s +150s
allowance, not measured compute). Recovered old durations are NOT charged again.
Only reviewed current code may launch. Prior reports/reviews remain unchanged.

2026-09-16 — Astra accepts recovered runner after independent Sol07 PASS
(review SHA1da32c467b7fa6f0ddc29217c5097d9675f6b3ab7020b828de64f7cd25d479bd).
Runner567cb0ceff9107ca9fd2a3999d6126b9ec0c94559db860e73dbdd91670e4d98f;
tests b62bd8f2bbfc94d2ec114579de4f8a5e0addf4d59d490f3955b32b2f238f6f9e.
Independent32tests pass, additional1.074367625s; pre-run conservative debit
168.705074252s including150s historical allowance. Authorize exactly one default
Stage0 ladder invocation into attempts/feasibility-001, owned lock and deadline.
No model work before independently reviewed dataset PASS. A yielded command
must be polled by its exact session ID until explicit exit; never relaunched.

2026-09-16 — Production session8329 returned explicit exit0 once. Both rungs
returned LENGTH_FLOW_FAILED: A routine validation378/384; B training784/1024.
No timeout, relaunch, alternate selection or model training. Sol08 PASS independently
reproduced flow certificates and verified provenance within stated audit limits.
Astra accepts DATASET_LADDER_FAILED as the plan's terminal scientific construction
outcome, not an architecture result. Final conservative debit443.384519002s,
including150s historical allowance. No further redesign/compute in this iteration.
