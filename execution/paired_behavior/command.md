# One proposed training command — review required before launch

`.venv/bin/python -m schrodinger.route_policy_experiment train --root execution/model_training_comparison --ledger execution/model_training_comparison/ledger.jsonl --name paired-behavior-sa-8000 --prepared execution/model_training_comparison/prepare-001/prepared.json --decision execution/paired_behavior/sa-resume-decision.json --seed 1701 --mode schrodinger --updates 8000 --resume execution/model_training_comparison/pilot-1701-schrodinger-1000/checkpoints/update-1000.pt --resume-hash 61850806ace41a2ad6ecdbc9317d50eba4c5841d3a8fce4ed57a9d081610ca3b --initial-checkpoint execution/model_training_comparison/pilot-1701-schrodinger-1000/checkpoints/initial.pt`

Unmodified reviewed runner, authoritative existing ledger/owned lock. New uniquely
named output under existing root to preserve safety. Prospective 2200-second
resource envelope documented in plan; existing B deadline unchanged. Resume
identity read-only check cost 0.486582667 seconds; initial ledger summary cost
0.476610083 seconds, charged once as setup before launch. No new training yet.
