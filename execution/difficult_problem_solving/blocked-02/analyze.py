"""D0 retained-route diagnosis.  It never loads models, checkpoints, or test data."""
from __future__ import annotations
import argparse, hashlib, json, math, signal, sys, time
from collections import Counter, defaultdict
from pathlib import Path
from schrodinger import route_policy_experiment as core
from schrodinger.route_policy_data import load_validation
from execution.seed_replication import train as wrapper
from execution.seed_replication.analyze import _owner_record, _manifest_file
from execution.paired_behavior.job import _event_digest, _storedroutes

ROOT=wrapper.ROOT; SEEDS=(1702,1703,1704,1705); UPDATES=(1000,2000,4000,8000); KS=(1,2,4,8,16,32)
LENGTH_BINS=("14","15","16"); DETOUR_BINS=("0","2+"); MULTIPLICITY_BINS=("1-8","9-64","65+")
WORKSPACE=Path(__file__).resolve().parents[2]; PLAN=WORKSPACE/"difficult_problem_solving_plan.md"; PLAN_SHA="c31c3ee84131ec4e96dbbd42e073a4ec96be63a0b3fc65058a18275714c035fe"
SPEC=WORKSPACE/"execution/difficult_problem_solving/spec.md"; APPROVAL=WORKSPACE/"execution/difficult_problem_solving/approval.md"
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def choose(n,k): return 0 if n<k or k<0 else math.comb(n,k)
def bag(c,counts,k):
    den=choose(32,k); passed=1-choose(32-c,k)/den
    distinct=sum(1-choose(32-n,k)/den for n in counts.values())
    return {"pass":passed,"u_per_k":distinct/k,"expected_distinct":distinct}
def prefix(attempts,k,m):
    valid=[x for x in attempts[:k] if x["valid"]]; u=len({bytes(x["route"]) for x in valid})
    return {"pass":float(bool(valid)),"Q":len(valid)/k,"u_per_k":u/k,"u_per_M":u/m}
def metric(attempts,m):
    if len(attempts)!=32 or m<=0: raise core.IdentityError("invalid retained bag/M")
    valid=[x for x in attempts if x["valid"]]; counts=Counter(bytes(x["route"]) for x in valid); c=len(valid); u=len(counts)
    return {"c":c,"u":u,"c_per_32":c/32,"u_if_solved":None if not c else u,"duplicate_concentration":None if not c else sum((n/c)**2 for n in counts.values()),"valid_route_counts":{x.hex():n for x,n in counts.items()},"bag":{str(k):bag(c,counts,k)|{"u_per_M":bag(c,counts,k)["expected_distinct"]/m} for k in KS},"prefix":{str(k):prefix(attempts,k,m) for k in KS}}
def geom(p):
    r,c=divmod(p.start,12); gr,gc=divmod(p.goal,12); d=p.length-(abs(r-gr)+abs(c-gc))
    if d<0 or d%2 or p.M<=0: raise core.IdentityError("invalid geometry")
    return {"length":str(p.length),"detour":"0" if d==0 else "2+","multiplicity":"1-8" if p.M<=8 else "9-64" if p.M<=64 else "65+"}
def equal(rows):
    by=defaultdict(list)
    for r in rows: by[r["map_id"]].append(r["value"])
    return None if not by else sum(sum(x)/len(x) for x in by.values())/len(by)
def gate(seed_maps):
    if set(seed_maps)!=set(SEEDS) or any(len(maps)!=8 or set(maps)!={m for m in next(iter(seed_maps.values()))} for maps in seed_maps.values()): raise core.IdentityError("nonexact fresh seed/challenge map gate input")
    deltas={s:equal([{"map_id":m,"value":v["sa"]-v["sm"]} for m,v in maps.items()]) for s,maps in seed_maps.items()}
    loo={m:sum(equal([{"map_id":x,"value":v["sa"]-v["sm"]} for x,v in maps.items() if x!=m]) for maps in seed_maps.values())/4 for m in next(iter(seed_maps.values()))}
    return {"seed_deltas":deltas,"positive_seed_count":sum(x>0 for x in deltas.values()),"leave_one_map_out":loo,"integrity":True,"pass":sum(x>0 for x in deltas.values())>=3 and all(x>0 for x in loo.values())}
def summaries(rows):
    """All-problem and solved-only summaries, equal problems within maps then maps."""
    out={"strata":{},"geometry":{axis:{} for axis in("length","detour","multiplicity")}}
    for label,group in (("routine",[r for r in rows if r["family"]!="IIIILLLL"]),("challenge",[r for r in rows if r["family"]=="IIIILLLL"])):
      out["strata"][label]={}
      for mode in("sm","sa"):
       x=[r for r in group if r["mode"]==mode]; out["strata"][label][mode]={"problems":len(x),"maps":len({r["map_id"]for r in x}),"zeros":sum(r["c"]==0 for r in x),"all_problem":{str(k):equal([{"map_id":r["map_id"],"value":r["bag"][str(k)]["pass"]}for r in x])for k in KS},"solved_support":sum(r["c"]>0 for r in x),"conditional":{str(k):equal([{"map_id":r["map_id"],"value":r["bag"][str(k)]["u_per_M"]}for r in x if r["c"]>0])for k in KS}}
    for axis in out["geometry"]:
      for value in sorted({r[axis]for r in rows}):
       x=[r for r in rows if r[axis]==value]; out["geometry"][axis][value]={"problems":len(x),"maps":len({r["map_id"]for r in x}),"metrics":{m:equal([{"map_id":r["map_id"],"value":r[m]}for r in x]) for m in("c_per_32","u")}}
    return out
def pkey(p): return (p.canonical.hex(),p.map_id,p.family,p.start,p.goal,p.length,p.M)
def panel(problems):
    if len(problems)!=512 or len({pkey(p)for p in problems})!=512: raise core.IdentityError("validation problem identity panel mismatch")
    maps=defaultdict(list)
    for p in problems: maps[p.map_id].append(p)
    if len(maps)!=32 or any(len(x)!=16 for x in maps.values()): raise core.IdentityError("validation map/problem counts mismatch")
    challenge={m for m,x in maps.items() if x[0].family=="IIIILLLL"}; families=Counter(x[0].family for x in maps.values())
    if families!={"IIIILLLL":8,"IIIIIIII":12,"LLLLLLLL":12} or any(any(p.family!=x[0].family for p in x) for x in maps.values()): raise core.IdentityError("validation family panel mismatch")
    return maps,challenge
def _mean(xs): return None if not xs else sum(xs)/len(xs)
def assemble(problems,bags):
    """Pure D0 assembly shared with tests; bags are exact retained 32-attempt rows."""
    maps,challenge=panel(problems); expected=[pkey(p)for p in problems]; rows=[]
    for (seed,mode), supplied in bags.items():
      if seed not in SEEDS or mode not in("sm","sa") or [pkey(p)for p,_a,_e in supplied]!=expected: raise core.IdentityError("mode/seed retained order mismatch")
      for p,a,e in supplied:
       q=metric(a,p.M); g=geom(p); rows.append({"seed":seed,"mode":mode,"identity":{"canonical":p.canonical.hex(),"map_id":p.map_id,"family":p.family,"start":p.start,"goal":p.goal,"length":p.length,"M":p.M},"event":e,**g,**q})
    for seed in SEEDS:
      for mode in("sm","sa"):
       if sum(r["seed"]==seed and r["mode"]==mode for r in rows)!=512: raise core.IdentityError("missing seed/mode problem cell")
    def aggregate(group):
      result={"problems":len(group),"maps":len({r["identity"]["map_id"]for r in group}),"zeros":sum(r["c"]==0 for r in group),"all_problem":{},"solved_only":{"support":sum(r["c"]>0 for r in group)}}
      for k in KS:
       result["all_problem"][str(k)]={name:equal([{"map_id":r["identity"]["map_id"],"value":r["bag"][str(k)][name]}for r in group]) for name in("pass","u_per_k","u_per_M")}
       result["solved_only"][str(k)]={name:equal([{"map_id":r["identity"]["map_id"],"value":r["bag"][str(k)][name]}for r in group if r["c"]>0]) for name in("u_per_k","u_per_M")}
      result["empirical_c_per_32"]=equal([{"map_id":r["identity"]["map_id"],"value":r["c_per_32"]}for r in group]); result["duplicate_concentration"]=equal([{"map_id":r["identity"]["map_id"],"value":r["duplicate_concentration"]}for r in group if r["c"]>0]); result["valid_count_distribution"]={"c":dict(Counter(r["c"]for r in group)),"u":dict(Counter(r["u"]for r in group))}; result["prefix_sensitivity"]={str(k):{n:equal([{"map_id":r["identity"]["map_id"],"value":r["prefix"][str(k)][n]}for r in group])for n in("pass","Q","u_per_k","u_per_M")}for k in KS}; return result
    summary={}; paired={}
    for seed in SEEDS:
      summary[str(seed)]={}; paired[str(seed)]={}
      for stratum,ms in (("routine",set(maps)-challenge),("challenge",challenge)):
       summary[str(seed)][stratum]={m:aggregate([r for r in rows if r["seed"]==seed and r["mode"]==m and r["identity"]["map_id"]in ms]) for m in("sm","sa")}
       summary[str(seed)][stratum]["sa_minus_sm"]={k:summary[str(seed)][stratum]["sa"]["all_problem"][str(k)]["pass"]-summary[str(seed)][stratum]["sm"]["all_problem"][str(k)]["pass"] for k in KS}
      for m in maps:
       a=[r for r in rows if r["seed"]==seed and r["identity"]["map_id"]==m]; sm={r["identity"]["canonical"]+":"+str(r["identity"]["start"])+":"+str(r["identity"]["goal"]):r for r in a if r["mode"]=="sm"}; sa={r["identity"]["canonical"]+":"+str(r["identity"]["start"])+":"+str(r["identity"]["goal"]):r for r in a if r["mode"]=="sa"}
       if len(sm)!=16 or list(sm)!=list(sa): raise core.IdentityError("paired challenge cell mismatch")
       outcomes=Counter(("both" if sm[k]["c"] and sa[k]["c"] else "sm_only" if sm[k]["c"] else "sa_only" if sa[k]["c"] else "neither") for k in sm); paired[str(seed)][str(m)]={"outcomes":dict(outcomes),"gain":outcomes["sa_only"],"loss":outcomes["sm_only"],"sm_c_per_32":[sm[k]["c_per_32"] for k in sm],"sa_c_per_32":[sa[k]["c_per_32"] for k in sm],"sm":_mean([sm[k]["bag"]["32"]["pass"]for k in sm]),"sa":_mean([sa[k]["bag"]["32"]["pass"]for k in sm])}
    geometry={axis:{b:{"routine":{},"challenge":{}} for b in bins}for axis,bins in (("length",LENGTH_BINS),("detour",DETOUR_BINS),("multiplicity",MULTIPLICITY_BINS))}
    for axis in geometry:
      for b in geometry[axis]:
       for stratum,ms in (("routine",set(maps)-challenge),("challenge",challenge)):
        for seed in SEEDS: geometry[axis][b][stratum][str(seed)]={m:aggregate([r for r in rows if r["seed"]==seed and r["mode"]==m and r[axis]==b and r["identity"]["map_id"]in ms]) for m in("sm","sa")}
    gate_input={s:{int(m):{"sm":x["sm"],"sa":x["sa"]}for m,x in paired[str(s)].items() if int(m)in challenge}for s in SEEDS}
    return {"problems":rows,"summary":summary,"paired_k32":paired,"geometry":geometry,"gate":gate(gate_input)}
def owners(root,ids):
    out={}
    for s in SEEDS:
      for mode in ("softmax","schrodinger"):
       d,r,result,authority=_owner_record(root,s,mode,ids); _manifest_file(d,"checkpoints/events.jsonl"); out[s,mode]=(d,r,result,authority)
    return out
def run(root=ROOT):
 root=Path(root); wrapper.install_replication_resource_limits(); core.configure_runtime()
 with core.OwnedAttempt.begin(root,root/"ledger.jsonl","D","difficult-d0-001") as attempt:
  signal.setitimer(signal.ITIMER_REAL,min(56.,signal.getitimer(signal.ITIMER_REAL)[0])); start=time.perf_counter(); _,ids=core._prepared_ids(root/"prepare-001"/"prepared.json")
  if sha(PLAN)!=PLAN_SHA: raise core.IdentityError("plan changed")
  val=load_validation(); own=owners(root,ids); output={"status":"COMPLETE","scope":{"model_calls":False,"test_access":False,"new_samples":False},"input_ids":ids,"owners":{f"{s}-{m}":x[3] for(s,m),x in own.items()},"updates":{},"route_order_limitation":"Retained route rows bind producer/event/dataset order; all-invalid permutations remain indistinguishable.","argv":list(sys.argv)}
  for u in UPDATES:
   bags={}
   for s in SEEDS:
    for mode in("softmax","schrodinger"):
     directory,record,_,authority=own[s,mode]; ev=next((x for x in record["result"]["events"] if x["update"]==u),None)
     if ev is None: raise core.IdentityError("missing event")
     event_hash=_event_digest(ev); result_hash=_manifest_file(directory,"result.json"); ev={**ev,"_binding":{"event_sha256":event_hash}}; route_rows,_=_storedroutes(ev,"t1_k32",val.problems)
     short="sm" if mode=="softmax" else "sa"; evidence={"event_sha256":event_hash,"result_sha256":result_hash,"input_ids":ids,"authority":authority}
     bags[s,short]=[(p,route_rows[i*32:(i+1)*32],evidence)for i,p in enumerate(val.problems)]
   output["updates"][str(u)]=assemble(val.problems,bags)
   if u==8000: output["gate"]=output["updates"][str(u)]["gate"]
  output["provenance"]={"plan":sha(PLAN),"spec":sha(SPEC),"approval":sha(APPROVAL),"code":sha(__file__),"helpers":{"replication_analysis":sha(WORKSPACE/"execution/seed_replication/analyze.py"),"paired_job":sha(WORKSPACE/"execution/paired_behavior/job.py")},"elapsed_seconds":time.perf_counter()-start}
  core._write_json(attempt.output/"d0.json",output)
 return output
def main(argv=None):
 p=argparse.ArgumentParser(); p.parse_args(argv); run()
if __name__=="__main__": main()
