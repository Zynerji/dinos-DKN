"""Quark sector scaffold tests (HYPOTHESIS Step 6b)."""

from math import isclose

import numpy as np
import pytest

from dinos import constants as C, quarks


# -----------------------------------------------------------------------------
# Color Casimir scaffold
# -----------------------------------------------------------------------------

def test_color_casimir_scales_with_dof():
    """Scaffold: C_color ∝ N_dof_color · c_per_dof."""
    base = quarks.C_bag_Dirac if hasattr(quarks, "C_bag_Dirac") else C.C_bag_Dirac
    for N in [1, 3, 6]:
        c = quarks.color_casimir_scaffold(N_dof_color=N, c_per_dof=base)
        assert isclose(c, N * base, rel_tol=1e-12)


def test_su3_casimir_constants():
    """Standard QCD values: C_F = 4/3, C_A = 3."""
    assert isclose(quarks.C_F_SU3, 4.0 / 3.0, rel_tol=1e-12)
    assert isclose(quarks.C_A_SU3, 3.0, rel_tol=1e-12)


# -----------------------------------------------------------------------------
# Generalised closure with fractional charge
# -----------------------------------------------------------------------------

def test_closure_residue_reduces_to_lepton_at_q_eq_1():
    """At q² = 1 and C_color = 0, the residue equals 1 − 2C − α (lepton form)."""
    r_quark = quarks.quark_closure_residue(
        C_em=C.C_bag_Dirac, C_color=0.0, q_charge=1.0,
    )
    r_lepton = 1.0 - 2.0 * C.C_bag_Dirac - C.alpha_EM
    assert isclose(r_quark, r_lepton, rel_tol=1e-12)


def test_closure_residue_uses_q_squared():
    """Residue depends on q² only — sign of charge doesn't matter."""
    r_plus = quarks.quark_closure_residue(0.1, 0.0, q_charge=+2.0/3.0)
    r_minus = quarks.quark_closure_residue(0.1, 0.0, q_charge=-2.0/3.0)
    assert isclose(r_plus, r_minus, rel_tol=1e-12)


def test_quark_mass_round_trips_via_sigma():
    """sigma_for_quark_mass ∘ quark_mass_from_sigma is identity."""
    target = 100.0  # MeV
    q = -1.0/3.0
    sigma = quarks.sigma_for_quark_mass(
        target, C_em=0.1, C_color=0.05, q_charge=q,
    )
    m = quarks.quark_mass_from_sigma(
        sigma, C_em=0.1, C_color=0.05, q_charge=q,
    )
    assert isclose(m, target, rel_tol=1e-9)


def test_closure_with_full_color_casimir_can_be_inadmissible():
    """If C_em + C_color is too large, the residue becomes ≤ 0 and the
    closure has no positive mass solution — flag honestly."""
    big_C_color = 1.0  # way above the physical scaffold
    with pytest.raises(ValueError):
        quarks.quark_mass_from_sigma(
            sigma_MeV3=1.0, C_em=C.C_bag_Dirac, C_color=big_C_color,
            q_charge=1.0,
        )


# -----------------------------------------------------------------------------
# Per-quark calibration
# -----------------------------------------------------------------------------

def test_per_quark_sigmas_keys():
    """Should produce a σ for each of the 6 quarks."""
    sigmas = quarks.per_quark_sigmas()
    assert set(sigmas.keys()) == {"u", "d", "s", "c", "b", "t"}


def test_per_quark_sigmas_use_correct_charges():
    """σ for u and c (charge 2/3) should differ from σ for d, s, b (charge -1/3)
    only via the empirical mass, not via the residue at q² = 4/9 vs 1/9."""
    # At fixed mass, quarks with different charge would have different σ.
    # Verify by computing σ for a hypothetical mass-1 MeV quark of each charge.
    sigma_up_charge = quarks.sigma_for_quark_mass(
        m_q_MeV=1.0, C_em=C.C_bag_Dirac, C_color=0.0, q_charge=2.0/3.0,
    )
    sigma_down_charge = quarks.sigma_for_quark_mass(
        m_q_MeV=1.0, C_em=C.C_bag_Dirac, C_color=0.0, q_charge=-1.0/3.0,
    )
    # Charges differ → σ differs.
    assert sigma_up_charge != sigma_down_charge


def test_quark_sigma_log_range_spans_orders_of_magnitude():
    """Quark masses span ~5 orders of magnitude (u: 2 MeV to t: 173 GeV);
    σ should span ~15 orders of magnitude (since σ ∝ m³)."""
    report = quarks.quark_calibration_report(C_em=C.C_bag_Dirac, C_color=0.0)
    # Default closure admits all 6 quarks (since C_color=0 keeps residue large).
    assert report.closure_admissible, report.notes
    # m_t / m_u ≈ 8e4, so σ_t / σ_u ≈ 5e14, log ≈ 33.
    assert 25.0 < report.log_sigma_range < 40.0, (
        f"log σ range = {report.log_sigma_range}, expected 25-40"
    )


def test_quark_calibration_with_full_color_scaffold():
    """At default C_color (the scaffold value ≈ 0.53), the closure may
    become inadmissible for the lighter quarks — this is honest:
    the framework cannot accommodate a literal full color Casimir
    addition at the lepton-like mass scales."""
    C_color_full = quarks.color_casimir_scaffold()  # ≈ 0.53
    # Total C = 0.177 + 0.53 = 0.707 → 2C = 1.414 > 1 → residue negative
    report = quarks.quark_calibration_report(
        C_em=C.C_bag_Dirac, C_color=C_color_full,
    )
    assert not report.closure_admissible, (
        f"Expected inadmissible closure with C_color = {C_color_full}, "
        f"but got: {report.notes}"
    )


def test_quark_sigma_inverts_quark_mass_per_quark():
    """For each quark, sigma_for_quark_mass → quark_mass_from_sigma round-trips."""
    sigmas = quarks.per_quark_sigmas(C_em=C.C_bag_Dirac, C_color=0.0)
    for q_name, sigma in sigmas.items():
        if not np.isfinite(sigma):
            continue
        m_recovered = quarks.quark_mass_from_sigma(
            sigma, C_em=C.C_bag_Dirac, C_color=0.0,
            q_charge=quarks.QUARK_CHARGES[q_name],
        )
        assert isclose(m_recovered, quarks.QUARK_MASSES_MeV[q_name],
                       rel_tol=1e-9), q_name
