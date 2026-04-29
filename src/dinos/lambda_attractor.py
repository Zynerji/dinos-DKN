"""Lambda_eff vs f_DM Gaussian ansatz (HYPOTHESIS Step 46b).

Honest scope
------------
This module DOES:
  - Implement Grok's proposed ansatz: Lambda_eff(f_DM, A) = Lambda_0 *
    exp(-gamma * (f_DM - f_star)^2) * (1 + kappa * (A - A_0)).
  - Compute Lambda_eff for given inputs.
  - Sweep parameters to show that the Gaussian center f_star is an
    INPUT — it has to be chosen as the answer you want.

This module DOES NOT:
  - Derive f_star = 0.27 from any physics. Replacing 0.27 with any
    value in [0, 1] gives an "attractor" at that value.

Verdict: CURVE-FIT. Marked explicitly.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class LambdaAttractorParams:
    Lambda_0_planck_units: float = 1e-120
    f_star: float = 0.27         # <-- THE ANSWER, hardcoded
    gamma: float = 8.0           # Gaussian width inverse-sq
    A_0: float = 0.48
    kappa: float = 0.6


def lambda_eff(f_DM: float, A: float, params: LambdaAttractorParams = None) -> float:
    """Grok's proposed ansatz."""
    if params is None:
        params = LambdaAttractorParams()
    return float(params.Lambda_0_planck_units
                 * np.exp(-params.gamma * (f_DM - params.f_star) ** 2)
                 * (1.0 + params.kappa * (A - params.A_0)))


def replace_attractor_center(new_center: float = 0.45) -> LambdaAttractorParams:
    """Demonstrate that the attractor center is a free parameter.
    Replace 0.27 with new_center; the same Gaussian shape gives a peak
    at new_center."""
    return LambdaAttractorParams(f_star=new_center)


@dataclass(frozen=True)
class AttractorScanReport:
    f_DM_grid: np.ndarray
    lambda_grid: np.ndarray
    peak_at: float
    requested_center: float
    notes: str


def scan_lambda_vs_fDM(params: LambdaAttractorParams = None,
                        A: float = 0.48,
                        n_grid: int = 100) -> AttractorScanReport:
    if params is None:
        params = LambdaAttractorParams()
    f_grid = np.linspace(0.05, 0.95, n_grid)
    L = np.array([lambda_eff(f, A, params) for f in f_grid])
    peak_at = float(f_grid[np.argmax(L)])
    return AttractorScanReport(
        f_DM_grid=f_grid,
        lambda_grid=L,
        peak_at=peak_at,
        requested_center=float(params.f_star),
        notes=("Peak at the same value as f_star (the ansatz center). "
               "The 'attractor' is an algebraic identity of the Gaussian "
               "shape — no physics is being derived. Sweep f_star to see "
               "the peak move."),
    )


__all__ = [
    "LambdaAttractorParams", "lambda_eff",
    "replace_attractor_center",
    "AttractorScanReport", "scan_lambda_vs_fDM",
]
