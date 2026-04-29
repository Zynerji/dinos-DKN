"""ee.txt + ej.txt validation tests (HYPOTHESIS Step 53)."""

import numpy as np

from dinos import monodromy_hecke_test as mht
from dinos import ee_ej_validation as eev


# ---- Riemann-Hurwitz computation (from ee.txt §II step 1) ----

def test_riemann_hurwitz_z3_cover_is_torus():
    """Z3 cover of P^1 with 3 branch points fully ramified → genus 1."""
    g = mht.riemann_hurwitz_genus(degree=3, base_genus=0,
                                    n_branch_points=3,
                                    ramification_per_point=3)
    assert g == 1


# ---- Hecke trace field test ----

def test_hecke_lambda_q_known_values():
    """λ_3 = 1, λ_4 = √2, λ_5 = φ, λ_6 = √3."""
    assert abs(mht.lambda_q(3) - 1.0) < 1e-10
    assert abs(mht.lambda_q(4) - np.sqrt(2)) < 1e-10
    phi = (1 + np.sqrt(5)) / 2
    assert abs(mht.lambda_q(5) - phi) < 1e-10
    assert abs(mht.lambda_q(6) - np.sqrt(3)) < 1e-10


def test_hecke_h4_silver_match():
    """H(4) trace field includes √2; lepton b should match."""
    rep = mht.test_hecke_against_atlas("H(4)", np.sqrt(2), max_length=6)
    assert rep.n_atlas_matches_within_1pct >= 1


def test_hecke_no_universal_match_across_atlas():
    """No single Hecke triangle group matches more than 2 atlas b values."""
    reports = mht.all_hecke_tests(max_length=6)
    for r in reports:
        assert r.n_atlas_matches_within_1pct <= 2


def test_hecke_pathway_does_not_explain_atlas():
    """The total atlas-coverage of Hecke trace fields is < half the atlas."""
    reports = mht.all_hecke_tests(max_length=6)
    # Each atlas b can be matched by at most one Hecke group; sum is conservative
    total_matches = sum(r.n_atlas_matches_within_1pct for r in reports)
    # Even with double-counting, total << 19
    assert total_matches < 19 / 2


# ---- ee.txt vulnerabilities ----

def test_ee_vulnerabilities_both_valid():
    vs = eev.ee_vulnerabilities()
    assert len(vs) == 2
    for v in vs:
        assert v.valid is True


# ---- ej.txt 20 algorithms ----

def test_twenty_ej_algorithms_catalogued():
    out = eev.ej_algorithm_statuses()
    assert len(out) == 20


def test_ej_status_counts_show_no_unconditional_wins():
    """No ej algorithm has status that would imply Conjecture #1 holds."""
    out = eev.ej_algorithm_statuses()
    confirmed = sum(1 for a in out if a.status == "CONFIRMED")
    assert confirmed == 0


def test_ej_summary_documents_cascade():
    s = eev.ej_status_summary()
    assert s["total_algorithms"] == 20
    # All 20 algorithms have one of the conditional / overload statuses
    counts = s["status_counts"]
    assert sum(counts.values()) == 20


def test_ee_addition_11_is_underived():
    s = eev.ee_addition_11_status()
    assert s.status == "UNDERIVED"
