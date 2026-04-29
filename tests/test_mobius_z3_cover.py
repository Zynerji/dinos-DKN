"""Three-fold Möbius cover tests (HYPOTHESIS Step 9b)."""

from math import isclose, pi

import numpy as np
import pytest

from dinos import mobius_z3_cover as mz3


# -----------------------------------------------------------------------------
# OMEGA cube root of unity
# -----------------------------------------------------------------------------

def test_omega_is_primitive_cube_root_of_unity():
    """OMEGA^3 = 1 and OMEGA != 1."""
    assert isclose(abs(mz3.OMEGA ** 3 - 1.0), 0.0, abs_tol=1e-12)
    assert abs(mz3.OMEGA - 1.0) > 0.5
    # OMEGA + OMEGA^2 + 1 = 0 (sum of cube roots of unity)
    s = mz3.OMEGA + mz3.OMEGA ** 2 + 1.0
    assert isclose(abs(s), 0.0, abs_tol=1e-12)


def test_omega_bar_is_complex_conjugate():
    """OMEGA_BAR = conj(OMEGA)."""
    assert isclose(abs(mz3.OMEGA_BAR - np.conjugate(mz3.OMEGA)),
                   0.0, abs_tol=1e-12)


# -----------------------------------------------------------------------------
# Z_3 Laplacian basics
# -----------------------------------------------------------------------------

def test_z3_laplacian_returns_complex_for_complex_input():
    """The Z_3 Laplacian operates on complex fields (unlike Z_2)."""
    psi = np.exp(1j * np.linspace(0, 2 * pi, 8, endpoint=False))
    out = mz3.z3_mobius_laplacian(psi)
    assert out.dtype == complex


def test_z3_laplacian_seam_corrections_use_omega():
    """At the seam, forward[N-1] = OMEGA * psi[0]."""
    N = 4
    psi = np.array([1.0, 0.0, 0.0, 0.0], dtype=complex)
    # Compute manually: forward = roll(-1) so forward[3] = psi[0] then
    # corrected to OMEGA*psi[0]; backward = roll(+1) so backward[0] = psi[3] = 0
    # then corrected to conj(OMEGA)*psi[3] = 0.
    out = mz3.z3_mobius_laplacian(psi)
    # Position 3: forward[3]=OMEGA*1=OMEGA, backward[3]=psi[2]=0, -2*psi[3]=0
    # so out[3] = OMEGA + 0 - 0 = OMEGA
    assert isclose(abs(out[3] - mz3.OMEGA), 0.0, abs_tol=1e-12)


# -----------------------------------------------------------------------------
# Closed-form vs numerical
# -----------------------------------------------------------------------------

def test_closed_form_branches_have_correct_continuum_limits():
    """In the continuum limit (large N, rescaled by (N/2pi)^2), branch
    b eigenvalues converge to (n + b/3)^2."""
    N = 256
    for branch in (0, 1, 2):
        eigs = mz3.z3_mobius_eigenvalues_rescaled(N, branch=branch)
        eigs_sorted = np.sort(eigs)
        for n in range(4):
            target = (n + branch / 3.0) ** 2
            # find closest eigenvalue
            idx = np.argmin(np.abs(eigs_sorted - target))
            assert isclose(eigs_sorted[idx], target, rel_tol=2e-2,
                           abs_tol=1e-2), (
                f"branch={branch}, n={n}: expected {target}, "
                f"closest eig = {eigs_sorted[idx]}"
            )


def test_branch_0_recovers_periodic_spectrum():
    """Branch 0 (Z_3-trivial sector) recovers the periodic-Laplacian
    spectrum 2(1 - cos(2*pi*n/N)), with eigenvalue 0 included."""
    N = 64
    eigs = mz3.z3_mobius_eigenvalues_closed_form(N, branch=0)
    assert isclose(float(np.min(eigs)), 0.0, abs_tol=1e-12)


def test_branches_1_and_2_have_same_spectrum_via_conjugation():
    """Branches 1 and 2 (twisted by OMEGA and OMEGA-bar) have
    eigenvalue sets related by n -> -n shift; both have the SAME
    minimum rescaled eigenvalue 1/9 (from (n + b/3)^2 minimised
    over integer n)."""
    N = 64
    for branch in (1, 2):
        eigs_raw = mz3.z3_mobius_eigenvalues_closed_form(N, branch=branch)
        # Always positive (no exact zero mode).
        assert float(np.min(eigs_raw)) > 0.0
        # Rescaled lowest is 1/9 (the optimal integer shift).
        eigs_rescaled = mz3.z3_mobius_eigenvalues_rescaled(N, branch=branch)
        assert isclose(float(np.min(eigs_rescaled)), 1.0 / 9.0,
                       rel_tol=2e-2), (
            f"branch={branch}: rescaled min = {np.min(eigs_rescaled)}, "
            f"expected 1/9"
        )
    # And branch 1 and branch 2 have IDENTICAL spectra.
    eigs_1 = np.sort(mz3.z3_mobius_eigenvalues_closed_form(N, branch=1))
    eigs_2 = np.sort(mz3.z3_mobius_eigenvalues_closed_form(N, branch=2))
    np.testing.assert_allclose(eigs_1, eigs_2, atol=1e-12)


# -----------------------------------------------------------------------------
# Triplet structure
# -----------------------------------------------------------------------------

def test_lowest_triplets_are_zero_one_ninth_four_ninths_in_continuum():
    """The lowest 3 distinct eigenvalues across all branches, rescaled,
    converge to {0, 1/9, 4/9} in the continuum."""
    N = 256
    triplets = mz3.lowest_distinct_triplets(N, n_triplets=3)
    rescaled = triplets * (N / (2.0 * pi)) ** 2
    expected = np.array([0.0, 1.0 / 9.0, 4.0 / 9.0])
    np.testing.assert_allclose(rescaled, expected, rtol=2e-2, atol=2e-3)


def test_triplet_square_roots_form_ladder_of_thirds():
    """sqrt of distinct eigenvalues gives the ladder {0, 1/3, 2/3, 1, 4/3, 5/3}."""
    N = 256
    triplets = mz3.lowest_distinct_triplets(N, n_triplets=6)
    rescaled = triplets * (N / (2.0 * pi)) ** 2
    sqrt_eigs = np.sqrt(rescaled)
    expected = np.array([0.0, 1.0 / 3.0, 2.0 / 3.0, 1.0, 4.0 / 3.0, 5.0 / 3.0])
    np.testing.assert_allclose(sqrt_eigs, expected, rtol=3e-2, atol=2e-3)


# -----------------------------------------------------------------------------
# Honest negative: Z_3 cover does NOT pin the lepton mixing angle
# -----------------------------------------------------------------------------

def test_z3_cover_does_not_pin_lepton_phi():
    """Z_3 cover provides a natural 3-fold spectrum but its eigenvalues
    are RATIONAL fractions, while the empirical Foot mixing angle phi
    is IRRATIONAL. So Z_3 cover by itself does NOT pin phi."""
    result = mz3.attempt_z3_to_foot_identification(N=256)
    assert not result.matches_lepton_phi, (
        "Z_3 cover unexpectedly matched the empirical lepton phi"
    )
    # The triplet eigenvalues should be near {0, 1/9, 4/9}
    np.testing.assert_allclose(
        result.triplet_eigenvalues,
        [0.0, 1.0 / 9.0, 4.0 / 9.0],
        rtol=5e-2, atol=2e-3,
    )


# -----------------------------------------------------------------------------
# Bad input
# -----------------------------------------------------------------------------

def test_invalid_branch_rejected():
    with pytest.raises(ValueError):
        mz3.z3_mobius_eigenvalues_closed_form(N=10, branch=5)


def test_too_small_N_rejected():
    with pytest.raises(ValueError):
        mz3.z3_mobius_eigenvalues_closed_form(N=1, branch=0)
