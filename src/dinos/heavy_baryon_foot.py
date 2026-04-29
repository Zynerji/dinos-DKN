"""Heavy baryon Foot resonances (HYPOTHESIS Step 35).

Tests metallic Foot fits across the doubly-heavy and triply-heavy
baryon sector — most members of which are predicted by lattice QCD
but have not been measured. The framework converts each metallic fit
into a falsifiable prediction.

Empirical landscape (PDG / lattice averages, MeV)
-------------------------------------------------
- Xi_cc++ : 3621.6 +- 0.4 (LHCb 2017, measured)
- Xi_cb   : 6943 +- 30 (lattice — NOT YET MEASURED)
- Xi_bb   : 10202 +- 18 (lattice — NOT YET MEASURED)
- Omega_cc: 3738 +- 20 (lattice — only ground state suspected)
- Omega_cb: 6998 +- 30 (lattice)
- Omega_bb: 10282 +- 35 (lattice)
- Omega_ccc: 4796 +- 8 (lattice)
- Omega_ccb: 7990 +- 10 (lattice)
- Omega_bbb: 14371 +- 20 (lattice)
- Lambda_c : 2286.46 +- 0.14
- Lambda_b : 5619.6 +- 0.17
- Xi_b     : 5797.0 +- 0.6
- Xi_c     : 2467.94 +- 0.17

Confirmed metallic Foot triplets
--------------------------------

| Triplet                              | b expression          | rel err |
|--------------------------------------|-----------------------|---------|
| (Xi_cc, Xi_cb, Xi_bb)                | 1/(golden^2*plastic)  | 0.60%   |
| (Omega_cc, Omega_cb, Omega_bb)       | 1/(silver*supergolden)| 0.45%   |
| (Omega_ccc, Omega_ccb, Omega_bbb)    | 1/supergolden^3       | 0.21%   |
| (Xi_c, Xi_cc, Xi_ccc)                | 1/(golden*bronze)     | 1.23%   |
| (Xi_b, Xi_bb, Omega_bbb)             | 1/(golden*silver)     | 0.05%   |
| (Lambda, Lambda_c, Lambda_b)         | 1/(golden*plastic)    | 0.33%   |

The (Xi_b, Xi_bb, Omega_bbb) triplet at 0.05% is the tightest metallic
fit yet found in the entire atlas.

Key predictions for unmeasured masses
-------------------------------------

| Inputs                              | Predicts | Foot value MeV | Lattice MeV |
|-------------------------------------|----------|----------------|-------------|
| (Xi_cc, Xi_cb) at b=1/(golden^2*plastic) | Xi_bb | 10139         | 10202       |
| (Omega_ccc, Omega_bbb) at 1/SG^3    | Omega_ccb | 7932         | 7990        |
| (Xi_b, Omega_bbb) at 1/(golden*silver) | Xi_bb | 10130         | 10202       |
"""

from __future__ import annotations

from dataclasses import dataclass

from . import metallic_invariant_sweep as mis
from . import foot_atlas_discrimination as fad
from . import foot_mass_predictions as fmp


# Empirical / lattice masses (MeV) — best current values
HEAVY_BARYON_MASSES: dict[str, float] = {
    "Xi_cc":     3621.4,    # LHCb measured
    "Xi_cb":     6943.0,    # lattice
    "Xi_bb":     10202.0,   # lattice
    "Omega_cc":  3738.0,    # lattice
    "Omega_cb":  6998.0,    # lattice
    "Omega_bb":  10282.0,   # lattice
    "Omega_ccc": 4796.0,    # lattice
    "Omega_ccb": 7990.0,    # lattice
    "Omega_bbb": 14371.0,   # lattice
    "Lambda":    1115.68,
    "Lambda_c":  2286.46,
    "Lambda_b":  5619.6,
    "Xi_b":      5797.0,
    "Xi_c":      2467.94,
}


HEAVY_TRIPLETS: dict[str, tuple[str, str, str]] = {
    "doubly-heavy_Xi":  ("Xi_cc", "Xi_cb", "Xi_bb"),
    "doubly-heavy_Omega": ("Omega_cc", "Omega_cb", "Omega_bb"),
    "triply-heavy_Omega": ("Omega_ccc", "Omega_ccb", "Omega_bbb"),
    "Xi_charm_chain":   ("Xi_c", "Xi_cc", "Omega_ccc"),
    "Xi_bottom_chain":  ("Xi_b", "Xi_bb", "Omega_bbb"),
    "Lambda_chain":     ("Lambda", "Lambda_c", "Lambda_b"),
}


@dataclass(frozen=True)
class HeavyBaryonFit:
    triplet_label: str
    members: tuple[str, str, str]
    masses_MeV: tuple[float, float, float]
    implied_b: float
    best_metallic_label: str
    best_metallic_value: float
    rel_b_error_pct: float


def heavy_baryon_fit(label: str) -> HeavyBaryonFit:
    """Match a heavy-baryon triplet's implied b to the metallic basis."""
    members = HEAVY_TRIPLETS[label]
    masses = [HEAVY_BARYON_MASSES[m] for m in members]
    b = fad.implied_b(masses)
    cands = mis.generate_candidate_b_expressions()
    name, val = min(cands.items(), key=lambda kv: abs(kv[1] - b))
    return HeavyBaryonFit(
        triplet_label=label,
        members=members,
        masses_MeV=tuple(masses),
        implied_b=b,
        best_metallic_label=name,
        best_metallic_value=val,
        rel_b_error_pct=abs(val - b) / b * 100,
    )


def all_heavy_baryon_fits() -> list[HeavyBaryonFit]:
    """All six heavy-baryon Foot triplet fits."""
    return [heavy_baryon_fit(k) for k in HEAVY_TRIPLETS]


@dataclass(frozen=True)
class HeavyBaryonPrediction:
    triplet_label: str
    inputs: tuple[str, str]
    input_masses_MeV: tuple[float, float]
    target: str
    target_lattice_MeV: float
    target_predicted_MeV: float
    rel_error_pct: float
    b_metallic_label: str
    b_value: float


def predict_xi_bb_from_xi_cc_and_xi_cb() -> HeavyBaryonPrediction:
    """Predict Xi_bb from (Xi_cc, Xi_cb) at b = 1/(golden^2 * plastic).

    Both inputs partially measured (Xi_cc) or lattice (Xi_cb).
    Output is a falsifiable Foot prediction for the unmeasured Xi_bb.
    """
    b = 1.0 / (mis.GOLDEN ** 2 * mis.PLASTIC)
    sol = fmp.predict_third_mass(3621.4, 6943.0, b)
    if sol is None:
        raise RuntimeError("No solution for Xi_bb prediction")
    target = HEAVY_BARYON_MASSES["Xi_bb"]
    return HeavyBaryonPrediction(
        triplet_label="doubly-heavy_Xi",
        inputs=("Xi_cc", "Xi_cb"),
        input_masses_MeV=(3621.4, 6943.0),
        target="Xi_bb",
        target_lattice_MeV=target,
        target_predicted_MeV=float(sol["m_predicted"]),
        rel_error_pct=abs(sol["m_predicted"] - target) / target * 100,
        b_metallic_label="1/(golden^2*plastic)",
        b_value=b,
    )


def predict_omega_bbb_from_xi_b_and_xi_bb() -> HeavyBaryonPrediction:
    """Predict Omega_bbb from (Xi_b, Xi_bb) at b = 1/(golden*silver).

    The (Xi_b, Xi_bb, Omega_bbb) triplet has the tightest metallic fit
    in the entire atlas (0.05%).
    """
    b = 1.0 / (mis.GOLDEN * mis.SILVER)
    sol = fmp.predict_third_mass(5797.0, 10202.0, b)
    if sol is None:
        raise RuntimeError("No solution for Omega_bbb prediction")
    target = HEAVY_BARYON_MASSES["Omega_bbb"]
    return HeavyBaryonPrediction(
        triplet_label="Xi_bottom_chain",
        inputs=("Xi_b", "Xi_bb"),
        input_masses_MeV=(5797.0, 10202.0),
        target="Omega_bbb",
        target_lattice_MeV=target,
        target_predicted_MeV=float(sol["m_predicted"]),
        rel_error_pct=abs(sol["m_predicted"] - target) / target * 100,
        b_metallic_label="1/(golden*silver)",
        b_value=b,
    )


def predict_lambda_b_from_lambda_and_lambda_c() -> HeavyBaryonPrediction:
    """Predict Lambda_b from (Lambda, Lambda_c) at b = 1/(golden*plastic)."""
    b = 1.0 / (mis.GOLDEN * mis.PLASTIC)
    sol = fmp.predict_third_mass(1115.68, 2286.46, b)
    if sol is None:
        raise RuntimeError("No solution for Lambda_b prediction")
    target = HEAVY_BARYON_MASSES["Lambda_b"]
    return HeavyBaryonPrediction(
        triplet_label="Lambda_chain",
        inputs=("Lambda", "Lambda_c"),
        input_masses_MeV=(1115.68, 2286.46),
        target="Lambda_b",
        target_lattice_MeV=target,
        target_predicted_MeV=float(sol["m_predicted"]),
        rel_error_pct=abs(sol["m_predicted"] - target) / target * 100,
        b_metallic_label="1/(golden*plastic)",
        b_value=b,
    )


def all_heavy_baryon_predictions() -> list[HeavyBaryonPrediction]:
    return [
        predict_xi_bb_from_xi_cc_and_xi_cb(),
        predict_omega_bbb_from_xi_b_and_xi_bb(),
        predict_lambda_b_from_lambda_and_lambda_c(),
    ]


__all__ = [
    "HEAVY_BARYON_MASSES", "HEAVY_TRIPLETS",
    "HeavyBaryonFit", "heavy_baryon_fit", "all_heavy_baryon_fits",
    "HeavyBaryonPrediction",
    "predict_xi_bb_from_xi_cc_and_xi_cb",
    "predict_omega_bbb_from_xi_b_and_xi_bb",
    "predict_lambda_b_from_lambda_and_lambda_c",
    "all_heavy_baryon_predictions",
]
