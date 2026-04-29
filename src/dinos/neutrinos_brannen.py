"""Neutrino sector — Foot ansatz prediction (HYPOTHESIS Step 12a).

Tests whether the Foot ansatz with b = sqrt(2) (universal across
charged leptons) extends to neutrinos, given the empirical
mass-squared differences from oscillation experiments.

Empirical neutrino oscillation parameters (PDG 2022, normal ordering):
    Delta m_21^2 = 7.39e-5 eV^2  (solar)
    |Delta m_31^2| = 2.523e-3 eV^2 (atmospheric)
    Cosmological bound: Sum m_nu < 0.12 eV (Planck 2018 + BAO).

Construction
------------
With b = sqrt(2) fixed (lepton-universal), 2 free parameters (a, phi)
match 2 constraints (Delta m_21^2, Delta m_31^2) — system is uniquely
solvable.

Result (at empirical Delta m^2):
    m_1 = 0.000357 eV    (lightest)
    m_2 = 0.00860 eV
    m_3 = 0.0502 eV
    Sum m_nu = 0.0592 eV   (well within Planck bound 0.12 eV)

Branch difference from charged leptons
--------------------------------------
At the converged neutrino phi (~ 0.477 rad), one of the three
(1 + b cos(phi + 2*pi*l/3)) factors is NEGATIVE. The Foot mass
m_l = a(1 + b cos)^2 is still positive (it's a square), but the
sum-of-square-roots Sum sqrt(m_l) is NO LONGER 3*sqrt(a) — so the
Koide identity Q = 3/2 does NOT hold for neutrinos.

Charged leptons live in the *all-positive branch* of Foot;
neutrinos live in the *one-sign-flip branch*. Same algebraic
structure (Z_3 cover, b = sqrt(2)), different sign sector.

Predictions
-----------
- Lightest neutrino: 0.000357 eV (~ 0.36 meV).
- Heaviest neutrino: 0.0502 eV (~ 50 meV).
- Sum: 0.059 eV — testable against future cosmological surveys
  (Euclid, DESI, CMB-S4 target sigma ~ 0.02 eV).

If future cosmology measures Sum m_nu = 0.059 +/- 0.02 eV → consistent.
If Sum m_nu < 0.04 eV or > 0.10 eV → framework excluded.

Honest scope statement
----------------------
- This module DERIVES neutrino mass scale FROM Delta m^2 + (Foot ansatz
  + b = sqrt(2)).
- The framework is consistent with neutrino oscillation data.
- It does NOT explain Dirac vs Majorana, mass ordering (assumes normal),
  or CP violation in the PMNS matrix.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import cos, pi, sqrt

import numpy as np
from scipy.optimize import fsolve


# Empirical neutrino oscillation parameters (PDG 2022, normal ordering)
DELTA_M21_SQ_eV2: float = 7.39e-5
DELTA_M31_SQ_ABS_eV2: float = 2.523e-3
PLANCK_SUM_BOUND_eV: float = 0.12   # 95% CL upper bound (Planck 2018 + BAO)


def foot_masses(a: float, b: float, phi: float) -> np.ndarray:
    """Three Foot masses m_l = a (1 + b cos((l-1)*2pi/3 + phi))^2.

    Returns sorted ascending (lightest to heaviest)."""
    cos_vals = np.array([cos(l * 2 * pi / 3 + phi) for l in range(3)])
    masses = a * (1 + b * cos_vals) ** 2
    return np.sort(masses)


def solve_foot_for_neutrinos(
    delta_m21_sq: float = DELTA_M21_SQ_eV2,
    delta_m31_sq: float = DELTA_M31_SQ_ABS_eV2,
    b: float = sqrt(2.0),
    phi_init: float = 0.4,
    a_init: float = 0.01,
) -> tuple[float, float, np.ndarray]:
    """Solve the Foot ansatz for neutrino masses given Δm² constraints.

    Returns (a, phi, masses_sorted_eV).
    """
    def equations(params):
        a, phi = params
        m = foot_masses(a, b, phi)
        return [
            m[1] ** 2 - m[0] ** 2 - delta_m21_sq,
            m[2] ** 2 - m[0] ** 2 - delta_m31_sq,
        ]
    sol, info, ier, msg = fsolve(
        equations, [a_init, phi_init], full_output=True,
    )
    if ier != 1:
        raise RuntimeError(f"fsolve failed: {msg}")
    a_sol, phi_sol = sol
    masses = foot_masses(a_sol, b, phi_sol)
    return float(a_sol), float(phi_sol), masses


def count_negative_foot_factors(b: float, phi: float) -> int:
    """Count how many of the three (1 + b cos(phi + (l-1)*2*pi/3))
    factors are negative. Charged leptons: 0 (all positive); neutrinos: 1.
    """
    n = 0
    for l in range(3):
        if (1 + b * cos(l * 2 * pi / 3 + phi)) < 0:
            n += 1
    return n


# -----------------------------------------------------------------------------
# Verdict
# -----------------------------------------------------------------------------

@dataclass(frozen=True)
class NeutrinoFootReport:
    """Aggregate Foot prediction for neutrino sector."""
    a_eV: float
    phi_rad: float
    b_assumed: float
    m_1_eV: float
    m_2_eV: float
    m_3_eV: float
    sum_m_eV: float
    sum_within_planck: bool
    n_negative_foot_factors: int
    koide_q: float
    notes: str


def neutrino_prediction_report() -> NeutrinoFootReport:
    """Compile the Foot-derived neutrino mass prediction."""
    a, phi, masses = solve_foot_for_neutrinos()
    sum_m = float(masses.sum())
    n_neg = count_negative_foot_factors(sqrt(2.0), phi)
    sqrt_m = np.sqrt(masses)
    Q = float((sqrt_m.sum() ** 2) / sum_m)
    notes = (
        f"Foot ansatz with b = sqrt(2) and Delta m^2 constraints predicts "
        f"neutrino masses (m_1, m_2, m_3) = ({masses[0]:.4e}, "
        f"{masses[1]:.4e}, {masses[2]:.4e}) eV, Sum = {sum_m:.4f} eV. "
        f"This sits {'within' if sum_m < PLANCK_SUM_BOUND_eV else 'outside'} "
        f"the Planck bound 0.12 eV. {n_neg} of 3 Foot factors negative "
        f"(charged leptons: 0, all positive). Koide Q = {Q:.4f} "
        f"(charged leptons: 3/2; neutrinos in different branch)."
    )
    return NeutrinoFootReport(
        a_eV=a,
        phi_rad=phi,
        b_assumed=sqrt(2.0),
        m_1_eV=float(masses[0]),
        m_2_eV=float(masses[1]),
        m_3_eV=float(masses[2]),
        sum_m_eV=sum_m,
        sum_within_planck=(sum_m < PLANCK_SUM_BOUND_eV),
        n_negative_foot_factors=n_neg,
        koide_q=Q,
        notes=notes,
    )


__all__ = [
    "DELTA_M21_SQ_eV2", "DELTA_M31_SQ_ABS_eV2", "PLANCK_SUM_BOUND_eV",
    "foot_masses", "solve_foot_for_neutrinos",
    "count_negative_foot_factors",
    "NeutrinoFootReport", "neutrino_prediction_report",
]
