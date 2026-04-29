"""Polar excitations test (HYPOTHESIS.md Step 4).

Verifies the generalised polar shift Δ_polar(n_θ, m_j) = (n_θ+½)(2|m_j|+n_θ+½)
extends Step 2's ground-state shift (m_j + ¼) to arbitrary polar
excitations, recovering Dirac |k|² for every (n_θ, m_j).
"""

import numpy as np
import pytest

from dinos import polar_strip, spectrum


# -----------------------------------------------------------------------------
# Reduction to Step 2's ground state
# -----------------------------------------------------------------------------

def test_polar_shift_at_n_theta_zero_matches_spectrum_module():
    """At n_θ = 0, generalised shift must equal Step 2's m_j + ¼."""
    for n_phi in range(6):
        m_j = n_phi + 0.5
        gen = polar_strip.polar_shift_generalised(0, m_j)
        old = spectrum.polar_shift(m_j)
        assert gen == old, f"mismatch at m_j={m_j}: gen={gen}, old={old}"


# -----------------------------------------------------------------------------
# Closed-form algebraic identity: m_j² + Δ_polar = |k|²
# -----------------------------------------------------------------------------

def test_total_eigenvalue_equals_k_squared_at_continuum_m_j_squared():
    """For exact azimuthal m_j², adding Δ_polar(n_θ, m_j) gives |k|²."""
    for n_phi in range(5):
        m_j = n_phi + 0.5
        for n_theta in range(5):
            total = polar_strip.total_eigenvalue_from_mobius(
                mobius_azimuthal=m_j ** 2,
                n_theta=n_theta, m_j=m_j,
            )
            expected = polar_strip.dirac_k_squared(n_theta, m_j)
            assert total == expected, (
                f"(n_θ={n_theta}, m_j={m_j}): total={total}, expected={expected}"
            )


def test_dirac_k_squared_matches_geodesic_module():
    """Cross-check: |k|² from polar_strip ↔ |k|² from dinos.geodesic
    for ground-state polar (n_θ = 0) and various n_φ."""
    from dinos import geodesic
    for n_phi in range(6):
        for n_theta in range(4):
            m_j = n_phi + 0.5
            k_from_polar = polar_strip.dirac_k_squared(n_theta, m_j)
            labels = geodesic.geodesic_to_dirac(n_phi=n_phi, n_theta=n_theta)
            k_from_geodesic = float(labels.k_abs ** 2)
            assert k_from_polar == k_from_geodesic, (
                f"(n_φ={n_phi}, n_θ={n_theta}): polar={k_from_polar}, "
                f"geodesic={k_from_geodesic}"
            )


# -----------------------------------------------------------------------------
# End-to-end: numerical Möbius spectrum + polar shift = Dirac |k|²
# -----------------------------------------------------------------------------

def test_numerical_mobius_plus_polar_shift_recovers_full_dirac_ladder():
    """For each (n_θ, n_φ) up to (3, 3), take the numerical Möbius
    eigenvalue and add the generalised polar shift; verify the result
    matches Dirac |k|² to discretisation accuracy."""
    N = 256
    n_max = 3
    azimuthal_eigs = spectrum.lowest_distinct_mobius_eigenvalues(N, n_max)
    # Each azimuthal_eigs[n_phi] ≈ (n_phi + ½)² = m_j²
    for n_phi in range(n_max + 1):
        m_j = n_phi + 0.5
        for n_theta in range(n_max + 1):
            total = polar_strip.total_eigenvalue_from_mobius(
                mobius_azimuthal=azimuthal_eigs[n_phi],
                n_theta=n_theta, m_j=m_j,
            )
            expected = polar_strip.dirac_k_squared(n_theta, m_j)
            # O(1/N²) discretisation error in the azimuthal piece;
            # polar shift is exact analytical.
            np.testing.assert_allclose(
                total, expected, rtol=2e-2,
                err_msg=(
                    f"(n_φ={n_phi}, n_θ={n_theta}, m_j={m_j}): "
                    f"got {total}, expected {expected} = |k|²"
                ),
            )


# -----------------------------------------------------------------------------
# Ladders for inspection
# -----------------------------------------------------------------------------

def test_k_squared_ladder_is_perfect_squares_of_n_phi_plus_n_theta_plus_one():
    """The (n_θ, n_φ) ladder of |k|² should equal (n_φ + n_θ + 1)²."""
    n_max = 4
    ladder = polar_strip.k_squared_ladder(n_max, n_max)
    for nt in range(n_max + 1):
        for nphi in range(n_max + 1):
            assert ladder[nt, nphi] == (nphi + nt + 1) ** 2


def test_polar_shift_ladder_is_strictly_positive_and_increasing_in_n_theta():
    """Δ_polar > 0 for all (n_θ ≥ 0, m_j > 0), and increases with n_θ."""
    n_max = 4
    ladder = polar_strip.polar_shift_ladder(n_max, n_max)
    assert (ladder > 0).all()
    # Each column (fixed n_φ) increases monotonically in n_θ.
    for col in range(n_max + 1):
        col_vals = ladder[:, col]
        assert (np.diff(col_vals) > 0).all(), (
            f"polar shift not monotonic at n_φ={col}: {col_vals}"
        )


# -----------------------------------------------------------------------------
# Negative test: bad input
# -----------------------------------------------------------------------------

def test_negative_n_theta_rejected():
    with pytest.raises(ValueError):
        polar_strip.polar_shift_generalised(-1, 0.5)
