"""SU(2) x U(1) electroweak collective modes on the polar strip
(HYPOTHESIS Step 41).

Honest scope
------------
This module DOES:
  - Take SU(2)_L coupling g2, U(1)_Y coupling g', and Higgs VEV v as
    INPUTS (not derived from the Möbius geometry).
  - Compute the tree-level SM electroweak observables (mW, mZ,
    sin^2(theta_W), photon mass = 0).
  - Provide the framework where future work could try to derive
    g2 and g' from polar spin-connection eigenvalues.

This module DOES NOT:
  - Derive g2, g', or v from the polar Möbius geometry. This is the
    open question. Grok claimed sin^2(theta_W) = 0.23174 to 0.23%
    accuracy from "polar Möbius dynamics" but in fact hardcoded the
    observed couplings. We make that fact explicit by labelling the
    couplings as inputs.
  - Predict W, Z masses without taking v as an input.

Verdict on the Grok claim that ElectroweakPolarStrip "derives" the
weak mixing angle: TAUTOLOGICAL — it computes tree-level SM relations
of input couplings. See dinos.grok_claims_validation.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

# Default values: PDG observed (NOT derived).
DEFAULT_G2: float = 0.6520
DEFAULT_GP: float = 0.3570
DEFAULT_V_GEV: float = 246.22


@dataclass(frozen=True)
class ElectroweakObservables:
    g2: float
    gp: float
    v_GeV: float
    mW_GeV: float
    mZ_GeV: float
    mW_over_mZ: float
    sin2_thetaW: float
    thetaW_deg: float
    e_charge: float        # e = g2 sin(thetaW)
    notes: str


def electroweak_observables(g2: float = DEFAULT_G2,
                             gp: float = DEFAULT_GP,
                             v_GeV: float = DEFAULT_V_GEV) -> ElectroweakObservables:
    """Tree-level SM electroweak relations from input couplings.

    NOTE: g2, gp, v are INPUTS. The framework does not currently
    derive them from the Möbius polar strip — that is open work.
    """
    mW = 0.5 * g2 * v_GeV
    mZ = 0.5 * np.sqrt(g2 * g2 + gp * gp) * v_GeV
    thetaW = float(np.arctan(gp / g2))
    sin2 = float(np.sin(thetaW) ** 2)
    e_charge = float(g2 * np.sin(thetaW))
    return ElectroweakObservables(
        g2=g2, gp=gp, v_GeV=v_GeV,
        mW_GeV=float(mW), mZ_GeV=float(mZ),
        mW_over_mZ=float(mW / mZ),
        sin2_thetaW=sin2,
        thetaW_deg=float(np.degrees(thetaW)),
        e_charge=e_charge,
        notes=("Tree-level SM electroweak relations evaluated at given "
               "(g2, g', v). Does NOT derive these inputs from the "
               "Möbius geometry — this is open work."),
    )


@dataclass(frozen=True)
class CouplingDerivationStatus:
    label: str
    derived_from_geometry: bool
    placeholder_value: float
    notes: str


def coupling_derivation_status() -> list[CouplingDerivationStatus]:
    """Honest statement of which SM electroweak parameters are derived
    from the framework versus inserted by hand."""
    return [
        CouplingDerivationStatus(
            label="g2 (SU(2)_L coupling)",
            derived_from_geometry=False,
            placeholder_value=DEFAULT_G2,
            notes=("Conjectured to come from polar spin-connection "
                   "eigenvalue but no derivation in current framework."),
        ),
        CouplingDerivationStatus(
            label="g' (U(1)_Y coupling)",
            derived_from_geometry=False,
            placeholder_value=DEFAULT_GP,
            notes=("Conjectured to come from temporal U(1) phase "
                   "strength; no derivation in current framework."),
        ),
        CouplingDerivationStatus(
            label="v (Higgs VEV)",
            derived_from_geometry=False,
            placeholder_value=DEFAULT_V_GEV,
            notes=("Conjectured to come from antipodal Higgs wall "
                   "fixed-point; current `dinos.dm.HiddenScalarChannel` "
                   "predicts m* ~ 156 keV, not v ~ 246 GeV."),
        ),
    ]


__all__ = [
    "DEFAULT_G2", "DEFAULT_GP", "DEFAULT_V_GEV",
    "ElectroweakObservables", "electroweak_observables",
    "CouplingDerivationStatus", "coupling_derivation_status",
]
