"""Minimal immutable v2 dataset runner; no model or training functionality."""
from __future__ import annotations
import argparse, hashlib, json, os, signal, sys, time, uuid
from datetime import datetime, timezone
from pathlib import Path
import numpy as np
from schrodinger.route_feasibility import append_ledger, canonical_map, neighbors
from schrodinger import productive_diversity_data as data
from schrodinger.productive_diversity_data import ConstructionFailure, OracleCache, RUNGS, inventory, training_dataset, stratum

ROOT=Path(__file__).resolve().parents[1]; LEDGER=ROOT/'execution/next_level_v2/ledger.jsonl'; LOCK=ROOT/'execution/next_level_v2/compute.lock'; REJECTIONS=ROOT/'execution/next_level_v2/rejections'; CAP=900.; GLOBAL=7200.; STARTUP=2.; RESERVE=30.
class Deadline(RuntimeError): pass
class TechnicalFailure(RuntimeError): pass
def _now(): return datetime.now(timezone.utc).isoformat()
def _json(v):
 if isinstance(v,bytes): return v.hex()
 if isinstance(v,(set,frozenset)): return [_json(x) for x in sorted(v)]
 if isinstance(v,tuple): return [_json(x) for x in v]
 if isinstance(v,list): return [_json(x) for x in v]
 if isinstance(v,dict): return {str(k):_json(x) for k,x in v.items()} if all(isinstance(k,str) for k in v) else [{'key':_json(k),'value':_json(x)} for k,x in sorted(v.items(),key=lambda item:repr(item[0]))]
 if isinstance(v,np.generic): return v.item()
 return v
def _write(path:Path,value):
 with path.open('x') as handle: json.dump(_json(value),handle,sort_keys=True,indent=2,allow_nan=False)
def _prior(path): return sum(json.loads(x).get('charged_seconds',0.)+json.loads(x).get('budget_allowance_seconds',0.) for x in path.read_text().splitlines()) if path.exists() else 0.
class Attempt:
 def __init__(self,out,*,lock=LOCK,ledger=LEDGER,deadline=None,rejections=None):
  self.out,self.lock,self.ledger,self.deadline=Path(out),Path(lock),Path(ledger),deadline;self.started=time.perf_counter();self.prior=_prior(self.ledger);self.id=str(uuid.uuid4());self.fd=None;self.owned=False;self.owned_lock=False;self.handler=None;self.old_timer=None;self.manifest_sha256=None;self.recorded=False
  self.rejections=Path(rejections) if rejections is not None else self.ledger.parent/'rejections'
 def record(self,status,error=None):
  e=time.perf_counter()-self.started;return {'entry_id':self.id,'kind':'productive_diversity_v2','stage':'stage0','status':status,'execution_status':status,'error':None if error is None else repr(error),'started_at_utc':self.started_utc,'ended_at_utc':_now(),'elapsed_seconds':e,'startup_allowance_seconds':STARTUP,'charged_seconds':STARTUP+e,'prior_global_seconds':self.prior,'cumulative_global_seconds':self.prior+STARTUP+e,'argv':getattr(sys,'orig_argv',sys.argv),'pid':os.getpid(),'manifest_sha256':self.manifest_sha256}
 def __enter__(self):
  self.started_utc=_now()
  if self.out.exists() or self.lock.exists(): self.reject('fresh output and lock required');raise FileExistsError('fresh output and lock required')
  self.lock.parent.mkdir(parents=True,exist_ok=True)
  try:self.fd=os.open(self.lock,os.O_CREAT|os.O_EXCL|os.O_WRONLY);self.owned_lock=True
  except FileExistsError as exc:self.reject(f'lock acquisition rejected: {exc}');raise
  try:
   self.out.mkdir(parents=True);self.owned=True;base=min(CAP-self.prior-STARTUP-RESERVE,GLOBAL-self.prior-STARTUP-RESERVE);remain=min(base,self.deadline) if self.deadline is not None else base
   if remain<=0: raise Deadline('v2 budget exhausted')
   self.handler=signal.getsignal(signal.SIGALRM);self.old_timer=signal.setitimer(signal.ITIMER_REAL,0);signal.signal(signal.SIGALRM,lambda *_:(_ for _ in ()).throw(Deadline('v2 deadline')));signal.setitimer(signal.ITIMER_REAL,remain);return self
  except BaseException as exc:
   try:
    if self.owned: self.persist('FAILED',exc)
    else: self.reject(f'output acquisition rejected: {exc}')
   finally:self.cleanup()
   raise
 def append(self,record):
  if not self.recorded: append_ledger(record,self.ledger);self.recorded=True
 def reject(self,reason):
  record=self.record('REJECTED',reason)
  try:self.rejections.mkdir(parents=True,exist_ok=True);_write(self.rejections/f'rejected-{self.id}.json',record)
  finally:self.append(record)
 def persist(self,status,error=None):
  record=self.record(status,error)
  try:_write(self.out/'attempt.json',record)
  except BaseException as write_error:
   self.append({**record,'status':'FAILED','execution_status':'FAILED','error':f'log write failed: {write_error!r}'});raise
  else:self.append(record)
 def cleanup(self):
  if self.handler is not None:
   signal.setitimer(signal.ITIMER_REAL,0);signal.signal(signal.SIGALRM,self.handler)
   if self.old_timer and self.old_timer[0]>0:signal.setitimer(signal.ITIMER_REAL,*self.old_timer)
  if self.fd is not None: os.close(self.fd);self.fd=None
  if self.owned_lock and self.lock.exists(): self.lock.unlink()
 def __exit__(self,t,v,b):
  rec=self.record('FAILED' if t else 'COMPLETE',v)
  try:
   if self.owned: self.persist('FAILED' if t else 'COMPLETE',v)
  finally:self.cleanup()
def _counts(spec):
 return {'validation_routine':{f:12 for f in spec.training_families},'test_routine':{f:48 for f in spec.training_families},'validation_challenge':{f:(4 if spec.name=='A' else 8) for f in spec.challenge_families},'test_challenge':{f:(16 if spec.name=='A' else 32) for f in spec.challenge_families}}
def _rows(rows): return [{k:v for k,v in x.items() if k!='walls'} for x in rows]
def _validate_stratum(records,required,kind,quotas,*,maps,seen,cache,support,per_map=16,multiplicity=(16,256)):
 total=sum(required.values())*per_map
 if len(records)!=total: raise TechnicalFailure(f'stratum total mismatch expected={total} actual={len(records)}')
 by={};identities=set()
 for row in records:
  item=maps[row['map_id']];identity=canonical_map(row['walls'],8)
  if row['family'] not in required or row['family']!=item['family'] or row['walls']!=item['walls']: raise TechnicalFailure('stratum family/walls mismatch')
  if identity!=item['canonical'] or identity in seen: raise TechnicalFailure('canonical identity mismatch/cross-split reuse')
  identities.add(identity)
  by.setdefault(row['map_id'],[]).append(row)
  distances,counts=cache.bfs(row['walls'],row['goal'],8);signatures=cache.signatures(row['walls'],row['start'],row['goal'],8)
  if distances.get(row['start'])!=row['length'] or counts.get(row['start'])!=row['M'] or len(signatures)!=row['M'] or not multiplicity[0]<=row['M']<=multiplicity[1]:raise TechnicalFailure('oracle length/M mismatch')
  if kind is not None:
   novel=sum(sig not in support for sig in signatures)
   if row['M_novel']!=novel or row.get('route_count',row['M'])!=row['M']:raise TechnicalFailure('oracle novelty mismatch')
   if (kind=='routine' and novel!=0) or (kind=='challenge' and not (novel>=4 and .25<=novel/row['M']<=.75)):raise TechnicalFailure('stratum novelty predicate mismatch')
 families={family:sum(rows[0]['family']==family for rows in by.values()) for family in required}
 if families!=required or len(identities)!=len(by):raise TechnicalFailure('family map count/canonical duplicate mismatch')
 for map_id,rows in by.items():
  if len(rows)!=per_map or len({(x['start'],x['goal']) for x in rows})!=per_map: raise TechnicalFailure('stratum per-map cardinality/duplicate mismatch')
 observed={length:sum(row['length']==length for row in records) for length in quotas}
 if observed!=quotas or sum(observed.values())!=len(records): raise TechnicalFailure(f'stratum quota mismatch observed={observed} quotas={quotas}')
 seen.update(identities)
 return {'problems':len(records),'maps':len(by),'families':families,'lengths':observed}

def _validate_states(states,maps,cache):
 seen=set()
 for row in states:
  key=(row['map_id'],row['state'],row['goal'])
  if key in seen:raise TechnicalFailure('duplicate supervised state')
  seen.add(key);walls=maps[row['map_id']]['walls'];dist,cnt=cache.bfs(walls,row['goal'],8)
  if row['state']==row['goal'] or row['state'] not in dist:raise TechnicalFailure('invalid supervised state')
  legal=dict(neighbors(row['state'],walls,8));q=[cnt.get(legal.get(a),0)/cnt[row['state']] if a in legal and dist.get(legal[a])==dist[row['state']]-1 else 0. for a in range(4)]
  if not np.allclose(q,row['q'],atol=1e-12,rtol=0):raise TechnicalFailure('q mismatch')

def run_rung(spec,out:Path,inventory_fn=inventory,*,counts=None,training_kwargs=None,per_map=16,multiplicity=(16,256),training_fn=None,stratum_fn=None,training_counts=None):
 out.mkdir(); stages={k:'NOT_EVALUATED' for k in ('inventory','training','validation_routine','validation_challenge','test_routine','test_challenge')};excluded=set();seen=set();current='inventory'
 counts=_counts(spec) if counts is None else counts;training_kwargs={} if training_kwargs is None else training_kwargs
 training_fn=training_dataset if training_fn is None else training_fn;stratum_fn=stratum if stratum_fn is None else stratum_fn
 training_counts={f:32 for f in spec.training_families} if training_counts is None else training_counts
 required={k:{'maps':v,'problems':sum(v.values())*per_map} for k,v in {'training':training_counts,**counts}.items()}
 result={'rung':spec.name,'stages':stages,'observed_counts':{},'required_counts':required};cache=OracleCache()
 try:
  stages[current]='RUNNING';rows,pool=inventory_fn(spec);maps={row['map_id']:row for row in rows}
  if len(maps)!=len(rows):raise TechnicalFailure('duplicate inventory id')
  _write(out/'inventory.json',{'rows':rows,'pool':pool});stages[current]='COMPLETE';result['observed_counts'][current]=len(rows)
  current='training';stages[current]='RUNNING'
  train,states,support,digest,ta=training_fn(rows,spec,excluded,**training_kwargs)
  quotas=data.length_quotas(spec.lengths,required['training']['problems'])
  result['observed_counts'][current]=_validate_stratum(train,training_counts,None,quotas,maps=maps,seen=seen,cache=cache,support=None,per_map=per_map,multiplicity=multiplicity)
  coverage=data.require_training_orientation_coverage(train,n=8);_validate_states(states,maps,cache)
  payload=b''.join(len(x).to_bytes(2,'big')+x for x in support)
  if support!=sorted(set(support)) or hashlib.sha256(payload).hexdigest()!=digest:raise TechnicalFailure('support hash/order mismatch')
  _write(out/'training.json',{'rows':train,'audit':ta,'orientation_coverage':coverage});_write(out/'states.json',states)
  with (out/'support.bin').open('xb') as handle:handle.write(payload)
  stages[current]='COMPLETE';excluded.update(seen);result['support_sha256']=digest
  props={l:quotas[l]/len(train) for l in spec.lengths}
  for key,kind in (('validation_routine','routine'),('validation_challenge','challenge'),('test_routine','routine'),('test_challenge','challenge')):
   current=key;stages[current]='RUNNING';split='validation' if key.startswith('validation') else 'test'
   records,audit=stratum_fn(rows,spec,split,counts[key],excluded,set(support),kind,props,cache=cache)
   quotas=data.length_quotas(spec.lengths,required[key]['problems'],props)
   if audit['quotas']!=quotas:raise TechnicalFailure('reported quota differs from frozen quota')
   result['observed_counts'][key]=_validate_stratum(records,counts[key],kind,quotas,maps=maps,seen=seen,cache=cache,support=set(support),per_map=per_map,multiplicity=multiplicity)
   excluded.update(seen);_write(out/f'{key}.json',{'rows':records,'audit':audit});stages[key]='COMPLETE'
  result.update(outcome='DATASET_PASS',execution_status='COMPLETE')
 except ConstructionFailure as exc:
  if exc.outcome not in ('MAP_SUPPLY_FAILED','LENGTH_FLOW_FAILED','TRAINING_ORIENTATION_COVERAGE_FAILED'):
   stages[current]='TECHNICAL_FAILURE';result.update(outcome='TECHNICAL_FAILURE',execution_status='FAILED',error=repr(exc));raise TechnicalFailure('unrecognized scientific failure') from exc
  stages[current]='SCIENTIFIC_FAILURE';result.update(outcome=exc.outcome,execution_status='COMPLETE',evidence=exc.evidence)
 except BaseException as exc:
  stages[current]='DEADLINE' if isinstance(exc,Deadline) else 'TECHNICAL_FAILURE';result.update(outcome=stages[current],execution_status='FAILED',error=repr(exc));raise
 finally:_write(out/'summary.json',result)
 return result
def effective_config():
 return {'n':8,'pool_seed':data.POOL_SEED,'pool_limit':data.POOL_LIMIT,'pool_trials':data.POOL_TRIALS,'problems_per_map':16,'multiplicity':[16,256],
 'rungs':[{'name':r.name,'index':r.index,'seeds':r.split_seeds,'family_codes':r.family_codes,'training_families':r.training_families,'challenge_families':r.challenge_families,'lengths':r.lengths,'training_counts':{f:32 for f in r.training_families},'counts':_counts(r)} for r in RUNGS],
 'caps':{'stage':CAP,'global':GLOBAL,'startup':STARTUP,'reserve':RESERVE},'order':['inventory','training','validation_routine','validation_challenge','test_routine','test_challenge']}
def _manifest(out,summary):
 files={str(p.relative_to(out)):hashlib.sha256(p.read_bytes()).hexdigest() for p in out.rglob('*') if p.is_file() and p.name not in ('manifest.json','attempt.json')}
 inputs=[ROOT/'agent_execution_protocol.md',ROOT/'schrodinger/productive_diversity_data.py',ROOT/'schrodinger/productive_diversity_runner.py',ROOT/'schrodinger/route_feasibility.py',ROOT/'tests/test_productive_diversity_data.py',ROOT/'tests/test_productive_diversity_runner.py',ROOT/'productive_diversity_v2_plan.md',*sorted((ROOT/'execution/next_level_v2/specs').glob('*.md')),*sorted((ROOT/'execution/next_level_v2/reviews').glob('*.md'))]
 m={'argv':getattr(sys,'orig_argv',sys.argv),'executable':sys.executable,'threads':{'OMP_NUM_THREADS':os.environ.get('OMP_NUM_THREADS'),'MKL_NUM_THREADS':os.environ.get('MKL_NUM_THREADS')},'runtime':{'python':sys.version,'numpy':np.__version__},'effective_config':effective_config(),'inputs':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs},'output_hashes':files,'summary':summary}
 _write(out/'manifest.json',m);return m
def execute(output,inventory_fn=inventory,*,lock=LOCK,ledger=LEDGER,deadline=None,rejections=None):
 output=Path(output)
 with Attempt(output,lock=lock,ledger=ledger,deadline=deadline,rejections=rejections) as attempt:
  parent={'selected_rung':None,'execution_status':'RUNNING','outcome':'NOT_EVALUATED','observed_counts':{},'required_counts':{}}
  try:
   for spec in RUNGS:
    summary=run_rung(spec,output/spec.name,inventory_fn);parent[spec.name]=summary
    if summary['outcome']=='DATASET_PASS':parent['selected_rung']=spec.name;break
    if summary['outcome'] not in ('MAP_SUPPLY_FAILED','LENGTH_FLOW_FAILED','TRAINING_ORIENTATION_COVERAGE_FAILED'):raise TechnicalFailure('unrecognized ladder continuation')
   parent.update(execution_status='COMPLETE',outcome='DATASET_PASS' if parent['selected_rung'] else 'DATASET_LADDER_FAILED')
  except BaseException as exc:
   parent.update(execution_status='FAILED',outcome='DEADLINE' if isinstance(exc,Deadline) else 'TECHNICAL_FAILURE',error=repr(exc));raise
  finally:
   for spec in RUNGS:
    path=output/spec.name/'summary.json'
    if path.exists():parent[spec.name]=json.loads(path.read_text())
    if spec.name in parent:
     parent['observed_counts'][spec.name]=parent[spec.name].get('observed_counts',{});parent['required_counts'][spec.name]=parent[spec.name].get('required_counts',{})
   _write(output/'summary.json',parent);_manifest(output,parent);attempt.manifest_sha256=hashlib.sha256((output/'manifest.json').read_bytes()).hexdigest()
  return parent
def main():
 p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args();execute(a.output)
if __name__=='__main__':main()
