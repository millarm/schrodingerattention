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
from execution.difficult_problem_solving import d1_watchdog as watchdog

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
def _provenance(): return {'hashes':watchdog.file_hashes(),'authorities':watchdog.authority_hashes(),'analysis_source_expected_sha256':ANALYSIS_SHA}
def retained_metadata(root=ROOT):
 root=Path(root); common=None; rows={}
 for seed in SEEDS:
  owner=root/f'replication-{seed}-analysis'; attempt=json.loads((owner/'attempt.json').read_text())
  if attempt.get('status')!='COMPLETE': raise core.IdentityError('analysis owner incomplete')
  _manifest_file(owner,'attempt.json'); _manifest_file(owner,'analysis.json'); a=json.loads((owner/'analysis.json').read_text()); ids=a.get('input_ids')
  if a.get('status')!='COMPLETE' or a.get('seed')!=seed or a.get('source_hashes',{}).get('execution/seed_replication/analyze.py')!=ANALYSIS_SHA or not isinstance(ids,dict) or(common is not None and ids!=common): raise core.IdentityError('analysis identity mismatch')
  common=ids; stored=a.get('stored_fullvalidation',{}).get('8000',{}).get('t1',{}); qc=a.get('quality_control',{}).get('grid',[])
  if len(qc)!=3 or {x.get('temperature')for x in qc}!={.75,1.,1.25}: raise core.IdentityError('retained temperature grid mismatch')
  find=lambda t:next(x.get('raw')for x in qc if x.get('temperature')==t)
  if _canon(find(1.))!=_canon(stored.get('sa')): raise core.IdentityError('retained SA T1 copies differ')
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
def corroborate_raw(raw,problems):
 """Local verification only; authority is the caller's bound analysis manifest.

 The synthetic event digest is NOT independent historical producer evidence.
 """
 event={'routes':{'t1_k32':raw}}
 event['_binding']={'event_sha256':_event_digest(event)}
 routes,_=_storedroutes(event,'t1_k32',problems)
 return {'verified_attempts':len(routes),'raw_sha256':hashlib.sha256(_canon(raw)).hexdigest(),
         'authority':'manifest-bound analysis/seed/temperature; local order/validity corroboration',
         'limitation':'all-invalid within-map permutations cannot be distinguished'}
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
 def __init__(self,output): self.output=Path(output); self.cells=self.output/'cells'; self.greedy=self.output/'greedy'; self.cells.mkdir(parents=True,exist_ok=True); self.greedy.mkdir(parents=True,exist_ok=True); self.index=[]; self.greedy_index=[]; self.panel_sha=None; self.bindings={}; self.write_seconds=0.
 def emit(self,c):
  started=time.perf_counter()
  ident=f"{c['seed']}-{c['mode']}-{float(c['temperature']):g}"; path=self.cells/(ident+'.json')
  if path.exists()or any(x['cell_id']==ident for x in self.index): raise FileExistsError('immutable endpoint '+ident)
  row=dict(c); greedy=row.pop('greedy'); panel=row.pop('problem_ids'); panel_path=self.output/'panel.json'
  binding=row.pop('shared_binding'); shared_path=self.output/f"binding-{c['seed']}.json"
  binding_hash=hashlib.sha256(_canon(binding)).hexdigest()
  if not shared_path.exists(): _atomic_json(shared_path,binding)
  elif sha(shared_path)!=binding_hash: raise core.IdentityError('shared binding changed')
  row['binding_sha256']=binding_hash; self.bindings[str(c['seed'])]=binding_hash
  if self.panel_sha is None:
   _atomic_json(panel_path,{'ordered_problem_ids':panel}); self.panel_sha=sha(panel_path)
  elif sha(panel_path)!=self.panel_sha: raise core.IdentityError('shared panel mutation')
  row['panel_sha256']=self.panel_sha; gid=f"{c['seed']}-{c['mode']}"; gp=self.greedy/(gid+'.json')
  if not gp.exists(): _atomic_json(gp,greedy); self.greedy_index.append({'greedy_id':gid,'sha256':sha(gp)})
  elif sha(gp)!=hashlib.sha256(_canon(greedy)).hexdigest(): raise core.IdentityError('greedy record mutation across endpoints')
  row['greedy_id']=gid; _atomic_json(path,row); self.index.append({'cell_id':ident,'sha256':sha(path),'status':'COMPLETE','seed':c['seed'],'mode':c['mode'],'temperature':c['temperature'],'reused':c['reused']}); _atomic_json(self.output/'cell-index.json',{'status':'PARTIAL','cells':self.index,'greedy':self.greedy_index})
  self.write_seconds+=time.perf_counter()-started
 def finish(self):
  if {e['cell_id']for e in self.index}!={f'{s}-{m}-{t:g}'for s,m,t in grid()} or {g['greedy_id']for g in self.greedy_index}!={f'{s}-{m}'for s in SEEDS for m in ('sm','sa')} or self.panel_sha is None: raise core.IdentityError('incomplete durable D1 output')
  _atomic_json(self.output/'cell-index.json',{'status':'COMPLETE','cells':self.index,'greedy':self.greedy_index,'panel_sha256':self.panel_sha,'bindings':self.bindings}); return list(self.index)
def _defaults(): return {'metadata':retained_metadata,'validation':load_validation,'training':load_training,'pair':validate_pair,'event':retained_event,'model':_model,'evaluator':evaluate_rollouts,'panel':_panel,'validate_cells':validate_cells}
def produce_cells(root=ROOT,*,emit=None,deps=None):
 loading_started=time.perf_counter()
 d=_defaults(); d.update(deps or {}); root=Path(root); ids,old=d['metadata'](root); validation=d['validation'](); ordered=d['panel'](validation.problems); training=d['training'](); support=frozenset(training.support); support_digest=_support_digest(support)
 if training.support_hash!=support_digest: raise core.IdentityError('accepted training support hash mismatch')
 training_identity={'input_ids':ids,'support_hash':training.support_hash}; cells=[]; setup_seconds=time.perf_counter()-loading_started
 for seed in SEEDS:
  seed_loading_started=time.perf_counter()
  pair=d['pair'](root,seed,ids)
  retained_pair=old[seed]['pair']
  for key in ('checkpoint_hashes','checkpoint_identity','initial_checkpoint_hashes','owner_authority','shared_initial_digest','batch_prefix'):
   if pair.get(key)!=retained_pair.get(key): raise core.IdentityError('retained/current pair binding mismatch: '+key)
  models={}; digest=_uniform_digest(validation.problems,seed)
  shared_binding={'input_ids':ids,'support_hash':support_digest,'uniform_digest':digest,
      'rng':{'seed':seed,'splitcode':1,'replicate':0,'k':32,'scheme':'accepted rollout_uniforms PCG64 SeedSequence95002'},
      'analysis_sha256':old[seed]['analysis_sha256'],'pair':retained_pair,'training_identity':training_identity,
      'setup_seconds_once':setup_seconds if seed==SEEDS[0]else None,'evidence':{}}
  for mode,owner_mode in (('sm','softmax'),('sa','schrodinger')):
   payload=pair[mode+'_payload']; checkpoint=pair['checkpoint_hashes'][mode]; identity={'identity':pair['checkpoint_identity'][mode],'initial':pair['initial_checkpoint_hashes'][mode],'authority':pair['owner_authority'][mode]}
   if identity['identity'].get('seed')!=seed or identity['identity'].get('mode')!=owner_mode or identity['identity'].get('input_ids')!=ids: raise core.IdentityError('pair/checkpoint mismatch')
   event,event_hash=d['event'](root,seed,mode,ids,old[seed]['bindings'].get(mode)); models[mode]=(CountingModel(d['model'](payload)),checkpoint,identity,event,bound_greedy(event,validation.problems))
   proper=event.get('proper') or {}
   shared_binding['evidence'][mode]={'event_binding':old[seed]['bindings'].get(mode),'result_sha256':event_hash,
       'greedy_timing':event['routes']['greedy'].get('timing',{}),
       'proper_timing':proper.get('timing',{}),'proper_rows':len(proper.get('rows',[]))}
  shared_binding['seed_loading_seconds']=time.perf_counter()-seed_loading_started
  for mode in ('sm','sa'):
   model,checkpoint,identity,event,greedy=models[mode]
   for (m,temp),raw in old[seed]['raw'].items():
    if m==mode:
     if [(p['map_id'],p['family'])for p in raw['problems']]!=[(p.map_id,p.family)for p in validation.problems]: raise core.IdentityError('retained dataset order mismatch')
     verified=corroborate_raw(raw,validation.problems)
     c=_cell(seed,mode,temp,ordered,checkpoint,raw,reused=True,event=_event_digest(event),greedy=greedy,uniform_digest=digest,forward_calls=None,batch_states=None,generated_actions=None,historical_counter_status='unavailable: retained artifacts did not record counters',training_identity=training_identity,support_digest=support_digest,shared_binding=shared_binding,corroboration=verified); cells.append(c); emit and emit(c)
  for mode in(('sm','sa')if seed in(1702,1704)else('sa','sm')):
   model,checkpoint,identity,event,greedy=models[mode]; cache={}; missing=(.5,.75,1.25,1.5)if mode=='sm'else(.5,1.5)
   for n,temp in enumerate(missing):
    fc,bs=model.forward_calls,model.batch_states; start=time.perf_counter(); result=d['evaluator'](model,validation.problems,identity=checkpoint,seed=seed,splitcode=1,support=support,k=32,temperature=temp,replicate=0,cache=cache); elapsed=time.perf_counter()-start
    c=_cell(seed,mode,temp,ordered,checkpoint,result,reused=False,event=_event_digest(event),greedy=greedy,uniform_digest=digest,forward_calls=model.forward_calls-fc,batch_states=model.batch_states-bs,generated_actions=sum(len(a['route'])for p in result['problems']for a in p['attempts']),endpoint_elapsed_seconds=elapsed,cache_phase='cold'if n==0 else'incremental',training_identity=training_identity,support_digest=support_digest,shared_binding=shared_binding); cells.append(c); emit and emit(c)
 return d['validate_cells'](cells)
def validate_cells(cells):
 keys=[(x.get('seed'),x.get('mode'),float(x.get('temperature')))for x in cells]
 if len(keys)!=40 or len(set(keys))!=40 or set(keys)!=set(grid()): raise core.IdentityError('exact 40-cell grid required')
 ordered=None; seed_rng={}; checkpoints={}
 for x in cells:
  if x.get('k')!=32 or x.get('splitcode')!=1 or x.get('replicate')!=0 or not isinstance(x.get('checkpoint'),str)or not isinstance(x.get('support_digest'),str)or not isinstance(x.get('uniform_digest'),str)or not isinstance(x.get('training_identity'),dict): raise core.IdentityError('cell binding missing')
  ids=x.get('problem_ids')
  if not isinstance(ids,list)or len(ids)!=512 or len({repr(v)for v in ids})!=512 or(ordered is not None and ids!=ordered)or bool(x.get('reused'))!=((x['mode'],float(x['temperature']))in REUSED): raise core.IdentityError('cell panel/reuse mismatch')
  ordered=ids
  if x['training_identity'].get('support_hash')!=x['support_digest']:raise core.IdentityError('cell training support mismatch')
  previous=seed_rng.setdefault(x['seed'],(x['uniform_digest'],x['support_digest']))
  if previous!=(x['uniform_digest'],x['support_digest']):raise core.IdentityError('within-seed RNG/support changed')
  if checkpoints.setdefault((x['seed'],x['mode']),x['checkpoint'])!=x['checkpoint']:raise core.IdentityError('within-model checkpoint changed')
  if any(not isinstance(x.get(k),(float,int))or not math.isfinite(x[k])or not 0<=x[k]<=1 for k in('routine_Q','challenge_Q','challenge_pass')):raise core.IdentityError('invalid selection metric')
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
 components=[]; bindings={}
 for c in cells:
  if isinstance(c.get('endpoint_elapsed_seconds'),(int,float)): observed[c.get('cache_phase','incremental')].append(c['endpoint_elapsed_seconds'])
  timing=c.get('raw',{}).get('timing',{})
  for o,k in(('sampling','categorical_rollout_seconds'),('verification','verifier_uniqueness_seconds')):
   if isinstance(timing.get(k),(int,float)): observed[o].append(timing[k])
  components.append({'cell_id':f"{c['seed']}-{c['mode']}-{float(c['temperature']):g}",'problem_count':len(c['problem_ids']),'k':32,'reused':c['reused'],'cache_phase':c.get('cache_phase'),'endpoint_elapsed_seconds':c.get('endpoint_elapsed_seconds'),'raw_timing':timing})
  bindings[str(c['seed'])]=c.get('shared_binding',{})
 return {k:None for k in COSTS}|{'observed_d1_timing_seconds':{'endpoint_components':components,'shared_loading_greedy_proper_evidence':bindings,'definition':'whole endpoint overlaps its cache/sampling/verifier subcomponents; never sum both; historical counters unavailable'}}
def compose(cells,costs,maps):
 validate_cells(cells); selected={str(s):select(cells,s)for s in SEEDS}; complete=not any(x.get('control_no_go')for x in selected.values()); deltas=[selected[str(s)]['sa']['challenge_pass']-selected[str(s)]['sm']['challenge_pass']for s in SEEDS]if complete else None
 def compact(c):
  return {'cell_id':f"{c['seed']}-{c['mode']}-{float(c['temperature']):g}",'temperature':c['temperature'],'routine_Q':c['routine_Q'],'challenge_Q':c['challenge_Q'],'challenge_pass':c['challenge_pass'],'strata':c['raw']['strata']}
 references={s:{m:compact(c)if isinstance(c,dict)else c for m,c in v.items()}for s,v in selected.items()}
 t1={str(s):{m:compact(next(c for c in cells if(c['seed'],c['mode'],float(c['temperature']))==(s,m,1.)))for m in('sm','sa')}for s in SEEDS}
 return {'status':'COMPLETE'if complete else'CONTROL_NO_GO','selected':references,'t1':t1,'paired_challenge_pass_deltas':deltas,'forecast':{'status':'D2_FORECAST_DEFERRED/NO_GO','missing_essential_costs':[k for k in COSTS if costs.get(k)is None],'observed_d1_timing_seconds':costs.get('observed_d1_timing_seconds',{}),'reason':'D2 forecast implementation deferred by explicit approval; retained D1 components are not a scaled D2 forecast'},'uncertainty':uncertainty(deltas,maps)if deltas else None,'route_order_limitation':'valid stored routes corroborate order; all-invalid permutations remain indistinguishable'}
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
 if {e['cell_id']for e in idx['cells']}!={f'{s}-{m}-{t:g}'for s,m,t in grid()}:raise core.IdentityError('index grid mismatch')
 if {e['greedy_id']for e in idx['greedy']}!={f'{s}-{m}'for s in SEEDS for m in('sm','sa')}:raise core.IdentityError('greedy grid mismatch')
 for e in idx['cells']:
  p=Path(output)/'cells'/(e['cell_id']+'.json')
  if not p.is_file()or sha(p)!=e['sha256']: raise core.IdentityError('cell hash mismatch')
  row=json.loads(p.read_text())
  if (row['seed'],row['mode'],row['temperature'],row['reused'])!=(e['seed'],e['mode'],e['temperature'],e['reused']):raise core.IdentityError('cell index identity mismatch')
  binding=Path(output)/f"binding-{row['seed']}.json"
  if sha(binding)!=row.pop('binding_sha256',None) or sha(binding)!=idx['bindings'].get(str(row['seed'])):raise core.IdentityError('shared binding hash mismatch')
  row['shared_binding']=json.loads(binding.read_text())
  if row.get('greedy_id')!=f"{row['seed']}-{row['mode']}":raise core.IdentityError('greedy reference mismatch')
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
 if Path(root).resolve()!=watchdog.ROOT.resolve():raise PermissionError('unexpected production root')
 watchdog.validate_decision(path,expected_kind='production')
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
  if generated: out['cells']=index; out['output_write_seconds_before_final_report']=sink.write_seconds
  out.update({'scope':{'test_access':False,'training':False},'provenance':{**_provenance(),'code':sha(__file__),'argv':list(sys.argv),'stage_table':STAGES,'max_seconds':300.,'timer_cap_seconds':cap}}); _atomic_json(attempt.output/'d1.json',out)
 return out
def main(argv=None):
 p=argparse.ArgumentParser(); p.add_argument('--production-decision',required=True); a=p.parse_args(argv); run(production_decision=a.production_decision)
if __name__=='__main__':main()
