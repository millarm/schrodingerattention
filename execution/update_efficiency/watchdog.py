"""Study-local stdlib process-group supervisor with auditable Darwin fallback."""
from __future__ import annotations

import errno
import json
import os
from pathlib import Path
import platform
import signal
import subprocess
import time


def _remaining(deadline: float) -> float:
    value = deadline - time.monotonic()
    if value <= 0:
        raise TimeoutError("process cleanup deadline exhausted")
    return value


def _kill_and_reap_helper(helper, deadline: float) -> None:
    if helper.poll() is None:
        helper.kill()
    remaining = max(0.0, deadline - time.monotonic())
    try:
        helper.communicate(timeout=remaining)
    except subprocess.TimeoutExpired as error:
        raise TimeoutError("Darwin process-table helper could not be reaped by deadline") from error
    if helper.poll() is None:
        raise TimeoutError("Darwin process-table helper reap is unconfirmed")


def _darwin_group_snapshot(pgid: int, deadline: float) -> dict:
    """Return a validated complete ps snapshot; uncertainty always raises."""
    _remaining(deadline)
    helper = subprocess.Popen(
        ["/bin/ps", "-axo", "pid=,pgid="], stdout=subprocess.PIPE,
        stderr=subprocess.PIPE, start_new_session=True)
    try:
        remaining = _remaining(deadline)
        reap_reserve = min(0.1, remaining * 0.2)
        probe_timeout = remaining - reap_reserve
        if probe_timeout <= 0:
            raise TimeoutError("insufficient deadline for bounded process-table probe and reap")
        try:
            out, err = helper.communicate(timeout=probe_timeout)
        except subprocess.TimeoutExpired as error:
            _kill_and_reap_helper(helper, deadline)
            raise TimeoutError("Darwin process-table probe timed out") from error
        _remaining(deadline)
        if helper.returncode != 0:
            raise RuntimeError("Darwin process-table probe failed")
        if not out or not out.endswith(b"\n") or err:
            raise RuntimeError("empty or diagnostic Darwin process-table snapshot")
        rows = []
        pids = set()
        for raw in out.splitlines():
            fields = raw.split()
            if len(fields) != 2 or any(not field.isdigit() for field in fields):
                raise RuntimeError("malformed Darwin process-table row")
            pid, row_pgid = map(int, fields)
            if pid <= 0 or row_pgid <= 0 or pid in pids:
                raise RuntimeError("invalid or duplicate Darwin process-table identity")
            pids.add(pid)
            rows.append((pid, row_pgid))
        own_pid, own_pgid = os.getpid(), os.getpgrp()
        if not rows or not any(pid == own_pid and row_pgid == own_pgid for pid, row_pgid in rows):
            raise RuntimeError("Darwin process-table visibility check failed")
        members = [pid for pid, row_pgid in rows if row_pgid == pgid]
        _remaining(deadline)
        return {"method": "darwin_ps", "pgid": pgid, "member_pids": members,
                "row_count": len(rows), "own_pid": own_pid, "own_pgid": own_pgid,
                "stdout": out.decode("ascii", errors="strict"),
                "stderr": err.decode("ascii", errors="strict")}
    finally:
        if helper.poll() is None:
            _kill_and_reap_helper(helper, deadline)


def _group_probe(pgid: int, deadline: float) -> tuple[bool, dict]:
    _remaining(deadline)
    try:
        os.killpg(pgid, 0)
        return False, {"method": "killpg_zero", "pgid": pgid, "present": True}
    except ProcessLookupError:
        return True, {"method": "killpg_zero_esrch", "pgid": pgid, "present": False}
    except PermissionError as error:
        if error.errno != errno.EPERM or platform.system() != "Darwin":
            raise RuntimeError("process-group absence cannot be proven") from error
        snapshot = _darwin_group_snapshot(pgid, deadline)
        gone = not snapshot["member_pids"]
        snapshot["present"] = not gone
        return gone, snapshot


def group_gone(pgid: int, deadline: float | None = None) -> bool:
    """Compatibility helper: verify absence with the same strict probe."""
    end = time.monotonic() + 2.0 if deadline is None else deadline
    return _group_probe(pgid, end)[0]


def _signal_group(pgid: int, sig: int, deadline: float) -> dict:
    _remaining(deadline)
    try:
        os.killpg(pgid, sig)
        return {"method": "killpg_signal", "pgid": pgid, "signal": sig,
            "result": "sent"}
    except ProcessLookupError:
        return {"method": "killpg_signal", "pgid": pgid, "signal": sig,
                "result": "esrch_race"}
    except PermissionError as error:
        if error.errno != errno.EPERM:
            raise
        gone, proof = _group_probe(pgid, deadline)
        if gone:
            return {"method": "killpg_signal", "pgid": pgid, "signal": sig,
                    "result": "eperm_after_exit", "absence_proof": proof}
        raise RuntimeError("permission denied signaling a live owned process group") from error


def _save_evidence(logs: Path, evidence: list[dict]) -> None:
    path = logs / "cleanup-evidence.jsonl"
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(evidence[-1], sort_keys=True, allow_nan=False) + "\n")
        handle.flush()
        os.fsync(handle.fileno())


def supervise(command, cwd, logs, deadline):
    """Own one fresh process group and include termination grace in deadline."""
    logs = Path(logs)
    logs.mkdir(parents=True, exist_ok=True)
    child = None
    cleanup = False
    timed_out = False
    evidence = []
    with (logs / "stdout.txt").open("wb") as out, (logs / "stderr.txt").open("wb") as err:
        try:
            _remaining(deadline)
            child = subprocess.Popen(command, cwd=cwd, stdout=out, stderr=err,
                                     start_new_session=True)
            remaining = _remaining(deadline)
            grace = min(2.0, remaining * 0.2)
            try:
                child.wait(timeout=max(0.001, remaining - grace))
            except subprocess.TimeoutExpired:
                timed_out = True
            gone, proof = _group_probe(child.pid, deadline)
            evidence.append(proof)
            _save_evidence(logs, evidence)
            if not gone:
                evidence.append(_signal_group(child.pid, signal.SIGTERM, deadline))
                _save_evidence(logs, evidence)
                term_end = min(deadline, time.monotonic() + grace / 2)
                while time.monotonic() < term_end:
                    child.poll()
                    gone, proof = _group_probe(child.pid, deadline)
                    evidence.append(proof)
                    _save_evidence(logs, evidence)
                    if gone:
                        break
                    time.sleep(min(0.01, _remaining(deadline)))
                if not gone:
                    evidence.append(_signal_group(child.pid, signal.SIGKILL, deadline))
                    _save_evidence(logs, evidence)
                while not gone:
                    child.poll()
                    gone, proof = _group_probe(child.pid, deadline)
                    evidence.append(proof)
                    _save_evidence(logs, evidence)
                    if not gone:
                        time.sleep(min(0.01, _remaining(deadline)))
            remaining = _remaining(deadline)
            if child.poll() is None:
                child.wait(timeout=remaining)
            gone, proof = _group_probe(child.pid, deadline)
            evidence.append(proof)
            _save_evidence(logs, evidence)
            cleanup = gone and child.returncode is not None
            if not cleanup:
                raise RuntimeError("process group cleanup/reap not verified")
            out.flush(); os.fsync(out.fileno())
            err.flush(); os.fsync(err.fileno())
            _remaining(deadline)
            return {"child_pid": child.pid, "exit_code": child.returncode,
                    "timed_out": timed_out, "cleanup_verified": True,
                    "cleanup_evidence": evidence}
        except BaseException:
            original = __import__("sys").exc_info()
            if child is not None and not cleanup:
                try:
                    # Best-effort emergency signal remains scoped to the new
                    # session's owned group even after its success deadline.
                    os.killpg(child.pid, signal.SIGKILL)
                except BaseException as cleanup_error:
                    evidence.append({"method": "defensive_cleanup", "error": repr(cleanup_error),
                                     "cleanup_verified": False})
                try:
                    if child.poll() is None and time.monotonic() < deadline:
                        child.wait(timeout=max(0.0, deadline - time.monotonic()))
                    if time.monotonic() < deadline:
                        gone, proof = _group_probe(child.pid, deadline)
                        evidence.append(proof)
                        cleanup = gone and child.returncode is not None
                except BaseException as cleanup_error:
                    evidence.append({"method": "defensive_reap_or_probe", "error": repr(cleanup_error),
                                     "cleanup_verified": False})
            try:
                for row in evidence:
                    _save_evidence(logs, [row])
                out.flush(); os.fsync(out.fileno())
                err.flush(); os.fsync(err.fileno())
            except BaseException:
                pass
            raise original[1].with_traceback(original[2])
