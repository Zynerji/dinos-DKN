"""Hierarchy problem documentation (HYPOTHESIS Step 12c).

The DKN framework has a Higgs-wall scale v_bag ~ 0.43 MeV. The
Standard Model Higgs has VEV v_SM = 246 GeV. These are 5 orders of
magnitude apart.

This module documents the scale mismatch and HONESTLY states that
the framework cannot address the SM hierarchy problem (why the SM
Higgs is at 125 GeV rather than the Planck scale 10^19 GeV).

Honest scope statement
----------------------
- The bag wall in DKN is NOT the SM Higgs. It's a different field
  (Phi_bag) at a different scale.
- The framework lives in a low-energy effective sector.
- The SM hierarchy problem requires either SUSY, extra dimensions,
  compositeness, or some other UV mechanism. NONE of these are
  provided by the bag construction.
- VERDICT: hierarchy problem is NOT addressed. The bag wall coexists
  with the SM Higgs at separate scales, and the framework gives no
  rule for either.

What this module CAN do: quantify the scale mismatch, compute the
ratio v_SM / v_bag ~ 10^9 (about 1.4 GeV/MeV/eV-like), and make
explicit that any "DKN explanation of hierarchy" would require new
structure beyond the present framework.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import log10

from . import constants as C


# Standard Model Higgs VEV
V_SM_GeV: float = 246.0
V_SM_MeV: float = V_SM_GeV * 1.0e3
M_HIGGS_GeV: float = 125.10   # Higgs boson mass

# DKN bag wall VEV (paper §14.2)
V_BAG_MeV: float = C.v_bag_MeV   # ~ 0.43 MeV

# Planck mass
M_PL_GeV: float = 1.220890e19


@dataclass(frozen=True)
class HierarchyScaleReport:
    v_bag_MeV: float
    v_SM_MeV: float
    m_Higgs_GeV: float
    m_Pl_GeV: float
    v_SM_over_v_bag: float
    log10_v_SM_v_bag: float
    log10_m_Pl_m_Higgs: float
    framework_addresses_hierarchy: bool
    notes: str


def hierarchy_report() -> HierarchyScaleReport:
    """Document the scale mismatch."""
    ratio = V_SM_MeV / V_BAG_MeV
    log_ratio = log10(ratio)
    pl_higgs_log = log10(M_PL_GeV / M_HIGGS_GeV)
    notes = (
        f"DKN bag wall VEV: v_bag ~ {V_BAG_MeV} MeV. "
        f"SM Higgs VEV: v_SM ~ {V_SM_GeV} GeV. "
        f"Ratio: v_SM/v_bag = {ratio:.3e} (10^{log_ratio:.1f}). "
        f"SM hierarchy problem is m_Pl/m_Higgs = "
        f"10^{pl_higgs_log:.1f}. "
        f"VERDICT: the bag wall is NOT the SM Higgs. The DKN framework "
        f"lives at a separate, lower scale. The hierarchy problem "
        f"(why m_Higgs << m_Pl) is unaddressed; framework gives no UV "
        f"completion of the Higgs sector."
    )
    return HierarchyScaleReport(
        v_bag_MeV=V_BAG_MeV,
        v_SM_MeV=V_SM_MeV,
        m_Higgs_GeV=M_HIGGS_GeV,
        m_Pl_GeV=M_PL_GeV,
        v_SM_over_v_bag=ratio,
        log10_v_SM_v_bag=log_ratio,
        log10_m_Pl_m_Higgs=pl_higgs_log,
        framework_addresses_hierarchy=False,   # explicit non-claim
        notes=notes,
    )


__all__ = [
    "V_SM_GeV", "V_SM_MeV", "M_HIGGS_GeV", "M_PL_GeV", "V_BAG_MeV",
    "HierarchyScaleReport", "hierarchy_report",
]
