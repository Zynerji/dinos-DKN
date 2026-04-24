"""Quantum Möbius temporal loop (paper §7 extension)."""

from math import isclose, pi

import numpy as np
import pytest

from dinos.quantum_temporal_loop import (
    QuantumMobiusLoop, SIGMA_Z, von_neumann_entropy,
)


def test_twist_unitary_full_period_flips_spin():
    from dinos.quantum_temporal_loop import _twist_unitary
    U = _twist_unitary(dt=2 * pi / 1.0, tau=1.0)
    # exp(−i π σ_z) = diag(−1, +1) up to global phase
    expected = np.diag([np.exp(-1j * pi), np.exp(1j * pi)])
    np.testing.assert_allclose(U, expected, atol=1e-12)


def test_quantum_loop_converges():
    # The forward and backward CPTP steps are not exact time-inverses at
    # finite γ (a deliberate O(1−γ) residual that models the irreversible
    # Higgs-wall dissipation), so the trace distance plateaus at
    # ∼(1−γ)²·‖ρ_target‖ rather than reaching machine precision.  We test
    # convergence against that plateau, which is ∼ 10⁻³ at γ = 0.99.
    loop = QuantumMobiusLoop(D=2, T=pi, K=32, alpha=0.7, tau=1.0,
                             damping=0.99, seed=1)
    result = loop.evolve(max_iter=400, epsilon=1e-3)
    assert result["converged"], (
        f"quantum loop did not converge: td={result['final_trace_distance']:.2e}"
    )
    rho0 = result["fixed_point_rho_0"]
    assert isclose(float(np.real(np.trace(rho0))), 1.0, abs_tol=1e-9)
    assert result["purity_at_t0"] > 0.5
    assert 0.0 <= result["entropy_at_t0"] <= np.log(2.0) + 1e-9


def test_quantum_loop_history_plateaus_at_dissipation_floor():
    # Picard symmetrisation immediately lands near the (1−γ)²-scale floor
    # and stays there.  We only assert that the plateau is below the
    # classical-initialisation gap.
    loop = QuantumMobiusLoop(D=2, T=pi, K=32, alpha=0.7, tau=1.0,
                             damping=0.99, seed=3)
    loop.evolve(max_iter=20, epsilon=0.0)
    h = np.asarray(loop.history)
    assert h[-1] < 1e-2, f"plateau too high: {h[-1]:.2e}"
    assert h[-1] == pytest.approx(h[-2], rel=0.1), "plateau not stable"


def test_trace_distance_zero_at_fixed_point():
    loop = QuantumMobiusLoop(D=2, T=pi, K=16, alpha=0.5, tau=1.0,
                             damping=0.99, seed=2)
    loop.evolve(max_iter=100, epsilon=1e-6)
    assert loop.trace_distance() < 1e-4


def test_von_neumann_entropy_bounds():
    # Pure state |0⟩⟨0| → S = 0
    rho_pure = np.array([[1, 0], [0, 0]], dtype=complex)
    assert isclose(von_neumann_entropy(rho_pure), 0.0, abs_tol=1e-10)
    # Maximally mixed qubit → S = log 2
    rho_mix = 0.5 * np.eye(2, dtype=complex)
    assert isclose(von_neumann_entropy(rho_mix), np.log(2.0), rel_tol=1e-10)


def test_rejects_non_qubit():
    with pytest.raises(NotImplementedError):
        QuantumMobiusLoop(D=4)
