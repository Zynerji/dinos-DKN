"""Meta-pattern tests (HYPOTHESIS Step 19)."""

from dinos import foot_meta_pattern as fmp


def test_seven_confirmed_resonances():
    """Catalog has 7 confirmed metallic Foot resonances."""
    res = fmp.all_confirmed_metallic_resonances()
    assert len(res) == 7


def test_lepton_is_unique_additive_form():
    """Lepton b = silver - 1 is the unique 'additive' form;
    others are multiplicative reciprocals."""
    res = fmp.all_confirmed_metallic_resonances()
    additive = [r for r in res if r.b_expression == "silver - 1"]
    assert len(additive) == 1
    assert additive[0].family == "charged_leptons"


def test_silver_is_most_common_metallic():
    """Silver appears in the majority of b expressions."""
    report = fmp.generate_meta_pattern_report()
    assert report.most_common_metallic == "silver"
    assert report.silver_appearances >= 4


def test_b_values_span_two_orders_of_magnitude():
    """b values span ~ 0.04 to 1.4 — a 30x range."""
    report = fmp.generate_meta_pattern_report()
    b_min, b_max = report.b_values_range
    assert b_max / b_min > 20
    assert b_max / b_min < 100


def test_mass_scales_span_two_orders():
    """Mass scales span 313 MeV to 7480 MeV — a 24x range."""
    report = fmp.generate_meta_pattern_report()
    a_min, a_max = report.a_values_range
    assert 20 < a_max / a_min < 30


def test_no_resonance_uses_nickel():
    """Nickel (M_5) does NOT appear in any confirmed expression —
    interesting absence."""
    res = fmp.all_confirmed_metallic_resonances()
    nickel_count = sum(1 for r in res if "nickel" in r.b_expression)
    assert nickel_count == 0
