"""Theorems extension tests (HYPOTHESIS Step 50)."""

from dinos import theorems_extension as te


def test_z3_cover_eigenvalue_formula_confirmed():
    v = te.test_z3_cover_eigenvalue_formula(N=32)
    assert v.verdict == "CONFIRMED"


def test_silver_b_partial_match():
    v = te.test_silver_b_as_sl2_trace()
    assert v.verdict == "PARTIAL"
    assert "exact" in v.evidence.lower()


def test_a_b_gap_equation_falsified():
    v = te.test_a_b_gap_equation()
    assert v.verdict == "FALSIFIED"


def test_confinement_threshold_partial():
    v = te.test_confinement_at_sqrt2()
    assert v.verdict == "PARTIAL"


def test_theorem_1_conditional():
    v = te.test_theorem_1_conditional_algebraic_degree()
    assert v.verdict == "CONDITIONAL"


def test_summary_counts():
    s = te.theorem_verdict_summary()
    assert s["total_theorems_tested"] == 5
    assert s["verdict_counts"].get("CONFIRMED", 0) == 1
    assert s["verdict_counts"].get("FALSIFIED", 0) == 1
    assert s["verdict_counts"].get("PARTIAL", 0) == 2
    assert s["verdict_counts"].get("CONDITIONAL", 0) == 1
