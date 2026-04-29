"""Quark Foot+Koide test (HYPOTHESIS Step 10a)."""

from math import isclose

from dinos import quarks_foot_test as qft


# -----------------------------------------------------------------------------
# Sector Koide values
# -----------------------------------------------------------------------------

def test_up_sector_koide_q():
    """Q for up-type quarks ~ 1.18 (NOT 3/2)."""
    q = qft.koide_for_up_sector()
    assert isclose(q, 1.178, abs_tol=0.01), f"Q_up = {q}"
    # Crucially, NOT close to lepton 3/2.
    assert abs(q - 1.5) > 0.2


def test_down_sector_koide_q():
    """Q for down-type quarks ~ 1.37 (NOT 3/2)."""
    q = qft.koide_for_down_sector()
    assert isclose(q, 1.367, abs_tol=0.01), f"Q_down = {q}"
    assert abs(q - 1.5) > 0.1


def test_pair_sums_koide_not_three_halves():
    """Q for paired (m_1+m_1', m_2+m_2', m_3+m_3') ~ 1.19 — also not 3/2."""
    q = qft.koide_for_pair_sums()
    assert abs(q - 1.5) > 0.1, f"Q_pair = {q}, unexpectedly near 3/2"


# -----------------------------------------------------------------------------
# Implied b values
# -----------------------------------------------------------------------------

def test_b_from_koide_inverts_correctly():
    """Q = 3/(1 + b^2/2) => b = sqrt(6/Q - 2)."""
    q = 1.5
    b = qft.b_from_koide_q(q)
    assert isclose(b, qft.LEPTON_FOOT_B, rel_tol=1e-12)


def test_quark_b_values_differ_from_lepton():
    """Both quark sectors yield b values different from lepton sqrt(2)."""
    report = qft.quark_koide_report()
    assert not report.matches_lepton_template, (
        f"Quark sectors unexpectedly match lepton template: {report}"
    )
    # Up b ~ 1.76, lepton b = 1.414
    assert abs(report.up_b - report.lepton_b) > 0.2
    # Down b ~ 1.55, lepton b = 1.414
    assert abs(report.down_b - report.lepton_b) > 0.05


# -----------------------------------------------------------------------------
# Edge cases
# -----------------------------------------------------------------------------

def test_b_from_q_rejects_invalid_q():
    """b_from_koide_q rejects Q outside (0, 3]."""
    import pytest
    with pytest.raises(ValueError):
        qft.b_from_koide_q(0)
    with pytest.raises(ValueError):
        qft.b_from_koide_q(4)


def test_charges_are_correctly_assigned():
    """Up-type charge = +2/3, down-type = -1/3."""
    for q_name in ("u", "c", "t"):
        assert qft.QUARK_CHARGES[q_name] == 2.0 / 3.0
    for q_name in ("d", "s", "b"):
        assert qft.QUARK_CHARGES[q_name] == -1.0 / 3.0
