"""cz.txt 10-algorithm validation tests (HYPOTHESIS Step 52)."""

import numpy as np

from dinos import cz_claims_validation as cz


def test_market_koide_falsified():
    v = cz.validate_cz_2_market_koide()
    assert v.verdict == "FALSIFIED"


def test_cosmology_b_falsified():
    v = cz.validate_cz_10_cosmology_b()
    assert v.verdict == "FALSIFIED"


def test_urban_planner_unit_dependent():
    v = cz.validate_cz_8_urban_planner_units()
    assert v.verdict == "UNIT-DEPENDENT"


def test_climate_unit_dependent():
    v = cz.validate_cz_3_climate_units()
    assert v.verdict == "UNIT-DEPENDENT"


def test_ecosystem_unit_dependent():
    v = cz.validate_cz_6_ecosystem_units()
    assert v.verdict == "UNIT-DEPENDENT"


def test_codon_undefined():
    v = cz.validate_cz_1_codon_classifier()
    assert v.verdict == "UNDEFINED"


def test_drug_designer_undefined():
    v = cz.validate_cz_5_drug_designer()
    assert v.verdict == "UNDEFINED"


def test_consciousness_undefined():
    v = cz.validate_cz_9_consciousness()
    assert v.verdict == "UNDEFINED"


def test_z3_neural_unvalidated():
    v = cz.validate_cz_4_z3_neural_architecture()
    assert v.verdict == "UNVALIDATED"


def test_cf_detector_overclaimed():
    v = cz.validate_cz_7_universal_pattern_detector()
    assert v.verdict == "OVERCLAIMED"


def test_zero_cz_claims_confirmed():
    s = cz.cz_verdict_summary()
    assert s["verdict_counts"].get("CONFIRMED", 0) == 0
    assert s["total_claims_tested"] == 10


def test_koide_Q_unit_invariant_under_uniform_scaling():
    """Sanity: Q is unit-invariant under uniform scaling — but NOT under
    different unit changes per component."""
    a = [1.0, 2.0, 3.0]
    b = [10.0, 20.0, 30.0]
    assert abs(cz.koide_Q(a) - cz.koide_Q(b)) < 1e-12

    # Mixed scaling breaks invariance
    c = [1.0, 20.0, 3.0]   # different scaling per component
    assert abs(cz.koide_Q(a) - cz.koide_Q(c)) > 0.01


def test_b_from_Q_inverse_consistency():
    """If Q = 3/2 then b should be sqrt(2)."""
    assert abs(cz.b_from_Q(1.5) - np.sqrt(2)) < 1e-12
