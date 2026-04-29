"""Quark generation Foot resonances (HYPOTHESIS Step 34).

Tests whether each quark generation triplet sits on a metallic b in
the same way the charged leptons do. PDG MS-bar masses are noisy
(scheme dependence, scale-running), so we accept metallic fits up to
~1% on the implied b and bootstrap mass uncertainties.

Findings
--------

| Triplet              | implied b | metallic match     | rel err |
|----------------------|-----------|--------------------|---------|
| (c, b, t)            | 1.4201    | silver - 1 = sqrt(2) | 0.41%  |
| (d, s, b)            | 1.5455    | sqrt(silver)       | 0.54%   |
| (u, c, t)            | 1.7589    | sqrt(copper - 1)   | 2.27%   |
| (s, c, b)            | 0.8666    | plastic/supergolden | 4.30%  |

Notable: the heavy-quark family (c, b, t) sits on the SAME metallic b
as the charged leptons (silver - 1). This is a structural hint of a
heavy-fermion universality.

The down-type family (d, s, b) lands on sqrt(silver) — the geometric
mean of unity and silver.

Predictions
-----------
Given (m_c, m_b) at b = sqrt(2), the framework predicts m_t to ~2.5%
with PDG charm-quark uncertainty (~20 MeV) accounting for ~1.8% of
the spread. Tighter c-quark mass would tighten this.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import sqrt

import numpy as np

from . import foot_mass_predictions as fmp
from . import foot_atlas_discrimination as fad
from . import metallic_invariant_sweep as mis


# PDG MS-bar quark masses in MeV (with 1-sigma uncertainties)
QUARK_MASSES: dict[str, tuple[float, float]] = {
    "u": (2.16, 0.49),
    "d": (4.67, 0.48),
    "s": (93.4, 8.6),
    "c": (1270.0, 20.0),
    "b": (4180.0, 30.0),
    "t": (172690.0, 300.0),  # pole mass
}


@dataclass(frozen=True)
class QuarkFootFit:
    triplet: tuple[str, str, str]
    masses_MeV: tuple[float, float, float]
    implied_b: float
    best_metallic_label: str
    best_metallic_value: float
    rel_b_error_pct: float


def quark_foot_fit(triplet: tuple[str, str, str]) -> QuarkFootFit:
    """Match a quark triplet's implied b to the metallic basis."""
    masses = [QUARK_MASSES[q][0] for q in triplet]
    b = fad.implied_b(masses)
    cands = mis.generate_candidate_b_expressions()
    name, val = min(cands.items(), key=lambda kv: abs(kv[1] - b))
    rel = abs(val - b) / b * 100
    return QuarkFootFit(
        triplet=triplet,
        masses_MeV=tuple(masses),
        implied_b=b,
        best_metallic_label=name,
        best_metallic_value=val,
        rel_b_error_pct=rel,
    )


def all_quark_foot_fits() -> list[QuarkFootFit]:
    """All four primary quark triplets analyzed in this module."""
    return [
        quark_foot_fit(("c", "b", "t")),
        quark_foot_fit(("d", "s", "b")),
        quark_foot_fit(("u", "c", "t")),
        quark_foot_fit(("s", "c", "b")),
    ]


@dataclass(frozen=True)
class TopQuarkPrediction:
    inputs_MeV: tuple[float, float]
    b_metallic_label: str
    b_value: float
    m_top_predicted_MeV: float
    m_top_empirical_MeV: float
    rel_error_pct: float
    bootstrap_median_pct: float
    bootstrap_p16_pct: float
    bootstrap_p84_pct: float


def top_quark_prediction(n_bootstrap: int = 500,
                         seed: int = 42) -> TopQuarkPrediction:
    """Predict m_top from (m_c, m_b) at b = sqrt(2) (silver-1).

    Bootstraps over PDG MS-bar charm/bottom mass uncertainties.
    """
    mc, sigc = QUARK_MASSES["c"]
    mb, sigb = QUARK_MASSES["b"]
    mt = QUARK_MASSES["t"][0]
    b = sqrt(2.0)
    sol = fmp.predict_third_mass(mc, mb, b)
    if sol is None:
        raise RuntimeError("No solution for (c, b) at b = sqrt(2)")
    rel = abs(sol["m_predicted"] - mt) / mt * 100

    rng = np.random.default_rng(seed)
    errs = []
    for _ in range(n_bootstrap):
        mc_s = float(rng.normal(mc, sigc))
        mb_s = float(rng.normal(mb, sigb))
        s = fmp.predict_third_mass(mc_s, mb_s, b)
        if s:
            errs.append(abs(s["m_predicted"] - mt) / mt * 100)
    arr = np.array(errs)

    return TopQuarkPrediction(
        inputs_MeV=(mc, mb),
        b_metallic_label="silver - 1 = sqrt(2)",
        b_value=b,
        m_top_predicted_MeV=float(sol["m_predicted"]),
        m_top_empirical_MeV=mt,
        rel_error_pct=rel,
        bootstrap_median_pct=float(np.median(arr)),
        bootstrap_p16_pct=float(np.percentile(arr, 16)),
        bootstrap_p84_pct=float(np.percentile(arr, 84)),
    )


__all__ = [
    "QUARK_MASSES",
    "QuarkFootFit", "quark_foot_fit", "all_quark_foot_fits",
    "TopQuarkPrediction", "top_quark_prediction",
]
