"""PMNS matrix from left-handed polar overlaps (HYPOTHESIS Step 42b).

Honest scope
------------
This module DOES:
  - Compute the PMNS-style overlap matrix U_ij from a parameterised
    left-handed-only polar mode ansatz.
  - Allow a different basis for charged-lepton vs neutrino sectors,
    parameterised by an offset alpha.
  - Fit alpha against observed PMNS magnitudes; report best error.

This module DOES NOT:
  - Predict the large PMNS mixing angles from the framework. Grok
    claimed sub-percent matches; we show the simple ansatz cannot.
  - Predict delta_CP for neutrinos.

Verdict: UNDERSPECIFIED, same as CKM.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import pi

import numpy as np
from scipy.integrate import quad
from scipy.optimize import minimize


# Observed PMNS magnitudes (rough 2025 global fit, normal hierarchy)
PMNS_OBSERVED = np.array([
    [0.825, 0.546, 0.149],
    [0.391, 0.624, 0.677],
    [0.408, 0.560, 0.722],
])


def psi_charged_lepton(theta: float, n: int) -> float:
    """Charged-lepton mass-eigenstate polar mode (sine basis)."""
    return np.sin((n + 1) * theta) * np.sqrt(2.0 / pi)


def psi_neutrino(theta: float, n: int, alpha: float) -> float:
    """Neutrino mass-eigenstate polar mode shifted by alpha."""
    arg = (n + 1) * (theta - alpha)
    return np.sin(arg) * np.sqrt(2.0 / pi)


def pmns_overlap_matrix(alpha: float) -> np.ndarray:
    """U_ij = ∫_0^pi psi_charged(theta, i) psi_neutrino(theta, j, alpha) dθ."""
    U = np.zeros((3, 3))
    for i in range(3):
        for j in range(3):
            integrand = lambda t, ii=i, jj=j: psi_charged_lepton(t, ii) * psi_neutrino(t, jj, alpha)
            U[i, j], _ = quad(integrand, 0.0, pi)
    return np.abs(U)


@dataclass(frozen=True)
class PMNSFitReport:
    alpha_best: float
    matrix_predicted: np.ndarray
    rel_error_frobenius: float
    theta_23_predicted_deg: float
    theta_23_observed_deg: float
    notes: str


def fit_pmns(alpha_init: float = 0.4) -> PMNSFitReport:
    """Find alpha that minimises Frobenius error vs observed PMNS."""
    obs = PMNS_OBSERVED

    def loss(a):
        U = pmns_overlap_matrix(float(a[0]))
        return float(np.linalg.norm(U - obs))

    res = minimize(loss, [alpha_init], method="Nelder-Mead")
    alpha_best = float(res.x[0])
    U_pred = pmns_overlap_matrix(alpha_best)
    err = float(np.linalg.norm(U_pred - obs) / np.linalg.norm(obs))
    if abs(U_pred[2, 2]) < 1e-12:
        theta23 = float("nan")
    else:
        theta23 = float(np.degrees(np.arctan(abs(U_pred[1, 2]) / abs(U_pred[2, 2]))))
    return PMNSFitReport(
        alpha_best=alpha_best,
        matrix_predicted=U_pred,
        rel_error_frobenius=err,
        theta_23_predicted_deg=theta23,
        theta_23_observed_deg=49.1,
        notes=("Simple sine-mode ansatz fit. Same caveats as CKM: the "
               "framework does not specify the wavefunctions. Sub-percent "
               "agreement to PMNS angles requires bespoke ansatz that "
               "has not been derived from the Möbius geometry."),
    )


__all__ = [
    "PMNS_OBSERVED", "psi_charged_lepton", "psi_neutrino",
    "pmns_overlap_matrix", "PMNSFitReport", "fit_pmns",
]
