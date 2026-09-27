import pytest,torch
from schrodinger.route_policy import RoutePolicy,masked_log_probs,policy_losses
from schrodinger.attention import attention_from_scores
def test_matched_shapes_scalars_gradients_and_reload():
 torch.manual_seed(7); soft=RoutePolicy("softmax"); torch.manual_seed(7); sa=RoutePolicy("schrodinger")
 assert soft(torch.zeros(2,12,36)).shape==(2,4) and len(soft.extra_scalars())==len(sa.extra_scalars())==4
 assert sum(p.numel() for p in soft.extra_scalars())==sum(p.numel() for p in sa.extra_scalars())==8
 shared={k:v for k,v in soft.state_dict().items() if k in sa.state_dict()}; assert all(torch.equal(v,sa.state_dict()[k]) for k,v in shared.items()); sa.load_state_dict(shared,strict=False)
 assert sum(p.numel() for p in soft.parameters())==sum(p.numel() for p in sa.parameters())
 x=torch.randn(2,12,36); mask=torch.tensor([[1,1,0,0],[1,1,1,0]],dtype=torch.bool); q=torch.tensor([[.5,.5,0,0],[.2,.3,.5,0]])
 for model in (soft,sa):
  logits=model(x); ce,brier,kl=policy_losses(logits,mask,q); (ce+brier+kl).backward(); assert all(p.grad is not None and torch.isfinite(p.grad).all() for p in model.parameters())
 restored=RoutePolicy("softmax"); restored.load_state_dict(soft.state_dict()); assert torch.allclose(soft(x),restored(x),atol=1e-6)
 probs=torch.softmax(logits.masked_fill(~mask,float("-inf")),dim=-1)
 assert torch.allclose(probs.sum(-1),torch.ones(2)) and torch.equal(probs[~mask],torch.zeros_like(probs[~mask]))
 assert all(torch.isfinite(value).all() for value in policy_losses(logits,mask,q))
 bad=q.clone(); bad[0,2]=.1
 with pytest.raises(ValueError): policy_losses(logits,mask,bad)
def test_dt_zero_and_diagnostics_off():
 torch.manual_seed(3); model=RoutePolicy("schrodinger"); x=torch.randn(2,12,36)
 out=model(x,dt_override=0.0); logits,diags=model(x,dt_override=0.0,diagnostics=True)
 assert torch.allclose(out,logits,atol=2e-6,rtol=2e-5) and all(d is not None for d in diags)
 maxima=[]
 for scale in (.1,1.,3.):
  scores=torch.randn(2,2,13,13)*scale; values=torch.randn(2,2,13,32); so,sp=attention_from_scores(scores,values)
  saout,sap,diag=attention_from_scores(scores,values,torch.ones_like(scores)*.1,0.,"schrodinger",return_diagnostics=True)
  assert torch.allclose(sp,sap,atol=2e-6,rtol=2e-5) and torch.allclose(so,saout,atol=2e-6,rtol=2e-5)
  assert diag.max_hermiticity_error<=1e-6 and diag.max_unitarity_error<=2e-4 and diag.max_probability_row_error<=2e-4
  _,_,nonzero=attention_from_scores(scores,values,torch.ones_like(scores)*.1,.11,"schrodinger",return_diagnostics=True)
  assert nonzero.max_hermiticity_error<=1e-6 and nonzero.max_unitarity_error<=2e-4 and nonzero.max_probability_row_error<=2e-4
  maxima.append((float(nonzero.max_hermiticity_error),float(nonzero.max_unitarity_error),float(nonzero.max_probability_row_error),float((so-saout).abs().max()),float((sp-sap).abs().max())))
 print("length13 dt=.11 maxima",max(maxima))
 with pytest.raises(ValueError): RoutePolicy("bad")
 with pytest.raises(ValueError): masked_log_probs(torch.zeros(1,4),torch.zeros(1,4,dtype=torch.bool))
 with pytest.raises(ValueError): masked_log_probs(torch.zeros(1,4),torch.ones(1,4))
def test_diagnostics_off_does_not_call_primitive_diagnostics(monkeypatch):
 import schrodinger.attention as primitive
 model=RoutePolicy("schrodinger"); x=torch.randn(1,12,36)
 monkeypatch.setattr(primitive,"_diagnostics",lambda *_: (_ for _ in ()).throw(AssertionError("unexpected diagnostic")))
 model(x)
 with pytest.raises(AssertionError,match="unexpected"): model(x,diagnostics=True)
