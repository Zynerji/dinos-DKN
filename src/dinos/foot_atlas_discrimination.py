"""Discrimination test for the full 19-resonance atlas (HYPOTHESIS Step 31).

Re-runs the random-baseline discrimination from Step 15, but now with
the FULL set of 19 confirmed atlas fragments rather than the original
10. Establishes how strong the metallic structure is across the entire
atlas.

Method
------
For each of 19 fragment triplets, compute the implied b at all-positive
branch from Q. Find the closest candidate b in:
  (a) METALLIC basis (242 candidates from Step 15)
  (b) RANDOM basis (242 random log-uniform irrationals in [0.001, 5])

Repeat random basis 30 times for statistical reliability. Count how
many fragments fit at each tolerance.

If metallic significantly beats random, the metallic structure is real.
If they tie, it's combinatorial.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import sqrt

import numpy as np

from . import metallic_invariant_sweep as mis


# All 19 confirmed atlas fragment masses (PDG)
ATLAS_19_MASSES: dict[str, list[float]] = {
    "leptons":              [0.51099895, 105.6583755, 1776.86],
    "vector_mesons":        [775.26, 782.65, 1019.46],
    "light_baryons":        [938.92, 1115.68, 1318.3],
    "charmonium_eta_c":     [2983.9, 3096.90, 3414.71],
    "charmonium_1S2S1P":    [3096.90, 3686.10, 3525.38],
    "D_star_J_psi":         [2010.26, 2112.20, 3096.90],
    "Jpsi_Upsilon":         [3096.90, 9460.30, 10023.26],
    "B_mesons":             [5279.66, 5366.93, 6274.5],
    "tensor_mesons":        [1318.2, 1427.3, 1525.0],
    "axial_vector":         [1229.5, 1166, 1230],
    "scalar_mesons":        [475, 990, 980],
    "eta_h1_eta_c":         [547.86, 1166, 2983.9],
    "decuplet_baryons":     [1232.0, 1383.7, 1672.45],
    "K_K_star_B_star":      [497.611, 891.66, 5324.71],
    "gauge_bosons":         [80379.0, 91188.0, 125100.0],
    "K_D_B":                [497.611, 1869.66, 5279.66],
    "rho_excitations":      [775.26, 1465, 1720],
    "rho_b1_omega":         [775.26, 1229.5, 782.65],
    "Xi_c_Omega_c":         [2467.94, 2578.4, 2695.2],
}


def implied_b(masses: list[float]) -> float:
    """Implied b from observed Q at all-positive branch."""
    sm = sum(np.sqrt(m) for m in masses)
    Q = sm * sm / sum(masses)
    if not (0 < Q < 3):
        raise ValueError(f"Q = {Q} outside (0, 3)")
    return sqrt(6.0 / Q - 2.0)


def count_fits(candidates_values: list[float], targets: list[float],
               tolerance_pct: float) -> int:
    """How many targets have a candidate within tolerance_pct%?"""
    n = 0
    for t in targets:
        best_rel = min(abs(c - t) / t * 100 for c in candidates_values)
        if best_rel < tolerance_pct:
            n += 1
    return n


@dataclass(frozen=True)
class DiscriminationResult:
    tolerance_pct: float
    metallic_fits: int
    random_mean_fits: float
    random_std_fits: float
    random_max_fits: int
    n_total: int
    significance_ratio: float


def run_full_discrimination(n_random_seeds: int = 30) -> list[DiscriminationResult]:
    """Run discrimination at multiple tolerances."""
    metallic_cands = list(mis.generate_candidate_b_expressions().values())
    metallic_cands = [c for c in metallic_cands if c > 0]
    targets = [implied_b(m) for m in ATLAS_19_MASSES.values()]
    n_total = len(targets)
    n_cands = len(metallic_cands)

    results = []
    for tol in [5.0, 2.0, 1.0, 0.5, 0.3, 0.1, 0.05, 0.03, 0.01]:
        m_fits = count_fits(metallic_cands, targets, tol)
        r_fits = []
        for seed in range(n_random_seeds):
            rng = np.random.default_rng(seed * 7919)
            rand_cands = np.exp(rng.uniform(np.log(0.001), np.log(5),
                                             n_cands))
            r_fits.append(count_fits(list(rand_cands), targets, tol))
        r_arr = np.array(r_fits)
        r_mean = float(r_arr.mean())
        r_std = float(r_arr.std())
        r_max = int(r_arr.max())
        sig = m_fits / r_mean if r_mean > 0 else float("inf")
        results.append(DiscriminationResult(
            tolerance_pct=tol,
            metallic_fits=m_fits,
            random_mean_fits=r_mean,
            random_std_fits=r_std,
            random_max_fits=r_max,
            n_total=n_total,
            significance_ratio=sig,
        ))
    return results


__all__ = [
    "ATLAS_19_MASSES", "implied_b", "count_fits",
    "DiscriminationResult", "run_full_discrimination",
]
