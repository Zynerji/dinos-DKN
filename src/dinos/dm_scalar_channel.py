"""Hidden scalar second-saddle channel for dark matter (HYPOTHESIS Step 47b).

Honest scope
------------
This module DOES:
  - Wraps the existing `dinos.dm` module's hidden-scalar prediction
    (m* ~ 156 keV) and exposes it as a "DM scalar channel".
  - Provides hooks for combining the scalar mass with a relic density
    estimate (delegated to `dinos.axion_dm_bridge` if treating it as
    axion-like).

This module DOES NOT:
  - Predict m* from a "second saddle" of the Keldysh action — the
    156 keV figure comes from the joint closure equation in dm.py,
    which is itself parameterised. Whether this is genuinely a "DM
    candidate" requires (i) stability across cosmic time, (ii) coupling
    to SM that is consistent with non-detection, (iii) relic density
    matching observation. None of these are addressed in dm.py.
"""

from __future__ import annotations

from dataclasses import dataclass

from . import dm as dm_existing


@dataclass(frozen=True)
class DMScalarChannelReport:
    m_scalar_keV: float
    notes: str


def hidden_scalar_channel() -> DMScalarChannelReport:
    """Return the existing dm.py hidden-scalar mass.
    See dinos.dm for the joint closure equation."""
    sc = dm_existing.joint_closure()
    return DMScalarChannelReport(
        m_scalar_keV=float(sc.m_star_MeV * 1000.0),
        notes=("Hidden scalar mass from dinos.dm.joint_closure (~155 keV). "
               "This is a particle-physics scale derived from the "
               "framework's joint mass closure; whether it constitutes "
               "a viable DM candidate (relic density, stability, "
               "non-detection consistency) is NOT verified in this module. "
               "EDGES match and direct-detection status see dinos.dm.predictions()."),
    )


__all__ = ["DMScalarChannelReport", "hidden_scalar_channel"]
