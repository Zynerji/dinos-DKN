"""Foot resonance atlas tests (HYPOTHESIS Step 16)."""

from math import isclose, sqrt, acos

from dinos import foot_resonance_atlas as fra


def test_three_resonances_in_atlas():
    """Atlas contains exactly 3 confirmed resonances."""
    atlas = fra.generate_atlas()
    assert atlas.n_confirmed == 3


def test_lepton_resonance_b_is_sqrt_2():
    r = fra.lepton_resonance()
    assert isclose(r.b_value, sqrt(2.0), rel_tol=1e-12)


def test_lepton_phi_close_to_two_ninths():
    r = fra.lepton_resonance()
    assert isclose(r.phi_rad, 2/9, abs_tol=1e-3)


def test_vector_meson_b_is_one_over_bronze_squared():
    r = fra.vector_meson_resonance()
    from dinos.metallic_invariant_sweep import BRONZE
    assert isclose(r.b_value, 1/(BRONZE**2), rel_tol=1e-12)


def test_vector_meson_phi_near_zero():
    """Vector meson phi is small, consistent with rho-omega degeneracy."""
    r = fra.vector_meson_resonance()
    assert r.phi_rad < 0.05  # < 3 degrees


def test_light_baryon_b_is_one_over_silver_copper():
    r = fra.light_baryon_resonance()
    from dinos.metallic_invariant_sweep import SILVER, COPPER
    assert isclose(r.b_value, 1/(SILVER*COPPER), rel_tol=1e-12)


def test_light_baryon_cos_phi_close_to_seven_eighths():
    """Largest cos value for light baryons is close to 7/8."""
    r = fra.light_baryon_resonance()
    largest_cos = max(r.cos_values)
    assert isclose(largest_cos, 7/8, abs_tol=0.005)


def test_all_resonances_satisfy_foot_consistency():
    """Sum cos^2 = 3/2 to high precision for all three."""
    for r in fra.all_confirmed_resonances():
        assert r.foot_consistency_residual < 1e-3, (
            f"{r.family}: residual {r.foot_consistency_residual}"
        )


def test_all_resonances_predict_masses_below_one_percent():
    """Predicted masses match empirical to better than 1%."""
    for r in fra.all_confirmed_resonances():
        assert r.max_mass_residual_pct < 1.0, (
            f"{r.family}: max residual {r.max_mass_residual_pct}%"
        )


def test_atlas_notes_mention_each_family():
    notes = fra.generate_atlas().notes
    for fam in ["leptons", "vector mesons", "baryons"]:
        assert fam in notes
