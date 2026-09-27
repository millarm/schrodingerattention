"""Guarded immutable runner boundary for the v3 dataset invocation."""
from __future__ import annotations

import argparse
import dataclasses
import hashlib
import json
import math
import os
import platform
import signal
import sys
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

from schrodinger import productive_diversity_v3_data as data

ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "execution/next_level_v3/ledger.jsonl"
LOCK = ROOT / "execution/next_level_v3/runner.lock"
REJECTIONS = ROOT / "execution/next_level_v3/rejections"
STAGE_CAP_SECONDS = 1600.0
GLOBAL_CAP_SECONDS = 7200.0
STARTUP_ALLOWANCE_SECONDS = 2.0
FINALIZATION_RESERVE_SECONDS = 30.0
AUDIT_RESERVE_SECONDS = 120.0


class RunnerError(RuntimeError):
    pass


class Deadline(RunnerError):
    pass


STAGE_ORDER = ("training", "validation_routine", "validation_mixed", "test_routine", "test_mixed")


class ProposalStatuses:
    """Proposal-keyed decoder for the accepted Block2 callback protocol."""
    def __init__(self, proposals: tuple[int, ...] = ()) -> None:
        self.rows = {proposal: {stage: "NOT_COMPLETED_UNKNOWN" for stage in STAGE_ORDER} for proposal in proposals}
        self.artifacts: dict[tuple[int, str], dict[str, str]] = {}
    def observe(self, proposal: int, stage: str, payload: dict[str, object], filename: str, digest: str) -> None:
        if stage not in STAGE_ORDER: raise RunnerError("unknown callback stage")
        row = self.rows.setdefault(proposal, {name: "NOT_COMPLETED_UNKNOWN" for name in STAGE_ORDER})
        if payload.get("outcome") == "NOT_EVALUATED": outcome = "NOT_EVALUATED"
        elif stage == "training": outcome = payload.get("result", {}).get("outcome")
        else:
            results = payload.get("results")
            if not isinstance(results, list): raise RunnerError("unknown held-out callback payload")
            outcomes = [item.get("result", {}).get("outcome") for item in results]
            outcome = "OK" if outcomes and all(value == "OK" for value in outcomes) else next((value for value in outcomes if value != "OK"), None)
        accepted = {"OK", "NOT_EVALUATED", "SCIENTIFIC_TRAINING_SUPPLY_FAILED", "SCIENTIFIC_TRAINING_ORIENTATION_SHORTAGE", "SCIENTIFIC_HELDOUT_SUPPLY_FAILED"}
        if not isinstance(outcome, str) or outcome not in accepted: raise RunnerError("unknown callback outcome")
        row[stage] = "COMPLETE" if outcome == "OK" else outcome
        self.artifacts[(proposal, stage)] = {"file": filename, "sha256": digest}
    def failed_write(self, proposal: int, stage: str) -> None:
        row=self.rows.setdefault(proposal,{name:"NOT_COMPLETED_UNKNOWN" for name in STAGE_ORDER}); row[stage]="FAILED"
    def finalize(self, interrupted: bool) -> dict[str, object]:
        # Observations remain immutable: absence is not an observed outcome.
        derived = {proposal: {stage: "NOT_EVALUATED" if value == "NOT_COMPLETED_UNKNOWN" else value
                              for stage, value in row.items()}
                   for proposal, row in self.rows.items()}
        if interrupted:
            # Retained insertion order is selection order. Scientific failures
            # resolve a proposal; a write failure or full PASS terminates it.
            for proposal, row in self.rows.items():
                if "FAILED" in row.values() or all(value == "COMPLETE" for value in row.values()):
                    break
                if any(value.startswith("SCIENTIFIC_") for value in row.values()):
                    continue
                missing = next((stage for stage in STAGE_ORDER if row[stage] == "NOT_COMPLETED_UNKNOWN"), None)
                if missing is not None:
                    derived[proposal][missing] = "NOT_COMPLETED_UNKNOWN"
                    break
        return {str(key): {"stages": value, "artifacts": {stage:self.artifacts[(key,stage)] for stage in STAGE_ORDER if (key,stage) in self.artifacts}} for key,value in derived.items()}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _json(value: Any) -> Any:
    if dataclasses.is_dataclass(value):
        return _json(dataclasses.asdict(value))
    if isinstance(value, bytes):
        return {"bytes_hex": value.hex()}
    if isinstance(value, (set, frozenset)):
        return [_json(item) for item in sorted(value, key=repr)]
    if isinstance(value, tuple):
        return [_json(item) for item in value]
    if isinstance(value, list):
        return [_json(item) for item in value]
    if isinstance(value, dict):
        if all(isinstance(key, str) for key in value):
            return {key: _json(item) for key, item in value.items() if key != "cache"}
        return [{"key": _json(key), "value": _json(item)}
                for key, item in sorted(value.items(), key=lambda pair: repr(pair[0]))]
    if hasattr(value, "item"):
        return value.item()
    return value


def write_json(path: Path, value: object) -> str:
    """Write exactly once and hash the exact JSON bytes."""
    data = json.dumps(_json(value), sort_keys=True, separators=(",", ":"), allow_nan=False).encode()
    with path.open("xb") as handle:
        handle.write(data)
    return hashlib.sha256(data).hexdigest()


def _prior(path: Path, *, require_carry: bool = False) -> tuple[float, float]:
    """Return (v3-stage debit, global debit); historical carry is global-only."""
    stage = global_total = 0.0
    seen: set[str] = set()
    carries = 0
    if not path.exists():
        if require_carry:
            raise RunnerError("production v3 ledger requires exactly one carried budget debit")
        return stage, global_total
    for number, line in enumerate(path.read_text().splitlines(), 1):
        if not line.strip():
            continue
        row = json.loads(line)
        entry_id = row.get("entry_id")
        if not isinstance(entry_id, str) or not entry_id:
            raise RunnerError(f"ledger row {number} lacks entry_id")
        if entry_id in seen:
            raise RunnerError(f"duplicate ledger entry_id: {entry_id}")
        seen.add(entry_id)
        carry = float(row.get("carried_budget_debit_seconds", 0.0))
        charged = float(row.get("charged_seconds", 0.0))
        allowance = float(row.get("budget_allowance_seconds", 0.0))
        charge = charged + allowance
        if (not math.isfinite(carry) or not math.isfinite(charged) or not math.isfinite(allowance)
                or carry < 0 or charged < 0 or allowance < 0):
            raise RunnerError(f"negative ledger debit in {entry_id}")
        if "carried_budget_debit_seconds" in row:
            carries += 1
            if carry != 443.384519002:
                raise RunnerError("unexpected v3 carried budget debit")
        stage += charge
        global_total += carry + charge
    if require_carry and carries != 1:
        raise RunnerError("production v3 ledger requires exactly one carried budget debit")
    return stage, global_total


def _append_ledger(record: dict[str, Any], path: Path) -> None:
    """One append, protected against concurrent writers and duplicate IDs."""
    path.parent.mkdir(parents=True, exist_ok=True)
    lock = path.with_name(path.name + ".append.lock")
    fd = os.open(lock, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    try:
        existing = set()
        if path.exists():
            existing = {json.loads(line).get("entry_id") for line in path.read_text().splitlines() if line.strip()}
        if record["entry_id"] in existing:
            raise RunnerError(f"duplicate ledger entry_id: {record['entry_id']}")
        with path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, sort_keys=True, separators=(",", ":")) + "\n")
    finally:
        os.close(fd)
        try:
            lock.unlink()
        except FileNotFoundError:
            pass


class Attempt:
    """Owns one v3 output, lock, timer and exactly-one ledger charge."""
    def __init__(self, output: Path, *, lock: Path = LOCK, ledger: Path = LEDGER,
                 rejections: Path = REJECTIONS, deadline_seconds: float | None = None,
                 log_writer: Callable[[Path, object], str] = write_json) -> None:
        self.output, self.lock, self.ledger = Path(output), Path(lock), Path(ledger)
        self.rejections, self.override, self.log_writer = Path(rejections), deadline_seconds, log_writer
        self.entry_id, self.started, self.started_utc = str(uuid.uuid4()), time.perf_counter(), _now()
        self.stage_prior, self.global_prior = _prior(
            self.ledger, require_carry=self.ledger.resolve() == LEDGER.resolve())
        self.lock_fd: int | None = None
        self.owned_lock = self.owned_output = self.recorded = False
        self.manifest_sha256: str | None = None
        self.old_handler: Any = None
        self.old_timer: tuple[float, float] | None = None

    def deadline(self) -> float:
        value = min(STAGE_CAP_SECONDS - self.stage_prior, GLOBAL_CAP_SECONDS - self.global_prior)
        value -= STARTUP_ALLOWANCE_SECONDS + FINALIZATION_RESERVE_SECONDS + AUDIT_RESERVE_SECONDS
        if self.override is not None:
            if not math.isfinite(self.override) or self.override < 0:
                raise RunnerError("deadline override must be nonnegative")
            value = min(value, self.override)
        if value <= 0:
            raise Deadline("v3 stage/global budget exhausted")
        return value

    def _record(self, status: str, error: BaseException | None = None) -> dict[str, Any]:
        elapsed = time.perf_counter() - self.started
        return {"entry_id": self.entry_id, "kind": "productive_diversity_v3_runner",
                "status": status, "execution_status": status, "started_at_utc": self.started_utc,
                "ended_at_utc": _now(), "elapsed_seconds": elapsed, "charged_seconds": elapsed,
                "budget_allowance_seconds": STARTUP_ALLOWANCE_SECONDS,
                "stage_prior_seconds": self.stage_prior, "global_prior_seconds": self.global_prior,
                "argv": list(getattr(sys, "orig_argv", sys.argv)), "pid": os.getpid(),
                "manifest_sha256": getattr(self, "manifest_sha256", None),
                "error": None if error is None else repr(error)}

    def _append_once(self, record: dict[str, Any]) -> None:
        if not self.recorded:
            _append_ledger(record, self.ledger)
            self.recorded = True

    def _reject(self, error: BaseException) -> None:
        record = self._record("REJECTED", error)
        try:
            self.rejections.mkdir(parents=True, exist_ok=True)
            write_json(self.rejections / f"rejected-{self.entry_id}.json", record)
        finally:
            self._append_once(record)

    def _install_timer(self) -> None:
        self.old_handler = signal.getsignal(signal.SIGALRM)
        self.old_timer = signal.setitimer(signal.ITIMER_REAL, 0.0)
        signal.signal(signal.SIGALRM, lambda *_: (_ for _ in ()).throw(Deadline("v3 deadline")))
        signal.setitimer(signal.ITIMER_REAL, self.deadline())

    def cleanup(self) -> None:
        if self.old_handler is not None:
            signal.setitimer(signal.ITIMER_REAL, 0.0)
            signal.signal(signal.SIGALRM, self.old_handler)
            if self.old_timer is not None and self.old_timer[0] > 0:
                signal.setitimer(signal.ITIMER_REAL, *self.old_timer)
            self.old_handler = None
        if self.lock_fd is not None:
            os.close(self.lock_fd)
            self.lock_fd = None
        if self.owned_lock:
            try:
                self.lock.unlink()
            except FileNotFoundError:
                pass
            self.owned_lock = False

    def __enter__(self) -> "Attempt":
        try:
            if self.output.exists():
                raise FileExistsError("output already exists")
            self.lock.parent.mkdir(parents=True, exist_ok=True)
            self.lock_fd = os.open(self.lock, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
            self.owned_lock = True
            self.output.mkdir(parents=True, exist_ok=False)
            self.owned_output = True
            self._install_timer()
            return self
        except BaseException as error:
            try:
                self._reject(error)
            finally:
                self.cleanup()
            raise

    def __exit__(self, exc_type: object, exc: BaseException | None, traceback: object) -> bool:
        record = self._record("COMPLETE" if exc is None else "FAILED", exc)
        write_error: BaseException | None = None
        try:
            if not self.owned_output:
                raise RunnerError("attempt has no owned output")
            self.log_writer(self.output / "attempt.json", record)
        except BaseException as error:
            write_error = error
            record = {**self._record("FAILED", error), "error": f"mandatory attempt log failed: {error!r}"}
        finally:
            try:
                self._append_once(record)
            finally:
                self.cleanup()
        if write_error is not None:
            raise RunnerError(record["error"]) from write_error
        return False


def _source_hashes() -> dict[str, str]:
    required = (ROOT / "schrodinger/productive_diversity_v3_data.py", ROOT / "schrodinger/productive_diversity_v3_runner.py",
             ROOT / "schrodinger/route_feasibility.py", ROOT / "tests/test_productive_diversity_v3_data.py",
             ROOT / "tests/test_productive_diversity_v3_runner.py", ROOT / "productive_diversity_v3_plan.md",
             ROOT / "execution/next_level_v3/specs/00-dataset-contract.md", ROOT / "execution/next_level_v3/specs/03-runner.md",
             ROOT / "agent_execution_protocol.md")
    missing = [str(path) for path in required if not path.exists()]
    if missing:
        raise RunnerError("mandatory provenance input missing: " + ", ".join(missing))
    paths = set(required) | set((ROOT / "execution/next_level_v3/specs").glob("*.md")) | set((ROOT / "execution/next_level_v3/reviews").glob("*.md"))
    paths |= {ROOT / "execution/next_level_v3/fixtures/recovery_b_i8.json", ROOT / "execution/next_level_v3/fixtures/recovery_b_l8.json", ROOT / "execution/next_level_v3/fixtures/recovery_b_mixed.json"}
    return {str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest() for path in sorted(paths)}


def _save(attempt: Attempt, name: str, value: object) -> str:
    return write_json(attempt.output / name, value)


def _validate_pass(result: dict[str, object], records: tuple[dict[str, object], ...], counts: dict[str, int], train_maps_per_family: int, ranking: dict[str, object]) -> None:
    """Runner-side checks ensure an upstream source defect cannot label PASS."""
    if result.get("outcome") != "FIRST_FULL_DATASET_PASS":
        return
    stages = result["stages"]; proposal = result["proposal"]
    if proposal not in ranking.get("retained", ()):
        raise RunnerError("PASS proposal is not a retained ranking proposal")
    lengths, quota = tuple(proposal["window"]), tuple(proposal["quota"])
    training = stages["training"]
    if training.get("outcome") != "OK":
        raise RunnerError("PASS lacks successful training")
    support = tuple(training["support"])
    encoded = b"".join(len(item).to_bytes(2, "big") + item for item in support)
    if hashlib.sha256(encoded).hexdigest() != training["support_hash"]:
        raise RunnerError("support hash mismatch")
    expected = {"validation_routine": counts["val_routine"] * 2,
                "validation_mixed": counts["val_mixed"], "test_routine": counts["test_routine"] * 2,
                "test_mixed": counts["test_mixed"]}
    known = {row["canonical"]: row for row in records}
    def validate_rows(rows, name, *, mode):
        by_map: dict[bytes, list[dict[str, object]]] = {}
        for row in rows:
            source = known.get(row["canonical"])
            if source is None or row["n"] != 12 or row["family"] != source["family"] or row["map_id"] != source["map_id"]:
                raise RunnerError(f"PASS {name} row identity mismatch")
            pair = (row["start"], row["goal"], row["length"], row["M"])
            if row["length"] not in source["shortlists"] or pair not in source["shortlists"][row["length"]]["retained"]:
                raise RunnerError(f"PASS {name} row inventory mismatch")
            novel = row.get("Mnovel")
            if (mode == "routine" and novel != 0) or (mode == "challenge" and not (isinstance(novel, int) and novel >= 4 and 4 * novel >= row["M"] and 4 * novel <= 3 * row["M"])):
                raise RunnerError(f"PASS {name} novelty predicate mismatch")
            by_map.setdefault(row["canonical"], []).append(row)
        for map_rows in by_map.values():
            if len(map_rows) != sum(quota) or {row["length"] for row in map_rows} != set(lengths):
                raise RunnerError(f"PASS {name} per-map quota mismatch")
            if any(sum(row["length"] == length for row in map_rows) != need for length, need in zip(lengths, quota)):
                raise RunnerError(f"PASS {name} per-length quota mismatch")
        return set(by_map)
    train_rows = training["selected"]
    train_ids = validate_rows([{**row, "Mnovel": 0} for row in train_rows], "training", mode="routine")
    if {row["family"] for row in train_rows} != {"IIIIIIII", "LLLLLLLL"}:
        raise RunnerError("PASS training family mismatch")
    if any(sum(row["family"] == family for row in train_rows) != train_maps_per_family * sum(quota) for family in ("IIIIIIII", "LLLLLLLL")):
        raise RunnerError("PASS training count mismatch")
    identities = set(train_ids)
    wrappers = {"validation_routine": ("IIIIIIII", "LLLLLLLL"), "validation_mixed": ("IIIILLLL",),
                "test_routine": ("IIIIIIII", "LLLLLLLL"), "test_mixed": ("IIIILLLL",)}
    for name, amount in expected.items():
        groups = stages.get(name)
        if not isinstance(groups, list) or tuple(group.get("family") for group in groups) != wrappers[name]:
            raise RunnerError(f"PASS {name} wrapper family sequence mismatch")
        if any(group.get("result", {}).get("outcome") != "OK" for group in groups):
            raise RunnerError(f"PASS {name} non-OK stage result")
        rows = [row for family in groups for row in family["result"]["selected"]]
        current = validate_rows(rows, name, mode="challenge" if "mixed" in name else "routine")
        if len(current) != amount:
            raise RunnerError(f"PASS {name} map count mismatch")
        if identities & current:
            raise RunnerError(f"PASS {name} identity leakage")
        identities |= current


def execute_pipeline(attempt: Attempt, *, pools_fn: Callable[..., data.PoolResult] = data.pool_family,
                     assemble_fn: Callable[..., tuple[dict[str, object], ...]] = data.assemble_global_inventory,
                     rank_fn: Callable[..., dict[str, object]] = data.rank_proposals,
                     config: data.SelectionConfig | None = None, counts: dict[str, int] | None = None) -> dict[str, object]:
    """Persist each immutable boundary; seams exist solely for tiny integration tests."""
    config = config or data.SelectionConfig((12, 13, 14), (6, 5, 5), 32)
    counts = counts or {"val_routine": 12, "val_mixed": 8, "test_routine": 48, "test_mixed": 32}
    pools: dict[str, data.PoolResult] = {}; records: tuple[dict[str, object], ...] = (); ranking: dict[str, object] = {}
    stage_hashes: dict[str, str] = {}; output_hashes: dict[str, str] = {}; reached: list[str] = []; statuses = ProposalStatuses()
    def on_stage(name: str, payload: dict[str, object]) -> None:
        proposal = payload["proposal"]
        filename = f"proposal-{proposal}-{name}.json"
        try:
            stage_hashes[filename] = _save(attempt, filename, payload); reached.append(filename)
            statuses.observe(proposal, name, payload, filename, stage_hashes[filename])
        except BaseException:
            statuses.failed_write(proposal, name)
            raise
    result: dict[str, object] | None = None
    error: BaseException | None = None
    try:
        for family in data.FAMILIES:
            pools[family] = pools_fn(family)
            name = f"pool-{family}.json"; output_hashes[name] = _save(attempt, name, pools[family]); reached.append(name)
        records = assemble_fn(pools); data.validate_inventory_records(records)
        output_hashes["inventory.json"] = _save(attempt, "inventory.json", records); reached.append("inventory.json")
        ranking = rank_fn(records)
        output_hashes["ranking.json"] = _save(attempt, "ranking.json", ranking); reached.append("ranking.json")
        statuses = ProposalStatuses(tuple(item["window_start"] for item in ranking.get("retained", ())[:3]))
        result = data.run_ranked_proposals(ranking, records, config=config, counts=counts, on_stage=on_stage)
        _validate_pass(result, records, counts, config.train_maps_per_family, ranking)
        output_hashes["result.json"] = _save(attempt, "result.json", result); reached.append("result.json")
    except BaseException as caught:
        error = caught
    finally:
        for path in sorted(attempt.output.glob("*.json")):
            if path.name not in {"manifest.json", "summary.json", "attempt.json"}:
                output_hashes.setdefault(path.name, hashlib.sha256(path.read_bytes()).hexdigest())
        selected = result.get("proposal") if result else None
        effective = {"n": 12, "families": data.FAMILIES, "shape_components": 8,
                     "family_composition": {family: {"I": family.count("I"), "L": family.count("L")} for family in data.FAMILIES},
                     "seeds": {"pool": data.POOL_SEED, "shortlist": data.SHORTLIST_SEED, "split": data.SPLIT_SEED,
                               "family_codes": data.FAMILY_CODE},
                     "selection": {"window": selected.get("window") if selected else None, "quota": selected.get("quota") if selected else None,
                                   "train_maps_per_family": config.train_maps_per_family, "counts": counts},
                     "pool": {"limit": 256, "max_trials": 200000, "direct_placements": "cached n12 I/L"}, "shortlist_cap": 64,
                     "ranking_windows": data.WINDOWS, "ranking_quotas": data.QUOTAS,
                     "support": "all nonempty canonical suffixes", "novelty": "routine=0; challenge>=4 and 1/4..3/4",
                     "budget": {"stage": STAGE_CAP_SECONDS, "global": GLOBAL_CAP_SECONDS, "startup": STARTUP_ALLOWANCE_SECONDS,
                                "reserve": FINALIZATION_RESERVE_SECONDS, "audit_reserve": AUDIT_RESERVE_SECONDS,
                                "stage_prior": attempt.stage_prior, "global_prior": attempt.global_prior}}
        outcome = result.get("outcome") if result is not None and error is None else ("DEADLINE_FAILED" if isinstance(error, Deadline) else "TECHNICAL_FAILED")
        manifest = {"effective_config": effective, "argv": list(getattr(sys, "orig_argv", sys.argv)), "executable": sys.executable,
                    "runtime": {"python": sys.version, "numpy": __import__("numpy").__version__, "pid": os.getpid(),
                                "platform": platform.platform(), "cpu": platform.processor() or platform.machine(),
                                "threads": {key: os.environ.get(key) for key in ("OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS")}},
                    "sources": _source_hashes(), "outputs": {**output_hashes, **stage_hashes}, "reached": reached,
                    "outcome": outcome, "error": None if error is None else repr(error)}
        finalization_error: BaseException | None = None
        try:
            attempt.manifest_sha256 = _save(attempt, "manifest.json", manifest)
            _save(attempt, "summary.json", {"outcome": manifest["outcome"], "manifest_sha256": attempt.manifest_sha256,
                                              "reached": reached, "proposals": statuses.finalize(error is not None),
                                              "error": manifest["error"]})
        except BaseException as caught:
            finalization_error = caught
        if finalization_error is not None:
            if error is not None:
                raise error from finalization_error
            raise finalization_error
    if error is not None:
        raise error
    assert result is not None
    return result


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    args = parser.parse_args(argv)
    with Attempt(Path(args.output)) as attempt:
        result = execute_pipeline(attempt)
    print(json.dumps({"outcome": result["outcome"], "output": str(args.output),
                      "manifest_sha256": attempt.manifest_sha256}, sort_keys=True, separators=(",", ":"), allow_nan=False))


if __name__ == "__main__":
    main()
