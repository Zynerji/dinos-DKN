"""Sector-level structural tests (HYPOTHESIS Step 36)."""

from math import sqrt

from dinos import foot_sector_structure as fss


def test_charged_leptons_saturate_silver_bound():
    """Charged leptons sit within 0.01% of b = sqrt(2) Koide bound."""
    statuses = fss.fermion_generation_status()
    leptons = next(s for s in statuses if "charged_leptons" in s.triplet_label)
    assert abs(leptons.distance_from_silver_pct) < 0.01
    assert leptons.branch == "positive"


def test_quarks_in_sign_flip_branch():
    """Up- and down-type quark generations exceed sqrt(2) Koide bound,
    placing them in the sign-flip branch."""
    statuses = fss.fermion_generation_status()
    up   = next(s for s in statuses if "up-type" in s.triplet_label)
    down = next(s for s in statuses if "down-type" in s.triplet_label)
    assert up.branch == "sign-flip"
    assert down.branch == "sign-flip"


def test_b_is_scale_invariant():
    """log(b) vs log(gm) should have R^2 < 0.1 across the atlas
    (b is essentially uncorrelated with mass scale)."""
    inv = fss.b_scale_invariance()
    assert inv.r_squared < 0.1
    assert inv.n_triplets >= 25


def test_metallic_factor_distribution_is_binary_biased():
    """Two-metallic-factor combinations dominate the canonical 19."""
    stats = fss.metallic_factor_stats()
    assert stats.n_factor_distribution.get(2, 0) >= stats.n_factor_distribution.get(1, 0)
    assert stats.n_factor_distribution.get(3, 0) <= 2
