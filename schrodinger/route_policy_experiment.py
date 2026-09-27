"""Reviewed route-policy command harness; scientific configuration is fixed."""
from __future__ import annotations
import argparse, copy, hashlib, json, os, platform, resource, signal, sys, time, uuid
from dataclasses import asdict, dataclass, is_dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable
import numpy as np
import torch
from .route_policy import RoutePolicy, policy_losses
from .route_policy_data import MapBalancedSampler, features, legal_mask
from .route_policy_metrics import training_bank, heldout_bank, serialize_candidate
from .route_policy_evaluation import evaluate_rollouts, evaluate_proper, mechanism_probe
from .route_policy_data import ATTEMPT, MANIFEST_SHA256, load_training, load_validation, load_final_test

CARRY=923.003597253; GLOBAL_CAP=7200.; STAGES={"A":700.,"B":2000.,"C":1900.,"D":1300.}; FINAL_AUDIT=120.; FINALIZATION=30.; STARTUP=2.
class BudgetError(RuntimeError): pass
class IdentityError(RuntimeError): pass
class ArtifactError(RuntimeError): pass

FROZEN_CONFIG={"batch":64,"lr":.001,"betas":[.9,.999],"eps":1e-8,"weight_decay":.01,"clip":1.,"threads":2,"plan_sha256":"5ece45cdb11f860ae64933225f284297cff59aa544c6730b247138c660cc8ff0"}
INITIAL_TARGET=1000
PILOT_TARGETS=(1000,2000,4000,8000)
EVALUATION_UPDATES=(500,1000,2000,4000,8000)
CHECKPOINT_INTERVAL=100
def config_hash(config=FROZEN_CONFIG): return hashlib.sha256(json.dumps(config,sort_keys=True,separators=(",",":")).encode()).hexdigest()
def bank_payload(bank):
    def row(c): return {"id":serialize_candidate(c).hex(),"map_id":c.map_id,"family":c.family,"goal":c.goal,"current":c.current,"q":list(c.q)}
    return {"candidate_hash":bank.candidate_hash,"selected_hash":bank.selected_hash,"q_hash":bank.q_hash,"map_counts":list(bank.map_counts),"candidates":[row(c) for c in bank.candidates],"selected":[row(c) for c in bank.selected]}
def prepare_banks(training, validation, final_test):
    """Pure prepare surface: banks only, never model inference or output ownership."""
    return {"config":FROZEN_CONFIG,"config_hash":config_hash(),"training":bank_payload(training_bank(training.states)),"validation":bank_payload(heldout_bank(validation.problems)),"test":bank_payload(heldout_bank(final_test.problems))}
def write_prepared(path: Path, payload: dict):
    if path.exists(): raise FileExistsError("prepared artifact exists")
    path.parent.mkdir(parents=True,exist_ok=True); path.write_text(json.dumps(payload,sort_keys=True)); return hashlib.sha256(path.read_bytes()).hexdigest()
def require_final_release(decision: dict, *, config_digest: str, test_bank_hash: str):
    """The release record binds every main identity, not a directory or count."""
    base={"approved":True,"config_hash":config_digest,"test_bank_hash":test_bank_hash,"pilot_accepted":True,"power_accepted":True,"runtime_accepted":True}
    if not isinstance(decision,dict) or any(decision.get(k)!=v for k,v in base.items()): raise PermissionError("final test release not authorized")
    identities=decision.get("completed_main_identities")
    if not isinstance(identities,list) or len(identities)!=20: raise PermissionError("twenty completed main identities required")
    seen=set()
    for item in identities:
        if not isinstance(item,dict) or item.get("config_hash")!=config_digest or item.get("status")!="COMPLETE": raise PermissionError("invalid completed main identity")
        key=(item.get("seed"),item.get("mode"),item.get("checkpoint_hash"))
        if not isinstance(key[0],int) or key[1] not in {"softmax","schrodinger"} or not isinstance(key[2],str) or len(key[2])!=64 or key in seen: raise PermissionError("invalid completed main identity")
        seen.add(key)
def require_train_decision(decision: dict):
    if not isinstance(decision,dict) or decision.get("approved") is not True or decision.get("kind") not in {"smoke_or_profile","pilot","main"}: raise PermissionError("train decision not authorized")

def _serializable(value):
    if is_dataclass(value): return _serializable(asdict(value))
    if isinstance(value,dict): return {str(k):_serializable(v) for k,v in value.items() if k!="cache"}
    if isinstance(value,(tuple,list)): return [_serializable(v) for v in value]
    if isinstance(value,np.ndarray): return _serializable(value.tolist())
    if isinstance(value,(bytes,bytearray)): return bytes(value).hex()
    if isinstance(value,np.generic): return _serializable(value.item())
    if isinstance(value,float) and not np.isfinite(value): return None
    return value
def scheduled_training(model, opt, sampler, *, seed, source, config, input_ids, checkpoint_dir: Path, updates, validation=None, validation_problems=(), train_probe=(), validation_probe=(), support=frozenset(), decision=None, smoke_fixture=False, resume=None):
    """Bounded caller-owned train seam; no CLI or production authorization."""
    require_train_decision(decision); events=[]
    if resume is None:
        checkpoint_dir.mkdir(parents=True,exist_ok=False); initial=state_hash(model); total=0.; start=0
        initial_path=checkpoint_dir/"initial.pt"; parent=checkpoint(initial_path,model=model,opt=opt,sampler=sampler,seed=seed,mode=model.mode,source=source,config=config,initial_hash=initial,update=0,training_seconds=0.,parent=None,input_ids=input_ids)
    else:
        checkpoint_dir.mkdir(parents=True,exist_ok=False); cp=Path(resume["path"]); actual=hashlib.sha256(cp.read_bytes()).hexdigest()
        if actual!=resume["hash"]: raise IdentityError("resume checkpoint hash mismatch")
        payload=torch.load(cp,weights_only=False); identity=payload["identity"]; initial=identity["initial_hash"]; start=identity["update"]; parent=identity["parent_hash"]
        initial_path=Path(resume.get("initial_path", ""))
        if not initial_path.is_file(): raise IdentityError("resume requires approved original initial checkpoint")
        initial_bytes=initial_path.read_bytes(); initial_digest=hashlib.sha256(initial_bytes).hexdigest(); initial_payload=torch.load(initial_path,weights_only=False)
        initial_identity=initial_payload.get("identity")
        expected_initial={"seed":seed,"mode":model.mode,"source":source,"config":config,"initial_hash":initial,"input_ids":input_ids,"update":0,"parent_hash":None}
        if initial_identity!=expected_initial or state_hash_from_state(initial_payload["model"])!=initial: raise IdentityError("original initial checkpoint identity mismatch")
        expected=decision.get("resume_identity")
        if not isinstance(expected,dict) or expected!={"seed":seed,"mode":model.mode,"source":source,"config":config,"input_ids":input_ids,"initial_hash":initial,"update":start,"parent_hash":parent,"checkpoint_hash":actual,"initial_checkpoint_hash":initial_digest}: raise IdentityError("resume not bound by authorization record")
        restore(cp,model=model,opt=opt,sampler=sampler,seed=seed,mode=model.mode,source=source,config=config,initial_hash=initial,input_ids=input_ids,update=start,parent=parent)
        total=payload["training_seconds"]; parent=actual
    initial_file_hash=hashlib.sha256(initial_path.read_bytes()).hexdigest()
    def event(update):
        identity=(parent,model.mode,"normal"); controls={}
        if validation_problems:
            initial_model=RoutePolicy(model.mode); initial_model.load_state_dict(torch.load(initial_path,weights_only=False)["model"])
            controls={"greedy":evaluate_rollouts(model,validation_problems,identity=identity,seed=seed,splitcode=1,k=1,greedy=True,support=support),"t1_k32":evaluate_rollouts(model,validation_problems,identity=identity,seed=seed,splitcode=1,k=32,support=support),"own_initial":evaluate_rollouts(initial_model,validation_problems,identity=(initial,"own_initial","normal"),seed=seed,splitcode=1,k=32,support=support),"uniform_legal":evaluate_rollouts(model,validation_problems,identity=(parent,"uniform","normal"),seed=seed,splitcode=1,k=32,support=support,uniform_legal=True)}
        probes={origin:{"candidate_ids":[serialize_candidate(c).hex() for c in candidates],
                        "count":len(candidates),"result":mechanism_probe(model,candidates)}
                for origin,candidates in (("training",train_probe),("validation",validation_probe)) if candidates}
        return _serializable({"update":update,"proper":None if validation is None else evaluate_proper(model,validation,identity=identity),"routes":controls,"probes":probes})
    def durable(name, row):
        with (checkpoint_dir/name).open("a",encoding="utf8") as handle:
            handle.write(json.dumps(_serializable(row),sort_keys=True)+"\n"); handle.flush(); os.fsync(handle.fileno())
    if validation is not None and start==0:
        events.append(event(0)); durable("events.jsonl",events[-1])
    curves=[]
    for update in range(start+1,updates+1):
        step=train_step(model,opt,sampler,summary=update%CHECKPOINT_INTERVAL==0); total+=step["training_core_seconds"]
        curves.append({"update":update,"batch_digest":step["batch_digest"],"ce":step["scalars"]["ce"],"materialize_seconds":step["materialize_seconds"],"training_core_seconds":step["training_core_seconds"],"summary":step.get("summary")}); durable("curves.jsonl",curves[-1])
        if update%CHECKPOINT_INTERVAL==0 or update==updates:
            cp=checkpoint_dir/f"update-{update}.pt"; parent=checkpoint(cp,model=model,opt=opt,sampler=sampler,seed=seed,mode=model.mode,source=source,config=config,initial_hash=initial,update=update,training_seconds=total,parent=parent,input_ids=input_ids)
        if validation is not None and update in EVALUATION_UPDATES:
            events.append(event(update)); durable("events.jsonl",events[-1])
    return _serializable({"initial_hash":initial,"initial_checkpoint_path":str(initial_path.resolve()),
                          "initial_checkpoint_hash":initial_file_hash,"start_update":start,
                          "final_checkpoint":parent,"final_checkpoint_path":str(cp.resolve()),
                          "training_seconds":total,"events":events,"curves":curves})
def smoke_pair(states, validation, *, root: Path, decision, problems=None, support=frozenset()):
    """Five real updates/model plus supplied-bank evaluation; test callers own root."""
    torch.set_num_threads(2); soft,sa,digest=paired_models(1701); ids={"training_bundle":"smoke","support":"smoke","paired_stream":"smoke"}; config={"batch":64,"lr":.001}
    probes=validation.selected[:8]
    # A smoke fixture is intentionally small, but it is a real route evaluation.
    from .route_policy_data import Problem
    if problems is None:
        from .route_feasibility import bfs_counts
        p=validation.selected[0]; dist,counts=bfs_counts(frozenset(i for i,b in enumerate(p.canonical) if b),p.goal,n=12)
        problems=(Problem(p.canonical,p.map_id,p.family,p.current,p.goal,dist[p.current],counts[p.current],None),)
    return {"shared_init":digest,"softmax":scheduled_training(soft,optimizer(soft),MapBalancedSampler(states,1701),seed=1701,source="smoke",config=config,input_ids=ids,checkpoint_dir=root/"softmax",updates=5,validation=validation,validation_problems=problems,validation_probe=probes,support=support,smoke_fixture=True,decision=decision),"schrodinger":scheduled_training(sa,optimizer(sa),MapBalancedSampler(states,1701),seed=1701,source="smoke",config=config,input_ids=ids,checkpoint_dir=root/"schrodinger",updates=5,validation=validation,validation_problems=problems,validation_probe=probes,support=support,smoke_fixture=True,decision=decision)}
def forecast_profile(profile, *, remaining_updates=1000, models=2, checkpoints=11, evaluations=3, audit_seconds=120., serialization_seconds=0., missing_stratum_seconds=0.):
    """Conservative 1.5x forecast; callers supply measured complete phase cells."""
    steps=np.asarray(profile["measured_step_seconds"],float)
    if steps.shape != (models,20) or not np.isfinite(steps).all() or (steps<0).any(): raise ValueError("need 20 measured updates/model")
    cells=np.asarray(profile.get("stratum_seconds",[]),float); cell=float(max(cells)) if len(cells) else float(missing_stratum_seconds)
    if cell<0 or serialization_seconds<0 or audit_seconds<0: raise ValueError("invalid forecast costs")
    train=1.5*float(steps.mean())*remaining_updates*models
    evaluation=1.5*(cell*evaluations+serialization_seconds*checkpoints)
    total=train+evaluation+audit_seconds
    return {"warmup_updates":5,"measured_updates":20,"profile_seed":1699,"models":models,"train_seconds":train,"evaluation_io_seconds":evaluation,"audit_seconds":audit_seconds,"total_seconds":total,"conservative_cell_seconds":cell,"median_step_seconds":float(np.median(steps)),"p95_step_seconds":float(np.percentile(steps,95))}

def full_work_forecast(profile, *, remaining_updates=1000, validation_problems=512):
    """Conservative entry + equal-time + conditional operating-point bound.

    Physical work counts, not scientific mixture weights. Each cell includes
    current greedy/T1/proper, own-initial and uniform controls. Nested evaluator
    timings are evidence only and are never added again to this cell.
    """
    if validation_problems!=512: raise ValueError("frozen validation has 512 problems")
    base=forecast_profile(profile,remaining_updates=remaining_updates)
    cells=profile.get("stratum_cells",{})
    observed=[float(v) for v in cells.values() if isinstance(v,(int,float)) and np.isfinite(v) and v>0]
    if not observed: raise ValueError("measured positive evaluation cells required")
    rates={s:float(cells.get(s,max(observed))) for s in ("routine","challenge")}
    names=("setup_seconds","checkpoint_io_seconds","probe_seconds","serialization_per_problem_seconds",
           "ledger_seconds","trace_per_step_seconds")
    if any(k not in profile or not np.isfinite(profile[k]) or profile[k]<=0 for k in names):
        raise ValueError("complete positive measured phase units required")
    endpoints=3+4  # Scheduled 0/500/1000 plus four saved equal-time endpoints.
    validation=1.5*(384*rates["routine"]+128*rates["challenge"])*2*endpoints
    writes=1.5*profile["checkpoint_io_seconds"]*11*2
    probes=1.5*profile["probe_seconds"]*endpoints  # SA only, both identified banks.
    candidate_counts={"two_quality_searches":2*(2+8+6),"two_fixed_curves":2*6,
                      "softmax_entropy_search":2+8+6,"dt0_T1_and_quality_search":1+2+8+6}
    candidates=sum(candidate_counts.values())
    # Deliberately upper-bound even entropy-only/cache-reused work by the complete
    # measured endpoint cost; do not claim a cache makes sampling free.
    temperature=1.5*max(rates.values())*512*candidates
    serialization=1.5*profile["serialization_per_problem_seconds"]*512*(2*endpoints+candidates)
    traces=1.5*profile["trace_per_step_seconds"]*remaining_updates*2
    fixed=1.5*(2*profile["setup_seconds"]+12*profile["ledger_seconds"])+120.+30.
    total=base["train_seconds"]+validation+writes+probes+temperature+serialization+traces+fixed
    return {"train_seconds":base["train_seconds"],"checkpoint_count":11,"evaluation_updates":[0,500,1000],
            "equal_time_endpoints_per_model":4,"models":2,"validation_counts":{"routine":384,"challenge":128,"models":2,"endpoints":3},
            "per_stratum_problem_seconds":rates,"missing_stratum_rule":"largest_observed_rate",
            "validation_extrapolation_seconds":validation,"checkpoint_write_seconds":writes,"probe_seconds":probes,
            "temperature_candidate_counts":candidate_counts,"temperature_work_seconds":temperature,
            "serialization_seconds":serialization,"trace_seconds":traces,"fixed_seconds":fixed,
            "future_temperature_work":"NOT_IMPLEMENTED_GATED_COSTED","total_seconds":total}

def profile_map_subset(validation):
    """First two canonical map identities in each I/L/mixed validation family."""
    selected=[]
    for family in ("IIIIIIII","LLLLLLLL","IIIILLLL"):
        maps=sorted({p.map_id for p in validation.problems if p.family==family})[:2]
        selected.extend(p for p in validation.problems if p.map_id in maps and p.family==family)
    return tuple(selected)

def _probe_maps(bank, family, count): return sorted({c.map_id for c in bank.selected if c.family==family})[:count]
def training_probe_candidates(bank):
    maps=set(_probe_maps(bank,"IIIIIIII",4)+_probe_maps(bank,"LLLLLLLL",4))
    chosen=tuple(c for map_id in sorted(maps) for c in [x for x in bank.selected if x.map_id==map_id][:8])
    if len(chosen)!=64: raise IdentityError("training probe must contain 64 states")
    return chosen
def validation_probe_candidates(bank):
    maps=set(_probe_maps(bank,"IIIIIIII",4)+_probe_maps(bank,"LLLLLLLL",4)+_probe_maps(bank,"IIIILLLL",8))
    chosen=tuple(c for map_id in sorted(maps) for c in [x for x in bank.selected if x.map_id==map_id][:8])
    if len(chosen)!=128: raise IdentityError("validation probe must contain 128 states")
    return chosen

def configure_runtime():
    torch.set_num_threads(2)
    try: torch.set_num_interop_threads(1)
    except RuntimeError:
        if torch.get_num_interop_threads()!=1: raise

def utc() -> str: return datetime.now(timezone.utc).isoformat()
def _read(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text().splitlines() if line] if path.exists() else []
def ledger_totals(records: Iterable[dict]) -> dict[str,float]:
    rows=list(records); carries=[r for r in rows if r.get("kind")=="inherited_budget"]
    if len(carries)!=1 or carries[0].get("charged_seconds")!=0 or carries[0].get("carried_budget_debit_seconds")!=CARRY: raise BudgetError("exactly one inherited carry required")
    ids=set(); totals={stage:0. for stage in STAGES}; global_total=CARRY
    for row in rows:
        identifier=row.get("entry_id")
        if not isinstance(identifier,str) or identifier in ids: raise BudgetError("duplicate/missing ledger id")
        ids.add(identifier); charge=row.get("charged_seconds")
        if not isinstance(charge,(int,float)) or not np.isfinite(charge) or charge<0: raise BudgetError("invalid charge")
        if row.get("kind")!="inherited_budget":
            stage=row.get("stage")
            if stage not in STAGES: raise BudgetError("invalid stage")
            totals[stage]+=float(charge); global_total+=float(charge)
    return {**totals,"global":global_total}
def append_once(path: Path, row: dict) -> None:
    records=_read(path); ledger_totals(records+[row])
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open("a",encoding="utf8") as handle: handle.write(json.dumps(row,sort_keys=True)+"\n"); handle.flush(); os.fsync(handle.fileno())
def initialize_ledger(path: Path) -> None:
    if path.exists(): raise BudgetError("new ledger must not exist")
    append_once(path,{"entry_id":str(uuid.uuid4()),"recorded_at_utc":utc(),"kind":"inherited_budget","charged_seconds":0.,"carried_budget_debit_seconds":CARRY})
def deadline_seconds(ledger: Path, stage: str) -> float:
    totals=ledger_totals(_read(ledger)); stage_left=STAGES[stage]-totals[stage]; global_left=GLOBAL_CAP-totals["global"]-FINAL_AUDIT
    if stage_left<=0 or global_left<=0: raise BudgetError("budget exhausted")
    result=min(stage_left,global_left)-FINALIZATION-STARTUP
    if result<=0: raise BudgetError("deadline exhausted")
    return result

@dataclass
class OwnedAttempt:
    root: Path; ledger: Path; stage: str; entry_id: str; started_at_utc: str; started: float; lock: Path; output: Path; recorded: bool=False; timer_armed: bool=False; timer_acquired: bool=False; prior_handler: object=None; prior_timer: tuple[float,float]=(0.,0.); on_finalize: object=None
    @classmethod
    def begin(cls, root: Path, ledger: Path, stage: str, name: str) -> "OwnedAttempt":
        if stage not in STAGES: raise BudgetError("invalid stage")
        deadline_seconds(ledger,stage); output=root/name; lock=root/"experiment.lock"
        if output.exists(): raise FileExistsError("output already exists")
        try: fd=os.open(lock,os.O_CREAT|os.O_EXCL|os.O_WRONLY); os.close(fd)
        except FileExistsError: raise RuntimeError("owned lock contention")
        try:
            output.mkdir(parents=True); attempt=cls(root,ledger,stage,str(uuid.uuid4()),utc(),time.perf_counter(),lock,output)
            attempt.prior_handler=signal.getsignal(signal.SIGALRM); attempt.prior_timer=signal.setitimer(signal.ITIMER_REAL,0); attempt.timer_acquired=True
            signal.signal(signal.SIGALRM,lambda *_: (_ for _ in ()).throw(TimeoutError("attempt deadline"))); signal.setitimer(signal.ITIMER_REAL,deadline_seconds(ledger,stage)); attempt.timer_armed=True
            return attempt
        except BaseException:
            lock.unlink(missing_ok=True)
            try:
                if 'attempt' in locals() and attempt.timer_acquired:
                    signal.setitimer(signal.ITIMER_REAL,0)
                    signal.signal(signal.SIGALRM,attempt.prior_handler)
                    signal.setitimer(signal.ITIMER_REAL,*attempt.prior_timer)
            finally: pass
            raise
    def finalize(self, status: str, error: str|None=None) -> dict:
        if self.recorded: raise RuntimeError("attempt already finalized")
        finalization_start=time.perf_counter()
        # The expired training timer must not interrupt bounded failure accounting.
        if self.timer_armed: signal.setitimer(signal.ITIMER_REAL,0)
        elapsed=finalization_start-self.started; row={"entry_id":self.entry_id,"recorded_at_utc":utc(),"kind":"attempt_charge","stage":self.stage,"status":"FINALIZATION_UNCERTAIN","error":error,"elapsed_seconds":elapsed,"charged_seconds":STARTUP+elapsed+2.,"startup_allowance_seconds":STARTUP,"finalization_allowance_seconds":2.,"output":str(self.output)}
        artifact_error=None
        try: (self.output/"attempt.pending.json").write_text(json.dumps(row,sort_keys=True))
        except BaseException as write_error: row["status"]="FAILED_ARTIFACT"; row["error"]=repr(write_error); artifact_error=ArtifactError(repr(write_error))
        try:
            ledger_start=time.perf_counter()
            append_once(self.ledger,row)
            ledger_seconds=time.perf_counter()-ledger_start
            self.recorded=True
        except BaseException as ledger_error:
            # An append may have reached the file before fsync reports failure;
            # never retry this UUID or claim a successful finalization.
            self.recorded=True
            failure={"entry_id":self.entry_id,"status":"FAILED_LEDGER","error":repr(ledger_error),"attempt":row}
            try:
                (self.output/"finalization_error.json").write_text(json.dumps(failure,sort_keys=True))
                (self.output/"attempt.json").write_text(json.dumps(failure,sort_keys=True))
            except BaseException: pass
            raise
        finally:
            if self.timer_armed:
                signal.setitimer(signal.ITIMER_REAL,0); signal.signal(signal.SIGALRM,self.prior_handler); signal.setitimer(signal.ITIMER_REAL,*self.prior_timer); self.timer_armed=False
            self.lock.unlink(missing_ok=True)
        if artifact_error: raise artifact_error
        completed={**row,"kind":"attempt","status":status,"ledger_path":str(self.ledger.resolve()),
                   "ledger_append_seconds":ledger_seconds,"finalization_seconds":time.perf_counter()-finalization_start}
        try:
            if self.on_finalize is not None and status=="COMPLETE": self.on_finalize(completed)
            completed["finalization_seconds"]=time.perf_counter()-finalization_start
            (self.output/"attempt.json").write_text(json.dumps(completed,sort_keys=True))
            _write_json(self.output/"output-manifest.json",file_manifest(self.output))
        except BaseException as write_error:
            failure={"entry_id":self.entry_id,"status":"FAILED_ARTIFACT","error":repr(write_error),"attempt":row}
            try:
                (self.output/"finalization_error.json").write_text(json.dumps(failure,sort_keys=True))
                (self.output/"attempt.json").write_text(json.dumps(failure,sort_keys=True))
            except BaseException: pass
            raise ArtifactError(repr(write_error))
        return completed
    def __enter__(self): return self
    def __exit__(self, typ, value, trace):
        self.finalize("FAILED" if typ else "COMPLETE",None if value is None else repr(value)); return False

def source_hash(paths: Iterable[Path]) -> str: return hashlib.sha256(b"".join(p.read_bytes() for p in paths)).hexdigest()
def state_hash(model: RoutePolicy) -> str:
    return hashlib.sha256(b"".join(v.detach().cpu().numpy().tobytes() for _,v in sorted(model.state_dict().items()))).hexdigest()
def state_hash_from_state(state: dict) -> str:
    return hashlib.sha256(b"".join(v.detach().cpu().numpy().tobytes() for _,v in sorted(state.items()))).hexdigest()
def paired_models(seed: int) -> tuple[RoutePolicy,RoutePolicy,str]:
    torch.manual_seed(seed); soft=RoutePolicy("softmax"); torch.manual_seed(seed); sch=RoutePolicy("schrodinger")
    shared={k:v for k,v in soft.state_dict().items() if k in sch.state_dict()};
    if not all(torch.equal(v,sch.state_dict()[k]) for k,v in shared.items()): raise IdentityError("shared initialization mismatch")
    digest=hashlib.sha256(b"".join(v.detach().numpy().tobytes() for _,v in sorted(shared.items()))).hexdigest(); return soft,sch,digest
def optimizer(model: RoutePolicy) -> torch.optim.Optimizer: return torch.optim.AdamW(model.parameters(),lr=.001,betas=(.9,.999),eps=1e-8,weight_decay=.01)
def batch_tensors(states: Iterable[object]) -> tuple[torch.Tensor,torch.Tensor,torch.Tensor]:
    rows=list(states); return (torch.tensor(np.stack([features(s) for s in rows])),torch.tensor(np.stack([legal_mask(s) for s in rows])),torch.tensor(np.asarray([s.q for s in rows],np.float32)))
def _summary(model: RoutePolicy) -> dict[str,float]:
    params=[p.detach() for p in model.parameters()]; return {"weight_norm":float(torch.sqrt(sum((p*p).sum() for p in params))),"scalar_mean":float(torch.stack([p.detach().mean() for p in model.extra_scalars()]).mean())}
def _grouped_grad_norms(model: RoutePolicy) -> dict[str,float]:
    groups={"embedding":[],"attention":[],"feedforward":[],"normalization_head":[],"controls":[]}
    for name,param in model.named_parameters():
        if name.endswith(("alpha","beta","raw_dt","raw_gamma")): group="controls"
        elif name in ("row.weight","row.bias","pos","cls"): group="embedding"
        elif name.startswith("attn."): group="attention"
        elif name.startswith("ff."): group="feedforward"
        elif name.startswith(("norm1.","norm2.","final.","head.")): group="normalization_head"
        else: raise IdentityError(f"unclassified parameter {name}")
        if param.grad is None: raise FloatingPointError(f"missing gradient {name}")
        groups[group].append(param.grad.detach().square().sum())
    return {name:float(torch.sqrt(sum(parts))) for name,parts in groups.items()}
def _control_values(model: RoutePolicy) -> dict[str,list[float]]:
    values={}
    for layer,attention in enumerate(model.attn):
        if model.mode=="softmax":
            values[f"attention.{layer}.alpha"]=attention.alpha.detach().tolist(); values[f"attention.{layer}.beta"]=attention.beta.detach().tolist()
        else:
            values[f"attention.{layer}.dt"]=(.5*torch.sigmoid(attention.raw_dt.detach())).tolist(); values[f"attention.{layer}.gamma"]=(torch.pi*torch.tanh(attention.raw_gamma.detach())).tolist()
    return values
def train_step(model: RoutePolicy, opt: torch.optim.Optimizer, sampler: MapBalancedSampler, *, summary: bool=False) -> dict:
    start=time.perf_counter(); states=sampler.batch(); batch_digest=MapBalancedSampler.batch_hash(states); x,mask,q=batch_tensors(states); materialized=time.perf_counter()-start
    before=[p.detach().clone() for p in model.parameters()] if summary else None
    core=time.perf_counter(); opt.zero_grad(set_to_none=True); logits=model(x); ce,brier,kl=policy_losses(logits,mask,q); loss=ce; loss.backward()
    if any(p.grad is None or not torch.isfinite(p.grad).all() for p in model.parameters()): raise FloatingPointError("nonfinite gradient")
    core_prefix=time.perf_counter()-core
    summary_seconds=0.
    summary_start=time.perf_counter() if summary else None
    gradient_norms=_grouped_grad_norms(model) if summary else None
    if summary: summary_seconds+=time.perf_counter()-summary_start
    core=time.perf_counter(); grad_norm=float(torch.nn.utils.clip_grad_norm_(model.parameters(),1.))
    opt.step()
    if any(not torch.isfinite(p).all() for p in model.parameters()): raise FloatingPointError("nonfinite parameter")
    neural_seconds=core_prefix+(time.perf_counter()-core); scalar={"ce":float(ce.detach()),"brier":float(brier.detach()),"kl":float(kl.detach())}; result={"neural_seconds":neural_seconds,"training_core_seconds":materialized+neural_seconds,"materialize_seconds":materialized,"batch_digest":batch_digest,"grad_norm":grad_norm,"scalars":scalar}
    if summary:
        summary_start=time.perf_counter()
        theta=float(torch.sqrt(sum((p*p).sum() for p in before))); delta=float(torch.sqrt(sum(((p.detach()-old)**2).sum() for p,old in zip(model.parameters(),before))))
        summary_data=_summary(model)
        scalar_values=_control_values(model)
        summary_seconds+=time.perf_counter()-summary_start
        result["summary"]={**summary_data,"preclip_global_norm":grad_norm,"clipped":float(grad_norm>1.),"update_weight_ratio":delta/theta if theta else None,"group_gradient_norms":gradient_norms,"scalar_values":scalar_values,"summary_seconds":summary_seconds}
    result["end_to_end_seconds"]=time.perf_counter()-start
    return result
def checkpoint(path: Path, *, model: RoutePolicy, opt: torch.optim.Optimizer, sampler: MapBalancedSampler, seed:int, mode:str, source:str, config:dict, initial_hash:str, update:int, training_seconds:float, parent:str|None, input_ids:dict) -> str:
    if path.exists(): raise FileExistsError("checkpoint exists")
    if (update>0) != bool(parent): raise IdentityError("parent chain required")
    if parent is not None and (not isinstance(parent,str) or len(parent)!=64 or any(c not in "0123456789abcdef" for c in parent)): raise IdentityError("parent must be an exact checkpoint hash")
    identity={"seed":seed,"mode":mode,"source":source,"config":config,"initial_hash":initial_hash,"input_ids":input_ids,"update":update,"parent_hash":parent}
    payload={"model":model.state_dict(),"optimizer":opt.state_dict(),"sampler":sampler.state(),"torch_rng":torch.get_rng_state(),"identity":identity,"training_seconds":training_seconds}
    torch.save(payload,path); return hashlib.sha256(path.read_bytes()).hexdigest()
def restore(path: Path, *, model: RoutePolicy, opt: torch.optim.Optimizer, sampler: MapBalancedSampler, seed:int, mode:str, source:str, config:dict, initial_hash:str, input_ids:dict, update:int, parent:str|None) -> dict:
    payload=torch.load(path,weights_only=False); got=payload["identity"]; expected={"seed":seed,"mode":mode,"source":source,"config":config,"initial_hash":initial_hash,"input_ids":input_ids,"update":update,"parent_hash":parent}
    if got!=expected: raise IdentityError("checkpoint identity mismatch")
    model.load_state_dict(payload["model"]); opt.load_state_dict(payload["optimizer"]); sampler.restore(payload["sampler"]); torch.set_rng_state(payload["torch_rng"]); return payload

def runtime_provenance(prepared_hash: str|None=None) -> dict:
    root=Path(__file__).parents[1]
    source_paths=sorted(set(Path(__file__).parent.glob("route_policy*.py")) |
                        set((root/"tests").glob("test_route_policy*.py")) |
                        {root/"schrodinger/attention.py",root/"schrodinger/route_feasibility.py",root/"tests/test_attention.py"})
    execution=root/"execution/model_training_comparison"
    governing=sorted(set((execution/"specs").glob("*.md")) | set((execution/"reviews").glob("*.md")) |
                     set(execution.glob("approval*.md")) | {root/"model_training_comparison_plan.md",root/"agent_execution_protocol.md"})
    manifest=ATTEMPT/"manifest.json"
    inventory={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in source_paths}
    return {"source_hash":source_hash(source_paths),"source_files":inventory,
            "governing_files":{str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in governing},
            "input_files":{str(ATTEMPT/name):digest for name,digest in json.loads(manifest.read_text())["outputs"].items()},
            "plan_sha256":FROZEN_CONFIG["plan_sha256"],"manifest_sha256":hashlib.sha256(manifest.read_bytes()).hexdigest(),"expected_manifest_sha256":MANIFEST_SHA256,"prepared_sha256":prepared_hash,"python":sys.version,"torch":torch.__version__,"numpy":np.__version__,"os":platform.platform(),"cpu":platform.processor(),"threads":torch.get_num_threads(),"interop_threads":torch.get_num_interop_threads(),"executable":sys.executable,"argv":globals().get("COMMAND_ARGV",list(sys.argv)),"rss_max":resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}

def _load_decision(path: Path) -> dict:
    value=json.loads(path.read_text())
    if not isinstance(value,dict): raise ValueError("decision must be an object")
    return value

def _prepared_ids(path: Path) -> tuple[dict,dict]:
    raw=path.read_bytes(); payload=json.loads(raw)
    if payload.get("config_hash")!=config_hash(): raise IdentityError("prepared config hash mismatch")
    frozen=payload.get("frozen_source_provenance")
    if not isinstance(frozen,dict) or not isinstance(frozen.get("source_hash"),str): raise IdentityError("prepared artifact lacks frozen source provenance")
    if frozen["source_hash"]!=runtime_provenance()["source_hash"]: raise IdentityError("prepared implementation changed")
    ids={"prepared_sha256":hashlib.sha256(raw).hexdigest(),"training_selected_hash":payload["training"]["selected_hash"],"validation_selected_hash":payload["validation"]["selected_hash"],"test_selected_hash":payload["test"]["selected_hash"],"manifest_sha256":MANIFEST_SHA256,"frozen_source_hash":frozen["source_hash"]}
    return payload,ids

def _require_command_binding(decision: dict, ids: dict):
    if decision.get("config_hash")!=config_hash() or decision.get("prepared_sha256")!=ids["prepared_sha256"] or decision.get("manifest_sha256")!=MANIFEST_SHA256:
        raise PermissionError("decision does not bind frozen config and prepared inputs")

def _require_run_binding(decision: dict, args):
    expected={"command":"train","seed":args.seed,"mode":args.mode,"target_updates":args.updates,"run_kind":"resume" if args.resume else "fresh"}
    if any(decision.get(key)!=value for key,value in expected.items()): raise PermissionError("decision does not bind requested training run")
    if args.seed!=1701 or args.updates not in PILOT_TARGETS or decision.get("kind")!="pilot": raise PermissionError("only explicitly authorized 1701 pilot/continuation is implemented")
    if args.updates>INITIAL_TARGET and not args.resume: raise PermissionError("baseline continuation requires explicit approved resume")
    if bool(args.resume)!=(decision.get("run_kind")=="resume"): raise PermissionError("fresh/resume authorization mismatch")

def _write_json(path: Path, value: dict):
    path.write_text(json.dumps(_serializable(value),sort_keys=True,indent=2,allow_nan=False))

def file_manifest(directory: Path):
    return {str(p.relative_to(directory)):{"sha256":hashlib.sha256(p.read_bytes()).hexdigest(),"bytes":p.stat().st_size}
            for p in sorted(directory.rglob("*")) if p.is_file() and p.name!="output-manifest.json"}

def command_prepare(out: Path):
    training,validation,final_test=load_training(),load_validation(),load_final_test()
    payload=prepare_banks(training,validation,final_test); payload["frozen_source_provenance"]=runtime_provenance(); digest=write_prepared(out/"prepared.json",payload)
    record={"prepared_sha256":digest,"provenance":runtime_provenance(digest),"bank_hashes":{name:payload[name]["selected_hash"] for name in ("training","validation","test")},"test_model_predictions":False}
    _write_json(out/"result.json",record); return record

def command_smoke(out: Path, prepared: Path, decision: dict):
    _,ids=_prepared_ids(prepared); _require_command_binding(decision,ids); training,validation=load_training(),load_validation(); bank=heldout_bank(validation.problems[:1])
    configure_runtime()
    result=smoke_pair(training.states[:128],bank,root=out/"runs",decision=decision,problems=validation.problems[:1],support=frozenset(training.support))
    record={"provenance":runtime_provenance(ids["prepared_sha256"]),"input_ids":ids,"result":result,"test_model_predictions":False}
    _write_json(out/"result.json",record); return record

def command_profile(out: Path, prepared: Path, decision: dict, ledger: Path):
    started=time.perf_counter(); phases=[]
    def timed(name, callback):
        begin=time.perf_counter(); value=callback(); end=time.perf_counter()
        phases.append({"name":name,"start":begin-started,"end":end-started,"seconds":end-begin})
        return value,end-begin
    require_train_decision(decision)
    if decision.get("kind")!="smoke_or_profile": raise PermissionError("profile requires smoke_or_profile authorization")
    configure_runtime()
    def setup():
        train,val=load_training(),load_validation(); _,ids=_prepared_ids(prepared); _require_command_binding(decision,ids)
        subset=profile_map_subset(val)
        if len(subset)!=96 or len({p.map_id for p in subset})!=6: raise IdentityError("profile requires six maps/96 problems")
        tb,vb=training_bank(train.states),heldout_bank(val.problems)
        return train,val,ids,subset,{"training":training_probe_candidates(tb),"validation":validation_probe_candidates(vb)}
    (training,validation,ids,subset,probes),setup_seconds=timed("setup",setup)
    (soft,sa,shared),model_setup=timed("paired_initialization",lambda:paired_models(1699))
    profile={"profile_seed":1699,"run_order":["softmax","schrodinger"],"shared_initial_digest":shared,
             "map_ids":sorted({p.map_id for p in subset}),"problem_count":96,"measured_step_seconds":[],
             "stratum_cells":{},"operations":[],"models":{},"setup_seconds":setup_seconds+model_setup,
             "checkpoint_io_seconds":0.,"probe_seconds":0.,"serialization_per_problem_seconds":0.,
             "trace_per_step_seconds":0.,"phases":phases,"ledger_path":str(ledger.resolve())}
    support=frozenset(training.support); source=ids["frozen_source_hash"]
    for mode,model in (("softmax",soft),("schrodinger",sa)):
        def model_setup_fn(): return copy.deepcopy(model),optimizer(model),MapBalancedSampler(training.states,1699)
        (initial_model,opt,sampler),seconds=timed(mode+".setup",model_setup_fn); profile["setup_seconds"]+=seconds
        initial=state_hash(model); initial_cp=out/f"{mode}-initial.pt"
        parent,seconds=timed(mode+".initial_checkpoint",lambda:checkpoint(initial_cp,model=model,opt=opt,sampler=sampler,seed=1699,mode=mode,source=source,config=FROZEN_CONFIG,initial_hash=initial,update=0,training_seconds=0.,parent=None,input_ids=ids))
        profile["checkpoint_io_seconds"]=max(profile["checkpoint_io_seconds"],seconds)
        warm,_=timed(mode+".warmup",lambda:[train_step(model,opt,sampler) for _ in range(5)])
        measured,_=timed(mode+".measured_steps",lambda:[train_step(model,opt,sampler,summary=(i==19)) for i in range(20)])
        profile["measured_step_seconds"].append([r["end_to_end_seconds"] for r in measured])
        cp=out/f"{mode}-update-25.pt"; total=sum(r["training_core_seconds"] for r in warm+measured)
        final_hash,seconds=timed(mode+".final_checkpoint",lambda:checkpoint(cp,model=model,opt=opt,sampler=sampler,seed=1699,mode=mode,source=source,config=FROZEN_CONFIG,initial_hash=initial,update=25,training_seconds=total,parent=parent,input_ids=ids))
        profile["checkpoint_io_seconds"]=max(profile["checkpoint_io_seconds"],seconds)
        def write_trace():
            with (out/f"{mode}-step-trace.jsonl").open("x") as handle:
                for row in warm+measured:
                    handle.write(json.dumps(_serializable(row))+"\n"); handle.flush(); os.fsync(handle.fileno())
        _,seconds=timed(mode+".trace_io",write_trace); profile["trace_per_step_seconds"]=max(profile["trace_per_step_seconds"],seconds/25)
        profile["models"][mode]={"warmup_count":5,"measured_count":20,"initial_state_hash":initial,
                                  "initial_checkpoint_hash":parent,"final_checkpoint_hash":final_hash,
                                  "parameter_count":sum(p.numel() for p in model.parameters()),"training_core_seconds":total}
        for family in ("IIIIIIII","LLLLLLLL","IIIILLLL"):
            problems=tuple(p for p in subset if p.family==family)
            bank,seconds=timed(f"{mode}.{family}.bank_setup",lambda:heldout_bank(problems)); profile["setup_seconds"]+=seconds
            identity=(final_hash,mode,family); common=dict(seed=1699,splitcode=1,support=support)
            calls={"greedy":lambda:evaluate_rollouts(model,problems,identity=identity,k=1,greedy=True,**common),
                   "t1_k32":lambda:evaluate_rollouts(model,problems,identity=identity,k=32,**common),
                   "own_initial":lambda:evaluate_rollouts(initial_model,problems,identity=(parent,"initial",family),k=32,**common),
                   "uniform_legal":lambda:evaluate_rollouts(model,problems,identity=(parent,"uniform",family),k=32,uniform_legal=True,**common),
                   "proper":lambda:evaluate_proper(model,bank,identity=identity)}
            cell=serial=0.
            for name,call in calls.items():
                value,seconds=timed(f"{mode}.{family}.{name}",call); cell+=seconds
                filename=f"{mode}-{family}-{name}.json"
                _,io=timed(filename+".serialize",lambda:_write_json(out/filename,value)); serial+=io
                profile["operations"].append({"mode":mode,"family":family,"name":name,"problems":len(problems),
                                               "states":len(bank.selected) if name=="proper" else None,
                                               "seconds":seconds,"artifact":filename,"nested_timing":value["timing"]})
            stratum="challenge" if family=="IIIILLLL" else "routine"
            profile["stratum_cells"][stratum]=max(profile["stratum_cells"].get(stratum,0.),cell/len(problems))
            profile["serialization_per_problem_seconds"]=max(profile["serialization_per_problem_seconds"],serial/len(problems))
        if mode=="schrodinger":
            profile["probe_banks"]={}
            for origin,candidates in probes.items():
                value,seconds=timed("probe."+origin,lambda:mechanism_probe(model,candidates)); profile["probe_seconds"]+=seconds
                filename="probe-"+origin+".json"
                payload={"origin":origin,"candidate_ids":[serialize_candidate(c).hex() for c in candidates],"count":len(candidates),"result":value}
                _,io=timed(filename+".serialize",lambda:_write_json(out/filename,payload))
                # The probe workload includes its own serialization, separately from route rows.
                profile["probe_seconds"]+=io
                profile["probe_banks"][origin]={"count":len(candidates),"artifact":filename,"numerical":value["numerical"]}
    def ledger_fixture():
        path=out/"ledger-finalization-fixture.jsonl"; path.write_bytes(ledger.read_bytes())
        begin=time.perf_counter()
        append_once(path,{"entry_id":str(uuid.uuid4()),"recorded_at_utc":utc(),"kind":"fixture_only","stage":"A","charged_seconds":0.})
        return time.perf_counter()-begin
    ledger_seconds,_=timed("ledger_append_fsync_fixture",ledger_fixture)
    profile["ledger_seconds"]=ledger_seconds; profile["ledger_cost_kind"]="measured_append_fsync_on_copy_of_actual_ledger"
    profile["end_to_end_seconds"]=time.perf_counter()-started
    profile["exclusive_phase_seconds"]=sum(p["seconds"] for p in phases)
    if profile["exclusive_phase_seconds"]>profile["end_to_end_seconds"]: raise RuntimeError("overlapping profile phases")
    record={"provenance":runtime_provenance(ids["prepared_sha256"]),"input_ids":ids,"profile":profile,
            "forecast":full_work_forecast(profile),"test_model_predictions":False}
    _write_json(out/"result.json",record); return record

def _cli(argv=None):
    global COMMAND_ARGV
    COMMAND_ARGV=[sys.executable,"-m","schrodinger.route_policy_experiment",*(sys.argv[1:] if argv is None else argv)]
    parser=argparse.ArgumentParser(prog="python -m schrodinger.route_policy_experiment")
    parser.add_argument("command",choices=("prepare","smoke","profile","train","evaluate")); parser.add_argument("--root",type=Path,required=True); parser.add_argument("--ledger",type=Path,required=True); parser.add_argument("--name",required=True); parser.add_argument("--prepared",type=Path); parser.add_argument("--decision",type=Path); parser.add_argument("--seed",type=int,default=1701); parser.add_argument("--mode",choices=("softmax","schrodinger"),default="softmax"); parser.add_argument("--updates",type=int,default=1000); parser.add_argument("--resume",type=Path); parser.add_argument("--resume-hash"); parser.add_argument("--initial-checkpoint",type=Path); parser.add_argument("--checkpoint",type=Path); parser.add_argument("--split",choices=("validation","test"),default="validation")
    args=parser.parse_args(argv); stage="A" if args.command in {"prepare","smoke","profile"} else ("D" if args.command=="evaluate" else "B")
    with OwnedAttempt.begin(args.root,args.ledger,stage,args.name) as attempt:
        if args.command=="prepare": result=command_prepare(attempt.output)
        else:
            if not args.prepared or not args.decision: raise ValueError("prepared and decision are required")
            decision=_load_decision(args.decision)
            if args.command=="smoke": result=command_smoke(attempt.output,args.prepared,decision)
            elif args.command=="profile":
                result=command_profile(attempt.output,args.prepared,decision,args.ledger)
                def profile_finalized(completed):
                    result["profile"]["actual_ledger_append_seconds"]=completed["ledger_append_seconds"]
                    result["profile"]["ledger_seconds"]=max(result["profile"]["ledger_seconds"],completed["ledger_append_seconds"])
                    result["profile"]["actual_ledger_path"]=completed["ledger_path"]
                    result["forecast"]=full_work_forecast(result["profile"])
                    _write_json(attempt.output/"result.json",result)
                attempt.on_finalize=profile_finalized
            elif args.command=="train":
                require_train_decision(decision); _,ids=_prepared_ids(args.prepared); _require_command_binding(decision,ids); _require_run_binding(decision,args); configure_runtime(); train,validation=load_training(),load_validation(); soft,sa,shared=paired_models(args.seed); model=soft if args.mode=="softmax" else sa; bank=heldout_bank(validation.problems); trainbank=training_bank(train.states); resume=None if args.resume is None else {"path":args.resume,"hash":args.resume_hash,"initial_path":args.initial_checkpoint}; result=scheduled_training(model,optimizer(model),MapBalancedSampler(train.states,args.seed),seed=args.seed,source=ids["frozen_source_hash"],config=FROZEN_CONFIG,input_ids=ids,checkpoint_dir=attempt.output/"checkpoints",updates=args.updates,validation=bank,validation_problems=validation.problems,train_probe=training_probe_candidates(trainbank),validation_probe=validation_probe_candidates(bank),support=frozenset(train.support),decision=decision,resume=resume); _write_json(attempt.output/"result.json",{"provenance":runtime_provenance(ids["prepared_sha256"]),"input_ids":ids,"shared_initial_digest":shared,"parameter_count":sum(p.numel() for p in model.parameters()),"result":result,"test_model_predictions":False})
            else:
                configure_runtime()
                payload,ids=_prepared_ids(args.prepared); _require_command_binding(decision,ids)
                if not args.checkpoint: raise ValueError("checkpoint is required for evaluation")
                saved=torch.load(args.checkpoint,weights_only=False); identity=saved.get("identity",{})
                if identity.get("config")!=FROZEN_CONFIG or identity.get("input_ids")!=ids: raise IdentityError("checkpoint is not bound to current frozen records")
                if args.split=="test": raise PermissionError("final main/test inference is not implemented or released in this pilot harness")
                elif decision.get("kind") not in {"pilot","main","smoke_or_profile"}: raise PermissionError("validation evaluation not authorized")
                bundle=load_final_test() if args.split=="test" else load_validation(); support=frozenset(load_training().support); model=RoutePolicy(identity["mode"]); model.load_state_dict(saved["model"]); bank=heldout_bank(bundle.problems); checkpoint_hash=hashlib.sha256(args.checkpoint.read_bytes()).hexdigest(); result=_serializable({"proper":evaluate_proper(model,bank,identity=(checkpoint_hash,identity["mode"],"evaluation")),"greedy":evaluate_rollouts(model,bundle.problems,identity=(checkpoint_hash,identity["mode"],"evaluation"),seed=identity["seed"],splitcode=2 if args.split=="test" else 1,k=1,greedy=True,support=support),"t1_k32":evaluate_rollouts(model,bundle.problems,identity=(checkpoint_hash,identity["mode"],"evaluation"),seed=identity["seed"],splitcode=2 if args.split=="test" else 1,k=32,support=support),"test_model_predictions":args.split=="test"}); _write_json(attempt.output/"result.json",{"provenance":runtime_provenance(ids["prepared_sha256"]),"input_ids":ids,"result":result})
    completed=json.loads((attempt.output/"attempt.json").read_text())
    if completed.get("status")!="COMPLETE": raise ArtifactError("successful attempt artifact missing")
    print(json.dumps({"status":"COMPLETE","output":str(attempt.output),"result_path":str(attempt.output/"result.json")},sort_keys=True))

if __name__ == "__main__": _cli()
