"""Mass predictions from metallic Foot resonances (HYPOTHESIS Step 17).

For each confirmed Foot resonance with metallic b, given any TWO of
the three masses, predict the THIRD. Tests how tightly the framework
constrains masses.

Confirmed resonances and predictions
------------------------------------

Lepton: b = sqrt(2). Given (m_e, m_mu) -> predict m_tau.
  Predicted m_tau = 1776.98 MeV (vs PDG 1776.86 +/- 0.12 MeV).
  Gap: 0.12 MeV = ~1 sigma.

Vector mesons: b = 1/bronze^2. Given (m_rho, m_omega) -> predict m_phi.
  Compute below.

Light baryons: b = 1/(silver*copper). Given (m_N, m_Lambda) -> predict m_Xi.
  Compute below.

This module provides falsifiable predictions for each metallic resonance.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import cos, pi, sqrt

import numpy as np
from scipy.optimize import fsolve

from . import metallic_invariant_sweep as mis


def predict_third_mass(m1: float, m2: float, b: float,
                       require_hierarchy: bool = True,
                       require_positivity: bool = True,
                       initial_phi: float = 0.5,
                       initial_a_factor: float = 1.0) -> dict:
    """Given two masses and metallic b, find a Foot solution and predict
    the third mass.

    Branch selection: by default require positivity (all 1+b*cos > 0)
    and hierarchy (predicted m3 > max(m1, m2), so m3 is the heaviest).

    Returns dict with predicted m3 + (a, phi) + branch info, or None.
    """
    masses_in = sorted([m1, m2])

    def foot(a, b, phi):
        return np.array([a * (1 + b * cos(l * 2 * pi / 3 + phi)) ** 2
                         for l in range(3)])

    def factors(a, b, phi):
        return [1 + b * cos(l * 2 * pi / 3 + phi) for l in range(3)]

    # Try all 3 assignments of (m1, m2) to Foot positions.
    valid_solutions = []

    for assign in [(0, 1), (0, 2), (1, 2)]:
        l_left, l_right = assign

        def eqs(params):
            a, phi = params
            m_pred = foot(a, b, phi)
            return [
                m_pred[l_left] - masses_in[0],
                m_pred[l_right] - masses_in[1],
            ]

        for phi_init in np.linspace(0.001, 2 * pi - 0.001, 40):
            for a_factor in [0.1, 0.5, 1.0, 2.0, 10.0]:
                a_init = (m1 + m2) / 2 * a_factor / (1 + b ** 2 / 2)
                try:
                    sol, info, ier, _ = fsolve(
                        eqs, [a_init, phi_init], full_output=True,
                    )
                    if ier == 1:
                        a_v, phi_v = sol
                        if a_v > 0:
                            m_pred = foot(a_v, b, phi_v)
                            loss = abs(eqs(sol)[0]) + abs(eqs(sol)[1])
                            if loss < 1e-3:
                                third_l = 3 - l_left - l_right
                                m3 = float(m_pred[third_l])
                                facs = factors(a_v, b, phi_v)
                                # Apply branch filters
                                if require_positivity and any(f < 0 for f in facs):
                                    continue
                                if require_hierarchy and m3 < max(masses_in):
                                    continue
                                valid_solutions.append({
                                    "a": float(a_v),
                                    "phi": float(phi_v % (2 * pi)),
                                    "m_predicted": m3,
                                    "assignment": assign,
                                    "loss": loss,
                                    "factors": facs,
                                })
                except Exception:
                    pass

    if not valid_solutions:
        return None

    # Among valid solutions, return the one with smallest loss
    return min(valid_solutions, key=lambda s: s["loss"])


@dataclass(frozen=True)
class MassPrediction:
    family: str
    inputs: tuple[str, str]
    input_masses_MeV: tuple[float, float]
    target: str
    target_empirical_MeV: float
    target_predicted_MeV: float
    rel_error_pct: float
    b_metallic: str
    b_value: float


def lepton_mass_prediction() -> MassPrediction:
    """Predict m_tau from (m_e, m_mu) at b = sqrt(2)."""
    sol = predict_third_mass(0.51099895, 105.6583755, sqrt(2.0))
    if sol is None:
        raise RuntimeError("No Foot solution for leptons")
    target = 1776.86
    return MassPrediction(
        family="charged_leptons",
        inputs=("m_e", "m_mu"),
        input_masses_MeV=(0.51099895, 105.6583755),
        target="m_tau",
        target_empirical_MeV=target,
        target_predicted_MeV=sol["m_predicted"],
        rel_error_pct=abs(sol["m_predicted"] - target) / target * 100,
        b_metallic="silver - 1 = sqrt(2)",
        b_value=sqrt(2.0),
    )


def vector_meson_mass_prediction() -> MassPrediction:
    """Predict m_phi from (m_rho, m_omega) at b = 1/bronze^2."""
    sol = predict_third_mass(775.26, 782.65, 1.0 / (mis.BRONZE ** 2))
    if sol is None:
        raise RuntimeError("No Foot solution for vector mesons")
    target = 1019.46
    return MassPrediction(
        family="vector_mesons",
        inputs=("m_rho", "m_omega"),
        input_masses_MeV=(775.26, 782.65),
        target="m_phi",
        target_empirical_MeV=target,
        target_predicted_MeV=sol["m_predicted"],
        rel_error_pct=abs(sol["m_predicted"] - target) / target * 100,
        b_metallic="1/bronze^2",
        b_value=1.0 / (mis.BRONZE ** 2),
    )


def light_baryon_mass_prediction() -> MassPrediction:
    """Predict m_Xi from (m_N, m_Lambda) at b = 1/(silver*copper)."""
    sol = predict_third_mass(938.92, 1115.68, 1.0 / (mis.SILVER * mis.COPPER))
    if sol is None:
        raise RuntimeError("No Foot solution for baryons")
    target = 1318.3
    return MassPrediction(
        family="light_baryons",
        inputs=("m_N", "m_Lambda"),
        input_masses_MeV=(938.92, 1115.68),
        target="m_Xi",
        target_empirical_MeV=target,
        target_predicted_MeV=sol["m_predicted"],
        rel_error_pct=abs(sol["m_predicted"] - target) / target * 100,
        b_metallic="1/(silver*copper)",
        b_value=1.0 / (mis.SILVER * mis.COPPER),
    )


def all_predictions() -> list[MassPrediction]:
    """All three mass predictions from metallic Foot resonances."""
    return [
        lepton_mass_prediction(),
        vector_meson_mass_prediction(),
        light_baryon_mass_prediction(),
    ]


__all__ = [
    "predict_third_mass",
    "MassPrediction",
    "lepton_mass_prediction", "vector_meson_mass_prediction",
    "light_baryon_mass_prediction",
    "all_predictions",
]
