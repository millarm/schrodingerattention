import json
import numpy as np
import signal,time,subprocess,sys
import pytest
from schrodinger.route_feasibility import *

def test_d4_and_reversal_signature_invariance():
 walls=frozenset({cell(1,1),cell(1,2),cell(1,3),cell(3,4),cell(4,4),cell(4,5)})
 assert len({canonical_map([transform(x,k) for x in walls]) for k in range(8)})==1
 route=bytes([E,E,S,N]); assert signature(route)==signature(bytes([S,N,W,W]))

def test_bfs_counts_q_routes_and_verifier():
 walls=frozenset(); start,goal=cell(0,0),cell(2,2);dist,count=bfs_counts(walls,goal)
 routes=enumerate_routes(start,goal,walls)
 assert dist[start]==4 and count[start]==len(routes)==6
 q=q_target(start,walls,goal); assert sum(q.values())==pytest.approx(1) and q[E]==q[S]==.5
 assert set(q)==set(range(4)) and q[N]==q[W]==0
 for route in routes:
  x=start; product=1.
  for action in route:
   product*=q_target(x,walls,goal)[action];x=dict(neighbors(x,walls))[action]
  assert product==pytest.approx(1/6)
 assert all(verify(r,start,goal,walls) for r in routes)
 assert not verify(bytes([E,E,S]),start,goal,walls)
 assert not verify(bytes([E,E,S,S,E]),start,goal,walls)  # departure after goal
 assert not verify(bytes([E]),start,goal,frozenset({cell(0,1)}))

def test_support_novelty_and_hamilton_selection_replay():
 walls=frozenset(); support=support_for([(walls,cell(0,0),cell(1,1))])
 assert signature(bytes([E,S])) in support and signature(bytes([E])) in support
 assert signature(bytes([E,E,S])) not in support
 assert hamilton({(0,0):.5,(0,1):.5,(1,0):0,(1,1):0},3)=={(0,0):2,(0,1):1,(1,0):0,(1,1):0}
 inventory=[(i,'II' if i<4 else 'LL',bytes([i])) for i in range(8)]
 a,ra=select_maps(inventory,41001,'II',2,set());b,rb=select_maps(inventory,41001,'II',2,set())
 assert a==b and ra==rb

def test_deterministic_flow_feasible_infeasible_and_map_cap():
 caps={0:{(0,0):16,(0,1):16},1:{(0,0):16,(0,1):16}}
 flow=deterministic_flow(caps,{(0,0):16,(0,1):16})
 assert sum(flow.values())==32 and sum(v for (m,_),v in flow.items() if m==0)==16
 impossible=deterministic_flow({0:{(0,0):1}},{(0,0):2})
 assert sum(impossible.values())==1
 # Greedy m0->A blocks m1's only A edge; residual reverse m0->A permits m0->B.
 reverse=deterministic_flow({0:{(0,0):1,(0,1):1},1:{(0,0):1}},{(0,0):1,(0,1):1},map_capacity=1)
 assert reverse=={(0,(0,1)):1,(1,(0,0)):1}

def test_separate_bins_ties_and_continuous_problem_rng():
 assert bins(np.array([4,4,8,8]),np.array([4,16,4,16]))==(6.,3.)
 rows=[(0,1,4,4),(1,2,8,16),(2,3,4,16),(3,4,8,4)]
 rng=problem_rng(41002,'II'); first=choose_problems(0,rows,{(0,0):1,(1,1):1},(6.,3.),rng); second=choose_problems(1,rows,{(0,0):1,(1,1):1},(6.,3.),rng)
 replay=problem_rng(41002,'II'); assert (first,second)==(choose_problems(0,rows,{(0,0):1,(1,1):1},(6.,3.),replay),choose_problems(1,rows,{(0,0):1,(1,1):1},(6.,3.),replay))

def test_attempt_ownership_failure_and_local_ledger(tmp_path,monkeypatch):
 out,lock,ledger=tmp_path/'out',tmp_path/'lock',tmp_path/'ledger'
 with Attempt(out,lock,ledger): pass
 assert json.loads((out/'attempt.json').read_text())['status']=='COMPLETE' and not lock.exists()
 with pytest.raises(FileExistsError):
  with Attempt(out,lock,ledger):pass
 records=[json.loads(x) for x in ledger.read_text().splitlines()]; assert len(records)==2 and records[-1]['status']=='REJECTED' and records[-1]['charged_seconds']>=2

def test_attempt_real_timeout_restore_and_unique_ledger(tmp_path):
 old=signal.getsignal(signal.SIGALRM);out,lock,ledger=tmp_path/'out',tmp_path/'lock',tmp_path/'ledger'
 with pytest.raises(StageDeadline):
  with Attempt(out,lock,ledger,deadline=.02):time.sleep(.06)
 assert signal.getsignal(signal.SIGALRM)==old and not lock.exists()
 record=json.loads((out/'attempt.json').read_text());assert record['execution_status']=='FAILED' and record['entry_id']
 assert json.loads(ledger.read_text())['entry_id']==record['entry_id']

def test_attempt_output_mkdir_race_preserves_sentinel(tmp_path,monkeypatch):
 import schrodinger.route_feasibility as route
 out,lock,ledger=tmp_path/'out',tmp_path/'lock',tmp_path/'ledger';monkeypatch.setattr(route,'REJECTIONS',tmp_path/'rejects');original=type(out).mkdir
 def race(self,*a,**k):
  if self==out:original(self,*a,**k);(self/'attempt.json').write_bytes(b'sentinel');raise FileExistsError('race')
  return original(self,*a,**k)
 monkeypatch.setattr(type(out),'mkdir',race)
 with pytest.raises(FileExistsError):
  with Attempt(out,lock,ledger):pass
 record=json.loads(ledger.read_text());assert (out/'attempt.json').read_bytes()==b'sentinel' and not lock.exists() and record['status']=='REJECTED' and record['charged_seconds']>=STARTUP

def test_main_subprocess_tiny_injected_inventory_full_artifacts(tmp_path):
 output=tmp_path/'out'; ledger=tmp_path/'ledger'; lock=tmp_path/'lock'
 code=f'''import sys
import schrodinger.route_feasibility as r
r.LEDGER=r.Path({str(ledger)!r});r.LOCK=r.Path({str(lock)!r});r.REJECTIONS=r.Path({str(tmp_path/'rejects')!r})
OriginalAttempt=r.Attempt
r.Attempt=lambda out: OriginalAttempt(out,lock=r.LOCK,ledger=r.LEDGER)
r._inventory_records=lambda:[{{'id':0,'canonical':b'x','family':'II','walls':frozenset(), 'candidates':[]}}]
sys.argv=['route_feasibility','--output',{str(output)!r}]
r.main()
'''
 result=subprocess.run([sys.executable,'-c',code],cwd=str(ROOT),capture_output=True,text=True,timeout=5)
 assert result.returncode==0, result.stdout+result.stderr
 summary=json.loads((output/'summary.json').read_text())
 assert summary['execution_status']=='COMPLETE' and summary['outcome']=='FROZEN_SELECTION_FAILED'
 for name in ('inventory.json','selection.json','splits.json','training_states.json','novelty.json','summary.json','manifest.json','attempt.json'):assert (output/name).exists()
 assert len(ledger.read_text().splitlines())==1

def test_json_native_writer_scientific_failure_and_artifacts(tmp_path):
 records=[{'id':0,'canonical':b'0','family':'II','walls':frozenset(),'candidates':[]}]
 result={'outcome':'FROZEN_SELECTION_FAILED','execution_status':'COMPLETE','selection':{},'NOT_EVALUATED':['splits','support']}
 hashes=write_artifacts(tmp_path,records,result)
 for name in ('inventory.json','selection.json','splits.json','training_states.json','novelty.json','summary.json','manifest.json'):
  assert (tmp_path/name).exists();json.loads((tmp_path/name).read_text())
 assert set(hashes)>= {'inventory.json','summary.json'} and json.loads((tmp_path/'summary.json').read_text())['execution_status']=='COMPLETE'

def test_tiny_injected_whole_pipeline_all_eval_novelty_and_dag_states(tmp_path):
 walls=frozenset(); rows=candidates(walls); families=['II','LL','II','LL','II','LL','IL']
 records=[{'id':i,'canonical':bytes([i]),'family':family,'walls':walls,'candidates':rows} for i,family in enumerate(families)]
 counts={'train':{'II':1,'LL':1},'validation':{'II':1,'LL':1},'idtest':{'II':1,'LL':1},'iltest':{'IL':1}}
 result=pipeline(records,counts)
 assert result['execution_status']=='COMPLETE' and result['outcome']=='FEASIBILITY_FAILED_NOVELTY'
 assert set(result['novelty'])=={'validation','idtest','iltest'}
 assert {split:len(rows_) for split,rows_ in result['novelty'].items()}=={'validation':32,'idtest':32,'iltest':16}
 by_id={item['id']:item for item in records}; seeds={'validation':41002,'idtest':41003,'iltest':41004}
 for split,rows_ in result['novelty'].items():
  expected=[];flow={(item['map_id'],item['distance_bin'],item['logM_bin']):item['value'] for item in result['flow'][split]['flow']}
  for family,detail in result['selection'][split].items():
   rng=problem_rng(seeds[split],family)
   for map_id in detail['selected_ids']:
    item=by_id[map_id];alloc={key:flow.get((map_id,*key),0) for key in ((0,0),(0,1),(1,0),(1,1))}
    expected += [(map_id,start,goal) for start,goal,_,_ in choose_problems(map_id,item['candidates'],alloc,tuple(result['boundaries']),rng)]
  actual=[(row['map_id'],row['start'],row['goal']) for row in rows_]
  assert actual==expected and len(set(actual))==len(rows_)
  assert all(row['M']==len(row['routes'])==len(row['signatures']) for row in rows_)
 gate=novelty_gate(result['novelty']['iltest']);assert result['qualifying_il']==gate[1] and result['qualifying_maps']==gate[2]
 assert len({item['map_id'] for item in result['training']})==2
 assert all(sum(item['q'])==pytest.approx(1) for item in result['training_states'])
 assert result['support'] and result['support_sha256']
 write_artifacts(tmp_path,records,result)
 loaded={name:json.loads((tmp_path/name).read_text()) for name in ('selection.json','splits.json','training_states.json','novelty.json','summary.json','manifest.json')}
 assert loaded['novelty.json'].keys()=={'idtest','iltest','validation'} and loaded['summary.json']['execution_status']=='COMPLETE'

def test_enter_timer_exhaustion_persists_failed_attempt_manifest_and_charge(tmp_path):
 out,lock,ledger=tmp_path/'out',tmp_path/'lock',tmp_path/'ledger'; ledger.write_text(json.dumps({'charged_seconds':CAP})+'\n');old=signal.getsignal(signal.SIGALRM)
 with pytest.raises(StageDeadline):
  with Attempt(out,lock,ledger): pytest.fail('exhausted timer must reject before body')
 attempt=json.loads((out/'attempt.json').read_text());manifest=json.loads((out/'manifest.json').read_text());records=[json.loads(x) for x in ledger.read_text().splitlines()]
 assert attempt['status']==attempt['execution_status']=='FAILED' and attempt['charged_seconds']>=STARTUP and attempt['manifest_state']=='NOT_EVALUATED'
 assert manifest['execution_status']=='NOT_EVALUATED' and manifest['output_hashes']=={} and len(records)==2 and records[-1]['entry_id']==attempt['entry_id']
 assert not lock.exists() and signal.getsignal(signal.SIGALRM)==old

def test_log_write_failure_falls_back_to_failed_charged_ledger(tmp_path,monkeypatch):
 import schrodinger.route_feasibility as route
 out,lock,ledger=tmp_path/'out',tmp_path/'lock',tmp_path/'ledger';original=Path.write_text
 def fail_attempt(self,*args,**kwargs):
  if self==out/'attempt.json': raise OSError('injected attempt log failure')
  return original(self,*args,**kwargs)
 monkeypatch.setattr(Path,'write_text',fail_attempt)
 with pytest.raises(OSError,match='injected'):
  with Attempt(out,lock,ledger): pass
 record=json.loads(ledger.read_text());assert record['status']==record['execution_status']=='FAILED' and record['charged_seconds']>=STARTUP and 'log write failed' in record['error']
 assert not lock.exists() and not hasattr(route,'_open_attempt_fd')

def test_manifest_membership_and_attempt_binding_from_actual_written_output(tmp_path):
 out,lock,ledger=tmp_path/'out',tmp_path/'lock',tmp_path/'ledger';records=[{'id':0,'canonical':b'x','family':'II','walls':frozenset(),'candidates':[]}]
 with Attempt(out,lock,ledger) as attempt:
  write_artifacts(out,records,{'outcome':'FROZEN_SELECTION_FAILED','execution_status':'COMPLETE','selection':{}});attempt.bind_manifest()
 attempt_record=json.loads((out/'attempt.json').read_text());manifest=json.loads((out/'manifest.json').read_text())
 expected={'schrodinger/route_feasibility.py','tests/test_route_feasibility.py','next_level_learning_plan.md'}
 expected|={str(path.relative_to(ROOT)) for folder in ('specs','reviews') for path in (ROOT/'execution/next_level'/folder).glob('*.md')}
 assert expected<=set(manifest['inputs']) and attempt_record['manifest_sha256']==hashlib.sha256((out/'manifest.json').read_bytes()).hexdigest()
 assert attempt_record['output_hashes']==manifest['output_hashes'] and 'attempt.json' not in manifest['output_hashes'] and 'manifest.json' not in manifest['output_hashes']

def test_literal_nonuniform_hamilton_and_cross_family_global_flow():
 fractions={(0,0):.1,(0,1):.2,(1,0):.3,(1,1):.4}
 assert hamilton(fractions,17)=={(0,0):2,(0,1):3,(1,0):5,(1,1):7}
 a,b=(0,0),(0,1);global_flow=deterministic_flow({0:{a:1,b:1},1:{a:1}},{a:1,b:1},map_capacity=1)
 assert global_flow=={(0,b):1,(1,a):1}
 assert sum(deterministic_flow({1:{a:1}},{a:1,b:1},map_capacity=1).values())==1

def test_literal_novelty_255_256_and_15_16_map_gate():
 rows=lambda n,maps:[{'map_id':i%maps,'M_novel':4} for i in range(n)]
 assert novelty_gate(rows(255,16))==('FEASIBILITY_FAILED_NOVELTY',255,16)
 assert novelty_gate(rows(256,15))==('FEASIBILITY_FAILED_NOVELTY',256,15)
 assert novelty_gate(rows(256,16))==('FEASIBILITY_PASSED',256,16)

def test_actual_pipeline_bin_match_infeasible_schema_retains_selection_and_stops(tmp_path):
 walls=frozenset();low=[(0,4,4,4)]*16;high=[(0,8,8,16)]*16;families=['II','LL','II','LL','II','LL','IL']
 records=[{'id':i,'canonical':bytes([i]),'family':family,'walls':walls,'candidates':low if i<2 else high} for i,family in enumerate(families)]
 counts={'train':{'II':1,'LL':1},'validation':{'II':1,'LL':1},'idtest':{'II':1,'LL':1},'iltest':{'IL':1}}
 result=pipeline(records,counts);assert result['outcome']=='BIN_MATCH_INFEASIBLE' and result['execution_status']=='COMPLETE'
 assert result['selection'] and result['capacities'] and result['flow'] and result['NOT_EVALUATED']==['training_states','support','novelty']
 write_artifacts(tmp_path,records,result);summary=json.loads((tmp_path/'summary.json').read_text());assert summary['outcome']=='BIN_MATCH_INFEASIBLE' and summary['selection'] and summary['NOT_EVALUATED']

def test_lock_o_excl_race_preserves_external_owner_and_charges_rejection(tmp_path,monkeypatch):
 import schrodinger.route_feasibility as route
 out,lock,ledger=tmp_path/'out',tmp_path/'lock',tmp_path/'ledger';monkeypatch.setattr(route,'REJECTIONS',tmp_path/'rejects');original=route.os.open
 def race(path,flags,*args):
  if Path(path)==lock:
   fd=original(path,os.O_CREAT|os.O_EXCL|os.O_WRONLY);os.write(fd,b'external-owner');os.close(fd);raise FileExistsError('O_EXCL race')
  return original(path,flags,*args)
 monkeypatch.setattr(route.os,'open',race)
 with pytest.raises(FileExistsError,match='O_EXCL'):
  with Attempt(out,lock,ledger): pass
 record=json.loads(ledger.read_text());assert lock.read_bytes()==b'external-owner' and record['status']=='REJECTED' and record['charged_seconds']>=STARTUP
