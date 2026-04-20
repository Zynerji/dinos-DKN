"""Test the Bohr–Sommerfeld / Dirac-index map (§7)."""

import numpy as np
import pytest

from dinos import geodesic as g


def test_ground_state_is_1s_half():
    """Corollary 7.6: (n_φ, n_θ) = (0, 0) ⇒ |k| = 1, j = ½."""
    gs = g.ground_state()
    assert gs.k_abs == 1
    assert gs.j == 0.5
    assert gs.m_j == 0.5


def test_maslov_indices_fixed():
    """μ_φ = μ_θ = 2 (paper Remark 7.3, App. E)."""
    assert g.MU_PHI == 2
    assert g.MU_THETA == 2


def test_bs_azimuthal_half_integer_shift():
    """L_z = ℏ(n_φ + ½)."""
    for n in range(5):
        assert g.bs_azimuthal(n) == n + 0.5


def test_separation_constants_at_fundamental_mode():
    """At ω = c/(2a) (⇒ a ω = ½ in natural units):
    λ = m_j / ω,  η/ℏ² = 2|m_j|(n_θ + ½)/ω²."""
    omega = 2.0  # arbitrary; tests the scaling
    lam, eta = g.separation_constants(n_phi=0, n_theta=0, omega=omega)
    assert lam == pytest.approx(0.5 / omega)
    assert eta == pytest.approx(2.0 * 0.5 * 0.5 / omega ** 2)


def test_spectrum_shape():
    """|k| labels are strictly positive integers for admissible states."""
    spec = g.spectrum_up_to(N_max=3)
    for s in spec:
        assert s.k_abs >= 1
        assert abs(s.m_j) <= s.j + 1e-9


def test_potentials_reduce_to_flat_space():
    """a = 0: Θ(θ) = η − λ² cot²θ; R(r) = (r² − aλ)² − (r² − 2Mr + Q²)(η + λ²)."""
    R = g.R_potential(1.0, lam=0.5, eta=1.0, a=0.0, M=0.5, Q=0.1)
    assert R == pytest.approx((1.0) ** 2 - (1.0 - 1.0 + 0.01) * (1.0 + 0.25))
    Theta = g.Theta_near_equator(0.1, lam=0.5, eta=1.0)
    assert Theta == pytest.approx(1.0 - 0.25 * 0.01)
