import torch
import pytest
import json
import time

from schrodinger.data import training_batch
from schrodinger.model import TinyClassifier, paired_models
from schrodinger.experiment import append_ledger, budget_guard, ledger_total, save_evaluation_data
from schrodinger.data import evaluation_sets
import schrodinger.experiment as experiment


def test_paired_initialization_and_dt_zero_identity_at_length_15():
    baseline, experimental = paired_models(22)
    for name, value in baseline.state_dict().items():
        assert torch.equal(value, experimental.state_dict()[name])
    tokens = torch.from_numpy(training_batch(22, 1).tokens)
    tokens = torch.cat([tokens[:, :5], tokens[:, 5:], torch.full((64, 4), 16, dtype=torch.long)], dim=1)
    torch.testing.assert_close(baseline(tokens), experimental(tokens, dt_override=0.0), atol=2e-6, rtol=2e-5)
    assert sum(parameter.numel() for parameter in experimental.parameters()) - sum(parameter.numel() for parameter in baseline.parameters()) == 8


def test_checkpoint_state_reload_logits_equal():
    _, model = paired_models(33)
    tokens = torch.from_numpy(training_batch(33, 2).tokens)
    reference = model(tokens)
    restored = TinyClassifier("schrodinger")
    restored.load_state_dict(model.state_dict())
    torch.testing.assert_close(restored(tokens), reference, atol=1e-6, rtol=0)


def test_standard_sinusoidal_position_reference():
    position = TinyClassifier.positional(15, torch.device("cpu"), torch.float32)
    assert torch.allclose(position[0, 0::2], torch.zeros(16))
    expected = torch.sin(torch.tensor(1.0) * torch.exp(torch.arange(0, 32, 2) * (-torch.log(torch.tensor(10000.0)) / 32)))
    torch.testing.assert_close(position[1, 0::2], expected)


def test_local_ledger_and_tiny_budget_guard(tmp_path):
    ledger = tmp_path / "ledger.jsonl"
    append_ledger("initial", 1.0, path=ledger)
    append_ledger("failure", 0.2, status="failed", path=ledger, error="synthetic")
    assert ledger_total(ledger) == pytest.approx(1.2)
    with pytest.raises(RuntimeError):
        budget_guard(0.0, path=ledger, cap=0.1)


def test_multi_step_guard_interrupts_after_step_zero_and_preserves_jsonl(tmp_path, monkeypatch):
    _, model = paired_models(11)
    calls = {"count": 0}
    def forced_guard(*args, **kwargs):
        calls["count"] += 1
        if calls["count"] >= 2: raise RuntimeError("tiny cap")
    monkeypatch.setattr(experiment, "budget_guard", forced_guard)
    with pytest.raises(RuntimeError, match="tiny cap"):
        experiment._train_steps(model, 11, 3, tmp_path, eval_count=8, command_started=1.0)
    rows = [json.loads(line) for line in (tmp_path / "training.jsonl").read_text().splitlines()]
    assert rows[0]["step"] == 0


def test_pair_evaluate_uses_latest_existing_checkpoint_and_step_zero(tmp_path):
    first, second = tmp_path / "first", tmp_path / "second"; first.mkdir(); second.mkdir()
    initial = None
    for directory, mode in ((first, "softmax"), (second, "schrodinger")):
        model = TinyClassifier(mode)
        identity = experiment.model_identity(model) if initial is None else initial
        initial = identity
        records = [{"step": step, "cumulative_training_seconds": seconds, "batch_digest": "x" if step == 100 else ""} for step, seconds in ((0, 0.0), (100, 1.0))]
        digest = __import__("hashlib").sha256("x".encode()).hexdigest()
        for step in (0, 100): torch.save({"model": model.state_dict(), "mode": mode, "seed": 11, "config": experiment.config(), "source_hashes": experiment.source_hashes(), "initial_identity": identity, "stream_digest": digest}, directory / f"checkpoint-{step}.pt")
        (directory / "training.jsonl").write_text("\n".join(json.dumps(item) for item in records) + "\n")
        save_evaluation_data(evaluation_sets(1729, 8), directory / "evaluation.npz", kind="TEST")
    experiment.pair_evaluate(first, second, tmp_path / "pair.json")
    selected = json.loads((tmp_path / "pair.json").read_text())["runs"]
    assert all(item["step"] == 100 for item in selected)
    for directory in (first, second):
        (directory / "checkpoint-100.pt").unlink()
    with pytest.raises(ValueError):
        experiment.pair_evaluate(first, second, tmp_path / "pair-zero.json")


def test_completed_pair_rejects_final_step_and_stream_mismatch(tmp_path):
    first, second = tmp_path / "a", tmp_path / "b"; first.mkdir(); second.mkdir()
    identity = experiment.model_identity(TinyClassifier("softmax"))
    for directory, mode, digest in ((first, "softmax", "a"), (second, "schrodinger", "b")):
        model = TinyClassifier(mode); raw = __import__("hashlib").sha256(digest.encode()).hexdigest()
        torch.save({"model": model.state_dict(), "mode": mode, "seed": 11, "config": experiment.config(), "source_hashes": experiment.source_hashes(), "initial_identity": identity, "stream_digest": raw}, directory / "checkpoint-1.pt")
        (directory / "training.jsonl").write_text(json.dumps({"step": 1, "cumulative_training_seconds": 1.0, "batch_digest": digest}) + "\n")
        save_evaluation_data(evaluation_sets(1729, 8), directory / "evaluation.npz", kind="TEST")
    with pytest.raises(ValueError, match="stream digests differ"):
        experiment.pair_evaluate(first, second, tmp_path / "pair.json")


def test_completed_pair_rejects_unequal_final_steps(tmp_path):
    first, second = tmp_path / "a", tmp_path / "b"; first.mkdir(); second.mkdir()
    identity = experiment.model_identity(TinyClassifier("softmax"))
    for directory, mode, step in ((first, "softmax", 1), (second, "schrodinger", 2)):
        model = TinyClassifier(mode); raw = __import__("hashlib").sha256("x".encode()).hexdigest()
        torch.save({"model": model.state_dict(), "mode": mode, "seed": 11, "config": experiment.config(), "source_hashes": experiment.source_hashes(), "initial_identity": identity, "stream_digest": raw}, directory / f"checkpoint-{step}.pt")
        (directory / "training.jsonl").write_text(json.dumps({"step": step, "cumulative_training_seconds": 1.0, "batch_digest": "x"}) + "\n")
        save_evaluation_data(evaluation_sets(1729, 8), directory / "evaluation.npz", kind="TEST")
    with pytest.raises(ValueError, match="paired completed final steps differ"):
        experiment.pair_evaluate(first, second, tmp_path / "pair.json")


def test_pair_evaluate_rejects_missing_or_mismatched_stored_data(tmp_path):
    first, second = tmp_path / "first", tmp_path / "second"; first.mkdir(); second.mkdir()
    for directory in (first, second):
        model = TinyClassifier("softmax"); torch.save({"model": model.state_dict(), "mode": "softmax"}, directory / "checkpoint-0.pt")
        (directory / "training.jsonl").write_text(json.dumps({"step": 0, "cumulative_training_seconds": 0.0}) + "\n")
    with pytest.raises(ValueError, match="completed stream"): experiment.pair_evaluate(first, second, tmp_path / "x.json")
    save_evaluation_data(evaluation_sets(1729, 8), first / "evaluation.npz", kind="TEST")
    save_evaluation_data(evaluation_sets(2718, 8), second / "evaluation.npz", kind="TEST")
    with pytest.raises(ValueError): experiment.pair_evaluate(first, second, tmp_path / "x.json")


def test_evaluate_rejects_nonfinite_logits(monkeypatch):
    _, model = paired_models(11)
    monkeypatch.setattr(model, "forward", lambda tokens, **kwargs: torch.full((len(tokens), 2), float("nan")))
    with pytest.raises(FloatingPointError, match="logits"):
        experiment.evaluate(model, {"x": evaluation_sets(1729, 8)["validation_seen_d4"]})


def test_optimizer_nonfinite_parameter_aborts(tmp_path, monkeypatch):
    _, model = paired_models(11)
    original = torch.optim.AdamW.step
    def bad_step(self, *args, **kwargs):
        result = original(self, *args, **kwargs)
        next(iter(self.param_groups[0]["params"])).data.fill_(float("nan")); return result
    monkeypatch.setattr(torch.optim.AdamW, "step", bad_step)
    with pytest.raises(FloatingPointError, match="parameter"):
        experiment._train_steps(model, 11, 1, tmp_path, eval_count=8)


def test_initial_identity_is_stable_across_training_checkpoint(tmp_path):
    _, model = paired_models(11); identity = experiment.model_identity(model)
    experiment._train_steps(model, 11, 1, tmp_path, eval_count=8, initial_identity=identity)
    zero = torch.load(tmp_path / "checkpoint-0.pt", weights_only=False)
    trained = torch.load(tmp_path / "checkpoint-1.pt", weights_only=False)
    assert zero["initial_identity"] == trained["initial_identity"] == identity
    assert trained["current_state_identity"] != identity


def test_budget_reserve_boundary(tmp_path):
    ledger = tmp_path / "ledger.jsonl"; append_ledger("near", 99.0, path=ledger)
    with pytest.raises(RuntimeError): budget_guard(time.perf_counter(), path=ledger, cap=150.0, reserve=60.0)


def test_normal_invariants_are_distinct_from_dt_zero(monkeypatch):
    _, model = paired_models(11); batch = evaluation_sets(1729, 8)["validation_seen_d4"]
    values = iter([{"hermiticity": 0.0, "unitarity": 0.1, "row": 0.2}, {"hermiticity": 0.0, "unitarity": 0.0, "row": 0.0}])
    monkeypatch.setattr(model, "invariant_maxima", lambda: next(values))
    normal = experiment.evaluate(model, {"x": batch})["x"]["invariants"]
    dt_zero = experiment.evaluate(model, {"x": batch}, dt_zero=True)["x"]["invariants"]
    assert normal["unitarity"] == 0.1 and normal["row"] == 0.2
    assert dt_zero["unitarity"] == 0.0


@pytest.mark.parametrize("field,value,message", [("seed", 12, "same seed"), ("config", {"bad": 1}, "config mismatch"), ("source_hashes", {"bad": 1}, "source_hashes mismatch"), ("initial_identity", {"shared_initial_tensor_digest": "bad"}, "initial identity"), ("mode", "softmax", "opposite modes")])
def test_pair_identity_mismatches_reject(tmp_path, field, value, message):
    first, second = tmp_path / "first", tmp_path / "second"; first.mkdir(); second.mkdir()
    base = {"seed": 11, "config": experiment.config(), "source_hashes": experiment.source_hashes(), "initial_identity": experiment.model_identity(TinyClassifier("softmax"))}
    digest = __import__("hashlib").sha256("x".encode()).hexdigest()
    for directory, mode in ((first, "softmax"), (second, "schrodinger")):
        model = TinyClassifier(mode); metadata = {**base, "mode": mode, "model": model.state_dict(), "stream_digest": digest}; torch.save(metadata, directory / "checkpoint-1.pt"); (directory / "training.jsonl").write_text(json.dumps({"step": 1, "cumulative_training_seconds": 1.0, "batch_digest": "x"}) + "\n"); save_evaluation_data(evaluation_sets(1729, 8), directory / "evaluation.npz", kind="TEST")
    experiment.pair_evaluate(first, second, tmp_path / "valid.json")
    saved = torch.load(second / "checkpoint-1.pt", weights_only=False); saved[field] = value; torch.save(saved, second / "checkpoint-1.pt")
    with pytest.raises(ValueError, match=message): experiment.pair_evaluate(first, second, tmp_path / "pair.json")


def test_saved_checkpoint_metrics_recompute_from_correct_counts(tmp_path):
    batch = evaluation_sets(1729, 8)["validation_seen_d4"]
    _, model = paired_models(11)
    metrics = experiment.evaluate(model, {"condition": batch})["condition"]
    assert metrics["xor"] == pytest.approx(metrics["xor_correct"] / metrics["xor_count"])
    assert metrics["copy"] == pytest.approx(metrics["copy_correct"] / metrics["copy_count"])
    run = tmp_path / "run"; run.mkdir(); save_evaluation_data({"condition": batch}, run / "evaluation.npz", kind="TEST")
    torch.save({"model": model.state_dict(), "mode": "schrodinger", "seed": 11, "config": experiment.config(), "source_hashes": experiment.source_hashes(), "initial_identity": experiment.model_identity(model)}, run / "checkpoint-0.pt")
    loaded = TinyClassifier("schrodinger"); loaded.load_state_dict(torch.load(run / "checkpoint-0.pt", weights_only=False)["model"])
    assert experiment.evaluate(loaded, experiment.load_evaluation_data(run / "evaluation.npz"), dt_zero=True)["condition"]["xor_count"] == metrics["xor_count"]
