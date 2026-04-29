"""phi spectroscopy tests (HYPOTHESIS Step 23)."""

from math import isclose, pi

from dinos import foot_phi_spectroscopy as fps


def test_ten_phi_invariants_documented():
    """10 of 11 confirmed metallic resonances have simple phi matches
    (Steps 23 + 24)."""
    assert fps.n_phi_invariants() == 10


def test_d_star_j_psi_phi_is_four_thirty_fifths():
    """D*-J/psi phi = 4/35 (extraordinary 0.004% match)."""
    pi_inv = next(p for p in fps.PHI_INVARIANTS if p.family == "D_star_J_psi")
    assert isclose(pi_inv.simple_value, 4/35, rel_tol=1e-12)
    assert pi_inv.relative_error_pct < 0.01


def test_tensor_meson_phi_is_seventeen_thirtieths():
    """Tensor mesons phi = 17/30."""
    pi_inv = next(p for p in fps.PHI_INVARIANTS if p.family == "tensor_mesons")
    assert isclose(pi_inv.simple_value, 17/30, rel_tol=1e-12)


def test_lepton_phi_is_two_ninths():
    pi_inv = next(p for p in fps.PHI_INVARIANTS if p.family == "charged_leptons")
    assert pi_inv.simple_form == "2/9"
    assert isclose(pi_inv.simple_value, 2/9, rel_tol=1e-12)
    assert pi_inv.relative_error_pct < 0.01


def test_b_meson_phi_is_one_twelfth():
    pi_inv = next(p for p in fps.PHI_INVARIANTS if p.family == "B_mesons")
    assert pi_inv.simple_form == "1/12"
    assert isclose(pi_inv.simple_value, 1/12, rel_tol=1e-12)


def test_axial_and_scalar_both_pi_thirds():
    """Axial vector and scalar mesons both have phi ~ pi/3."""
    families = [p.family for p in fps.PHI_INVARIANTS]
    assert "axial_vector" in families
    assert "scalar_mesons" in families
    for p in fps.PHI_INVARIANTS:
        if p.family in ("axial_vector", "scalar_mesons"):
            assert isclose(p.simple_value, pi/3, rel_tol=1e-12)


def test_fraction_of_resonances_with_phi_match():
    """10 of 11 confirmed resonances have phi-invariants (~91%)."""
    frac = fps.fraction_phi_invariants()
    assert frac > 0.85


def test_all_phi_matches_below_two_percent():
    """Each documented phi match is within 2% of the simple form."""
    for p in fps.PHI_INVARIANTS:
        assert p.relative_error_pct < 2.0
