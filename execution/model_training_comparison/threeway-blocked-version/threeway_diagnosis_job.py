"""Review-gated, outcome-blind A/B/C checkpoint diagnosis."""
from __future__ import annotations
import hashlib,json,signal,time
from collections import defaultdict
from pathlib import Path
import numpy as np
from schrodinger.route_policy_data import Problem,load_training,load_validation
from schrodinger.route_policy_metrics import ScoreCandidate,ScoreBank,_bfs,_q_from_oracle,serialize_candidate,record_hash,q_array_hash
from schrodinger.route_policy_evaluation import evaluate_proper,evaluate_rollouts
from schrodinger.route_policy_experiment import IdentityError,OwnedAttempt,_prepared_ids,_serializable,configure_runtime
from execution.model_training_comparison.baseline_diagnosis_job import _model,sha,validate_checkpoint
ROOT=Path("execution/model_training_comparison"); NAME="threeway-diagnosis-001"; PREFIX=b"goaldiag-route-v1\\0"
def _rank_problem(p): return(hashlib.sha256(PREFIX+p.canonical+p.start.to_bytes(2,"big")+p.goal.to_bytes(2,"big")).digest(),p.start,p.goal)
def _rank_state(c): return(hashlib.sha256(serialize_candidate(c)).digest(),c.goal,c.current)
def _key(x): return(x.canonical,x.start,x.goal) if hasattr(x,"start") else(x.canonical,x.current,x.goal)
def _dag(p,cache=None):
 cache={} if cache is None else cache;k=(p.canonical,p.goal)
 if k not in cache:
  d,n=_bfs(p.canonical,p.goal);cache[k]=(d,n,frozenset(i for i,x in enumerate(p.canonical) if x))
 d,n,w=cache[k];back,_=_bfs(p.canonical,p.start)
 if p.goal not in back:return ()
 return tuple(ScoreCandidate(p.canonical,p.map_id,p.family,p.goal,x,_q_from_oracle(w,p.goal,x,d,n)) for x in d if x!=p.goal and x in back and back[x]+d[x]==back[p.goal])
def _startq(p,cache):
 k=(p.canonical,p.goal)
 if k not in cache:
  d,n=_bfs(p.canonical,p.goal);cache[k]=(d,n,frozenset(i for i,x in enumerate(p.canonical) if x))
 d,n,w=cache[k];return _q_from_oracle(w,p.goal,p.start,d,n)
def _exact_bank(rows):
 ordered=tuple(rows)
 if not ordered or len({(x.canonical,x.goal,x.current)for x in ordered})!=len(ordered):raise IdentityError("invalid matched bank")
 return ScoreBank(ordered,ordered,record_hash(ordered),record_hash(ordered),q_array_hash(ordered),tuple(sorted((m,sum(x.map_id==m for x in ordered))for m in {x.map_id for x in ordered})))
def _joint(rows,key,rank,cap,total):
 bins=[defaultdict(list) for _ in range(3)]
 for i,g in enumerate(rows):
  for x in {_key(x):x for x in g}.values():bins[i][key(x)].append(x)
 keys=sorted(set().union(*(set(x) for x in bins)));o=[[sorted(b.get(k,()),key=rank) for k in keys] for b in bins]
 q={str(k):min(cap,*(len(o[i][j]) for i in range(3))) for j,k in enumerate(keys)};out=[[]for _ in range(3)]
 for r in range(max(q.values(),default=0)):
  for j,k in enumerate(keys):
   if r<q[str(k)] and len(out[0])<total:
    for i in range(3):out[i].append(o[i][j][r])
 return tuple(tuple(x)for x in out),{"supply":{str(k):[len(o[i][j])for i in range(3)]for j,k in enumerate(keys)},"quotas":q}
def match_triplet(a,b,c):
 cache={};routes,rm=_joint((a,b,c),lambda p:(p.length,sum(q>0 for q in _startq(p,cache))),_rank_problem,2,6)
 if len(routes[0])<3:return None,{"route":rm,"reason":"route_support"}
 states,sm=_joint(tuple(tuple(s for p in x for s in _dag(p,cache))for x in routes),lambda s:(_bfs(s.canonical,s.goal)[0][s.current],sum(q>0 for q in s.q)),_rank_state,2,32)
 if len(states[0])<8:return None,{"route":rm,"state":sm,"reason":"state_support"}
 banks=tuple(_exact_bank(x)for x in states)
 return {"routes":routes,"states":states,"banks":banks},{"route":rm,"state":sm}
def b_candidates(p,saved):
 seen={s.goal for s in saved if s.canonical==p.canonical};walls={i for i,x in enumerate(p.canonical)if x};out=[]
 for goal in range(144):
  if goal in walls or goal in seen:continue
  d,n=_bfs(p.canonical,goal)
  for start,length in d.items():
   if start!=goal and length in(14,15,16):out.append(Problem(p.canonical,p.map_id,p.family,start,goal,length,n[start],None))
 return tuple(out)
def validate_overlap(a,b,saved):
 keys={(s.canonical,s.current,s.goal)for s in saved};cache={}
 if any((s.canonical,s.current,s.goal)not in keys for p in a for s in _dag(p,cache)):raise IdentityError("A state absent from saved support")
 if any((s.canonical,s.current,s.goal)in keys for p in b for s in _dag(p,cache)):raise IdentityError("B state overlaps saved support")
def _ids(x):return [{"canonical":p.canonical.hex(),"map_id":p.map_id,"start":p.start,"goal":p.goal,"length":p.length,"M":p.M,"Mnovel":p.Mnovel}for p in x]
def _sids(x):return [{"canonical":s.canonical.hex(),"map_id":s.map_id,"goal":s.goal,"current":s.current,"q":s.q,"distance_to_goal":_bfs(s.canonical,s.goal)[0][s.current],"teacher_entropy":float(-sum(q*np.log(q)for q in s.q if q)),"optimal_actions":sum(q>0 for q in s.q)}for s in x]
def _hash(x):return hashlib.sha256(json.dumps(_serializable(x),sort_keys=True,separators=(",",":")).encode()).hexdigest()
def _proper_aggregate(result):
 by=defaultdict(list)
 for i,row in enumerate(result["rows"]):by[(row.family,row.map_id)].append(i)
 per={f"{f}:{m}":{k:float(np.mean(v[ix]))for k,v in result["arrays"].items()if k!="p"}for(f,m),ix in by.items()}
 family={f:{k:float(np.mean([x[k]for key,x in per.items()if key.startswith(f+":")]))for k in next(iter(per.values()))}for f in("IIIIIIII","LLLLLLLL")}
 return {"per_map":per,"family":family,"routine":{k:float(np.mean([x[k]for x in per.values()]))for k in next(iter(per.values()))}}
def run(root=ROOT):
 root=Path(root);configure_runtime()
 with OwnedAttempt.begin(root,root/"ledger.jsonl","D",NAME)as attempt:
  signal.setitimer(signal.ITIMER_REAL,min(70.,signal.getitimer(signal.ITIMER_REAL)[0]));started=time.perf_counter();t=load_training();v=load_validation();tm=defaultdict(list);vm=defaultdict(list)
  for p in t.problems:tm[p.family,p.canonical].append(p)
  for p in v.problems:
   if p.family in("IIIIIIII","LLLLLLLL"):vm[p.family,p.canonical].append(p)
  triples=[];support=[]
  for family in("IIIIIIII","LLLLLLLL"):
   aa=sorted(c for f,c in tm if f==family)[:12];cc=sorted(c for f,c in vm if f==family)[:12]
   for rank,(ac,vc)in enumerate(zip(aa,cc)):
    A=tuple(tm[family,ac]);B=b_candidates(A[0],t.states);C=tuple(vm[family,vc]);m,meta=match_triplet(A,B,C);item={"family":family,"rank":rank,"a_map":ac.hex(),"c_map":vc.hex(),"candidate_counts":[len(A),len(B),len(C)],"matching":meta}
    if not m:item["excluded"]=True;support.append(item);continue
    validate_overlap(m["routes"][0],m["routes"][1],t.states);item.update({"excluded":False,"routes":[_ids(x)for x in m["routes"]],"states":[_sids(x)for x in m["states"]]});item["cohort_hashes"]=[_hash(x)for x in item["states"]];support.append(item);triples.append((family,rank,m))
  pre={"status":"MATCHED_SUPPORT_INSUFFICIENT","triplets":support,"retained_by_family":{f:sum(x[0]==f for x in triples)for f in("IIIIIIII","LLLLLLLL")}}
  (attempt.output/"matched_support.json").write_text(json.dumps(_serializable(pre),sort_keys=True,indent=2))
  if any(x<8 for x in pre["retained_by_family"].values()):(attempt.output/"threeway_diagnosis.json").write_text(json.dumps(_serializable(pre),sort_keys=True,indent=2));return pre
  _,prepared=_prepared_ids(root/"prepare-001"/"prepared.json");loaded={};expected=None
  _,initial,expected,_=validate_checkpoint(root,0,prepared_ids=prepared)
  for u in(1000,4000,8000):_,p,expected,h=validate_checkpoint(root,u,expected=expected,prepared_ids=prepared);loaded[u]=(p,h)
  states=[[],[],[]];routes=[[],[],[]]
  for _,_,m in triples:
   for i in range(3):states[i]+=m["states"][i];routes[i]+=m["routes"][i]
  banks=tuple(_exact_bank(x)for x in states)
  scores={}
  for u,(p,h)in loaded.items():
   model=_model(p);scores[str(u)]={}
   for i,name in enumerate("ABC"):
    identity=(h,"softmax","threeway");proper=evaluate_proper(model,banks[i],identity=identity);split=0 if name in"AB"else 1;g=evaluate_rollouts(model,routes[i],identity=identity,seed=1701,splitcode=split,greedy=True,k=1,support=frozenset(t.support));k=evaluate_rollouts(model,routes[i],identity=identity,seed=1701,splitcode=split,k=32,support=frozenset(t.support))
    scores[str(u)][name]={"proper":{z:y for z,y in proper.items()if z!="cache"},"proper_aggregate":_proper_aggregate(proper),"greedy":{z:y for z,y in g.items()if z!="cache"},"t1_k32":{z:y for z,y in k.items()if z!="cache"}}
  out={"status":"COMPLETE","support":support,"checkpoint_hashes":{str(k):v[1]for k,v in loaded.items()},"checkpoint_identity":expected,"scores":scores,"elapsed_seconds":time.perf_counter()-started,"source_hashes":{"script":sha(Path(__file__)),"metrics":sha(Path("schrodinger/route_policy_metrics.py")),"evaluator":sha(Path("schrodinger/route_policy_evaluation.py"))}}
  (attempt.output/"threeway_diagnosis.json").write_text(json.dumps(_serializable(out),sort_keys=True,indent=2,allow_nan=False));return out
if __name__=="__main__":run()
