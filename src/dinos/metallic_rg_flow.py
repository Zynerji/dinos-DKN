"""Metallic RG flow integrator (Algorithm #15 from ch.txt; HYPOTHESIS Step 51b).

Honest scope
------------
This module DOES:
  - Numerically integrate the conjectured beta function
    β(b) = b(1 - b^2)(b^2 - φ^-2)(b^2 - φ^2)
    proposed in ch.txt Algorithm #15.
  - Identify its zeros (fixed points) and classify their stability.
  - Run the flow b(μ) for given starting (b₀, μ₀) and target μ₁.

This module DOES NOT:
  - Justify the form of β(b). The conjecture in ch.txt is that the
    metallic invariant runs with energy scale; the specific quartic
    polynomial with zeros at {0, 1, φ⁻¹, φ} is not derived from any
    quantum field theory in the framework.
  - Predict the running of the SM gauge couplings. Until the metallic
    invariant is connected to a specific QFT coupling (it is not),
    this RG flow has no physical content.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from . import metallic_invariant_sweep as mis


@dataclass(frozen=True)
class RGFlowReport:
    b_initial: float
    log_mu_initial: float
    log_mu_final: float
    b_final: float
    n_steps: int
    notes: str


def beta_metallic(b: float, phi: float = mis.GOLDEN) -> float:
    """Conjectured β-function from ch.txt #15:
       β(b) = b(1 - b^2)(b^2 - φ^-2)(b^2 - φ^2)
    where φ is the golden ratio."""
    return float(b * (1 - b * b) * (b * b - phi ** (-2)) * (b * b - phi ** 2))


def fixed_points(phi: float = mis.GOLDEN) -> list[float]:
    """Zeros of β: {0, 1, φ⁻¹, φ}."""
    return [0.0, 1.0, 1.0 / phi, phi]


def classify_fixed_point(b_star: float, phi: float = mis.GOLDEN,
                          h: float = 1e-6) -> str:
    """Classify by sign of β'(b_star)."""
    deriv = (beta_metallic(b_star + h, phi) -
             beta_metallic(b_star - h, phi)) / (2 * h)
    if deriv > 1e-10:
        return "UV (unstable)"
    elif deriv < -1e-10:
        return "IR (stable)"
    else:
        return "marginal"


def integrate_rg_flow(b_init: float, log_mu_init: float = 0.0,
                       log_mu_final: float = 10.0,
                       n_steps: int = 1000,
                       phi: float = mis.GOLDEN) -> RGFlowReport:
    """RK4 integration of db/d(log μ) = β(b)."""
    b = float(b_init)
    log_mu = float(log_mu_init)
    h = (log_mu_final - log_mu_init) / n_steps
    for _ in range(n_steps):
        k1 = beta_metallic(b, phi)
        k2 = beta_metallic(b + 0.5 * h * k1, phi)
        k3 = beta_metallic(b + 0.5 * h * k2, phi)
        k4 = beta_metallic(b + h * k3, phi)
        b = b + (h / 6.0) * (k1 + 2 * k2 + 2 * k3 + k4)
        log_mu += h
        # Numerical safety: clamp to avoid blow-up
        if abs(b) > 100:
            b = float(np.sign(b) * 100)
            break
    return RGFlowReport(
        b_initial=float(b_init),
        log_mu_initial=float(log_mu_init),
        log_mu_final=float(log_mu),
        b_final=float(b),
        n_steps=n_steps,
        notes=("RK4 integration of conjectured β(b). Physical content of "
               "this β-function is not established by the framework."),
    )


def fixed_point_classification() -> dict:
    """Classify all four fixed points of β."""
    fps = fixed_points()
    return {
        f"b = {b:.4f}": classify_fixed_point(b)
        for b in fps
    }


__all__ = [
    "RGFlowReport", "beta_metallic", "fixed_points",
    "classify_fixed_point", "integrate_rg_flow",
    "fixed_point_classification",
]
