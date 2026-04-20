"""Dark-matter phenomenology of the DKN hidden scalar Φ_bag (paper §16).

The joint mass-closure (§14) and Derrick-closure (§12) converge on a single
new field with the properties of Theorem 16.6 / Remark 16.14:

    m_* = 0.156 ± 0.025 MeV
    λ_H = 0.129 ± 0.060
    v_bag = m_*/√λ_H ≃ 0.43 MeV
    y_e   = m_e/v_bag ≃ 1.19
    m_*·a = 0.153 ± 0.025

The testable predictions P1–P4 of §16.6 are implemented below. All formulas
are exactly those of the paper; experimental reference bounds are included
for convenience (XENONnT 2022, SENSEI 2020, EDGES 2018, Giannotti et al. 2017).
"""

from __future__ import annotations

from dataclasses import dataclass
from math import pi, sqrt

from . import constants as C


# -----------------------------------------------------------------------------
# Joint closure: (m_e, λ_H) ↦ (v_bag, m_*, y_e, a)        [eqs 71–72, Cor 16.2]
# -----------------------------------------------------------------------------

@dataclass(frozen=True)
class HiddenScalar:
    lambda_H: float        # scalar self-coupling
    v_bag_MeV: float       # bag VEV
    m_star_MeV: float      # hidden-scalar mass
    y_e: float             # Yukawa to electron
    m_star_times_a: float  # dimensionless m_*·a (must satisfy Derrick bound < 1)
    kappa: float           # m_*/m_e = 0.602 · λ_H^(1/3)   (eq. 72)


def joint_closure(lambda_H: float = C.lambda_H_DKN,
                  m_e_MeV: float = C.m_e_MeV,
                  C_bag: float = C.C_bag_Dirac,
                  alpha: float = C.alpha_EM) -> HiddenScalar:
    """Solve eqs (71)-(72) for the hidden-scalar parameters.

    Eq. 71:  v = [3 m_e³ (1 − 2𝒞 − α) / (2√2 π √λ_H)]^(1/3)
    Eq. 72:  m_* = √λ_H · v = 0.602 · λ_H^(1/3) · m_e
    """
    if lambda_H <= 0:
        raise ValueError("λ_H must be positive")
    one_minus_beta = 1.0 - 2.0 * C_bag - alpha
    v = (3.0 * m_e_MeV ** 3 * one_minus_beta / (2.0 * sqrt(2.0) * pi * sqrt(lambda_H))) ** (1.0 / 3.0)
    m_star = sqrt(lambda_H) * v
    kappa = m_star / m_e_MeV
    a_nat = 1.0 / (2.0 * m_e_MeV)   # MeV⁻¹
    return HiddenScalar(
        lambda_H=lambda_H,
        v_bag_MeV=v,
        m_star_MeV=m_star,
        y_e=m_e_MeV / v,
        m_star_times_a=m_star * a_nat,
        kappa=kappa,
    )


def derrick_bound_ok(scalar: HiddenScalar) -> bool:
    """Derrick bound m_* ≤ ℏ/a = 2 m_e c²  (paper Theorem 16.1 remark)."""
    return scalar.m_star_times_a <= 1.0


# -----------------------------------------------------------------------------
# P1 — Electron–DM elastic scattering cross section   [eq. 82]
# -----------------------------------------------------------------------------

# ℏc in MeV·cm:  1 MeV⁻¹ = ℏc/MeV = 1.97327e-11 cm
_MeV_inv_to_cm = C.hbar_c_MeV_fm * 1e-13   # 1.97327e-11 cm

def electron_dm_cross_section(scalar: HiddenScalar | None = None,
                              q_MeV: float = 0.0) -> float:
    """Eq. 82 — σ_eΦ(q) = y_e²/(4π) · m_e²/(q² + m_*²)².

    Returns σ in cm². Default q=0 gives the low-momentum-transfer limit.
    """
    if scalar is None:
        scalar = joint_closure()
    num = scalar.y_e ** 2 * C.m_e_MeV ** 2
    den = 4.0 * pi * (q_MeV ** 2 + scalar.m_star_MeV ** 2) ** 2
    sigma_MeV_inv2 = num / den
    return sigma_MeV_inv2 * _MeV_inv_to_cm ** 2


# -----------------------------------------------------------------------------
# P2 — 21-cm Rayleigh-type cooling signature (EDGES)
# -----------------------------------------------------------------------------
#
# Paper §16.6 P2: "sub-MeV dark scalar with m_* ~ 150 keV and Yukawa y_e ~ 1
# produces a Rayleigh-type cooling of the pre-reionization hydrogen gas matching
# the reported EDGES absorption anomaly within a factor 2."
#
# We do not re-derive the full 21-cm calculation here; we expose a window check.

EDGES_m_star_window_keV = (100.0, 250.0)
EDGES_y_e_window = (0.5, 2.0)

def matches_edges_anomaly(scalar: HiddenScalar | None = None) -> bool:
    """Return True if (m_*, y_e) lie inside the DKN-compatible EDGES window."""
    if scalar is None:
        scalar = joint_closure()
    in_mass = EDGES_m_star_window_keV[0] <= scalar.m_star_MeV * 1000 <= EDGES_m_star_window_keV[1]
    in_y = EDGES_y_e_window[0] <= scalar.y_e <= EDGES_y_e_window[1]
    return in_mass and in_y


# -----------------------------------------------------------------------------
# P3 — Electron self-form-factor shift from scalar exchange  [§16.6 P3]
# -----------------------------------------------------------------------------

def scalar_form_factor_shift(q_MeV: float, scalar: HiddenScalar | None = None) -> float:
    """ΔF₁^(Φ)(q²) = −y_e²/(6π²) · q²/m_*²   (for q ≲ 1 MeV).

    Distinct from the geometric bag term −½⟨r_e²⟩q²/3 by its different
    momentum dependence; separable by precision g−2 scans of loop momentum
    transfer.
    """
    if scalar is None:
        scalar = joint_closure()
    return -(scalar.y_e ** 2) / (6.0 * pi ** 2) * (q_MeV ** 2) / (scalar.m_star_MeV ** 2)


# -----------------------------------------------------------------------------
# P4 — Stellar-cooling bound (RGB, HB stars)
# -----------------------------------------------------------------------------
#
# Paper §16.6 P4: emission of Φ_bag via electron bremsstrahlung with effective
# vertex y_e contributes to RGB/HB cooling at ~10⁻³ of photon cooling — within
# current Giannotti et al. (2017) bounds but targetable with asteroseismology.

STELLAR_COOLING_FRACTION_PHOTON = 1.0e-3  # paper quoted order-of-magnitude

def stellar_cooling_fraction(scalar: HiddenScalar | None = None) -> float:
    """DKN stellar cooling rate as a fraction of photon cooling."""
    if scalar is None:
        scalar = joint_closure()
    # Order-of-magnitude scales as y_e² (coupling) times Boltzmann-suppression
    # factor for m_* in stellar-core temperatures (~10 keV). Paper keeps this at
    # ~10⁻³; we expose the scaling for custom scalars.
    baseline_y_e = C.m_e_MeV / C.v_bag_MeV
    return STELLAR_COOLING_FRACTION_PHOTON * (scalar.y_e / baseline_y_e) ** 2


# -----------------------------------------------------------------------------
# Experimental reference bounds (for plotting / consistency checks)
# -----------------------------------------------------------------------------

# XENONnT electronic-recoil 90% CL limit on sub-GeV DM–electron scattering
# (Aprile et al., PRL 129 (2022) 161805). Order of magnitude:
XENONNT_BOUND_cm2 = 1.0e-37

# SENSEI skipper-CCD bound (Barak et al., PRL 125 (2020) 171802)
SENSEI_BOUND_cm2 = 1.0e-36

def within_direct_detection_bounds(scalar: HiddenScalar | None = None) -> dict[str, bool]:
    """Sanity check against direct-detection upper limits."""
    sigma = electron_dm_cross_section(scalar)
    return {
        "sigma_cm2": sigma,
        "below_XENONnT": sigma < XENONNT_BOUND_cm2,
        "below_SENSEI":  sigma < SENSEI_BOUND_cm2,
    }


# -----------------------------------------------------------------------------
# Full report
# -----------------------------------------------------------------------------

def predictions(lambda_H: float = C.lambda_H_DKN) -> dict:
    """Emit every §16 DM prediction at a given λ_H."""
    s = joint_closure(lambda_H=lambda_H)
    return {
        "scalar": s,
        "sigma_eDM_cm2": electron_dm_cross_section(s),
        "edges_match":   matches_edges_anomaly(s),
        "dF1_at_q_1MeV": scalar_form_factor_shift(1.0, s),
        "stellar_cooling_fraction": stellar_cooling_fraction(s),
        "derrick_bound_ok": derrick_bound_ok(s),
        "direct_detection": within_direct_detection_bounds(s),
    }


__all__ = [
    "HiddenScalar", "joint_closure", "derrick_bound_ok",
    "electron_dm_cross_section", "matches_edges_anomaly",
    "scalar_form_factor_shift", "stellar_cooling_fraction",
    "XENONNT_BOUND_cm2", "SENSEI_BOUND_cm2",
    "within_direct_detection_bounds", "predictions",
]
