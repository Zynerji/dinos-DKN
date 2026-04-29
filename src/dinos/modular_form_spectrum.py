"""Modular form mass spectrum generator (Algorithm #19; HYPOTHESIS Step 51c).

Honest scope
------------
This module DOES:
  - Construct a parameterised q-expansion f(τ) = Σ a_n q^n with q = exp(2πiτ)
    given input coefficient generators (a_0, b, φ).
  - Compute mass tower via m_n ∝ √a_n.
  - Provide the toy machinery to test ch.txt #19's claim that "Foot
    triplets are modular forms."

This module DOES NOT:
  - Produce a true modular form. Modular invariance under SL(2,ℤ)
    requires specific transformation rules that this q-expansion does
    not satisfy unless the coefficients are chosen carefully (e.g.,
    Eisenstein series, theta series). The ch.txt suggestion that
    "imposing metallic constraint a_1/a_0 = b" gives a modular form
    is not a derivation — generic recursions do not produce modular forms.
  - Predict physical masses. The mass tower m_n is a free parameterised
    family until the coefficient recursion is constrained by genuine
    physics.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class ModularSpectrumReport:
    a_0: float
    b: float
    phi: float
    n_terms: int
    coefficients: np.ndarray
    mass_tower: np.ndarray
    notes: str


def foot_constrained_recursion(a_0: float = 1.0,
                                 b: float = 0.05,
                                 phi: float = 0.5,
                                 n_terms: int = 16) -> np.ndarray:
    """Generate a_n via the Foot-style recursion:
    a_{n+1} = a_n * (1 + b * cos(phi + n * 2π/3))^2
    inspired by the Foot mass formula. NOT a modular form — just a
    real recursion that generates a tower."""
    a = np.zeros(n_terms)
    a[0] = a_0
    for n in range(n_terms - 1):
        factor = (1.0 + b * np.cos(phi + n * 2 * np.pi / 3)) ** 2
        a[n + 1] = a[n] * factor
    return a


def mass_spectrum_from_coefficients(coeffs: np.ndarray,
                                      mass_scale_MeV: float = 1.0) -> np.ndarray:
    """Mass tower m_n ∝ √a_n (with chosen overall scale)."""
    nonneg = np.maximum(coeffs, 0.0)
    return mass_scale_MeV * np.sqrt(nonneg)


def modular_spectrum(a_0: float = 1.0, b: float = 0.05,
                       phi: float = 0.5, n_terms: int = 16,
                       mass_scale_MeV: float = 1.0) -> ModularSpectrumReport:
    coeffs = foot_constrained_recursion(a_0, b, phi, n_terms)
    masses = mass_spectrum_from_coefficients(coeffs, mass_scale_MeV)
    return ModularSpectrumReport(
        a_0=float(a_0), b=float(b), phi=float(phi),
        n_terms=int(n_terms),
        coefficients=coeffs,
        mass_tower=masses,
        notes=("Toy q-expansion-style coefficient recursion inspired by "
               "the Foot formula. NOT a modular form unless additional "
               "constraints from SL(2,Z) invariance are imposed. The "
               "predicted mass tower is a free-parameter family; "
               "physical content requires further constraints not derived here."),
    )


__all__ = [
    "ModularSpectrumReport",
    "foot_constrained_recursion",
    "mass_spectrum_from_coefficients",
    "modular_spectrum",
]
