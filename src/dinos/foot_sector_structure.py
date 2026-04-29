"""Sector-level structural patterns in the metallic Foot atlas
(HYPOTHESIS Step 36).

Three observations from analyzing all 25+ confirmed metallic Foot
resonances together (canonical 19 + 4 quark generations + 6 heavy
baryons):

1. Charged-lepton saturation
----------------------------
The charged leptons (e, mu, tau) sit at b = silver - 1 = sqrt(2).
This is exactly the Koide constraint Q = (sum sqrt m)^2 / sum m = 3/2.
The bound b <= sqrt(2) is the maximum achievable b in the all-positive
branch (where every (1 + b cos(theta_l)) > 0 for l = 0, 1, 2).
Charged leptons are the unique three-state SM family that saturates
this geometric bound.

2. Heavy-quark family universality
-----------------------------------
The (c, b, t) triplet sits at implied b = 1.4201, within 0.4% of
b = silver - 1 = sqrt(2). The same metallic invariant as charged
leptons. This suggests a heavy-fermion universality: all generations
that are sufficiently spread (m_3/m_1 >> 1) flow to the silver-
saturation point.

3. Sign-flip branch population
------------------------------
Triplets with implied b > sqrt(2) cannot live in the all-positive
branch. The (u, c, t) up-type triplet at b = 1.76 and (d, s, b) at
b = 1.55 exceed sqrt(2), forcing them into the sign-flip branch
(at least one negative factor) — exactly the Foot-Brannen branch
that hosts the neutrinos. This unites quarks and neutrinos as
sign-flip-branch fermions, distinct from charged leptons.

4. Scale invariance of b
------------------------
Across the atlas (mass scales 0.5 MeV to 172 GeV, ~3.5e8x range),
log(b) shows R^2 = 0.04 vs log(geometric mean of triplet masses).
b is essentially uncorrelated with mass scale. This rules out the
trivial interpretation that "b is small whenever masses are heavy."
Instead, b encodes a discrete metallic invariant of the triplet
geometry, independent of overall scale.

5. Metallic factor counts
-------------------------
Across 19 canonical entries, the metallic-factor distribution is:
- 1 factor:  7  (e.g., silver-1, 1/copper^2, 1/plastic)
- 2 factors: 11 (e.g., 1/(silver*copper), bronze/nickel)
- 3 factors: 1  (1/(golden*nickel*plastic))

The bias toward 2-factor combinations is strong. This is the
signature of a *binary* algebraic structure, not a free-form
combinatorial fit.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import sqrt
from collections import Counter

import numpy as np

from . import foot_atlas_discrimination as fad
from . import heavy_baryon_foot as hbf
from . import metallic_invariant_sweep as mis
from . import quark_generation_foot as qgf


# Bound: in all-positive branch (1 + b cos(theta_l) > 0 for l=0,1,2),
# the maximum b that satisfies the Koide constraint Q = 3/2 is sqrt(2).
B_KOIDE_BOUND: float = sqrt(2.0)


@dataclass(frozen=True)
class FermionGenerationStatus:
    """Whether a fermion generation triplet sits in the all-positive
    or sign-flip branch."""
    triplet_label: str
    implied_b: float
    branch: str         # "positive" or "sign-flip"
    distance_from_silver_pct: float


def fermion_generation_status() -> list[FermionGenerationStatus]:
    """Classify each known fermion generation by branch."""
    triplets = {
        "charged_leptons": [0.51099895, 105.6583755, 1776.86],
        "up-type_quarks":  [2.16, 1270.0, 172690.0],
        "down-type_quarks": [4.67, 93.4, 4180.0],
        "neutrinos_normal": [0.001, 0.009, 0.05],
    }
    out = []
    for name, masses in triplets.items():
        b = fad.implied_b(masses)
        branch = "positive" if b <= B_KOIDE_BOUND else "sign-flip"
        d = (b - sqrt(2.0)) / sqrt(2.0) * 100
        out.append(FermionGenerationStatus(
            triplet_label=name, implied_b=b,
            branch=branch, distance_from_silver_pct=d,
        ))
    return out


@dataclass(frozen=True)
class ScaleInvariance:
    """Linear-fit summary: log(b) vs log(geometric mean of triplet)."""
    n_triplets: int
    slope: float
    intercept: float
    r_squared: float


def b_scale_invariance() -> ScaleInvariance:
    """Confirm b is scale-invariant across the full extended atlas."""
    pairs = []
    for fam, masses in fad.ATLAS_19_MASSES.items():
        b = fad.implied_b(masses)
        gm = float(np.exp(np.mean(np.log(masses))))
        pairs.append((b, gm))
    for label, members in hbf.HEAVY_TRIPLETS.items():
        masses = [hbf.HEAVY_BARYON_MASSES[m] for m in members]
        b = fad.implied_b(masses)
        gm = float(np.exp(np.mean(np.log(masses))))
        pairs.append((b, gm))
    x = np.log([p[1] for p in pairs])
    y = np.log([p[0] for p in pairs])
    A = np.vstack([x, np.ones_like(x)]).T
    sl, ic = np.linalg.lstsq(A, y, rcond=None)[0]
    yp = sl * x + ic
    ss_res = np.sum((y - yp) ** 2)
    ss_tot = np.sum((y - y.mean()) ** 2)
    return ScaleInvariance(
        n_triplets=len(pairs), slope=float(sl),
        intercept=float(ic),
        r_squared=float(1 - ss_res / ss_tot),
    )


@dataclass(frozen=True)
class MetallicFactorStats:
    """Metallic-factor distribution across canonical 19."""
    n_factor_distribution: dict[int, int]
    ratio_usage_count: dict[str, int]


def metallic_factor_stats() -> MetallicFactorStats:
    from . import foot_canonical_atlas as fca
    nfact: dict[int, int] = {}
    rcount: Counter = Counter()
    for e in fca.CANONICAL_ATLAS:
        nfact[e.n_metallic_factors] = nfact.get(e.n_metallic_factors, 0) + 1
        txt = e.b_expression.lower()
        for r in mis.METALLIC_RATIOS:
            if r in txt:
                rcount[r] += txt.count(r)
    return MetallicFactorStats(
        n_factor_distribution=nfact,
        ratio_usage_count=dict(rcount),
    )


__all__ = [
    "B_KOIDE_BOUND",
    "FermionGenerationStatus", "fermion_generation_status",
    "ScaleInvariance", "b_scale_invariance",
    "MetallicFactorStats", "metallic_factor_stats",
]
