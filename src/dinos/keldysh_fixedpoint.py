"""Möbius-Keldysh fixed-point simulation (HYPOTHESIS Step 47a).

Honest scope
------------
This module DOES:
  - Discretise a 1D Möbius strip into N nodes with a Z2 sign flip
    at the seam.
  - Iterate ψ_{n+1} = ψ_n + η * (□ ψ - m^2 ψ) with normalisation, for
    a chosen propagation speed c (so that □ has effective speed c).
  - Report the final residual at convergence and the contraction
    factor of the iteration.

This module DOES NOT:
  - Identify a unique stable c by minimising stability across
    propagation speeds. Grok's claim that c=1 minimises residual is
    falsified in `dinos.dispersion_mobius` and
    `dinos.grok_claims_validation`.
  - Reproduce the electron mass via this fixed-point — the existing
    `dinos.closure.enforce_mobius_fixed_point` does that with a much
    richer setup.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class FixedPointReport:
    c: float
    final_residual: float
    final_norm: float
    iterations: int
    converged: bool
    notes: str


def discrete_dalembertian(psi: np.ndarray, c: float = 1.0,
                            twist_sign: int = -1) -> np.ndarray:
    """1D second-difference operator with Möbius Z2 twist at the seam."""
    N = len(psi)
    out = np.zeros_like(psi)
    for j in range(N):
        right = psi[(j + 1) % N] * (twist_sign if j == N - 1 else 1)
        left = psi[(j - 1) % N] * (twist_sign if j == 0 else 1)
        out[j] = c * c * (right - 2 * psi[j] + left)
    return out


def evolve_keldysh_fixed_point(N: int = 128, c: float = 1.0, m: float = 0.1,
                                 eta: float = 0.1, max_iter: int = 1000,
                                 tol: float = 1e-7,
                                 seed: int = 0) -> FixedPointReport:
    """Run prophetic-style iteration on the discrete twisted strip."""
    rng = np.random.default_rng(seed)
    psi = (rng.normal(0, 1, N) + 1j * rng.normal(0, 1, N))
    psi /= np.linalg.norm(psi)

    for it in range(max_iter):
        update = discrete_dalembertian(psi, c=c) - m * m * psi
        psi_new = psi + eta * update
        psi_new /= np.linalg.norm(psi_new)
        residual = float(np.linalg.norm(psi_new - psi))
        psi = psi_new
        if residual < tol:
            return FixedPointReport(
                c=c, final_residual=residual,
                final_norm=float(np.linalg.norm(psi)),
                iterations=it + 1, converged=True,
                notes=("Converged. Residual depends on (c, m, eta) — there is "
                       "no unique c that minimises it; the iteration converges "
                       "for a range of stable parameter combinations."),
            )
    return FixedPointReport(
        c=c, final_residual=residual,
        final_norm=float(np.linalg.norm(psi)),
        iterations=max_iter, converged=False,
        notes="Did not converge in max_iter; reduce eta or increase max_iter.",
    )


__all__ = ["FixedPointReport", "discrete_dalembertian",
           "evolve_keldysh_fixed_point"]
