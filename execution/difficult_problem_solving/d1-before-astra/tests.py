"""Bounded literal D1 repair tests; no checkpoint or retained artifact is used."""
import importlib.util, json, sys
from pathlib import Path
import numpy as np, pytest, torch
ROOT=Path(__file__).parents[1];sys.path.insert(0,str(ROOT));spec=importlib.util.spec_from_file_location('d1',ROOT/'execution/difficult_problem_solving/d1.py');d1=importlib.util.module_from_spec(spec);spec.loader.exec_module(d1)
class P:
 def __init__(self,i,f='IIIIIIII'):self.canonical=i.to_bytes(32,'little');self.map_id=i//16;self.family=f;self.start=0;self.goal=1
def panel():return tuple(P(i,'IIIILLLL'if i//16<8 else'IIIIIIII'if i//16<20 else'LLLLLLLL')for i in range(512))
def ids():return d1.ids_of(panel())
def result(temp=.8):
 attempts=[{'route':'00','valid':True}for _ in range(32)]
 return {'strata':{'routine':{'Q':.8,'pass_at_k':temp},'challenge':{'Q':.8,'pass_at_k':temp}},'problems':[{'map_id':i//16,'family':'IIIILLLL'if i//16<8 else'IIIIIIII','attempts':attempts}for i in range(512)],'maps':[]}
def cell(s,m,t):return d1._cell(s,m,t,ids(),'checkpoint-'+m,result(t),reused=(m,t)in d1.REUSED,uniform_digest='u',support_digest='s',training_identity='training',greedy={'route_order_corrobated':True})
def cells():return [cell(*x)for x in d1.grid()]
def test_production_panel_validator_has_exact_families():
 assert len(d1._panel(panel()))==512
 bad=list(panel());bad[16*20]=P(16*20,'IIIIIIII')
 with pytest.raises(d1.core.IdentityError):d1._panel(tuple(bad))
def test_actual_evaluator_counter_and_common_uniform_warm_cache():
 """Literal one-state accepted-evaluator smoke; no evaluator/counter monkeypatch."""
 from schrodinger.route_policy_data import ACTIONS, Problem
 east=ACTIONS.index((0,1))
 problem=Problem(bytes(144),17,'IIIIIIII',0,1,1,1,None)
 class EastOnly:
  mode='softmax'
  def __call__(self,states,**kwargs):
   logits=torch.full((len(states),4),float('-inf'))
   logits[:,east]=0.
   return logits
 counted=d1.CountingModel(EastOnly())
 first=d1.evaluate_rollouts(counted,(problem,),identity='literal-smoke',seed=1702,splitcode=1,replicate=0,k=32,temperature=1.,support=frozenset(),cache={})
 attempts=first['problems'][0]['attempts']
 assert counted.forward_calls==1
 assert counted.batch_states==1
 assert len(attempts)==32
 assert [row['route']for row in attempts]==[bytes([east])]*32
 assert all(row['valid']for row in attempts)
 assert sum(len(row['route'])for row in attempts)==32
 assert first['strata']['routine']['Q']==1.
 assert first['strata']['routine']['U_valid']==1/32
 calls,states=counted.forward_calls,counted.batch_states
 warm=d1.evaluate_rollouts(counted,(problem,),identity='literal-smoke',seed=1702,splitcode=1,replicate=0,k=32,temperature=1.,support=frozenset(),cache=first['cache'])
 half=d1.evaluate_rollouts(counted,(problem,),identity='literal-smoke',seed=1702,splitcode=1,replicate=0,k=32,temperature=.5,support=frozenset(),cache=first['cache'])
 assert counted.forward_calls-calls==0
 assert counted.batch_states-states==0
 assert [row['route']for row in warm['problems'][0]['attempts']]==[bytes([east])]*32
 assert [row['route']for row in half['problems'][0]['attempts']]==[bytes([east])]*32
 same=d1._uniform_digest((problem,),1702)
 assert same==d1._uniform_digest((problem,),1702)
 assert same!=d1._uniform_digest((problem,),1703)
def test_real_producer_dispatches_40_cells_once_under_sink(tmp_path,monkeypatch):
 """Real producer/sink dispatch with a prevalidated ten-Problem internal panel."""
 from schrodinger.route_policy_data import Problem
 problems=tuple(Problem(bytes(144),i,'IIIILLLL'if i<8 else'IIIIIIII'if i==8 else'LLLLLLLL',0,1,1,1,None)for i in range(10))
 east=1; attempts=[{'route':'01','valid':True}for _ in range(32)]
 maps={i:{'map_id':i,'family':p.family,'metrics':{'Q':1.,'U_valid':1/32,'pass_at_k':1.}}for i,p in enumerate(problems)}
 raw={'strata':{'routine':{'Q':1.,'pass_at_k':1.},'challenge':{'Q':1.,'pass_at_k':1.}},'problems':[{'map_id':p.map_id,'family':p.family,'attempts':attempts}for p in problems],'maps':maps}
 def event_for(seed,mode):
  event={'routes':{'greedy':{'problems':[{'map_id':p.map_id,'family':p.family,'attempts':[{'route':'01','valid':True}]}for p in problems]}}}
  event['_binding']={'event_sha256':d1._event_digest(event)}
  return event
 metadata=lambda root:({'x':'y'},{s:{'bindings':{'sm':{},'sa':{}},'pair':{'checkpoint_hashes':{'sm':'checkpoint-sm','sa':'checkpoint-sa'},'checkpoint_identity':{'sm':{'seed':s,'mode':'softmax','input_ids':{'x':'y'}},'sa':{'seed':s,'mode':'schrodinger','input_ids':{'x':'y'}}},'initial_checkpoint_hashes':{'sm':'i-sm','sa':'i-sa'},'owner_authority':{'sm':{},'sa':{}},'shared_initial_digest':'shared','batch_prefix':{}},'raw':{('sm',1.):raw,('sa',.75):raw,('sa',1.):raw,('sa',1.25):raw}}for s in d1.SEEDS})
 Training=type('Training',(),{'support':frozenset({b'x'}),'support_hash':d1._support_digest(frozenset({b'x'})),'identity':'training-fixture'})
 Validation=type('Validation',(),{'problems':problems})
 class Fake:
  def __init__(self,mode):self.mode=mode
  def __call__(self,x,**kw):return torch.tensor([[-20.,20.,-20.,-20.]]).repeat(len(x),1)
 calls=[]; caches=[]
 def event(root,seed,mode,ids,binding):return event_for(seed,mode),'fixture'
 def evaluator(model,items,**kw):
  calls.append((kw['seed'],model.mode,kw['identity'],kw['temperature'],kw['k'],kw['splitcode'],kw['replicate'],kw['support'],tuple(d1.ids_of(items)))); caches.append(kw['cache'])
  return d1.evaluate_rollouts(model,items,**kw)
 def pair(r,s,i):
  identity={'seed':s,'mode':'softmax','input_ids':i};sa_identity={**identity,'mode':'schrodinger'}
  return {'checkpoint_hashes':{'sm':'checkpoint-sm','sa':'checkpoint-sa'},'checkpoint_identity':{'sm':identity,'sa':sa_identity},'initial_checkpoint_hashes':{'sm':'i-sm','sa':'i-sa'},'owner_authority':{'sm':{},'sa':{}},'shared_initial_digest':'shared','batch_prefix':{},'sm_payload':{'mode':'softmax'},'sa_payload':{'mode':'schrodinger'}}
 def tiny_validate(rows):
  assert len(rows)==40 and len({(x['seed'],x['mode'],x['temperature'])for x in rows})==40 and sum(x['reused']for x in rows)==16
  expected=tuple(d1.ids_of(problems))
  assert all(tuple(tuple(row)for row in x['problem_ids'])==expected for x in rows);return rows
 deps={'metadata':metadata,'validation':lambda:Validation(),'training':lambda:Training(),'pair':pair,'event':event,'model':lambda p:Fake(p['mode']),'evaluator':evaluator,'panel':lambda p:d1.ids_of(problems),'expected_problem_count':10}
 root=tmp_path/'owned';root.mkdir();d1.core.initialize_ledger(root/'ledger.jsonl');d1.core.STAGES.clear();d1.core.STAGES.update(d1.PRISTINE_STAGES)
 monkeypatch.setattr(d1,'validate_cells',tiny_validate);monkeypatch.setattr(d1,'require_production_decision',lambda *a:{'fixture':True});monkeypatch.setattr(d1.core,'configure_runtime',lambda:None)
 writes=[];real_write=d1._atomic_json
 def record_write(path,value):
  writes.append(Path(path));return real_write(path,value)
 monkeypatch.setattr(d1,'_atomic_json',record_write)
 out=d1.run(root,production_decision='fixture',deps=deps)
 output=root/'difficult-d1-repair-001';index=json.loads((output/'cell-index.json').read_text())
 assert out['status']=='COMPLETE' and len(index['cells'])==40 and len({x['cell_id']for x in index['cells']})==40
 assert len(list((output/'cells').glob('*.json')))==40 and len(list((output/'greedy').glob('*.json')))==8 and not (output/'partial-cells.json').exists()
 assert len([path for path in writes if path.parent.name=='cells'])==40
 expected=[]
 for seed,order in ((1702,('sm','sa')),(1703,('sa','sm')),(1704,('sm','sa')),(1705,('sa','sm'))):
  for mode in order:
   for temperature in ((.5,.75,1.25,1.5)if mode=='sm'else(.5,1.5)):
    expected.append((seed,'softmax'if mode=='sm'else'schrodinger','checkpoint-'+mode,temperature,32,1,0,frozenset({b'x'}),tuple(d1.ids_of(problems))))
 assert calls==expected
 assert len({id(x)for x in caches})==8
 with pytest.raises(d1.core.IdentityError):d1.load_indexed_cells(output)
 assert len(d1.load_indexed_cells(output,expected_problem_count=10))==40
def test_binding_selection_floors_ties_and_missing_duplicate():
 x=cells();assert d1.select(x,1702)['sm']['temperature']==1.
 for z in x:
  if z['seed']==1702 and z['mode']=='sa':z['routine_Q']=.7
 assert d1.select(x,1702)['control_no_go']
 x=cells();x[0]['problem_ids']=list(reversed(x[0]['problem_ids']))
 with pytest.raises(d1.core.IdentityError):d1.validate_cells(x)
 x=cells();x[-1]=x[-2]
 with pytest.raises(d1.core.IdentityError):d1.validate_cells(x)
def test_owner_math_stage_table_and_partial_grid_rejected(tmp_path):
 assert d1.STAGES=={'A':1000.,'B':3500.,'C':0.,'D':1400.}
 u=d1.uncertainty([1,2,3,4],np.arange(32).reshape(4,8));assert u['seed_full_width']==2*u['seed_half_width']and u['approx_32_map_width']==u['map_full_width']*.5
 d1._atomic_json(tmp_path/'cell-index.json',{'status':'PARTIAL','cells':[]})
 with pytest.raises(d1.core.IdentityError):d1.load_indexed_cells(tmp_path)
