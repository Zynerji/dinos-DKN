"""Varying-c pruning experiment (HYPOTHESIS Step 46c).

Honest scope
------------
This module DOES:
  - Allow each branch in the HHmL ensemble to have its own propagation
    speed c_i drawn from a distribution.
  - Compute the per-branch coherence to mean as a function of c_i,
    and prune accordingly.
  - Report whether c-deviant branches are preferentially pruned.

This module DOES NOT:
  - Demonstrate that c is "selected" by the lattice. The pruning
    pressure on c_i depends on the choice of branch dynamics; for the
    simple eigenmode shifts here, c_i deviation does increase
    decoherence — but this is a tautology of the pruning metric,
    not a derivation of c.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from . import hhml_dkn_hybrid as hh


@dataclass(frozen=True)
class VaryingCReport:
    c_mean: float
    c_std: float
    threshold: float
    n_kept: int
    n_pruned: int
    kept_c_mean: float
    pruned_c_mean: float
    is_c_pressure_observed: bool
    notes: str


def evolve_with_variable_c(n_branches: int = 64,
                             n_nodes: int = 256,
                             c_base: float = 1.0,
                             c_std: float = 0.10,
                             threshold: float = 0.4,
                             seed: int = 7) -> VaryingCReport:
    """Each branch evolves under its own c; we then prune by coherence."""
    rng = np.random.default_rng(seed)
    cs = np.clip(rng.normal(c_base, c_std, n_branches), 0.1, 5.0)

    # Build branches whose phase rotates at speed c_i (a simple proxy)
    nodes = np.arange(n_nodes)
    branches = np.array([np.exp(1j * c_i * nodes / n_nodes * 2 * np.pi)
                         for c_i in cs])

    rep = hh.prune(branches, threshold=threshold)

    mean = branches.mean(axis=0)
    cohs = np.array([hh.coherence(b, mean) for b in branches])
    pruned_mask = cohs < threshold
    kept_c = float(cs[~pruned_mask].mean()) if (~pruned_mask).any() else float("nan")
    pruned_c = float(cs[pruned_mask].mean()) if pruned_mask.any() else float("nan")
    pressure = (
        not np.isnan(kept_c) and not np.isnan(pruned_c)
        and abs(kept_c - c_base) < abs(pruned_c - c_base)
    )

    return VaryingCReport(
        c_mean=float(cs.mean()),
        c_std=float(cs.std()),
        threshold=float(threshold),
        n_kept=int((~pruned_mask).sum()),
        n_pruned=int(pruned_mask.sum()),
        kept_c_mean=kept_c,
        pruned_c_mean=pruned_c,
        is_c_pressure_observed=bool(pressure),
        notes=("Per-branch c is sampled from N(c_base, c_std). The "
               "result that c-deviant branches prune more is a "
               "tautology of the chosen pruning metric (large |c - c_base| "
               "shifts the per-node phase, reducing coherence). It does "
               "NOT derive a physical mechanism for c-selection."),
    )


__all__ = ["VaryingCReport", "evolve_with_variable_c"]
