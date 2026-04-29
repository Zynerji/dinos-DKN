"""Cross-repo experiments — checking if tools from related projects close
the open Dinos bridges.

Two specific tests, both motivated by a survey of related repositories
(Aletheia BronzePendulum, Alembic chiral Laplacian) suggested as
candidate generators of generation-mass structure:

A. **Bronze-driven τ(t) Floquet shift**:  Replace static τ in
   :mod:`dinos.kerr_corrections` with a BronzePendulum-style
   oscillating τ_h(t) = τ_0(1 + a·cos(β₃·t + φ_h)) at multiple head
   phases φ_h.  *Hypothesis:* time-averaged shift differs per head,
   producing a generation tower.

B. **Chiral Laplacian eigenvalue ratios**:  Build the discrete
   Chern-Simons connection ``w(i→j) = cos(β₃·Δθ) + χ·sin(β₃·Δθ)``
   on a 3-node Möbius cycle and check whether its eigenvalue ratios
   match the empirical lepton tower (1 : 207 : 3477).

Both report **honest verdicts** — these are designed as falsifiable
experiments, not curve-fits.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np


# Bronze ratio constants (from Aletheia/torsion/bronze.py)
BRONZE_RATIO: float = (3.0 + math.sqrt(13.0)) / 2.0          # ≈ 3.3028
BRONZE_ANGLE: float = 2.0 * math.pi / BRONZE_RATIO           # ≈ 1.9022 rad
GOLDEN_ANGLE: float = math.pi * (3.0 - math.sqrt(5.0))       # ≈ 2.3998 rad


# -----------------------------------------------------------------------------
# Experiment A: Bronze-driven τ(t) Floquet shift
# -----------------------------------------------------------------------------

def bronze_tau_t(t: float, tau_0: float, phase: float,
                 amplitude: float = 0.4) -> float:
    """Per-head BronzePendulum τ(t) = τ_0(1 + a·cos(β₃·t + φ_h))."""
    return tau_0 * (1.0 + amplitude * math.cos(BRONZE_ANGLE * t + phase))


def bronze_time_averaged_shift_per_head(
    tau_0: float,
    n_heads: int,
    m_j: float,
    beta_plus_kappa: float,
    n_samples: int = 50000,
    n_bronze_periods: int = 100,
) -> dict[str, float]:
    """Time-averaged Möbius shift Δλ² = -⟨τ_h(t)²⟩·(m_j² − μ²) per head.

    Per-head phases are spread by the golden angle (Aletheia convention).
    """
    period = 2.0 * math.pi / BRONZE_ANGLE
    t_span = n_bronze_periods * period
    t = np.linspace(0.0, t_span, n_samples)

    shifts: dict[str, float] = {}
    V = m_j ** 2 - beta_plus_kappa
    for h in range(n_heads):
        phase = (GOLDEN_ANGLE * h) % (2.0 * math.pi)
        tau_t = tau_0 * (1.0 + 0.4 * np.cos(BRONZE_ANGLE * t + phase))
        avg_tau_sq = float(np.mean(tau_t ** 2))
        shifts[f"head_{h}"] = -avg_tau_sq * V
    return shifts


@dataclass(frozen=True)
class BronzeExperimentResult:
    """Outcome of Experiment A."""
    shifts_per_head: dict[str, float]
    relative_spread: float
    matches_lepton_tower: bool
    verdict: str


def run_experiment_A(tau_0: float = 0.5, n_heads: int = 3,
                     m_j: float = 0.5,
                     beta_plus_kappa: float = 0.1) -> BronzeExperimentResult:
    """Run Experiment A and return the result + honest verdict."""
    shifts = bronze_time_averaged_shift_per_head(
        tau_0=tau_0, n_heads=n_heads, m_j=m_j,
        beta_plus_kappa=beta_plus_kappa,
    )
    values = np.array(list(shifts.values()))
    mean_shift = float(np.mean(values))
    spread = float(np.max(values) - np.min(values))
    rel_spread = abs(spread / mean_shift) if mean_shift != 0 else float("inf")
    # For a generation tower, ratios should span ~3477 — i.e., spread/mean ≫ 1.
    matches = rel_spread > 100.0

    if matches:
        verdict = (
            f"Heads split by ratio {rel_spread:.1f} — large enough to "
            f"plausibly produce the lepton tower. Worth deeper analysis."
        )
    else:
        verdict = (
            f"Heads have rel-spread {rel_spread:.4f} — far below the "
            f"~6800 needed to span the lepton tower. The time-average "
            f"⟨τ_h²⟩ = τ_0²·(1 + a²/2) is *phase-independent*; per-head "
            f"phase shifts are washed out by averaging. NEGATIVE RESULT: "
            f"BronzePendulum-driven τ(t) does NOT produce a generation tower."
        )
    return BronzeExperimentResult(
        shifts_per_head=shifts,
        relative_spread=rel_spread,
        matches_lepton_tower=matches,
        verdict=verdict,
    )


# -----------------------------------------------------------------------------
# Experiment B: Chiral Laplacian eigenvalue ratios on a 3-cycle
# -----------------------------------------------------------------------------

def chiral_edge_weight(theta_i: float, theta_j: float,
                       chi: float = 1.0) -> float:
    """Discrete Chern–Simons connection from Alembic:

        w(i→j) = cos(β₃·Δθ) + χ·sin(β₃·Δθ)

    Asymmetric in (i, j); χ = ±1 is the chirality.
    """
    delta = theta_j - theta_i
    return math.cos(BRONZE_RATIO * delta) + chi * math.sin(BRONZE_RATIO * delta)


def chiral_laplacian_3cycle(chi: float = 1.0) -> np.ndarray:
    """Chiral Laplacian for a 3-node cycle with bronze-modulated edges.

    Nodes at θ ∈ {0, 2π/3, 4π/3}.  Returns the 3×3 matrix L = D − A
    where D is the out-degree diagonal and A[i, j] = w(i→j).
    """
    thetas = np.array([0.0, 2.0 * math.pi / 3.0, 4.0 * math.pi / 3.0])
    A = np.zeros((3, 3))
    for i in range(3):
        for j in range(3):
            if i != j:
                A[i, j] = chiral_edge_weight(thetas[i], thetas[j], chi)
    D = np.diag(A.sum(axis=1))
    return D - A


def lepton_mass_ratios_target() -> np.ndarray:
    """Empirical (m_e, m_μ, m_τ) normalised to m_e = 1."""
    from . import generations
    m_e = generations.M_E_MeV
    return np.array([1.0, generations.M_MU_MeV / m_e, generations.M_TAU_MeV / m_e])


@dataclass(frozen=True)
class ChiralLaplacianExperimentResult:
    """Outcome of Experiment B."""
    eigenvalues: np.ndarray
    eigenvalue_ratios: np.ndarray
    lepton_targets: np.ndarray
    log_residual: float
    matches_lepton_tower: bool
    verdict: str


def run_experiment_B() -> ChiralLaplacianExperimentResult:
    """Run Experiment B and return the result + honest verdict."""
    L = chiral_laplacian_3cycle(chi=1.0)
    eigs = np.linalg.eigvals(L)
    # Sort by absolute value (non-Hermitian L can have complex eigs)
    eigs = np.sort_complex(eigs)
    eigs_real = np.array([float(e.real) for e in eigs])
    # Ratios relative to smallest non-zero magnitude
    eigs_abs = np.abs(eigs_real)
    nonzero = eigs_abs[eigs_abs > 1e-9]
    if len(nonzero) == 0:
        ratios = np.zeros(3)
    else:
        ratios = eigs_abs / np.min(nonzero)

    targets = lepton_mass_ratios_target()
    if len(ratios) != 3:
        log_res = float("inf")
        matches = False
    else:
        ratios_sorted = np.sort(ratios)
        targets_sorted = np.sort(targets)
        log_res = float(np.linalg.norm(
            np.log(ratios_sorted + 1e-12) - np.log(targets_sorted + 1e-12)
        ))
        matches = log_res < 0.5  # ~50% on each log-mass

    if matches:
        verdict = (
            f"Chiral Laplacian eigenvalue ratios {ratios} are within "
            f"50%-log of empirical lepton ratios {targets}. Worth deeper exploration."
        )
    else:
        verdict = (
            f"Chiral Laplacian eigenvalues on 3-cycle give ratios "
            f"{[f'{r:.3f}' for r in np.sort(ratios)]}, which don't "
            f"resemble the lepton tower "
            f"{[f'{t:.1f}' for t in np.sort(targets)]}. log-residual = "
            f"{log_res:.2f}. NEGATIVE RESULT: the discrete Chern-Simons "
            f"connection on a 3-cycle does NOT produce the lepton tower."
        )
    return ChiralLaplacianExperimentResult(
        eigenvalues=eigs_real,
        eigenvalue_ratios=ratios,
        lepton_targets=targets,
        log_residual=log_res,
        matches_lepton_tower=matches,
        verdict=verdict,
    )


__all__ = [
    "BRONZE_RATIO", "BRONZE_ANGLE", "GOLDEN_ANGLE",
    "bronze_tau_t", "bronze_time_averaged_shift_per_head",
    "BronzeExperimentResult", "run_experiment_A",
    "chiral_edge_weight", "chiral_laplacian_3cycle",
    "lepton_mass_ratios_target",
    "ChiralLaplacianExperimentResult", "run_experiment_B",
]
