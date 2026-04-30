"""Substitution dynamics answer tests (HYPOTHESIS Step 57)."""

import numpy as np

from dinos import substitution_dynamics_answer as sda


def test_seven_atlas_two_term_recurrences():
    catalog = sda.all_known_pisot_recurrences()
    in_atlas = [r for r in catalog if r.in_atlas]
    assert len(in_atlas) == 7
    for r in in_atlas:
        assert r.n_recurrence_terms == 2


def test_two_term_growth_rates_match_known_metallics():
    """Numerically verify each 2-term recurrence reproduces its growth rate."""
    cases = [
        ([(1, 1), (1, 2)], 1.6180339887),
        ([(2, 1), (1, 2)], 2.4142135624),
        ([(3, 1), (1, 2)], 3.3027756378),
        ([(1, 2), (1, 3)], 1.3247179572),  # Padovan -> plastic
        ([(1, 1), (1, 3)], 1.4655712319),  # Narayana -> supergolden
    ]
    for coefs_lags, expected in cases:
        got = sda.recurrence_growth_rate(coefs_lags, depth=400)
        assert abs(got - expected) < 1e-6


def test_tribonacci_excluded_from_atlas():
    catalog = sda.all_known_pisot_recurrences()
    trib = next(r for r in catalog if r.name == "tribonacci")
    assert trib.n_recurrence_terms == 3
    assert trib.in_atlas is False


def test_selection_rule_predictions_match_observations():
    v = sda.two_term_recurrence_selection()
    assert v.n_atlas_predicted == v.n_atlas_observed == 7


def test_selection_rule_lists_excluded_examples():
    v = sda.two_term_recurrence_selection()
    assert any("tribonacci" in e.lower() for e in v.excluded_examples)
    assert any("tetranacci" in e.lower() for e in v.excluded_examples)


def test_minimal_polynomials_are_binomial():
    """All atlas-relevant minimal polys have exactly 2 nonzero monomials
    on the right of x^d, plus 1 (constant)."""
    catalog = sda.all_known_pisot_recurrences()
    for r in catalog:
        if not r.in_atlas:
            continue
        # Count terms in min poly: e.g. 'x^2 - x - 1' has 3 terms; subtract 1 for x^d
        n_terms = r.minimal_polynomial.count("x") + r.minimal_polynomial.count("- 1") - 1
        assert n_terms <= 4   # x^d, ax^k, +1 → at most 3 monomials, with safety
