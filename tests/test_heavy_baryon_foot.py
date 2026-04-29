"""Heavy baryon Foot tests (HYPOTHESIS Step 35)."""

from dinos import heavy_baryon_foot as hbf


def test_xi_bottom_chain_fits_within_0pt1_pct():
    """(Xi_b, Xi_bb, Omega_bbb) is the tightest metallic fit in the atlas."""
    fit = hbf.heavy_baryon_fit("Xi_bottom_chain")
    assert fit.rel_b_error_pct < 0.1


def test_doubly_heavy_xi_within_1_pct():
    """(Xi_cc, Xi_cb, Xi_bb) fits 1/(golden^2*plastic) within 1%."""
    fit = hbf.heavy_baryon_fit("doubly-heavy_Xi")
    assert fit.rel_b_error_pct < 1.0


def test_triply_heavy_omega_within_0pt5_pct():
    """(Omega_ccc, Omega_ccb, Omega_bbb) at 1/supergolden^3 within 0.5%."""
    fit = hbf.heavy_baryon_fit("triply-heavy_Omega")
    assert fit.rel_b_error_pct < 0.5


def test_xi_bb_predicted_within_1_pct():
    """Xi_bb predicted from (Xi_cc, Xi_cb) within 1% of lattice."""
    p = hbf.predict_xi_bb_from_xi_cc_and_xi_cb()
    assert p.rel_error_pct < 1.0


def test_omega_bbb_predicted_within_2_pct():
    """Omega_bbb predicted from (Xi_b, Xi_bb)."""
    p = hbf.predict_omega_bbb_from_xi_b_and_xi_bb()
    assert p.rel_error_pct < 2.0


def test_lambda_b_predicted_within_1_pct():
    """Lambda_b predicted from (Lambda, Lambda_c) within 1%."""
    p = hbf.predict_lambda_b_from_lambda_and_lambda_c()
    assert p.rel_error_pct < 1.0


def test_six_heavy_baryon_fits_exist():
    fits = hbf.all_heavy_baryon_fits()
    assert len(fits) == 6
    for f in fits:
        assert f.rel_b_error_pct < 2.0
