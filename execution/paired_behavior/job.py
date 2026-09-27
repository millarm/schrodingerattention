"""Review-gated, one-shot paired behavior inference (never a training runner)."""
from __future__ import annotations
import hashlib, json, signal, time
from pathlib import Path
import numpy as np
from schrodinger.route_policy import RoutePolicy
from schrodinger.route_policy_data import Problem, load_training, load_validation
from schrodinger.route_policy_evaluation import evaluate_proper, evaluate_rollouts
from schrodinger.route_policy_experiment import IdentityError, OwnedAttempt, _prepared_ids, _serializable, configure_runtime
from schrodinger.route_policy_metrics import ScoreCandidate, ScoreBank, heldout_bank, record_hash, q_array_hash, _bfs, _neighbors
from schrodinger.route_feasibility import signature
from execution.model_training_comparison.baseline_diagnosis_job import dag_aligned_bank, sha, validate_checkpoint
from execution.model_training_comparison.threeway_diagnosis_job import _exact_bank
from execution.paired_behavior.analysis import (AlignmentError, equal_map_summary, load_matched_support, paired_greedy, paired_states, state_summary, valid_route_sets)

ROOT=Path("execution/model_training_comparison"); NAME="paired-behavior-analysis-001"; UPDATES=(1000,4000,8000)
SM={1000:"pilot-1701-softmax-1000",4000:"pilot-1701-softmax-4000",8000:"pilot-1701-softmax-8000"}; SA={1000:"pilot-1701-schrodinger-1000",4000:"paired-behavior-sa-8000",8000:"paired-behavior-sa-8000"}

def _read(path): return json.loads(Path(path).read_text())
def _model(payload):
 m=RoutePolicy(payload["identity"]["mode"]);m.load_state_dict(payload["model"]);m.eval();return m
def _checkpoint(root, owner, update, expected):
 d=Path(root)/owner;p=d/f"checkpoints/update-{update}.pt"; manifest=_read(d/"output-manifest.json")
 if manifest.get(f"checkpoints/update-{update}.pt",{}).get("sha256") != sha(p): raise IdentityError("checkpoint owner hash mismatch")
 import torch
 x=torch.load(p,weights_only=False);i=x.get("identity",{})
 if i.get("update")!=update or i.get("seed")!=1701 or i.get("config")!=expected["config"] or i.get("input_ids")!=expected["input_ids"] or i.get("initial_hash")!=expected["initial_hash"]: raise IdentityError("paired checkpoint identity mismatch")
 return x,sha(p)
def _curves(root, owners):
 rows=[]
 for owner in owners:
  rows += [_readline(x) for x in (Path(root)/owner/"checkpoints/curves.jsonl").read_text().splitlines()]
 rows=sorted(rows,key=lambda x:x["update"])
 if len(rows)!=8000 or [x["update"] for x in rows] != list(range(1,8001)): raise IdentityError("curve update sequence is not exact 1..8000")
 return rows
def _readline(x): return json.loads(x)
def validate_batch_prefixes(root):
 sm=_curves(root,[SM[1000],"pilot-1701-softmax-2000",SM[4000],SM[8000]])
 sa=_curves(root,[SA[1000],SA[4000]])
 if [x["update"] for x in sm]!=list(range(1,8001)) or [x["update"] for x in sa]!=list(range(1,8001)): raise IdentityError("incomplete 1-8000 curve sequence")
 if [x["batch_digest"] for x in sm] != [x["batch_digest"] for x in sa]: raise IdentityError("paired batch digest mismatch")
 return {"updates":len(sm),"digest_sha256":hashlib.sha256("".join(x["batch_digest"] for x in sm).encode()).hexdigest()}
def _row(c,p): return {"canonical":c.canonical,"map_id":c.map_id,"family":c.family,"goal":c.goal,"current":c.current,"q":c.q,"p":p}
def _proper(model, bank, identity):
 x=evaluate_proper(model,bank,identity=identity);return [_row(c,p) for c,p in zip(x["rows"],x["arrays"]["p"])],x
def _event(root,owner,update):
 d=Path(root)/owner; manifest=_read(d/"output-manifest.json")
 if manifest.get("result.json",{}).get("sha256") != sha(d/"result.json"): raise IdentityError("result owner hash mismatch")
 record=_read(d/"result.json")
 _,ids=_prepared_ids(Path(root)/"prepare-001"/"prepared.json")
 if record["input_ids"]!=ids: raise IdentityError("event dataset/source binding mismatch")
 event=next((x for x in record["result"]["events"] if x["update"]==update),None)
 if event is None: raise IdentityError("stored full-validation event missing")
 event["_binding"]={"result_sha256":sha(d/"result.json"),"owner":owner,"event_sha256":_event_digest(event),"input_ids":ids}
 return event
def _event_digest(event):
 return hashlib.sha256(json.dumps({k:v for k,v in event.items() if k!="_binding"},sort_keys=True,separators=(",",":"),allow_nan=False).encode()).hexdigest()
def _verify_event(event):
 if event.get("_binding",{}).get("event_sha256")!=_event_digest(event): raise IdentityError("event mutation/order mismatch")
def _storedproper(event, bank):
 _verify_event(event)
 proper=event["proper"]; rows=proper["rows"]; p=proper["arrays"]["p"]
 if len(rows)!=len(p) or len(rows)!=len(bank.selected): raise IdentityError("stored proper row length mismatch")
 out=[]
 for raw,prob,expect in zip(rows,p,bank.selected):
  canonical=bytes.fromhex(raw["canonical"])
  if (canonical,raw["map_id"],raw["family"],raw["goal"],raw["current"],tuple(raw["q"])) != (expect.canonical,expect.map_id,expect.family,expect.goal,expect.current,expect.q): raise IdentityError("stored proper row/order/q mismatch")
  out.append({"canonical":canonical,"map_id":raw["map_id"],"family":raw["family"],"goal":raw["goal"],"current":raw["current"],"q":raw["q"],"p":prob})
 return out,proper
def _storedroutes(event,key,problems):
 _verify_event(event)
 saved=event["routes"][key]["problems"]
 if len(saved)!=len(problems): raise IdentityError("stored route problem length mismatch")
 out=[]; oracle={}
 for raw,problem in zip(saved,problems):
  if raw["map_id"]!=problem.map_id or raw["family"]!=problem.family: raise IdentityError("stored route dataset order mismatch")
  if len(raw["attempts"])!=(1 if key=="greedy" else 32): raise IdentityError("route sample count mismatch")
  oracle_key=(problem.canonical,problem.goal)
  if oracle_key not in oracle: oracle[oracle_key]=(_bfs(problem.canonical,problem.goal)[0],frozenset(i for i,x in enumerate(problem.canonical) if x))
  distances,walls=oracle[oracle_key]
  for attempt in raw["attempts"]:
   route=attempt["route"]; route=bytes.fromhex(route) if isinstance(route,str) else bytes(route)
   current=problem.start; valid=True
   for action in route:
    if current==problem.goal or action>3: valid=False;break
    current=dict(_neighbors(current,walls)).get(action,-1)
    if current<0: valid=False;break
   valid=valid and current==problem.goal and len(route)==distances.get(problem.start,-1)
   if valid!=bool(attempt["valid"]): raise IdentityError("route validity/order corroboration failed")
   out.append({"canonical":problem.canonical,"map_id":problem.map_id,"family":problem.family,"start":problem.start,"goal":problem.goal,"valid":attempt["valid"],"route":route})
 return out,event["routes"][key]
def _routes(model, problems, identity, support, temperature=1.):
 g=evaluate_rollouts(model,problems,identity=identity,seed=1701,splitcode=1,greedy=True,k=1,support=support,temperature=temperature)
 k=evaluate_rollouts(model,problems,identity=identity,seed=1701,splitcode=1,k=32,support=support,temperature=temperature)
 flat=lambda x:[{"canonical":p.canonical,"map_id":p.map_id,"family":p.family,"start":p.start,"goal":p.goal,"valid":z["valid"],"route":z["route"]} for p,item in zip(problems,x["problems"]) for z in item["attempts"]]
 return flat(g),flat(k),g,k
def _frozen_abc(bound):
 """Deserialize the already selected A/B/C rows verbatim; never match/select."""
 states=[[],[],[]];routes=[[],[],[]]
 for triplet in bound["retained"]:
  for arm in range(3):
   for x in triplet["states"][arm]: states[arm].append(ScoreCandidate(bytes.fromhex(x["canonical"]),x["map_id"],triplet["family"],x["goal"],x["current"],tuple(x["q"])))
   for x in triplet["routes"][arm]: routes[arm].append(Problem(bytes.fromhex(x["canonical"]),x["map_id"],triplet["family"],x["start"],x["goal"],x["length"],x["M"],x["Mnovel"]))
 return tuple(_exact_bank(x) for x in states),tuple(tuple(x) for x in routes)
def _without_cache(x): return {k:v for k,v in x.items() if k!="cache"}
def _load_sm_abc(root,frozen):
 path=Path(root)/"threeway-diagnosis-001"/"threeway_diagnosis.json"
 if sha(path)!="46ca7f60bca1ec2a5224d479623b0b69385f36f9acb69e55f3da895c444b9720": raise IdentityError("frozen softmax ABC hash mismatch")
 result=_read(path)
 if result["status"]!="COMPLETE" or result["support"]!=frozen["data"]["triplets"]: raise IdentityError("SM ABC support mismatch")
 return result,sha(path)
def _abc_compare(sm,sa,bank):
 # Compare exact row/q order before assembling paired proper scores.
 smrows,_=_storedproper_unbound(sm["proper"],bank)
 sarows=[_row(c,p) for c,p in zip(sa["proper"]["rows"],sa["proper"]["arrays"]["p"])]
 paired=state_summary(paired_states(smrows,sarows))
 summary={m:{"sm":sm["proper_aggregate"]["routine"][m],"sa":paired["equal_map"]["strata"]["routine"]["sa_"+m]} for m in ("ce","kl","brier","nonoptimal_mass")}
 for metric in summary: summary[metric]["sa_minus_sm"]=summary[metric]["sa"]-summary[metric]["sm"]
 for key in ("greedy","t1_k32"):
  x,y=sm[key]["strata"]["routine"]["Q"],sa[key]["strata"]["routine"]["Q"]
  summary[key]={"sm":x,"sa":y,"sa_minus_sm":y-x}
 return {"sm":sm,"sa":sa,"paired_state":paired,"summary":summary}
def _storedproper_unbound(proper,bank):
 # For separately immutable-hash-bound ABC results, reuse the same literal adapter.
 event={"proper":proper};event["_binding"]={"event_sha256":_event_digest(event)}
 return _storedproper(event,bank)
def _qc(sa,problems,sa_identity,support,sm_stored,sa_stored):
 """Predeclared 8k grid, selecting only the closest qualifying descriptive point."""
 target=sm_stored["mixture"]["Q"]; target_strata={s:sm_stored["strata"].get(s,{}).get("Q") for s in ("routine","challenge")}
 grid=[]
 for temperature,result in ((1.,sa_stored),(.75,evaluate_rollouts(sa,problems,identity=sa_identity,seed=1701,splitcode=1,k=32,support=support,temperature=.75)),(1.25,evaluate_rollouts(sa,problems,identity=sa_identity,seed=1701,splitcode=1,k=32,support=support,temperature=1.25))):
  mixture=result["mixture"]["Q"]; strata={s:result["strata"].get(s,{}).get("Q") for s in ("routine","challenge")}
  grid.append({"temperature":temperature,"quality":mixture,"strata_quality":strata,"novelty":result["mixture"].get("U_novel"),"raw":_without_cache(result)})
 chosen=min(grid,key=lambda x:(abs(x["quality"]-target),x["temperature"])); matched=abs(chosen["quality"]-target)<=.02 and all(chosen["strata_quality"][s] is not None and target_strata[s] is not None and abs(chosen["strata_quality"][s]-target_strata[s])<=.03 for s in target_strata)
 return {"target_sm_t1_quality":target,"grid":grid,"selected":chosen["temperature"],"matched":matched}
def run(root=ROOT):
 root=Path(root);configure_runtime()
 with OwnedAttempt.begin(root,root/"ledger.jsonl","D",NAME) as attempt:
  signal.setitimer(signal.ITIMER_REAL,min(296.,signal.getitimer(signal.ITIMER_REAL)[0]));started=time.perf_counter();_,prepared=_prepared_ids(root/"prepare-001"/"prepared.json")
  _,initial,expected,_=validate_checkpoint(root,0,prepared_ids=prepared);digests=validate_batch_prefixes(root)
  sa_result=_read(root/SA[1000]/"result.json")
  sm_result=_read(root/SM[1000]/"result.json")
  if sa_result.get("shared_initial_digest") != sm_result.get("shared_initial_digest"): raise IdentityError("shared initial parameter digest mismatch")
  sa_expected=dict(expected);sa_expected["initial_hash"]=sa_result["result"]["initial_hash"]
  validation=load_validation();training=load_training();bank=heldout_bank(validation.problems);support=frozenset(training.support); frozen=load_matched_support(root/"threeway-diagnosis-001"/"matched_support.json");abc_banks,abc_routes=_frozen_abc(frozen); sm_abc,sm_abc_hash=_load_sm_abc(root,frozen)
  output={"status":"COMPLETE","digests":digests,"identity":expected,"updates":{},"source_hash":sha(Path(__file__)),"analysis_source_hash":sha(Path(__file__).with_name("analysis.py")),"plan_hash":sha(Path(__file__).with_name("plan.md")),"matched_support_sha256":frozen["sha256"],"sm_abc_sha256":sm_abc_hash,"validation_problem_order":list(validation.problems),"route_binding_limitation":"Historical route rows omit start/goal; identities follow immutable reviewed producer and bound dataset order. Per-route verifier corroborates but cannot prove permutations among all-invalid groups."}
  for u in UPDATES:
   smp,smh=_checkpoint(root,SM[u],u,expected);sap,sah=_checkpoint(root,SA[u],u,sa_expected); sm,sa=_model(smp),_model(sap)
   if sm_abc["checkpoint_hashes"][str(u)]!=smh: raise IdentityError("SM ABC checkpoint mismatch")
   sme=_event(root,SM[u],u);sae=_event(root,SA[u],u);smr,smpx=_storedproper(sme,bank);sar,sapx=_storedproper(sae,bank); states=paired_states(smr,sar)
   smg,smgraw=_storedroutes(sme,"greedy",validation.problems);smk,smkraw=_storedroutes(sme,"t1_k32",validation.problems);sag,sagraw=_storedroutes(sae,"greedy",validation.problems);sak,sakraw=_storedroutes(sae,"t1_k32",validation.problems)
   require=lambda a,b: paired_greedy(a,b)
   route_rows=[]
   for i,(a,b) in enumerate(zip(validation.problems, validation.problems)):
    route_rows.append({"family":a.family,"map_id":a.map_id,**valid_route_sets(smk[i*32:(i+1)*32],sak[i*32:(i+1)*32],support,signature)})
   cohorts={}
   for arm,name in enumerate("ABC"):
    split=0 if name in "AB" else 1; proper=evaluate_proper(sa,abc_banks[arm],identity=(sah,"sa-abc",u)); greedy=evaluate_rollouts(sa,abc_routes[arm],identity=(sah,"sa-abc",u),seed=1701,splitcode=split,greedy=True,k=1,support=support); k32=evaluate_rollouts(sa,abc_routes[arm],identity=(sah,"sa-abc",u),seed=1701,splitcode=split,k=32,support=support)
    saraw={"proper":_without_cache(proper),"greedy":_without_cache(greedy),"t1_k32":_without_cache(k32),"problem_order":abc_routes[arm]}
    cohorts[name]=_abc_compare(sm_abc["scores"][str(u)][name],saraw,abc_banks[arm])
   output["updates"][str(u)]={"state":state_summary(states),"proper_sm":smpx["weighted"],"proper_sa":sapx["weighted"],"greedy":require(smg,sag),"route_sets":equal_map_summary(route_rows,tuple(sorted(route_rows[0].keys()-{"family","map_id","raw_sets"})) if route_rows else ()),"frozen_abc":cohorts,"checkpoint_hashes":{"sm":smh,"sa":sah},"event_bindings":{"sm":sme["_binding"],"sa":sae["_binding"]},"t1_stored":{"sm":smkraw,"sa":sakraw}}
   if u==8000: output["quality_control"]=_qc(sa,validation.problems,(sah,"sa-qc",u),support,smkraw,sakraw)
  output["elapsed_seconds"]=time.perf_counter()-started
  (attempt.output/"paired_behavior.json").write_text(json.dumps(_serializable(output),sort_keys=True,indent=2,allow_nan=False));return output
if __name__=="__main__":run()
