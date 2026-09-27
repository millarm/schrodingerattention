"""External D1 watchdog. It does not import D1 or share its SIGALRM timer."""
from __future__ import annotations
import argparse, fcntl, hashlib, json, os, signal, subprocess, tempfile, time, uuid
from datetime import datetime, timezone
from pathlib import Path

HERE=Path(__file__).resolve().parent
WORKSPACE=HERE.parents[1]
PREFIX_SHA='770d3490766d0ec2e40a796ee8f896b4f1fbc3e7647c00d145cf4010dfc7d7c0'
CAPS={'A':1000.,'B':3500.,'C':0.,'D':1400.}; CARRY=923.003597253; GLOBAL=7200.

def digest(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def utc(): return datetime.now(timezone.utc).isoformat()
def durable(path,value):
 path=Path(path); fd,tmp=tempfile.mkstemp(prefix='.'+path.name+'.',dir=path.parent)
 try:
  with os.fdopen(fd,'wb')as h: h.write(json.dumps(value,sort_keys=True,separators=(',',':')).encode()); h.flush(); os.fsync(h.fileno())
  os.replace(tmp,path); directory=os.open(path.parent,os.O_RDONLY); os.fsync(directory); os.close(directory)
 finally:
  if os.path.exists(tmp): os.unlink(tmp)
def read_rows(ledger):
 try: rows=[json.loads(line)for line in Path(ledger).read_text().splitlines()if line]
 except Exception as error: raise RuntimeError('invalid ledger JSONL')from error
 ids=set(); totals={stage:0. for stage in CAPS}; carries=0
 for row in rows:
  ident=row.get('entry_id'); charge=row.get('charged_seconds')
  if not isinstance(ident,str)or ident in ids or not isinstance(charge,(int,float))or charge<0 or charge!=charge: raise RuntimeError('invalid ledger row')
  ids.add(ident)
  if row.get('kind')=='inherited_budget': carries+=1; continue
  if row.get('stage') not in CAPS: raise RuntimeError('invalid ledger stage')
  totals[row['stage']]+=float(charge)
 if carries!=1: raise RuntimeError('ledger must retain one carry')
 return rows,totals
def verify_ledger(ledger):
 raw=Path(ledger).read_bytes(); lines=raw.splitlines(keepends=True)
 if len(lines)<143 or hashlib.sha256(b''.join(lines[:143])).hexdigest()!=PREFIX_SHA: raise RuntimeError('frozen prefix mismatch')
 rows,totals=read_rows(ledger)
 if totals['A']<300: raise RuntimeError('approved administrative addendum absent')
 return rows,totals
def locked_ledger(ledger):
 handle=Path(str(ledger)+'.watchdog.lock').open('a+')
 fcntl.flock(handle,fcntl.LOCK_EX)
 return handle
def append_locked(ledger,row):
 with Path(ledger).open('a',encoding='utf8')as h: h.write(json.dumps(row,sort_keys=True)+'\n'); h.flush(); os.fsync(h.fileno())
 directory=os.open(Path(ledger).parent,os.O_RDONLY); os.fsync(directory); os.close(directory)
def require_decision(path,kind,seconds,command,hashes):
 decision=json.loads(Path(path).read_text())
 if decision.get('kind')!=kind or decision.get('seconds')!=seconds or decision.get('argv')!=command or decision.get('hashes')!=hashes: raise RuntimeError('decision does not bind command/version')
 if seconds==60 and decision.get('sol_concurrence_sha256')!=digest(Path(path).with_name('sol-concurrence.md')): raise RuntimeError('missing exact Sol concurrence')
 return {'path':str(Path(path).resolve()),'sha256':digest(path)}
def group_gone(pgid):
 try: os.killpg(pgid,0); return False
 except ProcessLookupError: return True
def terminate_group(child,deadline):
 if child.poll() is None:
  try: os.killpg(child.pid,signal.SIGTERM)
  except ProcessLookupError: pass
  while time.monotonic()<deadline and child.poll() is None: time.sleep(.05)
 if not group_gone(child.pid):
  try: os.killpg(child.pid,signal.SIGKILL)
  except ProcessLookupError: pass
 while time.monotonic()<deadline and not group_gone(child.pid): time.sleep(.05)
 if not group_gone(child.pid): raise RuntimeError('descendant process group survived deadline')
 return child.wait()
def main(argv=None):
 parser=argparse.ArgumentParser(); parser.add_argument('--seconds',type=float,required=True); parser.add_argument('--record-dir',required=True); parser.add_argument('--kind',choices=('test','production'),required=True); parser.add_argument('--ledger',required=True); parser.add_argument('--decision',required=True); parser.add_argument('--expected-cwd',required=True); parser.add_argument('command',nargs=argparse.REMAINDER); args=parser.parse_args(argv)
 if not args.command or Path.cwd().resolve()!=Path(args.expected_cwd).resolve(): raise SystemExit('cwd/argv required')
 allowed=(args.seconds in(10.,30.,60.))if args.kind=='test'else args.seconds==300.
 if not allowed: raise SystemExit('unapproved envelope')
 files={'d1':HERE/'d1.py','test':WORKSPACE/'tests/test_difficult_problem_solving_d1.py','watchdog':Path(__file__)}; hashes={key:digest(value)for key,value in files.items()}
 decision=require_decision(args.decision,'d1-'+args.kind,args.seconds,args.command,hashes)
 ledger=Path(args.ledger); lock=locked_ledger(ledger)
 try:
  rows,totals=verify_ledger(ledger); recovery=sum(float(r['charged_seconds'])for r in rows if r.get('recovery')=='d1-minimal-repair')
  if args.kind=='test'and recovery+args.seconds>120: raise RuntimeError('fresh recovery cap exhausted')
  stage='A'if args.kind=='test'else'D'
  if totals[stage]+args.seconds>CAPS[stage]or CARRY+sum(totals.values())+args.seconds>GLOBAL: raise RuntimeError('stage/global headroom exhausted')
  root=Path(args.record_dir); root.mkdir(parents=True,exist_ok=False); ident=str(uuid.uuid4()); start_tick=time.monotonic(); record={'id':ident,'argv':args.command,'cwd':str(Path.cwd()),'started_utc':utc(),'seconds':args.seconds,'kind':args.kind,'hashes':hashes,'decision':decision}; durable(root/'start.json',record)
  with(root/'stdout.txt').open('wb')as out,(root/'stderr.txt').open('wb')as err:
   child=subprocess.Popen(args.command,stdout=out,stderr=err,start_new_session=True); timed=False; deadline=start_tick+args.seconds
   try: code=child.wait(timeout=max(0.,deadline-time.monotonic()))
   except subprocess.TimeoutExpired: timed=True; code=terminate_group(child,deadline+5.)
  elapsed=time.monotonic()-start_tick; result={**record,'ended_utc':utc(),'monotonic_elapsed_seconds':elapsed,'exit_code':code,'timed_out':timed,'stdout_sha256':digest(root/'stdout.txt'),'stderr_sha256':digest(root/'stderr.txt')}; durable(root/'result.json',result)
  # Re-read while the exclusive lock is held; a terminal record exists before any charge.
  rows,totals=verify_ledger(ledger)
  if args.kind=='test':
   row={'entry_id':ident,'recorded_at_utc':utc(),'kind':'attempt_charge','stage':'A','status':'success'if code==0 and not timed else'failed','charged_seconds':elapsed,'charge_owner':'d1-watchdog','recovery':'d1-minimal-repair','watchdog_record':str(root.resolve())}; append_locked(ledger,row); result['accounting']={'status':'APPENDED','entry_id':ident}
  else:
   output=Path(args.ledger).parent/'difficult-d1-repair-001'; attempt=output/'attempt.json'; owned=[r for r in rows if r.get('stage')=='D'and r.get('output')==str(output)]
   if len(owned)==1 and attempt.is_file(): result['accounting']={'status':'OWNED_RECONCILED','entry_id':owned[0]['entry_id'],'attempt_sha256':digest(attempt)}
   elif not owned:
    row={'entry_id':ident,'recorded_at_utc':utc(),'kind':'attempt_charge','stage':'D','status':'UNCERTAIN_FAILURE','charged_seconds':elapsed,'recovery':'d1-minimal-repair','watchdog_record':str(root.resolve()),'output':str(output)}; append_locked(ledger,row); result['accounting']={'status':'UNCERTAIN_FALLBACK','entry_id':ident}
   else: result['accounting']={'status':'STOP_AMBIGUOUS_OWNER'}; code=1
  durable(root/'result.json',result); print(json.dumps(result,sort_keys=True)); return 124 if timed else code
 finally:
  fcntl.flock(lock,fcntl.LOCK_UN); lock.close()
if __name__=='__main__': raise SystemExit(main())
