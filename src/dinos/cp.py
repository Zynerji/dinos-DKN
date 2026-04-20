"""Chandrasekhar–Page (CP) angular eigenvalues on a Kerr background.

Paper §4, Appendix B.

Flat-space limit (aω, aμ → 0):

    λ_CP² = k²,     |k| = j + ½,     j ∈ {½, 3/2, …}      [Prop. 4.1]

Rayleigh–Schrödinger expansion in (aω, aμ) (eq. 88):

    λ_CP² = k² − ½ a² (ω² − μ²) + O((aω)⁴)

For exact values one solves the second-order ODE (eq. 87):

    ∂_x[(1−x²) ∂_x S₊] + [a²(ω² − μ²)(1−x²)
        − (m_j − ½)² / (1 − x²) + λ_CP² + ¼] S₊ = 0,    x = cos θ

with regularity at x = ±1. We provide a shooting-based solver for that.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import sqrt

import numpy as np
from scipy.integrate import solve_ivp
from scipy.optimize import brentq


# -----------------------------------------------------------------------------
# Closed-form limits
# -----------------------------------------------------------------------------

def k_from_j(j: float, parity: int = +1) -> int:
    """|k| = j + ½, with sign set by parity (Proposition 4.1).

    j = l − ½  ⇒  k > 0;   j = l + ½  ⇒  k < 0.
    """
    if (j - 0.5) != round(j - 0.5):
        raise ValueError("j must be half-integer (½, 3/2, …)")
    if parity not in (+1, -1):
        raise ValueError("parity must be ±1")
    return int(parity * (int(j + 0.5)))


def lambda_CP_flat(k: int) -> float:
    """Flat-space eigenvalue |λ_CP| = |k|."""
    return float(abs(k))


def lambda_CP_leading(k: int, a: float, omega: float, mu: float) -> float:
    """Leading Rayleigh–Schrödinger correction (eq. 88):

    λ_CP² = k² − ½ a² (ω² − μ²) + O((aω)⁴).

    Returns the positive root.
    """
    lam2 = k * k - 0.5 * a * a * (omega * omega - mu * mu)
    if lam2 <= 0:
        raise ValueError("a² (ω² − μ²) term inverted sign of λ_CP²; out of perturbative range")
    return sqrt(lam2)


# -----------------------------------------------------------------------------
# Exact ODE solver (Appendix B, eq. 87)
# -----------------------------------------------------------------------------

@dataclass
class CPProblem:
    m_j: float    # azimuthal quantum number (half-integer)
    a: float      # Kerr rotation parameter
    omega: float  # mode frequency
    mu: float     # Dirac mass (natural units)

    def rhs(self, x: float, S: np.ndarray, lam_CP_sq: float):
        """Second-order ODE (87) written as a first-order system.

        S = [S₊, S₊']
        (1 − x²) S'' − 2x S' + [a²(ω² − μ²)(1 − x²)
            − (m_j − ½)² / (1 − x²) + λ_CP² + ¼] S = 0.
        """
        one_minus_x2 = 1.0 - x * x
        if abs(one_minus_x2) < 1e-14:
            one_minus_x2 = 1e-14 if one_minus_x2 >= 0 else -1e-14
        prefactor = (
            self.a ** 2 * (self.omega ** 2 - self.mu ** 2) * one_minus_x2
            - (self.m_j - 0.5) ** 2 / one_minus_x2
            + lam_CP_sq + 0.25
        )
        Sp_prime = (2.0 * x * S[1] - prefactor * S[0]) / one_minus_x2
        return np.array([S[1], Sp_prime])


def _shoot(problem: CPProblem, lam_CP_sq: float,
           x0: float = -1.0 + 1e-6, x1: float = 1.0 - 1e-6) -> float:
    """Integrate from x₀ toward x₁ with regular-at-−1 initial conditions;
    return the value of S at x₁.  Zero of this function ⇒ eigenvalue."""
    def rhs(x, y):
        return problem.rhs(x, y, lam_CP_sq)

    # Frobenius ansatz near x = −1: S ~ (1 + x)^((m_j−½)/2)
    # We just start from a small regular value and an analytic first derivative.
    S0 = 1.0
    S0_prime = 0.5 * (problem.m_j - 0.5) / (1.0 + x0)
    sol = solve_ivp(rhs, [x0, x1], [S0, S0_prime], rtol=1e-8, atol=1e-10, max_step=0.01)
    return sol.y[0, -1]


def solve_cp_exact(m_j: float, a: float, omega: float, mu: float,
                   k_guess: int = 1, bracket: tuple[float, float] | None = None) -> float:
    """Shoot-and-match solve for λ_CP² using a bracket around the flat-space eigenvalue.

    Returns |λ_CP| (positive root).
    """
    prob = CPProblem(m_j=m_j, a=a, omega=omega, mu=mu)
    lam0_sq = float(k_guess) ** 2
    if bracket is None:
        bracket = (max(1e-6, 0.25 * lam0_sq), 4.0 * lam0_sq)

    def f(lam_sq: float) -> float:
        return _shoot(prob, lam_sq)

    root = brentq(f, bracket[0], bracket[1], xtol=1e-6)
    return sqrt(root)


__all__ = [
    "k_from_j", "lambda_CP_flat", "lambda_CP_leading",
    "CPProblem", "solve_cp_exact",
]
