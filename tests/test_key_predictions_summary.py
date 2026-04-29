"""Headline-prediction sanity tests (HYPOTHESIS Step 38)."""

from dinos import key_predictions_summary as kps


def test_at_least_10_headline_predictions():
    preds = kps.collect_all_headline_predictions()
    assert len(preds) >= 10


def test_higgs_in_top_predictions():
    preds = kps.collect_all_headline_predictions()
    higgs_preds = [p for p in preds if "HIGGS" in p.label]
    assert len(higgs_preds) == 1
    assert higgs_preds[0].relative_error_pct < 0.5


def test_majority_below_1_percent():
    """At least 70% of headline predictions match within 1%."""
    d = kps.predictive_density_below(1.0)
    assert d["fraction"] >= 0.7


def test_at_least_half_below_0pt1_percent():
    """At least 50% of headline predictions match within 0.1%."""
    d = kps.predictive_density_below(0.1)
    assert d["fraction"] >= 0.5


def test_all_have_non_empty_metallic_label():
    for p in kps.collect_all_headline_predictions():
        assert p.metallic_b_label
