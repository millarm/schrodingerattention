"""Standard-library-only one-shot owner driver for early-learning inference."""
from __future__ import annotations

import argparse
import fcntl
import hashlib
import json
import math
import os
import signal
import subprocess
import sys
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path

from execution.update_efficiency import watchdog

HERE = Path(__file__).resolve().parent
WORKSPACE = HERE.parents[1]
ATTEMPTS = HERE / "attempts"
LEDGER = HERE / "ledger.jsonl"
LOCK = HERE / "driver.lock"
INVENTORY = HERE / "inventory.json"
PLAN = HERE / "plan.md"
SPEC = HERE / "spec-01-dense-scoring.md"
METHOD_REVIEW = HERE / "reviews" / "00-methodology.md"
METHOD_ACCEPTANCE = HERE / "methodology-acceptance.md"
AMENDMENT = HERE / "amendment-01-statewise-kl.md"
AMENDMENT_SPEC = HERE / "spec-02-corrections-and-kl.md"
AMENDMENT_REVIEW = HERE / "reviews" / "02-amendment-methodology.md"
AMENDMENT_ACCEPTANCE = HERE / "amendment-acceptance.md"
FINAL_CORRECTION_SPEC = HERE / "spec-03-final-static-correction.md"
FINAL_CORRECTION_REVIEW = HERE / "reviews" / "03-static-rereview.md"
OLD_LEDGER = WORKSPACE / "execution" / "model_training_comparison" / "ledger.jsonl"
OLD_LEDGER_SHA = "ddfe5b2df043d940b1dcbf30ed367483abac1a5935863d123a1e9c6267229da2"
CAPS = {"A": 120.0, "B": 1440.0, "C": 0.0, "D": 240.0}
GLOBAL_CAP = 1800.0
ENVELOPES = {"softmax": 300.0, "schrodinger": 360.0}
ALLOWANCE = 1.0
MIN_FREE = 2 * 1024 ** 3
ORDER = ((2201, "softmax"), (2201, "schrodinger"),
         (2202, "schrodinger"), (2202, "softmax"))


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _json(path: Path) -> dict:
    value = json.loads(Path(path).read_text())
    if not isinstance(value, dict):
        raise ValueError("JSON object required")
    return value


def _durable(path: Path, value: dict) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name("." + path.name + "." + uuid.uuid4().hex)
    try:
        with temporary.open("xb") as stream:
            stream.write(json.dumps(value, sort_keys=True, allow_nan=False,
                                    separators=(",", ":")).encode())
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
        directory = os.open(path.parent, os.O_RDONLY)
        try:
            os.fsync(directory)
        finally:
            os.close(directory)
    finally:
        temporary.unlink(missing_ok=True)


def authority_hashes() -> dict[str, str]:
    sources = {
        "command": HERE / "command.py", "study": HERE / "study.py",
        "tests": WORKSPACE / "tests" / "test_early_learning.py",
        "inventory": INVENTORY, "plan": PLAN, "spec": SPEC,
        "methodology_review": METHOD_REVIEW, "methodology_acceptance": METHOD_ACCEPTANCE,
        "amendment": AMENDMENT, "amendment_spec": AMENDMENT_SPEC,
        "amendment_methodology_review": AMENDMENT_REVIEW,
        "amendment_acceptance": AMENDMENT_ACCEPTANCE,
        "final_correction_spec": FINAL_CORRECTION_SPEC,
        "final_correction_review": FINAL_CORRECTION_REVIEW,
        "research_refocus": WORKSPACE / "research" / "early_learning_refocus_2026-09-27.md",
        "protocol": WORKSPACE / "agent_execution_protocol.md",
        "accepted_driver": WORKSPACE / "execution" / "update_efficiency" / "command.py",
        "watchdog": WORKSPACE / "execution" / "update_efficiency" / "watchdog.py",
        "accepted_model": WORKSPACE / "schrodinger" / "route_policy.py",
        "accepted_experiment": WORKSPACE / "schrodinger" / "route_policy_experiment.py",
        "accepted_data": WORKSPACE / "schrodinger" / "route_policy_data.py",
        "accepted_evaluation": WORKSPACE / "schrodinger" / "route_policy_evaluation.py",
        "accepted_metrics": WORKSPACE / "schrodinger" / "route_policy_metrics.py",
        "attention": WORKSPACE / "schrodinger" / "attention.py",
        "feasibility": WORKSPACE / "schrodinger" / "route_feasibility.py",
    }
    return {key: sha256(path) for key, path in sorted(sources.items())}


def _ledger_rows(raw: bytes) -> tuple[list[dict], dict[str, float]]:
    if not raw.endswith(b"\n"):
        raise RuntimeError("ledger EOF is incomplete")
    rows = [json.loads(line) for line in raw.splitlines()]
    if not rows or rows[0].get("kind") != "inherited_budget" or rows[0].get("carried_budget_debit_seconds") != 0:
        raise RuntimeError("zero-carry allocation record missing")
    if rows[0].get("allocation_seconds") != {key: int(value) for key, value in CAPS.items()}:
        raise RuntimeError("stage allocation identity mismatch")
    if rows[0].get("global_allocation_seconds") != int(GLOBAL_CAP):
        raise RuntimeError("global allocation identity mismatch")
    ids, totals = set(), dict.fromkeys(CAPS, 0.0)
    for row in rows:
        ident, charge = row.get("entry_id"), row.get("charged_seconds")
        if not isinstance(ident, str) or ident in ids:
            raise RuntimeError("duplicate/missing ledger identity")
        if isinstance(charge, bool) or not isinstance(charge, (int, float)) or not math.isfinite(charge) or charge < 0:
            raise RuntimeError("invalid ledger charge")
        ids.add(ident)
        if row.get("kind") != "inherited_budget":
            stage = row.get("stage")
            if stage not in totals:
                raise RuntimeError("invalid ledger stage")
            totals[stage] += float(charge)
    return rows, totals


def _snapshot() -> tuple[bytes, list[dict], dict[str, float]]:
    with LEDGER.open("a+b") as stream:
        fcntl.flock(stream, fcntl.LOCK_EX)
        try:
            stream.seek(0)
            raw = stream.read()
        finally:
            fcntl.flock(stream, fcntl.LOCK_UN)
    rows, totals = _ledger_rows(raw)
    return raw, rows, totals


def ledger_eof() -> str:
    return hashlib.sha256(_snapshot()[0]).hexdigest()


def initialize_ledger() -> None:
    if LEDGER.exists():
        _snapshot()
        return
    if not OLD_LEDGER.is_file() or sha256(OLD_LEDGER) != OLD_LEDGER_SHA:
        raise RuntimeError("historical ledger SHA mismatch")
    row = {"entry_id": str(uuid.uuid4()), "recorded_at_utc": datetime.now(timezone.utc).isoformat(),
        "kind": "inherited_budget", "status": "ALLOCATION", "charged_seconds": 0.0,
        "carried_budget_debit_seconds": 0.0,
        "allocation_seconds": {key: int(value) for key, value in CAPS.items()},
        "global_allocation_seconds": int(GLOBAL_CAP), "historical_ledger_sha256": OLD_LEDGER_SHA}
    LEDGER.parent.mkdir(parents=True, exist_ok=True)
    with LEDGER.open("xb") as stream:
        stream.write(json.dumps(row, sort_keys=True, allow_nan=False).encode() + b"\n")
        stream.flush()
        os.fsync(stream.fileno())


def _append_once(row: dict) -> None:
    with LEDGER.open("a+b") as stream:
        fcntl.flock(stream, fcntl.LOCK_EX)
        try:
            stream.seek(0)
            rows, _ = _ledger_rows(stream.read())
            if any(item.get("entry_id") == row.get("entry_id") for item in rows):
                raise RuntimeError("duplicate ledger append id")
            stream.seek(0, os.SEEK_END)
            stream.write(json.dumps(row, sort_keys=True, allow_nan=False).encode() + b"\n")
            stream.flush()
            os.fsync(stream.fileno())
        finally:
            fcntl.flock(stream, fcntl.LOCK_UN)


def _append_once_certain(row: dict) -> bool:
    """Append/reconcile exactly one preassigned ledger identity.

    A retry is allowed only with the same UUID and only after a readable EOF
    proves that the first attempt left no row. Any ambiguity fails closed.
    """
    def reconcile() -> bool | None:
        try:
            rows = _snapshot()[1]
        except BaseException:
            return None
        matches = [item for item in rows if item.get("entry_id") == row.get("entry_id")]
        if not matches:
            return False
        if len(matches) != 1:
            return None
        return matches[0] == row
    try:
        _append_once(row)
        return reconcile() is True
    except BaseException:
        state = reconcile()
        if state is True:
            return True
        if state is None:
            return False
        try:
            _append_once(row)
            return reconcile() is True
        except BaseException:
            return reconcile() is True


def _durable_certain(path: Path, value: dict, state: dict | None = None) -> bool:
    """Remember any failed terminal durability operation for this attempt.

    A later readable/replaced file cannot prove the earlier directory fsync
    succeeded, so the attempt must retain its reservation permanently.
    """
    if state is None:
        state = {"uncertain": False}
    try:
        _durable(path, value)
        return not state["uncertain"]
    except BaseException:
        state["uncertain"] = True
        return False


def _review_ok(decision: dict, hashes: dict[str, str]) -> None:
    review = decision.get("review")
    if not isinstance(review, dict):
        raise RuntimeError("implementation review binding missing")
    path = Path(review.get("path", ""))
    text = path.read_text() if path.is_file() else ""
    phase = review.get("phase")
    if phase not in ("static-safety", "implementation") or not path.is_file() or sha256(path) != review.get("sha256"):
        raise RuntimeError("implementation review identity mismatch")
    token = "IMPLEMENTATION_REVIEW_VERDICT: PASS" if phase == "implementation" else "DRIVER_REVIEW_VERDICT: PASS"
    if text.count(token) != 1 or any(digest not in text for digest in hashes.values()):
        raise RuntimeError("review PASS does not bind all sources")
    if decision.get("kind") in ("production", "audit"):
        binding = decision.get("astra_acceptance")
        if phase != "implementation" or not isinstance(binding, dict):
            raise RuntimeError("distinct Astra exact-version acceptance required")
        acceptance_path = Path(binding.get("path", ""))
        if not acceptance_path.is_file() or sha256(acceptance_path) != binding.get("sha256"):
            raise RuntimeError("Astra acceptance artifact identity mismatch")
        acceptance = _json(acceptance_path)
        if (acceptance.get("verdict") != "ASTRA_ACCEPTANCE_VERDICT: PASS"
                or acceptance.get("implementation_review_path") != str(path.resolve())
                or acceptance.get("implementation_review_sha256") != sha256(path)
                or acceptance.get("source_hashes") != hashes):
            raise RuntimeError("Astra acceptance does not bind this exact reviewed version")


def review_ok(decision: dict, hashes: dict[str, str]) -> None:
    _review_ok(decision, hashes)


def _reserve(decision: dict, stage: str, envelope: float) -> None:
    try:
        fd = os.open(LOCK, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
        os.close(fd)
    except FileExistsError as error:
        raise RuntimeError("early-learning driver reservation already exists") from error
    try:
        raw, rows, totals = _snapshot()
        if decision.get("ledger_sha256") != hashlib.sha256(raw).hexdigest():
            raise RuntimeError("ledger EOF changed after decision")
        hashes = authority_hashes()
        if decision.get("source_hashes") != hashes:
            raise RuntimeError("reviewed source set changed")
        if decision.get("inventory_sha256") != sha256(INVENTORY):
            raise RuntimeError("immutable inventory changed")
        if decision.get("plan_sha256") != sha256(PLAN) or decision.get("spec_sha256") != sha256(SPEC):
            raise RuntimeError("plan/spec identity changed")
        _review_ok(decision, hashes)
        if totals[stage] + envelope > CAPS[stage] or sum(totals.values()) + envelope > GLOBAL_CAP:
            raise RuntimeError("fresh inference envelope exceeds allocation")
        if sha256(OLD_LEDGER) != OLD_LEDGER_SHA:
            raise RuntimeError("historical ledger changed")
    except BaseException:
        LOCK.unlink(missing_ok=True)
        raise


def _owner_path(seed: int, mode: str) -> Path:
    return ATTEMPTS / f"early-{seed}-{mode}-0-to-3000"


def _expected_order(seed: int, mode: str) -> None:
    key = (seed, mode)
    index = ORDER.index(key)
    if _owner_path(seed, mode).exists():
        raise RuntimeError("owner already has durable history; automatic retry is forbidden")
    for prior_seed, prior_mode in ORDER[:index]:
        prior = _owner_path(prior_seed, prior_mode)
        terminal = _json(prior / "attempt.json") if (prior / "attempt.json").is_file() else {}
        result = _json(prior / "result.json") if (prior / "result.json").is_file() else {}
        if terminal.get("status") != "COMPLETE" or result.get("status") != "COMPLETE":
            raise RuntimeError("fixed sequential owner order is incomplete")


def _inventory_entry(seed: int, mode: str) -> dict:
    inventory = _json(INVENTORY)
    rows = [row for row in inventory.get("owners", [])
            if row.get("seed") == seed and row.get("mode") == mode]
    if len(rows) != 1:
        raise RuntimeError("immutable inventory entry missing or duplicated")
    return rows[0]


def _acceptance_binding(review_path: Path, acceptance_path: Path, hashes: dict[str, str]) -> dict:
    review_path, acceptance_path = Path(review_path).resolve(), Path(acceptance_path).resolve()
    if not acceptance_path.is_file():
        raise RuntimeError("Astra exact-version acceptance artifact missing")
    acceptance = _json(acceptance_path)
    if (acceptance.get("verdict") != "ASTRA_ACCEPTANCE_VERDICT: PASS"
            or acceptance.get("implementation_review_path") != str(review_path)
            or acceptance.get("implementation_review_sha256") != sha256(review_path)
            or acceptance.get("source_hashes") != hashes):
        raise RuntimeError("Astra acceptance artifact is stale or mismatched")
    return {"path": str(acceptance_path), "sha256": sha256(acceptance_path)}


def make_owner_decision(seed: int, mode: str, review_path: Path,
                        acceptance_path: Path, output: Path) -> dict:
    if (seed, mode) not in ORDER:
        raise ValueError("unknown owner")
    review_path = Path(review_path).resolve()
    hashes = authority_hashes()
    acceptance = _acceptance_binding(review_path, acceptance_path, hashes)
    decision = {"approved": True, "kind": "production", "stage": "B",
        "seed": seed, "mode": mode, "updates": 3000, "envelope_seconds": ENVELOPES[mode],
        "cwd": str(WORKSPACE), "argv": [sys.executable, "-m", "execution.early_learning.study",
            "--decision", str(Path(output).resolve())],
        "argv_template": [sys.executable, "-m", "execution.early_learning.study",
            "--decision", str(Path(output).resolve()), "--session", "SESSION", "--nonce", "NONCE"],
        "source_hashes": hashes, "inventory_sha256": sha256(INVENTORY),
        "owner_inventory_entry": _inventory_entry(seed, mode),
        "ledger_sha256": ledger_eof(), "plan_sha256": sha256(PLAN), "spec_sha256": sha256(SPEC),
        "review": {"path": str(review_path), "phase": "implementation", "sha256": sha256(review_path)},
        "astra_acceptance": acceptance,
        "expires_unix": time.time() + 300.0}
    _durable(Path(output), decision)
    return decision


def make_check_decision(kind: str, review_path: Path, output: Path) -> dict:
    if kind not in ("smoke", "suite"):
        raise ValueError("check kind must be smoke or suite")
    test = "tests/test_early_learning.py::test_smoke_gate" if kind == "smoke" else "tests/test_early_learning.py"
    argv = [sys.executable, "-m", "pytest", "-q", test]
    review_path = Path(review_path).resolve()
    decision = {"approved": True, "kind": kind, "stage": "A",
        "envelope_seconds": 10.0 if kind == "smoke" else 60.0,
        "cwd": str(WORKSPACE), "argv": argv, "source_hashes": authority_hashes(),
        "inventory_sha256": sha256(INVENTORY), "ledger_sha256": ledger_eof(),
        "plan_sha256": sha256(PLAN), "spec_sha256": sha256(SPEC),
        "review": {"path": str(review_path), "phase": "static-safety", "sha256": sha256(review_path)}}
    _durable(Path(output), decision)
    return decision


def make_audit_decision(review_path: Path, acceptance_path: Path, output: Path) -> dict:
    review_path = Path(review_path).resolve()
    hashes = authority_hashes()
    acceptance = _acceptance_binding(review_path, acceptance_path, hashes)
    decision = {"approved": True, "kind": "audit", "stage": "D",
        "envelope_seconds": 240.0, "cwd": str(WORKSPACE),
        "source_hashes": hashes, "inventory_sha256": sha256(INVENTORY),
        "ledger_sha256": ledger_eof(), "plan_sha256": sha256(PLAN), "spec_sha256": sha256(SPEC),
        "review": {"path": str(review_path), "phase": "implementation", "sha256": sha256(review_path)}}
    decision["astra_acceptance"] = acceptance
    _durable(Path(output), decision)
    return decision


def _run_check(decision_path: Path, decision: dict) -> None:
    kind = decision.get("kind")
    test = "tests/test_early_learning.py::test_smoke_gate" if kind == "smoke" else "tests/test_early_learning.py"
    envelope = 10.0 if kind == "smoke" else 60.0
    expected = [sys.executable, "-m", "pytest", "-q", test]
    if decision.get("stage") != "A" or decision.get("argv") != expected or decision.get("envelope_seconds") != envelope:
        raise RuntimeError("bounded check decision mismatch")
    started = time.monotonic()
    if __import__("shutil").disk_usage(HERE).free < MIN_FREE:
        raise RuntimeError("less than two GiB free")
    _reserve(decision, "A", envelope)
    session = ATTEMPTS / ("driver-check-" + str(uuid.uuid4()))
    session.mkdir(parents=True, exist_ok=False)
    charge_id = str(uuid.uuid4())
    cleanup = accounted = terminal = False
    terminal_state = {"uncertain": False}
    charge_row = None
    prior_handler = signal.getsignal(signal.SIGTERM)
    try:
        signal.signal(signal.SIGTERM, _interrupt)
        child = watchdog.supervise(expected, WORKSPACE, session, started + envelope - ALLOWANCE)
        cleanup = child.get("cleanup_verified") is True
        charged = max(time.monotonic() - started + ALLOWANCE, 0.0)
        success = child.get("exit_code") == 0 and not child.get("timed_out") and cleanup and charged <= envelope
        charge_row = {"entry_id": charge_id, "recorded_at_utc": datetime.now(timezone.utc).isoformat(),
            "kind": "driver_check", "stage": "A", "status": "COMPLETE" if success else "FAILED",
            "charged_seconds": charged, "external_seconds": charged, "output": str(session)}
        accounted = _append_once_certain(charge_row)
        if not accounted:
            raise RuntimeError("check charge append is uncertain; reservation retained")
        terminal_row = {"status": "COMPLETE" if success else "FAILED",
            "charge_entry_id": charge_id, "charged_seconds": charged, "cleanup_verified": cleanup}
        terminal = _durable_certain(session / "terminal.json", terminal_row, terminal_state)
        if not terminal:
            raise RuntimeError("check terminal durability is uncertain; reservation retained")
        if not success:
            raise RuntimeError("bounded acceptance check failed")
    except BaseException as error:
        if not accounted:
            if charge_row is None:
                charged = max(time.monotonic() - started + ALLOWANCE, 0.0)
                charge_row = {"entry_id": charge_id, "recorded_at_utc": datetime.now(timezone.utc).isoformat(),
                    "kind": "driver_check", "stage": "A", "status": "FAILED",
                    "charged_seconds": charged, "external_seconds": charged, "output": str(session),
                    "error": repr(error)}
            accounted = _append_once_certain(charge_row)
        if not terminal:
            terminal = _durable_certain(session / "terminal.json", {"status": "FAILED_DRIVER",
                "charge_entry_id": charge_id, "error": repr(error),
                "charged_seconds": max(time.monotonic() - started + ALLOWANCE, 0.0),
                "cleanup_verified": cleanup, "accounting_resolved": accounted}, terminal_state)
        raise
    finally:
        signal.signal(signal.SIGTERM, prior_handler)
        if accounted and cleanup and terminal:
            LOCK.unlink(missing_ok=True)


def _audit_work(decision: dict, summary_path: Path) -> dict:
    from execution.early_learning import study

    owners, reused, new, greedy, probes = [], 0, 0, 0, 0
    by_seed = {}
    for seed, mode in ORDER:
        owner_path = _owner_path(seed, mode)
        result = _validate_complete(owner_path, seed, mode, decision["inventory_sha256"])
        metadata = _json(owner_path / "lineage.json")["statewise_rows"]
        points, statewise_rows = result["points"], []
        states_by_update = {}
        for point in points:
            detail = _json(owner_path / f"score-{point['update']:04d}.json")
            if detail.get("point") != point or not isinstance(detail.get("greedy"), dict):
                raise RuntimeError("raw checkpoint evidence/greedy cell missing")
            proper = detail.get("proper")
            rebuilt = study.statewise_scores(proper["rows"], proper["arrays"], metadata)
            if rebuilt != detail.get("statewise"):
                raise RuntimeError("stored statewise arithmetic does not reproduce from raw arrays")
            if abs(point["metrics"]["nonoptimal_mass"] - rebuilt["weighted_nonoptimal_mass"]) > 1e-10:
                raise RuntimeError("nonoptimal-mass point differs from statewise reconstruction")
            if point["update"] in (0, 1200, 2000, 2400):
                reused += 1
            else:
                new += 1
                if not isinstance(proper, dict) or not isinstance(detail.get("rollout"), dict):
                    raise RuntimeError("new proper/Q evidence missing")
            greedy += 1
            if detail.get("probe") is not None:
                probes += 1
            states_by_update[point["update"]] = rebuilt
            statewise_rows.append({"update": point["update"],
                "weighted_nonoptimal_mass": rebuilt["weighted_nonoptimal_mass"],
                "weighted_one_minus_support_mass": rebuilt["weighted_one_minus_support_mass"],
                "nonoptimal_mass_validation_residual": rebuilt["nonoptimal_mass_validation_residual"],
                "decomposition_available": rebuilt["decomposition_available"],
                "weighted_A": rebuilt.get("weighted_A"), "weighted_B": rebuilt.get("weighted_B"),
                "component_reconstruction_residual": rebuilt.get("component_reconstruction_residual"),
                "unavailable_states": rebuilt.get("unavailable_states", [])})
        comparisons = {}
        for earlier, later in zip(range(0, 3000, 100), range(100, 3001, 100)):
            label = f"{earlier}-{later}"
            comparisons[label] = study.statewise_transitions(states_by_update[earlier], states_by_update[later], label)
        comparisons["800-2000"] = study.statewise_transitions(states_by_update[800], states_by_update[2000], "800-2000")
        owner_summary = study.summarize_owner(points)
        owner_summary["statewise_nonoptimal_and_components"] = statewise_rows
        owner_summary["statewise_transitions"] = comparisons
        row = {"seed": seed, "mode": mode, "points": points,
            "summary": owner_summary, "statewise_800_2000": comparisons["800-2000"],
            "probe_updates": result["probe_updates"],
            "paired_batch_stream_sha256": result["paired_batch_stream_sha256"],
            "output_manifest_sha256": sha256(owner_path / "output-manifest.json"),
            "attempt_sha256": sha256(owner_path / "attempt.json"),
            "result_sha256": sha256(owner_path / "result.json"),
            "raw_detail_files": [f"{owner_path.name}/score-{p['update']:04d}.json" for p in points]}
        owners.append(row)
        by_seed.setdefault(seed, {})[mode] = result
    if (len(owners), reused, new, greedy, probes) != (4, 16, 108, 124, 14):
        raise RuntimeError("final audit cell counts do not match frozen scope")
    for seed in (2201, 2202):
        sm, sa = by_seed[seed]["softmax"], by_seed[seed]["schrodinger"]
        for key in ("input_ids", "config_hash", "shared_initial_digest", "bank", "source_hashes", "paired_batch_stream_sha256"):
            if sm.get(key) != sa.get(key):
                raise RuntimeError(f"final paired identity mismatch for seed {seed}: {key}")
    result = study.summarize_pairs(owners)
    result.update({"status": "COMPLETE", "inventory_sha256": decision["inventory_sha256"],
        "source_hashes": decision["source_hashes"], "historical_ledger_sha256": OLD_LEDGER_SHA,
        "counts": {"owners": 4, "checkpoints": 124, "new_proper_q": new,
            "reused_proper_q": reused, "greedy": greedy, "sa_probes": probes}})
    _durable(summary_path, result)
    return result


def _audit_worker(decision_path: Path, session_path: Path, nonce: str, summary_path: Path) -> None:
    decision, capability = _json(decision_path), _json(session_path)
    hashes = authority_hashes()
    if (capability.get("nonce") != nonce or capability.get("parent_pid") != os.getppid()
            or not LOCK.exists() or capability.get("decision_sha256") != sha256(decision_path)
            or capability.get("summary_path") != str(summary_path.resolve())
            or capability.get("source_hashes") != hashes or decision.get("source_hashes") != hashes
            or capability.get("ledger_sha256") != ledger_eof()
            or decision.get("ledger_sha256") != capability.get("ledger_sha256")):
        raise PermissionError("audit child capability/source/ledger mismatch")
    _review_ok(decision, hashes)
    if decision.get("kind") != "audit" or decision.get("stage") != "D":
        raise PermissionError("audit worker requires exact D decision")
    _audit_work(decision, summary_path)


def _run_audit(decision_path: Path, decision: dict) -> None:
    if decision.get("stage") != "D" or decision.get("envelope_seconds") != 240.0:
        raise RuntimeError("fixed D audit envelope required")
    if any(not _owner_path(seed, mode).is_dir() for seed, mode in ORDER):
        raise RuntimeError("all four production owners must complete before audit")
    started = time.monotonic()
    if __import__("shutil").disk_usage(HERE).free < MIN_FREE:
        raise RuntimeError("less than two GiB free")
    _reserve(decision, "D", 240.0)
    summary_path = ATTEMPTS / "final-paired-summary.json"
    if summary_path.exists() or (ATTEMPTS / "audit-terminal.json").exists():
        raise RuntimeError("final audit already has durable history")
    session = ATTEMPTS / ("driver-audit-" + str(uuid.uuid4()))
    session.mkdir(parents=True, exist_ok=False)
    nonce, charge_id = uuid.uuid4().hex, str(uuid.uuid4())
    session_file = session / "session.json"
    capability = {"nonce": nonce, "parent_pid": os.getpid(),
        "decision_sha256": sha256(decision_path), "ledger_sha256": decision["ledger_sha256"],
        "source_hashes": decision["source_hashes"],
        "summary_path": str(summary_path.resolve())}
    _durable(session_file, capability)
    argv = [sys.executable, "-m", "execution.early_learning.command", "--audit-worker",
        "--decision", str(decision_path.resolve()), "--session", str(session_file.resolve()),
        "--nonce", nonce, "--summary", str(summary_path.resolve())]
    cleanup = accounted = terminal = False
    terminal_state = {"uncertain": False}
    charge_row = None
    prior_handler = signal.getsignal(signal.SIGTERM)
    try:
        signal.signal(signal.SIGTERM, _interrupt)
        child = watchdog.supervise(argv, WORKSPACE, session, started + 240.0 - ALLOWANCE)
        cleanup = child.get("cleanup_verified") is True
        ext = max(time.monotonic() - started + ALLOWANCE, 0.0)
        success = child.get("exit_code") == 0 and not child.get("timed_out") and cleanup and ext <= 240.0
        charge_row = {"entry_id": charge_id, "recorded_at_utc": datetime.now(timezone.utc).isoformat(),
            "kind": "inference_audit", "stage": "D", "status": "COMPLETE" if success else "FAILED",
            "charged_seconds": ext, "external_seconds": ext, "output": str(summary_path),
            "driver_session": str(session)}
        if success and not summary_path.is_file():
            success = False
            charge_row["status"] = "FAILED"
        accounted = _append_once_certain(charge_row)
        if not accounted:
            raise RuntimeError("D-stage charge uncertain; reservation retained")
        terminal = _durable_certain(ATTEMPTS / "audit-terminal.json", {"status": "COMPLETE" if success else "FAILED",
            "entry_id": charge_id, "charged_seconds": ext, "cleanup_verified": cleanup,
            "summary_sha256": sha256(summary_path) if summary_path.is_file() else None,
            "historical_ledger_sha256": OLD_LEDGER_SHA}, terminal_state)
        if not terminal:
            raise RuntimeError("D-stage terminal uncertain; reservation retained")
        if not success:
            raise RuntimeError("D-stage audit worker failed or exceeded its external deadline")
        print(json.dumps({"status": "COMPLETE", "summary": str(summary_path)}, sort_keys=True))
    except BaseException as error:
        if not accounted:
            if charge_row is None:
                ext = max(time.monotonic() - started + ALLOWANCE, 0.0)
                charge_row = {"entry_id": charge_id, "recorded_at_utc": datetime.now(timezone.utc).isoformat(),
                    "kind": "inference_audit", "stage": "D", "status": "FAILED",
                    "charged_seconds": ext, "external_seconds": ext, "output": str(summary_path),
                    "driver_session": str(session), "error": repr(error)}
            accounted = _append_once_certain(charge_row)
        if not terminal:
            terminal = _durable_certain(ATTEMPTS / "audit-terminal.json", {"status": "FAILED_DRIVER",
                "entry_id": charge_id, "error": repr(error), "accounting_resolved": accounted,
                "cleanup_verified": cleanup}, terminal_state)
        raise
    finally:
        signal.signal(signal.SIGTERM, prior_handler)
        if accounted and cleanup and terminal:
            LOCK.unlink(missing_ok=True)


def _append_overhead(owner: Path, session: Path, external: float, owner_charge: float,
                     entry_id: str) -> bool:
    overhead = max(0.0, external - owner_charge)
    rows = _snapshot()[1]
    prior = [row for row in rows if row.get("kind") == "driver_overhead" and
             row.get("owner_output") == str(owner) and row.get("driver_session") == str(session)]
    if len(prior) > 1:
        raise RuntimeError("duplicate driver overhead rows")
    if prior:
        expected = {"entry_id": entry_id, "kind": "driver_overhead", "stage": "B",
            "status": "ACCOUNTED", "charged_seconds": overhead, "external_seconds": external,
            "owner_charge_seconds": owner_charge, "owner_output": str(owner),
            "output": str(owner), "driver_session": str(session)}
        if any(prior[0].get(key) != value for key, value in expected.items()):
            raise RuntimeError("driver overhead reconciliation mismatch")
    elif overhead:
        row = {"entry_id": entry_id, "recorded_at_utc": datetime.now(timezone.utc).isoformat(),
            "kind": "driver_overhead", "stage": "B", "status": "ACCOUNTED",
            "charged_seconds": overhead, "external_seconds": external,
            "owner_charge_seconds": owner_charge, "owner_output": str(owner),
            "output": str(owner), "driver_session": str(session)}
        return _append_once_certain(row)
    return True


def _owner_charge(owner: Path) -> tuple[dict | None, str | None]:
    rows = _snapshot()[1]
    artifacts = [_json(path) for path in (owner / "attempt.pending.json", owner / "attempt.json") if path.is_file()]
    ids = {item.get("entry_id") for item in artifacts if isinstance(item.get("entry_id"), str)}
    charges = [row for row in rows if row.get("kind") == "attempt_charge" and row.get("stage") == "B" and row.get("output") == str(owner)]
    if len(ids) > 1 or len(charges) > 1 or (charges and (len(ids) != 1 or charges[0].get("entry_id") not in ids)):
        raise RuntimeError("owner accounting identity ambiguous")
    return (charges[0], next(iter(ids))) if charges else (None, next(iter(ids)) if len(ids) == 1 else None)


def _validate_complete(owner: Path, seed: int, mode: str, inventory_sha: str,
                       *, fixture_updates: tuple[int, ...] | None = None) -> dict:
    attempt, result, index, manifest = (_json(owner / name) for name in
        ("attempt.json", "result.json", "index.json", "output-manifest.json"))
    if attempt.get("status") != "COMPLETE" or result.get("status") != "COMPLETE" or attempt.get("entry_id") != result.get("attempt_entry_id"):
        raise RuntimeError("owner terminal is not complete")
    if (result.get("seed"), result.get("mode"), result.get("updates"), result.get("inventory_sha256")) != (seed, mode, 3000, inventory_sha):
        raise RuntimeError("owner result identity mismatch")
    if index.get("status") != "COMPLETE" or index.get("result_sha256") != sha256(owner / "result.json"):
        raise RuntimeError("owner index binding mismatch")
    points = result.get("points")
    expected_points = list(range(0, 3001, 100)) if fixture_updates is None else list(fixture_updates)
    if not isinstance(points, list) or [point.get("update") for point in points] != expected_points:
        raise RuntimeError("owner missing one or more required score cells")
    refs = index.get("points")
    if not isinstance(refs, list) or len(refs) != len(expected_points):
        raise RuntimeError("owner index lacks expected point files")
    for ref in refs:
        path = owner / ref["path"]
        if not path.is_file() or sha256(path) != ref.get("sha256"):
            raise RuntimeError("per-checkpoint score file hash mismatch")
    actual = {str(path.relative_to(owner)): sha256(path) for path in owner.rglob("*")
              if path.is_file() and path.name != "output-manifest.json"}
    if set(actual) != set(manifest) or any(manifest[key].get("sha256") != value for key, value in actual.items()):
        raise RuntimeError("owner output manifest mismatch")
    if result.get("probe_updates") != list(PROBE_UPDATES if mode == "schrodinger" else ()):
        raise RuntimeError("owner local-probe checkpoint set mismatch")
    return result


PROBE_UPDATES = [0, 500, 1000, 1500, 2000, 2500, 3000]


def _interrupt(signum, frame):
    raise InterruptedError("driver interruption requested")


def run_decision(decision_path: Path, *, _fixture: dict | None = None) -> None:
    started = time.monotonic()
    decision = _json(decision_path)
    kind = decision.get("kind")
    if kind in ("smoke", "suite"):
        _run_check(decision_path, decision)
        return
    if kind == "audit":
        _run_audit(decision_path, decision)
        return
    if kind != "production":
        raise RuntimeError("unknown early-learning decision kind")
    seed, mode = decision.get("seed"), decision.get("mode")
    if (seed, mode) not in ORDER or decision.get("stage") != "B" or decision.get("updates") != 3000:
        raise RuntimeError("invalid owner identity")
    envelope = ENVELOPES[mode]
    if decision.get("envelope_seconds") != envelope:
        raise RuntimeError("owner envelope differs from frozen mode envelope")
    expected = [sys.executable, "-m", "execution.early_learning.study",
        "--decision", str(decision_path.resolve()), "--session", "SESSION", "--nonce", "NONCE"]
    # The two placeholders are replaced with the exact durable capability path
    # and random nonce after the reservation is acquired.
    if decision.get("cwd") != str(WORKSPACE) or decision.get("argv_template") != expected:
        raise RuntimeError("owner argv/cwd is not exact")
    if time.time() > decision.get("expires_unix", 0):
        raise RuntimeError("owner decision expired")
    _expected_order(seed, mode)
    if __import__("shutil").disk_usage(HERE).free < MIN_FREE:
        raise RuntimeError("less than two GiB free")
    if decision.get("owner_inventory_entry", {}).get("seed") != seed or decision.get("owner_inventory_entry", {}).get("mode") != mode:
        raise RuntimeError("owner inventory decision mismatch")
    if decision.get("owner_inventory_entry") != _inventory_entry(seed, mode):
        raise RuntimeError("decision does not bind exact original inventory owner")
    _reserve(decision, "B", envelope)
    session = ATTEMPTS / ("driver-" + str(uuid.uuid4()))
    session.mkdir(parents=True, exist_ok=False)
    nonce = uuid.uuid4().hex
    session_file = session / "session.json"
    child_argv = [sys.executable, "-m", "execution.early_learning.study",
        "--decision", str(decision_path.resolve()), "--session", str(session_file.resolve()), "--nonce", nonce]
    deadline = started + envelope - ALLOWANCE
    capability = {"nonce": nonce, "decision_sha256": sha256(decision_path),
        "decision_path": str(decision_path.resolve()), "parent_pid": os.getpid(),
        "seed": seed, "mode": mode, "stage": "B", "ledger_sha256": decision["ledger_sha256"],
        "inventory_sha256": decision["inventory_sha256"], "source_hashes": decision["source_hashes"],
        "review": decision["review"], "deadline_monotonic": deadline, "argv": child_argv}
    _durable(session_file, capability)
    _durable(session / "start.json", {"pid": os.getpid(), "argv": child_argv,
        "decision": str(decision_path.resolve()), "started_monotonic": started,
        "ledger_sha256": decision["ledger_sha256"], "source_hashes": decision["source_hashes"]})
    cleanup = accounted = terminal = False
    terminal_state = {"uncertain": False}
    owner = _owner_path(seed, mode)
    fallback_id, overhead_id = str(uuid.uuid4()), str(uuid.uuid4())
    fallback_row = None
    prior_handler = signal.getsignal(signal.SIGTERM)
    try:
        signal.signal(signal.SIGTERM, _interrupt)
        child = watchdog.supervise(child_argv, WORKSPACE, session, deadline)
        _durable(session / "child-terminal.json", child)
        cleanup = child.get("cleanup_verified") is True
        ext = max(time.monotonic() - started + ALLOWANCE, 0.0)
        owner_charge, owner_id = _owner_charge(owner)
        if owner_charge is None:
            fallback_row = {"entry_id": fallback_id, "recorded_at_utc": datetime.now(timezone.utc).isoformat(),
                "kind": "watchdog_uncertain_fallback", "stage": "B", "status": "UNCERTAIN_FAILURE",
                "charged_seconds": ext, "external_seconds": ext, "output": str(owner),
                "driver_session": str(session)}
            accounted = _append_once_certain(fallback_row)
            if not accounted:
                raise RuntimeError("fallback charge uncertain; reservation retained")
            raise RuntimeError("no unique owner charge; charged external fallback")
        if owner_id != owner_charge.get("entry_id"):
            raise RuntimeError("owner terminal UUID differs from its ledger charge")
        ext = max(ext, float(owner_charge["charged_seconds"]))
        accounted = _append_overhead(owner, session, ext, float(owner_charge["charged_seconds"]), overhead_id)
        if not accounted:
            raise RuntimeError("owner overhead charge uncertain; reservation retained")
        if child.get("exit_code") != 0 or child.get("timed_out") or not cleanup:
            raise RuntimeError("study child failed or cleanup was not proven")
        if ext > envelope:
            raise RuntimeError("external owner envelope exceeded")
        if sha256(OLD_LEDGER) != OLD_LEDGER_SHA:
            raise RuntimeError("historical ledger changed during owner")
        _validate_complete(owner, seed, mode, decision["inventory_sha256"],
            fixture_updates=None if _fixture is None else tuple(_fixture["updates"]))
        terminal = _durable_certain(session / "terminal.json", {"status": "COMPLETE", "charged_seconds": ext,
            "owner_charge_seconds": owner_charge["charged_seconds"], "cleanup_verified": cleanup,
            "overhead_entry_id": overhead_id}, terminal_state)
        if not terminal:
            raise RuntimeError("driver terminal uncertain; reservation retained")
        print(json.dumps({"status": "COMPLETE", "session": str(session)}, sort_keys=True))
    except BaseException as error:
        if not accounted:
            try:
                ext = max(time.monotonic() - started + ALLOWANCE, 0.0)
                owner_charge, owner_id = _owner_charge(owner)
                if owner_charge is None:
                    if fallback_row is None:
                        fallback_row = {"entry_id": fallback_id, "recorded_at_utc": datetime.now(timezone.utc).isoformat(),
                        "kind": "watchdog_uncertain_fallback", "stage": "B", "status": "UNCERTAIN_FAILURE",
                        "charged_seconds": ext, "external_seconds": ext, "output": str(owner),
                        "driver_session": str(session), "error": repr(error)}
                    accounted = _append_once_certain(fallback_row)
                else:
                    ext = max(ext, float(owner_charge["charged_seconds"]))
                    accounted = _append_overhead(owner, session, ext, float(owner_charge["charged_seconds"]), overhead_id)
            except BaseException:
                accounted = False
        if not terminal:
            terminal = _durable_certain(session / "terminal.json", {"status": "FAILED_DRIVER", "error": repr(error),
                "charged_seconds": max(time.monotonic() - started + ALLOWANCE, 0.0),
                "cleanup_verified": cleanup, "accounting_resolved": accounted,
                "fallback_entry_id": fallback_id, "overhead_entry_id": overhead_id}, terminal_state)
        raise
    finally:
        signal.signal(signal.SIGTERM, prior_handler)
        if accounted and cleanup and terminal:
            LOCK.unlink(missing_ok=True)


def main(argv=None) -> None:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--decision", type=Path)
    group.add_argument("--initialize-ledger", action="store_true")
    parser.add_argument("--audit-worker", action="store_true")
    parser.add_argument("--session", type=Path)
    parser.add_argument("--nonce")
    parser.add_argument("--summary", type=Path)
    args = parser.parse_args(argv)
    if args.audit_worker:
        if not all((args.decision, args.session, args.nonce, args.summary)):
            parser.error("audit worker requires decision, session, nonce, and summary")
        _audit_worker(args.decision, args.session, args.nonce, args.summary)
    elif args.initialize_ledger:
        initialize_ledger()
    else:
        run_decision(args.decision)


if __name__ == "__main__":
    main()
