"""Stage-0 immutable oracle for the frozen 6x6 route-feasibility contract."""
from __future__ import annotations
import argparse, hashlib, json, os, signal, sys, time, uuid
from collections import deque
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable
import numpy as np

ROOT=Path(__file__).resolve().parents[1]; SIZE=6; ACTIONS=(( -1,0),(0,1),(1,0),(0,-1)); N,E,S,W=range(4)
LEDGER=ROOT/'execution/next_level/ledger.jsonl'; LOCK=ROOT/'execution/next_level/compute.lock'; CAP=600.; GLOBAL_CAP=7200.; RESERVE=30.; STARTUP=2.
REJECTIONS=ROOT/'execution/next_level/rejections'

class StageDeadline(RuntimeError): pass
def cell(r:int,c:int,n:int=SIZE)->int: return n*r+c
def rc(i:int,n:int=SIZE)->tuple[int,int]: return divmod(i,n)
def neighbors(i:int,walls:frozenset[int],n:int=SIZE)->list[tuple[int,int]]:
 r,c=rc(i,n); return [(a,cell(r+dr,c+dc,n)) for a,(dr,dc) in enumerate(ACTIONS) if 0<=r+dr<n and 0<=c+dc<n and cell(r+dr,c+dc,n) not in walls]
def transform(i:int,k:int,n:int=SIZE)->int:
 r,c=rc(i,n); reflect=k>=4; turns=k%4
 if reflect: c=n-1-c
 for _ in range(turns): r,c=c,n-1-r
 return cell(r,c,n)
def canonical_map(walls:Iterable[int],n:int=SIZE)->bytes:
 return min(bytes(int(i in set(transform(x,k,n) for x in walls)) for i in range(n*n)) for k in range(8))
def _connected(parts:set[int],n:int=SIZE)->bool:
 seen={next(iter(parts))}; q=list(seen)
 while q:
  x=q.pop()
  for _,y in neighbors(x,frozenset(),n):
   if y in parts and y not in seen: seen.add(y);q.append(y)
 return len(seen)==len(parts)
def triominoes(n:int=SIZE)->dict[frozenset[int],str]:
 out={}
 from itertools import combinations
 for part in combinations(range(n*n),3):
  s=frozenset(part)
  if not _connected(set(s),n): continue
  rows={rc(x,n)[0] for x in s}; cols={rc(x,n)[1] for x in s}; out[s]='I' if len(rows)==1 or len(cols)==1 else 'L'
 return out
def layouts(n:int=SIZE)->list[tuple[bytes,str,frozenset[int]]]:
 tris=triominoes(n); seen={}; items=list(tris.items())
 for a,ta in items:
  for b,tb in items:
   if tuple(sorted(a))>=tuple(sorted(b)) or a&b: continue
   if any(y in b for x in a for _,y in neighbors(x,frozenset(),n)): continue
   walls=a|b; key=canonical_map(walls,n); family=''.join(sorted((ta,tb)))
   seen.setdefault(key,(family,frozenset(i for i,value in enumerate(key) if value)))
 return [(key,*seen[key]) for key in sorted(seen)]
def bfs_counts(walls:frozenset[int],goal:int,n:int=SIZE)->tuple[dict[int,int],dict[int,int]]:
 dist={goal:0};q=deque([goal])
 while q:
  x=q.popleft()
  for _,y in neighbors(x,walls,n):
   if y not in dist: dist[y]=dist[x]+1;q.append(y)
 counts={goal:1}
 for x,d in sorted(dist.items(),key=lambda x:x[1]):
  if d: counts[x]=sum(counts.get(y,0) for _,y in neighbors(x,walls,n) if dist.get(y)==d-1)
 return dist,counts
def candidates(walls:frozenset[int],n:int=SIZE)->list[tuple[int,int,int,int]]:
 out=[]
 for goal in range(n*n):
  if goal in walls:continue
  dist,count=bfs_counts(walls,goal,n)
  for start in sorted(dist):
   if 4<=dist[start]<=10 and 4<=count[start]<=64: out.append((start,goal,dist[start],count[start]))
 return sorted(out)
def q_target(state:int,walls:frozenset[int],goal:int,n:int=SIZE)->dict[int,float]:
 dist,count=bfs_counts(walls,goal,n); denom=count[state]; legal=dict(neighbors(state,walls,n)); return {a:(count.get(legal[a],0)/denom if a in legal and dist.get(legal[a])==dist[state]-1 else 0.) for a in range(4)}
def enumerate_routes(start:int,goal:int,walls:frozenset[int],n:int=SIZE)->list[bytes]:
 dist,_=bfs_counts(walls,goal,n);out=[]
 def walk(x:int,path:bytes):
  if x==goal:out.append(path);return
  for a,y in neighbors(x,walls,n):
   if dist.get(y)==dist[x]-1:walk(y,path+bytes([a]))
 walk(start,b'');return out
def verify(route:bytes,start:int,goal:int,walls:frozenset[int],n:int=SIZE)->bool:
 dist,_=bfs_counts(walls,goal,n); x=start
 for a in route:
  if x==goal or a>3:return False
  nxt=dict(neighbors(x,walls,n)).get(a)
  if nxt is None:return False
  x=nxt
 return x==goal and len(route)==dist.get(start,-1)
def signature(route:bytes)->bytes:
 vectors=[ACTIONS[a] for a in route]; forms=[]
 def tv(dr:int,dc:int,k:int)->tuple[int,int]:
  if k>=4:dc=-dc
  for _ in range(k%4):dr,dc=dc,-dr
  return dr,dc
 for k in range(8):
  seq=bytes(ACTIONS.index(tv(dr,dc,k)) for dr,dc in vectors)
  forms.append(bytes(seq)); forms.append(bytes(ACTIONS.index((-ACTIONS[a][0],-ACTIONS[a][1])) for a in reversed(seq)))
 return min(forms)
def support_for(problems:Iterable[tuple[frozenset[int],int,int]])->set[bytes]:
 out=set()
 for walls,start,goal in problems:
  for route in enumerate_routes(start,goal,walls):
   for i in range(len(route)): out.add(signature(route[i:]))
 return out
def bins(distances:np.ndarray, multiplicities:np.ndarray)->tuple[float,float]: return float(np.quantile(distances,.5,method='linear')),float(np.quantile(np.log2(multiplicities),.5,method='linear'))
def bin_index(distance:int,m:int,boundaries:tuple[float,float])->tuple[int,int]: return (int(distance>boundaries[0]),int(np.log2(m)>boundaries[1]))
def hamilton(fractions:dict[tuple[int,int],float],total:int)->dict[tuple[int,int],int]:
 raw={k:v*total for k,v in fractions.items()}; result={k:int(v) for k,v in raw.items()}
 for k in sorted(raw,key=lambda k:(-(raw[k]-result[k]),k))[:total-sum(result.values())]:result[k]+=1
 return result
def deterministic_flow(capacities:dict[int,dict[tuple[int,int],int]],quotas:dict[tuple[int,int],int],map_capacity:int=16)->dict[tuple[int,tuple[int,int]],int]:
 """Genuine lexicographic Edmonds--Karp with map->cell reverse edges."""
 source=('source',); sink=('sink',); maps=[('map',m) for m in sorted(capacities)]; cells=[('cell',k) for k in sorted(quotas)]
 capacity={}
 def edge(a,b,n): capacity[(a,b)]=n;capacity.setdefault((b,a),0)
 for m in maps: edge(source,m,map_capacity)
 for m in maps:
  for k,n in sorted(capacities[m[1]].items()): edge(m,('cell',k),n)
 for c in cells: edge(c,sink,quotas[c[1]])
 flow={key:0 for key in capacity}
 while True:
  parent={source:None};q=deque([source])
  while q and sink not in parent:
   u=q.popleft(); nxt=sorted({b for a,b in capacity if a==u and capacity[(a,b)]-flow[(a,b)]>0},key=lambda node:(0 if node[0]=='source' else 1 if node[0]=='map' else 2 if node[0]=='cell' else 3,node[1] if len(node)>1 else -1))
   for v in nxt:
    if v not in parent: parent[v]=u;q.append(v)
    if v==sink:break
  if sink not in parent:break
  v=sink
  while parent[v] is not None:
   u=parent[v];flow[(u,v)]+=1;flow[(v,u)]-=1;v=u
 return {(m[1],c[1]):flow[(m,c)] for m in maps for c in cells if (m,c) in flow and flow[(m,c)]>0}
def choose_problems(map_id:int,candidates_:list[tuple[int,int,int,int]],alloc:dict[tuple[int,int],int],boundaries:tuple[float,float],rng:np.random.Generator)->list[tuple[int,int,int,int]]:
 ranked=list(candidates_);out=[]
 for key in sorted(alloc):
  eligible=[row for row in ranked if bin_index(row[2],row[3],boundaries)==key]; order=rng.permutation(len(eligible)); out += [eligible[i] for i in order[:alloc[key]]]
 return sorted(out)
def problem_rng(seed:int,family:str)->np.random.Generator: return np.random.Generator(np.random.PCG64(np.random.SeedSequence([seed,{'II':0,'LL':1,'IL':2}[family],1])))
def _inventory_records()->list[dict]:
 return [{'id':i,'canonical':key,'family':family,'walls':walls,'candidates':candidates(walls)} for i,(key,family,walls) in enumerate(layouts())]
def _select_split(records:list[dict],seed:int,needs:dict[str,int],excluded:set[bytes])->tuple[dict[str,list[dict]],dict]:
 selected={};detail={}
 for family,count in needs.items():
  eligible=[r for r in records if r['family']==family and r['canonical'] not in excluded and len(r['candidates'])>=16]
  rng=np.random.Generator(np.random.PCG64(np.random.SeedSequence([seed,{'II':0,'LL':1,'IL':2}[family],0])));perm=rng.permutation(len(eligible));chosen=[eligible[i] for i in perm[:count]]
  detail[family]={'requested':count,'available':len(eligible),'permutation':perm.tolist(),'selected_ids':[r['id'] for r in chosen]}
  if len(chosen)!=count: raise ValueError(json.dumps({'outcome':'FROZEN_SELECTION_FAILED','split_seed':seed,'family':family,**detail[family]}))
  selected[family]=chosen;excluded.update(r['canonical'] for r in chosen)
 return selected,detail
def _training_pairs(maps:list[dict],seed:int,family:str)->list[dict]:
 rng=problem_rng(seed,family);out=[]
 for item in sorted(maps,key=lambda x:x['id']):
  order=rng.permutation(len(item['candidates']));
  for start,goal,d,m in [item['candidates'][i] for i in order[:16]]:out.append({'map_id':item['id'],'family':family,'walls':item['walls'],'start':start,'goal':goal,'distance':d,'M':m})
 return sorted(out,key=lambda x:(x['map_id'],x['start'],x['goal']))
# Deprecated pre-C1 helpers: retained only for provenance and are unreachable;
# `main` invokes `pipeline`, which uses whole-split quotas and JSON-native rows.
def _evaluation_pairs(maps:list[dict],seed:int,family:str,boundaries:tuple[float,float],total:int)->tuple[list[dict],dict]:
 fractions={(a,b):0.25 for a in range(2) for b in range(2)}; quotas=hamilton(fractions,total); capacities={r['id']:{k:sum(bin_index(d,m,boundaries)==k for _,_,d,m in r['candidates']) for k in quotas} for r in maps};flow=deterministic_flow(capacities,quotas)
 if sum(flow.values())!=total: raise ValueError(json.dumps({'outcome':'BIN_MATCH_INFEASIBLE','quotas':quotas,'capacities':capacities,'flow':flow}))
 rng=problem_rng(seed,family);out=[]
 for item in sorted(maps,key=lambda x:x['id']):
  alloc={k:flow.get((item['id'],k),0) for k in quotas};
  for start,goal,d,m in choose_problems(item['id'],item['candidates'],alloc,boundaries,rng):out.append({'map_id':item['id'],'family':family,'walls':item['walls'],'start':start,'goal':goal,'distance':d,'M':m})
 return sorted(out,key=lambda x:(x['map_id'],x['start'],x['goal'])),{'quotas':quotas,'capacities':capacities,'flow':flow}
def feasibility(records:list[dict])->dict:
 """Pure full gate; selection failures remain frozen-selection evidence."""
 excluded=set();train,train_detail=_select_split(records,41001,{'II':32,'LL':32},excluded);validation,val_detail=_select_split(records,41002,{'II':4,'LL':4},excluded);idt,id_detail=_select_split(records,41003,{'II':8,'LL':8},excluded);il,il_detail=_select_split(records,41004,{'IL':32},excluded)
 training=_training_pairs(train['II'],41001,'II')+_training_pairs(train['LL'],41001,'LL'); boundaries=bins(np.array([x['distance'] for x in training]),np.array([x['M'] for x in training]))
 val,vd=_evaluation_pairs(validation['II'],41002,'II',boundaries,64);v2,vd2=_evaluation_pairs(validation['LL'],41002,'LL',boundaries,64);idp,id1=_evaluation_pairs(idt['II'],41003,'II',boundaries,128);id2,id2d=_evaluation_pairs(idt['LL'],41003,'LL',boundaries,128);ilp,ild=_evaluation_pairs(il['IL'],41004,'IL',boundaries,512)
 support=support_for((x['walls'],x['start'],x['goal']) for x in training);test=[]
 for x in ilp:
  routes=enumerate_routes(x['start'],x['goal'],x['walls']);novel=sum(signature(route) not in support for route in routes);test.append({**{k:v for k,v in x.items() if k!='walls'},'M_novel':novel,'route_signatures':[signature(r).hex() for r in routes]})
 qualifying=[x for x in test if x['M_novel']>=4]; maps=len({x['map_id'] for x in qualifying}); outcome='FEASIBILITY_PASSED' if len(qualifying)>=256 and maps>=16 else 'FEASIBILITY_FAILED_NOVELTY'
 return {'outcome':outcome,'execution_status':'COMPLETE','selection':{'train':train_detail,'validation':val_detail,'idtest':id_detail,'iltest':il_detail},'boundaries':boundaries,'training':training,'validation':val+v2,'idtest':idp+id2,'iltest':test,'flow':{'validation':[vd,vd2],'idtest':[id1,id2d],'iltest':ild},'support':sorted(support),'qualifying_il':len(qualifying),'qualifying_maps':maps}
def _jsonable(value):
 if isinstance(value,bytes):return value.hex()
 if isinstance(value,np.generic):return value.item()
 if isinstance(value,tuple):return [_jsonable(x) for x in value]
 if isinstance(value,list):return [_jsonable(x) for x in value]
 if isinstance(value,dict):return {str(k):_jsonable(v) for k,v in value.items()}
 return value
def _flow_records(flow): return [{'map_id':m,'distance_bin':k[0],'logM_bin':k[1],'value':v} for (m,k),v in sorted(flow.items())]
def _capacity_records(cap): return [{'map_id':m,'distance_bin':k[0],'logM_bin':k[1],'value':v} for m in sorted(cap) for k,v in sorted(cap[m].items())]
def _novel_records(rows,support,split):
 out=[]
 for x in rows:
  routes=enumerate_routes(x['start'],x['goal'],x['walls']); sig=[signature(r) for r in routes]
  out.append({'split':split,'map_id':x['map_id'],'start':x['start'],'goal':x['goal'],'distance':x['distance'],'M':x['M'],'M_novel':sum(s not in support for s in sig),'routes':[list(r) for r in routes],'signatures':[s.hex() for s in sig]})
 return out
def novelty_gate(rows:list[dict])->tuple[str,int,int]:
 qualifying=[row for row in rows if row['M_novel']>=4]; maps=len({row['map_id'] for row in qualifying})
 return ('FEASIBILITY_PASSED' if len(qualifying)>=256 and maps>=16 else 'FEASIBILITY_FAILED_NOVELTY',len(qualifying),maps)
def pipeline(records:list[dict],counts:dict|None=None)->dict:
 """Whole-split deterministic pipeline; ordinary supply/bin outcomes are data."""
 counts=counts or {'train':{'II':32,'LL':32},'validation':{'II':4,'LL':4},'idtest':{'II':8,'LL':8},'iltest':{'IL':32}}
 seeds={'train':41001,'validation':41002,'idtest':41003,'iltest':41004};excluded=set();selected={};selection={}
 try:
  for split in ('train','validation','idtest','iltest'):
   selected[split],selection[split]=_select_split(records,seeds[split],counts[split],excluded)
 except ValueError as error:
  return {'outcome':'FROZEN_SELECTION_FAILED','execution_status':'COMPLETE','evidence':json.loads(str(error)),'selection':selection,'NOT_EVALUATED':['splits','training_states','support','novelty']}
 training=[]
 for family,maps in selected['train'].items():training+=_training_pairs(maps,seeds['train'],family)
 distances=np.array([x['distance'] for x in training]); mult=np.array([x['M'] for x in training]); boundaries=bins(distances,mult); hist={k:int(sum(bin_index(d,m,boundaries)==k for d,m in zip(distances,mult))) for k in [(0,0),(0,1),(1,0),(1,1)]}; fractions={k:hist[k]/len(training) for k in hist}
 split_rows={}; flow_detail={}
 try:
  for split in ('validation','idtest','iltest'):
   maps=[x for group in selected[split].values() for x in group]; total=sum(counts[split].values())*16; quotas=hamilton(fractions,total); capacities={r['id']:{k:sum(bin_index(d,m,boundaries)==k for _,_,d,m in r['candidates']) for k in quotas} for r in maps}; flow=deterministic_flow(capacities,quotas)
   if sum(flow.values())!=total: return {'outcome':'BIN_MATCH_INFEASIBLE','execution_status':'COMPLETE','selection':selection,'boundaries':boundaries,'training_histogram':hist,'quotas':_jsonable(quotas),'capacities':_capacity_records(capacities),'flow':_flow_records(flow),'NOT_EVALUATED':['training_states','support','novelty']}
   rows=[]
   for family in sorted(selected[split]):
    rng=problem_rng(seeds[split],family)
    for item in sorted(selected[split][family],key=lambda x:x['id']):
     alloc={k:flow.get((item['id'],k),0) for k in quotas}
     for start,goal,d,m in choose_problems(item['id'],item['candidates'],alloc,boundaries,rng): rows.append({'map_id':item['id'],'family':family,'walls':item['walls'],'start':start,'goal':goal,'distance':d,'M':m})
   split_rows[split]=rows;flow_detail[split]={'quotas':_jsonable(quotas),'capacities':_capacity_records(capacities),'flow':_flow_records(flow)}
 except ValueError as error:return {'outcome':'BIN_MATCH_INFEASIBLE','execution_status':'COMPLETE','evidence':str(error),'selection':selection,'NOT_EVALUATED':['training_states','support','novelty']}
 states={}
 for x in training:
  dist,_=bfs_counts(x['walls'],x['goal']); from_start,_=bfs_counts(x['walls'],x['start'])
  for state in dist:
   if state!=x['goal'] and from_start.get(state,10**9)+dist[state]==dist[x['start']]:states.setdefault((x['map_id'],state,x['goal']),{'map_id':x['map_id'],'current':state,'goal':x['goal'],'q':[q_target(state,x['walls'],x['goal'])[a] for a in range(4)]})
 support=support_for((x['walls'],x['start'],x['goal']) for x in training);novelty={split:_novel_records(rows,support,split) for split,rows in split_rows.items()};outcome,nqual,nmaps=novelty_gate(novelty['iltest'])
 return {'outcome':outcome,'execution_status':'COMPLETE','selection':selection,'boundaries':boundaries,'training_histogram':hist,'flow':flow_detail,'training':training,'training_states':list(states.values()),'support':sorted(support),'support_sha256':hashlib.sha256(b''.join(bytes([len(x)])+x for x in sorted(support))).hexdigest(),'novelty':novelty,'qualifying_il':nqual,'qualifying_maps':nmaps}
def _input_hashes()->dict[str,str]:
 paths=[ROOT/'schrodinger/route_feasibility.py',ROOT/'tests/test_route_feasibility.py',ROOT/'next_level_learning_plan.md']
 paths += sorted((ROOT/'execution/next_level/specs').glob('*.md'))
 paths += sorted((ROOT/'execution/next_level/reviews').glob('*.md'))
 return {str(path.relative_to(ROOT)):hashlib.sha256(path.read_bytes()).hexdigest() for path in paths}
def _write_manifest(output:Path,output_hashes:dict[str,str],execution_status:str)->dict:
 manifest={'argv':getattr(sys,'orig_argv',sys.argv),'executable':sys.executable,'runtime':{'python':sys.version,'numpy':np.__version__},'inputs':_input_hashes(),'output_hashes':output_hashes,'execution_status':execution_status}
 (output/'manifest.json').write_text(json.dumps(manifest,indent=2,sort_keys=True))
 return manifest
def write_artifacts(output:Path,records:list[dict],result:dict)->dict:
 """JSON-native C1 writer; output hashes deliberately exclude manifest/attempt."""
 inventory=[{'id':x['id'],'canonical':x['canonical'].hex(),'family':x['family'],'walls':sorted(x['walls']),'candidate_count':len(x['candidates'])} for x in records]
 files={'inventory.json':inventory,'selection.json':result.get('selection',{}),'splits.json':{'boundaries':result.get('boundaries'),'training_histogram':result.get('training_histogram'),'flow':result.get('flow'),'training':[{k:v for k,v in x.items() if k!='walls'} for x in result.get('training',[])]},'training_states.json':result.get('training_states','NOT_EVALUATED'),'novelty.json':result.get('novelty','NOT_EVALUATED'),'summary.json':{k:v for k,v in result.items() if k not in ('support','training','training_states','novelty')}}
 for name,value in files.items():(output/name).write_text(json.dumps(_jsonable(value),indent=2,sort_keys=True))
 if isinstance(result.get('support'),list):(output/'support.bin').write_bytes(b''.join(bytes([len(x)])+x for x in result['support']))
 hashes={name:hashlib.sha256((output/name).read_bytes()).hexdigest() for name in files}
 if (output/'support.bin').exists():hashes['support.bin']=hashlib.sha256((output/'support.bin').read_bytes()).hexdigest()
 _write_manifest(output,hashes,result['execution_status']);return hashes
def select_maps(inventory:list[tuple[int,str,list]],seed:int,family:str,required:int,excluded:set[bytes])->tuple[list,dict]:
 code={'II':0,'LL':1,'IL':2}[family]; eligible=[x for x in inventory if x[1]==family and x[2] not in excluded]
 rng=np.random.Generator(np.random.PCG64(np.random.SeedSequence([seed,code,0]))); order=rng.permutation(len(eligible)); chosen=[eligible[i] for i in order[:required]]
 return chosen,{'available':len(eligible),'required':required,'permutation':order.tolist(),'selected_ids':[x[0] for x in chosen]}
def append_ledger(record:dict,path:Path=LEDGER)->None:
 import fcntl
 path.parent.mkdir(parents=True,exist_ok=True)
 with path.open('a+') as f:
  fcntl.flock(f,fcntl.LOCK_EX)
  try:
   f.seek(0)
   if record.get('entry_id') and any(json.loads(line).get('entry_id')==record['entry_id'] for line in f.read().splitlines() if line):raise RuntimeError('duplicate ledger entry id')
   f.write(json.dumps(record,sort_keys=True)+'\n');f.flush();os.fsync(f.fileno())
  finally:fcntl.flock(f,fcntl.LOCK_UN)
class Attempt:
 def __init__(self,out:Path,lock:Path=LOCK,ledger:Path=LEDGER,deadline:float|None=None):
  self.out,self.lock,self.ledger=out,lock,ledger;self.fd=None;self.owned_output=False;self.owned_lock=False;self.started=time.perf_counter();self.start_utc=datetime.now(timezone.utc).isoformat();self.prior=sum(json.loads(x).get('charged_seconds',0) for x in ledger.read_text().splitlines()) if ledger.exists() else 0;self.old_handler=None;self.old_timer=None;self.deadline=deadline;self.entry_id=str(uuid.uuid4());self.manifest_hash=None;self.output_hashes={};self.manifest_state='NOT_EVALUATED';self.recorded=False
 def record(self,status,error=None):
  elapsed=time.perf_counter()-self.started;charged=STARTUP+elapsed
  return {'entry_id':self.entry_id,'kind':'route_feasibility','stage':'stage0','execution_status':status,'status':status,'error':None if error is None else repr(error),'started_at_utc':self.start_utc,'ended_at_utc':datetime.now(timezone.utc).isoformat(),'elapsed_seconds':elapsed,'startup_allowance_seconds':STARTUP,'charged_seconds':charged,'prior_stage_seconds':self.prior,'cumulative_stage_seconds':self.prior+charged,'prior_global_seconds':self.prior,'cumulative_global_seconds':self.prior+charged,'pid':os.getpid(),'argv':getattr(sys,'orig_argv',sys.argv),'executable':sys.executable,'manifest_state':self.manifest_state,'manifest_sha256':self.manifest_hash,'output_hashes':self.output_hashes}
 def bind_manifest(self):
  self.output_hashes={name:hashlib.sha256(path.read_bytes()).hexdigest() for name in ('inventory.json','selection.json','splits.json','training_states.json','novelty.json','summary.json','support.bin') if (path:=self.out/name).exists()}
  self.manifest_hash=hashlib.sha256((self.out/'manifest.json').read_bytes()).hexdigest();self.manifest_state='EVALUATED'
 def _append_once(self,record):
  if not self.recorded:append_ledger(record,self.ledger);self.recorded=True
 def _persist_enter_failure(self,error):
  self.manifest_state='NOT_EVALUATED';self.output_hashes={}
  record=self.record('FAILED',error)
  try:
   _write_manifest(self.out,{},'NOT_EVALUATED');self.manifest_hash=hashlib.sha256((self.out/'manifest.json').read_bytes()).hexdigest();record=self.record('FAILED',error)
   (self.out/'attempt.json').write_text(json.dumps(record,indent=2))
  except BaseException as write_error:
   record={**self.record('FAILED',error),'error':f'enter failure {error!r}; required log write failed: {write_error!r}'}
  self._append_once(record)
 def _timer(self):
  remain=self.deadline if self.deadline is not None else min(CAP-self.prior-STARTUP-RESERVE,GLOBAL_CAP-self.prior-STARTUP-RESERVE)
  if remain<=0:raise StageDeadline('stage0 deadline exhausted')
  self.old_handler=signal.getsignal(signal.SIGALRM);self.old_timer=signal.setitimer(signal.ITIMER_REAL,0);signal.signal(signal.SIGALRM,lambda *_:(_ for _ in ()).throw(StageDeadline('stage0 deadline interrupted')));signal.setitimer(signal.ITIMER_REAL,remain)
 def __enter__(self):
  if self.out.exists() or self.lock.exists():self.reject('preflight fresh output/lock required');raise FileExistsError('fresh output/lock required')
  self.lock.parent.mkdir(parents=True,exist_ok=True)
  try:self.fd=os.open(self.lock,os.O_CREAT|os.O_EXCL|os.O_WRONLY);self.owned_lock=True;self.out.mkdir(parents=True);self.owned_output=True;self._timer();return self
  except BaseException as error:
   try:
    if self.owned_output:self._persist_enter_failure(error)
    elif isinstance(error,FileExistsError):self.reject(f'acquisition race: {error}')
   finally:self.cleanup()
   raise
 def reject(self,reason):
  record=self.record('REJECTED',reason);REJECTIONS.mkdir(parents=True,exist_ok=True);p=REJECTIONS/f'rejected-{record["entry_id"]}.json';fd=os.open(p,os.O_CREAT|os.O_EXCL|os.O_WRONLY)
  try:os.write(fd,json.dumps(record).encode())
  finally:os.close(fd)
  append_ledger(record,self.ledger)
 def guard(self):
  if self.prior+STARTUP+time.perf_counter()-self.started+RESERVE>=CAP or self.prior+STARTUP+time.perf_counter()-self.started>=GLOBAL_CAP:raise StageDeadline('stage0 cap')
 def cleanup(self):
  try:
   if self.fd is not None:os.close(self.fd)
  finally:
   if self.owned_lock:self.lock.unlink(missing_ok=True)
   self.fd=None;self.owned_lock=False
   if self.old_handler is not None:
    signal.setitimer(signal.ITIMER_REAL,0);signal.signal(signal.SIGALRM,self.old_handler)
    if self.old_timer and self.old_timer[0]>0:signal.setitimer(signal.ITIMER_REAL,*self.old_timer)
    self.old_handler=None
 def __exit__(self,t,v,b):
  record=self.record('FAILED' if t else 'COMPLETE',v)
  try:
   if self.owned_output:
    try:(self.out/'attempt.json').write_text(json.dumps(record,indent=2))
    except BaseException as e:self._append_once({**record,'status':'FAILED','execution_status':'FAILED','error':f'required log write failed: {e!r}'});raise
    else:self._append_once(record)
  finally:self.cleanup()
def main()->None:
 p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args()
 with Attempt(a.output) as attempt:
  attempt.guard();records=_inventory_records();result=pipeline(records);attempt.guard();write_artifacts(a.output,records,result);attempt.bind_manifest()
if __name__=='__main__':main()
