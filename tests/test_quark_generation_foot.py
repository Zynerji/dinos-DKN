"""Quark generation Foot tests (HYPOTHESIS Step 34)."""

from dinos import quark_generation_foot as qgf


def test_heavy_quark_b_is_silver_minus_1_within_0pt5_percent():
    """The (c, b, t) implied b sits within 0.5% of silver - 1 = sqrt(2)."""
    fit = qgf.quark_foot_fit(("c", "b", "t"))
    assert fit.rel_b_error_pct < 0.5
    assert fit.best_metallic_label in ("silver-1", "sqrt(2)")


def test_down_type_b_is_sqrt_silver_within_0pt6_percent():
    """The (d, s, b) implied b sits within 0.6% of sqrt(silver)."""
    fit = qgf.quark_foot_fit(("d", "s", "b"))
    assert fit.rel_b_error_pct < 0.6
    assert "silver" in fit.best_metallic_label


def test_top_quark_predicted_within_3_percent():
    """Predict m_top from (m_c, m_b) at b = sqrt(2) within 3%
    (PDG c/b uncertainties dominate the band)."""
    p = qgf.top_quark_prediction(n_bootstrap=200)
    assert p.rel_error_pct < 3.0


def test_top_quark_bootstrap_median_below_3_percent():
    """Bootstrap median error for m_top stays below 3%."""
    p = qgf.top_quark_prediction(n_bootstrap=200)
    assert p.bootstrap_median_pct < 3.0


def test_all_quark_foot_fits_return_4():
    fits = qgf.all_quark_foot_fits()
    assert len(fits) == 4
    for f in fits:
        assert f.implied_b > 0
