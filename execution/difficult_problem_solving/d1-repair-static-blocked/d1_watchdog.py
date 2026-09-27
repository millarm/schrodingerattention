"""External, durable watchdog for the two bounded D1 repair test commands.

It intentionally never imports D1.  The child gets its own process group so a
runner's SIGALRM cannot suppress this independent wall-clock deadline.
"""
from __future__ import annotations

import argparse, hashlib, json, os, signal, subprocess, sys, time, uuid
from datetime import datetime, timezone
from pathlib import Path

def _sha(path):
 h=hashlib.sha256()
 with Path(path).open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''): h.update(b)
 return h.hexdigest()
def _utc(): return datetime.now(timezone.utc).isoformat()
def main(argv=None):
 p=argparse.ArgumentParser();p.add_argument('--seconds',type=float,required=True);p.add_argument('--record-dir',required=True);p.add_argument('--kind',choices=('test','production'),required=True);p.add_argument('--owner-entry-id');p.add_argument('command',nargs=argparse.REMAINDER);a=p.parse_args(argv)
 if not 0<a.seconds<=60 or not a.command: raise SystemExit('bounded seconds and command required')
 root=Path(a.record_dir);root.mkdir(parents=True,exist_ok=False); ident=str(uuid.uuid4()); start=_utc(); tick=time.monotonic()
 if a.kind=='production' and not a.owner_entry_id: raise SystemExit('production requires owner entry ID for ledger reconciliation')
 record={'id':ident,'argv':a.command,'cwd':str(Path.cwd()),'started_utc':start,'seconds':a.seconds,'kind':a.kind,'owner_entry_id':a.owner_entry_id,'source_sha256':_sha(Path(__file__).with_name('d1.py')),'test_sha256':_sha(Path(__file__).parents[2]/'tests/test_difficult_problem_solving_d1.py')}
 (root/'start.json').write_text(json.dumps(record,sort_keys=True,indent=2))
 with (root/'stdout.txt').open('wb')as out,(root/'stderr.txt').open('wb')as err:
  child=subprocess.Popen(a.command,stdout=out,stderr=err,start_new_session=True)
  timed_out=False
  try: exit_code=child.wait(timeout=a.seconds)
  except subprocess.TimeoutExpired:
   timed_out=True;os.killpg(child.pid,signal.SIGTERM)
   try: exit_code=child.wait(timeout=2)
   except subprocess.TimeoutExpired: os.killpg(child.pid,signal.SIGKILL);exit_code=child.wait()
 end=_utc(); accounting={'stage':'A','charge_owner':'watchdog','reconcile_owner_entry_id':None} if a.kind=='test' else {'stage':'D','charge_owner':'OwnedAttempt','reconcile_owner_entry_id':a.owner_entry_id,'on_missing_owner':'record uncertain linked failure; append once only after unique-ID reconciliation'}
 result={**record,'ended_utc':end,'monotonic_elapsed_seconds':time.monotonic()-tick,'exit_code':exit_code,'timed_out':timed_out,'accounting':accounting,'stdout_sha256':_sha(root/'stdout.txt'),'stderr_sha256':_sha(root/'stderr.txt')}
 (root/'result.json').write_text(json.dumps(result,sort_keys=True,indent=2));print(json.dumps(result,sort_keys=True));return 124 if timed_out else exit_code
if __name__=='__main__':raise SystemExit(main())
