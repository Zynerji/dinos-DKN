"""Generation-mass tower test (HYPOTHESIS.md Step 3).

Asks: can the lepton mass ratios m_μ/m_e ≈ 206.77 and m_τ/m_e ≈ 3477.15
be produced as topological labels (n_φ, n_θ) of the *same* Möbius loop
with fixed σ, α?

The mass closure (paper eq. 61–63):

    m = ( π σ / (1 − 2C − α) )^(1/3)

implies that, at fixed σ and α, the mass ratio between any two states is
entirely controlled by the Casimir parameter C:

    m_l / m_e  =  ( (1 − 2C_e − α) / (1 − 2C_l − α) )^(1/3)

Inverting: the C required to produce each lepton at fixed σ is

    C_l  =  ( 1 − α − (1 − 2C_e − α) / (m_l/m_e)^3 ) / 2

For the empirical ratios this gives ``C_μ ≈ C_τ ≈ 0.4963`` — both
saturate against the upper bound ``(1 − α)/2 ≈ 0.4963`` from positivity
of the Higgs-wall residue ``1 − 2C − α``. The two values are
indistinguishable to ~10⁻⁶ despite μ and τ being 17× apart in mass.

So the lepton tower **cannot** be a fixed-σ topological excitation of
the same loop. Per-generation σ_l is required, and the framework gives
no independent rule for it: σ_l ∝ m_l^3 just restates the mass.

This module provides the utilities used by ``tests/test_generations.py``
to document this cleanly. The point is to falsify the topological-tower
reading and pin where the framework ends.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from . import constants as C, closure


# -----------------------------------------------------------------------------
# Empirical lepton masses (PDG 2022)
# -----------------------------------------------------------------------------

M_E_MeV: float = C.m_e_MeV               # 0.51099895
M_MU_MeV: float = 105.6583755            # PDG 2022
M_TAU_MeV: float = 1776.86               # PDG 2022

LEPTON_MASSES_MeV: dict[str, float] = {
    "e":   M_E_MeV,
    "mu":  M_MU_MeV,
    "tau": M_TAU_MeV,
}


def lepton_mass_ratios() -> dict[str, float]:
    """{mu_over_e: 206.77, tau_over_e: 3477.15, tau_over_mu: 16.82}."""
    return {
        "mu_over_e":   M_MU_MeV / M_E_MeV,
        "tau_over_e":  M_TAU_MeV / M_E_MeV,
        "tau_over_mu": M_TAU_MeV / M_MU_MeV,
    }


# -----------------------------------------------------------------------------
# Closure-derived utilities
# -----------------------------------------------------------------------------

def C_max(alpha: float = C.alpha_EM) -> float:
    """Upper bound (1 − α)/2 from positivity of the Higgs-wall residue.

    The closure is well-posed only for ``2C + α < 1``.  Lepton masses
    requiring ``C → C_max`` push the residue ``1 − 2C − α → 0``, which is
    exactly the regime where the framework's perturbative structure
    breaks down.
    """
    return 0.5 * (1.0 - alpha)


def C_required_for_ratio(mass_ratio: float,
                         C_e: float = C.C_bag_Dirac,
                         alpha: float = C.alpha_EM) -> float:
    """Solve the closure for C_l given a target ratio m_l/m_e at fixed σ.

        C_l = ( 1 − α − (1 − 2C_e − α)/r³ ) / 2,    r = m_l/m_e.

    Returns ``C_l`` in dimensionless units.  Asymptotes to ``C_max`` as
    ``r → ∞``.
    """
    base_residue = 1.0 - 2.0 * C_e - alpha
    new_residue = base_residue / (mass_ratio ** 3)
    return 0.5 * (1.0 - alpha - new_residue)


def mass_for_C(C_val: float,
               sigma_MeV3: float | None = None,
               alpha: float = C.alpha_EM) -> float:
    """m = ( π σ / (1 − 2C − α) )^(1/3)  in MeV.

    If σ is None, uses the value that closes m_e at C = C_bag_Dirac.
    """
    if sigma_MeV3 is None:
        sigma_MeV3 = closure.required_surface_tension(
            m_e_MeV=C.m_e_MeV, C_bag=C.C_bag_Dirac, alpha=alpha,
        )
    residue = 1.0 - 2.0 * C_val - alpha
    if residue <= 0.0:
        raise ValueError(
            f"2C + α ≥ 1 (= {2.0 * C_val + alpha}); closure has no positive mass"
        )
    return (np.pi * sigma_MeV3 / residue) ** (1.0 / 3.0)


def required_C_per_generation(C_e: float = C.C_bag_Dirac,
                              alpha: float = C.alpha_EM) -> dict[str, float]:
    """C value each lepton would need at fixed σ."""
    ratios = lepton_mass_ratios()
    return {
        "e":   C_e,
        "mu":  C_required_for_ratio(ratios["mu_over_e"], C_e, alpha),
        "tau": C_required_for_ratio(ratios["tau_over_e"], C_e, alpha),
    }


def k_dirac_per_generation() -> dict[str, int]:
    """The natural |k| assignment if we treat generations as ground-state
    n_φ = 0, 1, 2 (n_θ = 0) excitations of the Möbius loop:

        |k| = n_φ + n_θ + 1   ⇒   |k|_e = 1, |k|_μ = 2, |k|_τ = 3.
    """
    return {"e": 1, "mu": 2, "tau": 3}


# -----------------------------------------------------------------------------
# Power-law fit to test "C ∝ |k|^p" hypothesis
# -----------------------------------------------------------------------------

@dataclass(frozen=True)
class PowerLawFit:
    c0: float
    p: float
    relative_residual: float
    predicted: dict[str, float]
    actual: dict[str, float]


def fit_C_power_law(C_per_gen: dict[str, float],
                    k_per_gen: dict[str, int]) -> PowerLawFit:
    """Fit ``C_l = c₀ · |k|^p`` to the (e, μ, τ) data.

    Returns the best-fit exponent and prefactor along with the residual.
    A clean topological law would have residual ≪ 1 and a small-integer
    exponent.
    """
    keys = ["e", "mu", "tau"]
    ks = np.array([k_per_gen[k] for k in keys], dtype=float)
    Cs = np.array([C_per_gen[k] for k in keys], dtype=float)
    log_k = np.log(ks)
    log_C = np.log(Cs)
    p, log_c0 = np.polyfit(log_k, log_C, 1)
    c0 = float(np.exp(log_c0))
    predicted_arr = c0 * ks ** p
    residual = float(np.linalg.norm(Cs - predicted_arr) / np.linalg.norm(Cs))
    return PowerLawFit(
        c0=c0, p=float(p), relative_residual=residual,
        predicted={k: float(predicted_arr[i]) for i, k in enumerate(keys)},
        actual={k: float(Cs[i]) for i, k in enumerate(keys)},
    )


# -----------------------------------------------------------------------------
# Two-point extrapolation: calibrate on (e, μ), predict τ
# -----------------------------------------------------------------------------

def residue(C_val: float, alpha: float = C.alpha_EM) -> float:
    """Higgs-wall residue r ≡ 1 − 2C − α.  The closure ``m³ ∝ 1/r``
    means r is the natural variable for log-space comparisons —
    differences invisible in C (which saturates at C_max = 0.4963)
    span ~11 orders of magnitude in r across the lepton tower."""
    return 1.0 - 2.0 * C_val - alpha


def log_residue_per_generation(C_e: float = C.C_bag_Dirac,
                               alpha: float = C.alpha_EM) -> dict[str, float]:
    """log(r_l) for l ∈ {e, μ, τ}.  Spans ~25 in natural log even though
    log|k| spans only ~1 — the cleanest visualisation of the
    falsification."""
    Cs = required_C_per_generation(C_e=C_e, alpha=alpha)
    return {l: float(np.log(residue(Cs[l], alpha))) for l in ("e", "mu", "tau")}


def log_residue_vs_log_mass_slope(C_e: float = C.C_bag_Dirac,
                                  alpha: float = C.alpha_EM) -> float:
    """Linear fit of log(r_l/r_e) against log(m_l/m_e).

    Closure identity ``r_l/r_e = (m_l/m_e)^{-3}`` predicts slope = -3
    exactly.  This is *not* a fit; it's an algebraic identity surfaced
    by the log transform.  Returned for use in a falsification test.
    """
    log_r = log_residue_per_generation(C_e, alpha)
    log_m = {l: float(np.log(LEPTON_MASSES_MeV[l])) for l in ("e", "mu", "tau")}
    log_r_rel = np.array([log_r[l] - log_r["e"] for l in ("e", "mu", "tau")])
    log_m_rel = np.array([log_m[l] - log_m["e"] for l in ("e", "mu", "tau")])
    # Skip the trivial (0, 0) point.
    slope, intercept = np.polyfit(log_m_rel[1:], log_r_rel[1:], 1)
    return float(slope)


def predict_tau_from_e_and_mu(C_e: float = C.C_bag_Dirac,
                              alpha: float = C.alpha_EM) -> dict:
    """If a power law C ∝ |k|^p is calibrated on (e, μ) alone, what
    mass does it predict for τ?

    The empirical answer is m_τ = 1776.86 MeV.  Falsification check.
    """
    Cs = required_C_per_generation(C_e=C_e, alpha=alpha)
    ks = k_dirac_per_generation()
    p = float(np.log(Cs["mu"] / Cs["e"]) / np.log(ks["mu"] / ks["e"]))
    C_tau_pred = Cs["e"] * (ks["tau"] / ks["e"]) ** p
    if 2.0 * C_tau_pred + alpha >= 1.0:
        m_tau_pred = float("inf")
    else:
        m_tau_pred = mass_for_C(C_tau_pred, alpha=alpha)
    return {
        "p_calibrated": p,
        "C_tau_predicted": C_tau_pred,
        "m_tau_predicted_MeV": m_tau_pred,
        "m_tau_empirical_MeV": M_TAU_MeV,
        "rel_error": abs(m_tau_pred - M_TAU_MeV) / M_TAU_MeV
                     if np.isfinite(m_tau_pred) else float("inf"),
    }


__all__ = [
    "M_E_MeV", "M_MU_MeV", "M_TAU_MeV", "LEPTON_MASSES_MeV",
    "lepton_mass_ratios", "C_max",
    "C_required_for_ratio", "mass_for_C",
    "required_C_per_generation", "k_dirac_per_generation",
    "PowerLawFit", "fit_C_power_law",
    "predict_tau_from_e_and_mu",
    "residue", "log_residue_per_generation", "log_residue_vs_log_mass_slope",
]
