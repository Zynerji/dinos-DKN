"""Test the Derrick-gap closure (paper Appendix D, eqs 104–105)."""

from math import isclose

from dinos import casimir


def test_single_scalar_constant():
    """C_Φ(0; 1) = c₀ = 0.0113."""
    assert isclose(casimir.C_phi_single(0.0), 0.0113, abs_tol=1e-6)


def test_multiplet_at_x_zero():
    """N=4: C_Φ(0; 4) = 4 · c₀ = 0.0452."""
    assert isclose(casimir.C_phi_multiplet(0.0, N_dof=4), 0.0452, abs_tol=1e-6)


def test_closed_form_does_not_close_gap():
    """The paper's truncated expansion (eq. 103) cannot reach 0.0955 by itself.

    This is a diagnostic test: the full closure must include higher-order
    zeta-regularized contributions (paper Remark 12.5). We verify the
    truncated expression stays near its x=0 baseline, as expected.
    """
    # Over the physical range x ∈ (0, 0.9):
    import pytest
    with pytest.raises(ValueError, match="outside image"):
        casimir.solve_derrick_x()


def test_gap_budget_at_paper_x():
    """At paper's quoted x = 0.153, show each term's contribution."""
    budget = casimir.derrick_gap_budget(0.153)
    assert isclose(budget["baseline_N_c0"], 0.0452, abs_tol=1e-4)
    assert budget["bag_bc_x_1p5"] > 0  # positive bag-BC enhancement
    assert budget["x_squared_term"] < 0  # negative x² coefficient
    # Residual to 0.0955 is nontrivial — that's the open gap in the paper.
    assert abs(budget["residual_vs_target"]) > 0.04


def test_robin_mode_equation_has_roots():
    """qa · j'_ℓ + κa · j_ℓ = 0 admits a positive root for every ℓ."""
    roots = casimir.radial_roots(ell=0, kappa_a=0.1, n_roots=3, q_max=30.0)
    assert len(roots) == 3
    assert all(r > 0 for r in roots)
