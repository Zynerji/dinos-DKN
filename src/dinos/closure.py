"""DKN mass self-consistency (paper §14).

Implements the dimensionless closure equation (paper eq. 61)

    1 = 8π a³ σ + 2𝒞 + α

with its unique positive solution (Theorem 14.1),

    a  = [(1 - 2𝒞 - α) / (8πσ)]^(1/3)
    m_e = 1/(2a) = [πσ / (1 - 2𝒞 - α)]^(1/3)        (natural units)
    m_e c² = [πσ ℏ²c⁵ / (1 - 2𝒞 - α)]^(1/3)         (SI units).

All σ values below are in natural units (MeV³, i.e. (MeV/c²)³ · (ℏc)³).
"""

from __future__ import annotations

from dataclasses import dataclass
from math import pi, sqrt

from . import constants as C


# -----------------------------------------------------------------------------
# Forward / inverse closure
# -----------------------------------------------------------------------------

def compton_radius(sigma_MeV3: float, C_bag: float, alpha: float = C.alpha_EM) -> float:
    """Solve (62): a = [(1 − 2𝒞 − α)/(8πσ)]^(1/3).

    Returns ``a`` in MeV⁻¹.
    """
    numerator = 1.0 - 2.0 * C_bag - alpha
    if numerator <= 0:
        raise ValueError(f"2C + α ≥ 1 (2C+α = {2*C_bag + alpha:.4f}); no positive root")
    if sigma_MeV3 <= 0:
        raise ValueError("σ must be strictly positive")
    return (numerator / (8.0 * pi * sigma_MeV3)) ** (1.0 / 3.0)


def electron_mass(sigma_MeV3: float, C_bag: float = C.C_bag_Dirac,
                  alpha: float = C.alpha_EM) -> float:
    """Solve (63): m_e = [πσ / (1 − 2𝒞 − α)]^(1/3).

    Returns ``m_e`` in MeV.
    """
    a = compton_radius(sigma_MeV3, C_bag, alpha)
    return 1.0 / (2.0 * a)


def required_surface_tension(m_e_MeV: float = C.m_e_MeV,
                             C_bag: float = C.C_bag_Dirac,
                             alpha: float = C.alpha_EM) -> float:
    """Inverse of (63): σ = m_e³ (1 − 2𝒞 − α) / π     [eq. 65].

    Returns σ in MeV³.
    """
    return m_e_MeV ** 3 * (1.0 - 2.0 * C_bag - alpha) / pi


def required_bag_vev(sigma_MeV3: float, lambda_H: float = C.lambda_H_SM) -> float:
    """Invert Proposition 8.1: σ = (2√2/3)·√λ_H · v³   ⇒   v = [3σ/(2√2·√λ_H)]^(1/3).

    Returns the Higgs VEV inside the bag in MeV (eq. 66).
    """
    if sigma_MeV3 <= 0 or lambda_H <= 0:
        raise ValueError("σ and λ_H must be positive")
    return (3.0 * sigma_MeV3 / (2.0 * sqrt(2.0) * sqrt(lambda_H))) ** (1.0 / 3.0)


# -----------------------------------------------------------------------------
# Fractional decomposition (Corollary 14.3)
# -----------------------------------------------------------------------------

@dataclass(frozen=True)
class MassFractions:
    """Three-term decomposition of the electron rest energy.

    8π a³ σ + 2𝒞 + α = 1.
    """
    higgs_wall: float      # 1 − 2𝒞 − α
    dirac_casimir: float   # 2𝒞
    em_self: float         # α
    total: float           # sum (sanity check — should be 1)


def mass_fractions(C_bag: float = C.C_bag_Dirac,
                   alpha: float = C.alpha_EM) -> MassFractions:
    """Fractional decomposition of m_e c² (Table 14.2)."""
    dirac = 2.0 * C_bag
    em = alpha
    wall = 1.0 - dirac - em
    return MassFractions(
        higgs_wall=wall,
        dirac_casimir=dirac,
        em_self=em,
        total=wall + dirac + em,
    )


# -----------------------------------------------------------------------------
# Full closure report
# -----------------------------------------------------------------------------

@dataclass(frozen=True)
class ClosureResult:
    sigma_MeV3: float
    C_bag: float
    alpha: float
    a_MeV_inv: float
    a_m: float
    m_e_MeV: float
    v_bag_MeV: float
    fractions: MassFractions


def full_closure(m_e_MeV: float = C.m_e_MeV,
                 C_bag: float = C.C_bag_Dirac,
                 alpha: float = C.alpha_EM,
                 lambda_H: float = C.lambda_H_SM) -> ClosureResult:
    """End-to-end inverse closure: from empirical m_e back to (σ, v_bag).

    Reproduces every number in paper §14.2.
    """
    sigma = required_surface_tension(m_e_MeV, C_bag, alpha)
    a_nat = compton_radius(sigma, C_bag, alpha)
    a_m = a_nat * C.hbar_c_eV_m * 1e-6  # MeV⁻¹ → m via ℏc
    v = required_bag_vev(sigma, lambda_H)
    return ClosureResult(
        sigma_MeV3=sigma,
        C_bag=C_bag,
        alpha=alpha,
        a_MeV_inv=a_nat,
        a_m=a_m,
        m_e_MeV=1.0 / (2.0 * a_nat),
        v_bag_MeV=v,
        fractions=mass_fractions(C_bag, alpha),
    )


__all__ = [
    "compton_radius", "electron_mass", "required_surface_tension",
    "required_bag_vev", "mass_fractions", "full_closure",
    "MassFractions", "ClosureResult",
]
