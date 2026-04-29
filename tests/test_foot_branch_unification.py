"""Foot branch unification tests (HYPOTHESIS Step 13)."""

from math import isclose, sqrt

from dinos import foot_branch_unification as fbu


# -----------------------------------------------------------------------------
# Universal b
# -----------------------------------------------------------------------------

def test_b_universal_is_sqrt_2():
    """The universal coupling shared across both fermion families."""
    assert isclose(fbu.B_UNIVERSAL, sqrt(2.0), rel_tol=1e-12)


# -----------------------------------------------------------------------------
# Lepton resonance
# -----------------------------------------------------------------------------

def test_lepton_resonance_in_all_positive_branch():
    """Charged-lepton sign pattern: (+, +, +) — all positive."""
    L = fbu.lepton_resonance()
    assert L.sign_pattern == (1, 1, 1)


def test_lepton_resonance_has_q_three_halves():
    """Charged-lepton Koide Q ≈ 3/2 (within 1e-4 of empirical)."""
    L = fbu.lepton_resonance()
    assert isclose(L.koide_q, 1.5, abs_tol=1e-3)


def test_lepton_phi_is_two_ninths():
    """Charged-lepton phi = 2/9."""
    L = fbu.lepton_resonance()
    assert isclose(L.phi_rad, 2.0 / 9.0, abs_tol=1e-12)


def test_lepton_scale_in_MeV():
    """Charged-lepton a ≈ 313.84 MeV."""
    L = fbu.lepton_resonance()
    assert isclose(L.a_MeV_or_eV, 313.84, abs_tol=0.5)
    assert L.a_unit == "MeV"


# -----------------------------------------------------------------------------
# Neutrino resonance
# -----------------------------------------------------------------------------

def test_neutrino_resonance_in_one_sign_flip_branch():
    """Neutrino sign pattern has exactly ONE negative."""
    nu = fbu.neutrino_resonance()
    n_neg = sum(1 for s in nu.sign_pattern if s < 0)
    assert n_neg == 1


def test_neutrino_q_is_not_three_halves():
    """Neutrinos Q != 3/2 because of the sign flip (~ 1.90)."""
    nu = fbu.neutrino_resonance()
    assert abs(nu.koide_q - 1.5) > 0.3
    assert isclose(nu.koide_q, 1.9048, abs_tol=0.01)


def test_neutrino_phi_around_zero_pt_48():
    """Neutrino phi ≈ 0.477 rad."""
    nu = fbu.neutrino_resonance()
    assert isclose(nu.phi_rad, 0.4768, abs_tol=0.005)


def test_neutrino_scale_in_eV():
    """Neutrino a ≈ 9.87e-3 eV."""
    nu = fbu.neutrino_resonance()
    assert isclose(nu.a_MeV_or_eV, 9.87e-3, rel_tol=1e-2)
    assert nu.a_unit == "eV"


# -----------------------------------------------------------------------------
# Unification report
# -----------------------------------------------------------------------------

def test_scale_ratio_is_about_3e10():
    """a_L (in eV) / a_nu (in eV) ≈ 3 × 10^10. NOT derived; just
    the empirical mass-scale separation between leptons and neutrinos."""
    report = fbu.generate_unification_report()
    assert 1e10 < report.scale_ratio_L_over_nu < 1e11


def test_both_resonances_share_b_universal():
    """The two resonances share the same b = sqrt(2). This is the
    central unification claim."""
    report = fbu.generate_unification_report()
    assert isclose(report.b_universal, sqrt(2.0), rel_tol=1e-12)


def test_resonances_have_different_signs_and_phis():
    """The two resonances are distinguished by sign pattern AND by phi."""
    report = fbu.generate_unification_report()
    L = report.leptons
    nu = report.neutrinos
    assert L.sign_pattern != nu.sign_pattern
    assert abs(L.phi_rad - nu.phi_rad) > 0.1
