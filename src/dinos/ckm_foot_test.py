"""CKM matrix vs Foot structure (HYPOTHESIS Step 12b).

Scaffold testing whether CKM Wolfenstein parameters fit any Foot-like
structure. Honest result: NO, beyond noting that the Cabibbo angle is
suspiciously close to but distinct from the lepton Foot angle.

Empirical CKM (Wolfenstein parameterisation, PDG 2022):
    lambda     = sin(theta_C) ~ 0.2253
    A          ~ 0.836
    rho_bar    ~ 0.155
    eta_bar    ~ 0.34

Honest scope statement
----------------------
- This module CAN: compute the gap between Cabibbo angle and lepton phi,
  test simple Foot-like fits to CKM angles.
- This module CANNOT: derive any CKM parameter. The CKM matrix has
  4 free parameters with no known Koide-like formula relating them.
- VERDICT: Foot structure does NOT extend to CKM directly. Cabibbo
  angle is close to but distinct from lepton phi (gap 0.30 deg).
"""

from __future__ import annotations

from dataclasses import dataclass
from math import asin, sin

import numpy as np

# CKM Wolfenstein parameters (PDG 2022)
WOLFENSTEIN_LAMBDA: float = 0.2253
WOLFENSTEIN_A: float = 0.836
WOLFENSTEIN_RHO_BAR: float = 0.155
WOLFENSTEIN_ETA_BAR: float = 0.34

# Derived: Cabibbo angle in radians
THETA_CABIBBO_RAD: float = float(asin(WOLFENSTEIN_LAMBDA))   # ~ 0.2272
THETA_CABIBBO_DEG: float = float(np.degrees(THETA_CABIBBO_RAD))

# Lepton Foot angle (resolved as 2/9 within 1 sigma in Step 11)
LEPTON_PHI_RAD: float = 2.0 / 9.0


@dataclass(frozen=True)
class CKMFootReport:
    cabibbo_rad: float
    lepton_phi_rad: float
    gap_rad: float
    gap_deg: float
    relative_gap_pct: float
    sin_lepton_phi: float
    foot_extension_works: bool
    notes: str


def cabibbo_lepton_gap_report() -> CKMFootReport:
    """Quantitative comparison of Cabibbo angle to lepton Foot phi = 2/9."""
    gap_rad = THETA_CABIBBO_RAD - LEPTON_PHI_RAD
    gap_deg = float(np.degrees(gap_rad))
    rel_pct = abs(gap_rad / LEPTON_PHI_RAD) * 100
    sin_phi = float(sin(LEPTON_PHI_RAD))
    sin_diff = sin_phi - WOLFENSTEIN_LAMBDA
    # Tight tolerance: 0.001 (well below experimental λ uncertainty ~0.0007)
    works = abs(sin_diff) < 0.001
    notes = (
        f"theta_Cabibbo = {THETA_CABIBBO_DEG:.4f} deg "
        f"(= asin({WOLFENSTEIN_LAMBDA})). "
        f"Lepton Foot phi = 2/9 rad = {np.degrees(LEPTON_PHI_RAD):.4f} deg. "
        f"Gap = {gap_deg:.4f} deg ({rel_pct:.2f}% relative). "
        f"sin(2/9) = {sin_phi:.4f} vs Wolfenstein lambda = {WOLFENSTEIN_LAMBDA} "
        f"(difference: {sin_diff:+.4f}, ~ 2.2%). "
        f"VERDICT: Foot extension to CKM does NOT work as exact identity; "
        f"sin(2/9) is within 2% of lambda, suggestive but outside "
        f"experimental uncertainty (~0.3% on lambda). Likely a near-miss "
        f"with sub-leading corrections, not a clean derivation."
    )
    return CKMFootReport(
        cabibbo_rad=THETA_CABIBBO_RAD,
        lepton_phi_rad=LEPTON_PHI_RAD,
        gap_rad=gap_rad,
        gap_deg=gap_deg,
        relative_gap_pct=rel_pct,
        sin_lepton_phi=sin_phi,
        foot_extension_works=works,
        notes=notes,
    )


__all__ = [
    "WOLFENSTEIN_LAMBDA", "WOLFENSTEIN_A",
    "WOLFENSTEIN_RHO_BAR", "WOLFENSTEIN_ETA_BAR",
    "THETA_CABIBBO_RAD", "THETA_CABIBBO_DEG", "LEPTON_PHI_RAD",
    "CKMFootReport", "cabibbo_lepton_gap_report",
]
