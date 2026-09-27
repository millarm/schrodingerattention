import json
import signal
import time

import pytest
import torch

import schrodinger.checkpoint_diagnostic as diagnostic
from schrodinger.checkpoint_diagnostic import Attempt, DiagnosticTimeout, ROOT, _assert_retained_metrics, _downstream_summary, _tv_checks, _validate_inputs, _post_projection_summary, _probability_checks, _record_rejection, _summary, _manifest, direct, quantiles, rms_change, total_variation, trace_batch, trace_model
from schrodinger.data import evaluation_sets, training_batch
from schrodinger.model import TinyClassifier


def _model() -> TinyClassifier:
    torch.manual_seed(17)
    model = TinyClassifier("schrodinger").eval()
    # Make the nondegenerate direct/propagated effect clear while staying local
    # to the fixture, not any retained checkpoint.
    for layer in model.layers:
        layer.attention.raw_dt.data.fill_(0.2)
        layer.attention.raw_gamma.data.fill_(0.3)
    return model


def test_tv_quantiles_and_rms_known_values() -> None:
    a = torch.tensor([[.2, .8]]); b = torch.tensor([[.5, .5]])
    assert total_variation(a, b).item() == pytest.approx(.3)
    assert total_variation(a, a).item() == 0
    assert quantiles(torch.tensor([0., .1]))["p95"] >= .09
    change = rms_change(torch.tensor([[1., -1.]]), torch.zeros(1, 2))
    assert change["absolute"].item() == pytest.approx(1.)
    assert torch.isfinite(change["relative"]).all()


def test_direct_dt_zero_is_softmax_and_changed_time_is_detectable() -> None:
    torch.manual_seed(4)
    scores = torch.randn(1, 1, 4, 4); values = torch.randn(1, 1, 4, 3); phase = torch.randn_like(scores)
    zero = direct(scores, values, phase, torch.tensor(0.))
    torch.testing.assert_close(zero["attention"], zero["softmax"], atol=2e-6, rtol=2e-5)
    torch.testing.assert_close(zero["evolved"], zero["soft_value"], atol=2e-6, rtol=2e-5)
    assert zero["tv"].max() < 2e-6
    changed = direct(scores, values, phase, torch.tensor(.25))
    assert changed["tv"].max() > 1e-5
    assert torch.all(changed["attention"].sum(-1).sub(1).abs() < 2e-4)


def test_manual_normal_and_dt0_trace_reproduce_api_and_separate_paths() -> None:
    model = _model(); tokens = torch.from_numpy(training_batch(11, 3).tokens)
    normal, dt0 = trace_model(model, tokens), trace_model(model, tokens, dt_zero=True)
    torch.testing.assert_close(normal["logits"], model(tokens), atol=2e-6, rtol=2e-5)
    torch.testing.assert_close(dt0["logits"], model(tokens, dt_override=0.), atol=2e-6, rtol=2e-5)
    # Layer 1 begins from identical input; layer 2 proves full-path propagation.
    torch.testing.assert_close(normal["layers"][0]["normalized_input"], dt0["layers"][0]["normalized_input"], atol=2e-6, rtol=2e-5)
    assert (normal["layers"][1]["normalized_input"] - dt0["layers"][1]["normalized_input"]).abs().max() > 1e-7
    assert normal["layers"][0]["local_tv"].min() >= 0
    assert normal["layers"][0]["local_tv"].max() <= 1.0002
    assert torch.isfinite(normal["layers"][0]["phase_dispersion"]).all()


def test_lock_contention_uses_different_output_and_failure_cleanup(tmp_path) -> None:
    first, second, lock, ledger = tmp_path / "first", tmp_path / "second", tmp_path / "lock", tmp_path / "ledger.jsonl"
    with Attempt(first, lock, ledger=ledger):
        with pytest.raises(FileExistsError, match="File exists"):
            with Attempt(second, lock, ledger=ledger):
                pass
        assert not second.exists()
    assert not lock.exists()
    assert json.loads((first / "attempt.json").read_text())["status"] == "success"
    with pytest.raises(RuntimeError):
        with Attempt(tmp_path / "failed", lock, ledger=ledger):
            raise RuntimeError("intentional")
    assert not lock.exists()
    assert json.loads((tmp_path / "failed" / "attempt.json").read_text())["status"] == "failed"
    assert len(ledger.read_text().splitlines()) == 3


def test_exact_provenance_and_rejected_preflight_are_separate(tmp_path, monkeypatch) -> None:
    output, lock, ledger, rejected = tmp_path / "done", tmp_path / "lock", tmp_path / "ledger", tmp_path / "rejected"
    argv = ["/python", "-m", "schrodinger.checkpoint_diagnostic", "--output", str(output), "--lock", str(lock)]
    with Attempt(output, lock, argv=argv, ledger=ledger): pass
    record = json.loads((output / "attempt.json").read_text())
    assert record["argv"] == argv and record["lock"] == str(lock) and record["executable"]
    monkeypatch.setattr(diagnostic, "REJECTIONS", rejected)
    _record_rejection("output already exists", output, lock, argv, ledger=ledger)
    assert json.loads(next(rejected.iterdir()).read_text())["status"] == "rejected"


def test_real_sigalrm_interrupts_post_processing_and_restores_handler(tmp_path) -> None:
    previous = signal.getsignal(signal.SIGALRM)
    with pytest.raises(DiagnosticTimeout, match="interrupting"):
        with Attempt(tmp_path / "slow", tmp_path / "lock", deadline_seconds=.02, ledger=tmp_path / "ledger"):
            time.sleep(.08)  # actual expensive-stage stand-in; signal interrupts it.
    assert signal.getsignal(signal.SIGALRM) == previous
    assert json.loads((tmp_path / "slow" / "attempt.json").read_text())["status"] == "failed"


def test_actual_o_excl_race_records_charged_rejection_without_unlocking_owner(tmp_path, monkeypatch) -> None:
    lock, ledger, rejected = tmp_path / "owner.lock", tmp_path / "ledger", tmp_path / "rejected"
    monkeypatch.setattr(diagnostic, "REJECTIONS", rejected)
    owner = Attempt(tmp_path / "owner", lock, ledger=ledger)
    with owner:
        with pytest.raises(FileExistsError):
            with Attempt(tmp_path / "contender", lock, argv=["exact", "argv"], ledger=ledger): pass
        assert lock.exists() and not (tmp_path / "contender").exists()
    records=[json.loads(path.read_text()) for path in rejected.iterdir()]
    assert records[0]["argv"] == ["exact", "argv"] and records[0]["charged_seconds"] >= 2.0


def test_output_mkdir_race_preserves_other_owners_sentinel_bytes(tmp_path, monkeypatch) -> None:
    output, lock, ledger, rejected = tmp_path / "output", tmp_path / "lock", tmp_path / "ledger", tmp_path / "rejected"
    monkeypatch.setattr(diagnostic, "REJECTIONS", rejected)
    original = type(output).mkdir
    def lose_race(self, *args, **kwargs):
        if self == output:
            original(self, *args, **kwargs)
            (self / "attempt.json").write_bytes(b"other-owner-sentinel")
            raise FileExistsError("injected output mkdir race")
        return original(self, *args, **kwargs)
    monkeypatch.setattr(type(output), "mkdir", lose_race)
    with pytest.raises(FileExistsError, match="injected output mkdir race"):
        with Attempt(output, lock, ledger=ledger): pass
    assert (output / "attempt.json").read_bytes() == b"other-owner-sentinel"
    assert not lock.exists()
    record=json.loads(next(rejected.iterdir()).read_text())
    assert record["status"] == "rejected" and record["charged_seconds"] >= 2.0


def test_enter_record_write_failure_still_cleans_owned_resources(tmp_path, monkeypatch) -> None:
    output, lock, ledger = tmp_path / "owned", tmp_path / "lock", tmp_path / "ledger"
    original = type(output).write_text
    def fail(self, *args, **kwargs):
        if self.name == "attempt.json": raise OSError("injected enter record failure")
        return original(self, *args, **kwargs)
    monkeypatch.setattr(type(output), "write_text", fail)
    with pytest.raises(OSError, match="injected enter record failure"):
        with Attempt(output, lock, deadline_seconds=0., ledger=ledger): pass
    assert not lock.exists()
    assert json.loads(ledger.read_text())["status"] == "failed"


def test_attempt_enter_mkdir_failure_releases_lock(tmp_path, monkeypatch) -> None:
    lock = tmp_path / "lock"; output = tmp_path / "out"
    original = type(output).mkdir
    def fail(self, *args, **kwargs):
        if self == output: raise OSError("injected mkdir failure")
        return original(self, *args, **kwargs)
    monkeypatch.setattr(type(output), "mkdir", fail)
    with pytest.raises(OSError, match="injected"):
        with Attempt(output, lock, ledger=tmp_path / "ledger"):
            pass
    assert not lock.exists()


def test_guard_includes_prior_ledger_charge_and_preserves_failure(tmp_path) -> None:
    ledger = tmp_path / "ledger.jsonl"; ledger.write_text(json.dumps({"charged_seconds": 870.0}) + "\n")
    lock, output = tmp_path / "lock", tmp_path / "capped"
    with pytest.raises(RuntimeError, match="deadline exhausted|cap reserve"):
        with Attempt(output, lock, ledger=ledger) as attempt:
            attempt.guard()
    assert json.loads((output / "attempt.json").read_text())["status"] == "failed"
    assert not lock.exists()
    assert len(ledger.read_text().splitlines()) == 2


def test_post_processing_guard_can_abort_after_trace_stage(tmp_path) -> None:
    lock, output = tmp_path / "lock", tmp_path / "post-cap"
    # Simulates a completed trace consuming the cap before serialization/plot.
    with pytest.raises(RuntimeError, match="deadline exhausted|cap reserve"):
        with Attempt(output, lock, command_started=__import__("time").perf_counter() - 875, ledger=tmp_path / "ledger") as attempt:
            _ = [0] * 100  # bounded stand-in for conversion/summary work
            attempt.guard()
    assert json.loads((output / "attempt.json").read_text())["status"] == "failed"


def test_lock_is_released_if_attempt_log_write_fails(tmp_path, monkeypatch) -> None:
    lock, output, ledger = tmp_path / "lock", tmp_path / "write-fail", tmp_path / "ledger"
    original = type(output).write_text
    def fail(self, *args, **kwargs):
        if self.name == "attempt.json": raise OSError("injected log failure")
        return original(self, *args, **kwargs)
    monkeypatch.setattr(type(output), "write_text", fail)
    with pytest.raises(OSError, match="injected log failure"):
        with Attempt(output, lock, ledger=ledger):
            pass
    assert not lock.exists()
    failed = json.loads(ledger.read_text())
    assert failed["status"] == "failed" and "required attempt record" in failed["error"]


def test_selected_batch_trace_records_rows_examples_and_correct_counts() -> None:
    model = _model()
    batch = evaluation_sets(1729, 8)["validation_seen_d4"]
    rows, examples, numerical = trace_batch(11, "validation_seen_d4", batch, model)
    assert len(examples["seed"]) == len(batch.labels)
    assert set(examples["operation"]) == {1, 2}
    assert set(rows["layer"]) == {0, 1}
    assert set(rows["head"]) == {-1, 0, 1}
    assert all(0 <= value <= 1.0002 for value in rows["local_tv"] if value == value)
    correct = sum(examples["normal_correct"])
    assert correct == sum(int(a == b) for a, b in zip(examples["normal_prediction"], examples["label"], strict=True))
    assert numerical["max_row_error"] < 2e-3
    assert all(torch.isfinite(torch.tensor(value, dtype=torch.float32)).all() for key, value in rows.items() if key != "condition")
    direct_cells, post_cells, downstream = _summary(rows), _post_projection_summary(rows), _downstream_summary(examples)
    assert {"local_value_abs_mean", "dt_h_operator_p95", "phase_dispersion_max"} <= set(direct_cells[0])
    assert {"local_projected_abs_mean", "propagated_hidden_abs_p95"} <= set(post_cells[0])
    assert {"normal_accuracy", "dt0_accuracy", "loss_benefit_mean", "disagreement_rate"} <= set(downstream[0])
    assert all("locally_small" in cell for cell in direct_cells)


def test_manifest_contains_all_review_gate_identities() -> None:
    manifest = _manifest()
    for path in ("tests/test_checkpoint_diagnostic.py", "execution/diagnostics/specs/01-review-corrections.md", "execution/diagnostics/specs/02-final-safety-corrections.md", "execution/diagnostics/specs/03-output-ownership-fix.md", "execution/diagnostics/reviews/00-plan.md", "execution/diagnostics/reviews/01-implementation.md", "execution/diagnostics/reviews/02-revision1.md", "execution/diagnostics/reviews/03-final-safety.md", "execution/diagnostics/handoffs/01-implementation.md", "execution/diagnostics/handoffs/02-revision1.md", "execution/diagnostics/handoffs/03-final-safety.md"):
        assert path in manifest


def test_final_json_metric_schema_recomputation_accepts_and_rejects_counts() -> None:
    examples = {"label": [0., 1., 0., 1.], "operation": [1., 1., 2., 2.], "normal_prediction": [0., 1., 1., 1.], "dt0_prediction": [0., 0., 0., 1.], "normal_loss": [.1, .2, .3, .4], "dt0_loss": [.2, .3, .4, .5]}
    normal = {"cross_entropy": .25, "xor_correct": 2, "xor_count": 2, "copy_correct": 1, "copy_count": 2}
    zero = {"cross_entropy": .35, "xor_correct": 1, "xor_count": 2, "copy_correct": 2, "copy_count": 2}
    _assert_retained_metrics(examples, normal, zero, "synthetic")
    bad = dict(normal); bad["xor_correct"] = 1
    with pytest.raises(AssertionError, match="correct/count"):
        _assert_retained_metrics(examples, bad, zero, "synthetic")


def test_retained_checkpoint_selected_batch_reproduces_forward_api() -> None:
    root = ROOT / "execution" / "results" / "measured" / "seed-11" / "schrodinger"
    saved = torch.load(root / "checkpoint-2000.pt", weights_only=False)
    model = TinyClassifier("schrodinger").eval(); model.load_state_dict(saved["model"])
    archive = __import__("numpy").load(root / "evaluation.npz")
    tokens = torch.from_numpy(archive["validation_seen_d4_tokens"][:64])
    trace = trace_model(model, tokens)
    torch.testing.assert_close(trace["logits"], model(tokens), atol=2e-6, rtol=2e-5)


def test_numeric_bounds_reject_nan_bad_tv_and_row_sum() -> None:
    with pytest.raises(FloatingPointError, match="nonfinite"):
        _probability_checks("fixture", torch.tensor([[float("nan"), 0.]]))
    with pytest.raises(FloatingPointError, match="TV"):
        _tv_checks(torch.tensor([1.1]))
    with pytest.raises(FloatingPointError, match="row-sum"):
        _probability_checks("fixture", torch.tensor([[.2, .2]]))


def test_retained_input_identity_and_malformed_batch_reject() -> None:
    root = ROOT / "execution" / "results" / "measured" / "seed-11" / "schrodinger"
    saved = torch.load(root / "checkpoint-2000.pt", weights_only=False); final = json.loads((root / "final.json").read_text())
    batches = __import__("schrodinger.experiment", fromlist=["load_evaluation_data"]).load_evaluation_data(root / "evaluation.npz")
    _validate_inputs(11, root, saved, final, batches)
    bad = dict(saved); bad["seed"] = 22
    with pytest.raises(ValueError, match="seed identity"):
        _validate_inputs(11, root, bad, final, batches)
    broken = dict(batches); item = broken["validation_seen_d4"]
    broken["validation_seen_d4"] = type(item)(item.tokens[:-1], item.labels[:-1], item.operations[:-1], item.pairs[:-1])
    with pytest.raises(ValueError, match="digest identity|shape/count"):
        _validate_inputs(11, root, saved, final, broken)
