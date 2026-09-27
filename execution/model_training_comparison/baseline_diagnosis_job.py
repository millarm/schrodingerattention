"""One bounded, inference-only diagnostic for the accepted softmax baseline."""
from __future__ import annotations
import hashlib, json, signal, time
from pathlib import Path
import numpy as np
import torch
from schrodinger.route_policy import RoutePolicy
from schrodinger.route_policy_data import legal_mask, load_training, load_validation
from schrodinger.route_policy_evaluation import evaluate_proper, evaluate_rollouts
from schrodinger.route_policy_experiment import (FROZEN_CONFIG, IdentityError, OwnedAttempt,
    _prepared_ids, _serializable, configure_runtime, state_hash_from_state)
from schrodinger.route_policy_metrics import ScoreCandidate, _bank, _bfs, _q_from_oracle, training_bank

ROOT=Path("execution/model_training_comparison"); NAME="baseline-diagnosis-001"; CHECKPOINTS={
    0:("pilot-1701-softmax-1000","checkpoints/initial.pt"),1000:("pilot-1701-softmax-1000","checkpoints/update-1000.pt"),
    4000:("pilot-1701-softmax-4000","checkpoints/update-4000.pt"),8000:("pilot-1701-softmax-8000","checkpoints/update-8000.pt")}

def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def jdump(path, value): Path(path).write_text(json.dumps(_serializable(value),sort_keys=True,indent=2,allow_nan=False))
def _walls(canonical): return frozenset(i for i,x in enumerate(canonical) if x)
def _check_bank(bank):
    for c in bank.selected:
        if not np.isclose(sum(c.q),1.) or any(q and not ok for q,ok in zip(c.q,legal_mask(c))): raise IdentityError("malformed selected oracle q")
    return bank

def dag_aligned_bank(problems):
    """Only nonterminal cells on each saved start-to-goal shortest DAG."""
    rows={}
    for p in problems:
        to_goal,count=_bfs(p.canonical,p.goal); from_start,_=_bfs(p.canonical,p.start)
        if p.goal not in from_start: raise IdentityError("saved validation problem is unreachable")
        walls=_walls(p.canonical); length=from_start[p.goal]
        for current in to_goal:
            if current!=p.goal and current in from_start and from_start[current]+to_goal[current]==length:
                c=ScoreCandidate(p.canonical,p.map_id,p.family,p.goal,current,_q_from_oracle(walls,p.goal,current,to_goal,count))
                rows[(c.canonical,c.map_id,c.family,c.goal,current)]=c
    return _bank(rows.values())

def validate_checkpoint(root, update, *, expected=None, prepared_ids=None):
    owner,relative=CHECKPOINTS[update]; directory=Path(root)/owner; checkpoint=directory/relative
    manifest=json.loads((directory/"output-manifest.json").read_text()); declared=manifest.get(relative,{ }).get("sha256")
    actual=sha(checkpoint)
    if actual!=declared: raise IdentityError("checkpoint owner-manifest hash mismatch")
    payload=torch.load(checkpoint,weights_only=False); identity=payload.get("identity")
    if not isinstance(identity,dict) or identity.get("seed")!=1701 or identity.get("mode")!="softmax" or identity.get("update")!=update: raise IdentityError("checkpoint mode/seed/update mismatch")
    if identity.get("config")!=FROZEN_CONFIG or identity.get("source")!=identity.get("input_ids",{}).get("frozen_source_hash"): raise IdentityError("checkpoint source/config mismatch")
    if prepared_ids is not None and (identity.get("source")!=prepared_ids["frozen_source_hash"] or identity.get("input_ids")!=prepared_ids): raise IdentityError("checkpoint prepared/input identity mismatch")
    if expected is None:
        if update!=0 or identity.get("parent_hash") is not None or state_hash_from_state(payload["model"])!=identity.get("initial_hash"): raise IdentityError("initial checkpoint identity mismatch")
        expected={k:identity[k] for k in ("source","config","initial_hash","input_ids")}
    elif {k:identity.get(k) for k in expected}!={k:expected[k] for k in expected}: raise IdentityError("checkpoint initial/input identity mismatch")
    return checkpoint,payload,expected,actual

def _bank_meta(bank):
    return {"candidate_hash":bank.candidate_hash,"selected_hash":bank.selected_hash,"q_hash":bank.q_hash,"map_counts":bank.map_counts,
            "selected":[{"canonical":c.canonical.hex(),"map_id":c.map_id,"family":c.family,"goal":c.goal,"current":c.current,"q":c.q} for c in bank.selected]}
def _properties(bank):
    out={}
    for c in bank.selected:
        dist,_=_bfs(c.canonical,c.goal); key=str(c.map_id); out.setdefault(key,[]).append({"distance_to_goal":dist[c.current],"teacher_entropy":float(-sum(x*np.log(x) for x in c.q if x)),"optimal_actions":sum(x>0 for x in c.q)})
    return out
def _broad(root, update):
    owner,_=CHECKPOINTS[update]; events=json.loads((Path(root)/owner/"result.json").read_text())["result"]["events"]
    row=next((x for x in events if x["update"]==update),None)
    if row is None: raise IdentityError("matching stored broad checkpoint event missing")
    return row["proper"]
def _model(payload):
    model=RoutePolicy("softmax"); model.load_state_dict(payload["model"]); model.eval(); return model
def _arrays(result): return {k:v for k,v in result["arrays"].items() if k!="p"}
def _without_cache(result): return {k:v for k,v in result.items() if k!="cache"}

def run(root=ROOT):
    root=Path(root); ledger=root/"ledger.jsonl"; configure_runtime()
    with OwnedAttempt.begin(root,ledger,"D",NAME) as attempt:
        remaining=signal.getitimer(signal.ITIMER_REAL)[0]; signal.setitimer(signal.ITIMER_REAL,min(70.,remaining))
        started=time.perf_counter(); scores={}; rollouts=None
        _,prepared_ids=_prepared_ids(root/"prepare-001"/"prepared.json")
        _,payload,expected,digest=validate_checkpoint(root,0,prepared_ids=prepared_ids); loaded={0:(payload,digest)}
        for update in (1000,4000,8000):
            _,p,_,h=validate_checkpoint(root,update,expected=expected,prepared_ids=prepared_ids); loaded[update]=(p,h)
        training=load_training(); validation=load_validation(); trainbank=_check_bank(training_bank(training.states)); valbank=_check_bank(dag_aligned_bank(validation.problems))
        for update,(checkpoint_hash_payload,checkpoint_hash) in loaded.items():
            model=_model(checkpoint_hash_payload); identity=(checkpoint_hash,"softmax","baseline_diagnosis")
            scores[str(update)]={"training":evaluate_proper(model,trainbank,identity=identity),"validation_dag":evaluate_proper(model,valbank,identity=identity),"stored_broad_comparator":_broad(root,update)}
            if update==8000:
                rollouts={"greedy":_without_cache(evaluate_rollouts(model,training.problems,identity=identity,seed=1701,splitcode=0,greedy=True,k=1,support=frozenset(training.support))),"t1_k32":_without_cache(evaluate_rollouts(model,training.problems,identity=identity,seed=1701,splitcode=0,k=32,support=frozenset(training.support)))}
        raw={u:{"training":_arrays(x["training"]),"validation_dag":_arrays(x["validation_dag"])} for u,x in scores.items()}
        summary={u:{"training":x["training"]["weighted"],"validation_dag":x["validation_dag"]["weighted"],"stored_broad_comparator":x["stored_broad_comparator"]} for u,x in scores.items()}
        result={"status":"COMPLETE","checkpoint_hashes":{str(k):v[1] for k,v in loaded.items()},"checkpoint_identity":expected,
                "banks":{"training":_bank_meta(trainbank),"validation_dag":_bank_meta(valbank)},"state_properties":{"training":_properties(trainbank),"validation_dag":_properties(valbank)},
                "raw_scores":raw,"summary":summary,"training_rollouts_update_8000":rollouts,"elapsed_seconds":time.perf_counter()-started,
                "source_hashes":{"diagnostic_script":sha(Path(__file__)),"accepted_metrics":sha(Path("schrodinger/route_policy_metrics.py")),"accepted_evaluator":sha(Path("schrodinger/route_policy_evaluation.py"))},
                "config_hash":hashlib.sha256(json.dumps(expected["config"],sort_keys=True,separators=(",",":" )).encode()).hexdigest(),"input_hashes":{"prepared":expected["input_ids"]["prepared_sha256"],"frozen_source":expected["source"]}}
        jdump(attempt.output/"baseline_diagnosis.json",result)
    return result

if __name__=="__main__": run()
