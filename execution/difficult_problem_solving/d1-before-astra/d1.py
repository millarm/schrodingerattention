"""Frozen D1 validation comparison. Production model work is only reachable via run."""
from __future__ import annotations
import argparse, hashlib, json, math, os, signal, sys, tempfile, time
from pathlib import Path
import numpy as np
from execution.paired_behavior.job import _event_digest, _storedroutes
from execution.seed_replication.analyze import _checkpoint, _manifest_file, _model, validate_pair
from schrodinger import route_policy_experiment as core
from schrodinger.route_policy_data import load_training, load_validation
from schrodinger.route_policy_evaluation import evaluate_rollouts
from schrodinger.route_policy_metrics import rollout_uniforms

HERE=Path(__file__).resolve().parent; ROOT=HERE.parent/'model_training_comparison'
SEEDS=(1702,1703,1704,1705); TEMPS=(.5,.75,1.,1.25,1.5); REUSED=frozenset((('sm',1.),('sa',.75),('sa',1.),('sa',1.25)))
PRISTINE_STAGES={'A':700.,'B':2000.,'C':1900.,'D':1300.}; STAGES={'A':1000.,'B':3500.,'C':0.,'D':1400.}
PLAN=HERE/'d1-minimal-repair-plan.md'; APPROVAL=HERE/'d1-recovery-approval.md'; STATIC_REVIEW=HERE/'d1-repair-static-review.md'; PLAN_SHA='370650b044b51eab8c331b54718e0af85be9dfa75758bab695e23cc4312d2a31'; ANALYSIS_SHA='cbf8d19b31b429a91e48ad3dba2e2079ab0245d9811c92ad9e0e851bc8ffa3dd'
COSTS=('cold','incremental','sampling','verification','bank','loading','io_finalization')
def sha(path):
 d=hashlib.sha256()
 with Path(path).open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''): d.update(b)
 return d.hexdigest()
def _canon(x): return json.dumps(core._serializable(x),sort_keys=True,separators=(',',':'),allow_nan=False).encode()
def _atomic_json(path,value):
 path=Path(path); path.parent.mkdir(parents=True,exist_ok=True); fd,tmp=tempfile.mkstemp(prefix='.'+path.name+'.',dir=path.parent)
 try:
  with os.fdopen(fd,'wb') as f: f.write(_canon(value)); f.flush(); os.fsync(f.fileno())
  os.replace(tmp,path); d=os.open(path.parent,os.O_RDONLY); os.fsync(d); os.close(d)
 finally:
  if os.path.exists(tmp): os.unlink(tmp)
def grid(): return [(s,m,t)for s in SEEDS for m in ('sm','sa') for t in TEMPS]
def required_new(): return [x for x in grid() if x[1:] not in REUSED]
def ids_of(problems): return [(p.canonical.hex(),p.map_id,p.family,p.start,p.goal)for p in problems]
def _panel(problems):
 ids=ids_of(problems); maps={}
 for p in problems: maps.setdefault(p.map_id,[]).append(p)
 if len(ids)!=512 or len(set(ids))!=512 or len(maps)!=32 or any(len(v)!=16 for v in maps.values()): raise core.IdentityError('validation 512/32x16 mismatch')
 counts={f:sum(v[0].family==f for v in maps.values())for f in ('IIIIIIII','LLLLLLLL','IIIILLLL')}
 if counts!={'IIIIIIII':12,'LLLLLLLL':12,'IIIILLLL':8} or any(any(p.family!=v[0].family for p in v)for v in maps.values()): raise core.IdentityError('validation 12I/12L/8mixed mismatch')
 return ids
def _support_digest(s):
 rows=tuple(sorted(s))
 if any(not isinstance(x,bytes) or not x for x in rows): raise core.IdentityError('invalid training support')
 return hashlib.sha256(b''.join(len(x).to_bytes(2,'big')+x for x in rows)).hexdigest()
def _provenance(): return {'d1_source_sha256':sha(__file__),'plan_sha256':sha(PLAN),'approval_sha256':sha(APPROVAL),'static_review_sha256':sha(STATIC_REVIEW),'analysis_source_expected_sha256':ANALYSIS_SHA}
def retained_metadata(root=ROOT):
 root=Path(root); common=None; rows={}
 for seed in SEEDS:
  owner=root/f'replication-{seed}-analysis'; attempt=json.loads((owner/'attempt.json').read_text())
  if attempt.get('status')!='COMPLETE': raise core.IdentityError('analysis owner incomplete')
  _manifest_file(owner,'attempt.json'); _manifest_file(owner,'analysis.json'); a=json.loads((owner/'analysis.json').read_text()); ids=a.get('input_ids')
  if a.get('status')!='COMPLETE' or a.get('seed')!=seed or a.get('source_hashes',{}).get('execution/seed_replication/analyze.py')!=ANALYSIS_SHA or not isinstance(ids,dict) or(common is not None and ids!=common): raise core.IdentityError('analysis identity mismatch')
  common=ids; stored=a.get('stored_fullvalidation',{}).get('8000',{}).get('t1',{}); qc=a.get('quality_control',{}).get('grid',[]); find=lambda t:next((x.get('raw')for x in qc if x.get('temperature')==t),None)
  raw={('sm',1.):stored.get('sm'),('sa',.75):find(.75),('sa',1.):stored.get('sa'),('sa',1.25):find(1.25)}
  for r in raw.values():
   if not isinstance(r,dict)or len(r.get('problems',[]))!=512 or any(len(p.get('attempts',[]))!=32 or not isinstance(z.get('route'),str)for p in r['problems']for z in p['attempts']): raise core.IdentityError('retained K32 routes mismatch')
  if not isinstance(a.get('pair'),dict): raise core.IdentityError('accepted pair absent')
  rows[seed]={'analysis_sha256':sha(owner/'analysis.json'),'pair':a['pair'],'raw':raw,'bindings':a.get('stored_fullvalidation',{}).get('8000',{}).get('event_bindings',{})}
 return common,rows
def retained_event(root,seed,mode,ids,binding):
 owner=Path(root)/f"replication-{seed}-{'softmax'if mode=='sm'else'schrodinger'}-8000"; rh=_manifest_file(owner,'result.json'); result=json.loads((owner/'result.json').read_text()); event=next((x for x in result.get('result',{}).get('events',[])if x.get('update')==8000),None)
 if result.get('input_ids')!=ids or not isinstance(binding,dict)or event is None or binding.get('event_sha256')!=_event_digest(event)or binding.get('result_sha256')!=rh or binding.get('input_ids')!=ids: raise core.IdentityError('final event binding mismatch')
 event=dict(event); event['_binding']=dict(binding)
 return event,rh
def bound_greedy(event,problems):
 routes,raw=_storedroutes(event,'greedy',problems)
 if len(routes)!=len(problems): raise core.IdentityError('bound greedy count mismatch')
 return {'raw':raw,'route_count':len(routes),'route_order_corrobated':True,'all_invalid_permutation_limitation':'all-invalid rows cannot distinguish within-map permutation'}
class CountingModel:
 def __init__(self,model): self.model=model; self.mode=getattr(model,'mode','fixture'); self.forward_calls=0; self.batch_states=0
 def __call__(self,x,**kw): self.forward_calls+=1; self.batch_states+=len(x); return self.model(x,**kw)
def _uniform_digest(problems,seed):
 h=hashlib.sha256()
 for p in problems:
  for k in range(32): h.update(np.asarray(rollout_uniforms(seed,1,p.map_id,p.start,p.goal,0,k),dtype=np.float64).tobytes())
 return h.hexdigest()
def _cell(seed,mode,temp,ids,checkpoint,result,**extra):
 s=result['strata']; return {'seed':seed,'mode':mode,'temperature':temp,'k':32,'splitcode':1,'replicate':0,'problem_ids':ids,'routine_Q':s['routine']['Q'],'challenge_Q':s['challenge']['Q'],'challenge_pass':s['challenge']['pass_at_k'],'raw':{k:v for k,v in result.items()if k!='cache'},'checkpoint':checkpoint,**extra}
class CellSink:
 def __init__(self,output): self.output=Path(output); self.cells=self.output/'cells'; self.greedy=self.output/'greedy'; self.cells.mkdir(parents=True,exist_ok=True); self.greedy.mkdir(parents=True,exist_ok=True); self.index=[]; self.greedy_index=[]; self.panel_sha=None
 def emit(self,c):
  ident=f"{c['seed']}-{c['mode']}-{float(c['temperature']):g}"; path=self.cells/(ident+'.json')
  if path.exists()or any(x['cell_id']==ident for x in self.index): raise FileExistsError('immutable endpoint '+ident)
  row=dict(c); greedy=row.pop('greedy'); panel=row.pop('problem_ids'); panel_path=self.output/'panel.json'
  if self.panel_sha is None:
   _atomic_json(panel_path,{'ordered_problem_ids':panel}); self.panel_sha=sha(panel_path)
  elif sha(panel_path)!=self.panel_sha: raise core.IdentityError('shared panel mutation')
  row['panel_sha256']=self.panel_sha; gid=f"{c['seed']}-{c['mode']}"; gp=self.greedy/(gid+'.json')
  if not gp.exists(): _atomic_json(gp,greedy); self.greedy_index.append({'greedy_id':gid,'sha256':sha(gp)})
  elif sha(gp)!=hashlib.sha256(_canon(greedy)).hexdigest(): raise core.IdentityError('greedy record mutation across endpoints')
  row['greedy_id']=gid; _atomic_json(path,row); self.index.append({'cell_id':ident,'sha256':sha(path),'status':'COMPLETE','seed':c['seed'],'mode':c['mode'],'temperature':c['temperature'],'reused':c['reused']}); _atomic_json(self.output/'cell-index.json',{'status':'PARTIAL','cells':self.index,'greedy':self.greedy_index})
 def finish(self):
  if len(self.index)!=40 or len(self.greedy_index)!=8 or self.panel_sha is None: raise core.IdentityError('incomplete durable D1 output')
  _atomic_json(self.output/'cell-index.json',{'status':'COMPLETE','cells':self.index,'greedy':self.greedy_index,'panel_sha256':self.panel_sha}); return list(self.index)
def _defaults(): return {'metadata':retained_metadata,'validation':load_validation,'training':load_training,'pair':validate_pair,'event':retained_event,'model':_model,'evaluator':evaluate_rollouts,'panel':_panel,'validate_cells':validate_cells}
def produce_cells(root=ROOT,*,emit=None,deps=None):
 d=_defaults(); d.update(deps or {}); root=Path(root); ids,old=d['metadata'](root); validation=d['validation'](); ordered=d['panel'](validation.problems); training=d['training'](); support=frozenset(training.support); support_digest=_support_digest(support)
 if training.support_hash!=support_digest: raise core.IdentityError('accepted training support hash mismatch')
 training_identity={'input_ids':ids,'support_hash':training.support_hash}; cells=[]
 for seed in SEEDS:
  pair=d['pair'](root,seed,ids)
  retained_pair=old[seed]['pair']
  for key in ('checkpoint_hashes','checkpoint_identity','initial_checkpoint_hashes','owner_authority','shared_initial_digest','batch_prefix'):
   if pair.get(key)!=retained_pair.get(key): raise core.IdentityError('retained/current pair binding mismatch: '+key)
  models={}
  for mode,owner_mode in (('sm','softmax'),('sa','schrodinger')):
   payload=pair[mode+'_payload']; checkpoint=pair['checkpoint_hashes'][mode]; identity={'identity':pair['checkpoint_identity'][mode],'initial':pair['initial_checkpoint_hashes'][mode],'authority':pair['owner_authority'][mode]}
   if identity['identity'].get('seed')!=seed or identity['identity'].get('mode')!=owner_mode or identity['identity'].get('input_ids')!=ids: raise core.IdentityError('pair/checkpoint mismatch')
   event,_=d['event'](root,seed,mode,ids,old[seed]['bindings'].get(mode)); models[mode]=(CountingModel(d['model'](payload)),checkpoint,identity,event,bound_greedy(event,validation.problems))
   for (m,temp),raw in old[seed]['raw'].items():
    if m==mode:
     if [(p['map_id'],p['family'])for p in raw['problems']]!=[(p.map_id,p.family)for p in validation.problems]: raise core.IdentityError('retained dataset order mismatch')
     c=_cell(seed,mode,temp,ordered,checkpoint,raw,reused=True,event=_event_digest(event),greedy=models[mode][4],uniform_digest=_uniform_digest(validation.problems,seed),forward_calls=None,batch_states=None,generated_actions=None,historical_counter_status='unavailable: retained artifacts did not record counters',training_identity=training_identity,support_digest=support_digest); cells.append(c); emit and emit(c)
  for mode in(('sm','sa')if seed in(1702,1704)else('sa','sm')):
   model,checkpoint,identity,event,greedy=models[mode]; cache={}; missing=(.5,.75,1.25,1.5)if mode=='sm'else(.5,1.5); digest=_uniform_digest(validation.problems,seed)
   for n,temp in enumerate(missing):
    fc,bs=model.forward_calls,model.batch_states; start=time.perf_counter(); result=d['evaluator'](model,validation.problems,identity=checkpoint,seed=seed,splitcode=1,support=support,k=32,temperature=temp,replicate=0,cache=cache); elapsed=time.perf_counter()-start
    c=_cell(seed,mode,temp,ordered,checkpoint,result,reused=False,event=_event_digest(event),greedy=greedy,uniform_digest=digest,forward_calls=model.forward_calls-fc,batch_states=model.batch_states-bs,generated_actions=sum(len(a['route'])for p in result['problems']for a in p['attempts']),endpoint_elapsed_seconds=elapsed,cache_phase='cold'if n==0 else'incremental',training_identity=training_identity,support_digest=support_digest); cells.append(c); emit and emit(c)
 return d['validate_cells'](cells)
def validate_cells(cells):
 keys=[(x.get('seed'),x.get('mode'),float(x.get('temperature')))for x in cells]
 if len(keys)!=40 or len(set(keys))!=40 or set(keys)!=set(grid()): raise core.IdentityError('exact 40-cell grid required')
 ordered=None
 for x in cells:
  if x.get('k')!=32 or x.get('splitcode')!=1 or x.get('replicate')!=0 or not isinstance(x.get('checkpoint'),str)or not isinstance(x.get('support_digest'),str)or not isinstance(x.get('uniform_digest'),str)or not isinstance(x.get('training_identity'),dict): raise core.IdentityError('cell binding missing')
  ids=x.get('problem_ids')
  if not isinstance(ids,list)or len(ids)!=512 or len({repr(v)for v in ids})!=512 or(ordered is not None and ids!=ordered)or bool(x.get('reused'))!=((x['mode'],float(x['temperature']))in REUSED): raise core.IdentityError('cell panel/reuse mismatch')
  ordered=ids
 return cells
def select(cells,seed):
 by={(x['mode'],float(x['temperature'])):x for x in cells if x['seed']==seed}; ref=by.get(('sm',1.))
 if ref is None: raise core.IdentityError('missing SM T1')
 out={'sm':ref}
 for mode in('sm','sa'):
  c=[x for(m,_),x in by.items()if m==mode and x['routine_Q']>=ref['routine_Q']-.02 and x['challenge_Q']>=ref['challenge_Q']-.02]
  if not c:
   if mode=='sa': out['control_no_go']=True; continue
   raise core.IdentityError('SM floor failed')
  p=max(x['challenge_pass']for x in c); c=[x for x in c if p-x['challenge_pass']<=1e-12]; q=max(x['challenge_Q']for x in c); out[mode]=min((x for x in c if q-x['challenge_Q']<=1e-12),key=lambda x:x['temperature'])
 return out
def uncertainty(seed_deltas,maps_by_seed):
 x=np.asarray(seed_deltas,float); maps=np.asarray(maps_by_seed,float)
 if x.shape!=(4,)or maps.shape!=(4,8): raise core.IdentityError('requires 4 seeds / 8 shared maps')
 sd=float(x.std(ddof=1)); half=3.182446*sd/2; rng=np.random.Generator(np.random.PCG64(91703)); samples=np.asarray([maps[:,rng.integers(0,8,8)].mean(axis=1).mean()for _ in range(2000)]); lo,hi=np.quantile(samples,[.025,.975],method='linear'); width=float(hi-lo)
 return {'mean':float(x.mean()),'sample_sd':sd,'seed_half_width':half,'seed_full_width':2*half,'map_interval':[float(lo),float(hi)],'map_full_width':width,'approx_32_map_width':width*.5,'selection_fixed':True,'map_assumptions':'iid/exchangeable maps only'}
def forecast_costs(cells):
 observed={k:[]for k in COSTS}
 for c in cells:
  if isinstance(c.get('endpoint_elapsed_seconds'),(int,float)): observed[c.get('cache_phase','incremental')].append(c['endpoint_elapsed_seconds'])
  timing=c.get('raw',{}).get('timing',{})
  for o,k in(('sampling','categorical_rollout_seconds'),('verification','verifier_uniqueness_seconds')):
   if isinstance(timing.get(k),(int,float)): observed[o].append(timing[k])
 return {k:None for k in COSTS}|{'observed_d1_timing_seconds':observed}
def compose(cells,costs,maps):
 validate_cells(cells); selected={str(s):select(cells,s)for s in SEEDS}; complete=not any(x.get('control_no_go')for x in selected.values()); deltas=[selected[str(s)]['sa']['challenge_pass']-selected[str(s)]['sm']['challenge_pass']for s in SEEDS]if complete else None
 return {'status':'COMPLETE'if complete else'CONTROL_NO_GO','cells':cells,'selected':selected,'forecast':{'status':'D2_FORECAST_DEFERRED/NO_GO','missing_essential_costs':[k for k in COSTS if costs.get(k)is None],'observed_d1_timing_seconds':costs.get('observed_d1_timing_seconds',{}),'reason':'available D1 timing retained; no non-overlapping D2 bound'},'uncertainty':uncertainty(deltas,maps)if deltas else None,'route_order_limitation':'valid stored routes corroborate order; all-invalid permutations remain indistinguishable'}
def load_indexed_cells(output, *, expected_problem_count=512):
 idx=json.loads((Path(output)/'cell-index.json').read_text())
 panel=Path(output)/'panel.json'
 if idx.get('status')!='COMPLETE'or len(idx.get('cells',[]))!=40 or len(idx.get('greedy',[]))!=8 or not panel.is_file() or sha(panel)!=idx.get('panel_sha256'): raise core.IdentityError('partial grid cannot select')
 problem_ids=json.loads(panel.read_text()).get('ordered_problem_ids')
 if not isinstance(problem_ids,list) or len(problem_ids)!=expected_problem_count: raise core.IdentityError('shared panel missing')
 for g in idx['greedy']:
  path=Path(output)/'greedy'/(g['greedy_id']+'.json')
  if not path.is_file() or sha(path)!=g['sha256']: raise core.IdentityError('greedy hash mismatch')
 cells=[]
 for e in idx['cells']:
  p=Path(output)/'cells'/(e['cell_id']+'.json')
  if not p.is_file()or sha(p)!=e['sha256']: raise core.IdentityError('cell hash mismatch')
  row=json.loads(p.read_text())
  if row.pop('panel_sha256',None)!=idx['panel_sha256']: raise core.IdentityError('cell panel reference mismatch')
  row['problem_ids']=problem_ids; cells.append(row)
 return validate_cells(cells)
def selected_map_contrasts(cells,selected):
 rows=[]
 for seed in SEEDS:
  def index(v): return {x['map_id']:x['metrics']['pass_at_k']for x in(v.values()if isinstance(v,dict)else v)if x.get('family')=='IIIILLLL'}
  left,right=index(selected[str(seed)]['sm']['raw'].get('maps',{})),index(selected[str(seed)]['sa']['raw'].get('maps',{}))
  if set(left)!=set(right)or len(left)!=8: raise core.IdentityError('challenge map binding mismatch')
  rows.append([right[m]-left[m]for m in sorted(left)])
 return rows
def require_production_decision(path,root):
 """Decision is written only after implementation PASS; booleans are not authority."""
 decision=json.loads(Path(path).read_text())
 required={'kind':'d1-production-release','owner':'difficult-d1-repair-001','command':['-m','execution.difficult_problem_solving.d1','--production-decision',str(Path(path))],'d1_sha256':sha(__file__),'test_sha256':sha(HERE.parents[1]/'tests/test_difficult_problem_solving_d1.py'),'watchdog_sha256':sha(HERE/'d1_watchdog.py'),'plan_sha256':sha(PLAN),'approval_sha256':sha(APPROVAL),'static_review_sha256':sha(STATIC_REVIEW)}
 if any(decision.get(k)!=v for k,v in required.items()): raise PermissionError('exact D1 production decision binding mismatch')
 ledger=Path(root)/'ledger.jsonl'
 if decision.get('ledger_sha256')!=sha(ledger) or decision.get('ledger_prefix_sha256')!='770d3490766d0ec2e40a796ee8f896b4f1fbc3e7647c00d145cf4010dfc7d7c0': raise PermissionError('ledger decision binding mismatch')
 return {'path':str(Path(path).resolve()),'sha256':sha(path)}
def run(root=ROOT,*,cells=None,costs=None,maps_by_seed=None,production_decision=None,deps=None):
 if cells is None and not production_decision: raise PermissionError('exact production decision required')
 if core.STAGES!=PRISTINE_STAGES: raise core.BudgetError('unexpected pristine module stage table')
 core.STAGES.clear(); core.STAGES.update(STAGES); root=Path(root)
 with core.OwnedAttempt.begin(root,root/'ledger.jsonl','D','difficult-d1-repair-001')as attempt:
  cap=min(296.,core.deadline_seconds(root/'ledger.jsonl','D')); signal.setitimer(signal.ITIMER_REAL,cap); generated=cells is None
  if generated:
   decision_binding=require_production_decision(production_decision,root); core.configure_runtime(); sink=CellSink(attempt.output); _atomic_json(attempt.output/'provenance.json',{**_provenance(),'decision':decision_binding}); cells=produce_cells(root,emit=sink.emit,deps=deps); index=sink.finish(); cells=load_indexed_cells(attempt.output,expected_problem_count=(deps or {}).get('expected_problem_count',512))
  else:index=[]
  selected={str(s):select(cells,s)for s in SEEDS}; actual=selected_map_contrasts(cells,selected)if generated and not any(x.get('control_no_go')for x in selected.values())else maps_by_seed
  if actual is None and not any(x.get('control_no_go')for x in selected.values()): raise core.IdentityError('selected map contrasts required')
  out=compose(cells,forecast_costs(cells)if costs is None else costs,actual if actual is not None else np.zeros((4,8)))
  if generated: out['cells']=index
  out.update({'scope':{'test_access':False,'training':False},'provenance':{**_provenance(),'code':sha(__file__),'argv':list(sys.argv),'stage_table':STAGES,'max_seconds':300.,'timer_cap_seconds':cap}}); _atomic_json(attempt.output/'d1.json',out)
 return out
def main(argv=None):
 p=argparse.ArgumentParser(); p.add_argument('--production-decision',required=True); a=p.parse_args(argv); run(production_decision=a.production_decision)
if __name__=='__main__':main()
