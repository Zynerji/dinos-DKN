"""Branch taxonomy tests (HYPOTHESIS Step 13b)."""

from math import isclose, sqrt

from dinos import branch_taxonomy as bt


# -----------------------------------------------------------------------------
# Lepton family fits
# -----------------------------------------------------------------------------

def test_charged_leptons_fit_at_b_sqrt_2():
    """Charged leptons live in the all-positive branch, Q = 3/2."""
    a = bt.lepton_family_analysis()
    assert a.matches_b_sqrt_2
    assert isclose(a.koide_q, 1.5, abs_tol=1e-3)


def test_neutrinos_fit_at_b_sqrt_2_different_branch():
    """Neutrinos at the same b, but in one-sign-flip branch."""
    a = bt.neutrino_family_analysis()
    assert a.matches_b_sqrt_2
    assert abs(a.koide_q - 1.5) > 0.3   # NOT in all-positive branch


# -----------------------------------------------------------------------------
# Quark family rejects
# -----------------------------------------------------------------------------

def test_up_quarks_rejected_at_b_sqrt_2():
    """Up-type quarks REJECT b = sqrt(2)."""
    a = bt.up_quark_analysis()
    assert not a.matches_b_sqrt_2
    # Implied b is around 1.76, not sqrt(2) = 1.414
    assert abs(a.implied_b_at_all_positive - sqrt(2.0)) > 0.2


def test_down_quarks_rejected_at_b_sqrt_2():
    """Down-type quarks REJECT b = sqrt(2)."""
    a = bt.down_quark_analysis()
    assert not a.matches_b_sqrt_2


def test_up_and_down_quarks_have_different_implied_b():
    """Up and down sectors have different implied b values — confirming
    they're not the same family in the Foot sense."""
    up = bt.up_quark_analysis()
    down = bt.down_quark_analysis()
    assert abs(up.implied_b_at_all_positive
               - down.implied_b_at_all_positive) > 0.1


# -----------------------------------------------------------------------------
# Framework scope
# -----------------------------------------------------------------------------

def test_framework_scope_includes_leptons():
    """The framework includes both charged leptons and neutrinos."""
    report = bt.framework_scope_report()
    families = [a.family for a in report.fits]
    assert "charged_leptons" in families
    assert "neutrinos" in families


def test_framework_scope_excludes_quarks():
    """The framework explicitly REJECTS both quark sectors."""
    report = bt.framework_scope_report()
    families = [a.family for a in report.rejects]
    assert "up_type_quarks" in families
    assert "down_type_quarks" in families


def test_framework_status_is_lepton_complete_quarks_separate():
    """The honest scope: complete for leptons, separate for quarks."""
    report = bt.framework_scope_report()
    assert "lepton" in report.framework_status
    assert "quark" in report.framework_status
