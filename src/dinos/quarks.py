"""Quark sector scaffold (HYPOTHESIS Step 6b).

Extends the closure to handle:

1. **Fractional EM charges**: replace ``α`` in the closure with
   ``q²·α`` where ``q ∈ {±2/3, ±1/3}``.
2. **Color Casimir scaffold**: SU(3) Casimir for confined gluon
   field in a bag.  Provides a single ``C_color`` to add to the
   electromagnetic ``C_bag`` term.
3. **Per-quark calibration**: like Step 6a for leptons, the quark
   masses are *fitted*, not predicted, by adjusting σ_q.

Honest scope statement
----------------------
- This module CAN: extend the closure to fractional charges + color
  Casimir; calibrate σ_q per quark.
- This module CANNOT: predict quark masses, derive the CKM matrix,
  implement confinement (bag is the wrong soliton object), or
  produce running couplings.

Confinement specifically requires a string-like / flux-tube soliton
that is structurally beyond the bag construction.  This scaffold
treats quarks as if they were free (current quark mass parameters);
it cannot describe constituent or pole masses without the missing
confinement physics.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import pi

import numpy as np

from . import constants as C, closure


# -----------------------------------------------------------------------------
# Empirical quark masses (PDG 2022 — current quark, MS-bar at 2 GeV unless noted)
# -----------------------------------------------------------------------------

QUARK_MASSES_MeV: dict[str, float] = {
    "u": 2.16,         # up
    "d": 4.67,         # down
    "s": 93.4,         # strange
    "c": 1273.0,       # charm  (running, m_c(m_c))
    "b": 4180.0,       # bottom (running, m_b(m_b))
    "t": 172700.0,     # top    (pole)
}

QUARK_CHARGES: dict[str, float] = {
    "u":  2.0 / 3.0,
    "d": -1.0 / 3.0,
    "s": -1.0 / 3.0,
    "c":  2.0 / 3.0,
    "b": -1.0 / 3.0,
    "t":  2.0 / 3.0,
}


# -----------------------------------------------------------------------------
# SU(3) color Casimir (scaffold)
# -----------------------------------------------------------------------------

# Quadratic Casimir in fundamental representation: C_F = (N²-1)/(2N) for SU(N)
C_F_SU3: float = 4.0 / 3.0       # SU(3) fundamental Casimir
C_A_SU3: float = 3.0             # SU(3) adjoint Casimir (= N for SU(N))


def color_casimir_scaffold(N_dof_color: int = 3,
                           c_per_dof: float = C.C_bag_Dirac) -> float:
    """Order-of-magnitude scaffold for the color contribution to the bag
    Casimir.

    For a quark confined in a bag, the QCD vacuum contributes a
    color-Casimir-like term scaling as ``N_dof_color · c_per_dof``.
    For a single confined Dirac with 3 colors at the same per-dof
    Casimir as the EM bag: ``C_color ≈ 3 · 0.177 ≈ 0.53``.

    This is a SCAFFOLD — the actual QCD bag Casimir requires the full
    gluon-mode sum, which is beyond this module's scope.  The scaffold
    is provided for dimensional/structural exploration.
    """
    return float(N_dof_color * c_per_dof)


# -----------------------------------------------------------------------------
# Closure with fractional EM charge + color Casimir
# -----------------------------------------------------------------------------

def quark_closure_residue(C_em: float, C_color: float, q_charge: float,
                          alpha: float = C.alpha_EM) -> float:
    """Generalised residue ``r_q = 1 − 2(C_em + C_color) − q²·α``."""
    return 1.0 - 2.0 * (C_em + C_color) - (q_charge ** 2) * alpha


def quark_mass_from_sigma(sigma_MeV3: float, C_em: float, C_color: float,
                          q_charge: float,
                          alpha: float = C.alpha_EM) -> float:
    """``m_q = (π σ_q / r_q)^{1/3}``  in MeV."""
    r = quark_closure_residue(C_em, C_color, q_charge, alpha)
    if r <= 0.0:
        raise ValueError(f"residue ≤ 0 (= {r}); closure inadmissible")
    return (pi * sigma_MeV3 / r) ** (1.0 / 3.0)


def sigma_for_quark_mass(m_q_MeV: float, C_em: float, C_color: float,
                         q_charge: float,
                         alpha: float = C.alpha_EM) -> float:
    """Inverse: ``σ_q = m_q³ · r_q / π``  given the closure parameters."""
    r = quark_closure_residue(C_em, C_color, q_charge, alpha)
    if r <= 0.0:
        raise ValueError(f"residue ≤ 0 (= {r})")
    return float(m_q_MeV ** 3 * r / pi)


def per_quark_sigmas(C_em: float = C.C_bag_Dirac,
                     C_color: float | None = None,
                     alpha: float = C.alpha_EM) -> dict[str, float]:
    """σ_q for each empirical quark mass.

    If ``C_color`` is None, uses :func:`color_casimir_scaffold`.
    """
    if C_color is None:
        C_color = color_casimir_scaffold()
    out: dict[str, float] = {}
    for q_name, m in QUARK_MASSES_MeV.items():
        try:
            out[q_name] = sigma_for_quark_mass(
                m, C_em=C_em, C_color=C_color,
                q_charge=QUARK_CHARGES[q_name], alpha=alpha,
            )
        except ValueError as e:
            out[q_name] = float("nan")
    return out


# -----------------------------------------------------------------------------
# Diagnostic: cross-quark σ ratios
# -----------------------------------------------------------------------------

@dataclass(frozen=True)
class QuarkCalibrationReport:
    sigmas_MeV3: dict[str, float]
    log_sigma_range: float
    closure_admissible: bool
    notes: str


def quark_calibration_report(C_em: float = C.C_bag_Dirac,
                             C_color: float | None = None) -> QuarkCalibrationReport:
    """Summarise per-quark σ values and whether the closure remains
    admissible (residue > 0) for all six quarks."""
    sigmas = per_quark_sigmas(C_em=C_em, C_color=C_color)
    finite = {q: s for q, s in sigmas.items() if np.isfinite(s)}
    if not finite:
        return QuarkCalibrationReport(
            sigmas_MeV3=sigmas, log_sigma_range=float("inf"),
            closure_admissible=False,
            notes="closure inadmissible for ALL quarks at given (C_em, C_color)",
        )
    log_vals = np.array([np.log(s) for s in finite.values()])
    log_range = float(log_vals.max() - log_vals.min())
    notes = (
        f"σ spans {log_range:.2f} in natural log across "
        f"{len(finite)}/{len(sigmas)} quarks. "
        f"σ_q is calibrated per quark — not predicted."
    )
    return QuarkCalibrationReport(
        sigmas_MeV3=sigmas,
        log_sigma_range=log_range,
        closure_admissible=(len(finite) == len(sigmas)),
        notes=notes,
    )


__all__ = [
    "QUARK_MASSES_MeV", "QUARK_CHARGES",
    "C_F_SU3", "C_A_SU3", "color_casimir_scaffold",
    "quark_closure_residue", "quark_mass_from_sigma", "sigma_for_quark_mass",
    "per_quark_sigmas",
    "QuarkCalibrationReport", "quark_calibration_report",
]
