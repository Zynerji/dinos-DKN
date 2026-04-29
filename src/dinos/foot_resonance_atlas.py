"""Atlas of confirmed Foot+Koide resonances at metallic b values
(HYPOTHESIS Step 16).

Catalogs the three confirmed Foot+Koide resonances, each with:
  - A metallic-ratio coupling b
  - A specific mixing angle phi (sometimes simple, sometimes not)
  - Predicted vs empirical masses to high precision

Confirmed resonances
--------------------

| # | Family                | b (metallic)              | phi or cos(phi)       |
|---|-----------------------|---------------------------|----------------------|
| 1 | Charged leptons       | silver - 1 = sqrt(2)      | phi = 2/9 (1 sigma)  |
| 2 | Vector mesons rho/omega/phi | 1/bronze^2          | phi ~ 0 (rho-omega degenerate) |
| 3 | Light baryons N/Lambda/Xi  | 1/(silver*copper)   | cos(phi) ~ 7/8 (within 0.5%) |

Each metallic invariant gives a specific Foot resonance at all-positive
branch (1 + b cos > 0 for all l), uniquely determining the three masses
up to the overall scale a.

Honest scope statement
----------------------
- These three are the ONLY 3-state mass triplets identified to date
  whose b values fit metallic-ratio expressions to better than 0.1%.
- Dense candidate basis admits MANY 1%-level fits; only the sub-0.1%
  fits survive the random-baseline discrimination test (Step 15).
- The metallic invariance hypothesis is empirically confirmed for these
  three families. Whether it extends further requires:
  (a) more fragment data with similarly clean Q values,
  (b) deeper structural understanding of why specific metallics appear
      for each fermion sector.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import acos, cos, pi, sqrt

import numpy as np

from . import metallic_invariant_sweep as mis


@dataclass(frozen=True)
class FootResonance:
    """A confirmed Foot+Koide resonance at metallic b."""
    family: str
    members: tuple[str, ...]
    masses_MeV: tuple[float, float, float]
    b_expression: str
    b_value: float
    a_scale_MeV: float
    phi_rad: float
    cos_values: tuple[float, float, float]
    phi_simple_form: str       # "2/9", "0", "arccos(7/8)", or "(empirical)"
    foot_consistency_residual: float   # |Sum cos^2 - 3/2|
    max_mass_residual_pct: float


def derive_resonance(family: str, members: tuple[str, ...],
                     masses: list[float], b_expression: str,
                     b_value: float, phi_simple_form: str = "(empirical)"
                     ) -> FootResonance:
    """Derive a Foot resonance object from masses and a metallic b."""
    masses_sorted = tuple(sorted(masses))
    a = sum(masses_sorted) / (3 * (1 + b_value ** 2 / 2))
    cos_vals = tuple((sqrt(m / a) - 1) / b_value for m in masses_sorted)
    sum_cos = sum(cos_vals)
    sum_cos_sq = sum(c * c for c in cos_vals)
    consistency_residual = abs(sum_cos_sq - 1.5)
    # phi corresponds to the largest cosine
    phi = acos(min(max(max(cos_vals), -1.0), 1.0))
    # Compute predicted masses and check residuals
    predicted = sorted([
        a * (1 + b_value * cos(phi + l * 2 * pi / 3)) ** 2 for l in range(3)
    ])
    residuals = [abs(p - m) / m * 100 for p, m in zip(predicted, masses_sorted)]
    return FootResonance(
        family=family,
        members=members,
        masses_MeV=masses_sorted,
        b_expression=b_expression,
        b_value=b_value,
        a_scale_MeV=a,
        phi_rad=phi,
        cos_values=cos_vals,
        phi_simple_form=phi_simple_form,
        foot_consistency_residual=consistency_residual,
        max_mass_residual_pct=max(residuals),
    )


# -----------------------------------------------------------------------------
# The three confirmed resonances
# -----------------------------------------------------------------------------

def lepton_resonance() -> FootResonance:
    """Charged leptons: b = silver - 1 = sqrt(2), phi = 2/9 within 1 sigma."""
    return derive_resonance(
        family="charged_leptons",
        members=("e", "mu", "tau"),
        masses=[0.51099895, 105.6583755, 1776.86],
        b_expression="silver - 1 = sqrt(2)",
        b_value=sqrt(2.0),
        phi_simple_form="2/9 (within 1 sigma)",
    )


def vector_meson_resonance() -> FootResonance:
    """Vector mesons rho/omega/phi: b = 1/bronze^2, phi ~ 0."""
    return derive_resonance(
        family="vector_mesons",
        members=("rho", "omega", "phi"),
        masses=[775.26, 782.65, 1019.46],
        b_expression="1/bronze^2",
        b_value=1.0 / (mis.BRONZE ** 2),
        phi_simple_form="phi ~ 0 (rho-omega degeneracy emerges naturally)",
    )


def light_baryon_resonance() -> FootResonance:
    """Light baryons (N, Lambda, Xi): b = 1/(silver*copper), cos(phi) ~ 7/8."""
    return derive_resonance(
        family="light_baryons",
        members=("N", "Lambda", "Xi"),
        masses=[938.92, 1115.68, 1318.3],
        b_expression="1/(silver*copper)",
        b_value=1.0 / (mis.SILVER * mis.COPPER),
        phi_simple_form="cos(phi) ~ 7/8 (within 0.5%)",
    )


def all_confirmed_resonances() -> list[FootResonance]:
    """The three confirmed Foot resonances at metallic b."""
    return [lepton_resonance(),
            vector_meson_resonance(),
            light_baryon_resonance()]


# -----------------------------------------------------------------------------
# Aggregate atlas
# -----------------------------------------------------------------------------

@dataclass(frozen=True)
class FootAtlas:
    resonances: list[FootResonance]
    n_confirmed: int
    notes: str


def generate_atlas() -> FootAtlas:
    """Compile the atlas of confirmed Foot resonances."""
    res = all_confirmed_resonances()
    notes = (
        "Three confirmed Foot+Koide resonances at metallic b values: "
        "(1) charged leptons at b = silver - 1 with phi = 2/9; "
        "(2) vector mesons (rho, omega, phi) at b = 1/bronze^2 with phi ~ 0 "
        "(naturally explaining rho-omega degeneracy); "
        "(3) light baryons (N, Lambda, Xi) at b = 1/(silver*copper) with "
        "cos(phi) close to 7/8. All three exhibit the all-positive Foot "
        "branch with full ansatz consistency (Sum cos^2 = 3/2 to 4 decimals)."
    )
    return FootAtlas(
        resonances=res,
        n_confirmed=len(res),
        notes=notes,
    )


__all__ = [
    "FootResonance", "derive_resonance",
    "lepton_resonance", "vector_meson_resonance", "light_baryon_resonance",
    "all_confirmed_resonances",
    "FootAtlas", "generate_atlas",
]
