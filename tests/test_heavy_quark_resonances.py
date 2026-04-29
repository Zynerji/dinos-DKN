"""Heavy quark Foot resonance tests (HYPOTHESIS Step 18)."""

from math import isclose

from dinos import heavy_quark_resonances as hqr
from dinos import metallic_invariant_sweep as mis


def test_eight_heavy_and_extended_hadron_resonances():
    """8 heavy/extended hadron triplets documented (Step 18 + Step 21)."""
    assert len(hqr.HEAVY_QUARK_RESONANCES) == 8


def test_charmonium_b_is_one_over_copper_silver_squared():
    """(eta_c, J/psi, chi_c) at b = 1/(copper * silver^2)."""
    info = hqr.HEAVY_QUARK_RESONANCES["charmonium (eta_c, J/psi, chi_c)"]
    expected = 1.0 / (mis.COPPER * mis.SILVER ** 2)
    assert isclose(info["b_value_factory"](), expected, rel_tol=1e-12)


def test_jpsi_upsilon_b_is_half_over_supergolden():
    """(J/psi, Upsilon(1S), Upsilon(2S)) at b = 1/(2*supergolden)."""
    info = hqr.HEAVY_QUARK_RESONANCES["(J/psi, Upsilon(1S), Upsilon(2S))"]
    expected = 1.0 / (2 * mis.SUPERGOLDEN)
    assert isclose(info["b_value_factory"](), expected, rel_tol=1e-12)


def test_atlas_returns_eight_resonances():
    """Atlas function returns 8 FootResonance objects."""
    atlas = hqr.heavy_quark_resonance_atlas()
    assert len(atlas) == 8


def test_b_meson_b_is_one_over_copper_squared():
    """(B_0, B_s, B_c) at b = 1/copper^2 — tightest match found (0.004%)."""
    info = hqr.HEAVY_QUARK_RESONANCES["(B_0, B_s, B_c)"]
    expected = 1.0 / (mis.COPPER ** 2)
    assert isclose(info["b_value_factory"](), expected, rel_tol=1e-12)


def test_tensor_meson_b_uses_plastic():
    """Tensor mesons triplet uses plastic ratio."""
    info = hqr.HEAVY_QUARK_RESONANCES["tensor (a_2, K_2*, f_2')"]
    expected = 1.0 / (mis.COPPER ** 2 * mis.PLASTIC)
    assert isclose(info["b_value_factory"](), expected, rel_tol=1e-12)


def test_axial_vector_b_uses_nickel():
    """Axial vector mesons use nickel — first appearance of nickel
    in the metallic Foot atlas."""
    info = hqr.HEAVY_QUARK_RESONANCES["axial (b_1, h_1, a_1)"]
    expected = 1.0 / (mis.BRONZE ** 2 * mis.NICKEL)
    assert isclose(info["b_value_factory"](), expected, rel_tol=1e-12)


def test_charmonium_resonance_consistency():
    """Charmonium triplet satisfies Foot consistency at metallic b."""
    atlas = hqr.heavy_quark_resonance_atlas()
    charmonium = next(r for r in atlas if "eta_c" in r.family)
    assert charmonium.foot_consistency_residual < 0.01


def test_charmonium_mass_residuals_below_one_percent():
    """Charmonium predictions match empirical to better than 1%."""
    atlas = hqr.heavy_quark_resonance_atlas()
    for r in atlas:
        assert r.max_mass_residual_pct < 1.0, (
            f"{r.family}: max residual {r.max_mass_residual_pct}%"
        )
