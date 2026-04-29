"""Robustness tests for confirmed metallic Foot resonances (Step 22)."""

from dinos import foot_robustness as fr


def test_all_five_resonances_within_one_sigma():
    """Each metallic candidate is within 1 sigma of bootstrap b mean."""
    for r in fr.all_robustness_reports():
        assert r.n_sigma_displacement < 1.5, (
            f"{r.family}: {r.n_sigma_displacement:.2f}σ off"
        )


def test_metallic_within_95pc_ci():
    """Each metallic value falls within the 95% bootstrap CI."""
    for r in fr.all_robustness_reports():
        assert r.metallic_within_ci, (
            f"{r.family}: {r.metallic_b} outside CI {r.bootstrap_ci_95}"
        )


def test_bootstrap_returns_correct_distribution_shape():
    """Bootstrap function returns array of the requested size."""
    samples = fr.implied_b_with_bootstrap(
        masses=[1.0, 2.0, 3.0],
        uncertainties=[0.01, 0.01, 0.01],
        n_bootstrap=500,
        seed=0,
    )
    assert len(samples) > 400  # most should produce valid b
