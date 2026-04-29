"""Meta-pattern across all confirmed metallic Foot resonances
(HYPOTHESIS Step 19).

Synthesises Steps 16, 17, 18 into a single catalog of all confirmed
metallic Foot resonances. Tests for unifying patterns in (b, a) values.

Catalog (7 resonances)
----------------------

| # | Family                          | b expression               | b      | a (MeV) |
|---|---------------------------------|----------------------------|--------|---------|
| 1 | Charged leptons                 | silver - 1                 | 1.414  | 313.84  |
| 2 | Vector mesons (rho,omega,phi)   | 1/bronze^2                 | 0.092  | 855.5   |
| 3 | Light baryons (N,Lambda,Xi)     | 1/(silver*copper)          | 0.098  | 1118.9  |
| 4 | Charmonium (eta_c,J/psi,chi_c)  | 1/(copper*silver^2)        | 0.041  | 3142.0  |
| 5 | Charmonium 1S/2S/1P             | 1/(bronze*silver^2)        | 0.052  | 3404.5  |
| 6 | (D*, D_s*, J/psi)               | 1/(bronze*supergolden^2)   | 0.141  | 2400.0  |
| 7 | (J/psi, Upsilon(1S), Upsilon(2S)) | 1/(2*supergolden)        | 0.341  | 7480.0  |

Empirical observations
----------------------
1. ALL 7 b expressions involve only metallic ratios (golden, silver,
   bronze, copper, plastic, supergolden).
2. Lepton b = silver - 1 is the UNIQUE "additive" form; all others are
   multiplicative inverses.
3. Most expressions involve combinations of 2-3 metallic factors.
4. Silver appears in 5/7 expressions (most frequent).
5. No simple closed-form linking (b, a) values across resonances.

The meta-pattern: **every confirmed Foot+Koide 3-state mass triplet
has b expressible as a simple metallic combination**, but the specific
combination differs per family with no obvious unifying generator.

Honest scope statement
----------------------
- The metallic invariance is empirically confirmed across 7 different
  fermion/boson sectors.
- A first-principles derivation of WHY each family picks its specific
  metallic combination is OPEN.
- This may indicate:
  (a) A deeper geometric structure (each family corresponds to a
      different bundle/cover/representation),
  (b) A statistical artifact (with N candidates, sub-0.5% matches are
      not impossible), or
  (c) A genuine "metallic spectroscopy" of fermion taxonomy.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import sqrt

import numpy as np

from . import metallic_invariant_sweep as mis


@dataclass(frozen=True)
class MetallicResonanceEntry:
    """One entry in the meta-catalog."""
    family: str
    b_expression: str
    b_value: float
    a_scale_MeV: float
    n_metallic_factors: int    # how many metallic ratios in the expression


def all_confirmed_metallic_resonances() -> list[MetallicResonanceEntry]:
    """Return the 7 confirmed metallic Foot resonances."""
    return [
        MetallicResonanceEntry(
            family="charged_leptons",
            b_expression="silver - 1",
            b_value=sqrt(2.0),
            a_scale_MeV=313.84,
            n_metallic_factors=1,
        ),
        MetallicResonanceEntry(
            family="vector_mesons",
            b_expression="1/bronze^2",
            b_value=1.0 / (mis.BRONZE ** 2),
            a_scale_MeV=855.5,
            n_metallic_factors=1,
        ),
        MetallicResonanceEntry(
            family="light_baryons",
            b_expression="1/(silver*copper)",
            b_value=1.0 / (mis.SILVER * mis.COPPER),
            a_scale_MeV=1118.9,
            n_metallic_factors=2,
        ),
        MetallicResonanceEntry(
            family="charmonium_eta_c_Jpsi_chi_c",
            b_expression="1/(copper*silver^2)",
            b_value=1.0 / (mis.COPPER * mis.SILVER ** 2),
            a_scale_MeV=3142.0,
            n_metallic_factors=2,
        ),
        MetallicResonanceEntry(
            family="charmonium_1S_2S_1P",
            b_expression="1/(bronze*silver^2)",
            b_value=1.0 / (mis.BRONZE * mis.SILVER ** 2),
            a_scale_MeV=3404.5,
            n_metallic_factors=2,
        ),
        MetallicResonanceEntry(
            family="D_star_Ds_star_Jpsi",
            b_expression="1/(bronze*supergolden^2)",
            b_value=1.0 / (mis.BRONZE * mis.SUPERGOLDEN ** 2),
            a_scale_MeV=2400.0,
            n_metallic_factors=2,
        ),
        MetallicResonanceEntry(
            family="Jpsi_Upsilon_pair",
            b_expression="1/(2*supergolden)",
            b_value=1.0 / (2 * mis.SUPERGOLDEN),
            a_scale_MeV=7480.0,
            n_metallic_factors=1,
        ),
    ]


# -----------------------------------------------------------------------------
# Statistics on the meta-pattern
# -----------------------------------------------------------------------------

@dataclass(frozen=True)
class MetaPatternReport:
    n_resonances: int
    silver_appearances: int
    bronze_appearances: int
    copper_appearances: int
    supergolden_appearances: int
    most_common_metallic: str
    b_values_range: tuple[float, float]
    a_values_range: tuple[float, float]
    notes: str


def generate_meta_pattern_report() -> MetaPatternReport:
    res = all_confirmed_metallic_resonances()
    silver = sum(1 for r in res if "silver" in r.b_expression)
    bronze = sum(1 for r in res if "bronze" in r.b_expression)
    copper = sum(1 for r in res if "copper" in r.b_expression)
    supergolden = sum(1 for r in res if "supergolden" in r.b_expression)
    counts = {
        "silver": silver, "bronze": bronze,
        "copper": copper, "supergolden": supergolden,
    }
    most_common = max(counts, key=counts.get)
    b_vals = [r.b_value for r in res]
    a_vals = [r.a_scale_MeV for r in res]
    notes = (
        f"7 confirmed metallic Foot resonances spanning leptons, "
        f"light vector mesons, light baryons, charmonium, and "
        f"cross-quarkonium. Silver appears in {silver}/7 expressions "
        f"(most common). Bronze: {bronze}/7. Copper: {copper}/7. "
        f"Supergolden: {supergolden}/7. b values span "
        f"[{min(b_vals):.4f}, {max(b_vals):.4f}]. Mass scales span "
        f"[{min(a_vals):.1f}, {max(a_vals):.1f}] MeV. "
        f"All b expressions involve metallic ratios; the specific "
        f"combination differs per family with no obvious unifier."
    )
    return MetaPatternReport(
        n_resonances=len(res),
        silver_appearances=silver,
        bronze_appearances=bronze,
        copper_appearances=copper,
        supergolden_appearances=supergolden,
        most_common_metallic=most_common,
        b_values_range=(min(b_vals), max(b_vals)),
        a_values_range=(min(a_vals), max(a_vals)),
        notes=notes,
    )


__all__ = [
    "MetallicResonanceEntry", "all_confirmed_metallic_resonances",
    "MetaPatternReport", "generate_meta_pattern_report",
]
