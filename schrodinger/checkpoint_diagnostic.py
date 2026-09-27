"""Additive locked diagnostic of retained Schrödinger checkpoints.

The trace is deliberately reconstructed from the public model modules: no
hooks, training, or retained artifact is mutated.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import os
import platform
import signal
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import torch
from torch import Tensor
from torch.nn import functional as F

from .attention import attention_from_scores
from .data import Batch, COPY, XOR, validate_batch
from .experiment import CONFIG_PATH, ROOT, config, load_evaluation_data, source_hashes
from .model import TinyClassifier

SEEDS = (11, 22, 33)
CAP_SECONDS, RESERVE_SECONDS = 900.0, 30.0
LEDGER = ROOT / "execution" / "diagnostics" / "ledger.jsonl"
REJECTIONS = ROOT / "execution" / "diagnostics" / "rejections"
STARTUP_ALLOWANCE_SECONDS = 2.0


class DiagnosticTimeout(RuntimeError):
    """Raised by the main-thread real elapsed watchdog."""


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def total_variation(a: Tensor, b: Tensor) -> Tensor:
    return .5 * (a - b).abs().sum(-1)


def rms_change(value: Tensor, reference: Tensor) -> dict[str, Tensor]:
    absolute = (value - reference).square().mean(-1).sqrt()
    ref = reference.square().mean(-1).sqrt()
    return {"absolute": absolute, "reference": ref, "relative": absolute / ref.clamp_min(1e-8)}


def quantiles(values: Tensor) -> dict[str, float]:
    flat = values.detach().flatten().float()
    return {"mean": float(flat.mean()), "median": float(flat.quantile(.5)), "p90": float(flat.quantile(.9)), "p95": float(flat.quantile(.95)), "p99": float(flat.quantile(.99)), "max": float(flat.max()), "fraction_ge_001": float((flat >= .01).float().mean()), "fraction_ge_005": float((flat >= .05).float().mean())}


def _finite(name: str, value: Tensor | np.ndarray) -> None:
    array = value.detach().cpu().numpy() if isinstance(value, Tensor) else value
    if not np.isfinite(array).all(): raise FloatingPointError(f"nonfinite {name}")


def _probability_checks(name: str, value: Tensor) -> None:
    _finite(name, value)
    if (value < -2e-4).any() or (value > 1.0002).any(): raise FloatingPointError(f"{name} outside probability bounds")
    if (value.sum(-1).sub(1).abs() > 2e-4).any(): raise FloatingPointError(f"{name} row-sum violation")


def _tv_checks(value: Tensor) -> None:
    _finite("TV", value)
    if (value < -2e-4).any() or (value > 1.0002).any(): raise FloatingPointError("TV outside [0, 1]")


def direct(scores: Tensor, values: Tensor, phase: Tensor, dt: Tensor) -> dict[str, Tensor]:
    evolved, a = attention_from_scores(scores, values, phase, dt, "schrodinger")
    soft, p = attention_from_scores(scores, values, mode="softmax")
    return {"attention": a, "softmax": p, "evolved": evolved, "soft_value": soft, "tv": total_variation(a, p), "key_max": (a-p).abs().amax(-1), "value_rms": rms_change(evolved, soft)}


def _split(attention: Any, x: Tensor) -> tuple[Tensor, Tensor, Tensor, Tensor]:
    batch, length, _ = x.shape
    def split(z: Tensor) -> Tensor:
        return z.reshape(batch, length, attention.num_heads, attention.head_dim).transpose(1, 2)
    q, k, v = (split(proj(x)) for proj in (attention.q_proj, attention.k_proj, attention.v_proj))
    return q, k, v, q @ k.transpose(-2, -1) / math.sqrt(attention.head_dim)


def _project(attention: Any, value: Tensor) -> Tensor:
    return attention.out_proj(value.transpose(1, 2).reshape(value.shape[0], value.shape[2], attention.d_model))


def _phase_dt(scores: Tensor, attention: Any, *, zero: bool) -> tuple[Tensor, Tensor]:
    gamma = attention.effective_gamma().reshape(1, attention.num_heads, 1, 1)
    dt = torch.zeros_like(gamma) if zero else attention.effective_dt().reshape(1, attention.num_heads, 1, 1)
    return gamma * scores, dt


def _scale(scores: Tensor, dt: Tensor) -> tuple[Tensor, Tensor]:
    h = .5 * (scores + scores.transpose(-2, -1)) / math.sqrt(scores.shape[-1])
    eig = torch.linalg.eigvalsh(h.float())
    scalar = dt.abs().squeeze(-1).squeeze(-1)
    return scalar * eig.abs().amax(-1), scalar * h.square().sum((-2, -1)).sqrt() / math.sqrt(scores.shape[-1])


def trace_model(model: TinyClassifier, tokens: Tensor, *, dt_zero: bool = False) -> dict[str, Any]:
    """Manual complete path.  Callers assert its logits equal the model API."""
    if model.mode != "schrodinger":
        raise ValueError("only retained schrodinger checkpoints are in scope")
    model.eval()
    x = model.token_embedding(tokens) + model.positional(tokens.shape[1], tokens.device, model.token_embedding.weight.dtype)
    layers: list[dict[str, Tensor]] = []
    with torch.no_grad():
        for layer in model.layers:
            normalized = layer.norm1(x)
            _, _, values, scores = _split(layer.attention, normalized)
            phase, dt = _phase_dt(scores, layer.attention, zero=dt_zero)
            output, attention, diagnostics = attention_from_scores(scores, values, phase, dt, "schrodinger", return_diagnostics=True)
            # Fixed-input local comparison always uses the normal phase/time and
            # therefore shares exactly this normal path's normalized x, S, V.
            normal_phase, normal_dt = _phase_dt(scores, layer.attention, zero=False)
            local = direct(scores, values, normal_phase, normal_dt)
            _probability_checks("evolved attention", attention); _probability_checks("local attention", local["attention"]); _probability_checks("local softmax", local["softmax"]); _tv_checks(local["tv"])
            local_projected = rms_change(_project(layer.attention, local["evolved"]), _project(layer.attention, local["soft_value"]))
            attended = _project(layer.attention, output)
            post_attention = x + attended
            hidden = post_attention + layer.feedforward(layer.norm2(post_attention))
            opnorm, eigenphase = _scale(scores, normal_dt)
            phase_dispersion = 1 - (torch.softmax(scores, -1) * torch.exp(1j * normal_phase)).sum(-1).abs()
            layers.append({"normalized_input": normalized, "scores": scores, "values": values, "attention": attention, "projected": attended, "hidden": hidden, "local_attention": local["attention"], "local_softmax": local["softmax"], "local_tv": local["tv"], "local_key_max": local["key_max"], "local_value_abs": local["value_rms"]["absolute"], "local_value_reference": local["value_rms"]["reference"], "local_value_relative": local["value_rms"]["relative"], "local_projected_abs": local_projected["absolute"], "local_projected_reference": local_projected["reference"], "local_projected_relative": local_projected["relative"], "dt_h_operator": opnorm, "eigenphase_rms": eigenphase, "phase_dispersion": phase_dispersion, "hermiticity": torch.tensor(diagnostics.max_hermiticity_error), "unitarity": torch.tensor(diagnostics.max_unitarity_error), "row_error": torch.tensor(diagnostics.max_probability_row_error)})
            x = hidden
        logits = model.classifier(model.final_norm(x[:, 0]))
    _finite("diagnostic logits", logits)
    return {"layers": layers, "hidden": x, "logits": logits}


def _append_ledger(record: dict[str, Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    import fcntl
    with path.open("a") as handle:
        fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
        try: handle.write(json.dumps(record, sort_keys=True) + "\n"); handle.flush(); os.fsync(handle.fileno())
        finally: fcntl.flock(handle.fileno(), fcntl.LOCK_UN)


def _record_rejection(reason: str, output: Path, lock: Path, argv: list[str], *, started: float | None = None, ledger: Path = LEDGER) -> None:
    """Rejected preflight has no owned output/lock; record it elsewhere only."""
    elapsed=time.perf_counter()-(started if started is not None else time.perf_counter())
    record={"kind":"checkpoint_diagnostic_rejected","status":"rejected","reason":reason,"output":str(output),"lock":str(lock),"argv":argv,"executable":sys.executable,"pid":os.getpid(),"timestamp_utc":datetime.now(timezone.utc).isoformat(),"elapsed_seconds":elapsed,"startup_allowance_seconds":STARTUP_ALLOWANCE_SECONDS,"charged_seconds":STARTUP_ALLOWANCE_SECONDS+elapsed}
    REJECTIONS.mkdir(parents=True,exist_ok=True); destination=REJECTIONS/f"rejected-{os.getpid()}-{time.time_ns()}.json"; fd=os.open(destination,os.O_CREAT|os.O_EXCL|os.O_WRONLY)
    try: os.write(fd,json.dumps(record,sort_keys=True).encode())
    finally: os.close(fd)
    _append_ledger(record, ledger)


def _ledger_total(path: Path) -> float:
    if not path.exists(): return 0.0
    return sum(float(json.loads(line).get("charged_seconds", 0.0)) for line in path.read_text().splitlines() if line)


class Attempt:
    """Fresh output and atomic exclusive lock, with cleanup on every failure."""
    def __init__(self, output: Path, lock: Path, *, command: str = "checkpoint-diagnostic", argv: list[str] | None = None, command_started: float | None = None, deadline_seconds: float | None = None, ledger: Path = LEDGER) -> None:
        self.output, self.lock, self.command, self.ledger = output, lock, command, ledger
        self.argv=argv or [command]; self.command_started=command_started if command_started is not None else time.perf_counter(); self.deadline_seconds=deadline_seconds
        self.fd: int | None = None; self.started = 0.0; self.started_at = datetime.now(timezone.utc).isoformat(); self.prior_charged = _ledger_total(ledger)
        self.previous_handler: Any = None; self.previous_timer: tuple[float,float] | None = None
        self.output_owned = False
    def _arm_deadline(self) -> None:
        remaining=self.deadline_seconds if self.deadline_seconds is not None else CAP_SECONDS-self.prior_charged-STARTUP_ALLOWANCE_SECONDS-(time.perf_counter()-self.command_started)-RESERVE_SECONDS
        if remaining <= 0: raise DiagnosticTimeout("diagnostic deadline exhausted before work")
        if signal.getsignal(signal.SIGALRM) is not None:
            self.previous_handler=signal.getsignal(signal.SIGALRM); self.previous_timer=signal.setitimer(signal.ITIMER_REAL,0)
            def timeout(signum: int, frame: Any) -> None: raise DiagnosticTimeout("interrupting diagnostic elapsed deadline reached; partial output retained")
            signal.signal(signal.SIGALRM,timeout); signal.setitimer(signal.ITIMER_REAL,remaining)
    def _disarm_deadline(self) -> None:
        if self.previous_handler is not None:
            signal.setitimer(signal.ITIMER_REAL,0); signal.signal(signal.SIGALRM,self.previous_handler)
            if self.previous_timer and self.previous_timer[0]>0: signal.setitimer(signal.ITIMER_REAL,*self.previous_timer)
            self.previous_handler=None
    def _cleanup(self) -> None:
        """Only this instance's descriptor/lock are ever released."""
        try:
            if self.fd is not None: os.close(self.fd)
        finally:
            if self.fd is not None: self.lock.unlink(missing_ok=True)
            self.fd=None; self._disarm_deadline()
    def __enter__(self) -> "Attempt":
        if self.output.exists(): raise FileExistsError(f"diagnostic output already exists: {self.output}")
        self.lock.parent.mkdir(parents=True, exist_ok=True)
        try:
            self.fd = os.open(self.lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            os.write(self.fd, str(os.getpid()).encode())
            self.output.mkdir(parents=True, exist_ok=False)
            self.output_owned = True
            self.started = time.perf_counter()
            self._arm_deadline()
            return self
        except BaseException as error:
            try:
                if self.output_owned:
                    elapsed=time.perf_counter()-self.command_started; record={"kind":"checkpoint_diagnostic","status":"failed","command":self.command,"argv":self.argv,"executable":sys.executable,"lock":str(self.lock),"pid":os.getpid(),"started_at_utc":self.started_at,"ended_at_utc":datetime.now(timezone.utc).isoformat(),"prior_charged_seconds":self.prior_charged,"elapsed_seconds":elapsed,"startup_allowance_seconds":STARTUP_ALLOWANCE_SECONDS,"charged_seconds":STARTUP_ALLOWANCE_SECONDS+elapsed,"error":repr(error)}
                    try: (self.output/"attempt.json").write_text(json.dumps(record,indent=2,sort_keys=True))
                    except BaseException as write_error: _append_ledger({**record,"error":f"required attempt record write failed: {write_error!r}"},self.ledger); raise
                    else: _append_ledger(record,self.ledger)
                elif isinstance(error, FileExistsError):
                    _record_rejection(f"atomic acquisition race: {error}",self.output,self.lock,self.argv,started=self.command_started,ledger=self.ledger)
            finally:
                self._cleanup()
            raise
    def guard(self) -> None:
        if self.prior_charged + STARTUP_ALLOWANCE_SECONDS + time.perf_counter() - self.command_started + RESERVE_SECONDS >= CAP_SECONDS:
            raise RuntimeError("diagnostic 900-second cap reserve reached; partial output retained")
    def __exit__(self, typ: Any, value: BaseException | None, trace: Any) -> None:
        elapsed=time.perf_counter()-self.command_started
        charged=STARTUP_ALLOWANCE_SECONDS+elapsed
        record = {"kind": "checkpoint_diagnostic", "status": "failed" if typ else "success", "command": self.command,"argv":self.argv,"executable":sys.executable,"lock":str(self.lock), "pid": os.getpid(), "started_at_utc":self.started_at,"ended_at_utc":datetime.now(timezone.utc).isoformat(),"prior_charged_seconds":self.prior_charged,"elapsed_seconds": elapsed,"startup_allowance_seconds":STARTUP_ALLOWANCE_SECONDS, "charged_seconds": charged, "cumulative_seconds":self.prior_charged+charged,"error": None if value is None else repr(value)}
        try:
            try:
                (self.output / "attempt.json").write_text(json.dumps(record, indent=2, sort_keys=True))
            except BaseException as write_error:
                failed={**record,"status":"failed","error":f"required attempt record write failed: {write_error!r}"}
                _append_ledger(failed, self.ledger)
                raise
            else:
                _append_ledger(record, self.ledger)
        finally:
            self._cleanup()


ROW_KEYS = ("seed","condition","sample","operation","label","layer","head","query","local_tv","local_key_max","local_value_abs","local_value_reference","local_value_relative","local_projected_abs","local_projected_reference","local_projected_relative","propagated_tv","propagated_hidden_abs","propagated_hidden_relative","propagated_normalized_input_abs","dt_h_operator","eigenphase_rms","phase_dispersion","effective_dt","effective_gamma")
EXAMPLE_KEYS = ("seed","condition","sample","operation","label","normal_logit0","normal_logit1","dt0_logit0","dt0_logit1","normal_prob1","dt0_prob1","normal_loss","dt0_loss","normal_prediction","dt0_prediction","normal_correct","dt0_correct","disagreement","probability_abs_change","margin_abs_change","loss_benefit","absolute_loss_change")


def trace_batch(seed: int, condition: str, batch: Batch, model: TinyClassifier, attempt: Attempt | None = None) -> tuple[dict[str,list[Any]], dict[str,list[Any]], dict[str,float]]:
    rows = {key: [] for key in ROW_KEYS}; examples = {key: [] for key in EXAMPLE_KEYS}; numerical = {"max_hermiticity":0.,"max_unitarity":0.,"max_row_error":0.}
    for start in range(0, len(batch.labels), 64):
        if attempt: attempt.guard()
        stop = min(start+64, len(batch.labels)); tokens = torch.from_numpy(batch.tokens[start:stop]); labels = torch.from_numpy(batch.labels[start:stop])
        with torch.no_grad():
            normal, zero = trace_model(model, tokens), trace_model(model, tokens, dt_zero=True)
            torch.testing.assert_close(normal["logits"], model(tokens), atol=2e-6, rtol=2e-5)
            torch.testing.assert_close(zero["logits"], model(tokens, dt_override=0.), atol=2e-6, rtol=2e-5)
            torch.testing.assert_close(normal["layers"][0]["normalized_input"], zero["layers"][0]["normalized_input"], atol=2e-6, rtol=2e-5)
        probs, zprobs = normal["logits"].softmax(-1), zero["logits"].softmax(-1)
        _probability_checks("normal output probabilities", probs); _probability_checks("dt0 output probabilities", zprobs)
        loss, zloss = F.cross_entropy(normal["logits"], labels, reduction="none"), F.cross_entropy(zero["logits"], labels, reduction="none")
        for i in range(stop-start):
            j = start+i; base = (seed,condition,j,int(batch.operations[j]),int(batch.labels[j]))
            metrics = (normal["logits"][i,0],normal["logits"][i,1],zero["logits"][i,0],zero["logits"][i,1],probs[i,1],zprobs[i,1],loss[i],zloss[i],normal["logits"][i].argmax(),zero["logits"][i].argmax(),normal["logits"][i].argmax()==labels[i],zero["logits"][i].argmax()==labels[i],normal["logits"][i].argmax()!=zero["logits"][i].argmax(),(probs[i,1]-zprobs[i,1]).abs(),((normal["logits"][i,1]-normal["logits"][i,0])-(zero["logits"][i,1]-zero["logits"][i,0])).abs(),zloss[i]-loss[i],(zloss[i]-loss[i]).abs())
            for key, value in zip(EXAMPLE_KEYS, base+tuple(float(x) for x in metrics), strict=True): examples[key].append(value)
        for li,(n,z) in enumerate(zip(normal["layers"],zero["layers"],strict=True)):
            propagated_tv = total_variation(n["attention"],z["attention"]); hidden=rms_change(n["hidden"],z["hidden"]); input_change=rms_change(n["normalized_input"],z["normalized_input"])["absolute"]
            _probability_checks("propagated normal attention", n["attention"]); _probability_checks("propagated dt0 attention", z["attention"]); _tv_checks(propagated_tv)
            dt_cache=model.layers[li].attention.effective_dt().detach().cpu().tolist(); gamma_cache=model.layers[li].attention.effective_gamma().detach().cpu().tolist()
            numerical["max_hermiticity"] = max(numerical["max_hermiticity"],float(n["hermiticity"])); numerical["max_unitarity"] = max(numerical["max_unitarity"],float(n["unitarity"])); numerical["max_row_error"] = max(numerical["max_row_error"],float(n["row_error"]))
            for i in range(stop-start):
                j=start+i
                for h in range(n["attention"].shape[1]):
                    for q in range(n["attention"].shape[2]):
                        values=(seed,condition,j,int(batch.operations[j]),int(batch.labels[j]),li,h,q,n["local_tv"][i,h,q],n["local_key_max"][i,h,q],n["local_value_abs"][i,h,q],n["local_value_reference"][i,h,q],n["local_value_relative"][i,h,q],0.,0.,0.,propagated_tv[i,h,q],0.,0.,0.,n["dt_h_operator"][i,h],n["eigenphase_rms"][i,h],n["phase_dispersion"][i,h,q],dt_cache[h],gamma_cache[h])
                        for key,value in zip(ROW_KEYS,values,strict=True): rows[key].append(value.item() if isinstance(value,Tensor) else value)
                for q in range(n["hidden"].shape[1]):
                    values=(seed,condition,j,int(batch.operations[j]),int(batch.labels[j]),li,-1,q,0.,0.,0.,0.,0.,n["local_projected_abs"][i,q],n["local_projected_reference"][i,q],n["local_projected_relative"][i,q],0.,hidden["absolute"][i,q],hidden["relative"][i,q],input_change[i,q],0.,0.,0.,0.,0.)
                    for key,value in zip(ROW_KEYS,values,strict=True): rows[key].append(value.item() if isinstance(value,Tensor) else value)
    return rows,examples,numerical


def _merge(into: dict[str,list[Any]], other: dict[str,list[Any]]) -> None:
    for key,value in other.items(): into.setdefault(key,[]).extend(value)


def _manifest() -> dict[str,str]:
    paths=[CONFIG_PATH,ROOT/"execution"/"runtime.json",ROOT/"execution"/"experiment_contract.md",ROOT/"checkpoint_diagnostic_plan.md",ROOT/"execution"/"diagnostics"/"status.md",ROOT/"tests"/"test_checkpoint_diagnostic.py",ROOT/"execution"/"diagnostics"/"reviews"/"00-plan.md",ROOT/"execution"/"diagnostics"/"reviews"/"01-implementation.md",ROOT/"execution"/"diagnostics"/"reviews"/"02-revision1.md",ROOT/"execution"/"diagnostics"/"reviews"/"03-final-safety.md",ROOT/"execution"/"diagnostics"/"specs"/"01-review-corrections.md",ROOT/"execution"/"diagnostics"/"specs"/"02-final-safety-corrections.md",ROOT/"execution"/"diagnostics"/"specs"/"03-output-ownership-fix.md",ROOT/"execution"/"diagnostics"/"handoffs"/"01-implementation.md",ROOT/"execution"/"diagnostics"/"handoffs"/"02-revision1.md",ROOT/"execution"/"diagnostics"/"handoffs"/"03-final-safety.md"]+[ROOT/"schrodinger"/x for x in ("attention.py","data.py","model.py","experiment.py","checkpoint_diagnostic.py")]
    for seed in SEEDS:
        root=ROOT/"execution"/"results"/"measured"/f"seed-{seed}"/"schrodinger"; paths += [root/"checkpoint-2000.pt",root/"evaluation.npz",root/"evaluation.manifest.json",root/"final.json"]
    return {str(p.relative_to(ROOT)):sha256(p) for p in paths}


def _validate_inputs(seed: int, base: Path, saved: dict[str, Any], final: dict[str, Any], batches: dict[str, Batch]) -> None:
    """Fail before tracing if retained declarations do not identify one frozen run."""
    if saved.get("seed") != seed or final.get("seed") != seed: raise ValueError(f"seed identity mismatch at {base}")
    if saved.get("mode") != "schrodinger" or final.get("mode") != "schrodinger": raise ValueError(f"mode identity mismatch at {base}")
    final_checkpoint=Path(final.get("final_checkpoint", "")); final_checkpoint=final_checkpoint if final_checkpoint.is_absolute() else ROOT/final_checkpoint
    if saved.get("step") != 2000 or final_checkpoint.resolve() != (base / "checkpoint-2000.pt").resolve(): raise ValueError(f"step/final checkpoint identity mismatch at {base}")
    if saved.get("config") != final.get("runtime") or saved.get("config") != config(): raise ValueError(f"config identity mismatch at {base}")
    if saved.get("source_hashes") != final.get("source_hashes") or saved.get("source_hashes") != source_hashes(): raise ValueError(f"source identity mismatch at {base}")
    if saved.get("initial_identity") != final.get("initial_identity"): raise ValueError(f"initial identity mismatch at {base}")
    manifest=json.loads((base/"evaluation.manifest.json").read_text()); expected=manifest.get("hashes")
    digests={name:batch.digest() for name,batch in batches.items()}
    if expected != digests or final.get("evaluation_hashes") != digests: raise ValueError(f"evaluation digest identity mismatch at {base}")
    expected_names={"validation_seen_d4","test_seen_d4","test_heldout_d4","test_seen_d8","test_heldout_d8"}
    if set(batches) != expected_names: raise ValueError(f"evaluation condition keys mismatch at {base}")
    for name,batch in batches.items():
        distractors=8 if name.endswith("d8") else 4; heldout="heldout" in name; count=512 if name=="validation_seen_d4" else 1024
        if len(batch.labels)!=count or batch.tokens.shape!=(count,7+distractors): raise ValueError(f"evaluation shape/count mismatch at {base}/{name}")
        if not np.isin(batch.operations,[XOR,COPY]).all() or not np.isin(batch.labels,[0,1]).all(): raise ValueError(f"evaluation domain mismatch at {base}/{name}")
        validate_batch(batch,distractors,heldout)
        for operation in (XOR,COPY):
            if int((batch.operations==operation).sum()) != count//2: raise ValueError(f"evaluation operation balance mismatch at {base}/{name}")


def _summary(rows: dict[str,list[Any]]) -> list[dict[str,Any]]:
    """Every direct cell is explicit: seed/condition/op/layer/head/all-or-CLS."""
    answer=[]; data=np.asarray(rows["local_tv"],dtype=float)
    for seed in SEEDS:
      for condition in sorted(set(rows["condition"])):
       for op,name in ((XOR,"xor"),(COPY,"copy")):
        for layer in (0,1):
         for head in (0,1):
          for subset,q in (("all_rows",None),("cls_query",0)):
           mask=(np.asarray(rows["seed"])==seed)&(np.asarray(rows["condition"])==condition)&(np.asarray(rows["operation"])==op)&(np.asarray(rows["layer"])==layer)&(np.asarray(rows["head"])==head)
           if q is not None: mask &= np.asarray(rows["query"])==q
           if mask.any():
            cell={"seed":seed,"condition":condition,"operation":name,"layer":layer,"head":head,"subset":subset,**quantiles(torch.tensor(data[mask]))}
            cell["locally_small"] = bool(cell["mean"] < .01 and cell["p95"] < .05)
            for field in ("local_key_max","local_value_abs","local_value_reference","local_value_relative","propagated_tv","dt_h_operator","eigenphase_rms","phase_dispersion"):
                value=np.asarray(rows[field],dtype=float)[mask]; cell[field+"_mean"]=float(value.mean()); cell[field+"_p95"]=float(np.quantile(value,.95)); cell[field+"_max"]=float(value.max())
            answer.append(cell)
    return answer


def _downstream_summary(examples: dict[str,list[Any]]) -> list[dict[str,Any]]:
    answer=[]
    for seed in SEEDS:
      for condition in sorted(set(examples["condition"])):
       for op,name in ((XOR,"xor"),(COPY,"copy")):
        mask=(np.asarray(examples["seed"])==seed)&(np.asarray(examples["condition"])==condition)&(np.asarray(examples["operation"])==op)
        if not mask.any(): continue
        def number(key: str) -> np.ndarray: return np.asarray(examples[key],dtype=float)[mask]
        pchange=number("probability_abs_change"); benefit=number("loss_benefit"); margin=number("margin_abs_change"); absolute_loss=number("absolute_loss_change")
        normal_correct,zero_correct=number("normal_correct"),number("dt0_correct")
        answer.append({"seed":seed,"condition":condition,"operation":name,"count":int(mask.sum()),"normal_accuracy":float(normal_correct.mean()),"dt0_accuracy":float(zero_correct.mean()),"accuracy_delta":float(normal_correct.mean()-zero_correct.mean()),"probability_abs_mean":float(pchange.mean()),"probability_abs_p95":float(np.quantile(pchange,.95)),"probability_abs_max":float(pchange.max()),"margin_abs_mean":float(margin.mean()),"margin_abs_p95":float(np.quantile(margin,.95)),"margin_abs_max":float(margin.max()),"absolute_loss_mean":float(absolute_loss.mean()),"absolute_loss_p95":float(np.quantile(absolute_loss,.95)),"absolute_loss_max":float(absolute_loss.max()),"loss_benefit_mean":float(benefit.mean()),"loss_benefit_sample_sd":float(benefit.std(ddof=1)),"loss_benefit_median":float(np.quantile(benefit,.5)),"loss_benefit_p05":float(np.quantile(benefit,.05)),"loss_benefit_p95":float(np.quantile(benefit,.95)),"disagreement_rate":float(number("disagreement").mean()),"downstream_small":bool(pchange.mean()<.01 and np.quantile(pchange,.95)<.05 and number("disagreement").mean()<.01)})
    return answer


def _frozen_flags(cells: list[dict[str, Any]], downstream: list[dict[str, Any]]) -> dict[str, Any]:
    local_small = all(item["mean"] < .01 and item["p95"] < .05 for item in cells)
    benefits=[]
    for condition in sorted({item["condition"] for item in downstream if item["condition"].startswith("test_")}):
      for operation in ("xor","copy"):
       items=[item for item in downstream if item["condition"]==condition and item["operation"]==operation]
       benefits.append({"condition":condition,"operation":operation,"seed_benefits":[item["loss_benefit_mean"] for item in items],"mean_benefit":float(np.mean([item["loss_benefit_mean"] for item in items])),"positive_seeds":sum(item["loss_benefit_mean"]>0 for item in items),"noticeable_benefit":bool(np.mean([item["loss_benefit_mean"] for item in items])>=.01 and sum(item["loss_benefit_mean"]>0 for item in items)>=2)})
    return {"uniformly_local_small":local_small,"test_condition_operation_benefit":benefits}


def _post_projection_summary(rows: dict[str,list[Any]]) -> list[dict[str,Any]]:
    answer=[]
    for seed in SEEDS:
      for condition in sorted(set(rows["condition"])):
       for op,name in ((XOR,"xor"),(COPY,"copy")):
        for layer in (0,1):
         for subset,query in (("all_rows",None),("cls_query",0)):
          mask=(np.asarray(rows["seed"])==seed)&(np.asarray(rows["condition"])==condition)&(np.asarray(rows["operation"])==op)&(np.asarray(rows["layer"])==layer)&(np.asarray(rows["head"])==-1)
          if query is not None: mask &= np.asarray(rows["query"])==query
          if not mask.any(): continue
          result={"seed":seed,"condition":condition,"operation":name,"layer":layer,"subset":subset}
          for field in ("local_projected_abs","local_projected_reference","local_projected_relative","propagated_hidden_abs","propagated_hidden_relative","propagated_normalized_input_abs"):
            value=np.asarray(rows[field],dtype=float)[mask]; result[field+"_mean"]=float(value.mean()); result[field+"_p95"]=float(np.quantile(value,.95)); result[field+"_max"]=float(value.max())
          answer.append(result)
    return answer


def _plot(rows: dict[str,list[Any]], examples: dict[str,list[Any]], output: Path) -> None:
    import matplotlib.pyplot as plt
    averages: dict[tuple[int,str,int],list[float]]={}
    for s,c,i,h,tv in zip(rows["seed"],rows["condition"],rows["sample"],rows["head"],rows["local_tv"],strict=True):
        if h>=0: averages.setdefault((s,c,i),[]).append(tv)
    conditions=sorted(set(examples["condition"])); fig,axes=plt.subplots(len(SEEDS),len(conditions),figsize=(3*len(conditions),2.5*len(SEEDS)),sharex=True,sharey=True)
    arrays={key:np.asarray(value) for key,value in examples.items()}
    mean_tv=np.asarray([np.mean(averages[(s,c,i)]) for s,c,i in zip(arrays["seed"],arrays["condition"],arrays["sample"],strict=True)])
    for row,seed in enumerate(SEEDS):
      for column,condition in enumerate(conditions):
       axis=axes[row,column]; mask=(arrays["seed"]==seed)&(arrays["condition"]==condition)
       for op,label,color in ((XOR,"XOR","#4477aa"),(COPY,"COPY","#cc6677")):
        current=mask&(arrays["operation"]==op); axis.scatter(mean_tv[current],arrays["probability_abs_change"][current].astype(float),s=7,alpha=.45,color=color,label=label)
       axis.set_title(f"seed {seed}: {condition}",fontsize=8)
       if row==0 and column==0: axis.legend(fontsize=7)
    fig.supxlabel("direct local TV (mean across heads/queries)"); fig.supylabel("full-path |Δ p(class 1)|"); fig.tight_layout(); fig.savefig(output,dpi=160); plt.close(fig)


def _assert_retained_metrics(examples: dict[str,list[Any]], expected: dict[str,Any], expected_dt0: dict[str,Any], condition: str) -> None:
    """Independent count/CE reconstruction from manually traced logits."""
    labels=np.asarray(examples["label"],dtype=int); operations=np.asarray(examples["operation"],dtype=int)
    prediction=np.asarray(examples["normal_prediction"],dtype=int); zero_prediction=np.asarray(examples["dt0_prediction"],dtype=int); loss=np.asarray(examples["normal_loss"],dtype=float); zero_loss=np.asarray(examples["dt0_loss"],dtype=float)
    for value, target, label in ((loss,expected,"normal"),(zero_loss,expected_dt0,"dt0")):
        if not np.isclose(value.mean(), target["cross_entropy"], atol=2e-6, rtol=0): raise AssertionError(f"retained {label} CE mismatch for {condition}")
    for operation,name in ((XOR,"xor"),(COPY,"copy")):
        mask=operations==operation
        for predict,target,label in ((prediction,expected,"normal"),(zero_prediction,expected_dt0,"dt0")):
            correct=int((predict[mask]==labels[mask]).sum())
            if correct != target[f"{name}_correct"] or int(mask.sum()) != target[f"{name}_count"]: raise AssertionError(f"retained {label} correct/count mismatch for {condition}/{name}")


def _runtime_identity() -> dict[str, Any]:
    return {"python":sys.version,"executable":sys.executable,"platform":platform.platform(),"machine":platform.machine(),"torch":torch.__version__,"numpy":np.__version__,"torch_threads":torch.get_num_threads(),"torch_interop_threads":torch.get_num_interop_threads(),"cuda_available":torch.cuda.is_available()}


def run(output: Path, lock: Path, *, argv: list[str] | None = None, command_started: float | None = None) -> None:
    argv=argv or [sys.executable,"-m","schrodinger.checkpoint_diagnostic","--output",str(output),"--lock",str(lock)]
    command_started=time.perf_counter() if command_started is None else command_started
    if output.exists(): _record_rejection("output already exists",output,lock,argv,started=command_started); raise FileExistsError(f"diagnostic output already exists: {output}")
    if lock.exists(): _record_rejection("lock already exists; not cleared",output,lock,argv,started=command_started); raise FileExistsError(f"diagnostic lock already exists: {lock}")
    torch.set_num_threads(2); torch.set_num_interop_threads(1); torch.use_deterministic_algorithms(True)
    with Attempt(output,lock,command=" ".join(argv),argv=argv,command_started=command_started) as attempt:
        (output/"input_manifest.json").write_text(json.dumps(_manifest(),indent=2,sort_keys=True))
        (output/"runtime.json").write_text(json.dumps({"experiment_config":config(),"actual_runtime":_runtime_identity(),"dtype":"float32/complex64","batch_size":64,"cap_seconds":CAP_SECONDS,"reserve_seconds":RESERVE_SECONDS,"command":attempt.command,"argv":argv,"lock":str(lock)},indent=2,sort_keys=True))
        rows:dict[str,list[Any]]={}; examples:dict[str,list[Any]]={}; checks={}
        for seed in SEEDS:
            attempt.guard(); base=ROOT/"execution"/"results"/"measured"/f"seed-{seed}"/"schrodinger"; saved=torch.load(base/"checkpoint-2000.pt",weights_only=False); model=TinyClassifier("schrodinger"); model.load_state_dict(saved["model"]); model.eval()
            final=json.loads((base/"final.json").read_text())
            batches=load_evaluation_data(base/"evaluation.npz"); _validate_inputs(seed,base,saved,final,batches)
            for condition,batch in batches.items():
                attempt.guard()
                r,e,n=trace_batch(seed,condition,batch,model,attempt); _assert_retained_metrics(e,final["metrics"][condition],final["dt_zero"][condition],condition); _merge(rows,r); _merge(examples,e); checks[f"{seed}/{condition}"]=n
        attempt.guard(); row_arrays={key:np.asarray(value,dtype="U32" if key=="condition" else None) for key,value in rows.items()}; example_arrays={key:np.asarray(value,dtype="U32" if key=="condition" else None) for key,value in examples.items()}
        for value in list(row_arrays.values())+list(example_arrays.values()):
            if value.dtype.kind=="f" and not np.isfinite(value).all(): raise FloatingPointError("nonfinite diagnostic result")
        payload=lambda data:{k:np.asarray(v,dtype="U32" if k=="condition" else None) for k,v in data.items()}
        if any(v["max_hermiticity"]>1e-6 or v["max_unitarity"]>2e-3 or v["max_row_error"]>2e-4 for v in checks.values()): raise FloatingPointError("diagnostic invariant check failed")
        attempt.guard(); cells=_summary(row_arrays); downstream=_downstream_summary(example_arrays); post=_post_projection_summary(row_arrays); flags=_frozen_flags(cells,downstream); attempt.guard()
        np.savez_compressed(output/"rows.npz",**row_arrays); attempt.guard(); np.savez_compressed(output/"examples.npz",**example_arrays); attempt.guard()
        (output/"summary.json").write_text(json.dumps({"status":"COMPLETE","seeds":list(SEEDS),"row_count":len(row_arrays["seed"]),"example_count":len(example_arrays["seed"]),"numerical_checks":checks,"direct_tv_cells":cells,"post_projection_cells":post,"downstream_cells":downstream,"frozen_flags":flags,"field_applicability":{"head_ge_0":"attention-row, direct-Y, propagated-attention, scale and phase fields","head_minus_1":"post-output-projection and propagated-hidden fields; unrelated numeric fields are schema zero placeholders"}},indent=2,sort_keys=True)); attempt.guard()
        with (output/"summary.csv").open("w",newline="") as handle: writer=csv.DictWriter(handle,fieldnames=list(cells[0])); writer.writeheader(); writer.writerows(cells)
        attempt.guard(); _plot(row_arrays,example_arrays,output/"local_vs_downstream.png"); attempt.guard()


def main() -> None:
    started=time.perf_counter(); parser=argparse.ArgumentParser(description="single locked all-seed retained-checkpoint diagnostic"); parser.add_argument("--output",type=Path,required=True); parser.add_argument("--lock",type=Path,default=ROOT/"execution"/"diagnostics"/"diagnostic.lock"); args=parser.parse_args(); run(args.output,args.lock,argv=list(getattr(sys,"orig_argv",[sys.executable,*sys.argv])),command_started=started)


if __name__ == "__main__": main()
