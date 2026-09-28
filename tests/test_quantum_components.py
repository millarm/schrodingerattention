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


# --- C3: Trotterised dephasing knob -------------------------------------------------

from schrodinger.quantum_components import (  # noqa: E402
    ALL_VARIANTS,
    C4_VARIANTS,
    TROTTER_STEPS,
    c3_weights,
    c4_coefficients,
    c4_mix,
)


def test_c3_coherent_limit_equals_c1():
    scores = _scores()
    torch.testing.assert_close(c3_weights(scores, 0.3, 0.0), quantum_weights(scores, 0.3, "c1"))


def test_c3_classical_limit_is_markov_chain_of_trotter_steps():
    scores = _scores()
    h = hamiltonian(scores, hermitian=True)
    transition = torch.matrix_exp(-1j * (0.3 / TROTTER_STEPS) * h).abs().square()
    expected = torch.softmax(scores, -1)
    for _ in range(TROTTER_STEPS):
        expected = expected @ transition.transpose(-2, -1)
    torch.testing.assert_close(c3_weights(scores, 0.3, 1.0), expected)


@pytest.mark.parametrize("lam", [0.0, 0.3, 1.0])
def test_c3_rows_are_distributions_and_reduce_at_dt_zero(lam):
    scores = _scores(magnitude=3.0)
    weights = c3_weights(scores, 0.4, lam)
    assert weights.min() >= -1e-12
    torch.testing.assert_close(weights.sum(-1), torch.ones_like(weights.sum(-1)), atol=1e-10, rtol=0)
    torch.testing.assert_close(c3_weights(scores, 0.0, lam), torch.softmax(scores, -1))


def test_c3_intermediate_dephasing_lies_between_limits():
    scores = _scores()
    coherent, classical = c3_weights(scores, 0.4, 0.0), c3_weights(scores, 0.4, 1.0)
    middle = c3_weights(scores, 0.4, 0.5)
    assert total_variation(middle, coherent) > 1e-4 and total_variation(middle, classical) > 1e-4


def test_c3_double_precision_gradients():
    scores = _scores(length=5, magnitude=1.0).requires_grad_(True)
    dt = torch.tensor(0.2, dtype=torch.float64, requires_grad=True)
    lam = torch.tensor(0.4, dtype=torch.float64, requires_grad=True)
    assert gradcheck(c3_weights, (scores, dt, lam), eps=1e-6, atol=1e-5)


# --- C4: amplitude-level value mixing -----------------------------------------------


@pytest.mark.parametrize("variant", C4_VARIANTS)
def test_c4_coefficients_have_unit_norm_and_agree_at_dt_zero(variant):
    scores = _scores()
    coefficients = c4_coefficients(scores, 0.3, variant)
    norms = coefficients.abs().square().sum(-1)
    if variant != "c4_dephased":
        torch.testing.assert_close(norms, torch.ones_like(norms), atol=1e-10, rtol=0)
    base = torch.sqrt(torch.softmax(scores, -1)).to(torch.complex128)
    torch.testing.assert_close(c4_coefficients(scores, 0.0, variant), base)


def test_c4_twins_are_real_or_nonnegative_as_defined():
    scores = _scores()
    c4 = c4_coefficients(scores, 0.3, "c4")
    assert c4.imag.abs().max() > 1e-3
    magnitude = c4_coefficients(scores, 0.3, "c4_magnitude")
    torch.testing.assert_close(magnitude, c4.abs().to(magnitude.dtype))
    assert magnitude.real.min() >= 0
    signed = c4_coefficients(scores, 0.3, "c4_real")
    assert signed.imag.abs().max() == 0
    assert c4_coefficients(scores, 0.3, "c4_dephased").real.min() >= 0


def test_c4_output_can_leave_convex_hull_of_values():
    # Two keys with opposite complex phases cancel exactly: impossible for convex weights.
    coefficients = torch.tensor([[1.0 + 0j, -1.0 + 0j]], dtype=torch.complex128) / 2 ** 0.5
    values = torch.tensor([[1.0, 0.5], [1.0, 0.5]], dtype=torch.float64)
    torch.testing.assert_close(c4_mix(coefficients, values), torch.zeros(1, 2, dtype=torch.float64))


@pytest.mark.parametrize("variant", C4_VARIANTS)
def test_c4_double_precision_gradients(variant):
    scores = _scores(length=5, magnitude=1.0).requires_grad_(True)
    values = torch.randn(2, 2, 5, 4, dtype=torch.float64, requires_grad=True)
    dt = torch.tensor(0.2, dtype=torch.float64, requires_grad=True)
    assert gradcheck(lambda s, v, t: c4_mix(c4_coefficients(s, t, variant), v), (scores, values, dt), eps=1e-6, atol=1e-5)


def test_all_variants_share_initialisation_and_nearly_equal_parameter_counts():
    models = {}
    for variant in ALL_VARIANTS:
        torch.manual_seed(7)
        models[variant] = ProbeEncoder(12, 17, 2, variant)
    base = models["softmax"]
    base_count = sum(p.numel() for p in base.parameters())
    for variant, model in models.items():
        extra = 2 if variant == "c3" else 0  # one dephasing scalar per head
        assert sum(p.numel() for p in model.parameters()) == base_count + extra, variant
        for name, tensor in model.state_dict().items():
            if name in base.state_dict():
                assert torch.equal(tensor, base.state_dict()[name]), (variant, name)
        tokens = torch.randint(0, 12, (3, 17))
        assert torch.isfinite(model(tokens)).all(), variant


def test_dt_init_is_respected():
    attention = QuantumMultiheadAttention(16, 2, "c4", dt_init=0.25)
    torch.testing.assert_close(attention.effective_dt(), torch.full((2,), 0.25))
    torch.testing.assert_close(QuantumMultiheadAttention(16, 2, "c3").effective_lambda(), torch.full((2,), 0.5))
