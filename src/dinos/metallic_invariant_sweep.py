"""Comprehensive metallic-invariant sweep (HYPOTHESIS Step 15).

Tests the hypothesis: every observed fermion/boson 3-state family has
a Foot coupling b expressible as a SIMPLE COMBINATION OF METALLIC
RATIOS (golden, silver, bronze, copper, nickel, plastic, supergolden).

Rationale
---------
Step 14 showed that only the lepton family fits b = sqrt(2) =
silver - 1. The rejected fragments (mesons, baryons, gauge bosons)
each have their own implied b. The user's hypothesis: each b is itself
a metallic invariant.

Metallic invariance means: b is one of a discrete set of values built
from {golden, silver, bronze, copper, nickel, plastic, supergolden}
via simple operations (reciprocal, product, M-1, etc.). This makes
b an *anti-resonant* quantity — irrational, transcendental over Q,
and immune to harmonic locking.

Approach
--------
1. Generate ~100 candidate metallic-ratio expressions.
2. For each empirical fragment's implied b, find the best metallic
   match (within 1% relative tolerance).
3. Report: does every fragment have a clean metallic match?

Honest scope statement
----------------------
- This module tests EMPIRICAL fits to a metallic-invariant basis.
- A successful fit (within 1%) is suggestive but not derivative —
  the framework currently lacks a first-principles reason for
  WHY each family should pick a specific metallic.
- If many fragments fit, this is a *strong* numerical pattern that
  warrants investigation as a possible deep regularity.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import sqrt

import numpy as np

from . import generations_extended


# ---- Metallic ratios ----
GOLDEN: float = (1 + sqrt(5)) / 2          # M_1
SILVER: float = 1 + sqrt(2)                # M_2
BRONZE: float = (3 + sqrt(13)) / 2         # M_3
COPPER: float = 2 + sqrt(5)                # M_4
NICKEL: float = (5 + sqrt(29)) / 2         # M_5
PLASTIC: float = 1.32471795724474602596    # x^3 = x + 1
SUPERGOLDEN: float = 1.46557123187676802665  # x^3 = x^2 + 1


METALLIC_RATIOS: dict[str, float] = {
    "golden": GOLDEN, "silver": SILVER, "bronze": BRONZE,
    "copper": COPPER, "nickel": NICKEL,
    "plastic": PLASTIC, "supergolden": SUPERGOLDEN,
}


# ---- Generate candidate b expressions ----

def generate_candidate_b_expressions() -> dict[str, float]:
    """Generate a comprehensive basis of metallic-derived b values."""
    cands: dict[str, float] = {}

    # Direct metallic ratios
    for name, M in METALLIC_RATIOS.items():
        cands[name] = M
        cands[f"1/{name}"] = 1.0 / M
        cands[f"{name}-1"] = M - 1
        cands[f"1/({name}-1)"] = 1.0 / (M - 1)
        cands[f"sqrt({name})"] = sqrt(M)
        cands[f"sqrt({name}-1)"] = sqrt(M - 1)
        cands[f"1/{name}^2"] = 1.0 / (M * M)
        cands[f"1/{name}^3"] = 1.0 / (M ** 3)
        cands[f"1/(2*{name})"] = 1.0 / (2 * M)
        cands[f"1/(3*{name})"] = 1.0 / (3 * M)
        cands[f"2-{name}"] = abs(2 - M)

    # Pairwise products of reciprocals
    keys = list(METALLIC_RATIOS.keys())
    for i, n1 in enumerate(keys):
        for n2 in keys[i:]:
            M1, M2 = METALLIC_RATIOS[n1], METALLIC_RATIOS[n2]
            cands[f"1/({n1}*{n2})"] = 1.0 / (M1 * M2)
            cands[f"1/sqrt({n1}*{n2})"] = 1.0 / sqrt(M1 * M2)
            if i != keys.index(n2):
                cands[f"{n1}/{n2}"] = M1 / M2

    # Triple products
    for n1 in keys:
        for n2 in keys:
            for n3 in keys:
                if n1 <= n2 <= n3:
                    M1, M2, M3 = (METALLIC_RATIOS[n1], METALLIC_RATIOS[n2],
                                   METALLIC_RATIOS[n3])
                    cands[f"1/({n1}*{n2}*{n3})"] = 1.0 / (M1 * M2 * M3)

    # Special combinations involving silver - 1 = sqrt(2) (the lepton reference)
    sqrt2 = sqrt(2.0)
    cands["sqrt(2)"] = sqrt2
    cands["sqrt(2)/2"] = sqrt2 / 2
    cands["sqrt(2)/3"] = sqrt2 / 3
    cands["1/sqrt(2)"] = 1.0 / sqrt2

    return cands


# ---- Empirical fragments to fit ----

EMPIRICAL_FRAGMENTS: dict[str, dict] = {
    "leptons (e,mu,tau)": {
        "masses": [0.51099895, 105.6583755, 1776.86],
        "family": "leptons",
    },
    "ps_mesons (pi,K,eta)": {
        "masses": [134.977, 497.611, 547.862],
        "family": "pseudoscalar_mesons",
    },
    "ps_mesons (pi,K,eta')": {
        "masses": [134.977, 497.611, 957.78],
        "family": "pseudoscalar_mesons",
    },
    "ps_mesons (pi,eta,eta')": {
        "masses": [134.977, 547.862, 957.78],
        "family": "pseudoscalar_mesons",
    },
    "ps_mesons (K,eta,eta')": {
        "masses": [497.611, 547.862, 957.78],
        "family": "pseudoscalar_mesons",
    },
    "v_mesons (rho,omega,phi)": {
        "masses": [775.26, 782.65, 1019.46],
        "family": "vector_mesons",
    },
    "baryons (N,Lambda,Xi)": {
        "masses": [938.92, 1115.68, 1318.3],
        "family": "light_baryons",
    },
    "baryons (Lambda,Sigma,Xi)": {
        "masses": [1115.68, 1193.1, 1318.3],
        "family": "light_baryons",
    },
    "decuplet (Delta,Sigma*,Xi*)": {
        "masses": [1232.0, 1383.7, 1531.8],
        "family": "decuplet_baryons",
    },
    "gauge (W,Z,H)": {
        "masses": [80379.0, 91188.0, 125100.0],
        "family": "gauge_bosons",
    },
}


def implied_b_from_masses(masses: list[float]) -> float:
    """b at all-positive branch from observed Q."""
    Q = generations_extended.koide_q(masses)
    if Q <= 0 or Q >= 3:
        raise ValueError(f"Q = {Q} outside (0, 3)")
    return float(sqrt(6.0 / Q - 2.0))


@dataclass(frozen=True)
class MetallicMatch:
    expression: str
    value: float
    target_b: float
    relative_error_pct: float


def find_best_metallic_match(target_b: float,
                             candidates: dict[str, float] | None = None,
                             ) -> MetallicMatch:
    """Find the candidate expression closest to target_b."""
    if candidates is None:
        candidates = generate_candidate_b_expressions()
    best: tuple[str, float, float] | None = None
    for name, val in candidates.items():
        if val <= 0 or val > 5:   # skip non-physical
            continue
        diff = abs(val - target_b)
        rel = diff / target_b * 100 if target_b > 0 else float("inf")
        if best is None or rel < best[2]:
            best = (name, val, rel)
    return MetallicMatch(
        expression=best[0],
        value=best[1],
        target_b=target_b,
        relative_error_pct=best[2],
    )


@dataclass(frozen=True)
class FragmentMetallicReport:
    name: str
    family: str
    koide_q: float
    implied_b: float
    best_match: MetallicMatch
    fits_within_1_percent: bool


def scan_all_fragments() -> list[FragmentMetallicReport]:
    """Find best metallic match for every fragment."""
    candidates = generate_candidate_b_expressions()
    out: list[FragmentMetallicReport] = []
    for name, info in EMPIRICAL_FRAGMENTS.items():
        masses = info["masses"]
        try:
            b = implied_b_from_masses(masses)
        except ValueError:
            continue
        match = find_best_metallic_match(b, candidates)
        out.append(FragmentMetallicReport(
            name=name,
            family=info["family"],
            koide_q=generations_extended.koide_q(masses),
            implied_b=b,
            best_match=match,
            fits_within_1_percent=(match.relative_error_pct < 1.0),
        ))
    return out


# ---- Aggregate report ----

@dataclass(frozen=True)
class MetallicSweepReport:
    fragment_reports: list[FragmentMetallicReport]
    n_fits: int
    n_total: int
    fit_fraction: float
    notes: str


def generate_metallic_sweep_report() -> MetallicSweepReport:
    reports = scan_all_fragments()
    n_fits = sum(1 for r in reports if r.fits_within_1_percent)
    n_total = len(reports)
    fits = [r.name for r in reports if r.fits_within_1_percent]
    notes = (
        f"Scanned {n_total} 3-state fragments against ~"
        f"{len(generate_candidate_b_expressions())} metallic-ratio "
        f"expressions. {n_fits}/{n_total} match within 1% relative error. "
        f"Within-1% fits: {fits}. "
        f"Strong metallic invariance suggests a deep numerical regularity "
        f"linking each family's coupling b to a specific metallic combination."
    )
    return MetallicSweepReport(
        fragment_reports=reports,
        n_fits=n_fits,
        n_total=n_total,
        fit_fraction=n_fits / n_total if n_total > 0 else 0.0,
        notes=notes,
    )


__all__ = [
    "GOLDEN", "SILVER", "BRONZE", "COPPER", "NICKEL",
    "PLASTIC", "SUPERGOLDEN", "METALLIC_RATIOS",
    "generate_candidate_b_expressions",
    "EMPIRICAL_FRAGMENTS",
    "implied_b_from_masses",
    "MetallicMatch", "find_best_metallic_match",
    "FragmentMetallicReport", "scan_all_fragments",
    "MetallicSweepReport", "generate_metallic_sweep_report",
]
