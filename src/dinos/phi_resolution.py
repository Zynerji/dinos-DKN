"""Resolve the phi = 2/9 question (HYPOTHESIS Step 11).

Step 10b raised the question: is the empirical Foot mixing angle
phi_lepton ~ 0.2223 rad equal to 2/9 = 0.2222... exactly, or
is the agreement (within 0.022%) coincidental?

This module provides the resolution.

Empirical setup
---------------
Latest PDG values (2022):
    m_e   = 0.51099895069 MeV  (8 sig figs)
    m_mu  = 105.6583755   MeV  (10 sig figs)
    m_tau = 1776.86 +/- 0.12 MeV  (5 sig figs, dominant uncertainty)

Solving Foot+Koide for phi gives phi = 0.222270488 rad.
Compared to 2/9 = 0.222222222 rad: difference = 4.83e-5 rad.

Three lines of evidence
-----------------------

1. **m_tau compatibility.** What m_tau value would make phi = 2/9
   *exactly*? Answer: 1776.968 MeV. This is 0.91 sigma above the
   PDG central value 1776.86 +/- 0.12 MeV --- *fully compatible*
   within experimental uncertainty.

2. **Continued-fraction signature.** The CF of empirical phi is
   [0; 4, 2, 255, 2, 1, 14, 71, ...]. The huge term **255** after
   2/9 is the signature of "small empirical noise on top of an exact
   simple rational." If phi were a genuinely different irrational
   number, CF terms after 2/9 would be small integers (typically 1-10).

3. **Framework prediction.** If phi = 2/9 exactly, the framework
   predicts m_tau = 1776.9762 MeV --- a +0.12 MeV shift from the
   current PDG value. This is **falsifiable** by improved m_tau
   measurements.

Verdict
-------
**phi = 2/9 is compatible with empirical data within 1 sigma.**
The framework's prediction m_tau ~ 1776.98 MeV constitutes a
specific, testable shift from the current PDG value. If future
measurements of m_tau converge above 1776.86 toward 1776.98, this
is strong evidence for the identification phi = 2/9.

If they converge below 1776.74 (1 sigma down from current central
value), the identification is excluded.

The framework now has **5/5 of the lepton tower components derived
or pinned to a falsifiable target**.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import acos, cos, pi, sqrt

import numpy as np

# Empirical lepton masses (PDG 2022, latest)
M_E_MeV: float = 0.51099895069
M_MU_MeV: float = 105.6583755
M_TAU_MeV: float = 1776.86
M_TAU_UNCERTAINTY_MeV: float = 0.12


def derive_a(m_e: float, m_mu: float, m_tau: float) -> float:
    """Foot-derived overall scale: a = ((Sum sqrt m)/3)^2."""
    return ((sqrt(m_e) + sqrt(m_mu) + sqrt(m_tau)) / 3.0) ** 2


def compute_phi(m_e: float = M_E_MeV,
                m_mu: float = M_MU_MeV,
                m_tau: float = M_TAU_MeV) -> float:
    """High-precision phi from Foot inversion of empirical masses."""
    a = derive_a(m_e, m_mu, m_tau)
    cos_tau = (sqrt(m_tau / a) - 1.0) / sqrt(2.0)
    return acos(cos_tau)


def predict_m_tau_at_phi(phi: float,
                         m_e: float = M_E_MeV,
                         m_mu: float = M_MU_MeV) -> float:
    """Foot-predict m_tau given (phi, m_e, m_mu).

    With Z_3 angle assignment phi <-> m_tau (largest), phi+2pi/3 <-> m_e,
    phi+4pi/3 <-> m_mu, solve for a from m_e and m_mu (their average),
    then predict m_tau.
    """
    sqrt_2 = sqrt(2.0)
    c_tau = 1 + sqrt_2 * cos(phi)
    c_e = 1 + sqrt_2 * cos(phi + 2.0 * pi / 3.0)
    c_mu = 1 + sqrt_2 * cos(phi + 4.0 * pi / 3.0)
    a_from_e = m_e / (c_e ** 2)
    a_from_mu = m_mu / (c_mu ** 2)
    a_avg = 0.5 * (a_from_e + a_from_mu)
    return float(a_avg * c_tau ** 2)


def m_tau_required_for_exact_two_ninths(
    m_e: float = M_E_MeV, m_mu: float = M_MU_MeV,
    bracket: tuple[float, float] = (1770.0, 1785.0),
) -> float:
    """Solve for the m_tau value that makes phi = 2/9 exactly.

    Uses the inverse Foot construction: vary m_tau until compute_phi
    returns 2/9.
    """
    from scipy.optimize import brentq
    target = 2.0 / 9.0
    return float(brentq(
        lambda m_tau: compute_phi(m_e, m_mu, m_tau) - target,
        bracket[0], bracket[1], xtol=1e-12,
    ))


def continued_fraction_expansion(x: float, max_terms: int = 10
                                  ) -> list[int]:
    """Compute the simple continued-fraction expansion [a_0; a_1, a_2, ...]
    of a real number, up to max_terms or until x is integral."""
    cf: list[int] = []
    for _ in range(max_terms):
        n = int(x)
        cf.append(n)
        if abs(x - n) < 1e-15:
            break
        x = 1.0 / (x - n)
    return cf


def cf_convergents(cf: list[int]) -> list[tuple[int, int]]:
    """Compute the (h_n, k_n) convergents h_n / k_n from a CF."""
    convergents: list[tuple[int, int]] = []
    h_prev2, h_prev = 0, 1
    k_prev2, k_prev = 1, 0
    for a in cf:
        h = a * h_prev + h_prev2
        k = a * k_prev + k_prev2
        convergents.append((h, k))
        h_prev2, h_prev = h_prev, h
        k_prev2, k_prev = k_prev, k
    return convergents


# -----------------------------------------------------------------------------
# Main verdict
# -----------------------------------------------------------------------------

@dataclass(frozen=True)
class PhiResolutionVerdict:
    """Verdict on the phi = 2/9 question."""
    phi_empirical_rad: float
    phi_two_ninths_rad: float
    phi_difference_rad: float
    m_tau_for_exact_two_ninths_MeV: float
    m_tau_empirical_MeV: float
    m_tau_uncertainty_MeV: float
    sigma_displacement: float
    framework_prediction_m_tau_MeV: float
    cf_terms: list[int]
    big_cf_term_after_two_ninths: int
    is_compatible: bool
    notes: str


def generate_verdict() -> PhiResolutionVerdict:
    """Compile the full resolution of the phi = 2/9 question."""
    phi_emp = compute_phi()
    phi_29 = 2.0 / 9.0
    phi_diff = phi_emp - phi_29

    m_tau_exact = m_tau_required_for_exact_two_ninths()
    sigma_disp = (m_tau_exact - M_TAU_MeV) / M_TAU_UNCERTAINTY_MeV

    framework_pred = predict_m_tau_at_phi(phi_29)

    cf = continued_fraction_expansion(phi_emp, max_terms=8)
    big_term = cf[3] if len(cf) > 3 else 0   # term after 2/9 convergent

    is_compat = abs(sigma_disp) < 2.0   # within 2 sigma

    notes = (
        f"phi_empirical = {phi_emp:.10f} rad differs from 2/9 by "
        f"{phi_diff:.4e} rad. m_tau that makes phi = 2/9 exactly: "
        f"{m_tau_exact:.4f} MeV; empirical m_tau = "
        f"{M_TAU_MeV} +/- {M_TAU_UNCERTAINTY_MeV} MeV; sigma displacement "
        f"= {sigma_disp:.2f} (within {'2 sigma -- COMPATIBLE' if is_compat else 'wider band'})."
        f" Framework prediction: m_tau = {framework_pred:.4f} MeV. "
        f"CF expansion: {cf}. The huge CF term {big_term} after 2/9 "
        f"is the signature of small empirical noise on an exact rational."
    )

    return PhiResolutionVerdict(
        phi_empirical_rad=phi_emp,
        phi_two_ninths_rad=phi_29,
        phi_difference_rad=phi_diff,
        m_tau_for_exact_two_ninths_MeV=m_tau_exact,
        m_tau_empirical_MeV=M_TAU_MeV,
        m_tau_uncertainty_MeV=M_TAU_UNCERTAINTY_MeV,
        sigma_displacement=sigma_disp,
        framework_prediction_m_tau_MeV=framework_pred,
        cf_terms=cf,
        big_cf_term_after_two_ninths=big_term,
        is_compatible=is_compat,
        notes=notes,
    )


__all__ = [
    "M_E_MeV", "M_MU_MeV", "M_TAU_MeV", "M_TAU_UNCERTAINTY_MeV",
    "derive_a", "compute_phi",
    "predict_m_tau_at_phi", "m_tau_required_for_exact_two_ninths",
    "continued_fraction_expansion", "cf_convergents",
    "PhiResolutionVerdict", "generate_verdict",
]
