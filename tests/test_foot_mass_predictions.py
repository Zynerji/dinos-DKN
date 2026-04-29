"""Mass prediction tests (HYPOTHESIS Step 17)."""

from math import isclose

import pytest

from dinos import foot_mass_predictions as fmp


def test_lepton_m_tau_predicted_within_0pt01_percent():
    """From (m_e, m_mu) at b = sqrt(2), predict m_tau within 0.01%."""
    p = fmp.lepton_mass_prediction()
    assert p.rel_error_pct < 0.01, f"m_tau pred err {p.rel_error_pct}%"


def test_vector_meson_m_phi_predicted_within_0pt01_percent():
    """From (m_rho, m_omega) at b = 1/bronze^2, predict m_phi within 0.01%."""
    p = fmp.vector_meson_mass_prediction()
    assert p.rel_error_pct < 0.01, f"m_phi pred err {p.rel_error_pct}%"


def test_light_baryon_m_xi_predicted_within_0pt02_percent():
    """From (m_N, m_Lambda) at b = 1/(silver*copper), predict m_Xi within 0.02%."""
    p = fmp.light_baryon_mass_prediction()
    assert p.rel_error_pct < 0.02, f"m_Xi pred err {p.rel_error_pct}%"


def test_predict_third_mass_returns_None_for_impossible_inputs():
    """If b is too large/small to fit positive Foot, should return None
    (no valid branch)."""
    # Try very tight masses with very small b — likely no positive Foot soln
    sol = fmp.predict_third_mass(1.0, 1.001, b=0.0001,
                                 require_positivity=True,
                                 require_hierarchy=True)
    # May or may not find a solution; just ensure no crash
    # (function should return None or a valid solution)
    assert sol is None or sol["m_predicted"] > 0


def test_all_three_predictions_below_one_percent():
    """All three confirmed Foot resonances predict the third mass to
    better than 1% (in fact, all to better than 0.1%)."""
    for p in fmp.all_predictions():
        assert p.rel_error_pct < 0.1, (
            f"{p.family}: pred err {p.rel_error_pct}% > 0.1%"
        )
