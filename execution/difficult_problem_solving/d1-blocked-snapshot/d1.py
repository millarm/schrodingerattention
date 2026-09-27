"""D1 validation-only selection.  Production is review-gated by the caller."""
from __future__ import annotations
import argparse, hashlib, json, math, signal, sys, time
from pathlib import Path
import numpy as np
from execution.paired_behavior.job import _event_digest
from execution.seed_replication.analyze import _checkpoint, _manifest_file, _model
from schrodinger import route_policy_experiment as core
from schrodinger.route_policy_data import load_training, load_validation
from schrodinger.route_policy_evaluation import evaluate_rollouts
from schrodinger.route_policy_metrics import rollout_uniforms

HERE=Path(__file__).resolve().parent; ROOT=HERE.parent/'model_training_comparison'
SEEDS=(1702,1703,1704,1705); TEMPS=(.5,.75,1.,1.25,1.5)
REUSED=frozenset((('sm',1.),('sa',.75),('sa',1.),('sa',1.25)))
OLD_STAGES={'A':700.,'B':2000.,'C':1900.,'D':1300.}; STAGES={'A':700.,'B':3500.,'C':300.,'D':1400.}
PLAN_SHA='c31c3ee84131ec4e96dbbd42e073a4ec96be63a0b3fc65058a18275714c035fe'
SPEC_SHA='f36ab859b0eb8f7c5e120605a4963bb5ba8c48428a481345695f3b058efa76ad'
ANALYSIS_SHA='cbf8d19b31b429a91e48ad3dba2e2079ab0245d9811c92ad9e0e851bc8ffa3dd'
COSTS=('cold','incremental','sampling','verification','bank','loading','io_finalization')

def sha(path):
 d=hashlib.sha256()
 with Path(path).open('rb') as h:
  for b in iter(lambda:h.read(1048576),b''): d.update(b)
 return d.hexdigest()
def grid(): return [(s,m,t)for s in SEEDS for m in ('sm','sa') for t in TEMPS]
def required_new(): return [x for x in grid() if x[1:] not in REUSED]
def ids_of(problems): return [(p.canonical.hex(),p.map_id,p.family,p.start,p.goal)for p in problems]
def _panel(problems):
 ids=ids_of(problems); maps={}
 for p in problems: maps.setdefault(p.map_id,[]).append(p)
 if len(ids)!=512 or len(set(ids))!=512 or len(maps)!=32 or any(len(x)!=16 for x in maps.values()): raise core.IdentityError('validation ordered 512/32x16 panel mismatch')
 if sum(x[0].family=='IIIILLLL' for x in maps.values())!=8: raise core.IdentityError('validation requires eight challenge maps')
 return ids

def retained_metadata(root=ROOT):
 """Targeted, read-only manifest-bound COMPLETE analysis reader; never payload data."""
 root=Path(root); common=None; rows={}
 for seed in SEEDS:
  owner=root/f'replication-{seed}-analysis'; attempt=json.loads((owner/'attempt.json').read_text())
  if attempt.get('status')!='COMPLETE': raise core.IdentityError('analysis owner incomplete')
  _manifest_file(owner,'attempt.json'); _manifest_file(owner,'analysis.json'); a=json.loads((owner/'analysis.json').read_text())
  if a.get('status')!='COMPLETE' or a.get('seed')!=seed or a.get('source_hashes',{}).get('execution/seed_replication/analyze.py')!=ANALYSIS_SHA: raise core.IdentityError('analysis identity mismatch')
  ids=a.get('input_ids')
  if not isinstance(ids,dict) or common is not None and ids!=common: raise core.IdentityError('analysis input IDs disagree')
  common=ids; stored=a.get('stored_fullvalidation',{}).get('8000',{}).get('t1',{}); qc=a.get('quality_control',{}).get('grid',[])
  find=lambda t:next((x.get('raw')for x in qc if x.get('temperature')==t),None)
  raw={('sm',1.):stored.get('sm'),('sa',.75):find(.75),('sa',1.):stored.get('sa'),('sa',1.25):find(1.25)}
  for r in raw.values():
   if not isinstance(r,dict) or len(r.get('problems',[]))!=512 or any(len(p.get('attempts',[]))!=32 or not isinstance(a.get('route'),str)for p in r['problems']for a in p.get('attempts',[])): raise core.IdentityError('retained raw K32 hex-route endpoint mismatch')
  if not isinstance(a.get('pair'),dict): raise core.IdentityError('retained accepted pair binding absent')
  rows[seed]={'analysis_sha256':sha(owner/'analysis.json'),'raw':raw,'bindings':a.get('stored_fullvalidation',{}).get('8000',{}).get('event_bindings',{}),'greedy':a.get('stored_fullvalidation',{}).get('8000',{}).get('greedy')}
 return common,rows
def retained_event(root,seed,mode,ids,binding):
 owner=Path(root)/f"replication-{seed}-{'softmax'if mode=='sm'else'schrodinger'}-8000"; rh=_manifest_file(owner,'result.json'); result=json.loads((owner/'result.json').read_text())
 ev=next((x for x in result.get('result',{}).get('events',[])if x.get('update')==8000),None)
 if result.get('input_ids')!=ids or not isinstance(binding,dict) or ev is None or binding.get('event_sha256')!=_event_digest(ev) or binding.get('result_sha256')!=rh or binding.get('input_ids')!=ids: raise core.IdentityError('final event binding mismatch')
 return ev,rh
class CountingModel:
 def __init__(self,model): self.model=model; self.mode=model.mode; self.forward_calls=0; self.batch_states=0
 def __call__(self,x,**kw): self.forward_calls+=1; self.batch_states+=len(x); return self.model(x,**kw)
def _uniform_digest(problems,seed):
 h=hashlib.sha256()
 for p in problems:
  for k in range(32): h.update(np.asarray(rollout_uniforms(seed,1,p.map_id,p.start,p.goal,0,k),dtype=np.float64).tobytes())
 return h.hexdigest()
def _cell(seed,mode,temp,ids,checkpoint,result,**extra):
 s=result['strata']; persisted={k:v for k,v in result.items()if k!='cache'}
 return {'seed':seed,'mode':mode,'temperature':temp,'k':32,'splitcode':1,'replicate':0,'problem_ids':ids,'routine_Q':s['routine']['Q'],'challenge_Q':s['challenge']['Q'],'challenge_pass':s['challenge']['pass_at_k'],'raw':persisted,'checkpoint':checkpoint,**extra}
def produce_cells(root=ROOT,write_partial=None):
 """Actual D1 production seam: only 24 missing evaluator calls and 16 bound reuses."""
 ids,old=retained_metadata(root); validation=load_validation(); ordered=_panel(validation.problems); support=frozenset(load_training().support); cells=[]
 for seed in SEEDS:
  models={}
  for mode in ('sm','sa'):
   ev,_=retained_event(root,seed,mode,ids,old[seed]['bindings'].get(mode)); payload,checkpoint,identity=_checkpoint(Path(root),seed,'softmax'if mode=='sm'else'schrodinger',ids); models[mode]=(CountingModel(_model(payload)),checkpoint,identity,ev)
   for (m,temp),raw in old[seed]['raw'].items():
    if m==mode:
     if [(p['map_id'],p['family'])for p in raw['problems']]!=[(p.map_id,p.family)for p in validation.problems]: raise core.IdentityError('historical raw dataset order mismatch')
     cells.append(_cell(seed,mode,temp,ordered,checkpoint,raw,reused=True,event=_event_digest(ev),greedy=old[seed]['greedy'],uniform_digest=None,forward_calls=None,batch_states=None,generated_actions=None,cold_cache_seconds=None,incremental_cache_seconds=None))
     if write_partial: write_partial(cells)
  for mode in (('sm','sa')if seed in(1702,1704)else('sa','sm')):
   model,checkpoint,identity,ev=models[mode]; cache={}; missing=(.5,.75,1.25,1.5)if mode=='sm'else(.5,1.5); digest=_uniform_digest(validation.problems,seed)
   for n,temp in enumerate(missing):
    fc,bs=model.forward_calls,model.batch_states; started=time.perf_counter(); result=evaluate_rollouts(model,validation.problems,identity=checkpoint,seed=seed,splitcode=1,support=support,k=32,temperature=temp,replicate=0,cache=cache); elapsed=time.perf_counter()-started
    cells.append(_cell(seed,mode,temp,ordered,checkpoint,result,reused=False,event=_event_digest(ev),uniform_digest=digest,forward_calls=model.forward_calls-fc,batch_states=model.batch_states-bs,generated_actions=sum(len(a['route'])for p in result['problems']for a in p['attempts']),cold_cache_seconds=elapsed if n==0 else None,incremental_cache_seconds=elapsed if n else None))
    if write_partial: write_partial(cells)
 return validate_cells(cells)
def validate_cells(cells):
 keys=[(x.get('seed'),x.get('mode'),float(x.get('temperature')))for x in cells]
 if len(keys)!=40 or len(set(keys))!=40 or set(keys)!=set(grid()): raise core.IdentityError('D1 grid must be exact 40')
 ordered=None
 for x in cells:
  if x.get('k')!=32 or x.get('splitcode')!=1 or x.get('replicate')!=0: raise core.IdentityError('K/split/replicate mismatch')
  ids=x.get('problem_ids')
  if not isinstance(ids,list) or len(ids)!=512 or len({repr(v)for v in ids})!=512 or ordered is not None and ids!=ordered: raise core.IdentityError('problem ID ordering mismatch')
  ordered=ids
  if bool(x.get('reused')) != ((x['mode'],float(x['temperature']))in REUSED): raise core.IdentityError('reuse partition mismatch')
 return cells
def select(cells,seed):
 by={(x['mode'],float(x['temperature'])):x for x in cells if x['seed']==seed}; ref=by.get(('sm',1.))
 if ref is None: raise core.IdentityError('missing SM T1')
 out={'sm':ref}
 for mode in('sm','sa'):
  c=[x for(m,_),x in by.items()if m==mode and x['routine_Q']>=ref['routine_Q']-.02 and x['challenge_Q']>=ref['challenge_Q']-.02]
  if not c:
   if mode=='sa':out['control_no_go']=True;continue
   raise core.IdentityError('SM T1 failed floor')
  p=max(x['challenge_pass']for x in c); c=[x for x in c if p-x['challenge_pass']<=1e-12]; q=max(x['challenge_Q']for x in c); out[mode]=min((x for x in c if q-x['challenge_Q']<=1e-12),key=lambda x:x['temperature'])
 return out
def uncertainty(seed_deltas,maps_by_seed):
 x=np.asarray(seed_deltas,float); maps=np.asarray(maps_by_seed,float)
 if x.shape!=(4,)or maps.shape!=(4,8): raise core.IdentityError('requires four seeds/eight shared challenge maps')
 sd=float(x.std(ddof=1)); half=3.182446*sd/2; rng=np.random.Generator(np.random.PCG64(91703)); samples=np.asarray([maps[:,rng.integers(0,8,8)].mean(axis=1).mean()for _ in range(2000)]); lo,hi=np.quantile(samples,[.025,.975],method='linear'); width=float(hi-lo)
 return {'mean':float(x.mean()),'sample_sd':sd,'seed_half_width':half,'seed_full_width':2*half,'map_interval':[float(lo),float(hi)],'map_full_width':width,'approx_32_map_width':width*math.sqrt(8/32),'selection_fixed':True,'map_assumptions':'iid/exchangeable maps only'}
def forecast(costs):
 missing=[k for k in COSTS if costs.get(k)is None]
 if missing:return {'status':'UNSUPPORTED_NO_GO','missing_essential_costs':missing}
 raw=sum(float(costs[k])for k in COSTS); scaled=1.5*raw
 return {'status':'GO'if scaled<=420 else'NO_GO','raw_seconds':raw,'scaled_seconds':scaled,'factor':1.5,'d2_endpoints':8,'d2_problems_per_endpoint':2048,'d2_routine_problems':1536,'d2_challenge_problems':512,'cold_cache_required':True}
def forecast_costs(cells):
 """Retain raw D1 evidence without misrepresenting it as a D2 prediction."""
 observed={'cold':[],'incremental':[],'sampling':[],'verification':[],'bank':[]}
 for cell in cells:
  if cell.get('cold_cache_seconds') is not None: observed['cold'].append(cell['cold_cache_seconds'])
  if cell.get('incremental_cache_seconds') is not None: observed['incremental'].append(cell['incremental_cache_seconds'])
  timing=cell.get('raw',{}).get('timing',{})
  for out,key in (('sampling','categorical_rollout_seconds'),('verification','verifier_uniqueness_seconds')):
   if isinstance(timing.get(key),(int,float)): observed[out].append(timing[key])
  greedy=cell.get('greedy',{})
  proper=cell.get('proper',{})
  for source in (greedy,proper):
   timing=source.get('timing',{}) if isinstance(source,dict) else {}
   if isinstance(timing.get('proper_seconds'),(int,float)): observed['bank'].append(timing['proper_seconds'])
 # These observations are 512-problem D1 routes (often warm cache) and overlap
 # endpoint wall time.  They cannot safely be summed/scaled into an 8x2048 D2
 # forecast without a cold setup, proper-bank, loading, and finalization bound.
 return {key:None for key in COSTS}|{'observed_d1_timing_seconds':observed,
   'unsupported_reason':'D1 timing components are overlapping 512-problem evidence; essential D2 cold/setup/loading/finalization bounds are unavailable.'}
def compose(cells,costs,maps_by_seed):
 validate_cells(cells); selected={str(s):select(cells,s)for s in SEEDS}; complete=not any(x.get('control_no_go')for x in selected.values()); deltas=[selected[str(s)]['sa']['challenge_pass']-selected[str(s)]['sm']['challenge_pass']for s in SEEDS]if complete else None
 return {'status':'COMPLETE'if complete else'CONTROL_NO_GO','cells':cells,'selected':selected,'forecast':forecast(costs),'uncertainty':uncertainty(deltas,maps_by_seed)if deltas else None,'route_order_limitation':'Producer/event/dataset order binds historical routes; all-invalid permutations remain indistinguishable.'}
def selected_map_contrasts(cells,selected):
 """Eight matched challenge maps, equal-map contrasts, with temperatures fixed by selection."""
 rows=[]
 for seed in SEEDS:
  sm=selected[str(seed)]['sm']['raw'].get('maps',{}); sa=selected[str(seed)]['sa']['raw'].get('maps',{})
  def index(value):
   values=value.values() if isinstance(value,dict)else value
   return {x['map_id']:x['metrics']['pass_at_k']for x in values if x.get('family')=='IIIILLLL'}
  left,right=index(sm),index(sa)
  if set(left)!=set(right)or len(left)!=8: raise core.IdentityError('selected challenge map binding mismatch')
  rows.append([right[m]-left[m]for m in sorted(left)])
 return rows
def run(root=ROOT,*,cells=None,costs=None,maps_by_seed=None,reviewed=False):
 """Owned production/injected seam; reviewed=True is required for checkpoint inference."""
 root=Path(root)
 if cells is None and not reviewed: raise PermissionError('exact-version review is required before D1 production')
 if core.STAGES!=OLD_STAGES: raise core.BudgetError('unexpected prior stage table')
 core.STAGES.clear();core.STAGES.update(STAGES)
 with core.OwnedAttempt.begin(root,root/'ledger.jsonl','D','difficult-d1-001')as attempt:
  cap=min(296.,core.deadline_seconds(root/'ledger.jsonl','D'));signal.setitimer(signal.ITIMER_REAL,cap)
  generated=cells is None
  if generated:
   cells=produce_cells(root,write_partial=lambda partial:core._write_json(attempt.output/'partial-cells.json',{'status':'PARTIAL','cells':partial}))
  selected={str(s):select(cells,s)for s in SEEDS}
  actual_maps=selected_map_contrasts(cells,selected) if generated and not any(x.get('control_no_go')for x in selected.values()) else maps_by_seed
  if actual_maps is None and not any(x.get('control_no_go')for x in selected.values()): raise core.IdentityError('selected-map contrasts required')
  extracted=forecast_costs(cells) if costs is None else costs
  out=compose(cells,extracted,actual_maps if actual_maps is not None else np.zeros((4,8)))
  out['forecast']['observed_d1_timing_evidence']=extracted.get('observed_d1_timing_seconds',{})
  out['forecast']['unsupported_reason']=extracted.get('unsupported_reason') if out['forecast']['status']=='UNSUPPORTED_NO_GO' else None
  out.update({'scope':{'test_access':False,'training':False},'provenance':{'plan':PLAN_SHA,'spec':SPEC_SHA,'analysis':ANALYSIS_SHA,'code':sha(Path(__file__)),'argv':list(sys.argv),'stage_table':STAGES,'max_seconds':300.,'timer_cap_seconds':cap}});core._write_json(attempt.output/'d1.json',out)
 return out
def main(argv=None):
 p=argparse.ArgumentParser();p.add_argument('--reviewed-production',action='store_true');p.parse_args(argv);run(reviewed=p.parse_args(argv).reviewed_production)
if __name__=='__main__':main()
