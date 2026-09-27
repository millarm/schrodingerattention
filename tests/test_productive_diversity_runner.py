import json, subprocess, sys, time, hashlib
from pathlib import Path
import pytest
import copy, signal
from dataclasses import replace
import schrodinger.productive_diversity_runner as runner
import schrodinger.productive_diversity_data as data
from schrodinger.productive_diversity_data import ConstructionFailure, RUNGS, require_training_orientation_coverage, training_states_and_support, novelty_for
from schrodinger.route_feasibility import enumerate_routes, canonical_map, bfs_counts

def empty_inventory(spec): return [], {family:{'trials':0,'retained':0} for family in (*spec.training_families,*spec.challenge_families)}

def test_injected_main_scientific_a_b_failure_persists_outputs_and_one_ledger(tmp_path,monkeypatch):
 out,lock,ledger=tmp_path/'out',tmp_path/'lock',tmp_path/'ledger';original=runner.execute
 monkeypatch.setattr(runner,'execute',lambda output:original(output,inventory_fn=empty_inventory,lock=lock,ledger=ledger))
 monkeypatch.setattr(sys,'argv',['productive_diversity_runner','--output',str(out)]);runner.main()
 summary=json.loads((out/'summary.json').read_text());attempt=json.loads((out/'attempt.json').read_text());manifest=json.loads((out/'manifest.json').read_text())
 assert summary['A']['outcome']=='MAP_SUPPLY_FAILED' and summary['B']['outcome']=='MAP_SUPPLY_FAILED' and (out/'A'/'inventory.json').exists() and (out/'B'/'inventory.json').exists()
 assert attempt['status']=='COMPLETE' and attempt['manifest_sha256']==hashlib.sha256((out/'manifest.json').read_bytes()).hexdigest() and len(ledger.read_text().splitlines())==1 and manifest['output_hashes']

def test_technical_failure_does_not_start_b_and_deadline_is_charged(tmp_path,monkeypatch):
 out,lock,ledger=tmp_path/'out',tmp_path/'lock',tmp_path/'ledger'
 def broken(_): raise RuntimeError('technical')
 with pytest.raises(RuntimeError): runner.execute(out,inventory_fn=broken,lock=lock,ledger=ledger)
 assert not (out/'B').exists() and json.loads((out/'attempt.json').read_text())['status']=='FAILED' and not lock.exists()
 out,lock,ledger=tmp_path/'late',tmp_path/'late.lock',tmp_path/'late.ledger';ledger.write_text(json.dumps({'charged_seconds':899})+'\n')
 with pytest.raises(runner.Deadline): runner.execute(out,inventory_fn=empty_inventory,lock=lock,ledger=ledger)
 assert json.loads((out/'attempt.json').read_text())['status']=='FAILED' and len(ledger.read_text().splitlines())==2 and not lock.exists()

def test_deadline_after_completed_rung_artifact_preserves_parent_summary_manifest(tmp_path,monkeypatch):
 def slow(*args,**kwargs):time.sleep(.04)
 monkeypatch.setattr(runner,'training_dataset',slow);out=tmp_path/'out'
 with pytest.raises(runner.Deadline): runner.execute(out,inventory_fn=empty_inventory,lock=tmp_path/'lock',ledger=tmp_path/'ledger',deadline=.01)
 assert (out/'A'/'inventory.json').exists() and (out/'summary.json').exists() and (out/'manifest.json').exists()
 assert json.loads((out/'summary.json').read_text())['execution_status']=='FAILED'
 summary=json.loads((out/'A'/'summary.json').read_text())
 assert summary['stages']['inventory']=='COMPLETE' and summary['stages']['training']=='DEADLINE' and summary['stages']['validation_routine']=='NOT_EVALUATED'
 assert not (out/'B').exists()

def test_existing_output_and_lock_are_rejected_with_charged_preserved_owner(tmp_path):
 out,lock,ledger=tmp_path/'out',tmp_path/'lock',tmp_path/'ledger';out.mkdir()
 with pytest.raises(FileExistsError): runner.execute(out,inventory_fn=empty_inventory,lock=lock,ledger=ledger)
 assert json.loads(ledger.read_text())['status']=='REJECTED' and out.exists()
 lock.write_bytes(b'external')
 with pytest.raises(FileExistsError): runner.execute(tmp_path/'new',inventory_fn=empty_inventory,lock=lock,ledger=ledger)
 assert lock.read_bytes()==b'external' and len(ledger.read_text().splitlines())==2

def test_post_lock_mkdir_race_and_attempt_write_fault_charge_once(tmp_path,monkeypatch):
 out,lock,ledger=tmp_path/'out',tmp_path/'lock',tmp_path/'ledger';original=Path.mkdir
 def race(self,*args,**kwargs):
  if self==out: original(self,*args,**kwargs);raise FileExistsError('mkdir race')
  return original(self,*args,**kwargs)
 monkeypatch.setattr(Path,'mkdir',race)
 with pytest.raises(FileExistsError): runner.execute(out,inventory_fn=empty_inventory,lock=lock,ledger=ledger)
 assert out.exists() and not lock.exists() and json.loads(ledger.read_text())['status']=='REJECTED'
 monkeypatch.undo();out,lock,ledger=tmp_path/'fault',tmp_path/'fault.lock',tmp_path/'fault.ledger';write=runner._write
 def fault(path,value):
  if path.name=='attempt.json': raise OSError('fault')
  return write(path,value)
 monkeypatch.setattr(runner,'_write',fault)
 handler=signal.getsignal(signal.SIGALRM)
 with pytest.raises(OSError,match='fault'):runner.execute(out,inventory_fn=empty_inventory,lock=lock,ledger=ledger)
 assert len(ledger.read_text().splitlines())==1 and json.loads(ledger.read_text())['status']=='FAILED' and not lock.exists()
 assert signal.getsignal(signal.SIGALRM)==handler and signal.getitimer(signal.ITIMER_REAL)==(0.,0.)

def test_ladder_pass_stops_a_and_scientific_a_fail_b_pass_preserves_both(tmp_path,monkeypatch):
 calls=[]
 def fake(spec,out,_):
  calls.append(spec.name);out.mkdir();return {'outcome':'DATASET_PASS','execution_status':'COMPLETE','stages':{}}
 monkeypatch.setattr(runner,'run_rung',fake)
 result=runner.execute(tmp_path/'pass',lock=tmp_path/'pass.lock',ledger=tmp_path/'pass.ledger')
 assert result['selected_rung']=='A' and calls==['A']
 calls.clear()
 def mixed(spec,out,_):
  calls.append(spec.name);out.mkdir();return {'outcome':'MAP_SUPPLY_FAILED' if spec.name=='A' else 'DATASET_PASS','execution_status':'COMPLETE','stages':{}}
 monkeypatch.setattr(runner,'run_rung',mixed)
 result=runner.execute(tmp_path/'mixed',lock=tmp_path/'mixed.lock',ledger=tmp_path/'mixed.ledger')
 assert result['selected_rung']=='B' and result['A']['outcome']=='MAP_SUPPLY_FAILED' and calls==['A','B']

def oracle_fixture():
 # Deliberately tiny TEST-ONLY one-component task. Production families/counts/M
 # remain unchanged. All q/support/novelty and identities are genuine 8x8 oracles.
 walls_list=[{40,41,42},{20,28,36},{9,10,17},{10,11,19},{42,50,51},{45,52,53},
             {25,26,27},{41,42,43},{48,49,57},{54,55,62}]
 # Solve a <=49-placement UNIT fixture, not the frozen experimental generator:
 # two constrained 6-step teachers must leave a genuine mixed novel support.
 first={data.signature(r) for r in enumerate_routes(0,27,frozenset(walls_list[2]),8)}
 free=[data.signature(r) for r in enumerate_routes(0,27,frozenset(),8)]
 found=False
 for rr in range(7):
  for cc in range(7):
   candidate=frozenset({8*rr+cc,8*rr+cc+1,8*(rr+1)+cc+1})
   if 0 in candidate or 27 in candidate or canonical_map(candidate,8)==canonical_map(walls_list[2],8):continue
   if bfs_counts(candidate,27,8)[0].get(0)!=6:continue
   known=first|{data.signature(r) for r in enumerate_routes(0,27,candidate,8)}
   novel=sum(sig not in known for sig in free)
   if 5<=novel<=15:walls_list[3]=candidate;found=True;break
  if found:break
 assert found
 rows=[];pairs={};identities=set()
 for i,walls in enumerate(walls_list):
  walls=frozenset(walls);family='I' if i in (0,1,6,7) else 'L'
  start,goal=(0,27) if i in (2,3,8,9) else (0,6)
  # Fixed tiny shape translations only to avoid symmetry-equivalent fixtures;
  # no production pool or seed-dependent experiment selection occurs here.
  for dr,dc in [(0,0)]+[(r,c) for r in range(-7,8) for c in range(-7,8)]:
   coords=[(x//8+dr,x%8+dc) for x in walls]
   if any(not(0<=r<8 and 0<=c<8) for r,c in coords) or (i>=8 and min(r for r,c in coords)<4):continue
   candidate=frozenset(r*8+c for r,c in coords)
   if start in candidate or goal in candidate or canonical_map(candidate,8) in identities:continue
   if bfs_counts(candidate,goal,8)[0].get(start)!=6:continue
   walls=candidate;break
  identities.add(canonical_map(walls,8))
  rows.append(dict(map_id=i,walls=walls,canonical=canonical_map(walls,8),family=family,candidates=[]))
  dist,cnt=bfs_counts(walls,goal,8)
  assert dist[start]==6
  pairs[i]=[{**{k:v for k,v in rows[-1].items() if k not in ('canonical','candidates')},
             'start':s,'goal':g,'length':6,'M':cnt[start]} for s,g in ((start,goal),(goal,start))]
 assert len({r['canonical'] for r in rows})==len(rows)
 train=[p for i in range(6) for p in pairs[i]]
 states,support,digest=training_states_and_support(train,n=8)
 require_training_orientation_coverage(train,n=8)
 spec=replace(RUNGS[0],training_families=('I','L'),challenge_families=('L',),lengths=(6,))
 counts={key:{'I' if kind=='routine' else 'L':1} for key,kind in
         [('validation_routine','routine'),('validation_challenge','challenge'),('test_routine','routine'),('test_challenge','challenge')]}
 return rows,pairs,train,states,support,digest,spec,counts

def test_real_composed_success(tmp_path):
 rows,pairs,train,states,support,digest,spec,counts=oracle_fixture();calls=[];caches=[]
 def training(*args,**kwargs):return train,states,support,digest,{'flow':{(6,0):12}}
 def selected(rows,spec,split,required,excluded,actual_support,kind,props,cache):
  caches.append(cache);calls.append((split,kind))
  i={('validation','routine'):6,('test','routine'):7,('validation','challenge'):8,('test','challenge'):9}[(split,kind)]
  actual=novelty_for(pairs[i],actual_support,n=8,cache=cache)
  assert all(r['M_novel']==0 if kind=='routine' else r['M_novel']>=4 and .25<=r['M_novel']/r['M']<=.75 for r in actual),[(r['M'],r['M_novel']) for r in actual]
  return actual,{'quotas':{6:2},'flow':{(i,(6,0)):2}}
 out=tmp_path/'A'
 result=runner.run_rung(spec,out,lambda _:(rows,{}),counts=counts,per_map=2,multiplicity=(1,256),training_counts={'I':2,'L':4},training_fn=training,stratum_fn=selected)
 assert result['outcome']=='DATASET_PASS' and all(s=='COMPLETE' for s in result['stages'].values())
 assert calls==[('validation','routine'),('validation','challenge'),('test','routine'),('test','challenge')]
 assert len({id(c) for c in caches})==1
 assert hashlib.sha256((out/'support.bin').read_bytes()).hexdigest()==digest
 assert json.loads((out/'states.json').read_text())
 for key in counts:
  artifact=json.loads((out/f'{key}.json').read_text())
  assert len(artifact['rows'])==2 and isinstance(artifact['audit']['flow'],list)
  assert result['observed_counts'][key]['problems']==result['required_counts'][key]['problems']==2

def test_manifest_exact_and_isolated_rejections(tmp_path):
 out=tmp_path/'out';ledger=tmp_path/'ledger';lock=tmp_path/'lock'
 result=runner.execute(out,empty_inventory,lock=lock,ledger=ledger)
 assert result['execution_status']=='COMPLETE' and result['outcome']=='DATASET_LADDER_FAILED'
 m=json.loads((out/'manifest.json').read_text());config=m['effective_config']
 assert config['n']==8 and config['pool_seed']==80000 and config['problems_per_map']==16
 assert config['rungs'][0]['family_codes']==RUNGS[0].family_codes and config['rungs'][0]['counts']==runner._counts(RUNGS[0])
 assert 'execution/next_level_v2/specs/03-runner-invariants-reset.md' in m['inputs']
 for path,sha in m['inputs'].items():assert hashlib.sha256((runner.ROOT/path).read_bytes()).hexdigest()==sha
 for path,sha in m['output_hashes'].items():assert hashlib.sha256((out/path).read_bytes()).hexdigest()==sha
 with pytest.raises(FileExistsError):runner.execute(out,empty_inventory,lock=lock,ledger=ledger,rejections=tmp_path/'only_here')
 assert len(list((tmp_path/'only_here').glob('*.json')))==1

def test_cache_hits_and_budget_allowance(tmp_path,monkeypatch):
 cache=data.OracleCache();calls=0;original=data.enumerate_routes
 def counted(*args,**kwargs):
  nonlocal calls
  calls+=1;return original(*args,**kwargs)
 monkeypatch.setattr(data,'enumerate_routes',counted)
 a=cache.signatures(frozenset(),0,18,8);b=cache.signatures(frozenset(),0,18,8)
 assert a is b and calls==1
 ledger=tmp_path/'ledger';ledger.write_text(json.dumps({'charged_seconds':10.071845336})+'\n'+json.dumps({'charged_seconds':0,'budget_allowance_seconds':150})+'\n')
 assert runner._prior(ledger)==pytest.approx(160.071845336)

@pytest.mark.parametrize('fault',['wrong_family','duplicate','total','map_count','reuse','quota','M','fake_novelty','routine_novel'])
def test_independent_returned_record_invariants(fault):
 rows,pairs,train,states,support,digest,spec,counts=oracle_fixture()
 records=novelty_for(pairs[8],set(support),n=8);maps={r['map_id']:r for r in rows}
 required={'L':1};seen=set();quotas={6:2};per_map=2;kind='challenge'
 if fault=='wrong_family':records[0]['family']='I'
 elif fault=='duplicate':records[1]=dict(records[0])
 elif fault=='total':records.pop()
 elif fault=='map_count':required={'L':2};per_map=1
 elif fault=='reuse':seen.add(maps[8]['canonical'])
 elif fault=='quota':quotas={6:1,7:1}
 elif fault=='M':records[0]['M']+=1
 elif fault=='fake_novelty':records[0]['M_novel']=0
 elif fault=='routine_novel':kind='routine'
 with pytest.raises(runner.TechnicalFailure):
  runner._validate_stratum(records,required,kind,quotas,maps=maps,seen=seen,cache=data.OracleCache(),support=set(support),per_map=per_map,multiplicity=(1,256))

@pytest.mark.parametrize('novel_count',[0,2,4,16,20])
def test_challenge_zero_below_count_and_outside_ratio_rejected(novel_count):
 from itertools import combinations
 from collections import Counter
 walls=frozenset();signatures=[data.signature(r) for r in enumerate_routes(0,27,walls,8)]
 groups=Counter(signatures);keys=list(groups);novel=None
 for size in range(len(keys)+1):
  for combo in combinations(keys,size):
   if sum(groups[k] for k in combo)==novel_count:novel=set(combo);break
  if novel is not None:break
 assert novel is not None
 support=set(keys)-novel
 item=dict(map_id=0,family='I',walls=walls,canonical=canonical_map(walls,8))
 records=novelty_for([{**item,'start':0,'goal':27,'length':6,'M':20}],support,n=8)
 assert records[0]['M_novel']==novel_count
 with pytest.raises(runner.TechnicalFailure,match='novelty predicate'):
  runner._validate_stratum(records,{'I':1},'challenge',{6:1},maps={0:item},seen=set(),cache=data.OracleCache(),support=support,per_map=1,multiplicity=(1,256))

def test_real_rung_rejects_routine_as_challenge(tmp_path):
 rows,pairs,train,states,support,digest,spec,counts=oracle_fixture();calls=[]
 counts={k:{'I':1} for k in counts}
 def training(*args,**kwargs):return train,states,support,digest,{}
 def bad(rows,spec,split,required,excluded,support,kind,props,cache):
  calls.append(kind);i=6 if kind=='routine' else 7
  return novelty_for(pairs[i],support,n=8,cache=cache),{'quotas':{6:2}}
 out=tmp_path/'A'
 with pytest.raises(runner.TechnicalFailure,match='novelty predicate'):
  runner.run_rung(spec,out,lambda _:(rows,{}),counts=counts,per_map=2,multiplicity=(1,256),training_counts={'I':2,'L':4},training_fn=training,stratum_fn=bad)
 summary=json.loads((out/'summary.json').read_text())
 assert calls==['routine','challenge'] and summary['outcome']=='TECHNICAL_FAILURE'
 assert summary['stages']['validation_routine']=='COMPLETE' and summary['stages']['validation_challenge']=='TECHNICAL_FAILURE'
 assert summary['stages']['test_routine']=='NOT_EVALUATED'

def test_timer_restoration_and_no_old_artifact_edits(tmp_path):
 old=[runner.ROOT/'schrodinger/route_feasibility.py',runner.ROOT/'execution/next_level/ledger.jsonl']
 before=[hashlib.sha256(p.read_bytes()).hexdigest() for p in old]
 handler=signal.getsignal(signal.SIGALRM);previous=signal.setitimer(signal.ITIMER_REAL,10)
 try:
  runner.execute(tmp_path/'out',empty_inventory,lock=tmp_path/'lock',ledger=tmp_path/'ledger',deadline=1000)
  remaining=signal.getitimer(signal.ITIMER_REAL)[0]
  assert 9<remaining<=10 and signal.getsignal(signal.SIGALRM)==handler
 finally:
  signal.setitimer(signal.ITIMER_REAL,0)
  if previous[0]:signal.setitimer(signal.ITIMER_REAL,*previous)
 assert before==[hashlib.sha256(p.read_bytes()).hexdigest() for p in old]
