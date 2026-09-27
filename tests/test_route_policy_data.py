import hashlib,json
import numpy as np,pytest
import schrodinger.route_policy_data as data
from schrodinger.route_policy_data import RouteState,features,legal_mask,MapBalancedSampler,_state,load_training,load_validation,load_final_test
def state(current=13,goal=14,q=(0,1,0,0)):
 walls=bytearray(144); walls[0]=1; walls[1]=1
 return RouteState(bytes(walls),7,"IIIIIIII",current,goal,q)
def test_features_legality_and_q_metadata_rejection():
 s=state(); x=features(s); assert x.shape==(12,36) and x.dtype==np.float32 and x[1,13]==1 and x[1,26]==1
 assert legal_mask(s).tolist()==[False,True,True,True]
 with pytest.raises(ValueError,match="illegal"): legal_mask(state(q=(1,0,0,0)))
 identity={s.canonical:(7,"IIIIIIII")}
 row={"key":[{"bytes_hex":s.canonical.hex()},13,14],"value":[{"key":i,"value":v} for i,v in enumerate((0,1,0,0))]}
 assert _state(row,identity).current==13 and _state(row,identity).goal==14
 row["key"][1],row["key"][2]=row["key"][2],row["key"][1]
 swapped=_state(row,identity); assert (swapped.current,swapped.goal)==(14,13)
 illegal_swap={"key":[{"bytes_hex":s.canonical.hex()},13,2],"value":[{"key":0,"value":1},{"key":1,"value":0},{"key":2,"value":0},{"key":3,"value":0}]}
 with pytest.raises(ValueError,match="illegal"): _state(illegal_swap,identity)
def test_map_balanced_sampler_restore_and_hash():
 a=state(); b=RouteState(a.canonical,8,"LLLLLLLL",15,16,(0,1,0,0)); sampler=MapBalancedSampler((a,b),1701)
 saved=sampler.state(); first=sampler.batch(); digest=MapBalancedSampler.batch_hash(first); sampler.restore(saved)
 assert MapBalancedSampler.batch_hash(sampler.batch())==digest and len(first)==64 and {x.map_id for x in first}<={7,8}
def test_actual_saved_adapter_boundary_smoke():
 train=load_training(); validation=load_validation(); final=load_final_test()
 assert (len(train.states),len(train.problems),len(train.support),train.support_hash)==(32946,1024,63517,"b3feead79ea397f3b1be56ac1b601428cedf620157e2740a93cc15946f00ccc3")
 assert ({p.family for p in train.problems},[sum(p.family==f for p in train.problems) for f in ("IIIIIIII","LLLLLLLL")])==({"IIIIIIII","LLLLLLLL"},[512,512])
 assert (len(validation.problems),len(final.problems),len({p.map_id for p in validation.problems}),len({p.map_id for p in final.problems}))==(512,2048,32,128)
 assert [len({p.map_id for p in bundle.problems if p.family==family}) for bundle in (train,validation,final) for family in ("IIIIIIII","LLLLLLLL","IIIILLLL")]==[32,32,0,12,12,8,48,48,32]
 assert [sum(p.family==f for p in validation.problems) for f in ("IIIIIIII","LLLLLLLL","IIIILLLL")]==[192,192,128]
 assert [sum(p.family==f for p in final.problems) for f in ("IIIIIIII","LLLLLLLL","IIIILLLL")]==[768,768,512]
 identities=[{p.canonical for p in x.problems} for x in (train,validation,final)]
 assert all(identities[i].isdisjoint(identities[j]) for i in range(3) for j in range(i))
 assert [(s.map_id,s.goal,s.current) for s in train.states]==sorted((s.map_id,s.goal,s.current) for s in train.states)
 with pytest.raises(Exception): train.states[0].goal=0
 assert all(p.Mnovel is None for p in train.problems) and all(isinstance(p.Mnovel,int) for p in validation.problems+final.problems)

def _fixture(tmp_path,monkeypatch):
 root=tmp_path/"saved"; root.mkdir(exist_ok=True); walls=lambda n: {"bytes_hex":(bytes([1 if i==n else 0 for i in range(144)])).hex()}
 maps=[(1,"IIIIIIII",walls(0)),(2,"LLLLLLLL",walls(3)),(3,"IIIILLLL",walls(4))]
 inventory=[{"canonical":c,"map_id":mid,"family":family,"shortlists":[{"key":14,"value":{"retained":[[1,2,14,16]]}}]} for mid,family,c in maps]
 row=lambda mid,family,c,novel=None: {**({"Mnovel":novel} if novel is not None else {}),"canonical":c,"map_id":mid,"family":family,"start":1,"goal":2,"length":14,"M":16,"n":12}
 state={"key":[maps[0][2],1,2],"value":[{"key":0,"value":0},{"key":1,"value":1},{"key":2,"value":0},{"key":3,"value":0}]}
 support=[{"bytes_hex":"0102"},{"bytes_hex":"0304"}]; support_hash=hashlib.sha256(b"\x00\x02\x01\x02\x00\x02\x03\x04").hexdigest()
 payloads={"inventory.json":inventory,"proposal-14-training.json":{"result":{"selected":[row(*maps[0]),row(*maps[1])],"states":[state],"support":support,"support_hash":support_hash}},
  "proposal-14-validation_routine.json":{"proposal":14,"results":[{"family":"IIIIIIII","result":{"outcome":"OK","selected":[row(*maps[0],0)]}},{"family":"LLLLLLLL","result":{"outcome":"OK","selected":[row(*maps[1],0)]}}]},
  "proposal-14-validation_mixed.json":{"proposal":14,"results":[{"family":"IIIILLLL","result":{"outcome":"OK","selected":[row(*maps[2],4)]}}]},
  "proposal-14-test_routine.json":{"proposal":14,"results":[{"family":"IIIIIIII","result":{"outcome":"OK","selected":[row(*maps[0],0)]}},{"family":"LLLLLLLL","result":{"outcome":"OK","selected":[row(*maps[1],0)]}}]},
  "proposal-14-test_mixed.json":{"proposal":14,"results":[{"family":"IIIILLLL","result":{"outcome":"OK","selected":[row(*maps[2],4)]}}]}}
 def write(name,value):
  raw=json.dumps(value,sort_keys=True,separators=(",",":")).encode(); (root/name).write_bytes(raw); return hashlib.sha256(raw).hexdigest()
 def seal():
  outputs={name:hashlib.sha256((root/name).read_bytes()).hexdigest() for name in payloads}; manifest={"outputs":outputs}
  raw=json.dumps(manifest,sort_keys=True,separators=(",",":")).encode(); (root/"manifest.json").write_bytes(raw)
  monkeypatch.setattr(data,"ATTEMPT",root); monkeypatch.setattr(data,"MANIFEST_SHA256",hashlib.sha256(raw).hexdigest())
 for name,value in payloads.items(): write(name,value)
 seal()
 return payloads,write,seal

def test_saved_format_fixture_hash_decode_and_negative_boundaries(tmp_path,monkeypatch):
 payloads,write,seal=_fixture(tmp_path,monkeypatch)
 train=data.load_training(); held=data.load_validation()
 assert train.states[0].canonical.hex()==payloads["proposal-14-training.json"]["result"]["states"][0]["key"][0]["bytes_hex"] and (train.states[0].current,train.states[0].goal,train.states[0].q)==(1,2,(0.,1.,0.,0.))
 (data.ATTEMPT/"proposal-14-training.json").write_bytes(b"{}")
 with pytest.raises(ValueError,match="artifact hash mismatch"): data.load_training()
 write("proposal-14-training.json",payloads["proposal-14-training.json"]); seal()
 def reseal_support(p):
  items=[bytes.fromhex(item["bytes_hex"]) for item in p["proposal-14-training.json"]["result"]["support"]]
  p["proposal-14-training.json"]["result"]["support_hash"]=hashlib.sha256(b"".join(len(item).to_bytes(2,"big")+item for item in items)).hexdigest()
 cases=[
  ("malformed key",lambda p:p["proposal-14-training.json"]["result"]["states"][0].__setitem__("key",[]),data.load_training),
  ("inventory mismatch",lambda p:p["proposal-14-training.json"]["result"]["selected"][0].__setitem__("start",9),data.load_training),
  ("blocked endpoint",lambda p:p["proposal-14-training.json"]["result"]["selected"][0].__setitem__("start",0),data.load_training),
  ("out of range",lambda p:p["proposal-14-training.json"]["result"]["selected"][0].__setitem__("goal",144),data.load_training),
  ("duplicate state",lambda p:p["proposal-14-training.json"]["result"]["states"].append(p["proposal-14-training.json"]["result"]["states"][0]),data.load_training),
  ("duplicate problem",lambda p:p["proposal-14-training.json"]["result"]["selected"].append(p["proposal-14-training.json"]["result"]["selected"][0]),data.load_training),
  ("support hash",lambda p:p["proposal-14-training.json"]["result"].__setitem__("support_hash","0"*64),data.load_training),
  ("duplicate support",lambda p:(p["proposal-14-training.json"]["result"]["support"].append({"bytes_hex":"0102"}),reseal_support(p)),data.load_training),
  ("unsorted support",lambda p:(p["proposal-14-training.json"]["result"]["support"].reverse(),reseal_support(p)),data.load_training),
  ("wrong proposal",lambda p:p["proposal-14-validation_routine.json"].__setitem__("proposal",13),data.load_validation),
  ("wrong wrapper",lambda p:p["proposal-14-validation_routine.json"]["results"][0].__setitem__("family","IIIILLLL"),data.load_validation),
  ("non-OK wrapper",lambda p:p["proposal-14-validation_routine.json"]["results"][0]["result"].__setitem__("outcome","NO"),data.load_validation),
  ("invalid novelty",lambda p:p["proposal-14-validation_mixed.json"]["results"][0]["result"]["selected"][0].__setitem__("Mnovel",1),data.load_validation),]
 for _,mutate,loader in cases:
  payloads,write,seal=_fixture(tmp_path,monkeypatch); mutate(payloads)
  for name,value in payloads.items(): write(name,value)
  seal()
  with pytest.raises(ValueError): loader()
