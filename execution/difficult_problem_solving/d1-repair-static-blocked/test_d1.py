"""Minimal D1 literal tests.  They are intentionally not executed in static review."""
import importlib.util,sys
from pathlib import Path
import numpy as np,pytest
ROOT=Path(__file__).parents[1];sys.path.insert(0,str(ROOT));S=importlib.util.spec_from_file_location('d1',ROOT/'execution/difficult_problem_solving/d1.py');d1=importlib.util.module_from_spec(S);S.loader.exec_module(d1)
def ids(n=512):return [(str(i),i//16,'IIIILLLL'if i//16<8 else'IIIIIIII',i,i+1)for i in range(n)]
def cell(s,m,t,n=512):return {'seed':s,'mode':m,'temperature':t,'k':32,'splitcode':1,'replicate':0,'problem_ids':ids(n),'routine_Q':.8,'challenge_Q':.8,'challenge_pass':t,'reused':(m,t)in d1.REUSED,'raw':{'maps':{}},'checkpoint':'x'}
def cells():return [cell(*x)for x in d1.grid()]
def test_evaluator_counting_common_rng_and_warm_cache():
 # Accepted evaluator is exercised with a deterministic callable/model in the bounded smoke.
 assert d1.CountingModel and d1._uniform_digest and len(d1.required_new())==24
def test_owned_orchestration_16_24_40_and_endpoint_index(tmp_path,monkeypatch):
 x=cells();d1.validate_cells(x);p=d1.persist_cells(tmp_path,x);assert len(p)==40 and len(list((tmp_path/'cells').glob('*.json')))==40
 assert sum(z['reused']for z in x)==16 and len(d1.required_new())==24
def test_binding_order_floors_and_ties():
 x=cells();assert d1.select(x,1702)['sm']['temperature']==1
 x[0]['problem_ids']=list(reversed(x[0]['problem_ids']))
 with pytest.raises(d1.core.IdentityError):d1.validate_cells(x)
 y=cells()
 for z in y:
  if z['seed']==1702 and z['mode']=='sa':z['routine_Q']=.7
 assert d1.select(y,1702)['control_no_go']
def test_owner_failures_stage_cap_and_uncertainty():
 assert d1.STAGES=={'A':700.,'B':3500.,'C':300.,'D':1400.}
 u=d1.uncertainty([1,2,3,4],np.arange(32).reshape(4,8));assert u['seed_full_width']==2*u['seed_half_width'] and u['approx_32_map_width']==u['map_full_width']*.5
