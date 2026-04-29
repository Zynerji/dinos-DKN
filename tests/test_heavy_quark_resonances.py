"""Heavy quark Foot resonance tests (HYPOTHESIS Step 18)."""

from math import isclose

from dinos import heavy_quark_resonances as hqr
from dinos import metallic_invariant_sweep as mis


def test_four_heavy_quark_resonances():
    """4 heavy quark triplets are documented."""
    assert len(hqr.HEAVY_QUARK_RESONANCES) == 4


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


def test_atlas_returns_four_resonances():
    """Atlas function returns 4 FootResonance objects."""
    atlas = hqr.heavy_quark_resonance_atlas()
    assert len(atlas) == 4


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
