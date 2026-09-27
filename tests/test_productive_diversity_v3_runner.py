import json
import signal
import sys
from copy import deepcopy
from pathlib import Path

import pytest

from schrodinger.productive_diversity_v3_runner import Attempt, Deadline, RunnerError, _prior, write_json, _validate_pass
from schrodinger.productive_diversity_v3_runner import execute_pipeline
from schrodinger import productive_diversity_v3_runner as runner
from schrodinger import productive_diversity_v3_data as data


def _ledger(path: Path, *rows: dict) -> None:
    path.write_text("".join(json.dumps(row) + "\n" for row in rows))


def _attempt(tmp_path, **kwargs):
    options = {"lock": tmp_path / "lock", "ledger": tmp_path / "ledger.jsonl",
               "rejections": tmp_path / "rejections"}
    options.update(kwargs)
    return Attempt(tmp_path / "out", **options)


def test_strict_json_and_exclusive_write(tmp_path):
    path = tmp_path / "x.json"
    write_json(path, {(1, 2): b"x", "cache": "omit"})
    assert path.exists()
    with pytest.raises(FileExistsError):
        write_json(path, {})


def test_prior_carry_is_global_only_and_duplicate_ids_rejected(tmp_path):
    ledger = tmp_path / "ledger.jsonl"
    _ledger(ledger, {"entry_id": "carry", "carried_budget_debit_seconds": 443.384519002},
            {"entry_id": "new", "charged_seconds": 5, "budget_allowance_seconds": 2})
    assert _prior(ledger) == (7.0, 450.384519002)
    _ledger(ledger, {"entry_id": "same"}, {"entry_id": "same"})
    with pytest.raises(RunnerError, match="duplicate ledger entry_id"):
        _prior(ledger)
    _ledger(ledger, {"entry_id": "bad", "charged_seconds": float("nan")})
    with pytest.raises(RunnerError, match="negative ledger debit"):
        _prior(ledger)
    _ledger(ledger, {"entry_id": "bad-allowance", "charged_seconds": 2, "budget_allowance_seconds": -2})
    with pytest.raises(RunnerError, match="negative ledger debit"):
        _prior(ledger)
    _ledger(ledger, {"entry_id": "only-charge", "charged_seconds": 1})
    with pytest.raises(RunnerError, match="exactly one carried"):
        _prior(ledger, require_carry=True)
    with pytest.raises(RunnerError, match="exactly one carried"):
        _prior(tmp_path / "absent.jsonl", require_carry=True)
    _ledger(ledger, {"entry_id": "c1", "carried_budget_debit_seconds": 443.384519002},
            {"entry_id": "c2", "carried_budget_debit_seconds": 443.384519002})
    with pytest.raises(RunnerError, match="exactly one carried"):
        _prior(ledger, require_carry=True)


def test_deadline_uses_stage_global_and_tightening_override(tmp_path):
    ledger = tmp_path / "ledger.jsonl"
    _ledger(ledger, {"entry_id": "new", "charged_seconds": 1568.0})
    with pytest.raises(Deadline):
        _attempt(tmp_path, ledger=ledger).deadline()
    _ledger(ledger, {"entry_id": "new", "charged_seconds": 10.0})
    assert _attempt(tmp_path, ledger=ledger, deadline_seconds=3.0).deadline() == 3.0
    assert _attempt(tmp_path, ledger=ledger, deadline_seconds=99999.0).deadline() == 1438.0
    with pytest.raises(RunnerError, match="deadline override"):
        _attempt(tmp_path, ledger=ledger, deadline_seconds=float("nan")).deadline()


def test_output_and_lock_rejections_are_local_and_charged_once(tmp_path):
    output = tmp_path / "out"
    output.mkdir()
    with pytest.raises(FileExistsError):
        with _attempt(tmp_path):
            pass
    rows = [json.loads(line) for line in (tmp_path / "ledger.jsonl").read_text().splitlines()]
    assert len(rows) == 1 and rows[0]["status"] == "REJECTED"
    assert list((tmp_path / "rejections").glob("rejected-*.json"))
    output.rmdir()
    (tmp_path / "lock").write_text("other")
    with pytest.raises(FileExistsError):
        with _attempt(tmp_path):
            pass
    assert len((tmp_path / "ledger.jsonl").read_text().splitlines()) == 2


def test_postlock_output_race_cleans_only_owned_lock_and_charges(tmp_path, monkeypatch):
    attempt = _attempt(tmp_path)
    original = Path.mkdir
    def race(path, *args, **kwargs):
        if path == attempt.output:
            original(path, *args, **kwargs)
            raise FileExistsError("raced")
        return original(path, *args, **kwargs)
    monkeypatch.setattr(Path, "mkdir", race)
    with pytest.raises(FileExistsError, match="raced"):
        with attempt:
            pass
    assert attempt.output.exists() and not (tmp_path / "lock").exists()
    assert len((tmp_path / "ledger.jsonl").read_text().splitlines()) == 1


def test_log_failure_charges_once_cleans_lock_and_propagates(tmp_path):
    def fail_log(*_):
        raise OSError("disk full")
    with pytest.raises(RunnerError, match="mandatory attempt log failed"):
        with _attempt(tmp_path, log_writer=fail_log):
            pass
    rows = [json.loads(line) for line in (tmp_path / "ledger.jsonl").read_text().splitlines()]
    assert len(rows) == 1 and rows[0]["status"] == "FAILED"
    assert not (tmp_path / "lock").exists()


def test_deadline_cleanup_restores_previous_handler(tmp_path):
    old_handler = signal.getsignal(signal.SIGALRM)
    old_timer = signal.setitimer(signal.ITIMER_REAL, 0.0)
    try:
        with _attempt(tmp_path, deadline_seconds=0.01):
            with pytest.raises(Deadline):
                signal.raise_signal(signal.SIGALRM)
        assert signal.getsignal(signal.SIGALRM) == old_handler
    finally:
        signal.setitimer(signal.ITIMER_REAL, *old_timer)


def _eight_records():
    root = Path(__file__).resolve().parents[1] / "execution/next_level_v3/fixtures"
    rows = []; map_id = 0
    for filename, family in (("recovery_b_i8.json", "IIIIIIII"), ("recovery_b_l8.json", "LLLLLLLL"),
                             ("recovery_b_mixed.json", "IIIILLLL")):
        payload = json.loads((root / filename).read_text())
        names = (("base", payload["base_walls"]), ("validation", payload["validation_walls"]),
                 ("test", payload["test_walls"])) if family != "IIIILLLL" else (("base", payload["base_walls"]), ("variant", payload["variant_walls"]))
        for _, raw in names:
            walls = frozenset(raw); pairs = []
            for start, goal, *_ in payload["pairs"]:
                distance, multiplicity = data.bfs_counts(walls, goal, 12)
                pairs.append((start, goal, distance[start], multiplicity[start]))
            rows.append({"n": 12, "map_id": map_id, "family": family,
                         "canonical": data.canonical_map(walls, 12), "walls": walls,
                         "shortlists": {pair[2]: {"retained": (pair,)} for pair in pairs}})
            map_id += 1
    return tuple(rows)


def test_real_eight_map_selection_writes_immutable_pipeline_artifacts(tmp_path):
    records = _eight_records()
    pools = {family: data.PoolResult(family, tuple(row["canonical"] for row in records if row["family"] == family), 0, 0, 0, 0)
             for family in data.FAMILIES}
    ranking = {"retained": ({"window_start": 12, "window": (12, 13, 14), "quota": (1, 1, 1)},)}
    config = data.SelectionConfig((12, 13, 14), (1, 1, 1), 1)
    counts = {"val_routine": 1, "val_mixed": 1, "test_routine": 1, "test_mixed": 1}
    with _attempt(tmp_path) as attempt:
        outcome = execute_pipeline(attempt, pools_fn=lambda family: pools[family],
                                   assemble_fn=lambda _pools: records, rank_fn=lambda _records: ranking,
                                   config=config, counts=counts)
    assert outcome["outcome"] == "FIRST_FULL_DATASET_PASS"
    assert (tmp_path / "out" / "manifest.json").exists()
    assert json.loads((tmp_path / "out" / "attempt.json").read_text())["manifest_sha256"]
    assert len(list((tmp_path / "out").glob("proposal-*.json"))) == 5


def test_raw_capacity_failure_persists_truthful_result(tmp_path):
    records = _eight_records()
    pools = {family: data.PoolResult(family, (), 0, 0, 0, 0) for family in data.FAMILIES}
    with _attempt(tmp_path) as attempt:
        outcome = execute_pipeline(attempt, pools_fn=lambda family: pools[family],
                                   assemble_fn=lambda _pools: records, rank_fn=lambda _records: {"retained": ()},
                                   config=data.SelectionConfig((12, 13, 14), (1, 1, 1), 1),
                                   counts={"val_routine": 1, "val_mixed": 1, "test_routine": 1, "test_mixed": 1})
    assert outcome["outcome"] == "RAW_JOINT_CAPACITY_FAILED"
    assert json.loads((tmp_path / "out" / "summary.json").read_text())["outcome"] == "RAW_JOINT_CAPACITY_FAILED"


def test_real_tiny_pool_assemble_rank_capacity_failure(tmp_path):
    records = _eight_records()
    pools = {family: data.PoolResult(family, tuple(row["canonical"] for row in records if row["family"] == family), 0, 0, 0, 0)
             for family in data.FAMILIES}
    with _attempt(tmp_path) as attempt:
        outcome = execute_pipeline(attempt, pools_fn=lambda family: pools[family],
                                   config=data.SelectionConfig((12, 13, 14), (1, 1, 1), 1),
                                   counts={"val_routine": 1, "val_mixed": 1, "test_routine": 1, "test_mixed": 1})
    assert outcome["outcome"] == "RAW_JOINT_CAPACITY_FAILED"
    assert json.loads((tmp_path / "out" / "ranking.json").read_text())["status"] == "RAW_JOINT_CAPACITY_FAILED"


def test_pipeline_deadline_after_pool_persists_partial_summary_and_failed_attempt(tmp_path):
    records = _eight_records()
    pools = {family: data.PoolResult(family, tuple(row["canonical"] for row in records if row["family"] == family), 0, 0, 0, 0)
             for family in data.FAMILIES}
    calls = []
    def interrupted(family):
        calls.append(family)
        if len(calls) == 2:
            raise Deadline("injected after first pool")
        return pools[family]
    with pytest.raises(Deadline, match="injected"):
        with _attempt(tmp_path) as attempt:
            execute_pipeline(attempt, pools_fn=interrupted)
    out = tmp_path / "out"
    summary = json.loads((out / "summary.json").read_text())
    attempt_record = json.loads((out / "attempt.json").read_text())
    assert (out / "pool-IIIIIIII.json").exists() and (out / "manifest.json").exists()
    assert summary["outcome"] == "DEADLINE_FAILED" and "injected after first pool" in summary["error"]
    assert attempt_record["status"] == "FAILED" and attempt_record["manifest_sha256"] == summary["manifest_sha256"]
    assert len((tmp_path / "ledger.jsonl").read_text().splitlines()) == 1 and not (tmp_path / "lock").exists()


def _valid_selection_result():
    records = _eight_records()
    ranking = {"retained": ({"window_start": 12, "window": (12, 13, 14), "quota": (1, 1, 1)},)}
    counts = {"val_routine": 1, "val_mixed": 1, "test_routine": 1, "test_mixed": 1}
    result = data.run_ranked_proposals(ranking, records, config=data.SelectionConfig((12, 13, 14), (1, 1, 1), 1), counts=counts)
    return records, ranking, counts, result


@pytest.mark.parametrize("mutation,match", [
    (lambda result, ranking: result.update(proposal={"window_start": 99}), "retained ranking"),
    (lambda result, ranking: result["stages"]["validation_routine"][0]["result"].update(outcome="BAD"), "non-OK"),
    (lambda result, ranking: result["stages"]["validation_routine"][0].update(family="IIIILLLL"), "wrapper family"),
    (lambda result, ranking: result["stages"]["validation_mixed"][0]["result"]["selected"].pop(), "quota"),
    (lambda result, ranking: result["stages"]["validation_mixed"][0]["result"]["selected"][0].update(length=99), "inventory"),
    (lambda result, ranking: result["stages"]["validation_mixed"][0]["result"]["selected"][0].update(n=8), "identity"),
    (lambda result, ranking: result["stages"]["validation_mixed"][0]["result"]["selected"][0].update(M=17), "inventory"),
    (lambda result, ranking: result["stages"]["validation_mixed"][0]["result"]["selected"][0].update(Mnovel=1), "novelty"),
    (lambda result, ranking: result["stages"]["training"].update(support_hash="0" * 64), "support hash"),
])
def test_validate_pass_rejects_literal_corruptions(mutation, match):
    records, ranking, counts, result = _valid_selection_result()
    result, ranking = deepcopy(result), deepcopy(ranking)
    mutation(result, ranking)
    with pytest.raises(RunnerError, match=match):
        _validate_pass(result, records, counts, 1, ranking)


def test_success_manifest_recomputes_artifacts_and_serializes_science_fields(tmp_path):
    records = _eight_records()
    pools = {family: data.PoolResult(family, tuple(row["canonical"] for row in records if row["family"] == family), 0, 0, 0, 0) for family in data.FAMILIES}
    ranking = {"retained": ({"window_start": 12, "window": (12, 13, 14), "quota": (1, 1, 1)},)}
    with _attempt(tmp_path) as attempt:
        execute_pipeline(attempt, pools_fn=lambda family: pools[family], assemble_fn=lambda _pools: records,
                         rank_fn=lambda _records: ranking, config=data.SelectionConfig((12, 13, 14), (1, 1, 1), 1),
                         counts={"val_routine": 1, "val_mixed": 1, "test_routine": 1, "test_mixed": 1})
    out = tmp_path / "out"; manifest = json.loads((out / "manifest.json").read_text())
    attempt_record = json.loads((out / "attempt.json").read_text())
    assert manifest["effective_config"]["seeds"]["pool"] == data.POOL_SEED
    assert manifest["effective_config"]["selection"]["quota"] == [1, 1, 1]
    assert manifest["runtime"]["python"] and "schrodinger/productive_diversity_v3_data.py" in manifest["sources"]
    assert attempt_record["manifest_sha256"] == __import__("hashlib").sha256((out / "manifest.json").read_bytes()).hexdigest()
    for name, digest in manifest["outputs"].items():
        assert __import__("hashlib").sha256((out / name).read_bytes()).hexdigest() == digest
    training = json.loads((out / "proposal-12-training.json").read_text())
    held = json.loads((out / "proposal-12-validation_mixed.json").read_text())
    assert "cache" not in training["result"] and training["result"]["profile"] and training["result"]["support"]
    assert held["results"][0]["result"]["profile"] and held["results"][0]["result"]["evidence"]


def test_post_training_callback_deadline_preserves_stage_artifact_and_failed_attempt(tmp_path, monkeypatch):
    records = _eight_records(); pools = {f: data.PoolResult(f, tuple(r["canonical"] for r in records if r["family"] == f), 0, 0, 0, 0) for f in data.FAMILIES}
    ranking = {"retained": ({"window_start": 12, "window": (12, 13, 14), "quota": (1, 1, 1)},)}
    original = runner._save
    def interrupt(attempt, name, value):
        if name == "proposal-12-validation_routine.json":
            raise Deadline("post-training deadline")
        return original(attempt, name, value)
    monkeypatch.setattr(runner, "_save", interrupt)
    with pytest.raises(Deadline, match="post-training"):
        with _attempt(tmp_path) as attempt:
            execute_pipeline(attempt, pools_fn=lambda f: pools[f], assemble_fn=lambda _: records, rank_fn=lambda _: ranking,
                             config=data.SelectionConfig((12,13,14),(1,1,1),1), counts={"val_routine":1,"val_mixed":1,"test_routine":1,"test_mixed":1})
    out=tmp_path/"out"; training=json.loads((out/"proposal-12-training.json").read_text()); summary=json.loads((out/"summary.json").read_text())
    assert training["result"]["profile"] and training["result"]["states"] and summary["outcome"] == "DEADLINE_FAILED"
    assert summary["proposals"]["12"]["stages"] == {"training":"COMPLETE", "validation_routine":"FAILED",
                                  "validation_mixed":"NOT_EVALUATED", "test_routine":"NOT_EVALUATED", "test_mixed":"NOT_EVALUATED"}
    assert json.loads((out/"attempt.json").read_text())["status"] == "FAILED" and len((tmp_path/"ledger.jsonl").read_text().splitlines()) == 1


@pytest.mark.parametrize("fault_name", ["manifest.json", "summary.json"])
def test_pipeline_write_fault_keeps_primary_error_charged_once(tmp_path, monkeypatch, fault_name):
    original = runner._save
    def fault(attempt, name, value):
        if name == fault_name:
            raise OSError("write fault " + name)
        return original(attempt, name, value)
    monkeypatch.setattr(runner, "_save", fault)
    with pytest.raises(ValueError, match="primary pipeline error") as raised:
        with _attempt(tmp_path) as attempt:
            execute_pipeline(attempt, pools_fn=lambda _: (_ for _ in ()).throw(ValueError("primary pipeline error")))
    assert isinstance(raised.value.__cause__, OSError)
    assert len((tmp_path/"ledger.jsonl").read_text().splitlines()) == 1 and not (tmp_path/"lock").exists()


def test_rejection_artifact_write_failure_charges_once_and_cleans(tmp_path, monkeypatch):
    out=tmp_path/"out"; out.mkdir()
    monkeypatch.setattr(runner, "write_json", lambda *_: (_ for _ in ()).throw(OSError("reject write fault")))
    with pytest.raises(OSError, match="reject write fault"):
        with _attempt(tmp_path): pass
    assert len((tmp_path/"ledger.jsonl").read_text().splitlines()) == 1 and not (tmp_path/"lock").exists()


def test_cli_prints_exact_compact_success_and_no_success_on_failure(tmp_path, monkeypatch, capsys):
    class FakeAttempt:
        manifest_sha256 = "abc"
        def __init__(self, *_): pass
        def __enter__(self): return self
        def __exit__(self, *_): return False
    monkeypatch.setattr(runner, "Attempt", FakeAttempt)
    monkeypatch.setattr(runner, "execute_pipeline", lambda _: {"outcome":"FIRST_FULL_DATASET_PASS"})
    runner.main(["--output", str(tmp_path/"out")])
    assert json.loads(capsys.readouterr().out) == {"outcome":"FIRST_FULL_DATASET_PASS","output":str(tmp_path/"out"),"manifest_sha256":"abc"}
    monkeypatch.setattr(runner, "execute_pipeline", lambda _: (_ for _ in ()).throw(RunnerError("nope")))
    with pytest.raises(RunnerError): runner.main(["--output", str(tmp_path/"bad")])
    assert capsys.readouterr().out == ""


@pytest.mark.parametrize("fault_name,expected", [
    ("proposal-12-training.json", {"training":"FAILED", "validation_routine":"NOT_EVALUATED", "validation_mixed":"NOT_EVALUATED", "test_routine":"NOT_EVALUATED", "test_mixed":"NOT_EVALUATED"}),
    ("result.json", {"training":"COMPLETE", "validation_routine":"COMPLETE", "validation_mixed":"COMPLETE", "test_routine":"COMPLETE", "test_mixed":"COMPLETE"}),
])
def test_real_pipeline_stage_or_result_write_fault_truthful_state(tmp_path, monkeypatch, fault_name, expected):
    records = _eight_records(); pools = {f: data.PoolResult(f, tuple(r["canonical"] for r in records if r["family"] == f), 0, 0, 0, 0) for f in data.FAMILIES}
    ranking = {"retained": ({"window_start":12,"window":(12,13,14),"quota":(1,1,1)},)}; original = runner._save
    def fault(attempt, name, value):
        if name == fault_name: raise OSError("primary write " + name)
        return original(attempt, name, value)
    monkeypatch.setattr(runner, "_save", fault)
    with pytest.raises(OSError, match="primary write"):
        with _attempt(tmp_path) as attempt:
            execute_pipeline(attempt, pools_fn=lambda f:pools[f], assemble_fn=lambda _:records, rank_fn=lambda _:ranking,
                             config=data.SelectionConfig((12,13,14),(1,1,1),1), counts={"val_routine":1,"val_mixed":1,"test_routine":1,"test_mixed":1})
    out=tmp_path/"out"; summary=json.loads((out/"summary.json").read_text()); manifest=json.loads((out/"manifest.json").read_text())
    assert summary["proposals"]["12"]["stages"] == expected and summary["outcome"] == "TECHNICAL_FAILED" and not (out/fault_name).exists()
    assert json.loads((out/"attempt.json").read_text())["status"] == "FAILED" and len((tmp_path/"ledger.jsonl").read_text().splitlines()) == 1 and not (tmp_path/"lock").exists()
    for name,digest in manifest["outputs"].items(): assert __import__("hashlib").sha256((out/name).read_bytes()).hexdigest()==digest


def test_03b_real_valroutine_three_is_scientific_failure(tmp_path):
    records=_eight_records(); pools={f:data.PoolResult(f,tuple(r["canonical"] for r in records if r["family"]==f),0,0,0,0) for f in data.FAMILIES}
    ranking={"retained":({"window_start":12,"window":(12,13,14),"quota":(1,1,1)},)}
    with _attempt(tmp_path) as attempt:
        out=execute_pipeline(attempt,pools_fn=lambda f:pools[f],assemble_fn=lambda _:records,rank_fn=lambda _:ranking,
          config=data.SelectionConfig((12,13,14),(1,1,1),1),counts={"val_routine":3,"val_mixed":1,"test_routine":1,"test_mixed":1})
    assert out["outcome"]=="DATASET_CONSTRUCTION_FAILED"
    stages=json.loads((tmp_path/"out"/"summary.json").read_text())["proposals"]["12"]["stages"]
    assert stages == dict(zip(runner.STAGE_ORDER, (
        "COMPLETE", "SCIENTIFIC_HELDOUT_SUPPLY_FAILED", "NOT_EVALUATED", "NOT_EVALUATED", "NOT_EVALUATED")))
    held = json.loads((tmp_path/"out"/"proposal-12-validation_routine.json").read_text())["results"]
    assert [(item["family"], item["result"]["outcome"]) for item in held] == [
        ("IIIIIIII", "SCIENTIFIC_HELDOUT_SUPPLY_FAILED"), ("LLLLLLLL", "NOT_EVALUATED")]
    assert held[0]["result"]["evidence"] and held[0]["result"]["selected"]


def test_03b_first_window_training_failure_then_real_second_pass(tmp_path):
    records=_eight_records(); pools={f:data.PoolResult(f,tuple(r["canonical"] for r in records if r["family"]==f),0,0,0,0) for f in data.FAMILIES}
    for record in records:
        record["shortlists"][15]={"retained":()}; record["shortlists"][16]={"retained":()}
    ranking={"retained":({"window_start":14,"window":(14,15,16),"quota":(1,1,1)},{"window_start":12,"window":(12,13,14),"quota":(1,1,1)})}
    with _attempt(tmp_path) as attempt:
        out=execute_pipeline(attempt,pools_fn=lambda f:pools[f],assemble_fn=lambda _:records,rank_fn=lambda _:ranking,
          config=data.SelectionConfig((12,13,14),(1,1,1),1),counts={"val_routine":1,"val_mixed":1,"test_routine":1,"test_mixed":1})
    states=json.loads((tmp_path/"out"/"summary.json").read_text())["proposals"]
    assert out["outcome"] == "FIRST_FULL_DATASET_PASS"
    assert states["14"]["stages"] == dict(zip(runner.STAGE_ORDER, (
        "SCIENTIFIC_TRAINING_SUPPLY_FAILED", *("NOT_EVALUATED",) * 4)))
    assert states["12"]["stages"] == dict.fromkeys(runner.STAGE_ORDER, "COMPLETE")
    assert set(states) == {"14", "12"}
    assert set(states["12"]["artifacts"]) == set(runner.STAGE_ORDER)
    assert not any(value == "NOT_EVALUATED" for value in states["12"]["stages"].values())


@pytest.mark.parametrize("after_training", [False, True])
def test_03c_real_first_failure_second_interrupted_third_unattempted(tmp_path, monkeypatch, after_training):
    records = _eight_records()
    for record in records:
        for length in (15, 16, 17, 18):
            record["shortlists"][length] = {"retained": ()}
    pools = {f: data.PoolResult(f, tuple(r["canonical"] for r in records if r["family"] == f), 0, 0, 0, 0)
             for f in data.FAMILIES}
    ranking = {"retained": tuple({"window_start": start, "window": tuple(range(start, start+3)), "quota": (1, 1, 1)}
                                 for start in (14, 12, 16))}
    original = data.run_ranked_proposals
    def interrupted(*args, on_stage=None, **kwargs):
        def callback(name, payload):
            target = payload["proposal"] == 12 and name == "training"
            if target and not after_training:
                raise Deadline("second before training callback")
            on_stage(name, payload)
            if target:
                raise Deadline("second after training callback")
        return original(*args, on_stage=callback, **kwargs)
    monkeypatch.setattr(data, "run_ranked_proposals", interrupted)
    with pytest.raises(Deadline, match="second"):
        with _attempt(tmp_path) as attempt:
            execute_pipeline(attempt, pools_fn=lambda f: pools[f], assemble_fn=lambda _: records,
                             rank_fn=lambda _: ranking, config=data.SelectionConfig((12,13,14),(1,1,1),1),
                             counts={"val_routine":1,"val_mixed":1,"test_routine":1,"test_mixed":1})
    output = tmp_path / "out"
    summary = json.loads((output/"summary.json").read_text())
    states = summary["proposals"]
    assert states["14"]["stages"] == dict(zip(runner.STAGE_ORDER, (
        "SCIENTIFIC_TRAINING_SUPPLY_FAILED", *("NOT_EVALUATED",) * 4)))
    assert states["12"]["stages"] == dict(zip(runner.STAGE_ORDER,
        ("COMPLETE", "NOT_COMPLETED_UNKNOWN", *("NOT_EVALUATED",)*3) if after_training else
        ("NOT_COMPLETED_UNKNOWN", *("NOT_EVALUATED",)*4)))
    assert states["16"] == {"stages": dict.fromkeys(runner.STAGE_ORDER, "NOT_EVALUATED"), "artifacts": {}}
    assert set(states["12"]["artifacts"]) == ({"training"} if after_training else set())
    assert summary["outcome"] == "DEADLINE_FAILED"
    prior = json.loads((output/"proposal-14-training.json").read_text())["result"]
    assert prior["outcome"] == "SCIENTIFIC_TRAINING_SUPPLY_FAILED" and prior["family"] == "IIIIIIII"
    for proposal in states.values():
        for artifact in proposal["artifacts"].values():
            assert __import__("hashlib").sha256((output/artifact["file"]).read_bytes()).hexdigest() == artifact["sha256"]
    assert json.loads((output/"attempt.json").read_text())["status"] == "FAILED"
    assert len((tmp_path/"ledger.jsonl").read_text().splitlines()) == 1
    assert not (tmp_path/"lock").exists()


def test_03b_real_training_callback_then_deadline_before_next_callback(tmp_path, monkeypatch):
    records=_eight_records(); pools={f:data.PoolResult(f,tuple(r["canonical"] for r in records if r["family"]==f),0,0,0,0) for f in data.FAMILIES}; ranking={"retained":({"window_start":12,"window":(12,13,14),"quota":(1,1,1)},)}
    original=data.run_ranked_proposals
    def wrapped(*args, on_stage=None, **kwargs):
        def callback(name,payload):
            on_stage(name,payload)
            if name=="training": raise Deadline("between callbacks")
        return original(*args,on_stage=callback,**kwargs)
    monkeypatch.setattr(runner.data,"run_ranked_proposals",wrapped)
    with pytest.raises(Deadline,match="between callbacks"):
        with _attempt(tmp_path) as attempt: execute_pipeline(attempt,pools_fn=lambda f:pools[f],assemble_fn=lambda _:records,rank_fn=lambda _:ranking,config=data.SelectionConfig((12,13,14),(1,1,1),1),counts={"val_routine":1,"val_mixed":1,"test_routine":1,"test_mixed":1})
    out=tmp_path/"out"; summary=json.loads((out/"summary.json").read_text()); item=summary["proposals"]["12"]
    assert item["stages"]=={"training":"COMPLETE","validation_routine":"NOT_COMPLETED_UNKNOWN","validation_mixed":"NOT_EVALUATED","test_routine":"NOT_EVALUATED","test_mixed":"NOT_EVALUATED"}
    assert __import__("hashlib").sha256((out/"proposal-12-training.json").read_bytes()).hexdigest()==item["artifacts"]["training"]["sha256"]


def test_03b_proposal_status_helper_unattempted_and_unknown_payload():
    statuses=runner.ProposalStatuses((12,14)); final=statuses.finalize(False)
    assert all(value=="NOT_EVALUATED" for value in final["14"]["stages"].values())
    with pytest.raises(RunnerError,match="unknown"):
        statuses.observe(12,"training",{"result":{"outcome":"BOGUS"}},"x", "0"*64)


def test_03b_manifest_has_exact_sources_reviews_specs_and_fixture_hashes(tmp_path):
    records=_eight_records(); pools={f:data.PoolResult(f,tuple(r["canonical"] for r in records if r["family"]==f),0,0,0,0) for f in data.FAMILIES}; ranking={"retained":({"window_start":12,"window":(12,13,14),"quota":(1,1,1)},)}
    with _attempt(tmp_path) as attempt: execute_pipeline(attempt,pools_fn=lambda f:pools[f],assemble_fn=lambda _:records,rank_fn=lambda _:ranking,config=data.SelectionConfig((12,13,14),(1,1,1),1),counts={"val_routine":1,"val_mixed":1,"test_routine":1,"test_mixed":1})
    manifest=json.loads((tmp_path/"out"/"manifest.json").read_text()); root=Path(__file__).resolve().parents[1]
    fixed={"schrodinger/productive_diversity_v3_runner.py","schrodinger/productive_diversity_v3_data.py","schrodinger/route_feasibility.py","tests/test_productive_diversity_v3_runner.py","tests/test_productive_diversity_v3_data.py","productive_diversity_v3_plan.md","agent_execution_protocol.md"}
    docs={str(p.relative_to(root)) for directory in (root/"execution/next_level_v3/specs",root/"execution/next_level_v3/reviews") for p in directory.glob("*.md")}
    fixtures={"execution/next_level_v3/fixtures/recovery_b_i8.json","execution/next_level_v3/fixtures/recovery_b_l8.json","execution/next_level_v3/fixtures/recovery_b_mixed.json"}
    assert set(manifest["sources"]) == fixed|docs|fixtures
    for relative,digest in manifest["sources"].items(): assert __import__("hashlib").sha256((root/relative).read_bytes()).hexdigest()==digest
