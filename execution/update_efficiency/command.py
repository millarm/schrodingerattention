"""Stdlib-only, one-shot driver with durable per-owner reconciliation."""
from __future__ import annotations
import argparse, fcntl, hashlib, json, math, os, sys, tempfile, time, uuid
from datetime import datetime, timezone
from pathlib import Path
from execution.update_efficiency import watchdog as reviewed_watchdog

HERE = Path(__file__).resolve().parent; WORKSPACE = HERE.parents[1]
if not (WORKSPACE / "schrodinger" / "route_policy_experiment.py").is_file(): raise RuntimeError("literal project-root assertion failed")
ROOT = WORKSPACE / "execution" / "model_training_comparison"; LEDGER = ROOT / "ledger.jsonl"; ATTEMPTS = HERE / "attempts"
PREFIX_SHA = "1340ee945d663e22c7a4fa7bd232c9832b90babe20d3d91662967116d232c3f9"; PREFIX_LINES = 147; CARRY = 923.003597253
CAPS = {"A":1000.,"B":4100.,"C":0.,"D":800.}; NEW = {"A":100.,"B":1800.,"D":100.}; GLOBAL = 7200.
KINDS = {"smoke":("A",10.),"suite":("A",30.),"production":("B",None)}
SMOKE = "tests/test_update_efficiency.py::test_driver_main_timeout_descendant_and_accounting"; ALLOWANCE = 1.
DRIVER_REVIEW = HERE / "reviews" / "09-platform-static.md"; IMPLEMENTATION_REVIEW = HERE / "reviews" / "10-platform-implementation.md"
GRID = (0,1200,2000,2400,3600,4000,4800,6000,8000,10000,12000,14000,16000)

def sha256(path):
 h=hashlib.sha256()
 with Path(path).open("rb") as f:
  for b in iter(lambda:f.read(1048576),b""): h.update(b)
 return h.hexdigest()
def utc(): return datetime.now(timezone.utc).isoformat()
def _json(path):
 value=json.loads(Path(path).read_text())
 if not isinstance(value,dict): raise RuntimeError("object artifact required")
 return value
def durable(path,value):
 path=Path(path);path.parent.mkdir(parents=True,exist_ok=True);fd,tmp=tempfile.mkstemp(prefix="."+path.name,dir=path.parent)
 try:
  with os.fdopen(fd,"wb") as f:f.write(json.dumps(value,sort_keys=True,allow_nan=False).encode());f.flush();os.fsync(f.fileno())
  os.replace(tmp,path)
 finally:
  if os.path.exists(tmp):os.unlink(tmp)
def authority_hashes():
 paths={"study":HERE/"study.py","driver":Path(__file__),"watchdog":Path(reviewed_watchdog.__file__).resolve(),"tests":WORKSPACE/"tests/test_update_efficiency.py","plan":HERE/"plan-v3-saturation.md","spec":HERE/"spec-03-saturation.md","clarification":HERE/"driver-accounting-clarification.md","decisions":HERE/"decisions.md","attention":WORKSPACE/"schrodinger/attention.py","feasibility":WORKSPACE/"schrodinger/route_feasibility.py","protocol":WORKSPACE/"agent_execution_protocol.md","platform_spec":HERE/"spec-09-platform-cleanup.md"}
 paths.update({"accepted_"+p.name:p for p in (WORKSPACE/"schrodinger").glob("route_policy*.py")})
 return {k:sha256(v)for k,v in sorted(paths.items())}
def _ledger_rows(raw):
 lines=raw.splitlines(keepends=True)
 if not raw.endswith(b"\n") or len(lines)<PREFIX_LINES or hashlib.sha256(b"".join(lines[:PREFIX_LINES])).hexdigest()!=PREFIX_SHA:raise RuntimeError("ledger historical prefix changed")
 rows=[json.loads(x)for x in lines];ids=set();totals={x:0. for x in CAPS};carries=[]
 for row in rows:
  ident=row.get("entry_id");charge=row.get("charged_seconds")
  if not isinstance(ident,str)or ident in ids:raise RuntimeError("ledger UUID invalid")
  if isinstance(charge,bool)or not isinstance(charge,(int,float))or not math.isfinite(charge)or charge<0:raise RuntimeError("ledger charge invalid")
  ids.add(ident)
  if row.get("kind")=="inherited_budget":carries.append(row)
  else:
   if row.get("stage")not in totals:raise RuntimeError("ledger stage invalid")
   totals[row["stage"]]+=float(charge)
 if len(carries)!=1 or carries[0].get("charged_seconds")!=0 or carries[0].get("carried_budget_debit_seconds")!=CARRY:raise RuntimeError("exact inherited carry required")
 return rows,totals
def ledger_rows(path=LEDGER): return _ledger_rows(Path(path).read_bytes())
def locked_ledger_snapshot():
 """One append-lock byte snapshot binds decision EOF to prefix and totals."""
 with LEDGER.open("a+b")as f:
  fcntl.flock(f,fcntl.LOCK_EX)
  try:f.seek(0);raw=f.read();return hashlib.sha256(raw).hexdigest(),_ledger_rows(raw)
  finally:fcntl.flock(f,fcntl.LOCK_UN)
def review_ok(decision,hashes,kind):
 review=decision.get("review",{});path=Path(review.get("path",""));text=path.read_text()if path.is_file()else""
 required=IMPLEMENTATION_REVIEW if kind=="production" else DRIVER_REVIEW;phase="implementation"if kind=="production"else"static-safety";token="IMPLEMENTATION_REVIEW_VERDICT: PASS"if kind=="production"else"DRIVER_REVIEW_VERDICT: PASS"
 if path.resolve()!=required.resolve()or review.get("phase")!=phase or review.get("sha256")!=sha256(path):raise RuntimeError("review identity mismatch")
 if text.count(token)!=1 or any(value not in text for value in hashes.values()):raise RuntimeError("machine review PASS missing")
def acquire_reservation(decision,stage,envelope):
 lock=HERE/"driver.lock"
 try:fd=os.open(lock,os.O_CREAT|os.O_EXCL|os.O_WRONLY);os.close(fd)
 except FileExistsError:raise RuntimeError("driver reservation contention")
 try:
  if (ROOT/"experiment.lock").exists()or(ATTEMPTS/"experiment.lock").exists():raise RuntimeError("experiment lock contention")
  eof,(rows,totals)=locked_ledger_snapshot()
  if decision.get("ledger_sha256")!=eof:raise RuntimeError("ledger EOF changed after decision")
  used=sum(float(r["charged_seconds"])for r in rows if r.get("stage")==stage and(r.get("study")=="update_efficiency_v3"or(isinstance(r.get("output"),str)and r["output"].startswith(str(ATTEMPTS)))))
  if used+envelope>NEW[stage]or totals[stage]+envelope>CAPS[stage]or CARRY+sum(totals.values())+envelope>GLOBAL:raise RuntimeError("reserved envelope unavailable")
 except BaseException:
  lock.unlink(missing_ok=True);raise
 return lock
def reserve(decision,stage,envelope): return acquire_reservation(decision,stage,envelope)
def append_once(row):
 with LEDGER.open("a+b")as f:
  fcntl.flock(f,fcntl.LOCK_EX)
  try:
   f.seek(0);rows,_=_ledger_rows(f.read())
   if any(x["entry_id"]==row["entry_id"]for x in rows):raise RuntimeError("duplicate EOF append")
   f.write(json.dumps(row,sort_keys=True,allow_nan=False).encode()+b"\n");f.flush();os.fsync(f.fileno())
  finally:fcntl.flock(f,fcntl.LOCK_UN)
def charge(start):return time.monotonic()-start+ALLOWANCE
def budget_ok(stage,extra=0.):
 rows,totals=ledger_rows();used=sum(float(r["charged_seconds"])for r in rows if r.get("stage")==stage and(r.get("study")=="update_efficiency_v3"or(isinstance(r.get("output"),str)and r["output"].startswith(str(ATTEMPTS)))))
 return used+extra<=NEW[stage]and totals[stage]+extra<=CAPS[stage]and CARRY+sum(totals.values())+extra<=GLOBAL
def owner_path(seed,mode):return ATTEMPTS/f"update-efficiency-{seed}-{mode}-16000"
def prelaunch_owner(owner):
 rows,_=ledger_rows()
 if owner.exists()or any(r.get("output")==str(owner)for r in rows):raise RuntimeError("fixed owner already has durable history")
def owner_uuid(owner):
 found=[]
 for name in("attempt.pending.json","attempt.json"):
  path=owner/name
  if path.is_file():
   ident=_json(path).get("entry_id")
   if not isinstance(ident,str):raise RuntimeError("owner UUID invalid")
   found.append(ident)
 if len(set(found))>1:raise RuntimeError("owner UUID disagreement")
 return found[0]if found else None
def fallback(owner,session,start,reason):
 rows,_=ledger_rows()
 if any(r.get("kind")=="watchdog_uncertain_fallback"and r.get("output")==str(owner)for r in rows):raise RuntimeError("permanent fallback already recorded")
 row={"entry_id":str(uuid.uuid4()),"recorded_at_utc":utc(),"kind":"watchdog_uncertain_fallback","study":"update_efficiency_v3","stage":"B","status":"UNCERTAIN_FAILURE","error":reason,"charged_seconds":charge(start),"finalization_allowance_seconds":ALLOWANCE,"output":str(owner),"driver_session":str(session)};append_once(row);return row
def reconcile_owner(owner,session,start):
 """The UUID is discovered after launch; fallbacks never count as owner rows."""
 ident=owner_uuid(owner);rows,_=ledger_rows();normal=[r for r in rows if r.get("kind")=="attempt_charge"and r.get("stage")=="B"and r.get("output")==str(owner)]
 if any(r.get("kind")=="watchdog_uncertain_fallback"and r.get("output")==str(owner)for r in rows):raise RuntimeError("fallback is never an owner charge")
 if normal and (ident is None or len(normal)!=1 or normal[0].get("entry_id")!=ident):raise RuntimeError("owner charge identity ambiguity")
 if ident is None:fallback(owner,session,start,"owner UUID absent");return None
 if len(normal)==1:return normal[0]
 if not normal:fallback(owner,session,start,"resolved owner charge absent");return None
 raise RuntimeError("owner charge ambiguous")
def settle_owner(owner,owned,session,start):
 """Account only uncovered external driver overhead, never a second owner debit."""
 external=charge(start);covered=float(owned["charged_seconds"]);overhead=max(0.,external-covered);rows,_=ledger_rows()
 prior=[r for r in rows if r.get("kind")=="driver_overhead"and r.get("output")==str(owner)and r.get("owner_entry_id")==owned.get("entry_id")and r.get("driver_session")==str(session)]
 if len(prior)>1:raise RuntimeError("duplicate driver overhead")
 if prior:
  if not math.isclose(float(prior[0].get("charged_seconds",math.nan)),overhead,rel_tol=0.,abs_tol=1e-9):raise RuntimeError("driver overhead disagreement")
 elif overhead>0:
  append_once({"entry_id":str(uuid.uuid4()),"recorded_at_utc":utc(),"kind":"driver_overhead","study":"update_efficiency_v3","stage":"B","status":"ACCOUNTED","charged_seconds":overhead,"external_seconds":external,"owner_charge_seconds":covered,"finalization_allowance_seconds":ALLOWANCE,"output":str(owner),"owner_entry_id":owned["entry_id"],"driver_session":str(session)})
 return max(covered,external)
def _safe_file(owner,relative):
 raw=Path(relative);path=(raw if raw.is_absolute()else owner/raw).resolve()
 if owner.resolve()not in path.parents:raise RuntimeError("artifact escapes owner")
 return path
def _references(value):
 if isinstance(value,dict):
  for key,item in value.items():
   if key.endswith("_path")and isinstance(item,str):yield item,value.get(key[:-5]+"_sha256")or value.get(key[:-5]+"_hash")or value.get("sha256")
   yield from _references(item)
 elif isinstance(value,list):
  for item in value:yield from _references(item)
def validate_complete(owner,owned,seed,mode):
 attempt=owner/"attempt.json";result=owner/"result.json";index=owner/"index.json";manifest=owner/"output-manifest.json"
 if not all(p.is_file()for p in(attempt,result,index,manifest)):raise RuntimeError("owned production terminal artifacts missing")
 terminal=_json(attempt);m=_json(manifest);idx=_json(index);payload=_json(result)
 if terminal.get("status")!="COMPLETE"or terminal.get("entry_id")!=owned.get("entry_id")or idx.get("status")!="COMPLETE"or payload.get("seed")!=seed or payload.get("mode")!=mode:raise RuntimeError("owner terminal identity mismatch")
 if idx.get("result_sha256")!=sha256(result):raise RuntimeError("index result binding mismatch")
 actual={str(p.relative_to(owner)):sha256(p)for p in owner.rglob("*")if p.is_file()and p.name!="output-manifest.json"}
 if set(m)!=set(actual)or any(not isinstance(v,dict)or v.get("sha256")!=actual[k]for k,v in m.items()):raise RuntimeError("complete manifest mismatch")
 points=payload.get("points")
 if not isinstance(points,list)or [x.get("update")if isinstance(x,dict)else None for x in points]!=list(GRID):raise RuntimeError("exact endpoint grid missing")
 if idx.get("scores")!=points:raise RuntimeError("index endpoint set mismatch")
 for point in points:
  score=_safe_file(owner,point.get("score_path",""));digest=point.get("score_sha256")
  if not score.is_file()or not isinstance(digest,str)or sha256(score)!=digest:raise RuntimeError("endpoint hash mismatch")
  checkpoint=_safe_file(owner,"checkpoints/initial.pt"if point["update"]==0 else f"checkpoints/update-{point['update']}.pt")
  if not checkpoint.is_file()or sha256(checkpoint)!=_json(score).get("checkpoint_sha256"):raise RuntimeError("endpoint checkpoint mismatch")
 for relative,digest in _references({"result":payload,"index":idx}):
  path=_safe_file(owner,relative)
  if not path.is_file()or not isinstance(digest,str)or sha256(path)!=digest:raise RuntimeError("referenced endpoint/checkpoint mismatch")
def supervise(argv,deadline,output):return reviewed_watchdog.supervise(argv,WORKSPACE,Path(output),time.monotonic()+deadline)
def main(argv=None):
 started=time.monotonic();lock=session=stage=owner=None;completed=False;accounting_certain=False;settlement_started=False;cleanup_certain=False;terminal_certain=False;finalization_uncertain=False;resource_overrun=False
 p=argparse.ArgumentParser();p.add_argument("--decision",type=Path,required=True);p.add_argument("--seconds",type=float,required=True);p.add_argument("--seed",type=int,required=True);p.add_argument("--mode",choices=("softmax","schrodinger"),required=True);a=p.parse_args(argv)
 try:
  decision=_json(a.decision);hashes=authority_hashes();kind=decision.get("kind")
  if kind not in KINDS or not math.isfinite(a.seconds)or a.seconds<=0:raise RuntimeError("unknown/nonfinite command envelope")
  stage,fixed=KINDS[kind];expected=[sys.executable,"-m","pytest","-q",SMOKE if kind=="smoke"else"tests/test_update_efficiency.py"]if kind!="production"else[sys.executable,"-m","execution.update_efficiency.study","--decision",str(a.decision.resolve())]
  if(fixed is not None and a.seconds!=fixed)or(kind=="production"and a.seconds!={"softmax":350.,"schrodinger":550.}[a.mode]):raise RuntimeError("exact command envelope required")
  if decision.get("approved")is not True or decision.get("hashes")!=hashes or decision.get("seed")!=a.seed or decision.get("mode")!=a.mode or decision.get("argv")!=expected or decision.get("cwd")!=str(WORKSPACE):raise RuntimeError("reviewed decision mismatch")
  if kind=="production"and(a.seed not in(2201,2202)or decision.get("updates")!=16000 or decision.get("plan_sha256")!=sha256(HERE/"plan-v3-saturation.md")or decision.get("spec_sha256")!=sha256(HERE/"spec-03-saturation.md")or decision.get("driver_accounting_clarification_sha256")!=sha256(HERE/"driver-accounting-clarification.md")):raise RuntimeError("v3 production binding mismatch")
  review_ok(decision,hashes,kind);lock=acquire_reservation(decision,stage,a.seconds);durable(lock,{"status":"RESERVED","stage":stage,"envelope_seconds":a.seconds,"started_monotonic":started});cleanup_certain=True;session=ATTEMPTS/("driver-"+str(uuid.uuid4()));session.mkdir(parents=True,exist_ok=False)
  if stage=="B":owner=owner_path(a.seed,a.mode);prelaunch_owner(owner)
  durable(session/"start.json",{"argv":expected,"decision":str(a.decision.resolve()),"ledger_sha256":sha256(LEDGER),"hashes":hashes,"started_monotonic":started})
  remaining=a.seconds-(time.monotonic()-started)-ALLOWANCE
  if remaining<=0:raise TimeoutError("setup exhausted command envelope")
  cleanup_certain=False;child=supervise(expected,remaining,session);cleanup_certain=bool(child.get("cleanup_verified"));durable(session/"child-terminal.json",child)
  if stage=="A":
   actual_charge=charge(started);resource_overrun=actual_charge>a.seconds or not budget_ok("A",actual_charge);terminal="COMPLETE"if child.get("exit_code")==0 and not child.get("timed_out")and child.get("cleanup_verified")and not resource_overrun else"FAILED"
   append_once({"entry_id":str(uuid.uuid4()),"recorded_at_utc":utc(),"kind":"attempt_charge","study":"update_efficiency_v3","stage":"A","status":terminal,"charged_seconds":actual_charge,"finalization_allowance_seconds":ALLOWANCE,"output":str(session),"driver_session":str(session),"resource_overrun":resource_overrun});accounting_certain=True
   if terminal!="COMPLETE":raise RuntimeError("child did not complete")
  else:
   settlement_started=True;owned=reconcile_owner(owner,session,started)
   if owned is None:accounting_certain=True;raise RuntimeError("missing owner charge; permanent fallback recorded")
   accounted_total=settle_owner(owner,owned,session,started);accounting_certain=True
   resource_overrun=accounted_total>a.seconds or not budget_ok("B")
   if child.get("exit_code")!=0 or child.get("timed_out")or not child.get("cleanup_verified")or resource_overrun:raise RuntimeError("charged owner child/resource did not complete")
   validate_complete(owner,owned,a.seed,a.mode)
  try:durable(session/"terminal.json",{"status":"COMPLETE","charged_seconds":charge(started)})
  except BaseException:finalization_uncertain=True;raise
  terminal_certain=True;completed=True;print(json.dumps({"status":"COMPLETE","session":str(session)}))
 except BaseException as error:
  if stage=="A"and session is not None and not accounting_certain:
   try:
    actual_charge=charge(started);resource_overrun=actual_charge>a.seconds or not budget_ok("A",actual_charge);append_once({"entry_id":str(uuid.uuid4()),"recorded_at_utc":utc(),"kind":"attempt_charge","study":"update_efficiency_v3","stage":"A","status":"FAILED","error":repr(error),"charged_seconds":actual_charge,"finalization_allowance_seconds":ALLOWANCE,"output":str(session),"driver_session":str(session),"resource_overrun":resource_overrun});accounting_certain=True
   except BaseException:pass
  if stage=="B"and owner is not None and not accounting_certain and not settlement_started:
   try:
    settlement_started=True;recovered=reconcile_owner(owner,session,started)
    if recovered is None:accounting_certain=True
    else:settle_owner(owner,recovered,session,started);accounting_certain=True
   except BaseException:pass
  if session is not None:
   try:durable(session/"terminal.json",{"status":"FAILED_DRIVER","error":repr(error),"charged_seconds":charge(started),"resource_overrun":resource_overrun});terminal_certain=not finalization_uncertain
   except BaseException:pass
  raise
 finally:
  if lock is not None and accounting_certain and cleanup_certain and terminal_certain and not finalization_uncertain:lock.unlink(missing_ok=True)
if __name__=="__main__":main()
