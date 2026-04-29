"""Metallic-ratio sweep across the bridge experiments (HYPOTHESIS Step 6+).

The Step 6 cross-repo experiments tested ONE specific metallic ratio
(Bronze β₃ ≈ 3.303). This module sweeps the full family —

  - Golden       φ        = (1 + √5)/2          ≈ 1.618   (x² = x + 1)
  - Silver       δ_S      = 1 + √2              ≈ 2.414   (x² = 2x + 1)
  - Bronze       β₃       = (3 + √13)/2         ≈ 3.303   (x² = 3x + 1)
  - Copper       δ_C      = 2 + √5              ≈ 4.236   (x² = 4x + 1)
  - Nickel       δ_N      = (5 + √29)/2         ≈ 5.193   (x² = 5x + 1)
  - Plastic      ρ        ≈ 1.325               (x³ = x + 1)
  - Supergolden  ψ_s      ≈ 1.466               (x³ = x² + 1)

— and reports whether any choice yields qualitatively different
behaviour for the cross-repo bridge experiments.

Two sweeps:

A. **Time-averaged τ(t) shift per ratio**: ⟨cos²(ω·t + φ)⟩ = ½ for any ω,
   so this should be **identical** across ratios — confirming the
   universality of the −½ prefactor (Step 5b).

B. **Chiral Laplacian eigenvalues per ratio**: the matrix entries
   ``cos(M·Δθ) + χ·sin(M·Δθ)`` depend on M, so eigenvalues vary —
   reports whether any M produces lepton-tower-like ratios.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np

from . import generations


# -----------------------------------------------------------------------------
# Metallic-ratio constants
# -----------------------------------------------------------------------------

GOLDEN_RATIO: float = (1.0 + math.sqrt(5.0)) / 2.0           # φ ≈ 1.618
SILVER_RATIO: float = 1.0 + math.sqrt(2.0)                   # δ_S ≈ 2.414
BRONZE_RATIO: float = (3.0 + math.sqrt(13.0)) / 2.0          # β₃ ≈ 3.303
COPPER_RATIO: float = 2.0 + math.sqrt(5.0)                   # δ_C ≈ 4.236
NICKEL_RATIO: float = (5.0 + math.sqrt(29.0)) / 2.0          # δ_N ≈ 5.193

# Cubic-recurrence constants (numerical roots, not closed quadratic)
PLASTIC_RATIO: float = 1.32471795724474602596       # ρ, x³ = x + 1
SUPERGOLDEN_RATIO: float = 1.46557123187676802665   # ψ_s, x³ = x² + 1


METALLIC_RATIOS: dict[str, float] = {
    "golden":      GOLDEN_RATIO,
    "silver":      SILVER_RATIO,
    "bronze":      BRONZE_RATIO,
    "copper":      COPPER_RATIO,
    "nickel":      NICKEL_RATIO,
    "plastic":     PLASTIC_RATIO,
    "supergolden": SUPERGOLDEN_RATIO,
}


# -----------------------------------------------------------------------------
# Sweep A: time-averaged shift universality
# -----------------------------------------------------------------------------

def time_averaged_shift_for_ratio(M: float, tau_0: float, m_j: float,
                                  beta_plus_kappa: float,
                                  amplitude: float = 0.4,
                                  n_periods: int = 100,
                                  n_samples: int = 50000) -> float:
    """Time-averaged Δλ² = -⟨τ(t)²⟩·V for τ(t) = τ_0(1 + a·cos(M·t + φ)).

    For *any* ratio M and any phase φ, ⟨cos²⟩ = ½, so this should
    return the same value (within numerical noise) for all M:

        ⟨τ²⟩ = τ_0² · (1 + a²/2)
    """
    omega = 2.0 * math.pi / M     # frequency of one full cycle
    period = 2.0 * math.pi / omega
    t = np.linspace(0.0, n_periods * period, n_samples)
    tau_t = tau_0 * (1.0 + amplitude * np.cos(omega * t))
    avg_tau_sq = float(np.mean(tau_t ** 2))
    return -avg_tau_sq * (m_j ** 2 - beta_plus_kappa)


def sweep_time_averaged_shifts(tau_0: float = 0.5, m_j: float = 0.5,
                               beta_plus_kappa: float = 0.1
                               ) -> dict[str, float]:
    """Time-averaged shift for each metallic ratio."""
    return {
        name: time_averaged_shift_for_ratio(M, tau_0, m_j, beta_plus_kappa)
        for name, M in METALLIC_RATIOS.items()
    }


# -----------------------------------------------------------------------------
# Sweep B: chiral Laplacian eigenvalues per ratio + per cycle length
# -----------------------------------------------------------------------------

def chiral_edge_weight(M: float, theta_i: float, theta_j: float,
                       chi: float = 1.0) -> float:
    """``w(i→j) = cos(M·Δθ) + χ·sin(M·Δθ)`` parameterised by metallic ratio M."""
    delta = theta_j - theta_i
    return math.cos(M * delta) + chi * math.sin(M * delta)


def chiral_laplacian_N_cycle(M: float, N: int, chi: float = 1.0) -> np.ndarray:
    """Chiral Laplacian for an N-node cycle with bronze-style edges.

    Nodes at θ ∈ {2πk/N : k = 0, …, N−1}.  L = D − A where
    D[i,i] = Σ_j A[i,j] and A[i,j] = w(i→j).
    """
    if N < 2:
        raise ValueError("need N ≥ 2 nodes")
    thetas = np.array([2.0 * math.pi * k / N for k in range(N)])
    A = np.zeros((N, N))
    for i in range(N):
        for j in range(N):
            if i != j:
                A[i, j] = chiral_edge_weight(M, thetas[i], thetas[j], chi)
    D = np.diag(A.sum(axis=1))
    return D - A


@dataclass(frozen=True)
class ChiralEigenResult:
    """Eigenvalue spectrum for a (ratio, N) combination."""
    ratio_name: str
    M: float
    N: int
    eigenvalues_real: np.ndarray
    sorted_abs_ratios: np.ndarray
    log_residual_vs_lepton: float
    matches_lepton_tower: bool


def eigen_result_for(name: str, M: float, N: int) -> ChiralEigenResult:
    """Compute the eigenvalue ratios and compare to the lepton tower."""
    L = chiral_laplacian_N_cycle(M, N)
    eigs = np.linalg.eigvals(L)
    eigs_real = np.array([float(e.real) for e in eigs])
    eigs_abs = np.abs(eigs_real)
    nonzero = eigs_abs[eigs_abs > 1e-9]
    if len(nonzero) == 0:
        ratios = np.zeros(N)
        log_res = float("inf")
    else:
        ratios = np.sort(eigs_abs / np.min(nonzero))
        # Compare top 3 ratios (or available) to lepton tower (1, 207, 3477).
        targets = np.sort(np.array([
            1.0,
            generations.M_MU_MeV / generations.M_E_MeV,
            generations.M_TAU_MeV / generations.M_E_MeV,
        ]))
        # If we have at least 3 non-trivial ratios, compare top 3.
        nontrivial = ratios[ratios > 1.0 + 1e-6]
        if len(nontrivial) >= 2:
            comparison = np.concatenate(([1.0], nontrivial[:2]))
        else:
            comparison = np.array([1.0, ratios[-1], ratios[-1]])
        log_res = float(np.linalg.norm(
            np.log(comparison + 1e-12) - np.log(targets + 1e-12)
        ))
    matches = log_res < 1.0
    return ChiralEigenResult(
        ratio_name=name, M=M, N=N,
        eigenvalues_real=eigs_real,
        sorted_abs_ratios=ratios,
        log_residual_vs_lepton=log_res,
        matches_lepton_tower=matches,
    )


def sweep_chiral_laplacian(N_values: list[int] | None = None
                           ) -> dict[tuple[str, int], ChiralEigenResult]:
    """Sweep all metallic ratios across cycle lengths N ∈ {3, 4, 6, 7}."""
    if N_values is None:
        N_values = [3, 4, 6, 7]
    out: dict[tuple[str, int], ChiralEigenResult] = {}
    for name, M in METALLIC_RATIOS.items():
        for N in N_values:
            out[(name, N)] = eigen_result_for(name, M, N)
    return out


# -----------------------------------------------------------------------------
# Summary report
# -----------------------------------------------------------------------------

@dataclass(frozen=True)
class SweepSummary:
    """Aggregate summary across both sweeps."""
    sweep_A_universal: bool                # ⟨τ²⟩ same for all ratios?
    sweep_A_max_relative_spread: float     # spread / mean
    sweep_B_best_match: ChiralEigenResult  # closest to lepton tower (if any)
    sweep_B_any_match: bool                # any ratio produce lepton tower?
    notes: str


def generate_summary() -> SweepSummary:
    """Run both sweeps and produce a digestible summary."""
    # Sweep A
    shifts = sweep_time_averaged_shifts()
    vals = np.array(list(shifts.values()))
    spread = float(vals.max() - vals.min())
    mean_val = float(np.mean(vals))
    rel_spread = abs(spread / mean_val) if mean_val != 0 else float("inf")
    universal = rel_spread < 1e-3

    # Sweep B
    results = sweep_chiral_laplacian()
    sorted_results = sorted(results.values(),
                            key=lambda r: r.log_residual_vs_lepton)
    best = sorted_results[0]
    any_match = best.matches_lepton_tower

    notes = (
        f"Sweep A (time-averaged shift): {len(shifts)} ratios tested; "
        f"all give the same shift to within rel-spread {rel_spread:.2e} "
        f"— universal as expected from ⟨cos²⟩ = ½. "
        f"Sweep B (chiral Laplacian): tested all ratios on N = 3, 4, 6, 7 cycles; "
        f"best match is {best.ratio_name} on N={best.N} with log-residual "
        f"{best.log_residual_vs_lepton:.3f} vs lepton tower; "
        f"{'MATCHES' if any_match else 'NO match — lepton tower not produced'}."
    )
    return SweepSummary(
        sweep_A_universal=universal,
        sweep_A_max_relative_spread=rel_spread,
        sweep_B_best_match=best,
        sweep_B_any_match=any_match,
        notes=notes,
    )


__all__ = [
    "GOLDEN_RATIO", "SILVER_RATIO", "BRONZE_RATIO", "COPPER_RATIO",
    "NICKEL_RATIO", "PLASTIC_RATIO", "SUPERGOLDEN_RATIO", "METALLIC_RATIOS",
    "time_averaged_shift_for_ratio", "sweep_time_averaged_shifts",
    "chiral_edge_weight", "chiral_laplacian_N_cycle",
    "ChiralEigenResult", "eigen_result_for", "sweep_chiral_laplacian",
    "SweepSummary", "generate_summary",
]
