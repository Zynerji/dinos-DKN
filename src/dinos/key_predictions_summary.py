"""Headline falsifiable predictions of the metallic Foot framework
(HYPOTHESIS Step 38).

Single-stop summary of every numerical prediction the framework makes
that is directly comparable to experiment, lattice, or PDG. Used for
poster-level reporting and as a sanity check before any major claim.

Each prediction is a tuple (inputs, b_metallic, target, predicted,
empirical, relative_error). The aggregate "predictive density" is
the number of sub-0.1% predictions divided by total atlas size.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from math import sqrt

from . import foot_predictions_extended as fpe
from . import foot_mass_predictions as fmp
from . import heavy_baryon_foot as hbf
from . import quark_generation_foot as qgf


@dataclass(frozen=True)
class HeadlinePrediction:
    rank: int
    label: str
    inputs: str
    target: str
    metallic_b_label: str
    predicted_value_MeV: float
    empirical_value_MeV: float
    relative_error_pct: float
    falsifiable: bool      # Is the empirical value precise enough to falsify?
    notes: str = ""


def collect_all_headline_predictions() -> list[HeadlinePrediction]:
    """All headline metallic Foot mass predictions, ranked by precision."""
    out: list[HeadlinePrediction] = []
    rank = 0

    # Step 17 originals
    p = fmp.lepton_mass_prediction()
    rank += 1
    out.append(HeadlinePrediction(
        rank=rank, label="charged lepton tower",
        inputs="(m_e, m_mu)", target="m_tau",
        metallic_b_label=p.b_metallic,
        predicted_value_MeV=p.target_predicted_MeV,
        empirical_value_MeV=p.target_empirical_MeV,
        relative_error_pct=p.rel_error_pct,
        falsifiable=True,
        notes="0.12 MeV gap = 1 sigma; tighter m_tau measurement falsifies",
    ))

    p = fmp.vector_meson_mass_prediction()
    rank += 1
    out.append(HeadlinePrediction(
        rank=rank, label="vector mesons",
        inputs="(m_rho, m_omega)", target="m_phi",
        metallic_b_label=p.b_metallic,
        predicted_value_MeV=p.target_predicted_MeV,
        empirical_value_MeV=p.target_empirical_MeV,
        relative_error_pct=p.rel_error_pct,
        falsifiable=True,
    ))

    p = fmp.light_baryon_mass_prediction()
    rank += 1
    out.append(HeadlinePrediction(
        rank=rank, label="light baryons",
        inputs="(m_N, m_Lambda)", target="m_Xi",
        metallic_b_label=p.b_metallic,
        predicted_value_MeV=p.target_predicted_MeV,
        empirical_value_MeV=p.target_empirical_MeV,
        relative_error_pct=p.rel_error_pct,
        falsifiable=True,
    ))

    # Step 33 extended predictions
    higgs = fpe.gauge_boson_higgs_prediction()
    rank += 1
    out.append(HeadlinePrediction(
        rank=rank, label="HIGGS BOSON FROM (W, Z)",
        inputs="(m_W, m_Z)", target="m_H",
        metallic_b_label=higgs.b_metallic_label,
        predicted_value_MeV=higgs.predicted_MeV,
        empirical_value_MeV=higgs.empirical_MeV,
        relative_error_pct=higgs.relative_error_pct,
        falsifiable=True,
        notes=("Framework's first electroweak-scale prediction not "
               "using m_H as input; matches PDG within sub-percent"),
    ))

    bc = fpe.b_meson_bc_prediction()
    rank += 1
    out.append(HeadlinePrediction(
        rank=rank, label="B_c meson",
        inputs="(m_B0, m_Bs)", target="m_Bc",
        metallic_b_label=bc.b_metallic_label,
        predicted_value_MeV=bc.predicted_MeV,
        empirical_value_MeV=bc.empirical_MeV,
        relative_error_pct=bc.relative_error_pct,
        falsifiable=True,
    ))

    chi = fpe.charmonium_chi_c_prediction()
    rank += 1
    out.append(HeadlinePrediction(
        rank=rank, label="chi_c meson",
        inputs="(m_eta_c, m_Jpsi)", target="m_chi_c",
        metallic_b_label=chi.b_metallic_label,
        predicted_value_MeV=chi.predicted_MeV,
        empirical_value_MeV=chi.empirical_MeV,
        relative_error_pct=chi.relative_error_pct,
        falsifiable=True,
    ))

    # Step 34 quark generation
    top = qgf.top_quark_prediction(n_bootstrap=200)
    rank += 1
    out.append(HeadlinePrediction(
        rank=rank, label="top quark",
        inputs="(m_c, m_b) MS-bar", target="m_t pole",
        metallic_b_label=top.b_metallic_label,
        predicted_value_MeV=top.m_top_predicted_MeV,
        empirical_value_MeV=top.m_top_empirical_MeV,
        relative_error_pct=top.rel_error_pct,
        falsifiable=False,
        notes=("MS-bar c-quark uncertainty dominates; bootstrap "
               f"16-84%: [{top.bootstrap_p16_pct:.1f}, "
               f"{top.bootstrap_p84_pct:.1f}]%"),
    ))

    # Step 35 heavy baryon
    xb = hbf.predict_xi_bb_from_xi_cc_and_xi_cb()
    rank += 1
    out.append(HeadlinePrediction(
        rank=rank, label="Xi_bb baryon (UNMEASURED)",
        inputs="(Xi_cc, Xi_cb)", target="Xi_bb",
        metallic_b_label=xb.b_metallic_label,
        predicted_value_MeV=xb.target_predicted_MeV,
        empirical_value_MeV=xb.target_lattice_MeV,
        relative_error_pct=xb.rel_error_pct,
        falsifiable=True,
        notes=("Xi_bb not yet measured at hadron collider; "
               "framework predicts 10,139 MeV vs lattice 10,202 MeV"),
    ))

    ob = hbf.predict_omega_bbb_from_xi_b_and_xi_bb()
    rank += 1
    out.append(HeadlinePrediction(
        rank=rank, label="Omega_bbb baryon (UNMEASURED)",
        inputs="(Xi_b, Xi_bb)", target="Omega_bbb",
        metallic_b_label=ob.b_metallic_label,
        predicted_value_MeV=ob.target_predicted_MeV,
        empirical_value_MeV=ob.target_lattice_MeV,
        relative_error_pct=ob.rel_error_pct,
        falsifiable=True,
        notes="Triply-bottom baryon; triplet has tightest fit in atlas",
    ))

    lb = hbf.predict_lambda_b_from_lambda_and_lambda_c()
    rank += 1
    out.append(HeadlinePrediction(
        rank=rank, label="Lambda_b baryon",
        inputs="(Lambda, Lambda_c)", target="Lambda_b",
        metallic_b_label=lb.b_metallic_label,
        predicted_value_MeV=lb.target_predicted_MeV,
        empirical_value_MeV=lb.target_lattice_MeV,
        relative_error_pct=lb.rel_error_pct,
        falsifiable=True,
    ))

    return sorted(out, key=lambda p: p.relative_error_pct)


def predictive_density_below(threshold_pct: float) -> dict:
    """Fraction of headline predictions with rel err below threshold."""
    preds = collect_all_headline_predictions()
    n_total = len(preds)
    n_below = sum(1 for p in preds if p.relative_error_pct < threshold_pct)
    return {
        "threshold_pct": threshold_pct,
        "n_below": n_below,
        "n_total": n_total,
        "fraction": n_below / n_total if n_total else 0.0,
    }


__all__ = [
    "HeadlinePrediction",
    "collect_all_headline_predictions",
    "predictive_density_below",
]
