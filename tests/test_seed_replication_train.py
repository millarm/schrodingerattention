import hashlib
import importlib.util
import json
from pathlib import Path
from types import SimpleNamespace

import pytest


MODULE = Path(__file__).parents[1] / "execution" / "seed_replication" / "train.py"
SPEC = importlib.util.spec_from_file_location("seed_replication_train", MODULE)
replication = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(replication)


def _decision(seed=1702, mode="softmax", **changes):
    value = {"approved": True, "kind": "pilot", "command": "replication_train", "run_kind": "fresh",
             "seed": seed, "mode": mode, "target_updates": 8000,
             "replication_plan_sha256": replication.PLAN_SHA256,
             "config_hash": replication.accepted.config_hash(), "prepared_sha256": "prepared",
             "manifest_sha256": replication.accepted.MANIFEST_SHA256,
             "resource_limits": replication.REPLICATION_STAGES}
    value.update(changes)
    return value


@pytest.mark.parametrize("seed,mode", [(1702, "softmax"), (1703, "schrodinger")])
def test_authorization_forwards_frozen_seed_mode_and_updates(monkeypatch, tmp_path, seed, mode):
    prepared = tmp_path / "prepared.json"; prepared.write_text("prepared")
    decision_path = tmp_path / "decision.json"; decision_path.write_text(json.dumps(_decision(seed, mode)))
    calls = {}
    ids = {"prepared_sha256": "prepared", "frozen_source_hash": "source"}
    monkeypatch.setattr(replication, "PREPARED", prepared)
    monkeypatch.setattr(replication.accepted, "_prepared_ids", lambda _: ({}, ids))
    monkeypatch.setattr(replication.accepted, "_load_decision", lambda _: _decision(seed, mode))
    monkeypatch.setattr(replication.accepted, "STAGES", dict(replication.ORIGINAL_STAGES))
    monkeypatch.setattr(replication.accepted, "configure_runtime", lambda: calls.setdefault("runtime", True))
    training = SimpleNamespace(states=("state",), support=("support",)); validation = SimpleNamespace(problems=("problem",))
    monkeypatch.setattr(replication, "load_training", lambda: training); monkeypatch.setattr(replication, "load_validation", lambda: validation)
    monkeypatch.setattr(replication, "heldout_bank", lambda _: "heldout"); monkeypatch.setattr(replication, "training_bank", lambda _: "trainbank")
    monkeypatch.setattr(replication.accepted, "training_probe_candidates", lambda _: ("trainprobe",)); monkeypatch.setattr(replication.accepted, "validation_probe_candidates", lambda _: ("valprobe",))
    class Model:
        def __init__(self, name): self.name = name
        def parameters(self): return []
    monkeypatch.setattr(replication.accepted, "paired_models", lambda actual_seed: (Model("softmax"), Model("schrodinger"), "shared"))
    monkeypatch.setattr(replication.accepted, "optimizer", lambda _: "optimizer")
    monkeypatch.setattr(replication, "MapBalancedSampler", lambda states, actual_seed: (states, actual_seed))
    def fake_training(model, opt, sampler, **kwargs):
        calls.update(model=model.name, opt=opt, sampler=sampler, **kwargs); return {"ok": True}
    monkeypatch.setattr(replication.accepted, "scheduled_training", fake_training)
    monkeypatch.setattr(replication.accepted, "runtime_provenance", lambda _: {"accepted": True})
    class Attempt:
        output = tmp_path / "output"
        def __enter__(self): self.output.mkdir(); return self
        def __exit__(self, *args):
            (self.output / "attempt.json").write_text(json.dumps({"status": "COMPLETE"}))
            return False
    def begin(*args):
        calls["begin"] = args
        return Attempt()
    monkeypatch.setattr(replication.accepted.OwnedAttempt, "begin", begin)
    monkeypatch.setattr(replication.accepted, "_write_json", lambda path, value: calls.setdefault("record", value))
    record = replication.run(seed=seed, mode=mode, decision_path=decision_path, argv=["wrapper", "--seed", str(seed)])
    assert calls["model"] == mode and calls["seed"] == seed and calls["updates"] == 8000
    assert calls["resume"] is None and calls["sampler"] == (("state",), seed)
    assert calls["config"] == replication.accepted.FROZEN_CONFIG
    assert replication.accepted.STAGES == replication.REPLICATION_STAGES
    assert calls["begin"] == (replication.ROOT, replication.LEDGER, "B", f"replication-{seed}-{mode}-8000")
    assert record["wrapper_provenance"]["actual_argv"] == ["wrapper", "--seed", str(seed)]
    assert record["provenance"] == {"accepted": True}
    assert record["decision_sha256"] == hashlib.sha256(decision_path.read_bytes()).hexdigest()
    assert record["resource_provenance"]["installed_limits"] == replication.REPLICATION_STAGES


@pytest.mark.parametrize("seed,mode", [(1701, "softmax"), (1706, "softmax"), (1702, "bad")])
def test_rejects_unfrozen_seed_or_mode(seed, mode, tmp_path):
    with pytest.raises(PermissionError):
        replication.run(seed=seed, mode=mode, decision_path=tmp_path / "missing.json")


@pytest.mark.parametrize("changes", [{"target_updates": 7999}, {"replication_plan_sha256": "wrong"}, {"prepared_sha256": "wrong"}])
def test_decision_must_bind_updates_plan_and_prepared(changes):
    with pytest.raises(PermissionError):
        replication._validate_authorization(_decision(**changes), seed=1702, mode="softmax", prepared_sha256="prepared")


def test_original_resource_table_and_wrapper_hash_are_literal():
    assert replication.ORIGINAL_STAGES == {"A": 700.0, "B": 2000.0, "C": 1900.0, "D": 1300.0}
    assert replication.REPLICATION_STAGES == {"A": 700.0, "B": 3500.0, "C": 400.0, "D": 1300.0}
    provenance = replication.wrapper_provenance(["x"])
    assert provenance["replication_plan_sha256"] == replication.PLAN_SHA256
    assert provenance["wrapper_sha256"] == hashlib.sha256(MODULE.read_bytes()).hexdigest()


def test_actual_prepared_fixture_and_authorization_record_bind_cleanly():
    _, input_ids = replication.accepted._prepared_ids(replication.PREPARED)
    decision_path = replication.HERE / "decisions" / "1702-softmax.json"
    decision = json.loads(decision_path.read_text())
    replication._validate_authorization(decision, seed=1702, mode="softmax",
                                        prepared_sha256=input_ids["prepared_sha256"])


def test_default_workspace_paths_are_repository_local():
    assert replication.WORKSPACE == Path(__file__).parents[1]
    assert replication.ROOT == replication.WORKSPACE / "execution" / "model_training_comparison"
    assert replication.PREPARED.is_file() and replication.LEDGER.is_file()


def test_resource_installation_rejects_changed_global_contract(monkeypatch):
    monkeypatch.setattr(replication.accepted, "STAGES", dict(replication.ORIGINAL_STAGES))
    monkeypatch.setattr(replication.accepted, "GLOBAL_CAP", 7199.0)
    with pytest.raises(replication.accepted.BudgetError):
        replication.install_replication_resource_limits()
