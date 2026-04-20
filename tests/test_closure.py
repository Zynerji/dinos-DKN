"""Reproduce §14.2 numerical check."""

from math import isclose

import pytest

from dinos import closure, constants as C


def test_required_surface_tension_matches_paper():
    """Paper eq. 65: σ ≃ 2.74e-2 MeV³ for m_e = 0.511 MeV (paper rounds to 3 sig figs)."""
    sigma = closure.required_surface_tension()
    assert isclose(sigma, 2.74e-2, rel_tol=1.5e-2), f"σ = {sigma:.5e}"


def test_forward_closure_reproduces_m_e():
    """Round-trip: σ → m_e should recover 0.511 MeV."""
    sigma = closure.required_surface_tension(C.m_e_MeV)
    m_e = closure.electron_mass(sigma)
    assert isclose(m_e, C.m_e_MeV, rel_tol=1e-10)


def test_bag_vev_matches_paper():
    """Paper eq. 66: v_bag ≃ 0.43 MeV at λ_H = 0.13."""
    sigma = closure.required_surface_tension()
    v = closure.required_bag_vev(sigma, lambda_H=0.13)
    assert isclose(v, 0.43, rel_tol=5e-3), f"v_bag = {v:.4f}"


def test_mass_fractions_sum_to_unity():
    f = closure.mass_fractions()
    assert isclose(f.total, 1.0, abs_tol=1e-12)


def test_mass_fraction_table_14_2():
    """Paper Table 14.2 percentages."""
    f = closure.mass_fractions()
    assert isclose(f.higgs_wall,    C.FRACTION_HIGGS_WALL,    abs_tol=5e-4)
    assert isclose(f.dirac_casimir, C.FRACTION_DIRAC_CASIMIR, abs_tol=5e-4)
    assert isclose(f.em_self,       C.FRACTION_EM_SELF,       abs_tol=5e-5)


def test_full_closure_report():
    r = closure.full_closure()
    assert isclose(r.m_e_MeV, C.m_e_MeV, rel_tol=1e-10)
    assert 0.4 < r.v_bag_MeV < 0.5
    assert 1.9e-13 < r.a_m < 2.0e-13   # ≈ 1.93e-13 m (paper eq. 15)


def test_closure_rejects_impossible_input():
    # 2C + α > 1 → no positive root
    with pytest.raises(ValueError):
        closure.compton_radius(sigma_MeV3=1.0, C_bag=0.6, alpha=0.1)
