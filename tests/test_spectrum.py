"""Spectral correspondence tests (HYPOTHESIS.md §3 — Step 2).

Three layers, each falsifiable:

  2A. Möbius -D_s eigenvalues match the closed-form 2(1-cos((n+½)·2π/N))
      and converge to m_j² in the continuum limit (rescaled by (Δs)⁻²).

  2B. Adding the analytic polar shift Δ_polar(m_j) = m_j + ¼ recovers
      the full Dirac |k|² for n_θ = 0 — i.e. the missing piece between
      the Möbius azimuthal sector and the full Chandrasekhar–Page
      operator is *exactly* the spin-connection contribution from the
      polar 2-sphere.

  2C. The continuum-limit error scales as O(1/N²), confirming that the
      mismatch is purely from the discretisation, not from a structural
      gap in the bridge.
"""

import numpy as np
import pytest

from dinos import spectrum


# -----------------------------------------------------------------------------
# 2A — Möbius spectrum: closed form, numerical, and continuum limit
# -----------------------------------------------------------------------------

def test_mobius_closed_form_matches_numerical():
    """Closed-form -D_s eigenvalues must match those obtained by
    diagonalising the explicit :func:`mobius_laplacian` operator."""
    for N in (8, 16, 32, 64):
        a = spectrum.mobius_eigenvalues_closed_form(N)
        b = spectrum.mobius_eigenvalues_numerical(N)
        np.testing.assert_allclose(a, b, atol=1e-10, rtol=1e-10), N


def test_mobius_eigenvalues_pair_around_n_max():
    """Each eigenvalue level appears twice (n and N-1-n give the same
    cosine) — the ±m_j degeneracy of the spinor azimuthal sector."""
    N = 32
    eigs = spectrum.mobius_eigenvalues_closed_form(N)
    # Adjacent pairs in the sorted spectrum should be near-identical (up
    # to numerical noise) — except possibly the two extremes.
    diffs = np.diff(eigs)
    pair_gaps = diffs[::2]   # gap between paired levels
    # Most pair gaps should be < 1e-9 (true degeneracy)
    n_paired = int(np.sum(pair_gaps < 1e-9))
    assert n_paired >= N // 2 - 1, (
        f"only {n_paired}/{N//2} pairs degenerate; spectrum is not "
        f"behaving as ±m_j doublets"
    )


def test_mobius_continuum_limit_matches_m_j_squared():
    """At large N, the lowest distinct rescaled -D_s eigenvalues equal
    m_j² for m_j = ½, 3/2, 5/2, …"""
    N = 256
    n_max = 5
    eigs_distinct = spectrum.lowest_distinct_mobius_eigenvalues(N, n_max)
    expected = spectrum.cp_eigenvalues_azimuthal(n_max)
    # O(1/N²) discretisation error; we ask for 1% tolerance at N=256.
    np.testing.assert_allclose(
        eigs_distinct, expected, rtol=1e-2,
        err_msg=(
            f"continuum-limit -D_s spectrum {eigs_distinct} does not match "
            f"m_j² = {expected}"
        ),
    )


# -----------------------------------------------------------------------------
# 2B — Polar shift recovers full Dirac |k|²
# -----------------------------------------------------------------------------

def test_polar_corrected_matches_dirac_k_squared():
    """Adding Δ_polar(m_j) = m_j + ¼ to the Möbius azimuthal eigenvalue
    should give the full Dirac |k|² for the n_θ = 0 polar ground state.

    This *quantifies the gap* between the Möbius construction (a 1D
    spatial strip) and the full angular Dirac operator on the 2-sphere:
    the gap is exactly the spin-connection contribution, no more.
    """
    n_max = 5
    m_j = spectrum.m_j_values(n_max)
    azimuthal = spectrum.cp_eigenvalues_azimuthal(n_max)        # m_j²
    corrected = azimuthal + spectrum.polar_shift(m_j)            # + (m_j + ¼)
    expected = spectrum.cp_eigenvalues_full_polar_ground(n_max)  # |k|² = (n+1)²
    np.testing.assert_allclose(corrected, expected, atol=1e-12)


def test_polar_shift_applied_to_mobius_recovers_dirac():
    """End-to-end: take the *numerical* Möbius spectrum, apply the polar
    shift, and recover Dirac |k|² to discretisation accuracy."""
    N = 256
    n_max = 5
    azimuthal_numerical = spectrum.lowest_distinct_mobius_eigenvalues(N, n_max)
    m_j_numerical = np.sqrt(azimuthal_numerical)
    corrected = azimuthal_numerical + spectrum.polar_shift(m_j_numerical)
    expected = spectrum.cp_eigenvalues_full_polar_ground(n_max)
    np.testing.assert_allclose(
        corrected, expected, rtol=2e-2,
        err_msg=(
            f"polar-corrected Möbius spectrum {corrected} ≠ Dirac |k|² "
            f"{expected}"
        ),
    )


# -----------------------------------------------------------------------------
# 2C — Discretisation error scales as O(1/N²)
# -----------------------------------------------------------------------------

def test_continuum_convergence_rate():
    """Error in the lowest eigenvalue (m_j² = ¼) must scale as O(1/N²)."""
    Ns = [16, 32, 64, 128, 256]
    errors = []
    for N in Ns:
        eig0 = spectrum.lowest_distinct_mobius_eigenvalues(N, 0)[0]
        errors.append(abs(eig0 - 0.25))
    errors = np.array(errors)
    # The ratio of successive errors should approach 4 (since N doubles
    # each time and error scales as N⁻²).
    ratios = errors[:-1] / errors[1:]
    # Expect each ratio in [3.5, 4.5] for clean O(1/N²).
    for i, r in enumerate(ratios):
        assert 3.5 < r < 4.5, (
            f"convergence ratio {r:.3f} at step {i} (N={Ns[i]}→{Ns[i+1]}) "
            f"is not consistent with O(1/N²) scaling; errors={errors}"
        )


def test_continuum_convergence_log_log_slope():
    """Direct log-log slope: log(error) vs log(N) should give -2 ± 0.1
    for clean O(1/N²) convergence.  More compact than the ratios test
    and gives a single defensible number."""
    Ns = np.array([16, 32, 64, 128, 256])
    errors = np.array([
        abs(spectrum.lowest_distinct_mobius_eigenvalues(N, 0)[0] - 0.25)
        for N in Ns
    ])
    slope, _ = np.polyfit(np.log(Ns), np.log(errors), 1)
    assert -2.1 < slope < -1.9, (
        f"log-log slope = {slope:.4f}; expected -2 for O(1/N²). "
        f"Errors: {errors}"
    )


# -----------------------------------------------------------------------------
# Sanity: m_j → |k| relationship is consistent with dinos.geodesic
# -----------------------------------------------------------------------------

def test_dirac_k_from_geodesic_module_matches_polar_correction():
    """For each ground-state (n_θ=0, n_φ) mode, the |k| produced by
    :func:`dinos.geodesic.geodesic_to_dirac` must equal m_j + ½ where
    m_j = n_φ + ½."""
    from dinos import geodesic
    for n_phi in range(6):
        labels = geodesic.geodesic_to_dirac(n_phi=n_phi, n_theta=0)
        m_j = n_phi + 0.5
        assert labels.k_abs == int(m_j + 0.5), (
            f"n_phi={n_phi}: geodesic gives |k|={labels.k_abs}, "
            f"polar-shift formula gives m_j+½={m_j+0.5}"
        )
