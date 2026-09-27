import importlib.util
import copy
import json
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pytest


MODULE = Path(__file__).parents[1] / "execution" / "seed_replication" / "analyze.py"
SPEC = importlib.util.spec_from_file_location("seed_replication_analysis", MODULE)
analysis = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(analysis)


def _routes(q, routine=None, challenge=None):
    return {"mixture": {"Q": q}, "strata": {"routine": {"Q": q if routine is None else routine},
            "challenge": {"Q": q if challenge is None else challenge}}, "cache": {"ignored": True}}


def test_fresh_owner_names_and_seed_guard_are_literal():
    assert analysis._owner(1702, "softmax") == "replication-1702-softmax-8000"
    assert analysis._owner(1705, "schrodinger") == "replication-1705-schrodinger-8000"
    with pytest.raises(PermissionError):
        analysis.run(seed=1701)


def test_quality_control_makes_exactly_two_new_sa_calls_with_fresh_seed(monkeypatch):
    calls = []
    def rollout(model, problems, **kwargs):
        calls.append(kwargs)
        return _routes(.51 if kwargs["temperature"] == .75 else .49, .51, .49)
    monkeypatch.setattr(analysis, "evaluate_rollouts", rollout)
    result = analysis._quality_control("sa", ("p",), identity=("checkpoint", "sa-qc", 8000), seed=1703,
                                       support=frozenset(), sm_stored=_routes(.50), sa_stored=_routes(.48))
    assert [call["temperature"] for call in calls] == [.75, 1.25]
    assert all(call["seed"] == 1703 and call["splitcode"] == 1 and call["replicate"] == 0 and call["k"] == 32 for call in calls)
    assert result["selected_temperature"] == .75 and result["matched"]


def test_resource_contract_is_delegated_to_the_frozen_wrapper(monkeypatch):
    seen = []
    monkeypatch.setattr(analysis.replication_train, "install_replication_resource_limits", lambda: seen.append(True))
    monkeypatch.setattr(analysis.accepted, "configure_runtime", lambda: None)
    monkeypatch.setattr(analysis.accepted.OwnedAttempt, "begin", lambda *args: (_ for _ in ()).throw(RuntimeError("stop before analysis")))
    with pytest.raises(RuntimeError, match="stop before analysis"):
        analysis.run(seed=1702)
    assert seen == [True]


def test_actual_owner_authority_rejects_mutated_wrapper_decision_resource_and_source():
    root = analysis.ROOT
    _, ids = analysis.accepted._prepared_ids(root / "prepare-001" / "prepared.json")
    record = json.loads((root / analysis._owner(1702, "softmax") / "result.json").read_text())
    evidence = analysis._owner_authority(record, seed=1702, mode="softmax", ids=ids)
    assert evidence["wrapper_sha256"] == analysis._sha(Path(analysis.replication_train.__file__))
    for path, value in ((["wrapper_provenance", "wrapper_sha256"], "wrong"),
                        (["wrapper_provenance", "replication_plan_sha256"], "wrong"),
                        (["decision_sha256"], "wrong"),
                        (["resource_provenance", "resource_limits_sha256"], "wrong"),
                        (["provenance", "source_hash"], "wrong")):
        broken = copy.deepcopy(record)
        target = broken
        for key in path[:-1]:
            target = target[key]
        target[path[-1]] = value
        with pytest.raises(analysis.accepted.IdentityError):
            analysis._owner_authority(broken, seed=1702, mode="softmax", ids=ids)


@pytest.mark.parametrize("field,value", [("seed", 1701), ("mode", "schrodinger"), ("update", 7999),
                                           ("source", "wrong"), ("config", {"wrong": True})])
def test_actual_checkpoint_identity_rejects_mutated_scalar_or_source(monkeypatch, field, value):
    root = analysis.ROOT
    _, ids = analysis.accepted._prepared_ids(root / "prepare-001" / "prepared.json")
    original = analysis.torch.load
    def bad_load(path, **kwargs):
        payload = original(path, **kwargs)
        if Path(path).name == "update-8000.pt":
            payload = copy.deepcopy(payload)
            payload["identity"][field] = value
        return payload
    monkeypatch.setattr(analysis.torch, "load", bad_load)
    with pytest.raises(analysis.accepted.IdentityError):
        analysis._checkpoint(root, 1702, "softmax", ids)


def test_frozen_abc_counts_and_both_model_assembly_forward_current_seed(monkeypatch):
    frozen = analysis.load_matched_support(analysis.ROOT / "threeway-diagnosis-001" / "matched_support.json")
    banks, routes = analysis._frozen_abc(frozen)
    assert len(frozen["retained"]) == 24
    assert [len(bank.selected) for bank in banks] == [768, 768, 768]
    assert [len(rows) for rows in routes] == [144, 144, 144]
    candidate = SimpleNamespace(canonical=b"x", map_id=1, family="IIIIIIII", goal=2, current=3, q=(1., 0., 0., 0.))
    calls = []
    monkeypatch.setattr(analysis, "evaluate_proper", lambda *args, **kwargs: {"rows": [candidate], "arrays": {"p": [[1., 0., 0., 0.]]}})
    monkeypatch.setattr(analysis, "evaluate_rollouts", lambda *args, **kwargs: (calls.append(kwargs) or _routes(.5)))
    assembled = {}
    for index, name in enumerate("ABC"):
        split = 0 if name in "AB" else 1
        sm = analysis._abc_score("sm", "bank", (SimpleNamespace(canonical=b"x", map_id=1, family="IIIIIIII", start=0, goal=2),), identity=("sm", name, 8000), seed=1704, split=split, support=frozenset())
        sa = analysis._abc_score("sa", "bank", (SimpleNamespace(canonical=b"x", map_id=1, family="IIIIIIII", start=0, goal=2),), identity=("sa", name, 8000), seed=1704, split=split, support=frozenset())
        assembled[name] = analysis._abc_compare(sm, sa)
    assert set(assembled) == {"A", "B", "C"} and all({"sm", "sa", "state", "quality"} <= set(row) for row in assembled.values())
    assert len(calls) == 12 and all(call["seed"] == 1704 and call["replicate"] == 0 for call in calls)
    assert [call["splitcode"] for call in calls] == [0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1]


def test_composed_output_has_primary_8k_pair_abc_and_qc_requirements():
    output = analysis._compose_output(seed=1702, ids={"frozen_source_hash": "source"},
                                      pair={"sm_payload": object(), "sa_payload": object(), "batch_prefix": {"updates": 8000}},
                                      stored={"8000": {"primary_delta_sa_minus_sm": .1, "paired_8000": {"states": {}, "route_sets": {}}}},
                                      abc={name: {"sm": {}, "sa": {}, "state": {}, "quality": {}} for name in "ABC"},
                                      qc={"matched": False, "grid": []}, argv=["python"], elapsed_seconds=.1)
    assert output["stored_fullvalidation"]["8000"]["primary_delta_sa_minus_sm"] == .1
    assert {"states", "route_sets"} <= set(output["stored_fullvalidation"]["8000"]["paired_8000"])
    assert set(output["frozen_abc"]) == {"A", "B", "C"} and "matched" in output["quality_control"]
    assert {"execution/paired_behavior/job.py", "execution/model_training_comparison/threeway_diagnosis_job.py"} <= set(output["source_hashes"])


def test_actual_1702_retained_events_and_direct_hex_adapters_after_pair_completion():
    """Run only after the fresh 1702 pair exists; no model inference is performed."""
    root = analysis.ROOT
    _, ids = analysis.accepted._prepared_ids(root / "prepare-001" / "prepared.json")
    pair = analysis.validate_pair(root, 1702, ids)
    validation = analysis.load_validation()
    bank = analysis.heldout_bank(validation.problems)
    for mode in ("softmax", "schrodinger"):
        for update in analysis.UPDATES:
            event = analysis._event(root, analysis._owner(1702, mode), update)
            rows, proper = analysis._storedproper(event, bank)
            greedy, _ = analysis._storedroutes(event, "greedy", validation.problems)
            k32, _ = analysis._storedroutes(event, "t1_k32", validation.problems)
            assert len(rows) == len(bank.selected) == len(proper["arrays"]["p"])
            assert len(greedy) == len(validation.problems)
            assert len(k32) == 32 * len(validation.problems)
            assert isinstance(rows[0]["canonical"], bytes) and isinstance(k32[0]["route"], bytes)
    assert pair["batch_prefix"]["updates"] == 8000
    assert len(pair["batch_prefix"]["digest_sha256"]) == 64
