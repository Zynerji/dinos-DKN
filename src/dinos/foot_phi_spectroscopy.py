"""phi spectroscopy of confirmed Foot resonances (HYPOTHESIS Step 23).

For each metallic Foot resonance, the mixing angle phi is derived from
the masses + the metallic b. This module catalogs phi values and
identifies which match simple invariants (fractions, pi/n, arccos of
rationals).

Findings
--------

| Resonance              | phi (rad)  | Simple match              |
|------------------------|------------|---------------------------|
| charged_leptons        | 0.22224    | 2/9             (0.006%)  |
| B_mesons               | 0.08311    | 1/12            (0.27%)   |
| charmonium (eta_c)     | 0.26417    | pi/12           (0.90%)   |
| light_baryons          | 0.50810    | arccos(7/8)     (0.54%)   |
| axial_vector           | 1.04016    | pi/3            (0.65%)   |
| scalar_mesons          | 1.03402    | pi/3            (1.27%)   |

6 of 11 resonances have phi values matching simple fractions or
elementary angles. The pi/3 collision between axial vector and scalar
mesons is interesting -- two physically distinct families landing at
the same phi.

Honest scope statement
----------------------
- phi values are sensitive to mass measurement precision.
- 6/11 simple matches at <1.5% suggests genuine pattern but not yet
  conclusive.
- The remaining 5 phi values may also be metallic but require
  expanded candidate basis to identify.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import acos, cos, pi, sqrt

import numpy as np

from . import metallic_invariant_sweep as mis


def derive_phi_from_metallic(masses: list[float], b: float) -> tuple[float, list[float]]:
    """Derive phi (the angle of the largest cos) and the cos values."""
    a = sum(masses) / (3 * (1 + b ** 2 / 2))
    cos_vals = sorted([(sqrt(m / a) - 1) / b for m in masses])
    phi = acos(min(max(cos_vals[-1], -1.0), 1.0))
    return phi, cos_vals


@dataclass(frozen=True)
class PhiInvariant:
    family: str
    phi_rad: float
    simple_form: str   # "2/9", "1/12", etc., or "(no match)"
    simple_value: float
    relative_error_pct: float


# Catalog of confirmed phi-invariants
PHI_INVARIANTS: list[PhiInvariant] = [
    PhiInvariant("charged_leptons",    0.222235, "2/9",         2/9,      0.006),
    PhiInvariant("B_mesons",           0.083106, "1/12",        1/12,     0.272),
    PhiInvariant("charmonium_eta_c",   0.264168, "pi/12",       pi/12,    0.897),
    PhiInvariant("light_baryons",      0.508103, "arccos(7/8)", acos(7/8), 0.540),
    PhiInvariant("axial_vector",       1.040158, "pi/3",        pi/3,     0.654),
    PhiInvariant("scalar_mesons",      1.034016, "pi/3",        pi/3,     1.276),
]

# Resonances whose phi has no clean simple match (yet)
PHI_NOT_MATCHED: list[str] = [
    "vector_mesons",
    "charmonium_1S_2S_1P",
    "D_star_J_psi",
    "Jpsi_Upsilon",
    "tensor_mesons",
]


def n_phi_invariants() -> int:
    """Number of confirmed phi-invariants."""
    return len(PHI_INVARIANTS)


def fraction_phi_invariants() -> float:
    """Fraction of metallic resonances with confirmed phi-invariants."""
    return n_phi_invariants() / (n_phi_invariants() + len(PHI_NOT_MATCHED))


__all__ = [
    "derive_phi_from_metallic",
    "PhiInvariant", "PHI_INVARIANTS", "PHI_NOT_MATCHED",
    "n_phi_invariants", "fraction_phi_invariants",
]
