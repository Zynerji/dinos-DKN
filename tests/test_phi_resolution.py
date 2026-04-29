"""Phi resolution tests (HYPOTHESIS Step 11 — the answer)."""

from math import isclose

from dinos import phi_resolution as phires


# -----------------------------------------------------------------------------
# Headline result: phi = 2/9 is COMPATIBLE within 1 sigma
# -----------------------------------------------------------------------------

def test_two_ninths_within_one_sigma_of_empirical():
    """The m_tau that makes phi = 2/9 exactly is within 1 sigma of
    the PDG central value."""
    m_tau_exact = phires.m_tau_required_for_exact_two_ninths()
    diff = m_tau_exact - phires.M_TAU_MeV
    sigma_disp = diff / phires.M_TAU_UNCERTAINTY_MeV
    # The displacement should be ~ 0.91 sigma.
    assert abs(sigma_disp) < 1.0, (
        f"phi = 2/9 requires m_tau shift of {sigma_disp:.2f} sigma "
        f"(expected ~ 0.91 sigma)"
    )


def test_framework_prediction_m_tau_at_phi_two_ninths():
    """If phi = 2/9 EXACTLY, the framework predicts m_tau ~ 1776.97 MeV."""
    m_tau_pred = phires.predict_m_tau_at_phi(2.0 / 9.0)
    # Should be close to 1776.98 MeV (consistency between m_e and m_mu).
    assert isclose(m_tau_pred, 1776.97, abs_tol=0.05)


def test_m_tau_required_for_two_ninths_specific_value():
    """The specific m_tau value should be ~ 1776.97 MeV."""
    m_tau_exact = phires.m_tau_required_for_exact_two_ninths()
    assert isclose(m_tau_exact, 1776.97, abs_tol=0.02), (
        f"got {m_tau_exact}, expected ~1776.97"
    )


# -----------------------------------------------------------------------------
# Continued-fraction signature
# -----------------------------------------------------------------------------

def test_cf_first_three_terms_match_two_ninths():
    """The CF of phi_empirical should start [0; 4, 2, ...] — exactly
    matching the CF of 2/9 = [0; 4, 2]."""
    phi = phires.compute_phi()
    cf = phires.continued_fraction_expansion(phi, max_terms=4)
    assert cf[0] == 0
    assert cf[1] == 4
    assert cf[2] == 2


def test_cf_term_after_two_ninths_is_huge():
    """The 4th CF term (the one AFTER 2/9 convergent) is very large
    (> 100), the signature of empirical noise on top of an exact
    simple rational."""
    phi = phires.compute_phi()
    cf = phires.continued_fraction_expansion(phi, max_terms=4)
    assert cf[3] > 100, (
        f"4th CF term = {cf[3]}, expected > 100 (signature of "
        f"phi = 2/9 + small empirical noise)"
    )


def test_two_ninths_is_a_cf_convergent():
    """2/9 should appear as the third convergent of phi_empirical."""
    phi = phires.compute_phi()
    cf = phires.continued_fraction_expansion(phi, max_terms=5)
    convergents = phires.cf_convergents(cf)
    third = convergents[2]   # (h_2, k_2)
    assert third == (2, 9), f"third convergent = {third}, expected (2, 9)"


# -----------------------------------------------------------------------------
# Empirical phi value
# -----------------------------------------------------------------------------

def test_empirical_phi_high_precision():
    """Empirical phi from PDG masses ~ 0.222270 rad."""
    phi = phires.compute_phi()
    assert isclose(phi, 0.222270, abs_tol=1e-5)


def test_phi_difference_from_two_ninths_is_small():
    """phi - 2/9 ~ 4.8e-5 rad."""
    phi = phires.compute_phi()
    diff = phi - 2.0 / 9.0
    assert 0 < diff < 1e-4, f"phi - 2/9 = {diff}"


# -----------------------------------------------------------------------------
# Verdict object
# -----------------------------------------------------------------------------

def test_generate_verdict_reports_compatibility():
    """The aggregated verdict should report COMPATIBLE within 2 sigma."""
    v = phires.generate_verdict()
    assert v.is_compatible, f"verdict reports NOT compatible: {v.notes}"
    # And the specific predictions:
    assert isclose(v.framework_prediction_m_tau_MeV, 1776.97, abs_tol=0.05)
    assert v.big_cf_term_after_two_ninths > 100
