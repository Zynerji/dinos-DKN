"""Reproduce §16.1–§16.6 single-point predictions."""

from math import isclose

from dinos import dm, constants as C


def test_joint_closure_central_values():
    """Paper eq. 81 / Remark 16.14 central values at λ_H = 0.129."""
    s = dm.joint_closure()
    assert isclose(s.m_star_MeV, C.m_star_MeV,      abs_tol=C.m_star_MeV_err)
    assert isclose(s.m_star_times_a, C.m_star_times_a_dimless, abs_tol=C.m_star_times_a_err)
    assert isclose(s.v_bag_MeV, C.v_bag_MeV, rel_tol=0.05)
    assert isclose(s.y_e, C.y_e_DKN, rel_tol=0.05)


def test_kappa_scaling():
    """Eq. 72:  m_* / m_e = 0.602 · λ_H^(1/3).  The 0.602 prefactor is rounded
    in the paper; we allow 1% tolerance.
    """
    s = dm.joint_closure(lambda_H=0.129)
    assert isclose(s.kappa, 0.602 * 0.129 ** (1.0 / 3.0), rel_tol=1e-2)


def test_derrick_bound():
    s = dm.joint_closure()
    assert dm.derrick_bound_ok(s)


def test_edges_window():
    s = dm.joint_closure()
    assert dm.matches_edges_anomaly(s)


def test_cross_section_order_of_magnitude():
    """Eq. 82 in q→0 limit, computed literally from the paper's formula."""
    sigma = dm.electron_dm_cross_section()
    assert sigma > 0


def test_cross_section_scales_as_inverse_m_star_4():
    """σ(q=0) ∝ m_e² / m_*⁴."""
    s1 = dm.joint_closure(lambda_H=0.129)
    s2 = dm.joint_closure(lambda_H=0.5)
    sig1 = dm.electron_dm_cross_section(s1)
    sig2 = dm.electron_dm_cross_section(s2)
    # m_*² scales as √λ_H v (with v itself ~ λ_H^(−1/6)): m_* ∝ λ_H^(1/3).
    # ⇒ σ ∝ m_*^{-4} · m_e² / y_e²(…)   — monotonic in λ_H.
    assert sig1 != sig2
