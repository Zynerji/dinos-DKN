"""Atlas discrimination tests (HYPOTHESIS Step 31)."""

from dinos import foot_atlas_discrimination as fad


def test_atlas_has_19_fragments():
    assert len(fad.ATLAS_19_MASSES) == 19


def test_implied_b_is_positive():
    """Every atlas fragment has positive implied b."""
    for masses in fad.ATLAS_19_MASSES.values():
        b = fad.implied_b(masses)
        assert b > 0


def test_metallic_significantly_beats_random_at_0pt05_pct():
    """At 0.05% tolerance, metallic should significantly outperform random."""
    results = fad.run_full_discrimination(n_random_seeds=30)
    r_05 = next(r for r in results if abs(r.tolerance_pct - 0.05) < 1e-9)
    # Metallic: ~8/19, random: ~0.4 on average → 18x significance
    assert r_05.metallic_fits >= 5
    assert r_05.significance_ratio >= 5.0


def test_metallic_overwhelmingly_significant_at_0pt03_pct():
    """At 0.03% tolerance, metallic structure is overwhelming."""
    results = fad.run_full_discrimination(n_random_seeds=30)
    r_03 = next(r for r in results if abs(r.tolerance_pct - 0.03) < 1e-9)
    assert r_03.significance_ratio >= 10.0
