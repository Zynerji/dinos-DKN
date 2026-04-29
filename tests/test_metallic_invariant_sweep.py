"""Metallic-invariant sweep tests (HYPOTHESIS Step 15).

Tests the user's hypothesis that b is a metallic invariant for each
fermion/boson family. Discrimination test at multiple tolerances
shows 3 fragments fit within 0.1% (significant: random gives 0.5),
while looser tolerances admit ~all fragments at chance level.
"""

from math import isclose, sqrt

import numpy as np
import pytest

from dinos import metallic_invariant_sweep as mis
from dinos import generations_extended


# -----------------------------------------------------------------------------
# Constants
# -----------------------------------------------------------------------------

def test_metallic_ratios_match_known_values():
    """Verify the metallic ratio constants."""
    assert isclose(mis.GOLDEN, (1 + sqrt(5)) / 2, rel_tol=1e-12)
    assert isclose(mis.SILVER, 1 + sqrt(2), rel_tol=1e-12)
    assert isclose(mis.BRONZE, (3 + sqrt(13)) / 2, rel_tol=1e-12)
    assert isclose(mis.COPPER, 2 + sqrt(5), rel_tol=1e-12)
    assert isclose(mis.NICKEL, (5 + sqrt(29)) / 2, rel_tol=1e-12)


def test_candidate_basis_is_substantial():
    """Should generate ~200+ candidate b expressions."""
    cands = mis.generate_candidate_b_expressions()
    assert len(cands) > 200


# -----------------------------------------------------------------------------
# The three TIGHT fits (sub-0.1%) — the genuine metallic invariants
# -----------------------------------------------------------------------------

def test_lepton_b_is_exactly_silver_minus_one():
    """Lepton b = silver - 1 = sqrt(2) exactly (algebraic identity)."""
    masses = mis.EMPIRICAL_FRAGMENTS["leptons (e,mu,tau)"]["masses"]
    b = mis.implied_b_from_masses(masses)
    assert isclose(b, sqrt(2.0), abs_tol=1e-4)
    assert isclose(b, mis.SILVER - 1, abs_tol=1e-4)


def test_vector_meson_b_matches_one_over_bronze_squared():
    """Vector mesons (ρ, ω, φ) b matches 1/bronze² to better than 0.1%."""
    masses = mis.EMPIRICAL_FRAGMENTS["v_mesons (rho,omega,phi)"]["masses"]
    b = mis.implied_b_from_masses(masses)
    target = 1.0 / (mis.BRONZE ** 2)
    rel = abs(b - target) / b
    assert rel < 0.001, f"b = {b}, 1/bronze^2 = {target}, rel diff = {rel}"


def test_light_baryon_b_matches_one_over_silver_times_copper():
    """(N, Λ, Ξ) b matches 1/(silver·copper) to better than 0.1%."""
    masses = mis.EMPIRICAL_FRAGMENTS["baryons (N,Lambda,Xi)"]["masses"]
    b = mis.implied_b_from_masses(masses)
    target = 1.0 / (mis.SILVER * mis.COPPER)
    rel = abs(b - target) / b
    assert rel < 0.001, f"b = {b}, 1/(silver*copper) = {target}, rel diff = {rel}"


# -----------------------------------------------------------------------------
# Looser fits (sub-1%) — likely combinatorial
# -----------------------------------------------------------------------------

def test_pseudoscalar_meson_pi_K_eta_loose_fit_only():
    """(π, K, η) doesn't fit any metallic to better than 1%."""
    masses = mis.EMPIRICAL_FRAGMENTS["ps_mesons (pi,K,eta)"]["masses"]
    b = mis.implied_b_from_masses(masses)
    cands = mis.generate_candidate_b_expressions()
    best = min(abs(v - b) / b for v in cands.values() if v > 0)
    assert best > 0.01, f"unexpected tight fit: {best:.4f}"


# -----------------------------------------------------------------------------
# Discrimination test (statistical significance)
# -----------------------------------------------------------------------------

def _discrimination_test(tol_pct: float, n_random_seeds: int = 20) -> dict:
    """At given tolerance, count metallic fits and random-baseline fits."""
    cands = mis.generate_candidate_b_expressions()
    fragments = list(mis.EMPIRICAL_FRAGMENTS.values())

    metallic_fit_count = 0
    for info in fragments:
        masses = info["masses"]
        Q = generations_extended.koide_q(masses)
        if 0 < Q < 3:
            b = sqrt(6 / Q - 2)
            best = min(abs(v - b) / b * 100 for v in cands.values() if v > 0)
            if best < tol_pct:
                metallic_fit_count += 1

    random_fits = []
    for seed in range(n_random_seeds):
        rng = np.random.default_rng(seed * 7919)
        rand_cands = np.exp(rng.uniform(np.log(0.001), np.log(5), len(cands)))
        n = 0
        for info in fragments:
            masses = info["masses"]
            Q = generations_extended.koide_q(masses)
            if 0 < Q < 3:
                b = sqrt(6 / Q - 2)
                best = min(abs(v - b) / b * 100 for v in rand_cands)
                if best < tol_pct:
                    n += 1
        random_fits.append(n)

    return {
        "metallic": metallic_fit_count,
        "random_mean": float(np.mean(random_fits)),
        "random_max": int(max(random_fits)),
    }


def test_metallic_significantly_beats_random_at_0p1_pct():
    """At tolerance 0.1%, metallic gets ~3 fits while random gives ~0.5
    on average — a ~6x improvement, statistically significant."""
    result = _discrimination_test(tol_pct=0.1, n_random_seeds=20)
    assert result["metallic"] >= 3, (
        f"metallic fits {result['metallic']}, expected >= 3"
    )
    assert result["random_mean"] < 1.5, (
        f"random mean {result['random_mean']}, expected < 1.5"
    )
    # Metallic must beat random by 2x or more
    assert result["metallic"] > 2 * result["random_mean"]


def test_loose_tolerance_is_NOT_significant():
    """At 5% tolerance, both metallic and random fit nearly all fragments
    — the structure is meaningless at loose tolerance."""
    result = _discrimination_test(tol_pct=5.0)
    # At 5%, both should fit nearly all
    assert result["metallic"] >= 9
    assert result["random_mean"] >= 8.0   # very close to metallic


# -----------------------------------------------------------------------------
# Aggregate report
# -----------------------------------------------------------------------------

def test_aggregate_sweep_report_is_consistent():
    """Aggregate report should reproduce per-fragment data."""
    report = mis.generate_metallic_sweep_report()
    assert report.n_total == 10
    # At 1% tolerance, report uses, expect 9 fits
    assert 8 <= report.n_fits <= 10
