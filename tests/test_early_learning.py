"""Narrow tests for the inference-only early-learning block.

Runtime tests are intentionally tiny. They run only after the static review gate;
no test here opens the final-test panel or performs an optimizer update.
"""
from __future__ import annotations

import copy
import json
import math
from pathlib import Path

import pytest

from execution.early_learning import command, study


def _points(gap: float = 0.0) -> list[dict]:
    rows = []
    for update in study.UPDATES:
        x = update / 1000
        q = 0.2 + 0.03 * x + gap
        kl = 1.0 - 0.02 * x
        rows.append({"update": update, "metrics": {
            "q": q, "kl": kl, "brier": kl * 0.5,
            "teacher_entropy": 1.2, "policy_entropy": 1.1,
            "greedy_q": q - 0.01, "challenge_q": q - 0.02,
            "nonoptimal_mass": 0.2}})
    return rows


def test_smoke_gate() -> None:
    assert study.UPDATES == tuple(range(0, 3001, 100))
    assert len(study.UPDATES) == 31
    assert len(study.REUSED) == 4
    assert len(study.PROBE_UPDATES) == 7
    assert command.CAPS == {"A": 120.0, "B": 1440.0, "C": 0.0, "D": 240.0}


def _state_bank_fixture():
    rows, masks = [], []
    # Unequal state counts per map make the original map-balanced weights
    # distinguishable from uniform-per-state weighting.
    specs = [(1, "IIIIIIII"), (1, "IIIIIIII"), (2, "LLLLLLLL"),
             (3, "IIIILLLL"), (3, "IIIILLLL"), (4, "IIIILLLL")]
    for index, (map_id, family) in enumerate(specs):
        q = [0.5, 0.5, 0.0, 0.0]
        rows.append({"canonical": f"map-{map_id}-{index}", "map_id": map_id,
            "family": family, "goal": index + 10, "current": index + 20, "q": q})
        masks.append([True, True, True, True])
    metadata = study.statewise_metadata(rows, masks)
    return rows, metadata


def _scored_fixture(rows, metadata, *, p=None, kl=None):
    if p is None:
        p = [[0.4, 0.4, 0.1, 0.1] for _ in rows]
    if kl is None:
        kl = [math.log(1.25)] * len(rows)
    arrays = {"p": p, "kl": kl,
        "nonoptimal_mass": [sum(values[i] for i in range(4) if row["q"][i] == 0)
                            for row, values in zip(rows, p)]}
    return study.statewise_scores(rows, arrays, metadata)


def test_statewise_weighting_argmax_and_transition_partition() -> None:
    rows, metadata = _state_bank_fixture()
    weights = [row["weight"] for row in metadata]
    assert weights == pytest.approx([0.2, 0.2, 0.4, 0.05, 0.05, 0.1])
    assert study._argmax_legal([0.4, 0.4, 0.2, 0.0], [True, True, True, False]) == 0
    earlier = _scored_fixture(rows, metadata)
    for item, flag in zip(earlier["states"], [True, True, False, False, False, True]):
        item["argmax_in_oracle_support"] = flag
    later = copy.deepcopy(earlier)
    onoff = [True, False, True, False, True, False]
    for index, item in enumerate(later["states"]):
        item["argmax_in_oracle_support"] = onoff[index]
        item["kl"] += index / 10
        item["A"] += index / 100
        item["B"] += index / 10 - index / 100
    result = study.statewise_transitions(earlier, later, "fixture")
    assert {key: value["count"] for key, value in result["groups"].items()} == {
        "on_on": 1, "on_off": 2, "off_on": 2, "off_off": 1}
    assert sum(value["weighted_prevalence"] for value in result["groups"].values()) == pytest.approx(1.0)
    assert result["group_closure_residual"] == pytest.approx(0.0, abs=1e-15)
    assert set(result["stratum_contributions"]) == {"routine", "challenge"}
    broken = copy.deepcopy(later)
    broken["states"][0]["A"] += 1e-6
    with pytest.raises(ValueError, match="group A\\+B"):
        study.statewise_transitions(earlier, broken, "bad-component-closure")
    all_on = _scored_fixture(rows, metadata)
    empty = study.statewise_transitions(all_on, all_on, "all-on")
    assert empty["groups"]["off_off"]["count"] == 0
    assert empty["groups"]["off_off"]["conditional_weighted_mean"] is None


def test_statewise_kl_decomposition_zero_support_and_nonoptimal_contrast() -> None:
    rows, metadata = _state_bank_fixture()
    qrows = copy.deepcopy(rows)
    for row in qrows:
        row["q"] = [0.9, 0.1, 0.0, 0.0]
    metadata = study.statewise_metadata(qrows, [row["legal_mask"] for row in metadata])
    early_p = [[0.63, 0.07, 0.15, 0.15] for _ in qrows]
    late_p = [[0.4, 0.4, 0.1, 0.1] for _ in qrows]
    early_kl = [0.9 * math.log(0.9 / 0.63) + 0.1 * math.log(0.1 / 0.07)] * len(qrows)
    late_kl = [0.9 * math.log(0.9 / 0.4) + 0.1 * math.log(0.1 / 0.4)] * len(qrows)
    early = _scored_fixture(qrows, metadata, p=early_p, kl=early_kl)
    late = _scored_fixture(qrows, metadata, p=late_p, kl=late_kl)
    assert early["weighted_nonoptimal_mass"] == pytest.approx(0.3)
    assert late["weighted_nonoptimal_mass"] == pytest.approx(0.2)
    assert sum(row["weight"] * row["kl"] for row in late["states"]) > sum(
        row["weight"] * row["kl"] for row in early["states"])
    assert early["weighted_A"] + early["weighted_B"] == pytest.approx(early["weighted_kl_from_states"])

    zero_supported = [[0.0, 0.7, 0.2, 0.1] for _ in qrows]
    invalid = _scored_fixture(qrows, metadata, p=zero_supported,
        kl=[1.0] * len(qrows))
    assert invalid["decomposition_available"] is False
    assert "zero on positive-q" in invalid["unavailable_states"][0]["reason"]
    zero_total = [[0.0, 0.0, 0.5, 0.5] for _ in qrows]
    invalid_total = _scored_fixture(qrows, metadata, p=zero_total, kl=[1.0] * len(qrows))
    assert invalid_total["decomposition_available"] is False
    tiny = [[1e-200, 0.5, 0.25, 0.25 - 1e-200] for _ in qrows]
    tiny_rows = copy.deepcopy(qrows)
    for row in tiny_rows:
        row["q"] = [1.0, 0.0, 0.0, 0.0]
    tiny_meta = study.statewise_metadata(tiny_rows, [row["legal_mask"] for row in metadata])
    tiny_scores = _scored_fixture(tiny_rows, tiny_meta, p=tiny,
        kl=[-math.log(1e-200)] * len(tiny_rows))
    assert tiny_scores["decomposition_available"] is True
    assert tiny_scores["states"][0]["A"] == pytest.approx(-math.log(1e-200))


def test_statewise_identity_and_invalid_distribution_rejected() -> None:
    rows, metadata = _state_bank_fixture()
    with pytest.raises(ValueError, match="missing, duplicated, or reordered"):
        study.statewise_scores(rows[:-1], {"p": [], "kl": [], "nonoptimal_mass": []}, metadata)
    altered = copy.deepcopy(rows)
    altered[0]["q"] = [0.4, 0.6, 0.0, 0.0]
    with pytest.raises(ValueError, match="oracle q differs"):
        study.statewise_scores(altered, {"p": [], "kl": [], "nonoptimal_mass": []}, metadata)
    duplicate = copy.deepcopy(rows)
    duplicate.append({**duplicate[0], "q": [0.4, 0.6, 0.0, 0.0]})
    with pytest.raises(ValueError, match="duplicate state identity"):
        study.statewise_metadata(duplicate, [[True, True, True, False]] * len(duplicate))
    with pytest.raises(ValueError, match="invalid or unnormalized"):
        _scored_fixture(rows, metadata, p=[[0.3, 0.3, 0.3, 0.3]] * len(rows))
    illegal_metadata = copy.deepcopy(metadata)
    illegal_metadata[0]["legal_mask"] = [True, True, True, False]
    with pytest.raises(ValueError, match="illegal action"):
        _scored_fixture(rows, illegal_metadata)


def test_analytic_windows_slopes_ties_and_sample_sd() -> None:
    rows = _points()
    summary = study.summarize_owner(rows)
    primary = summary["primary_800_2000"]["q"]
    assert primary["n"] == 13
    assert primary["mean"] == pytest.approx(0.2 + 0.03 * 1.4)
    assert primary["slope_per_1000_updates"] == pytest.approx(0.03)
    assert primary["residual_sd"] == pytest.approx(0.0, abs=1e-15)
    assert primary["residual_sd_definition"] == "sample standard deviation; denominator n-1"
    # The grid minimum ties are represented exactly, without interpolation.
    tied = copy.deepcopy(rows)
    for row in tied:
        row["metrics"]["kl"] = 1.0 if row["update"] in (0, 100, 300) else 2.0
    minima = study._minimum(tied, "kl")
    assert minima["tie_updates"] == [0, 100, 300]
    assert minima["contiguous_intervals"] == [[0, 100], [300, 300]]
    assert study._sample_sd([1.0, 3.0]) == pytest.approx(math.sqrt(2.0))
    assert study._sample_sd([1.0]) is None


def test_paired_gap_sd_uses_sample_denominator_and_descriptive_label() -> None:
    owners = []
    for seed, mode, gap in ((2201, "softmax", 0.0), (2201, "schrodinger", 0.1),
                            (2202, "schrodinger", 0.2), (2202, "softmax", 0.0)):
        points = _points(gap)
        # Deliberately non-linear, paired checkpoint gaps for an analytic SD.
        for row, delta in zip(points, [0.0, 0.1, 0.0] + [0.0] * 28):
            if mode == "schrodinger":
                row["metrics"]["q"] += delta
        owners.append({"seed": seed, "mode": mode, "points": points,
                       "summary": study.summarize_owner(points)})
    result = study.summarize_pairs(owners)
    cell = result["paired_sa_minus_softmax"]["early_0_1000"]["q"]
    assert cell["raw_gap_sd_definition"] == "sample standard deviation; denominator n-1"
    assert cell["residual_sd_definition"] == "sample standard deviation of OLS residuals; denominator n-1"
    expected = study._sample_sd([0.1, 0.2, 0.1] + [0.1] * 8)
    assert cell["per_seed_raw_gap_sd"][0] == pytest.approx(expected)
    assert result["inference"] == "descriptive_two_existing_seed_pairs_no_population_inference"


def test_missing_or_unordered_grid_rejected() -> None:
    rows = _points()
    with pytest.raises(ValueError, match="31-point"):
        study.summarize_owner(rows[:-1])
    rows[1], rows[2] = rows[2], rows[1]
    with pytest.raises(ValueError, match="31-point"):
        study.summarize_owner(rows)


def test_tampered_inventory_entry_rejected() -> None:
    inventory = json.loads(study.INVENTORY.read_text())
    entry = study._owner_entry(inventory, 2201, "softmax")
    tampered = copy.deepcopy(inventory)
    tampered["owners"].append(copy.deepcopy(entry))
    with pytest.raises(ValueError, match="missing or duplicated"):
        study._owner_entry(tampered, 2201, "softmax")


def test_tampered_checkpoint_and_source_rejected(tmp_path: Path) -> None:
    owner = tmp_path / "owner"
    (owner / "checkpoints").mkdir(parents=True)
    (owner / "checkpoints" / "initial.pt").write_bytes(b"tampered checkpoint")
    entry = {"path": str(owner), "seed": 2201, "mode": "softmax",
        "checkpoints": [[update, "0" * 64] for update in study.UPDATES]}
    with pytest.raises(ValueError, match="checkpoint file hash"):
        study._audit_checkpoints(entry, {"input_ids": {"frozen_source_hash": "source"},
            "training": {"initial_hash": "initial"}}, object(), object(), object())
    with pytest.raises(ValueError, match="model/data/evaluator"):
        study._validate_frozen_source_identity({"source_hashes": {"accepted_route_policy.py": "wrong"}},
                                               {"accepted_model": "right"})


def test_driver_rejects_changed_ledger_before_launch(tmp_path: Path, monkeypatch) -> None:
    # A rejected reservation must fail on EOF binding before any child launch.
    import time

    ledger = tmp_path / "ledger.jsonl"
    allocation = {"entry_id": "allocation", "kind": "inherited_budget",
        "charged_seconds": 0.0, "carried_budget_debit_seconds": 0.0,
        "allocation_seconds": {key: int(value) for key, value in command.CAPS.items()},
        "global_allocation_seconds": int(command.GLOBAL_CAP)}
    ledger.write_text(json.dumps(allocation) + "\n")
    monkeypatch.setattr(command, "LEDGER", ledger)
    monkeypatch.setattr(command, "LOCK", tmp_path / "reservation.lock")
    hashes = command.authority_hashes()
    review = tmp_path / "review.md"
    review.write_text("IMPLEMENTATION_REVIEW_VERDICT: PASS\n" + "\n".join(hashes.values()))
    decision = {"kind": "production", "stage": "B", "source_hashes": hashes,
        "inventory_sha256": command.sha256(command.INVENTORY),
        "plan_sha256": command.sha256(command.PLAN), "spec_sha256": command.sha256(command.SPEC),
        "ledger_sha256": "wrong", "review": {"path": str(review), "phase": "implementation",
            "sha256": command.sha256(review)}}
    with pytest.raises(RuntimeError, match="ledger EOF changed"):
        command._reserve(decision, "B", 300.0)


def test_uncertain_append_reconciles_single_preassigned_identity(tmp_path: Path, monkeypatch) -> None:
    ledger = tmp_path / "ledger.jsonl"
    allocation = {"entry_id": "allocation", "kind": "inherited_budget",
        "charged_seconds": 0.0, "carried_budget_debit_seconds": 0.0,
        "allocation_seconds": {key: int(value) for key, value in command.CAPS.items()},
        "global_allocation_seconds": int(command.GLOBAL_CAP)}
    ledger.write_text(json.dumps(allocation) + "\n")
    monkeypatch.setattr(command, "LEDGER", ledger)
    append = command._append_once
    calls = []
    def write_then_raise(row):
        calls.append(row["entry_id"])
        append(row)
        raise OSError("simulated post-append fsync uncertainty")
    monkeypatch.setattr(command, "_append_once", write_then_raise)
    row = {"entry_id": "fixed-charge-id", "kind": "driver_check", "stage": "A",
        "status": "FAILED", "charged_seconds": 1.0}
    assert command._append_once_certain(row) is True
    assert calls == ["fixed-charge-id"]
    rows = command._snapshot()[1]
    assert [item["entry_id"] for item in rows if item.get("kind") == "driver_check"] == ["fixed-charge-id"]


def test_terminal_durability_uncertainty_is_permanent(tmp_path: Path, monkeypatch) -> None:
    durable = command._durable
    for after_write in (False, True):
        path = tmp_path / ("terminal-after.json" if after_write else "terminal-before.json")
        state = {"uncertain": False}
        def fail_once(target, value):
            monkeypatch.setattr(command, "_durable", durable)
            if after_write:
                durable(target, value)
            raise OSError("injected terminal fsync failure" if after_write else "injected terminal write failure")
        monkeypatch.setattr(command, "_durable", fail_once)
        assert command._durable_certain(path, {"status": "COMPLETE"}, state) is False
        assert state["uncertain"] is True
        assert command._durable_certain(path, {"status": "FAILED_DRIVER"}, state) is False
        assert json.loads(path.read_text())["status"] == "FAILED_DRIVER"
    monkeypatch.setattr(command, "_durable", durable)


def test_overhead_reconciliation_requires_preassigned_full_identity(tmp_path: Path, monkeypatch) -> None:
    ledger = tmp_path / "ledger.jsonl"
    allocation = {"entry_id": "allocation", "kind": "inherited_budget",
        "charged_seconds": 0.0, "carried_budget_debit_seconds": 0.0,
        "allocation_seconds": {key: int(value) for key, value in command.CAPS.items()},
        "global_allocation_seconds": int(command.GLOBAL_CAP)}
    owner, session = tmp_path / "owner", tmp_path / "session"
    row = {"entry_id": "some-other-attempt", "kind": "driver_overhead", "stage": "B",
        "status": "ACCOUNTED", "charged_seconds": 6.0, "external_seconds": 10.0,
        "owner_charge_seconds": 4.0, "owner_output": str(owner), "output": str(owner),
        "driver_session": str(session)}
    ledger.write_text(json.dumps(allocation) + "\n" + json.dumps(row) + "\n")
    monkeypatch.setattr(command, "LEDGER", ledger)
    with pytest.raises(RuntimeError, match="overhead reconciliation mismatch"):
        command._append_overhead(owner, session, 10.0, 4.0, "preassigned-overhead-id")


def test_composed_tiny_inference_fixture(monkeypatch, tmp_path: Path) -> None:
    """Exercise decision -> reserved owner -> authenticated study -> durable schema.

    The fixture seam narrows the score grid and validation panel only. It uses
    the immutable update-0 checkpoint and actual accepted model/evaluator.
    """
    import os

    from execution.early_learning import study as study_module
    from execution.update_efficiency import watchdog

    attempts = tmp_path / "attempts"
    ledger = tmp_path / "ledger.jsonl"
    lock = tmp_path / "driver.lock"
    attempts.mkdir()
    allocation = {"entry_id": "allocation", "kind": "inherited_budget",
        "charged_seconds": 0.0, "carried_budget_debit_seconds": 0.0,
        "allocation_seconds": {key: int(value) for key, value in command.CAPS.items()},
        "global_allocation_seconds": int(command.GLOBAL_CAP)}
    ledger.write_text(json.dumps(allocation) + "\n")
    monkeypatch.setattr(command, "ATTEMPTS", attempts)
    monkeypatch.setattr(command, "LEDGER", ledger)
    monkeypatch.setattr(command, "LOCK", lock)
    monkeypatch.setattr(study_module, "ATTEMPTS", attempts)
    monkeypatch.setattr(study_module, "LEDGER", ledger)

    # Preserve the production checkpoint audit; only score one new cell on two
    # validation problems so this composed test stays narrow.
    monkeypatch.setattr(study_module, "_audit_paired_stream", lambda inventory: {2201: "fixture", 2202: "fixture"})

    review = tmp_path / "implementation-review.md"
    hashes = command.authority_hashes()
    review.write_text("IMPLEMENTATION_REVIEW_VERDICT: PASS\n" + "\n".join(hashes.values()))
    decision_path = tmp_path / "decision.json"
    # decision hashes bind reviewed worktree files, while the runtime fixture
    # only redirects ephemeral ledgers/outputs to the temporary directory.
    acceptance = tmp_path / "astra-acceptance.json"
    acceptance.write_text(json.dumps({"verdict": "ASTRA_ACCEPTANCE_VERDICT: PASS",
        "implementation_review_path": str(review.resolve()),
        "implementation_review_sha256": command.sha256(review), "source_hashes": hashes}))
    decision = command.make_owner_decision(2201, "softmax", review, acceptance, decision_path)
    decision["ledger_sha256"] = command.ledger_eof()
    decision["argv_template"] = [__import__("sys").executable, "-m", "execution.early_learning.study",
        "--decision", str(decision_path.resolve()), "--session", "SESSION", "--nonce", "NONCE"]
    decision["argv"] = decision["argv_template"][:5]
    command._durable(decision_path, decision)
    monkeypatch.setattr(study_module.os, "getppid", lambda: os.getpid())

    def supervise(argv, cwd, session, deadline):
        session_file, nonce = Path(argv[argv.index("--session") + 1]), argv[argv.index("--nonce") + 1]
        study_module.run(decision_path=decision_path, session_path=session_file, nonce=nonce,
            argv=argv, _fixture={"updates": [100], "validation_count": 2})
        owner = attempts / "early-2201-softmax-0-to-3000"
        return {"exit_code": 0, "timed_out": False, "cleanup_verified": True,
                "owner": str(owner)}
    monkeypatch.setattr(watchdog, "supervise", supervise)
    command.run_decision(decision_path, _fixture={"updates": [100]})
    owner = attempts / "early-2201-softmax-0-to-3000"
    output = json.loads((owner / "result.json").read_text())
    assert output["status"] == "COMPLETE"
    assert output["points"][0]["update"] == 100
    detail = json.loads((owner / "score-0100.json").read_text())
    assert len(detail["rollout"]["problems"]) == 2
    assert len(detail["proper"]["arrays"]["ce"]) == 4
    assert {row["family"] for row in detail["rollout"]["problems"]} == {"IIIIIIII", "IIIILLLL"}
    assert {row["stratum"] for row in detail["statewise"]["states"]} == {"routine", "challenge"}
    assert "proper_entropy" not in detail["point"]["metrics"]
    assert detail["point"]["metrics"]["teacher_entropy"] == pytest.approx(
        detail["proper"]["weighted"]["entropy_q"])
    assert not lock.exists()


def test_tiny_sa_probe_is_finite_and_read_only() -> None:
    import torch
    from schrodinger import route_policy_experiment as accepted
    from schrodinger.route_policy import RoutePolicy
    from schrodinger.route_policy_data import load_validation
    from schrodinger.route_policy_evaluation import mechanism_probe
    from schrodinger.route_policy_metrics import heldout_bank

    accepted.configure_runtime()
    validation = load_validation()
    bank = heldout_bank(validation.problems)
    candidates = accepted.validation_probe_candidates(bank)
    chosen = [next(c for c in candidates if c.family != "IIIILLLL"),
              next(c for c in candidates if c.family == "IIIILLLL")]
    checkpoint = study.WORKSPACE / study._owner_entry(json.loads(study.INVENTORY.read_text()),
        2201, "schrodinger")["path"] / "checkpoints" / "initial.pt"
    model = RoutePolicy("schrodinger")
    payload = torch.load(checkpoint, map_location="cpu", weights_only=False)
    model.load_state_dict(payload["model"])
    model.eval()
    before = accepted.state_hash(model)
    with torch.inference_mode():
        result = mechanism_probe(model, chosen)
    assert result["applicable"] is True
    assert result["numerical"] is not None
    assert len(result["records"]) == 2 * 2 * 2 * 13
    assert len(result["fullpath_records"]) == 2
    assert all(math.isfinite(row["all_rows_tv"]) and math.isfinite(row["dt_h_spectral_norm"])
               for row in result["records"])
    assert accepted.state_hash(model) == before


def test_watchdog_timeout_reaps_descendant_process_group(tmp_path: Path) -> None:
    import subprocess
    import sys
    import time
    from execution.update_efficiency import watchdog

    proof = tmp_path / "descendant-reaped.json"
    child = f'''\
import json, pathlib, signal, subprocess, sys, time
proof = pathlib.Path({str(proof)!r})
grand = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(20)"])
def stop(sig, frame):
    grand.terminate()
    rc = grand.wait(timeout=1)
    proof.write_text(json.dumps({{"pid": grand.pid, "returncode": rc}}))
    raise SystemExit(0)
signal.signal(signal.SIGTERM, stop)
time.sleep(20)
'''
    session = tmp_path / "watchdog-session"
    result = watchdog.supervise([sys.executable, "-c", child], tmp_path, session,
                                time.monotonic() + 3.0)
    reaped = json.loads(proof.read_text())
    assert result["timed_out"] is True and result["cleanup_verified"] is True
    assert reaped["returncode"] < 0
    assert watchdog.group_gone(result["child_pid"], time.monotonic() + 1.0)
