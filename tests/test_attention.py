import math

import pytest
import torch
from torch.autograd import gradcheck

from schrodinger.attention import MultiheadAttention, attention_from_scores

torch.set_num_threads(2)
torch.set_num_interop_threads(1)


def _inputs(length: int, magnitude: float, dtype=torch.float32):
    generator = torch.Generator().manual_seed(1000 + length + int(magnitude * 10))
    scores = torch.randn(2, 2, length, length, generator=generator, dtype=dtype) * magnitude
    values = torch.randn(2, 2, length, 3, generator=generator, dtype=dtype)
    phase = torch.randn(2, 2, length, length, generator=generator, dtype=dtype) * 0.2
    return scores, values, phase


@pytest.mark.parametrize("length", [4, 11, 15])
@pytest.mark.parametrize("magnitude", [0.1, 1.0, 3.0])
def test_exact_invariants_with_numeric_evidence(length, magnitude):
    scores, values, phase = _inputs(length, magnitude)
    output, probabilities, diagnostics = attention_from_scores(
        scores, values, phase, dt=0.11, mode="schrodinger", return_diagnostics=True
    )
    print(
        f"invariants length={length} magnitude={magnitude}: "
        f"H={diagnostics.max_hermiticity_error:.3e} "
        f"U={diagnostics.max_unitarity_error:.3e} P={diagnostics.max_probability_row_error:.3e}"
    )
    assert torch.isfinite(output).all()
    assert diagnostics.max_hermiticity_error <= 1e-6
    assert diagnostics.max_unitarity_error <= 2e-4
    assert diagnostics.max_probability_row_error <= 2e-4


def test_explicit_row_state_orientation_reference():
    scores = torch.tensor([[[[0.1, 0.8, -0.3], [-0.2, 0.4, 0.7], [0.9, -0.5, 0.2]]]])
    values = torch.tensor([[[[1.0], [2.0], [4.0]]]])
    phase = torch.tensor([[[[0.2, -0.1, 0.4], [0.3, 0.1, -0.2], [-0.5, 0.2, 0.6]]]])
    _, actual = attention_from_scores(scores, values, phase, dt=0.23, mode="schrodinger")
    h = 0.5 * (scores + scores.transpose(-2, -1)) / math.sqrt(3)
    unitary = torch.matrix_exp((-1j * 0.23 * h).to(torch.complex64))
    psi0 = torch.sqrt(torch.softmax(scores, -1)).to(torch.complex64) * torch.exp((1j * phase).to(torch.complex64))
    expected = (psi0 @ unitary.transpose(-2, -1)).abs().square()
    wrong_column_evolution = (unitary @ psi0).abs().square()
    print(f"orientation delta={(actual - wrong_column_evolution).abs().max().item():.3e}")
    torch.testing.assert_close(actual, expected, atol=2e-6, rtol=2e-5)
    assert not torch.allclose(actual, wrong_column_evolution, atol=1e-4, rtol=1e-4)


def test_dt_zero_recovers_softmax_probabilities_and_output():
    scores, values, phase = _inputs(11, 3.0)
    baseline_output, baseline_probabilities = attention_from_scores(scores, values, mode="softmax")
    exact_output, exact_probabilities = attention_from_scores(
        scores, values, phase, dt=0.0, mode="schrodinger"
    )
    print(f"dt0 P={(exact_probabilities-baseline_probabilities).abs().max().item():.3e} Y={(exact_output-baseline_output).abs().max().item():.3e}")
    torch.testing.assert_close(exact_probabilities, baseline_probabilities, atol=2e-6, rtol=2e-5)
    torch.testing.assert_close(exact_output, baseline_output, atol=2e-6, rtol=2e-5)


@pytest.mark.parametrize("length", [4, 11, 15])
@pytest.mark.parametrize("magnitude", [0.1, 1.0, 3.0])
def test_gradients_include_scores_values_phase_and_time(length, magnitude):
    scores, values, phase = _inputs(length, magnitude)
    scores.requires_grad_(); values.requires_grad_(); phase.requires_grad_()
    dt = torch.tensor(0.11, requires_grad=True)
    output, _ = attention_from_scores(scores, values, phase, dt, "schrodinger")
    output.square().mean().backward()
    for name, tensor in {"scores": scores, "values": values, "phase": phase, "dt": dt}.items():
        assert tensor.grad is not None and torch.isfinite(tensor.grad).all(), name


def test_double_precision_gradcheck():
    scores, values, phase = _inputs(3, 0.1, torch.float64)
    scores.requires_grad_(); values.requires_grad_(); phase.requires_grad_()
    dt = torch.tensor(0.07, dtype=torch.float64, requires_grad=True)
    def fn(s, v, p, t):
        return attention_from_scores(s, v, p, t, "schrodinger")[0]
    assert gradcheck(fn, (scores, values, phase, dt), eps=1e-6, atol=1e-5, rtol=1e-3)


def test_multihead_initialization_dt0_and_parameter_gradients():
    torch.manual_seed(7)
    softmax = MultiheadAttention(8, 2, "softmax")
    exact = MultiheadAttention(8, 2, "schrodinger")
    softmax_state = softmax.state_dict()
    exact.load_state_dict({name: value for name, value in softmax_state.items() if name in exact.state_dict()}, strict=False)
    inputs = torch.randn(2, 4, 8)
    softmax_output = softmax(inputs)
    exact_output, diagnostics = exact(inputs, dt_override=0.0, return_diagnostics=True)
    print(f"initial dt={diagnostics.effective_dt.tolist()} gamma={diagnostics.effective_gamma.tolist()}")
    torch.testing.assert_close(exact_output, softmax_output, atol=2e-6, rtol=2e-5)
    torch.testing.assert_close(exact.effective_dt(), torch.full((2,), 0.05), atol=1e-7, rtol=0)
    torch.testing.assert_close(exact.effective_gamma(), torch.full((2,), 0.1), atol=1e-7, rtol=0)
    exact(inputs).square().mean().backward()
    for parameter in exact.parameters():
        assert parameter.grad is not None and torch.isfinite(parameter.grad).all()


def test_fixed_tiny_optimization_smoke_decreases_loss():
    torch.manual_seed(42)
    module = MultiheadAttention(8, 2, "schrodinger")
    inputs = torch.randn(4, 4, 8)
    target = torch.randn(4, 4, 8)
    optimizer = torch.optim.Adam(module.parameters(), lr=0.02)
    losses = []
    for _ in range(30):
        optimizer.zero_grad()
        loss = (module(inputs) - target).square().mean()
        assert torch.isfinite(loss)
        loss.backward()
        optimizer.step()
        losses.append(loss.item())
    print(f"optimization initial={losses[0]:.6f} final={losses[-1]:.6f}")
    assert losses[-1] < losses[0]
    checkpoint = {name: value.detach().clone() for name, value in module.state_dict().items()}
    restored = MultiheadAttention(8, 2, "schrodinger")
    restored.load_state_dict(checkpoint)
    torch.testing.assert_close(restored(inputs), module(inputs), atol=1e-6, rtol=0)
