"""Cross-repo experiment tests — confirms negative results.

Tests that:
A. BronzePendulum-driven τ(t) gives phase-independent time-averaged
   shift (cannot produce a generation tower).
B. Chiral Laplacian on a 3-cycle gives eigenvalue ratios that don't
   resemble the lepton tower (ratios are small integers, not 207/3477).

Both are falsifications: tool transplants from related repos do NOT
close the Step 3 generation problem.
"""

from math import isclose

import numpy as np

from dinos import cross_repo_experiments as exp


# -----------------------------------------------------------------------------
# Experiment A — Bronze τ(t) cannot split heads into generations
# -----------------------------------------------------------------------------

def test_bronze_tau_t_at_zero_time():
    """At t = 0, τ_h(0) = τ_0(1 + a·cos(φ_h))."""
    tau_0 = 0.5
    a = 0.4
    for h in range(3):
        phase = (exp.GOLDEN_ANGLE * h) % (2.0 * np.pi)
        expected = tau_0 * (1.0 + a * np.cos(phase))
        actual = exp.bronze_tau_t(t=0.0, tau_0=tau_0, phase=phase, amplitude=a)
        assert isclose(actual, expected, rel_tol=1e-12)


def test_bronze_time_averaged_shifts_are_phase_independent():
    """Time-average ⟨τ²⟩_t = τ_0²·(1 + a²/2) is the same for ALL heads.

    This is the core mechanism by which the Bronze pendulum FAILS to
    produce a generation tower: phases wash out under averaging."""
    shifts = exp.bronze_time_averaged_shift_per_head(
        tau_0=0.5, n_heads=3, m_j=0.5, beta_plus_kappa=0.1,
    )
    values = list(shifts.values())
    # Relative spread should be ~ 1e-5 or smaller (numerical noise).
    spread = max(values) - min(values)
    mean = float(np.mean(values))
    assert abs(spread / mean) < 1e-3, (
        f"Bronze heads NOT phase-independent: spread/mean = {spread/mean}"
    )


def test_experiment_A_returns_negative_verdict():
    """Run Experiment A and confirm it does NOT match the lepton tower."""
    res = exp.run_experiment_A()
    assert not res.matches_lepton_tower, (
        "Bronze tau(t) unexpectedly produced lepton tower — recheck"
    )
    assert res.relative_spread < 1e-3, (
        f"rel spread = {res.relative_spread}; expected ≪ 1"
    )


# -----------------------------------------------------------------------------
# Experiment B — Chiral Laplacian on 3-cycle doesn't produce lepton tower
# -----------------------------------------------------------------------------

def test_chiral_edge_weight_antisymmetric_in_chi():
    """w(i→j) flips sign of the chiral part under χ → −χ."""
    theta_i, theta_j = 0.0, 2.0 * np.pi / 3.0
    w_plus = exp.chiral_edge_weight(theta_i, theta_j, chi=1.0)
    w_minus = exp.chiral_edge_weight(theta_i, theta_j, chi=-1.0)
    sym = 0.5 * (w_plus + w_minus)
    antisym = 0.5 * (w_plus - w_minus)
    # Symmetric part should equal cos(β₃ Δθ); antisym should equal sin(β₃ Δθ)
    expected_sym = np.cos(exp.BRONZE_RATIO * (theta_j - theta_i))
    expected_antisym = np.sin(exp.BRONZE_RATIO * (theta_j - theta_i))
    assert isclose(sym, expected_sym, rel_tol=1e-12)
    assert isclose(antisym, expected_antisym, rel_tol=1e-12)


def test_chiral_laplacian_3cycle_has_zero_eigenvalue():
    """Any graph Laplacian has a zero eigenvalue from the constant mode."""
    L = exp.chiral_laplacian_3cycle(chi=1.0)
    eigs = np.sort(np.abs(np.linalg.eigvals(L).real))
    assert eigs[0] < 1e-9, f"smallest |eig| = {eigs[0]}; expected ~0"


def test_chiral_laplacian_eigenvalue_ratios_dont_match_lepton_tower():
    """The non-trivial eigenvalue ratio is ~3.3 (close to β₃), nowhere
    near the lepton ratios 207 and 3477.  Confirms the chiral
    Laplacian on a 3-cycle is the wrong structure."""
    res = exp.run_experiment_B()
    assert not res.matches_lepton_tower, (
        "Chiral Laplacian unexpectedly fits lepton tower — recheck"
    )
    # log-residual should be huge (>10 — many orders of magnitude off).
    assert res.log_residual > 10.0, (
        f"log-residual = {res.log_residual}; expected ≫ 1"
    )


def test_chiral_laplacian_nontrivial_eigenvalue_near_bronze_ratio():
    """Curious side observation: the non-trivial eigenvalue ratio
    ≈ 3.29, close to the Bronze ratio β₃ ≈ 3.303.  Documented for
    record; not load-bearing on any bridge claim."""
    res = exp.run_experiment_B()
    sorted_ratios = sorted(res.eigenvalue_ratios)
    # Largest ratio should be near β₃.
    largest = sorted_ratios[-1]
    assert abs(largest - exp.BRONZE_RATIO) < 0.1, (
        f"largest eigenvalue ratio = {largest}, β₃ = {exp.BRONZE_RATIO}"
    )
