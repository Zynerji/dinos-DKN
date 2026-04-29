"""Metallic selection rule tests (HYPOTHESIS Step 56)."""

from dinos import metallic_selection_rule as msr


def test_seven_atlas_relevant_ratios():
    assert len(msr.ATLAS_PISOT_RATIOS) == 7


def test_pisot_property_universal():
    """The Pisot property is universally satisfied across all 7 ratios."""
    props = msr.candidate_properties()
    pisot = next(p for p in props if p.label == "Pisot_number")
    assert pisot.atlas_satisfied is True


def test_quadratic_property_NOT_universal():
    """plastic and supergolden are cubic; quadratic property fails as universal."""
    props = msr.candidate_properties()
    quad = next(p for p in props if p.label == "quadratic_irrational")
    assert quad.atlas_satisfied is False


def test_period_1_cf_NOT_universal():
    """plastic and supergolden have non-periodic CFs."""
    props = msr.candidate_properties()
    cf = next(p for p in props if p.label == "period_1_continued_fraction")
    assert cf.atlas_satisfied is False


def test_binomial_recurrence_universal():
    """The proposed selection rule is satisfied by all 7."""
    props = msr.candidate_properties()
    bin_rec = next(p for p in props if p.label == "binomial_recurrence_Pisot")
    assert bin_rec.atlas_satisfied is True


def test_atlas_decomposition_period1_vs_cubic():
    d = msr.atlas_decomposition_by_pisot_type()
    assert d["n_period_1"] + d["n_cubic"] == 19
    # Both groups should be substantial
    assert d["n_period_1"] >= 5
    assert d["n_cubic"] >= 5


def test_proposed_rule_excludes_tribonacci():
    """Tribonacci (3-term recurrence) is Pisot but not in the atlas."""
    rule = msr.proposed_selection_rule()
    assert any("tribonacci" in c.lower() for c in rule.counter_examples_in_pisot_class)


def test_non_atlas_pisot_ratios_documented():
    """Non-atlas Pisots (tribonacci, etc.) documented for contrast."""
    assert len(msr.NON_ATLAS_PISOT_RATIOS) >= 2


def test_proposed_rule_n_atlas_relevant():
    rule = msr.proposed_selection_rule()
    assert rule.n_atlas_relevant == 7
