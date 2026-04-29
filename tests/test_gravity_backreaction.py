"""Gravity backreaction tests (HYPOTHESIS Step 6c)."""

from math import isclose, pi

import pytest

from dinos import constants as C, gravity_backreaction as gb


# -----------------------------------------------------------------------------
# Higgs energy density
# -----------------------------------------------------------------------------

def test_higgs_energy_density_uses_lambda_quartic_v():
    """ρ_H = (λ/4) v⁴ — verify the formula directly."""
    v = 0.43
    lam = 0.129
    expected = 0.25 * lam * v ** 4
    actual = gb.higgs_potential_energy_density(v_bag_MeV=v, lambda_H=lam)
    assert isclose(actual, expected, rel_tol=1e-12)


def test_higgs_energy_density_default_DKN_value_is_small():
    """At canonical DKN (v ≈ 0.43 MeV, λ ≈ 0.129):
    ρ ≈ 0.25 · 0.129 · 0.43⁴ ≈ 1.1e-3 MeV⁴."""
    rho = gb.higgs_potential_energy_density()
    assert 5.0e-4 < rho < 5.0e-3, f"ρ_H = {rho}"


# -----------------------------------------------------------------------------
# Newtonian potential
# -----------------------------------------------------------------------------

def test_newtonian_potential_scales_as_rho_r_squared():
    """Φ_N = (4π/3)·ρ·r²/M_Pl² — verify scaling."""
    rho = 1.0e-3
    M_Pl = 1.0e22
    for r in [0.1, 1.0, 10.0]:
        phi = gb.newtonian_potential_at_radius(rho, r, M_Pl_MeV_value=M_Pl)
        expected = (4.0 * pi / 3.0) * rho * r * r / M_Pl ** 2
        assert isclose(phi, expected, rel_tol=1e-12)


def test_negative_radius_rejected():
    with pytest.raises(ValueError):
        gb.newtonian_potential_at_radius(rho_MeV4=1.0, radius_MeV_inv=-1.0)


# -----------------------------------------------------------------------------
# DKN backreaction
# -----------------------------------------------------------------------------

def test_dkn_backreaction_is_far_below_unity():
    """At canonical DKN parameters, δg/g should be < 10⁻³⁰.

    Quantitatively: ρ ~ 10⁻³ MeV⁴, r ~ 1 MeV⁻¹, M_Pl ~ 10²² MeV
    ⇒ δg ~ 10⁻³ · 1² / 10⁴⁴ ~ 10⁻⁴⁷."""
    report = gb.dkn_backreaction_at_electron()
    assert report.is_negligible, report.notes
    assert report.delta_g_over_g < 1.0e-30


def test_dkn_backreaction_report_fields_consistent():
    """The report's δg should match newtonian_potential applied to its ρ."""
    report = gb.dkn_backreaction_at_electron()
    expected_delta = gb.newtonian_potential_at_radius(
        report.rho_higgs_MeV4, report.Compton_radius_MeV_inv,
    )
    assert isclose(report.delta_g_over_g, expected_delta, rel_tol=1e-12)


# -----------------------------------------------------------------------------
# Critical radius (where backreaction would become O(1))
# -----------------------------------------------------------------------------

def test_critical_radius_for_dkn_is_macroscopic():
    """For the DKN Higgs density, the radius at which δg/g = 1 should
    be macroscopic (≫ Compton wavelength).

    r_crit = M_Pl · √(3/(4π·ρ)) ~ 10²² · √(3/4π·10⁻³) ~ 10²² · 15 ~ 10²³ MeV⁻¹
    which in meters is ~10²³ · 1.97e-13 m ~ 2e10 m — astronomical.
    """
    rho = gb.higgs_potential_energy_density()
    r_crit = gb.critical_radius_MeV_inv(rho)
    a_Compton = C.a_Compton_MeV_inv
    # r_crit must be at least 10²⁰× the electron Compton radius.
    assert r_crit / a_Compton > 1.0e20, (
        f"critical radius {r_crit} MeV⁻¹ vs Compton {a_Compton} MeV⁻¹ "
        f"— ratio {r_crit/a_Compton} should be ≫ 10²⁰"
    )


def test_critical_radius_rejects_zero_density():
    with pytest.raises(ValueError):
        gb.critical_radius_MeV_inv(rho_MeV4=0.0)


# -----------------------------------------------------------------------------
# Self-consistency: Step 1-5b bridge claims unaffected
# -----------------------------------------------------------------------------

def test_backreaction_is_safely_neglected_at_electron_scale():
    """The framework's use of a fixed Kerr-Newman background is
    quantitatively justified: δg/g at electron Compton scale is
    smaller than any observable correction.  This is a positive
    null result — gravity is consistently neglected, not arbitrarily."""
    report = gb.dkn_backreaction_at_electron()
    # Mass closure precision is ~0.02% (paper claim); δg/g must be
    # at least 25 orders below this to be safely neglected.
    closure_precision = 2.0e-4
    assert report.delta_g_over_g < closure_precision * 1.0e-25, (
        f"δg = {report.delta_g_over_g} vs closure precision {closure_precision} "
        f"— gap should be ≥ 25 orders for safe neglect"
    )
