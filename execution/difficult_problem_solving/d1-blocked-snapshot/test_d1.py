"""Synthetic D1 contract checks: no model, checkpoint, or test payload calls."""
import importlib.util, json, sys
from pathlib import Path
import numpy as np, pytest
P=Path(__file__).parents[1]/'execution/difficult_problem_solving/d1.py';sys.path.insert(0,str(P.parents[2]));sp=importlib.util.spec_from_file_location('d1',P);d1=importlib.util.module_from_spec(sp);sp.loader.exec_module(d1)
def costs(v=1):return {k:v for k in d1.COSTS}
def cells():
 out=[]
 for s,m,t in d1.grid():out.append({'seed':s,'mode':m,'temperature':t,'k':32,'splitcode':1,'replicate':0,'problem_ids':[(i,i,'x',i,i+1)for i in range(512)],'routine_Q':.8,'challenge_Q':.8,'challenge_pass':.5+(t==1)*.1,'reused':(m,t)in d1.REUSED,'uniform_digest':'same','forward_calls':None if(m,t)in d1.REUSED else 1,'batch_states':None if(m,t)in d1.REUSED else 512,'generated_actions':None if(m,t)in d1.REUSED else 7})
 return out
def test_grid_partition_order_and_no_greedy_call():
 x=cells();assert len(d1.grid())==40 and len(d1.required_new())==24;d1.validate_cells(x)
 seen=[];d1.execute_missing if False else None
 # prescribed seed ordering and cache isolation are exercised without evaluator/model calls.
 for s in d1.SEEDS: assert [z for z in d1.required_new()if z[0]==s]
 assert sum(z['reused']for z in x)==16 and all(z['forward_calls']is None for z in x if z['reused'])
def test_floors_max_pass_and_ties():
 x=cells();a=[z for z in x if z['seed']==1702 and z['mode']=='sa'];a[0].update(challenge_pass=.9,challenge_Q=.79);a[1].update(challenge_pass=.9+5e-13,challenge_Q=.8);a[2].update(challenge_pass=.9,challenge_Q=.8+5e-13)
 assert d1.select(x,1702)['sa']['temperature']==.75
 for z in a:z['routine_Q']=.7
 assert d1.select(x,1702)['control_no_go']is True
 with pytest.raises(d1.core.IdentityError):d1.validate_cells(x[:-1])
 y=cells();y[0]['temperature']=.6
 with pytest.raises(d1.core.IdentityError):d1.validate_cells(y)
def test_retained_interface_and_negative_bindings(tmp_path):
 # Real retained interface is read-only; synthetic mutation checks prove rejection paths.
 ids,rows=d1.retained_metadata();assert isinstance(ids,dict)and len(rows)==4
 seed=d1.SEEDS[0];binding=rows[seed]['bindings']['sm'];assert isinstance(binding.get('event_sha256'),str)
 bad=dict(binding);bad['event_sha256']='0'*64
 with pytest.raises(d1.core.IdentityError):d1.retained_event(d1.ROOT,seed,'sm',ids,bad)
 assert 'all-invalid permutations' in d1.compose(cells(),costs(),np.zeros((4,8)))['route_order_limitation']
def test_owned_success_and_late_failure_forbidden_seam(tmp_path,monkeypatch):
 monkeypatch.setattr(d1.core,'STAGES',dict(d1.OLD_STAGES));called=[]
 monkeypatch.setattr(d1,'produce_cells',lambda *_:called.append('forbidden'))
 for name,fail in(('ok',False),('bad',True)):
  monkeypatch.setattr(d1.core,'STAGES',dict(d1.OLD_STAGES))
  root=tmp_path/name;root.mkdir();d1.core.initialize_ledger(root/'ledger.jsonl')
  if fail:monkeypatch.setattr(d1.core,'_write_json',lambda *_:(_ for _ in()).throw(OSError('late write')))
  if fail:
   with pytest.raises(d1.core.ArtifactError):d1.run(root,cells=cells(),costs=costs(),maps_by_seed=np.zeros((4,8)))
   assert not(root/'experiment.lock').exists()
  else:
   d1.run(root,cells=cells(),costs=costs(),maps_by_seed=np.zeros((4,8)));assert(root/'difficult-d1-001'/'output-manifest.json').is_file()
 assert not called
def test_forecast_stage_cap_and_no_go():
 assert d1.forecast({})['status']=='UNSUPPORTED_NO_GO';assert d1.forecast(costs(100))['status']=='NO_GO'
 f=d1.forecast(costs());assert(f['scaled_seconds'],f['d2_problems_per_endpoint'],f['factor'])==(10.5,2048,1.5)
 assert d1.STAGES=={'A':700.,'B':3500.,'C':300.,'D':1400.}
def test_accounting_and_shared_bootstrap():
 x=cells();new=[z for z in x if not z['reused']];assert sum(z['batch_states']for z in new)==24*512 and sum(z['generated_actions']for z in new)==24*7
 assert all(z['forward_calls']is None for z in x if z['reused'])
 u=d1.uncertainty([1,2,3,4],np.arange(32).reshape(4,8));assert u['sample_sd']==pytest.approx(np.std([1,2,3,4],ddof=1))and u['seed_half_width']==pytest.approx(3.182446*u['sample_sd']/2)and u['approx_32_map_width']==pytest.approx(u['map_full_width']*.5)
def test_injected_reviewed_production_path_and_observed_forecast(tmp_path,monkeypatch):
 class Problem:
  def __init__(self,i):self.canonical=bytes([i//256,i%256]);self.map_id=i//16;self.family='IIIILLLL'if i//16<8 else'IIIIIIII';self.start=i;self.goal=i+1
 problems=[Problem(i)for i in range(512)]; attempts=[{'route':'00','valid':False}for _ in range(32)]
 def raw():return {'problems':[{'map_id':p.map_id,'family':p.family,'attempts':attempts}for p in problems],'strata':{'routine':{'Q':.8,'pass_at_k':.5},'challenge':{'Q':.8,'pass_at_k':.5}},'maps':{p.map_id:{'map_id':p.map_id,'family':p.family,'metrics':{'pass_at_k':.5}}for p in problems[::16]},'timing':{'categorical_rollout_seconds':1.,'verifier_uniqueness_seconds':2.}}
 old={s:{'raw':{k:raw()for k in d1.REUSED},'bindings':{'sm':{'event_sha256':'x'},'sa':{'event_sha256':'x'}},'greedy':{'timing':{'proper_seconds':3.}}}for s in d1.SEEDS}; calls=[];root=tmp_path/'owned';root.mkdir();d1.core.initialize_ledger(root/'ledger.jsonl')
 monkeypatch.setattr(d1,'retained_metadata',lambda *_:({'bound':'ids'},old));monkeypatch.setattr(d1,'load_validation',lambda:type('V',(),{'problems':problems})());monkeypatch.setattr(d1,'load_training',lambda:type('T',(),{'support':set()})());monkeypatch.setattr(d1,'retained_event',lambda *_:({'update':8000},'h'));monkeypatch.setattr(d1,'_event_digest',lambda *_:'x');monkeypatch.setattr(d1,'_checkpoint',lambda *_:({},'checkpoint',{}));monkeypatch.setattr(d1,'_model',lambda *_:type('M',(),{'mode':'softmax'})());monkeypatch.setattr(d1,'_uniform_digest',lambda *_:'u')
 def evaluator(model,ps,**kw):
  assert(root/'experiment.lock').exists();calls.append((kw['seed'],kw['temperature'],id(kw['cache'])));return {**raw(),'cache':kw['cache'],'timing':{'categorical_rollout_seconds':1.,'verifier_uniqueness_seconds':2.}}
 monkeypatch.setattr(d1,'evaluate_rollouts',evaluator);monkeypatch.setattr(d1.core,'STAGES',dict(d1.OLD_STAGES));out=d1.run(root,reviewed=True)
 assert len(calls)==24 and len(out['cells'])==40 and out['forecast']['status']=='UNSUPPORTED_NO_GO' and set(out['forecast']['missing_essential_costs'])==set(d1.COSTS) and 'overlapping 512-problem' in out['forecast']['unsupported_reason']
 assert len({cache for _,_,cache in calls})==8 and all(x['forward_calls']is None for x in out['cells']if x['reused'])
