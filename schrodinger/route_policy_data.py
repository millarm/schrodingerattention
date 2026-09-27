"""Immutable pool512 proposal-14 route-policy data adapter."""
from __future__ import annotations
import hashlib, json
from dataclasses import dataclass
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
ATTEMPT=ROOT/"execution/next_level_v3_pool512/attempts/feasibility-001"
MANIFEST_SHA256="305a9dd782befa9209942a2f52ebc0ba31d9d7ca61c913ecfb69fa5cca466395"
ACTIONS=(( -1,0),(0,1),(1,0),(0,-1))

@dataclass(frozen=True)
class RouteState:
    canonical: bytes; map_id:int; family:str; current:int; goal:int; q:tuple[float,float,float,float]
@dataclass(frozen=True)
class Problem:
    canonical:bytes; map_id:int; family:str; start:int; goal:int; length:int; M:int; Mnovel:int|None
@dataclass(frozen=True)
class TrainingBundle:
    states:tuple[RouteState,...]; problems:tuple[Problem,...]; support:tuple[bytes,...]; support_hash:str
@dataclass(frozen=True)
class HeldoutBundle:
    split:str; problems:tuple[Problem,...]

def _bytes(value):
    if not isinstance(value,dict) or set(value)!={"bytes_hex"}: raise ValueError("expected bytes_hex")
    raw=bytes.fromhex(value["bytes_hex"])
    if len(raw)!=144 or any(x not in (0,1) for x in raw): raise ValueError("invalid canonical map")
    return raw
def _read_checked(name, digest):
    raw=(ATTEMPT/name).read_bytes()
    if hashlib.sha256(raw).hexdigest()!=digest: raise ValueError("artifact hash mismatch: "+name)
    return json.loads(raw)
def _manifest():
    raw=(ATTEMPT/"manifest.json").read_bytes()
    if hashlib.sha256(raw).hexdigest()!=MANIFEST_SHA256: raise ValueError("unexpected proposal14 manifest")
    return json.loads(raw)
def _state(row, identities):
    key=row.get("key"); values=row.get("value")
    if not isinstance(key,list) or len(key)!=3: raise ValueError("invalid state key")
    canonical,current,goal=_bytes(key[0]),key[1],key[2]
    if not all(isinstance(x,int) and 0<=x<144 for x in (current,goal)) or current==goal: raise ValueError("invalid current/goal")
    if canonical not in identities: raise ValueError("state canonical not selected")
    if not isinstance(values,list) or len(values)!=4: raise ValueError("invalid q mapping")
    q=[None]*4
    for item in values:
        action,value=item.get("key"),item.get("value")
        if not isinstance(action,int) or not 0<=action<4 or q[action] is not None or not isinstance(value,(int,float)) or not np.isfinite(value) or value<0: raise ValueError("invalid q action")
        q[action]=float(value)
    if any(x is None for x in q) or not np.isclose(sum(q),1.0,atol=1e-7): raise ValueError("q not normalized")
    meta=identities[canonical]
    state=RouteState(canonical,meta[0],meta[1],current,goal,tuple(q))
    if canonical[current] or canonical[goal]: raise ValueError("current/goal blocked")
    legal_mask(state)
    return state
def _problem(row,indexed,*,heldout):
    canonical=_bytes(row.get("canonical")); required=("map_id","family","start","goal","length","M","n")
    record=indexed.get(canonical)
    if any(key not in row for key in required) or row["n"]!=12 or record is None or (record["map_id"],record["family"])!=(row["map_id"],row["family"]): raise ValueError("heldout inventory mismatch")
    if not all(isinstance(row[k],int) and 0<=row[k]<144 for k in ("start","goal")) or not all(isinstance(row[k],int) and row[k]>=0 for k in ("map_id","length","M")) or row["start"]==row["goal"] or canonical[row["start"]] or canonical[row["goal"]]: raise ValueError("invalid problem metadata")
    novel=row.get("Mnovel")
    if heldout:
        if isinstance(novel,bool) or not isinstance(novel,int) or not 0<=novel<=row["M"]: raise ValueError("invalid Mnovel")
        if row["family"] in ("IIIIIIII","LLLLLLLL") and novel!=0: raise ValueError("invalid routine Mnovel")
        if row["family"]=="IIIILLLL" and (novel<4 or 4*novel<row["M"] or 4*novel>3*row["M"]): raise ValueError("invalid challenge Mnovel")
    elif novel is not None: raise ValueError("training Mnovel must be absent/None")
    shortlists={item["key"]:item["value"] for item in record["shortlists"]}
    retained=shortlists.get(row["length"],{}).get("retained",())
    if (row["start"],row["goal"],row["length"],row["M"]) not in [tuple(x) for x in retained]: raise ValueError("problem not retained inventory pair")
    return Problem(canonical,row["map_id"],row["family"],row["start"],row["goal"],row["length"],row["M"],novel)
def load_training():
    manifest=_manifest(); name="proposal-14-training.json"; payload=_read_checked(name,manifest["outputs"][name])
    result=payload["result"]; identities={_bytes(r["canonical"]):(r["map_id"],r["family"]) for r in result["selected"]}
    if any(family not in ("IIIIIIII","LLLLLLLL") for _,family in identities.values()): raise ValueError("training family must be homogeneous")
    inventory=_read_checked("inventory.json",manifest["outputs"]["inventory.json"])
    indexed={_bytes(r["canonical"]):r for r in inventory}
    if any(canonical not in indexed or (indexed[canonical]["map_id"],indexed[canonical]["family"])!=metadata for canonical,metadata in identities.items()): raise ValueError("selected map disagrees with inventory")
    states=tuple(sorted((_state(row,identities) for row in result["states"]),key=lambda s:(s.map_id,s.goal,s.current)))
    if len({(s.canonical,s.current,s.goal) for s in states})!=len(states): raise ValueError("duplicate training state")
    support=tuple(bytes.fromhex(x["bytes_hex"]) for x in result["support"] if isinstance(x,dict) and set(x)=={"bytes_hex"})
    if len(support)!=len(result["support"]) or any(not item for item in support): raise ValueError("invalid support bytes")
    if tuple(sorted(support))!=support or len(set(support))!=len(support): raise ValueError("support must be sorted and unique")
    encoded=b"".join(len(item).to_bytes(2,"big")+item for item in support)
    if hashlib.sha256(encoded).hexdigest()!=result["support_hash"]: raise ValueError("support hash mismatch")
    problems=tuple(_problem(row,indexed,heldout=False) for row in result["selected"])
    if len({(p.canonical,p.start,p.goal,p.length,p.M) for p in problems})!=len(problems): raise ValueError("duplicate selected problem")
    return TrainingBundle(states,problems,support,result["support_hash"])
def _heldout(named_families,split):
    manifest=_manifest(); out=[]
    inventory=_read_checked("inventory.json",manifest["outputs"]["inventory.json"]); indexed={_bytes(r["canonical"]):r for r in inventory}
    for name,expected_families in named_families:
        payload=_read_checked(name,manifest["outputs"][name])
        if payload.get("proposal")!=14 or not isinstance(payload.get("results"),list): raise ValueError("invalid heldout proposal")
        actual_families=[]
        for wrapper in payload["results"]:
            family=wrapper.get("family"); result=wrapper.get("result")
            if not isinstance(result,dict) or family not in expected_families or result.get("outcome")!="OK": raise ValueError("invalid heldout wrapper")
            actual_families.append(family); rows=result.get("selected")
            if not isinstance(rows,list): raise ValueError("invalid heldout selected rows")
            for row in rows:
                if row.get("family")!=family: raise ValueError("selected row family mismatch")
                out.append(_problem(row,indexed,heldout=True))
        if tuple(actual_families)!=tuple(expected_families): raise ValueError("unexpected heldout family sequence")
    if len({(p.canonical,p.start,p.goal,p.length,p.M) for p in out})!=len(out): raise ValueError("duplicate heldout problem")
    return HeldoutBundle(split,tuple(out))
def load_validation(): return _heldout((("proposal-14-validation_routine.json",("IIIIIIII","LLLLLLLL")),("proposal-14-validation_mixed.json",("IIIILLLL",))),"validation")
def load_final_test():
    return _heldout((("proposal-14-test_routine.json",("IIIIIIII","LLLLLLLL")),("proposal-14-test_mixed.json",("IIIILLLL",))),"test")
def features(state:RouteState):
    x=np.zeros((12,36),dtype=np.float32); walls=np.frombuffer(state.canonical,dtype=np.uint8).reshape(12,12)
    x[:,:12]=walls; x[state.current//12,12+state.current%12]=1; x[state.goal//12,24+state.goal%12]=1
    return x
def legal_mask(state:RouteState):
    walls=np.frombuffer(state.canonical,dtype=np.uint8).reshape(12,12); row,col=divmod(state.current,12); mask=np.zeros(4,dtype=bool)
    for a,(dr,dc) in enumerate(ACTIONS):
        r,c=row+dr,col+dc; mask[a]=0<=r<12 and 0<=c<12 and not walls[r,c]
    if any(q and not mask[a] for a,q in enumerate(state.q)): raise ValueError("q assigns illegal action")
    return mask
class MapBalancedSampler:
    def __init__(self,states,seed):
        self.groups={}; self.rng=np.random.default_rng(np.random.SeedSequence([95001,seed]))
        for state in states: self.groups.setdefault(state.map_id,[]).append(state)
        self.map_ids=np.array(sorted(self.groups));
        for group in self.groups.values(): group.sort(key=lambda s:(s.goal,s.current))
    def batch(self,size=64):
        maps=self.rng.choice(self.map_ids,size=size,replace=True); result=[]
        for map_id in maps: result.append(self.groups[int(map_id)][self.rng.integers(len(self.groups[int(map_id)]))])
        return tuple(result)
    def state(self): return self.rng.bit_generator.state
    def restore(self,state): self.rng.bit_generator.state=state
    @staticmethod
    def batch_hash(batch): return hashlib.sha256(b"".join(s.canonical+s.goal.to_bytes(2,"big")+s.current.to_bytes(2,"big") for s in batch)).hexdigest()
