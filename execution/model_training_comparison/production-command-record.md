# Production command/session record

Full command-tool results were emitted and retained in the conversation. This
index preserves the completed session identity; no yielded process was relaunched.

| Attempt | Command suffix after module | Session | Explicit final exit | Owner entry |
|---|---|---:|---:|---|
| prepare-001 | `prepare --root execution/model_training_comparison --ledger execution/model_training_comparison/ledger.jsonl --name prepare-001` |34159|0|946fca35-9819-4a78-904e-ba68496bf381|
| profile-001 | `profile --root execution/model_training_comparison --ledger execution/model_training_comparison/ledger.jsonl --name profile-001 --prepared execution/model_training_comparison/prepare-001/prepared.json --decision execution/model_training_comparison/profile-001-decision.json` |12385|0|27b8c6c1-7326-46ad-bccf-f3a2642be2bb|
| pilot-1701-softmax-1000 | `train --root execution/model_training_comparison --ledger execution/model_training_comparison/ledger.jsonl --name pilot-1701-softmax-1000 --prepared execution/model_training_comparison/prepare-001/prepared.json --decision execution/model_training_comparison/pilot-1701-softmax-1000-decision.json --seed 1701 --mode softmax --updates 1000` |48640|0|0f276448-0a88-4655-8441-43518a4a2a9d|
| pilot-1701-schrodinger-1000 | `train --root execution/model_training_comparison --ledger execution/model_training_comparison/ledger.jsonl --name pilot-1701-schrodinger-1000 --prepared execution/model_training_comparison/prepare-001/prepared.json --decision execution/model_training_comparison/pilot-1701-schrodinger-1000-decision.json --seed 1701 --mode schrodinger --updates 1000` |50977|0|3275b57a-2849-43a0-8ddb-934b96eaf77e|

Executable/module: `.venv/bin/python -m schrodinger.route_policy_experiment`.
Each owner records actual argv/runtime and exact input/source provenance. The
append-only ledger's conservative `FINALIZATION_UNCERTAIN` charge is resolved by
the matching canonical `attempt.json` COMPLETE status and output manifest, not
by rewriting earlier ledger evidence. Both final tool responses emitted COMPLETE
with their result paths. No pending production process remains at this checkpoint.

## Remaining completed commands

Exact argv is additionally bound in each result provenance. Equal-time commands
used the accepted evaluate command, validation split and the fixed decision file.
Orchestration cell541 waited on every returned session to explicit exit0 before
launching the next of the six evaluations; the complete nested results are retained.

| Attempt | Session | Explicit exit | Owner UUID |
|---|---:|---:|---|
|pilot-1701-softmax-2000|55256|0|739620c8-bf90-45c0-8623-44eaa47d6523|
|pilot-1701-softmax-4000|82481|0|b8f50f96-a1cf-4b0f-8def-2e245193c148|
|pilot-1701-softmax-8000|79445|0|b4681563-9574-47d1-be85-019c6c544b8c|
|equal-time-softmax-200|90056|0|9f501474-f320-4b32-b6e1-f21865c14958|
|equal-time-softmax-400|65037|0|f96e2ff6-d42f-4374-92d8-fc445005e877|
|equal-time-softmax-700|60154|0|31ed49f6-fc9d-4ec9-92c9-f03a46ceaf5d|
|equal-time-schrodinger-100|23791|0|86490834-200f-4b02-b6c1-609c2a4066be|
|equal-time-schrodinger-200|59490|0|e4cd49ac-6f1d-47af-a8a3-572c9597efad|
|equal-time-schrodinger-300|70079|0|62021e7c-cadb-4e7a-b9c4-9add846a1847|
