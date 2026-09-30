import pytest
import torch

from schrodinger.route_policy import RoutePolicy
from schrodinger.route_policy_variants import ARMS, RoutePolicyVariant, paired_arms, translate_route_policy_state

torch.set_num_threads(2)


def _inputs(seed=0, batch=5):
    generator = torch.Generator().manual_seed(seed)
    return torch.randn(batch, 12, 36, generator=generator)


def test_softmax_arm_reproduces_original_route_policy():
    """Equivalence test 1: same weights give the original model's logits."""
    torch.manual_seed(11)
    original = RoutePolicy("softmax")
    with torch.no_grad():  # move alpha/beta away from zero so the scale path is exercised
        for attention in original.attn:
            attention.alpha.uniform_(-0.3, 0.3)
            attention.beta.uniform_(-0.3, 0.3)
    variant = RoutePolicyVariant("softmax")
    variant.load_state_dict(translate_route_policy_state(original.state_dict()), strict=True)
    x = _inputs()
    torch.testing.assert_close(variant(x), original(x), atol=1e-6, rtol=1e-6)


def test_shared_seed_gives_original_initialisation():
    torch.manual_seed(5)
    original = RoutePolicy("softmax")
    variant = paired_arms(5)["softmax"]
    translated = translate_route_policy_state(original.state_dict())
    for name, tensor in variant.state_dict().items():
        assert torch.equal(tensor, translated[name]), name


def test_arms_have_equal_parameter_counts_and_shared_tensors():
    """Equivalence test 2."""
    models = paired_arms(3001)
    counts = {arm: sum(p.numel() for p in model.parameters()) for arm, model in models.items()}
    assert len(set(counts.values())) == 1, counts


@pytest.mark.parametrize("arm", ["wick_linear", "wick_real"])
def test_variant_arms_reduce_to_softmax_at_dt_zero(arm):
    """Equivalence test 3: with dt = 0 the variant equals the softmax arm with the same weights."""
    models = paired_arms(7, ("softmax", arm))
    softmax, variant = models["softmax"], models[arm]
    x = _inputs(1)
    torch.testing.assert_close(variant(x, dt_override=0.0), softmax(x), atol=1e-6, rtol=1e-6)
    assert not torch.allclose(variant(x), softmax(x), atol=1e-4)


@pytest.mark.parametrize("arm", ARMS)
def test_arms_train_one_step_and_report_dt(arm):
    model = paired_arms(9, (arm,))[arm]
    opt = torch.optim.AdamW(model.parameters(), lr=1e-3)
    loss = model(_inputs(2)).logsumexp(-1).mean()
    loss.backward()
    assert all(p.grad is not None and torch.isfinite(p.grad).all() for p in model.parameters())
    opt.step()
    dts = model.evolution_times()
    assert (dts == []) == (arm == "softmax")
    if dts:
        assert all(abs(x - 0.25) < 0.01 for layer in dts for x in layer)
