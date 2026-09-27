import pytest
import torch
from torch.autograd import gradcheck

from schrodinger.attention import attention_from_scores
from schrodinger.quantum_components import (
    VARIANTS,
    ProbeEncoder,
    QuantumMultiheadAttention,
    hamiltonian,
    quantum_weights,
    total_variation,
)

torch.set_num_threads(2)


def _scores(length=11, magnitude=2.0, dtype=torch.float64, seed=0):
    generator = torch.Generator().manual_seed(seed)
    return torch.randn(2, 2, length, length, generator=generator, dtype=dtype) * magnitude


def test_c1_hamiltonian_is_hermitian_and_keeps_antisymmetric_part():
    scores = _scores()
    h = hamiltonian(scores, hermitian=True)
    assert (h - h.conj().transpose(-2, -1)).abs().max() < 1e-12
    assert h.imag.abs().max() > 0.1
    assert hamiltonian(scores, hermitian=False).imag.abs().max() == 0


@pytest.mark.parametrize("variant", VARIANTS)
def test_rows_are_probability_distributions(variant):
    weights = quantum_weights(_scores(magnitude=3.0), 0.3, variant)
    assert weights.min() >= -1e-12
    torch.testing.assert_close(weights.sum(-1), torch.ones_like(weights.sum(-1)), atol=1e-10, rtol=0)


@pytest.mark.parametrize("variant", VARIANTS)
def test_dt_zero_reduces_to_softmax(variant):
    scores = _scores()
    torch.testing.assert_close(quantum_weights(scores, 0.0, variant), torch.softmax(scores, -1))


def test_phasefree_twin_matches_original_component_with_zero_phase():
    scores = _scores(dtype=torch.float32)
    values = torch.randn(2, 2, 11, 3)
    _, reference = attention_from_scores(scores, values, torch.zeros_like(scores), 0.2, "schrodinger")
    torch.testing.assert_close(quantum_weights(scores, 0.2, "c1_phasefree"), reference, atol=2e-6, rtol=1e-5)


def test_c1_acts_at_first_order_and_phasefree_at_second_order():
    scores = _scores()
    reference = torch.softmax(scores, -1)

    def ratio(variant):
        small, double = (total_variation(quantum_weights(scores, dt, variant), reference) for dt in (1e-3, 2e-3))
        return (double / small).item()

    print(f"TV ratio when dt doubles: c1={ratio('c1'):.3f} phasefree={ratio('c1_phasefree'):.3f}")
    assert abs(ratio("c1") - 2.0) < 0.05
    assert abs(ratio("c1_phasefree") - 4.0) < 0.05


def test_twins_differ_from_c1_away_from_zero_dt():
    scores = _scores()
    c1 = quantum_weights(scores, 0.3, "c1")
    for twin in ("c1_phasefree", "c1_wick", "c1_dephased"):
        assert total_variation(quantum_weights(scores, 0.3, twin), c1) > 1e-3, twin


@pytest.mark.parametrize("variant", VARIANTS[1:])
def test_double_precision_gradients(variant):
    scores = _scores(length=5, magnitude=1.0).requires_grad_(True)
    dt = torch.tensor(0.2, dtype=torch.float64, requires_grad=True)
    assert gradcheck(lambda s, t: quantum_weights(s, t, variant), (scores, dt), eps=1e-6, atol=1e-5)


def test_variants_have_equal_parameter_counts_and_shared_initialisation():
    models = {}
    for variant in VARIANTS:
        torch.manual_seed(7)
        models[variant] = ProbeEncoder(12, 17, 2, variant)
    counts = {variant: sum(p.numel() for p in model.parameters()) for variant, model in models.items()}
    assert len(set(counts.values())) == 1, counts
    base = models["softmax"].state_dict()
    for variant, model in models.items():
        for name, tensor in model.state_dict().items():
            if name in base:
                assert torch.equal(tensor, base[name]), (variant, name)


def test_module_forward_and_dt_override():
    torch.manual_seed(0)
    attention = QuantumMultiheadAttention(16, 2, "c1")
    inputs = torch.randn(3, 9, 16)
    output = attention(inputs)
    assert output.shape == inputs.shape and torch.isfinite(output).all()
    attention(inputs, dt_override=0.0)
    torch.testing.assert_close(attention.last_weights, torch.softmax(attention.last_scores, -1))
    torch.testing.assert_close(attention.effective_dt(), torch.full((2,), 0.05))
