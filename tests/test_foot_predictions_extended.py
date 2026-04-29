"""Extended Foot mass predictions tests (HYPOTHESIS Step 33)."""

from dinos import foot_predictions_extended as fpe


def test_higgs_predicted_within_0pt2_percent():
    """Predict Higgs from (W, Z) at b = 1/(copper*plastic^2): ~125,222 MeV vs 125,100."""
    p = fpe.gauge_boson_higgs_prediction()
    assert p.relative_error_pct < 0.2, f"H pred err: {p.relative_error_pct}"


def test_bc_predicted_within_0pt01_percent():
    """Predict B_c from (B_0, B_s) at b = 1/copper^2: 6,274.54 vs 6,274.5."""
    p = fpe.b_meson_bc_prediction()
    assert p.relative_error_pct < 0.01


def test_chi_c_predicted_within_0pt01_percent():
    """Predict chi_c from (eta_c, J/psi): 3,414.86 vs 3,414.71."""
    p = fpe.charmonium_chi_c_prediction()
    assert p.relative_error_pct < 0.01


def test_all_extended_predictions_below_0pt2_percent():
    """All 6 extended predictions match empirical to better than 0.2%."""
    for p in fpe.all_extended_predictions():
        assert p.relative_error_pct < 0.2, (
            f"{p.family} -> {p.target}: {p.relative_error_pct}%"
        )
