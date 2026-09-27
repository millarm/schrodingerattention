"""Bounded literal D1 repair tests; no checkpoint or retained artifact is used."""
import copy, importlib.util, json, sys
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
def cell(s,m,t):return d1._cell(s,m,t,ids(),'checkpoint-'+m,result(.8),reused=(m,t)in d1.REUSED,uniform_digest='u',support_digest='s',training_identity={'support_hash':'s'},greedy={'route_order_corrobated':True})
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
def owned_fixture(tmp_path,monkeypatch):
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
 metadata=lambda root:({'x':'y'},{s:{'analysis_sha256':'fixture-analysis','bindings':{'sm':{},'sa':{}},'pair':{'checkpoint_hashes':{'sm':'checkpoint-sm','sa':'checkpoint-sa'},'checkpoint_identity':{'sm':{'seed':s,'mode':'softmax','input_ids':{'x':'y'}},'sa':{'seed':s,'mode':'schrodinger','input_ids':{'x':'y'}}},'initial_checkpoint_hashes':{'sm':'i-sm','sa':'i-sa'},'owner_authority':{'sm':{},'sa':{}},'shared_initial_digest':'shared','batch_prefix':{}},'raw':{('sm',1.):raw,('sa',.75):raw,('sa',1.):raw,('sa',1.25):raw}}for s in d1.SEEDS})
 Training=type('Training',(),{'support':frozenset({b'x'}),'support_hash':d1._support_digest(frozenset({b'x'})),'identity':'training-fixture'})
 Validation=type('Validation',(),{'problems':problems})
 class Fake:
  def __init__(self,mode):self.mode=mode
  def __call__(self,x,**kw):return torch.tensor([[-20.,20.,-20.,-20.]]).repeat(len(x),1)
 calls=[]; caches=[]
 def event(root,seed,mode,ids,binding):return event_for(seed,mode),'fixture'
 def evaluator(model,items,**kw):
  assert (root/'experiment.lock').exists()
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
 for key in ('metadata','validation','training','pair','event','model'):
  original=deps[key]
  def locked(*a,_fn=original,**kw):
   assert (root/'experiment.lock').exists()
   return _fn(*a,**kw)
  deps[key]=locked
 def forbidden(*a,**kw):pytest.fail('forbidden prepared/test/training path')
 import schrodinger.route_policy_data as data
 import execution.paired_behavior.job as job
 monkeypatch.setattr(d1.core,'_prepared_ids',forbidden);monkeypatch.setattr(job,'_prepared_ids',forbidden)
 monkeypatch.setattr(data,'load_final_test',forbidden);monkeypatch.setattr(d1.core,'scheduled_training',forbidden)
 writes=[];real_write=d1._atomic_json
 def record_write(path,value):
  writes.append(Path(path));return real_write(path,value)
 monkeypatch.setattr(d1,'_atomic_json',record_write)
 return root,deps,problems,calls,caches,writes

def test_real_producer_dispatches_40_cells_once_under_sink(tmp_path,monkeypatch):
 root,deps,problems,calls,caches,writes=owned_fixture(tmp_path,monkeypatch)
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
 retained=d1.load_indexed_cells(output,expected_problem_count=10)
 assert all(x['forward_calls'] is None and x['batch_states'] is None for x in retained if x['reused'])
 assert all(x['generated_actions']==320 for x in retained if not x['reused'])
 assert all(x['raw']['problems'][0]['attempts'][0]['route']=='01' for x in retained)
 assert all('raw'not in x for v in out['selected'].values()for x in v.values()if isinstance(x,dict))
 assert len(json.loads((output/'cell-index.json').read_text())['bindings'])==4

def test_actual_owner_endpoint_write_failure_is_charged_and_releases_lock(tmp_path,monkeypatch):
 root,deps,_,_,_,_=owned_fixture(tmp_path,monkeypatch)
 real=d1._atomic_json
 def fail_second_endpoint(path,value):
  if Path(path).parent.name=='cells' and Path(path).name=='1702-sa-0.75.json':
   raise OSError('literal endpoint write failure')
  return real(path,value)
 monkeypatch.setattr(d1,'_atomic_json',fail_second_endpoint)
 with pytest.raises(OSError,match='literal endpoint write failure'):
  d1.run(root,production_decision='fixture',deps=deps)
 output=root/'difficult-d1-repair-001'
 attempt=json.loads((output/'attempt.json').read_text())
 rows=[json.loads(x)for x in (root/'ledger.jsonl').read_text().splitlines()]
 charges=[x for x in rows if x.get('stage')=='D']
 assert attempt['status']=='FAILED' and len(charges)==1
 assert charges[0]['entry_id']==attempt['entry_id'] and charges[0]['charged_seconds']>0
 assert not (root/'experiment.lock').exists()
 assert (output/'cells/1702-sm-1.json').is_file()
 assert not (output/'cells/1702-sa-0.75.json').exists()
 assert json.loads((output/'cell-index.json').read_text())['status']=='PARTIAL'
 assert not (output/'d1.json').exists()

def test_actual_owner_final_manifest_failure_is_not_success_or_double_charge(tmp_path,monkeypatch):
 root,deps,_,_,_,_=owned_fixture(tmp_path,monkeypatch)
 real=d1.core._write_json
 def fail_manifest(path,value):
  if Path(path).name=='output-manifest.json':raise OSError('literal final manifest failure')
  return real(path,value)
 monkeypatch.setattr(d1.core,'_write_json',fail_manifest)
 with pytest.raises(d1.core.ArtifactError,match='literal final manifest failure'):
  d1.run(root,production_decision='fixture',deps=deps)
 output=root/'difficult-d1-repair-001'
 attempt=json.loads((output/'attempt.json').read_text())
 rows=[json.loads(x)for x in (root/'ledger.jsonl').read_text().splitlines()]
 charges=[x for x in rows if x.get('stage')=='D']
 assert attempt['status']=='FAILED_ARTIFACT' and len(charges)==1
 assert charges[0]['entry_id']==attempt['entry_id'] and charges[0]['charged_seconds']>0
 assert not (root/'experiment.lock').exists()
 assert (output/'d1.json').exists() and not (output/'output-manifest.json').exists()
 assert (output/'finalization_error.json').exists()
 before=(root/'ledger.jsonl').read_bytes()
 answer=d1.watchdog.reconcile_production(rows,root/'ledger.jsonl',output,'outer',1.,tmp_path/'record')
 assert answer['status']=='OWNED_CHARGED_ARTIFACT_FAILURE' and not answer['success']
 assert (root/'ledger.jsonl').read_bytes()==before
def test_binding_selection_floors_ties_and_missing_duplicate():
 x=cells();assert d1.select(x,1702)['sm']['temperature']==.5
 for z in x:
  if z['seed']==1702 and z['mode']=='sa':z['routine_Q']=.7
 assert d1.select(x,1702)['control_no_go']
 x=cells();x[0]['problem_ids']=list(reversed(x[0]['problem_ids']))
 with pytest.raises(d1.core.IdentityError):d1.validate_cells(x)
 with pytest.raises(d1.core.IdentityError):d1.validate_cells(cells()[:-1])
 for floor in ('routine_Q','challenge_Q'):
  x=cells()
  for z in x:
   if z['mode']=='sa':z[floor]=.779
  assert d1.select(x,1702)['control_no_go']
 x=cells();a=next(z for z in x if(z['seed'],z['mode'],z['temperature'])==(1702,'sa',1.5))
 a['challenge_pass']=.9;a['challenge_Q']=.79
 assert d1.select(x,1702)['sa']['temperature']==1.5
 b=next(z for z in x if(z['seed'],z['mode'],z['temperature'])==(1702,'sa',.75))
 b['challenge_pass']=.9-5e-13;b['challenge_Q']=.8
 assert d1.select(x,1702)['sa']['temperature']==.75
 a['challenge_Q']=.8+5e-13
 assert d1.select(x,1702)['sa']['temperature']==.75

@pytest.mark.parametrize('key',['checkpoint_hashes','checkpoint_identity','initial_checkpoint_hashes','owner_authority','shared_initial_digest','batch_prefix'])
def test_owned_pair_binding_mutation_stops_before_evaluator(tmp_path,monkeypatch,key):
 root,deps,_,calls,_,_=owned_fixture(tmp_path,monkeypatch)
 original=deps['pair']
 def mutated(*a,**kw):
  pair=copy.deepcopy(original(*a,**kw))
  if key=='checkpoint_identity':pair[key]['sm']['config']={'wrong':True}
  else:pair[key]='mutated'
  return pair
 deps['pair']=mutated
 with pytest.raises(d1.core.IdentityError,match='binding mismatch'):d1.run(root,production_decision='fixture',deps=deps)
 assert calls==[] and not(root/'experiment.lock').exists()

def test_metadata_actual_owner_interface_and_mutation_negatives(tmp_path,monkeypatch):
 real=d1.ROOT/'replication-1702-analysis'
 assert json.loads((real/'attempt.json').read_text())['status']=='COMPLETE'
 assert d1._manifest_file(real,'attempt.json')==d1.sha(real/'attempt.json')
 monkeypatch.setattr(d1,'SEEDS',(1702,))
 owner=tmp_path/'replication-1702-analysis';owner.mkdir()
 raw=result();record={'status':'COMPLETE','seed':1702,'input_ids':{'fixture':'ids'},'source_hashes':{'execution/seed_replication/analyze.py':d1.ANALYSIS_SHA},'pair':{},'stored_fullvalidation':{'8000':{'t1':{'sm':raw,'sa':raw}}},'quality_control':{'grid':[{'temperature':t,'raw':raw}for t in(.75,1.,1.25)]}}
 def save(a):
  d1._atomic_json(owner/'attempt.json',{'status':'COMPLETE'})
  d1._atomic_json(owner/'analysis.json',a)
  d1._atomic_json(owner/'output-manifest.json',{n:{'sha256':d1.sha(owner/n)}for n in('attempt.json','analysis.json')})
 save(record);assert d1.retained_metadata(tmp_path)[0]=={'fixture':'ids'}
 (owner/'analysis.json').write_text('{}')
 with pytest.raises(d1.core.IdentityError,match='manifest'):d1.retained_metadata(tmp_path)
 changed=copy.deepcopy(record);changed['seed']=1703;save(changed)
 with pytest.raises(d1.core.IdentityError,match='identity'):d1.retained_metadata(tmp_path)
 changed=copy.deepcopy(record);changed['quality_control']['grid'][0]['temperature']=.5;save(changed)
 with pytest.raises(d1.core.IdentityError,match='temperature'):d1.retained_metadata(tmp_path)
 x=cells();x[-1]=x[-2]
 with pytest.raises(d1.core.IdentityError):d1.validate_cells(x)
def test_owner_math_stage_table_and_partial_grid_rejected(tmp_path):
 assert d1.STAGES=={'A':1000.,'B':3500.,'C':0.,'D':1400.}
 u=d1.uncertainty([1,2,3,4],np.arange(32).reshape(4,8));assert u['seed_full_width']==2*u['seed_half_width']and u['approx_32_map_width']==u['map_full_width']*.5
 d1._atomic_json(tmp_path/'cell-index.json',{'status':'PARTIAL','cells':[]})
 with pytest.raises(d1.core.IdentityError):d1.load_indexed_cells(tmp_path)

def test_retained_route_permutation_cannot_be_rebound_as_valid():
 from schrodinger.route_policy_data import Problem
 problems=(Problem(bytes(144),1,'IIIIIIII',0,1,1,1,None),Problem(bytes(144),1,'IIIIIIII',0,12,1,1,None))
 raw={'problems':[{'map_id':1,'family':'IIIIIIII','attempts':[{'route':route,'valid':True}for _ in range(32)]}for route in('01','02')]}
 assert d1.corroborate_raw(raw,problems)['verified_attempts']==64
 raw['problems'].reverse()
 with pytest.raises((ValueError,d1.core.IdentityError)):
  d1.corroborate_raw(raw,problems)

def watchdog_fixture(tmp_path,monkeypatch):
 w=d1.watchdog
 root=tmp_path/'watchdog';root.mkdir()
 ledger=root/'ledger.jsonl'
 # Copy immutable historical prefix plus approved administrative row only.
 ledger.write_bytes(b''.join(w.LEDGER.read_bytes().splitlines(keepends=True)[:144]))
 monkeypatch.setattr(w,'ROOT',root);monkeypatch.setattr(w,'LEDGER',ledger)
 return w,root,ledger

def test_watchdog_prefix_unique_finite_and_cumulative_budget(tmp_path,monkeypatch):
 w,root,ledger=watchdog_fixture(tmp_path,monkeypatch)
 original=ledger.read_bytes();rows,totals=w.verify_ledger(ledger)
 assert len(rows)==144 and totals['global']==pytest.approx(4583.809008752118)
 row={'entry_id':'test-charge','kind':'attempt_charge','stage':'A','charged_seconds':110.,'recovery':w.RECOVERY}
 w.append_once(ledger,row)
 with pytest.raises(RuntimeError,match='duplicate'):w.append_once(ledger,row)
 assert ledger.read_bytes().startswith(original)
 monkeypatch.setattr(w,'validate_decision',lambda p:{'kind':'suite','seconds':30.})
 monkeypatch.setattr(w,'supervise',lambda *a:pytest.fail('over-budget command launched'))
 assert w.execute(tmp_path/'decision',root/'blocked')==1
 assert len(w.verify_ledger(ledger)[0])==145
 ledger.write_bytes(original.replace(b'923.003597253',b'923.003597254',1))
 with pytest.raises(RuntimeError,match='prefix'):w.verify_ledger(ledger)

def test_watchdog_nonzero_exit_is_charged_once_and_allows_inspected_repeat(tmp_path,monkeypatch):
 w,root,ledger=watchdog_fixture(tmp_path,monkeypatch)
 decision=tmp_path/'decision.json';decision.write_text('{}')
 monkeypatch.setattr(w,'validate_decision',lambda p:{'kind':'smoke','seconds':10.,'argv':[sys.executable,'-c','raise SystemExit(7)']})
 assert w.execute(decision,root/'failed')==1
 terminal=json.loads((root/'failed/terminal.json').read_text())
 assert terminal['exit_code']==7 and terminal['cleanup_verified'] and not terminal['timed_out']
 rows,_=w.verify_ledger(ledger);charges=[r for r in rows if r.get('recovery')==w.RECOVERY]
 assert len(charges)==1 and charges[0]['charged_seconds']==terminal['elapsed_seconds']+w.FINALIZATION_ALLOWANCE
 assert not Path(str(ledger)+'.d1-reservation.json').exists()
 monkeypatch.setattr(w,'validate_decision',lambda p:{'kind':'smoke','seconds':10.,'argv':[sys.executable,'-c','print("ok")']})
 assert w.execute(decision,root/'repeat')==0
 assert len([r for r in w.verify_ledger(ledger)[0]if r.get('recovery')==w.RECOVERY])==2
 assert (root/'repeat/stdout.txt').read_text().strip()=='ok'

def test_watchdog_timeout_reaps_exact_child_group_including_descendant(tmp_path):
 import time
 w=d1.watchdog
 code='import subprocess,sys,signal,time; c=subprocess.Popen([sys.executable,"-c","import time; time.sleep(30)"]); signal.signal(signal.SIGTERM,lambda *a:(c.wait(),sys.exit(0))); print(c.pid,flush=True); time.sleep(30)'
 result=w.supervise([sys.executable,'-c',code],ROOT,tmp_path,time.monotonic()+1.)
 assert result['timed_out'] and result['cleanup_verified']
 assert result['exit_code'] is not None and w.group_gone(result['child_pid'])
 assert int((tmp_path/'stdout.txt').read_text().strip())!=result['child_pid']

def test_watchdog_append_failure_preserves_terminal_and_reservation(tmp_path,monkeypatch):
 w,root,ledger=watchdog_fixture(tmp_path,monkeypatch)
 before=ledger.read_bytes();decision=tmp_path/'decision';decision.write_text('{}')
 monkeypatch.setattr(w,'validate_decision',lambda p:{'kind':'smoke','seconds':10.,'argv':[sys.executable,'-c','print(1)']})
 monkeypatch.setattr(w,'append_once',lambda *a:(_ for _ in()).throw(OSError('append failed')))
 assert w.execute(decision,root/'failed-append')==1
 assert (root/'failed-append/terminal.json').is_file() and ledger.read_bytes()==before
 assert Path(str(ledger)+'.d1-reservation.json').is_file()
 assert json.loads((root/'failed-append/result.json').read_text())['status']=='ACCOUNTING_STOP'

def test_watchdog_production_fallback_and_manifest_reconciliation(tmp_path,monkeypatch):
 w,root,ledger=watchdog_fixture(tmp_path,monkeypatch)
 output=root/w.OWNER;output.mkdir()
 rows,_=w.verify_ledger(ledger)
 answer=w.reconcile_production(rows,ledger,output,'fallback',.2,root/'record')
 assert answer['status']=='UNCERTAIN_FALLBACK' and not answer['success']
 before=ledger.read_bytes();rows,_=w.verify_ledger(ledger)
 assert w.reconcile_production(rows,ledger,output,'second',.2,root/'record2')['status']=='PERMANENT_UNCERTAIN_FALLBACK'
 assert ledger.read_bytes()==before
 row=next(r for r in rows if r['entry_id']=='fallback')
 w.durable(output/'attempt.json',{**row,'status':'COMPLETE'})
 w.durable(output/'output-manifest.json',{'attempt.json':{'sha256':w.digest(output/'attempt.json')}})
 assert not w.reconcile_production(rows,ledger,output,'unused',.2,root/'record3')['success']
 assert ledger.read_bytes()==before

def test_watchdog_decision_binds_exact_files_review_argv_and_authority(tmp_path,monkeypatch):
 w,root,ledger=watchdog_fixture(tmp_path,monkeypatch)
 decision_path=tmp_path/'decision.json'; hashes=w.file_hashes()
 review=tmp_path/'d1-repair-static-review.md';review.write_text('D1_REVIEW_VERDICT: PASS\n'+'\n'.join(hashes.values()))
 monkeypatch.setattr(w,'REVIEW_PATHS',{'static':review,'implementation':tmp_path/'d1-repair-implementation-review.md'})
 decision={'kind':'smoke','seconds':10.,'approved':True,'hashes':hashes,'authorities':w.authority_hashes(),'cwd':str(w.WORKSPACE),'argv':w.expected_argv('smoke',decision_path),'owner':w.OWNER,'ledger':str(ledger),'ledger_sha256':w.digest(ledger),'review':{'path':str(review),'sha256':w.digest(review),'phase':'static','verdict':'PASS'}}
 w.durable(decision_path,decision);assert w.validate_decision(decision_path)==decision
 for key,value in [('hashes',{}),('authorities',{}),('argv',[]),('ledger_sha256','wrong'),('seconds',300.)]:
  w.durable(decision_path,{**decision,key:value})
  with pytest.raises(RuntimeError):w.validate_decision(decision_path)
 w.durable(decision_path,{**decision,'kind':'production','seconds':300.,'argv':w.expected_argv('production',decision_path)})
 with pytest.raises(RuntimeError,match='phase'):w.validate_decision(decision_path)
 suite={**decision,'kind':'suite','seconds':60.,'argv':w.expected_argv('suite',decision_path)}
 w.durable(decision_path,suite)
 with pytest.raises((KeyError,RuntimeError)):w.validate_decision(decision_path)
 concurrence=tmp_path/'concurrence.json'
 w.durable(concurrence,{'approved':True,'seconds':60.,'hashes':hashes,'argv':suite['argv']})
 suite['sol_concurrence']={'path':str(concurrence),'sha256':w.digest(concurrence)}
 w.durable(decision_path,suite);assert w.validate_decision(decision_path)['seconds']==60.
 concurrence.write_text('{}')
 with pytest.raises(RuntimeError,match='concurrence'):w.validate_decision(decision_path)
 review.write_text('D1_REVIEW_VERDICT: CHANGES REQUIRED\nPASS is required later.\n'+'\n'.join(hashes.values()))
 decision['review']['sha256']=w.digest(review);w.durable(decision_path,decision)
 with pytest.raises(RuntimeError,match='PASS'):w.validate_decision(decision_path)
 review.write_text('D1_REVIEW_VERDICT: PASS\nD1_REVIEW_VERDICT: PASS\n'+'\n'.join(hashes.values()))
 decision['review']['sha256']=w.digest(review);w.durable(decision_path,decision)
 with pytest.raises(RuntimeError,match='PASS'):w.validate_decision(decision_path)
 other=tmp_path/'unapproved-review.md';other.write_text('D1_REVIEW_VERDICT: PASS\n'+'\n'.join(hashes.values()))
 decision['review'].update(path=str(other),sha256=w.digest(other));w.durable(decision_path,decision)
 with pytest.raises(RuntimeError,match='phase'):w.validate_decision(decision_path)

def test_execute_production_fallback_charges_terminal_allowance_once(tmp_path,monkeypatch):
 w,root,ledger=watchdog_fixture(tmp_path,monkeypatch)
 decision=tmp_path/'decision';decision.write_text('{}')
 monkeypatch.setattr(w,'validate_decision',lambda p:{'kind':'production','seconds':300.,'argv':[sys.executable,'-c','raise SystemExit(8)']})
 assert w.execute(decision,root/'fallback-run')==1
 terminal=json.loads((root/'fallback-run/terminal.json').read_text())
 rows,_=w.verify_ledger(ledger)
 fallback=[r for r in rows if r.get('kind')=='watchdog_uncertain_fallback']
 assert len(fallback)==1 and fallback[0]['status']=='UNCERTAIN_FAILURE'
 assert fallback[0]['charged_seconds']==terminal['charged_seconds']==terminal['elapsed_seconds']+w.FINALIZATION_ALLOWANCE
 assert fallback[0]['elapsed_seconds']==terminal['elapsed_seconds']
 assert terminal['charged_seconds']<300.
 assert Path(str(ledger)+'.d1-reservation.json').exists()

def complete_terminal_fixture(w,root,ledger):
 import uuid
 output=root/w.OWNER;output.mkdir()
 row={'entry_id':str(uuid.uuid4()),'kind':'attempt_charge','stage':'D','status':'FINALIZATION_UNCERTAIN','output':str(output),'charged_seconds':4.1,'startup_allowance_seconds':2.,'finalization_allowance_seconds':2.}
 w.append_once(ledger,row)
 w.durable(output/'attempt.json',{**row,'kind':'attempt','status':'COMPLETE','ledger_path':str(ledger.resolve())})
 w.durable(output/'panel.json',{'ordered_problem_ids':list(range(512))});panel=w.digest(output/'panel.json')
 w.durable(output/'provenance.json',{'fixture':True})
 bindings={};greedy=[];entries=[]
 (output/'greedy').mkdir();(output/'cells').mkdir()
 for seed in d1.SEEDS:
  name=f'binding-{seed}.json';w.durable(output/name,{'seed':seed});bindings[str(seed)]=w.digest(output/name)
  for mode in ('sm','sa'):
   gid=f'{seed}-{mode}';name=f'greedy/{gid}.json';w.durable(output/name,{'fixture':True});greedy.append({'greedy_id':gid,'sha256':w.digest(output/name)})
   for temp in d1.TEMPS:
    cid=f'{seed}-{mode}-{temp:g}';name=f'cells/{cid}.json'
    w.durable(output/name,{'seed':seed,'mode':mode,'temperature':temp,'panel_sha256':panel,'binding_sha256':bindings[str(seed)],'greedy_id':gid})
    entries.append({'cell_id':cid,'sha256':w.digest(output/name),'status':'COMPLETE'})
 w.durable(output/'cell-index.json',{'status':'COMPLETE','cells':entries,'greedy':greedy,'bindings':bindings,'panel_sha256':panel})
 w.durable(output/'d1.json',{'status':'COMPLETE','cells':entries})
 manifest={str(p.relative_to(output)):{'sha256':w.digest(p)}for p in output.rglob('*')if p.is_file()}
 w.durable(output/'output-manifest.json',manifest)
 return output

@pytest.mark.parametrize('mutation',['none','manifest','result','index-altered','index-incomplete'])
def test_real_owner_terminal_requires_bound_complete_output_set(tmp_path,monkeypatch,mutation):
 w,root,ledger=watchdog_fixture(tmp_path,monkeypatch);output=complete_terminal_fixture(w,root,ledger)
 if mutation=='manifest':
  w.durable(output/'output-manifest.json',{'attempt.json':{'sha256':w.digest(output/'attempt.json')}})
 elif mutation=='result':w.durable(output/'d1.json',{'status':'COMPLETE','cells':[]})
 elif mutation in ('index-altered','index-incomplete'):
  index=json.loads((output/'cell-index.json').read_text());index['cells'].pop();w.durable(output/'cell-index.json',index)
  if mutation=='index-incomplete':
   manifest=json.loads((output/'output-manifest.json').read_text());manifest['cell-index.json']['sha256']=w.digest(output/'cell-index.json');w.durable(output/'output-manifest.json',manifest)
 rows,_=w.verify_ledger(ledger);before=ledger.read_bytes()
 if mutation=='none':assert w.reconcile_production(rows,ledger,output,'outer',.1,root/'record')['success']
 else:
  with pytest.raises(RuntimeError):w.reconcile_production(rows,ledger,output,'outer',.1,root/'record')
 assert ledger.read_bytes()==before

def test_watchdog_launch_exception_still_has_terminal_and_one_charge(tmp_path,monkeypatch):
 w,root,ledger=watchdog_fixture(tmp_path,monkeypatch)
 decision=tmp_path/'decision';decision.write_text('{}')
 monkeypatch.setattr(w,'validate_decision',lambda p:{'kind':'smoke','seconds':10.,'argv':['missing']})
 monkeypatch.setattr(w,'supervise',lambda *a:(_ for _ in()).throw(OSError('launch failed')))
 assert w.execute(decision,root/'launch-failure')==1
 terminal=json.loads((root/'launch-failure/terminal.json').read_text())
 assert terminal['exit_code'] is None and 'launch failed' in terminal['error']
 assert len([r for r in w.verify_ledger(ledger)[0]if r.get('recovery')==w.RECOVERY])==1
 assert Path(str(ledger)+'.d1-reservation.json').is_file()
