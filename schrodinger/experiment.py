"""CLI for smoke, profiling, training, and fixed-condition evaluation."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import resource
import tempfile
import time
from pathlib import Path

import numpy as np
import torch
from torch import nn

from .data import Batch, COPY, XOR, evaluation_sets, training_batch
from .model import TinyClassifier, paired_models

ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "execution" / "config.json"
LEDGER_PATH = ROOT / "execution" / "compute_ledger.jsonl"


def configure_torch() -> None:
    torch.set_num_threads(2)
    torch.set_num_interop_threads(1)
    torch.use_deterministic_algorithms(True)


def config() -> dict:
    value = json.loads(CONFIG_PATH.read_text())
    value["config_sha256"] = hashlib.sha256(CONFIG_PATH.read_bytes()).hexdigest()
    value["torch"] = torch.__version__; value["numpy"] = np.__version__
    return value


def source_hashes() -> dict[str, str]:
    paths = [ROOT / "schrodinger" / name for name in ("attention.py", "data.py", "model.py", "experiment.py")]
    return {path.name: hashlib.sha256(path.read_bytes()).hexdigest() for path in paths}


def model_identity(model: TinyClassifier) -> dict[str, object]:
    shared = hashlib.sha256()
    for name, tensor in model.state_dict().items():
        if name.endswith("raw_dt") or name.endswith("raw_gamma"): continue
        shared.update(name.encode()); shared.update(tensor.detach().cpu().numpy().tobytes())
    total = sum(parameter.numel() for parameter in model.parameters())
    return {"shared_initial_tensor_digest": shared.hexdigest(), "total_parameters": total, "trainable_parameters": sum(parameter.numel() for parameter in model.parameters() if parameter.requires_grad), "rss_bytes_caveat": "macOS ru_maxrss process-resident proxy, not tensor-only device memory"}


def _tensor(batch: Batch) -> tuple[torch.Tensor, torch.Tensor]:
    return torch.from_numpy(batch.tokens), torch.from_numpy(batch.labels)


def _accuracy(logits: torch.Tensor, labels: torch.Tensor, operations: np.ndarray) -> dict[str, float]:
    predicted = logits.argmax(-1).cpu().numpy(); truth = labels.cpu().numpy()
    result: dict[str, float] = {}
    for name, operation in (("xor", XOR), ("copy", COPY)):
        index = operations == operation
        result[name] = float((predicted[index] == truth[index]).mean())
        result[f"{name}_correct"] = int((predicted[index] == truth[index]).sum())
        result[f"{name}_count"] = int(index.sum())
    return result


def evaluate(model: TinyClassifier, batches: dict[str, Batch], *, dt_zero: bool = False, command_started: float | None = None) -> dict:
    model.eval(); output: dict[str, dict] = {}
    with torch.no_grad():
        for name, batch in batches.items():
            if command_started is not None: budget_guard(command_started)
            tokens, labels = _tensor(batch)
            logits = model(tokens, dt_override=0.0 if dt_zero and model.mode == "schrodinger" else None)
            if not torch.isfinite(logits).all(): raise FloatingPointError("nonfinite evaluation logits")
            metrics = _accuracy(logits, labels, batch.operations)
            metrics["cross_entropy"] = float(nn.functional.cross_entropy(logits, labels))
            if not np.isfinite(metrics["cross_entropy"]): raise FloatingPointError("nonfinite evaluation loss")
            metrics["invariants"] = model.invariant_maxima()
            output[name] = metrics
    return output


def save_evaluation_data(batches: dict[str, Batch], destination: Path, *, kind: str) -> dict[str, str]:
    """Persist arrays plus content hashes so evaluation data are auditable."""
    payload: dict[str, np.ndarray] = {}
    hashes: dict[str, str] = {}
    for name, batch in batches.items():
        for suffix, value in (("tokens", batch.tokens), ("labels", batch.labels), ("operations", batch.operations), ("pairs", batch.pairs)):
            payload[f"{name}_{suffix}"] = value
        hashes[name] = batch.digest()
    destination.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(destination, **payload)
    destination.with_suffix(".manifest.json").write_text(json.dumps({"kind": kind, "hashes": hashes}, indent=2, sort_keys=True))
    return hashes


def load_evaluation_data(source: Path) -> dict[str, Batch]:
    archive = np.load(source); names = sorted({key.rsplit("_", 1)[0] for key in archive.files})
    return {name: Batch(archive[f"{name}_tokens"], archive[f"{name}_labels"], archive[f"{name}_operations"], archive[f"{name}_pairs"]) for name in names}


def evaluation_blacklist(batches: dict[str, Batch]) -> set[bytes]:
    return {row.tobytes() for batch in batches.values() for row in batch.tokens}


def _append_jsonl(path: Path, record: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a") as handle:
        handle.write(json.dumps(record, sort_keys=True) + "\n")


def _atomic_torch_save(value: dict, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=destination.parent, delete=False) as handle:
        temporary = Path(handle.name)
    try:
        torch.save(value, temporary); os.replace(temporary, destination)
    finally:
        temporary.unlink(missing_ok=True)


def ledger_total(path: Path = LEDGER_PATH) -> float:
    return sum(json.loads(line).get("charged_seconds", 0.0) for line in path.read_text().splitlines() if line) if path.exists() else 0.0


def append_ledger(kind: str, seconds: float, *, status: str = "success", path: Path = LEDGER_PATH, **extra: object) -> None:
    LEDGER_PATH.parent.mkdir(parents=True, exist_ok=True)
    prior = ledger_total(path)
    entry = {"kind": kind, "status": status, "charged_seconds": seconds, "cumulative_seconds": prior + seconds, **extra}
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a") as handle:
        handle.write(json.dumps(entry, sort_keys=True) + "\n")


def budget_guard(started: float, *, path: Path = LEDGER_PATH, cap: float = 13800.0, reserve: float = 60.0) -> None:
    if ledger_total(path) + (time.perf_counter() - started) + reserve >= cap:
        raise RuntimeError("hard pre-summary compute guard reached")


def _train_steps(model: TinyClassifier, seed: int, steps: int, run_dir: Path, *, eval_count: int | None, checkpoint: bool = True, command_started: float | None = None, initial_identity: dict | None = None) -> list[dict]:
    optimizer = torch.optim.AdamW(model.parameters(), lr=0.001, betas=(0.9, 0.999), eps=1e-8, weight_decay=0.01)
    all_evaluations = evaluation_sets(1729, eval_count) if eval_count != 0 else {}
    validation = {"validation_seen_d4": all_evaluations["validation_seen_d4"]} if all_evaluations else {}
    blacklist = evaluation_blacklist(all_evaluations)
    records: list[dict] = []; cumulative = 0.0
    stream = run_dir / "training.jsonl"; stream.unlink(missing_ok=True)
    def save_point(step: int, record: dict) -> None:
        if validation:
            started = time.perf_counter(); record["validation"] = evaluate(model, validation, command_started=command_started); record["evaluation_seconds"] = time.perf_counter() - started
        dt, gamma = model.evolution_parameters(); record["dt"] = dt.tolist(); record["gamma"] = gamma.tolist(); record["rss_bytes"] = int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss); record["invariants"] = model.invariant_maxima()
        if record["invariants"]["hermiticity"] > 1e-6 or record["invariants"]["unitarity"] > 2e-3 or record["invariants"]["row"] > 2e-3:
            raise FloatingPointError(f"numerical invariant failure: {record['invariants']}")
        if checkpoint:
            started = time.perf_counter(); _atomic_torch_save({"model": model.state_dict(), "optimizer": optimizer.state_dict(), "seed": seed, "mode": model.mode, "step": step, "config": config(), "source_hashes": source_hashes(), "initial_identity": initial_identity or model_identity(model), "current_state_identity": model_identity(model), "timings": record, "stream_digest": hashlib.sha256("".join(x.get("batch_digest", "") for x in records).encode()).hexdigest()}, run_dir / f"checkpoint-{step}.pt"); record["checkpoint_seconds"] = time.perf_counter() - started
        _append_jsonl(stream, record)
    save_point(0, {"step": 0, "examples": 0, "training_seconds": 0.0, "cumulative_training_seconds": 0.0})
    for step in range(steps):
        if command_started is not None: budget_guard(command_started)
        started = time.perf_counter(); batch = training_batch(seed, step, blacklist=blacklist); tokens, labels = _tensor(batch); model.train(); optimizer.zero_grad()
        logits = model(tokens); loss = nn.functional.cross_entropy(logits, labels)
        if not torch.isfinite(loss) or not torch.isfinite(logits).all(): raise FloatingPointError("nonfinite forward/loss")
        loss.backward()
        if any(parameter.grad is not None and not torch.isfinite(parameter.grad).all() for parameter in model.parameters()): raise FloatingPointError("nonfinite gradient")
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0); optimizer.step()
        if any(not torch.isfinite(parameter).all() for parameter in model.parameters()): raise FloatingPointError("nonfinite parameter after optimizer")
        elapsed = time.perf_counter() - started; cumulative += elapsed
        record = {"step": step + 1, "examples": (step + 1) * len(labels), "train_loss": float(loss.detach()), "training_seconds": elapsed, "cumulative_training_seconds": cumulative, "batch_digest": batch.digest()}
        records.append(record)
        if validation and (step == steps - 1 or (step + 1) % 100 == 0): save_point(step + 1, record)
        else: _append_jsonl(stream, record)
    return records


def smoke(seed: int, output: Path, command_started: float | None = None) -> None:
    configure_torch(); output.mkdir(parents=True, exist_ok=True); started = time.perf_counter()
    baseline, experimental = paired_models(seed)
    evaluation_data = evaluation_sets(1729, 8)
    result: dict[str, object] = {"kind": "SMOKE", "seed": seed, "config": config(), "evaluation_hashes": save_evaluation_data(evaluation_data, output / "evaluation.npz", kind="SMOKE"), "models": {}}
    for name, model in (("softmax", baseline), ("schrodinger", experimental)):
        run_dir = output / name; fixed_tokens, fixed_labels = _tensor(training_batch(seed, 999))
        with torch.no_grad(): initial_fixed_loss = float(nn.functional.cross_entropy(model(fixed_tokens), fixed_labels))
        fixed_optimizer = torch.optim.AdamW(model.parameters(), lr=0.001)
        for _ in range(4):
            fixed_optimizer.zero_grad(); fixed_loss = nn.functional.cross_entropy(model(fixed_tokens), fixed_labels); fixed_loss.backward(); fixed_optimizer.step()
        records = _train_steps(model, seed, 4, run_dir, eval_count=8, command_started=command_started)
        with torch.no_grad(): final_fixed_loss = float(nn.functional.cross_entropy(model(fixed_tokens), fixed_labels))
        if not final_fixed_loss < initial_fixed_loss:
            raise AssertionError(f"{name} smoke fixed-batch loss did not decrease")
        result["models"][name] = {"records": records, "initial_fixed_loss": initial_fixed_loss, "final_fixed_loss": final_fixed_loss, "final": evaluate(model, evaluation_data), "dt_zero": evaluate(model, evaluation_data, dt_zero=True) if name == "schrodinger" else None}
        loaded = TinyClassifier("softmax" if name == "softmax" else "schrodinger")
        loaded.load_state_dict(torch.load(run_dir / "checkpoint-4.pt", weights_only=False)["model"])
        tokens, _ = _tensor(training_batch(seed, 3)); torch.testing.assert_close(loaded(tokens), model(tokens), atol=1e-6, rtol=0)
    result["elapsed_seconds"] = time.perf_counter() - started
    (output / "smoke.json").write_text(json.dumps(result, indent=2, sort_keys=True))


def profile(seed: int, output: Path, command_started: float | None = None) -> None:
    configure_torch(); output.mkdir(parents=True, exist_ok=True); started = time.perf_counter(); result = {"kind": "THROUGHPUT_ONLY", "seed": seed, "config": config(), "models": {}}
    for name, model in zip(("softmax", "schrodinger"), paired_models(seed), strict=True):
        _train_steps(model, seed, 5, output / name, eval_count=0, checkpoint=False, command_started=command_started)
        records = _train_steps(model, seed, 20, output / name, eval_count=0, checkpoint=False, command_started=command_started)
        seconds = sum(record["training_seconds"] for record in records)
        result["models"][name] = {"steps": 20, "training_seconds": seconds, "examples_per_second": 20 * 64 / seconds}
    result["elapsed_seconds"] = time.perf_counter() - started
    (output / "profile.json").write_text(json.dumps(result, indent=2, sort_keys=True))


def pair_evaluate(first: Path, second: Path, output: Path) -> None:
    """Evaluate latest saved checkpoints at the common accumulated training time."""
    def points(directory: Path) -> list[dict]:
        return [json.loads(line) for line in (directory / "training.jsonl").read_text().splitlines() if line and json.loads(line)["step"] >= 0]
    left, right = points(first), points(second)
    def completed(directory: Path, records: list[dict]) -> tuple[dict, dict]:
        finals = [item for item in records if (directory / f"checkpoint-{item['step']}.pt").exists()]
        record = max(finals, key=lambda item: item["step"])
        if records[-1]["step"] != record["step"]: raise ValueError("raw JSONL extends beyond completed checkpoint")
        saved = torch.load(directory / f"checkpoint-{record['step']}.pt", weights_only=False)
        digest = saved.get("stream_digest", "")
        raw = hashlib.sha256("".join(item.get("batch_digest", "") for item in records if item["step"] <= record["step"]).encode()).hexdigest()
        if record["step"] <= 0 or not digest or digest != raw: raise ValueError("completed stream digest missing or inconsistent with raw JSONL")
        return record, saved
    first_final, first_completed = completed(first, left); second_final, second_completed = completed(second, right)
    if first_final["step"] != second_final["step"]: raise ValueError("paired completed final steps differ")
    if first_completed["stream_digest"] != second_completed["stream_digest"]: raise ValueError("paired completed stream digests differ")
    first_data, second_data = first / "evaluation.npz", second / "evaluation.npz"
    if not first_data.exists() or not second_data.exists(): raise FileNotFoundError("pair evaluation requires stored evaluation.npz for both runs")
    first_batches, second_batches = load_evaluation_data(first_data), load_evaluation_data(second_data)
    if {name: batch.digest() for name, batch in first_batches.items()} != {name: batch.digest() for name, batch in second_batches.items()}: raise ValueError("paired evaluation data hashes differ")
    first_seed = first_completed; second_seed = second_completed
    if first_seed.get("seed") != second_seed.get("seed") or first_seed.get("mode") == second_seed.get("mode"): raise ValueError("paired checkpoints require same seed and opposite modes")
    for key in ("config", "source_hashes"):
        if first_seed.get(key) != second_seed.get(key): raise ValueError(f"paired checkpoint {key} mismatch")
    if first_seed.get("initial_identity", {}).get("shared_initial_tensor_digest") != second_seed.get("initial_identity", {}).get("shared_initial_tensor_digest"):
        raise ValueError("paired checkpoint initial identity mismatch")
    left_final, right_final = left[-1]["cumulative_training_seconds"], right[-1]["cumulative_training_seconds"]
    common = min(left_final, right_final)
    chosen = []
    for directory, records, batches in ((first, left, first_batches), (second, right, second_batches)):
        candidates = [item for item in records if item["cumulative_training_seconds"] <= common and (directory / f"checkpoint-{item['step']}.pt").exists()]
        record = max(candidates, key=lambda item: item["step"])
        checkpoint = directory / f"checkpoint-{record['step']}.pt"; saved = torch.load(checkpoint, weights_only=False); model = TinyClassifier(saved["mode"]); model.load_state_dict(saved["model"])
        chosen.append({"checkpoint": str(checkpoint), "mode": saved["mode"], "seed": saved.get("seed"), "step": record["step"], "training_seconds": record["cumulative_training_seconds"], "slack": common-record["cumulative_training_seconds"], "metrics": evaluate(model, batches), "dt_zero": evaluate(model, batches, dt_zero=True) if saved["mode"] == "schrodinger" else None})
    output.parent.mkdir(parents=True, exist_ok=True); output.write_text(json.dumps({"common_training_seconds": common, "completed_final_steps": [first_final["step"], second_final["step"]], "completed_stream_digest": first_completed["stream_digest"], "initial_identity": first_seed["initial_identity"], "config": first_seed["config"], "source_hashes": first_seed["source_hashes"], "evaluation_hashes": {name: batch.digest() for name, batch in first_batches.items()}, "runs": chosen}, indent=2, sort_keys=True))


def main() -> None:
    parser = argparse.ArgumentParser(); parser.add_argument("command", choices=["smoke", "profile", "train", "evaluate", "pair-evaluate"]); parser.add_argument("--seed", type=int, default=11); parser.add_argument("--output", type=Path, default=ROOT / "execution" / "results" / "smoke"); parser.add_argument("--steps", type=int, default=100); parser.add_argument("--mode", choices=["softmax", "schrodinger"], default="softmax"); parser.add_argument("--checkpoint", type=Path); parser.add_argument("--other", type=Path); parser.add_argument("--dt-zero", action="store_true")
    args = parser.parse_args()
    command_started = time.perf_counter(); status = "success"; error: str | None = None
    try:
      budget_guard(command_started)
      if args.command == "smoke": smoke(args.seed, args.output, command_started)
      elif args.command == "profile": profile(args.seed, args.output, command_started)
      elif args.command == "train":
        configure_torch(); started = time.perf_counter(); model = paired_models(args.seed)[0 if args.mode == "softmax" else 1]; initial_identity = model_identity(model); full_evals = evaluation_sets(); identities = save_evaluation_data(full_evals, args.output / "evaluation.npz", kind="FROZEN"); records = _train_steps(model, args.seed, args.steps, args.output, eval_count=None, command_started=command_started, initial_identity=initial_identity); (args.output / "train.jsonl").write_text("\n".join(json.dumps(value) for value in records) + "\n"); normal_metrics = evaluate(model, full_evals, command_started=command_started); normal_max = {key: max(value["invariants"][key] for value in normal_metrics.values()) for key in ("hermiticity", "unitarity", "row")}; intervention = evaluate(model, full_evals, dt_zero=True, command_started=command_started) if args.mode == "schrodinger" else None; final = {"mode": args.mode, "seed": args.seed, "runtime": config(), "source_hashes": source_hashes(), "initial_identity": initial_identity, "evaluation_hashes": identities, "stream_digest": hashlib.sha256("".join(x.get("batch_digest", "") for x in records).encode()).hexdigest(), "final_checkpoint": str(args.output / f"checkpoint-{args.steps}.pt"), "training_seconds": sum(x.get("training_seconds", 0.0) for x in records), "evaluation_seconds": sum(x.get("evaluation_seconds", 0.0) for x in records), "checkpoint_seconds": sum(x.get("checkpoint_seconds", 0.0) for x in records), "metrics": normal_metrics, "dt_zero": intervention, "dt": model.evolution_parameters()[0].tolist(), "gamma": model.evolution_parameters()[1].tolist(), "invariants": normal_max, "end_to_end_seconds": time.perf_counter()-started}; (args.output / "final.json").write_text(json.dumps(final, indent=2, sort_keys=True))
      elif args.command == "evaluate":
        if args.checkpoint is None:
            raise ValueError("evaluate requires --checkpoint")
        configure_torch(); saved = torch.load(args.checkpoint, weights_only=False); mode = saved.get("mode", args.mode); model = TinyClassifier(mode); model.load_state_dict(saved["model"])
        stored = args.checkpoint.parent / "evaluation.npz"
        if not stored.exists(): raise FileNotFoundError(f"stored evaluation data required: {stored}")
        batches = load_evaluation_data(stored)
        result = {"checkpoint": str(args.checkpoint), "mode": mode, "dt_zero": args.dt_zero, "metrics": evaluate(model, batches, dt_zero=args.dt_zero, command_started=command_started)}
        args.output.mkdir(parents=True, exist_ok=True); (args.output / "evaluation.json").write_text(json.dumps(result, indent=2, sort_keys=True))
      else:
        if args.checkpoint is None or args.other is None: raise ValueError("pair-evaluate requires --checkpoint RUN_DIR and --other RUN_DIR")
        configure_torch(); pair_evaluate(args.checkpoint, args.other, args.output)
    except Exception as exc:
      status = "failed"; error = f"{type(exc).__name__}: {exc}"; failure_parent = args.output.parent if args.output.suffix else args.output; failure_parent.mkdir(parents=True, exist_ok=True); (failure_parent / "failure.json").write_text(json.dumps({"command": args.command, "error": error}, indent=2)); raise
    finally:
      append_ledger(f"cli_{args.command}", time.perf_counter() - command_started, status=status, artifact=str(args.output), error=error)


if __name__ == "__main__": main()
