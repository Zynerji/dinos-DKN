"""Statistical robustness of metallic Foot resonances (HYPOTHESIS Step 22).

For each confirmed metallic resonance, propagate empirical mass
uncertainties to b uncertainty and check whether the metallic match
remains within experimental noise.

Method
------
- Bootstrap with Gaussian mass perturbations at PDG-quoted sigma.
- Compute distribution of implied b values.
- Check whether the metallic candidate value falls within the bootstrap
  CI.

This separates GENUINELY tight metallic matches (where b uncertainty
is much smaller than the metallic-candidate gap) from CHANCE matches
(where b uncertainty straddles many candidates).
"""

from __future__ import annotations

from dataclasses import dataclass
from math import sqrt

import numpy as np

from . import metallic_invariant_sweep as mis


# PDG mass uncertainties (MeV unless noted)
MASS_UNCERTAINTIES = {
    "e":      0.0,           # exact
    "mu":     0.000003,
    "tau":    0.12,
    "rho":    0.25,
    "omega":  0.13,
    "phi":    0.020,
    "N":      0.5,           # avg of proton/neutron
    "Lambda": 0.014,
    "Xi":     0.5,
    "eta_c":  0.5,
    "J/psi":  0.011,
    "chi_c":  0.05,
    "B_0":    0.12,
    "B_s":    0.10,
    "B_c":    0.4,
    # Defaults if not listed
}


def implied_b_with_bootstrap(masses: list[float],
                              uncertainties: list[float],
                              n_bootstrap: int = 1000,
                              seed: int = 42) -> np.ndarray:
    """Bootstrap b distribution from Gaussian mass perturbations."""
    rng = np.random.default_rng(seed)
    samples = []
    for _ in range(n_bootstrap):
        perturbed = [m + sigma * rng.standard_normal()
                     for m, sigma in zip(masses, uncertainties)]
        Q = sum(np.sqrt(max(m, 1e-10)) for m in perturbed) ** 2 / sum(perturbed)
        if 0 < Q < 3:
            b = sqrt(6.0 / Q - 2.0)
            samples.append(b)
    return np.array(samples)


@dataclass(frozen=True)
class RobustnessReport:
    family: str
    metallic_b: float
    metallic_label: str
    bootstrap_mean: float
    bootstrap_std: float
    bootstrap_ci_95: tuple[float, float]
    metallic_within_ci: bool
    n_sigma_displacement: float


def assess_robustness(family: str, masses: list[float],
                       uncertainties: list[float],
                       metallic_b: float,
                       metallic_label: str) -> RobustnessReport:
    """Assess whether the metallic match survives empirical uncertainty."""
    samples = implied_b_with_bootstrap(masses, uncertainties)
    mean = float(samples.mean())
    std = float(samples.std())
    ci_low = float(np.percentile(samples, 2.5))
    ci_high = float(np.percentile(samples, 97.5))
    n_sigma = abs(metallic_b - mean) / std if std > 0 else 0.0
    return RobustnessReport(
        family=family,
        metallic_b=metallic_b,
        metallic_label=metallic_label,
        bootstrap_mean=mean,
        bootstrap_std=std,
        bootstrap_ci_95=(ci_low, ci_high),
        metallic_within_ci=(ci_low <= metallic_b <= ci_high),
        n_sigma_displacement=n_sigma,
    )


def all_robustness_reports() -> list[RobustnessReport]:
    """Robustness for the four cleanest confirmed resonances."""
    out: list[RobustnessReport] = []
    out.append(assess_robustness(
        "charged_leptons",
        [0.51099895, 105.6583755, 1776.86],
        [0.0, 0.000003, 0.12],
        sqrt(2.0), "silver - 1",
    ))
    out.append(assess_robustness(
        "vector_mesons",
        [775.26, 782.65, 1019.46],
        [0.25, 0.13, 0.020],
        1.0 / (mis.BRONZE ** 2), "1/bronze^2",
    ))
    out.append(assess_robustness(
        "light_baryons",
        [938.92, 1115.68, 1318.3],
        [0.5, 0.014, 0.5],
        1.0 / (mis.SILVER * mis.COPPER), "1/(silver*copper)",
    ))
    out.append(assess_robustness(
        "charmonium",
        [2983.9, 3096.90, 3414.71],
        [0.5, 0.011, 0.05],
        1.0 / (mis.COPPER * mis.SILVER ** 2), "1/(copper*silver^2)",
    ))
    out.append(assess_robustness(
        "B_mesons",
        [5279.66, 5366.93, 6274.5],
        [0.12, 0.10, 0.4],
        1.0 / (mis.COPPER ** 2), "1/copper^2",
    ))
    return out


__all__ = [
    "MASS_UNCERTAINTIES", "implied_b_with_bootstrap",
    "RobustnessReport", "assess_robustness", "all_robustness_reports",
]
