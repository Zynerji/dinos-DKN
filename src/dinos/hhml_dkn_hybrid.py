"""HHmL multiverse coherence-pruning hybrid (HYPOTHESIS Step 46a).

Honest scope
------------
This module DOES:
  - Generate an ensemble of N "branch" wavefunctions on a 1D lattice
    via random perturbations of a base state.
  - Compute the mean ("hologram") and per-branch coherence to mean.
  - Prune low-coherence branches via a threshold; report the resulting
    "dark fraction" (energy in pruned branches / total energy).
  - Verify entropy-conservation (sum of energies before/after pruning).

This module DOES NOT:
  - Predict that the dark fraction equals 0.27. The threshold is a
    user input; ANY dark fraction in [0, 1] can be reached by sweeping
    the threshold.
  - Connect to gravitational backreaction or axion DM in any
    quantitative way.

Verdict on Grok's "0.270 +/- 0.018 dark fraction" hybrid claim: the
result is reproducible only because the threshold was tuned to give
0.27. With any other threshold the framework gives any other fraction.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class HHmLPruningParams:
    n_branches: int = 64
    n_nodes: int = 256
    perturbation_alpha: float = 0.32
    decoherence: float = 0.12
    seed: int = 42


@dataclass(frozen=True)
class HHmLPruningReport:
    threshold: float
    n_kept: int
    n_pruned: int
    dark_fraction: float
    entropy_before: float
    entropy_after_kept: float
    entropy_after_pruned: float
    entropy_conservation_ratio: float    # (kept + pruned) / before
    notes: str


def generate_branches(params: HHmLPruningParams) -> np.ndarray:
    """Generate (n_branches, n_nodes) complex wavefunctions."""
    rng = np.random.default_rng(params.seed)
    base = np.exp(1j * np.linspace(0, 2 * np.pi, params.n_nodes,
                                    endpoint=False))
    branches = np.zeros((params.n_branches, params.n_nodes), dtype=complex)
    for i in range(params.n_branches):
        phase_kicks = rng.normal(0, params.perturbation_alpha * 2 * np.pi,
                                  params.n_nodes)
        amp_damp = 1.0 - params.decoherence * params.perturbation_alpha
        thermal = rng.normal(0, np.sqrt(params.perturbation_alpha),
                              params.n_nodes) + 1j * rng.normal(
            0, np.sqrt(params.perturbation_alpha), params.n_nodes)
        branches[i] = amp_damp * base * np.exp(1j * phase_kicks) + 0.1 * thermal
    return branches


def coherence(psi: np.ndarray, mean: np.ndarray) -> float:
    """Coherence metric in (-inf, 1]."""
    diff_norm_sq = float(np.linalg.norm(psi - mean) ** 2)
    sum_norm_sq = float(np.linalg.norm(psi) ** 2 + np.linalg.norm(mean) ** 2)
    return 1.0 - diff_norm_sq / sum_norm_sq


def prune(branches: np.ndarray, threshold: float) -> HHmLPruningReport:
    """Prune branches with coherence below threshold; return report."""
    mean = branches.mean(axis=0)
    cohs = np.array([coherence(b, mean) for b in branches])
    pruned_mask = cohs < threshold
    energies = np.array([float(np.linalg.norm(b) ** 2) for b in branches])
    E_total = float(energies.sum())
    E_pruned = float(energies[pruned_mask].sum())
    E_kept = float(energies[~pruned_mask].sum())
    return HHmLPruningReport(
        threshold=float(threshold),
        n_kept=int((~pruned_mask).sum()),
        n_pruned=int(pruned_mask.sum()),
        dark_fraction=float(E_pruned / max(E_total, 1e-30)),
        entropy_before=float(E_total),
        entropy_after_kept=float(E_kept),
        entropy_after_pruned=float(E_pruned),
        entropy_conservation_ratio=float((E_kept + E_pruned) / max(E_total, 1e-30)),
        notes=("Pruning threshold is an INPUT. Any dark_fraction in [0, 1] "
               "can be achieved by sweeping threshold. Grok's claim that "
               "0.27 emerges naturally is achieved by choosing a threshold "
               "that gives 0.27."),
    )


def threshold_for_target_dark_fraction(branches: np.ndarray,
                                         target: float = 0.27,
                                         tol: float = 0.01,
                                         max_iter: int = 60) -> dict:
    """Bisection on threshold to hit target dark_fraction."""
    lo, hi = -1.0, 1.0
    for it in range(max_iter):
        mid = 0.5 * (lo + hi)
        r = prune(branches, mid)
        if abs(r.dark_fraction - target) < tol:
            return {
                "threshold": mid, "achieved_dark_fraction": r.dark_fraction,
                "iters": it + 1,
                "note": f"Reached target {target} +/- {tol} after {it+1} bisection steps.",
            }
        if r.dark_fraction > target:
            hi = mid
        else:
            lo = mid
    return {
        "threshold": mid, "achieved_dark_fraction": r.dark_fraction,
        "iters": max_iter, "note": "Did not converge tightly.",
    }


__all__ = [
    "HHmLPruningParams", "HHmLPruningReport",
    "generate_branches", "coherence", "prune",
    "threshold_for_target_dark_fraction",
]
