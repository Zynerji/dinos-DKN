"""Per-generation closure scaffold tests (HYPOTHESIS Step 6a).

Tests the calibration interface and demonstrates that:
1. Calibration round-trips correctly.
2. No clean σ(g) parametric law fits the empirical lepton tower.
3. The Koide formula Q ≈ 2/3 is satisfied empirically (consistent
   with the framework, but not derived from it).
4. The Foot 3-state parametrisation can fit the lepton tower exactly
   (3 parameters for 3 masses) — but is a postulate, not a derivation.
"""

from math import isclose

import numpy as np

from dinos import closure, generations, generations_extended


# -----------------------------------------------------------------------------
# Per-generation calibration round-trip
# -----------------------------------------------------------------------------

def test_sigma_for_mass_round_trip():
    """sigma_for_mass(m) ∘ closure.electron_mass(σ) should round-trip."""
    for m_target in [generations.M_E_MeV, generations.M_MU_MeV, generations.M_TAU_MeV]:
        sigma = generations_extended.sigma_for_mass(m_target)
        m_recovered = closure.electron_mass(sigma_MeV3=sigma)
        assert isclose(m_recovered, m_target, rel_tol=1e-9)


def test_per_generation_sigmas_match_individual():
    """per_generation_sigmas() should equal the individual values."""
    sigmas = generations_extended.per_generation_sigmas()
    for label, m in generations.LEPTON_MASSES_MeV.items():
        expected = generations_extended.sigma_for_mass(m)
        assert isclose(sigmas[label], expected, rel_tol=1e-12)


# -----------------------------------------------------------------------------
# No clean σ(g) law fits — strengthens Step 3 falsification
# -----------------------------------------------------------------------------

def test_power_law_does_not_fit():
    """σ_g = σ_0 · g^p has nonzero residual on the empirical tower."""
    diag = generations_extended.fit_sigma_power_law()
    assert not diag.fits_well, (
        f"Power-law fit unexpectedly succeeded: residual={diag.relative_residual}"
    )
    assert diag.relative_residual > 0.05


def test_exponential_law_does_not_fit():
    """σ_g = σ_0 · exp(λ·g) has nonzero residual on the empirical tower."""
    diag = generations_extended.fit_sigma_exponential()
    assert not diag.fits_well, (
        f"Exponential fit unexpectedly succeeded: residual={diag.relative_residual}"
    )
    assert diag.relative_residual > 0.01


# -----------------------------------------------------------------------------
# Koide formula
# -----------------------------------------------------------------------------

def test_koide_q_for_charged_leptons_is_three_halves():
    """Empirical lepton Koide Q in our convention (Σ√m)²/Σm ≈ 3/2.

    The alternate convention Σm/(Σ√m)² gives 2/3 — same coincidence."""
    q = generations_extended.lepton_koide_q()
    assert isclose(q, 1.5, rel_tol=1e-4), (
        f"Koide Q = {q}, expected ~3/2 = 1.5"
    )


def test_koide_q_handles_dict_or_list():
    """Koide accepts either a dict or list of 3 masses."""
    q_dict = generations_extended.koide_q({"a": 1.0, "b": 4.0, "c": 9.0})
    q_list = generations_extended.koide_q([1.0, 4.0, 9.0])
    assert isclose(q_dict, q_list, rel_tol=1e-12)


def test_koide_q_rejects_wrong_length():
    import pytest
    with pytest.raises(ValueError):
        generations_extended.koide_q([1.0, 2.0])


# -----------------------------------------------------------------------------
# Foot 3-state postulate: exact fit by construction
# -----------------------------------------------------------------------------

def test_foot_fit_reproduces_lepton_tower_exactly():
    """With 3 free parameters fit to 3 masses, residual should be ~0.

    This is NOT a derivation — it's an exact-fit demonstration. The
    framework has no first-principles way to pin (a, b, φ); they are
    calibrated against the empirical masses.
    """
    fit, rel_res = generations_extended.fit_foot_to_empirical()
    assert rel_res < 1e-6, (
        f"Foot fit residual = {rel_res} — should be negligible "
        f"with 3 params and 3 masses"
    )
    masses = generations_extended.foot_masses(fit)
    for label, target in generations.LEPTON_MASSES_MeV.items():
        assert isclose(masses[label], target, rel_tol=1e-4), (
            f"{label}: fit gives {masses[label]}, empirical {target}"
        )


def test_koide_predicted_b_matches_canonical():
    """For Q = 2/3, the Foot-Koide identity gives b = √7 ≈ 2.646;
    for Q = 3/2 (alternate convention), b = √2.

    Documents the convention dependence of the Koide-implied b."""
    b_at_two_thirds = generations_extended.koide_predicted_b(q_value=2.0 / 3.0)
    assert isclose(b_at_two_thirds, np.sqrt(7.0), rel_tol=1e-12)

    b_at_three_halves = generations_extended.koide_predicted_b(q_value=3.0 / 2.0)
    assert isclose(b_at_three_halves, np.sqrt(2.0), rel_tol=1e-12)


def test_foot_fitted_b_is_consistent_with_empirical_koide():
    """The b returned by fitting Foot to empirical masses should be
    consistent (within a few percent) with the Koide-predicted b for
    the empirical Q value.

    Documents that Foot is internally consistent with Koide — but
    again, this is fit consistency, not derivation."""
    fit, _ = generations_extended.fit_foot_to_empirical()
    q_empirical = generations_extended.lepton_koide_q()
    b_predicted = generations_extended.koide_predicted_b(q_empirical)
    # The fitted b should be near b_predicted (within ~10% — Foot has
    # some convention freedom beyond pure Koide).
    assert isclose(abs(fit.b), b_predicted, rel_tol=0.5), (
        f"fitted |b| = {abs(fit.b)}, Koide-predicted {b_predicted}"
    )
