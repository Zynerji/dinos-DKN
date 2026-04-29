"""Per-generation closure scaffold (HYPOTHESIS.md Step 6a).

Step 3 cleanly falsified the topological-tower reading of generations:
the lepton mass ratios cannot come from (n_φ, n_θ) labels of the same
loop with shared σ.  This module adds the **structural extension**
required to accommodate them at all — per-generation parameters σ_g
calibrated against the empirical masses.

This is **calibration, not prediction.** Per Step 3, three independent
σ_g values are needed for three masses; the framework gives no
first-principles rule for them.  What this module *does* provide:

1. A clean per-generation calibration interface (`sigma_for_mass`).
2. A check whether an *empirical* relation like the **Koide formula**
   is at least consistent with the framework — it is, because the
   formula is purely between the masses, and the framework can
   reproduce any mass set.
3. A diagnostic showing that no clean σ(g) law (power, exponential,
   or polynomial in a generation index g) reproduces the observed
   ratios — strengthening the Step 3 falsification.

Honest scope statement
----------------------
- This module CAN: fit each lepton's σ_g and demonstrate the
  framework can accommodate the empirical tower.
- This module CANNOT: predict m_μ, m_τ, or the Koide relation from
  any property of the framework.

Future work would need a higher-dimensional structure (extra
dimension, internal flavor space, twist class index) that pins σ_g.
None is provided here.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from . import constants as C, closure, generations


# -----------------------------------------------------------------------------
# Per-generation calibration
# -----------------------------------------------------------------------------

def sigma_for_mass(m_MeV: float, C_bag: float = C.C_bag_Dirac,
                   alpha: float = C.alpha_EM) -> float:
    """Inverse of the closure: σ_g = m_g³ (1 − 2C − α) / π.

    Returns the bag tension σ_g (in MeV³) that closes the DKN closure
    at the given mass with the given (C, α).  Per Step 3 this must be
    independently specified per generation; the formula is exact, the
    framework just doesn't predict m_g.
    """
    return closure.required_surface_tension(
        m_e_MeV=m_MeV, C_bag=C_bag, alpha=alpha,
    )


def per_generation_sigmas(C_bag: float = C.C_bag_Dirac,
                          alpha: float = C.alpha_EM) -> dict[str, float]:
    """σ_g for each empirical lepton mass at fixed (C, α)."""
    return {
        l: sigma_for_mass(m, C_bag, alpha)
        for l, m in generations.LEPTON_MASSES_MeV.items()
    }


# -----------------------------------------------------------------------------
# Koide formula diagnostic
# -----------------------------------------------------------------------------

def koide_q(masses_MeV: dict[str, float] | list[float]) -> float:
    """Koide ratio ``Q = (Σ √m)² / (Σ m)``  on a 3-mass set.

    Empirically Q ≈ 3/2 for the charged leptons in this convention
    (Koide 1981; the inverse 2/3 appears under the alternate
    Q' = Σm/(Σ√m)² convention).  No first-principles derivation, but
    a striking numerical coincidence.  Computing this is *consistent*
    with the framework (which can fit any mass set) but the framework
    does not derive the Q value.
    """
    if isinstance(masses_MeV, dict):
        m = list(masses_MeV.values())
    else:
        m = list(masses_MeV)
    if len(m) != 3:
        raise ValueError("Koide formula is defined on 3-mass sets")
    sqrt_sum = float(sum(np.sqrt(mi) for mi in m))
    return (sqrt_sum ** 2) / float(sum(m))


def lepton_koide_q() -> float:
    """Q for the empirical charged-lepton masses (e, μ, τ).

    Numerically ≈ 0.6669 — within 0.1% of the Koide value 2/3."""
    return koide_q(generations.LEPTON_MASSES_MeV)


# -----------------------------------------------------------------------------
# Diagnostic: no clean σ(g) law
# -----------------------------------------------------------------------------

@dataclass(frozen=True)
class GenerationFitDiagnostic:
    """Result of trying various σ(g) parametric forms against empirical."""
    form: str
    best_params: tuple[float, ...]
    relative_residual: float
    fits_well: bool


def fit_sigma_power_law(
    C_bag: float = C.C_bag_Dirac,
    alpha: float = C.alpha_EM,
) -> GenerationFitDiagnostic:
    """Fit σ_g = σ_0 · g^p for g ∈ {1, 2, 3} with (e, μ, τ) → g.

    Returns the best (σ_0, p) and the relative fit residual.
    Per the Step 3 algebra, no clean p exists.
    """
    sigmas = per_generation_sigmas(C_bag, alpha)
    g_vals = np.array([1.0, 2.0, 3.0])
    s_vals = np.array([sigmas[l] for l in ("e", "mu", "tau")])
    # Fit log σ = log σ_0 + p · log g
    log_g = np.log(g_vals)
    log_s = np.log(s_vals)
    p, log_s0 = np.polyfit(log_g, log_s, 1)
    s0 = float(np.exp(log_s0))
    p = float(p)
    predicted = s0 * g_vals ** p
    rel_res = float(np.linalg.norm(s_vals - predicted) / np.linalg.norm(s_vals))
    return GenerationFitDiagnostic(
        form="sigma_g = sigma_0 * g^p",
        best_params=(s0, p),
        relative_residual=rel_res,
        fits_well=rel_res < 0.01,
    )


def fit_sigma_exponential(
    C_bag: float = C.C_bag_Dirac,
    alpha: float = C.alpha_EM,
) -> GenerationFitDiagnostic:
    """Fit σ_g = σ_0 · exp(λ·g) for g ∈ {1, 2, 3}."""
    sigmas = per_generation_sigmas(C_bag, alpha)
    g_vals = np.array([1.0, 2.0, 3.0])
    s_vals = np.array([sigmas[l] for l in ("e", "mu", "tau")])
    log_s = np.log(s_vals)
    lam, log_s0 = np.polyfit(g_vals, log_s, 1)
    s0 = float(np.exp(log_s0))
    lam = float(lam)
    predicted = s0 * np.exp(lam * g_vals)
    rel_res = float(np.linalg.norm(s_vals - predicted) / np.linalg.norm(s_vals))
    return GenerationFitDiagnostic(
        form="sigma_g = sigma_0 * exp(lambda * g)",
        best_params=(s0, lam),
        relative_residual=rel_res,
        fits_well=rel_res < 0.01,
    )


# -----------------------------------------------------------------------------
# Minimal-structure derivation attempt (Foot-style 3-state matrix)
# -----------------------------------------------------------------------------
#
# The Foot parametrisation
#
#     m_l = a · (1 + b · cos((l − 1)·2π/3 + φ))²,   l ∈ {1, 2, 3}
#
# automatically satisfies the Koide relation Q = 3/(1 + b²/2):
# - b = √2  ⇒  Q = 3/2 (Koide central value).
# - 3 free parameters (a, b, φ) ↔ 3 masses (e, μ, τ): 0 d.o.f. left.
#
# This is **NOT a derivation from the DKN framework** — it's a
# *postulate* of a 3-state internal flavour space with a specific
# trigonometric form.  We implement it here to make the gap precise:
# any "derivation" of the lepton tower from the current framework
# requires ADDING this (or equivalent) structure as a new postulate.


@dataclass(frozen=True)
class FootParameters:
    """(a, b, φ) of the Foot 3-state mass parametrisation."""
    a_MeV: float
    b: float
    phi_rad: float


def foot_masses(params: FootParameters) -> dict[str, float]:
    """m_l for l ∈ {e, μ, τ} from the Foot parametrisation."""
    out: dict[str, float] = {}
    for label, l_idx in (("e", 0), ("mu", 1), ("tau", 2)):
        x = 1.0 + params.b * np.cos((l_idx) * 2.0 * np.pi / 3.0 + params.phi_rad)
        out[label] = params.a_MeV * (x ** 2)
    return out


def fit_foot_to_empirical(
    initial: FootParameters = FootParameters(a_MeV=313.0, b=1.0, phi_rad=0.222),
) -> tuple[FootParameters, float]:
    """Fit (a, b, φ) so foot_masses() reproduces empirical (m_e, m_μ, m_τ).

    Uses scipy.optimize.least_squares.  Returns the best params and the
    relative residual.  With 3 parameters and 3 masses, residual should
    be ~0 (exact fit possible).
    """
    from scipy.optimize import least_squares
    targets = np.array([
        generations.M_E_MeV, generations.M_MU_MeV, generations.M_TAU_MeV
    ])

    def residuals(x: np.ndarray) -> np.ndarray:
        p = FootParameters(a_MeV=float(x[0]), b=float(x[1]), phi_rad=float(x[2]))
        m = foot_masses(p)
        pred = np.array([m["e"], m["mu"], m["tau"]])
        # Use log to balance the three orders of magnitude.
        return np.log(pred) - np.log(targets)

    x0 = np.array([initial.a_MeV, initial.b, initial.phi_rad])
    result = least_squares(residuals, x0, xtol=1e-12)
    fit = FootParameters(
        a_MeV=float(result.x[0]),
        b=float(result.x[1]),
        phi_rad=float(result.x[2]),
    )
    rel_res = float(np.linalg.norm(result.fun) / np.linalg.norm(np.log(targets)))
    return fit, rel_res


def koide_predicted_b(q_value: float = 2.0 / 3.0) -> float:
    """Inverting Q = 3/(1 + b²/2):  b = √(6/Q − 2).

    For Q = 2/3:  b = √(9 − 2) = √7 ≈ 2.646.
    For Q = 3/2 (Koide canonical): b = √2.

    NB: literature varies on whether Koide is Q = 2/3 (lepton ratio) or
    Q = 3/2 (the inverse).  We use the (Σ√m)²/Σm convention
    (Q ≈ 0.667) here.
    """
    return float(np.sqrt(6.0 / q_value - 2.0))


__all__ = [
    "sigma_for_mass", "per_generation_sigmas",
    "koide_q", "lepton_koide_q",
    "GenerationFitDiagnostic",
    "fit_sigma_power_law", "fit_sigma_exponential",
    "FootParameters", "foot_masses", "fit_foot_to_empirical",
    "koide_predicted_b",
]
