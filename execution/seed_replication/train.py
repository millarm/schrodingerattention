"""Authorized fresh-seed replication entrypoint.

This is deliberately separate from the reviewed pilot CLI: it grants exactly
the amendment in ``plan.md`` and does not relax that CLI's seed-1701 guard.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

from schrodinger import route_policy_experiment as accepted
from schrodinger.route_policy_data import MapBalancedSampler, load_training, load_validation
from schrodinger.route_policy_metrics import heldout_bank, training_bank


HERE = Path(__file__).resolve().parent
WORKSPACE = HERE.parents[1]
ROOT = WORKSPACE / "execution" / "model_training_comparison"
PREPARED = ROOT / "prepare-001" / "prepared.json"
LEDGER = ROOT / "ledger.jsonl"
PLAN = HERE / "plan.md"
PLAN_SHA256 = "b58b88ae15712bca2b027ccb1ab3fc90bef4e9b2a5d94dc8dba43d61fbcb679e"
SEEDS = frozenset((1702, 1703, 1704, 1705))
MODES = frozenset(("softmax", "schrodinger"))
UPDATES = 8000
ORIGINAL_STAGES = {"A": 700.0, "B": 2000.0, "C": 1900.0, "D": 1300.0}
REPLICATION_STAGES = {"A": 700.0, "B": 3500.0, "C": 400.0, "D": 1300.0}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _json_sha256(value: dict) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def wrapper_provenance(argv: list[str]) -> dict:
    return {
        "wrapper_path": str(Path(__file__).resolve()),
        "wrapper_sha256": _sha256(Path(__file__)),
        "replication_plan_path": str(PLAN.resolve()),
        "replication_plan_sha256": PLAN_SHA256,
        "resource_limits": REPLICATION_STAGES,
        "resource_limits_sha256": _json_sha256(REPLICATION_STAGES),
        "actual_argv": list(argv),
    }


def _validate_authorization(decision: dict, *, seed: int, mode: str, prepared_sha256: str) -> None:
    expected = {
        "approved": True,
        "kind": "pilot",  # accepted scheduled_training's narrow seam contract
        "command": "replication_train",
        "run_kind": "fresh",
        "seed": seed,
        "mode": mode,
        "target_updates": UPDATES,
        "replication_plan_sha256": PLAN_SHA256,
        "config_hash": accepted.config_hash(),
        "prepared_sha256": prepared_sha256,
        "manifest_sha256": accepted.MANIFEST_SHA256,
        "resource_limits": REPLICATION_STAGES,
    }
    if _sha256(PLAN) != PLAN_SHA256:
        raise PermissionError("frozen replication plan bytes changed")
    if seed not in SEEDS or mode not in MODES:
        raise PermissionError("only frozen fresh seeds 1702--1705 and paired modes are authorized")
    if any(decision.get(key) != value for key, value in expected.items()):
        raise PermissionError("decision does not bind this authorized fresh replication")


def install_replication_resource_limits() -> None:
    """Apply only the prospective C-to-B transfer after proving old limits."""
    if accepted.STAGES != ORIGINAL_STAGES:
        raise accepted.BudgetError("accepted original resource table changed")
    if accepted.GLOBAL_CAP != 7200.0 or accepted.CARRY != 923.003597253:
        raise accepted.BudgetError("accepted global resource contract changed")
    accepted.STAGES.clear()
    accepted.STAGES.update(REPLICATION_STAGES)


def run(*, seed: int, mode: str, decision_path: Path, argv: list[str] | None = None) -> dict:
    """Train one fresh model via the accepted seams, with no resume path."""
    command_argv = list(sys.argv if argv is None else argv)
    if seed not in SEEDS or mode not in MODES:
        raise PermissionError("only frozen fresh seeds 1702--1705 and paired modes are authorized")
    decision = accepted._load_decision(decision_path)
    _, input_ids = accepted._prepared_ids(PREPARED)
    _validate_authorization(decision, seed=seed, mode=mode, prepared_sha256=input_ids["prepared_sha256"])
    install_replication_resource_limits()
    name = f"replication-{seed}-{mode}-8000"
    accepted.COMMAND_ARGV = command_argv
    with accepted.OwnedAttempt.begin(ROOT, LEDGER, "B", name) as attempt:
        accepted.configure_runtime()
        training, validation = load_training(), load_validation()
        softmax, schrodinger, shared = accepted.paired_models(seed)
        model = softmax if mode == "softmax" else schrodinger
        validation_bank = heldout_bank(validation.problems)
        training_bank_value = training_bank(training.states)
        result = accepted.scheduled_training(
            model, accepted.optimizer(model), MapBalancedSampler(training.states, seed),
            seed=seed, source=input_ids["frozen_source_hash"], config=accepted.FROZEN_CONFIG,
            input_ids=input_ids, checkpoint_dir=attempt.output / "checkpoints", updates=UPDATES,
            validation=validation_bank, validation_problems=validation.problems,
            train_probe=accepted.training_probe_candidates(training_bank_value),
            validation_probe=accepted.validation_probe_candidates(validation_bank),
            support=frozenset(training.support), decision=decision, resume=None,
        )
        record = {
            "provenance": accepted.runtime_provenance(input_ids["prepared_sha256"]),
            "wrapper_provenance": wrapper_provenance(command_argv),
            "decision_sha256": _sha256(decision_path),
            "resource_provenance": {"original_limits": ORIGINAL_STAGES,
                                    "installed_limits": REPLICATION_STAGES,
                                    "resource_limits_sha256": _json_sha256(REPLICATION_STAGES)},
            "input_ids": input_ids,
            "shared_initial_digest": shared,
            "parameter_count": sum(parameter.numel() for parameter in model.parameters()),
            "result": result,
            "test_model_predictions": False,
        }
        accepted._write_json(attempt.output / "result.json", record)
    completed = json.loads((attempt.output / "attempt.json").read_text())
    if completed.get("status") != "COMPLETE":
        raise accepted.ArtifactError("successful replication attempt artifact missing")
    return record


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(prog="python execution/seed_replication/train.py")
    parser.add_argument("--seed", type=int, required=True)
    parser.add_argument("--mode", choices=sorted(MODES), required=True)
    parser.add_argument("--decision", type=Path, required=True)
    args = parser.parse_args(argv)
    command = sys.argv[1:] if argv is None else argv
    run(seed=args.seed, mode=args.mode, decision_path=args.decision,
        argv=[sys.executable, "-m", "execution.seed_replication.train", *command])
    output = ROOT / f"replication-{args.seed}-{args.mode}-8000"
    print(json.dumps({"status": "COMPLETE", "output": str(output),
                      "result_path": str(output / "result.json")}, sort_keys=True))


if __name__ == "__main__":
    main()
