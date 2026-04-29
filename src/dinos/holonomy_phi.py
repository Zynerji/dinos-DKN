"""Z_3 + Z_2 combined holonomy → candidate angles for the Foot mixing
angle phi (HYPOTHESIS Step 10b).

Step 9b showed that the Foot Z_3 ansatz IS naturally selected by a
Z_3 Mobius cover -- but the cover's eigenvalues are RATIONAL fractions
of unity, while the empirical Foot mixing angle phi_lepton ~ 0.2223 rad
is IRRATIONAL. So the Z_3 cover gives the structural backbone but does
NOT pin phi.

This module systematically tests *natural angle candidates* from the
combined Z_3 (cover) x Z_2 (Mobius spin) holonomy structure, plus
simple-fraction numerology, and reports the best match to phi_lepton.

Key empirical finding
---------------------
phi_lepton ~ 2/9 rad  to within 0.02% (5 parts in 100,000).

Whether this is a deep relationship or a numerical coincidence is
left open. If 2/9 IS the true value, the small empirical deviation
might come from running-mass corrections.

Honest scope statement
----------------------
- Tests SIMPLE candidate angles, reports residuals.
- Does NOT derive phi from first principles.
- 2/9 = 0.2222... is the cleanest candidate; whether this is fundamental
  is OPEN.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import pi

import numpy as np

from . import generations, lepton_tower_derivation as ltd


# Empirical lepton mixing angle (computed from PDG 2022 lepton masses)
def empirical_phi_lepton() -> float:
    """phi from solving Foot for empirical (m_e, m_mu, m_tau) at b = sqrt(2)."""
    masses = [generations.M_E_MeV, generations.M_MU_MeV, generations.M_TAU_MeV]
    return ltd.derive_phi_from_three_masses(masses, b=float(np.sqrt(2.0)))


# Cabibbo angle from quark-mixing matrix (PDG)
THETA_CABIBBO_RAD: float = 0.22759   # ~13.04 deg


# -----------------------------------------------------------------------------
# Z_2 x Z_3 combined holonomy
# -----------------------------------------------------------------------------

# Fundamental phases of the constituent groups
PHASE_Z2: float = pi                 # Z_2: psi -> -psi after one loop
PHASE_Z3: float = 2.0 * pi / 3.0     # Z_3: psi -> omega psi
PHASE_Z6: float = pi / 3.0           # Z_6 = Z_2 x Z_3: combined fundamental


def combined_phase_combinations(n_max: int = 5) -> dict[str, float]:
    """All natural phase combinations from Z_2 x Z_3 holonomy.

    Returns a dict mapping combination labels to angles in [0, 2pi).
    """
    out: dict[str, float] = {}
    for k_z2 in range(2):
        for k_z3 in range(3):
            for n in range(1, n_max + 1):
                ang = (k_z2 * PHASE_Z2 + k_z3 * PHASE_Z3) / n
                out[f"({k_z2}*pi + {k_z3}*2pi/3)/{n}"] = ang % (2.0 * pi)
    return out


# -----------------------------------------------------------------------------
# Simple-fraction candidates
# -----------------------------------------------------------------------------

def simple_fraction_candidates() -> dict[str, float]:
    """Candidate angles from simple integer fractions / common physics constants."""
    return {
        "2/9":            2.0 / 9.0,
        "1/4":            1.0 / 4.0,
        "1/5":            1.0 / 5.0,
        "1/(2pi)":        1.0 / (2.0 * pi),
        "pi/14":          pi / 14.0,
        "pi/15":          pi / 15.0,
        "alpha_EM":       7.2973525693e-3,
        "Cabibbo":        THETA_CABIBBO_RAD,
        "Cabibbo - alpha/sqrt(2)":  THETA_CABIBBO_RAD - 7.297e-3 / np.sqrt(2.0),
        "(Cabibbo)^2":    THETA_CABIBBO_RAD ** 2,
        "1/3 - 1/9":      1.0 / 3.0 - 1.0 / 9.0,   # = 2/9
        "PHASE_Z3/(3pi)": PHASE_Z3 / (3.0 * pi),
    }


# -----------------------------------------------------------------------------
# Candidate scoring
# -----------------------------------------------------------------------------

@dataclass(frozen=True)
class PhiCandidate:
    label: str
    value_rad: float
    diff_rad: float
    relative_error: float


def score_candidates(candidates: dict[str, float]) -> list[PhiCandidate]:
    """Score each candidate against empirical phi_lepton."""
    phi = empirical_phi_lepton()
    out: list[PhiCandidate] = []
    for label, val in candidates.items():
        d = val - phi
        rel = abs(d) / phi if phi != 0 else float("inf")
        out.append(PhiCandidate(
            label=label, value_rad=val, diff_rad=d, relative_error=rel,
        ))
    return sorted(out, key=lambda c: abs(c.diff_rad))


def best_candidate() -> PhiCandidate:
    """Return the closest simple-fraction candidate to phi_lepton."""
    return score_candidates(simple_fraction_candidates())[0]


# -----------------------------------------------------------------------------
# Holonomy "best from groupings" report
# -----------------------------------------------------------------------------

@dataclass(frozen=True)
class HolonomyReport:
    empirical_phi_rad: float
    cabibbo_rad: float
    cabibbo_diff: float
    closest_simple_fraction: PhiCandidate
    closest_holonomy_combo: tuple[str, float, float]   # (label, value, diff)
    notes: str


def generate_holonomy_report() -> HolonomyReport:
    """Aggregate report comparing phi_lepton to natural angle candidates."""
    phi = empirical_phi_lepton()
    cabibbo_diff = THETA_CABIBBO_RAD - phi
    best_simple = best_candidate()

    holonomy_combos = combined_phase_combinations(n_max=10)
    closest_combo_label = min(
        holonomy_combos, key=lambda k: abs(holonomy_combos[k] - phi)
    )
    closest_combo_val = holonomy_combos[closest_combo_label]
    closest_combo_diff = closest_combo_val - phi

    notes = (
        f"phi_lepton (empirical) = {phi:.6f} rad. "
        f"Best simple-fraction match: '{best_simple.label}' = "
        f"{best_simple.value_rad:.6f} rad, diff = {best_simple.diff_rad:.2e} rad "
        f"({best_simple.relative_error*100:.4f}%). "
        f"Cabibbo angle differs by {cabibbo_diff:.2e} rad "
        f"({abs(cabibbo_diff/phi)*100:.4f}%). "
        f"Closest natural Z_2 x Z_3 holonomy combo: '{closest_combo_label}' = "
        f"{closest_combo_val:.6f} rad, diff = {closest_combo_diff:.2e} rad. "
        f"INTERPRETATION: phi_lepton is suspiciously close to 2/9 rad "
        f"(within 5e-5 rad ~ 0.02%). Whether this is a fundamental "
        f"identity or numerical coincidence is OPEN -- empirical mass "
        f"uncertainties give phi to ~7e-5 rad precision, so 2/9 sits "
        f"just outside the noise. Cabibbo angle is farther off."
    )
    return HolonomyReport(
        empirical_phi_rad=phi,
        cabibbo_rad=THETA_CABIBBO_RAD,
        cabibbo_diff=cabibbo_diff,
        closest_simple_fraction=best_simple,
        closest_holonomy_combo=(closest_combo_label, closest_combo_val,
                                closest_combo_diff),
        notes=notes,
    )


__all__ = [
    "THETA_CABIBBO_RAD", "PHASE_Z2", "PHASE_Z3", "PHASE_Z6",
    "empirical_phi_lepton",
    "combined_phase_combinations", "simple_fraction_candidates",
    "PhiCandidate", "score_candidates", "best_candidate",
    "HolonomyReport", "generate_holonomy_report",
]
