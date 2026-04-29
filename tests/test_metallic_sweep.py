"""Metallic-ratio sweep tests."""

from math import isclose

import numpy as np

from dinos import metallic_sweep as ms


# -----------------------------------------------------------------------------
# Constants
# -----------------------------------------------------------------------------

def test_metallic_ratios_satisfy_their_polynomials():
    """Each metallic mean satisfies its defining polynomial."""
    # Quadratic: x² = nx + 1 for n = 1, 2, 3, 4, 5
    for n, x in enumerate(
        [ms.GOLDEN_RATIO, ms.SILVER_RATIO, ms.BRONZE_RATIO,
         ms.COPPER_RATIO, ms.NICKEL_RATIO], start=1
    ):
        assert isclose(x * x, n * x + 1.0, rel_tol=1e-10), (
            f"x = {x} (n={n}): x² = {x*x}, nx+1 = {n*x + 1.0}"
        )
    # Cubic: plastic x³ = x + 1
    assert isclose(ms.PLASTIC_RATIO ** 3,
                   ms.PLASTIC_RATIO + 1.0, abs_tol=1e-9)
    # Cubic: supergolden x³ = x² + 1
    assert isclose(ms.SUPERGOLDEN_RATIO ** 3,
                   ms.SUPERGOLDEN_RATIO ** 2 + 1.0, abs_tol=1e-9)


def test_seven_ratios_in_dict():
    """The METALLIC_RATIOS dict has exactly the seven canonical entries."""
    assert set(ms.METALLIC_RATIOS.keys()) == {
        "golden", "silver", "bronze", "copper", "nickel",
        "plastic", "supergolden",
    }


# -----------------------------------------------------------------------------
# Sweep A: time-averaged shifts are universal across ratios
# -----------------------------------------------------------------------------

def test_sweep_A_universal_across_ratios():
    """The time-averaged ⟨τ²⟩ = τ_0²(1 + a²/2) does not depend on the
    metallic ratio M.  All sweeps should give the same shift to
    machine precision."""
    shifts = ms.sweep_time_averaged_shifts()
    values = list(shifts.values())
    spread = max(values) - min(values)
    mean = float(np.mean(values))
    assert abs(spread / mean) < 1e-12, (
        f"non-universal: rel spread = {spread/mean}"
    )


# -----------------------------------------------------------------------------
# Sweep B: chiral Laplacian eigenvalues vary with M and N
# -----------------------------------------------------------------------------

def test_chiral_laplacian_zero_eigenvalue():
    """Any (M, N) chiral Laplacian has a zero eigenvalue (constant mode)."""
    for M in ms.METALLIC_RATIOS.values():
        for N in [3, 4, 6]:
            L = ms.chiral_laplacian_N_cycle(M, N)
            eigs_abs = np.sort(np.abs(np.linalg.eigvals(L).real))
            assert eigs_abs[0] < 1e-9, (
                f"(M={M}, N={N}): smallest |eig| = {eigs_abs[0]}"
            )


def test_chiral_laplacian_non_trivial_eigenvalues_vary_with_ratio():
    """At fixed N, different metallic ratios give different non-trivial
    eigenvalues (sanity check that the operator is M-dependent)."""
    N = 5
    eigs_per_ratio = {}
    for name, M in ms.METALLIC_RATIOS.items():
        L = ms.chiral_laplacian_N_cycle(M, N)
        eigs = np.sort(np.abs(np.linalg.eigvals(L).real))
        # Take the second-smallest (first non-trivial) eigenvalue.
        eigs_per_ratio[name] = eigs[1]
    # At least two ratios should give different non-trivial eigenvalues.
    distinct = len(set(round(v, 6) for v in eigs_per_ratio.values()))
    assert distinct >= 2, (
        f"all metallic ratios gave the same second-smallest eigenvalue: "
        f"{eigs_per_ratio}"
    )


# -----------------------------------------------------------------------------
# Falsification: no metallic ratio + cycle length matches lepton tower
# -----------------------------------------------------------------------------

def test_no_metallic_ratio_matches_lepton_tower():
    """Sweep all (M, N) for N ∈ {3, 4, 6, 7} and confirm none reproduces
    the lepton mass tower (1, 207, 3477) within log-residual 1.0.

    Best result is bronze on N=7 with log-residual ~5.86 — much better
    than 3-cycle but still nowhere near the empirical hierarchy."""
    summary = ms.generate_summary()
    assert not summary.sweep_B_any_match, (
        f"unexpected match: {summary.sweep_B_best_match}"
    )
    # Best should be log-residual > 5 (we expect ~5.86 for bronze N=7).
    assert summary.sweep_B_best_match.log_residual_vs_lepton > 5.0, (
        f"best log_residual = {summary.sweep_B_best_match.log_residual_vs_lepton}"
    )


def test_summary_documents_universality_of_sweep_A():
    summary = ms.generate_summary()
    assert summary.sweep_A_universal
    assert summary.sweep_A_max_relative_spread < 1e-10
