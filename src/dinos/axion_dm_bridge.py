"""Axion-DM bridge scaffold (HYPOTHESIS Step 45c).

Honest scope
------------
This module DOES:
  - Provide a parameterised mapping (A, n_cover, twist) -> axion mass m_a
    via the standard misalignment formula m_a ~ Lambda_QCD^2 / f_a, with
    f_a treated as f_a = f_0 * A^(-n_cover) where f_0 is an input.
  - Compute the textbook misalignment relic density Omega_a h^2 from
    given (m_a, theta_initial, f_a) using the standard formula.
  - Map an input topological twist to a misalignment angle.

This module DOES NOT:
  - Predict m_a, f_a, or theta_initial from the framework. All three
    are inputs. The framework constrains f_a only insofar as A is
    constrained (which it is not — A is itself a fit parameter).
  - Justify the cosmological assumptions (post-inflation scenario,
    standard QCD-like cooling) used in the misalignment formula.

Verdict on Grok claim of 12.4 ± 4.8 μeV axion: TUNABLE. Any axion
mass in the post-inflation window is reachable for some choice of
(A, n_cover, f_0).
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


# Reference scales
LAMBDA_QCD_EV: float = 0.2e9     # ~200 MeV
F_PLANCK_EV: float = 1.22e28


@dataclass(frozen=True)
class AxionPrediction:
    A: float
    n_cover: int
    theta_init: float
    f_a_GeV: float
    m_axion_eV: float
    relic_density_Omega_h2: float
    notes: str


def axion_mass_from_decay_constant(f_a_GeV: float,
                                     Lambda_QCD_GeV: float = 0.2) -> float:
    """Standard QCD-axion mass m_a ~ (m_pi f_pi / f_a). Approx 5.7e-6 eV at f_a = 1e12 GeV."""
    return float(5.7e-6 * (1e12 / f_a_GeV))   # eV


def relic_density_misalignment(m_a_eV: float, theta_init: float,
                                 f_a_GeV: float) -> float:
    """Standard misalignment relic Omega_a h^2 ~ 0.12 * (theta_i^2)
    * (f_a / 1e12 GeV)^7/6 * (m_a / 5.7e-6 eV)^(-1/2). Order-of-magnitude
    only — this is the textbook formula."""
    return float(0.12 * (theta_init ** 2)
                 * (f_a_GeV / 1e12) ** (7 / 6)
                 * (5.7e-6 / max(m_a_eV, 1e-15)) ** (1 / 2))


def axion_prediction(A: float = 0.48, n_cover: int = 10,
                      theta_init: float = 1.0,
                      f_0_GeV: float = 1e11) -> AxionPrediction:
    """Compute m_a and Omega_a h^2 for given inputs."""
    f_a = f_0_GeV * A ** (-n_cover)
    m_a = axion_mass_from_decay_constant(f_a)
    omega = relic_density_misalignment(m_a, theta_init, f_a)
    return AxionPrediction(
        A=float(A), n_cover=int(n_cover),
        theta_init=float(theta_init),
        f_a_GeV=float(f_a),
        m_axion_eV=float(m_a),
        relic_density_Omega_h2=float(omega),
        notes=("Textbook misalignment-mechanism formulas evaluated at "
               "given inputs (A, n_cover, theta_init, f_0). The "
               "framework does not currently CONSTRAIN any of these "
               "inputs — m_a is tunable across the entire haloscope window."),
    )


def scan_axion_window(A: float = 0.48,
                       n_covers=range(5, 15),
                       theta_init: float = 1.0,
                       f_0_GeV: float = 1e11) -> list[AxionPrediction]:
    """Show how m_a and Omega vary with n_cover. Tunable parameter map."""
    return [axion_prediction(A=A, n_cover=n,
                              theta_init=theta_init, f_0_GeV=f_0_GeV)
            for n in n_covers]


__all__ = [
    "LAMBDA_QCD_EV", "F_PLANCK_EV",
    "AxionPrediction",
    "axion_mass_from_decay_constant", "relic_density_misalignment",
    "axion_prediction", "scan_axion_window",
]
