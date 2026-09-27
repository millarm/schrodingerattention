"""Matched 13-token route-policy models; no optimizer or training loop."""
from __future__ import annotations
import math, torch
from torch import nn
from schrodinger.attention import attention_from_scores
class Attention(nn.Module):
 def __init__(self,mode):
  if mode not in ("softmax","schrodinger"): raise ValueError("unknown attention mode")
  super().__init__(); self.mode=mode; self.q=nn.Linear(64,64); self.k=nn.Linear(64,64); self.v=nn.Linear(64,64); self.o=nn.Linear(64,64)
  if mode=="softmax": self.alpha=nn.Parameter(torch.zeros(2)); self.beta=nn.Parameter(torch.zeros(2))
  else: self.raw_dt=nn.Parameter(torch.full((2,),math.log(.1/.9))); self.raw_gamma=nn.Parameter(torch.full((2,),math.atanh(.1/math.pi)))
 def forward(self,x,dt_override=None,diagnostics=False):
  b,l,_=x.shape
  def h(z): return z.reshape(b,l,2,32).transpose(1,2)
  q,k,v=h(self.q(x)),h(self.k(x)),h(self.v(x)); scores=q@k.transpose(-2,-1)/math.sqrt(32)
  if self.mode=="softmax": out,prob=attention_from_scores(scores*torch.exp(self.alpha)[None,:,None,None],v*torch.exp(self.beta)[None,:,None,None]); diag=None
  else:
   dt=.5*torch.sigmoid(self.raw_dt)[None,:,None,None] if dt_override is None else dt_override; phase=math.pi*torch.tanh(self.raw_gamma)[None,:,None,None]*scores
   got=attention_from_scores(scores,v,phase,dt,"schrodinger",return_diagnostics=diagnostics)
   out,prob,*tail=got; diag=tail[0] if tail else None
  return self.o(out.transpose(1,2).reshape(b,l,64)),diag
class RoutePolicy(nn.Module):
 def __init__(self,mode="softmax"):
  if mode not in ("softmax","schrodinger"): raise ValueError("unknown policy mode")
  super().__init__(); self.mode=mode; self.row=nn.Linear(36,64); self.pos=nn.Parameter(torch.empty(12,64)); self.cls=nn.Parameter(torch.empty(1,1,64)); nn.init.normal_(self.pos,std=.02); nn.init.normal_(self.cls,std=.02)
  self.norm1=nn.ModuleList([nn.LayerNorm(64) for _ in range(2)]); self.attn=nn.ModuleList([Attention(mode) for _ in range(2)]); self.norm2=nn.ModuleList([nn.LayerNorm(64) for _ in range(2)]); self.ff=nn.ModuleList([nn.Sequential(nn.Linear(64,128),nn.GELU(),nn.Linear(128,64)) for _ in range(2)]); self.final=nn.LayerNorm(64); self.head=nn.Linear(64,4)
 def forward(self,x,dt_override=None,diagnostics=False):
  z=self.row(x)+self.pos; z=torch.cat((self.cls.expand(x.shape[0],-1,-1),z),1); diags=[]
  for n,a,m,f in zip(self.norm1,self.attn,self.norm2,self.ff):
   y,d=a(n(z),dt_override,diagnostics); z=z+y; z=z+f(m(z)); diags.append(d)
  logits=self.head(self.final(z)[:,0]); return (logits,diags) if diagnostics else logits
 def extra_scalars(self): return [p for n,p in self.named_parameters() if n.endswith(("alpha","beta","raw_dt","raw_gamma"))]
def masked_log_probs(logits,mask):
 if mask.dtype is not torch.bool or logits.shape!=mask.shape or mask.ndim!=2 or not torch.all(mask.any(-1)): raise ValueError("invalid legal mask")
 return torch.log_softmax(logits.masked_fill(~mask,float("-inf")),-1)
def policy_losses(logits,mask,q):
 if q.shape!=logits.shape or torch.any(q<0) or torch.any((q>0)&~mask) or not torch.allclose(q.sum(-1),torch.ones_like(q.sum(-1)),atol=1e-6): raise ValueError("invalid q")
 logp=masked_log_probs(logits,mask); p=logp.exp(); positive=q>0; ce=-(q[positive]*logp[positive]).sum()/q.shape[0]; brier=((p-q).square()).sum(-1).mean(); entropy=-(q[positive]*q[positive].log()).sum()/q.shape[0]
 return ce,brier,ce-entropy
