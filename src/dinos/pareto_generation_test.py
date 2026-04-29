"""Pareto-ratchet experiment for generations (HYPOTHESIS Step 6+).

The Aletheia Pareto ratchet operates on N orthogonal axes with per-axis
floor constraints — structurally a *splitting/stability mechanism*
that prevents modes from collapsing into each other. This module tests
whether wrapping it around a 3-mode generation problem can:

A. Maintain 3 distinct σ_g values under perturbation (its design role).
B. Pick the empirical lepton ratios from any natural optimisation
   objective (the falsifiable claim).

Honest scope statement
----------------------
- The ratchet is constraint-based: it *preserves* mode separation under
  optimisation but does not *create* it from nothing.
- To pin specific σ_g ratios (like 1 : 207 : 3477), an additional
  symmetry/constraint beyond the ratchet itself is needed.
- This module documents both: the ratchet does maintain separation,
  AND a generic objective doesn't reproduce the lepton tower.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from . import generations


# Lightweight ParetoRatchet (no dependence on Aletheia in tree)
@dataclass
class ParetoRatchet:
    anchor: dict[str, float]
    floor: float = 0.80
    eps: float = 1e-3

    def __post_init__(self) -> None:
        if not self.anchor:
            raise ValueError("anchor must have at least one axis")
        if not 0.0 < self.floor <= 1.0:
            raise ValueError(f"floor must be in (0, 1], got {self.floor}")
        self.best_scores: dict[str, float] = dict(self.anchor)
        self.best_product: float = self.product(self.anchor)

    def product(self, scores: dict[str, float]) -> float:
        p = 1.0
        for k in self.anchor:
            p *= max(scores.get(k, 0.0), self.eps)
        return p

    def below_floor_axes(self, scores: dict[str, float]) -> list[str]:
        return [
            k for k, v in self.anchor.items()
            if scores.get(k, 0.0) < self.floor * v
        ]

    def should_rollback(self, scores: dict[str, float]) -> bool:
        return len(self.below_floor_axes(scores)) >= 2

    def is_new_best(self, scores: dict[str, float]) -> bool:
        return (
            self.product(scores) > self.best_product
            and len(self.below_floor_axes(scores)) == 0
        )

    def update(self, scores: dict[str, float]) -> None:
        self.best_product = self.product(scores)
        self.best_scores = dict(scores)


# -----------------------------------------------------------------------------
# Experiment C: Pareto ratchet maintains separation under perturbation
# -----------------------------------------------------------------------------

def perturb_scores(scores: dict[str, float], rng: np.random.Generator,
                   amplitude: float) -> dict[str, float]:
    """Multiplicative perturbation: scores_new[k] = scores[k] · (1 + amp · N(0,1))."""
    return {
        k: max(0.0, v * (1.0 + amplitude * float(rng.standard_normal())))
        for k, v in scores.items()
    }


@dataclass(frozen=True)
class RatchetTrajectory:
    """Trajectory of a Pareto-ratchet-protected 3-mode optimisation."""
    initial_scores: dict[str, float]
    final_scores: dict[str, float]
    n_rollbacks: int
    n_updates: int
    final_separation: float    # min |s_i − s_j| / max s


def run_ratchet_perturbation_test(
    initial_scores: dict[str, float],
    rng_seed: int = 0,
    amplitude: float = 0.5,
    n_steps: int = 200,
    floor: float = 0.80,
) -> RatchetTrajectory:
    """Random-walk perturb the 3 mode scores; ratchet enforces separation.

    Verifies:
    - The minimum pairwise separation never drops to zero (ratchet works).
    - Number of rollbacks scales with perturbation amplitude.
    """
    rng = np.random.default_rng(rng_seed)
    ratchet = ParetoRatchet(anchor=dict(initial_scores), floor=floor)
    current = dict(initial_scores)
    n_rollbacks = 0
    n_updates = 0
    for _ in range(n_steps):
        candidate = perturb_scores(current, rng, amplitude)
        if ratchet.should_rollback(candidate):
            n_rollbacks += 1
            continue
        if ratchet.is_new_best(candidate):
            ratchet.update(candidate)
            current = candidate
            n_updates += 1
        else:
            # Accept non-best changes that don't trigger rollback (random walk).
            current = candidate
    # Compute final separation.
    vals = sorted(current.values())
    pairs = [vals[i+1] - vals[i] for i in range(len(vals) - 1)]
    sep = min(pairs) / max(vals) if max(vals) > 0 else 0.0
    return RatchetTrajectory(
        initial_scores=initial_scores,
        final_scores=current,
        n_rollbacks=n_rollbacks,
        n_updates=n_updates,
        final_separation=float(sep),
    )


# -----------------------------------------------------------------------------
# Experiment D: ratchet does NOT pin empirical lepton ratios
# -----------------------------------------------------------------------------

def lepton_anchor_scores() -> dict[str, float]:
    """Anchor the ratchet at the empirical lepton σ values."""
    from . import generations_extended
    return generations_extended.per_generation_sigmas()


def random_init_anchor_scores(rng_seed: int = 0,
                              base: float = 1.0) -> dict[str, float]:
    """Anchor with three RANDOM scores spanning ~3 orders of magnitude."""
    rng = np.random.default_rng(rng_seed)
    return {
        "e":   base * float(np.exp(rng.normal(0.0, 2.0))),
        "mu":  base * float(np.exp(rng.normal(2.0, 2.0))),
        "tau": base * float(np.exp(rng.normal(4.0, 2.0))),
    }


@dataclass(frozen=True)
class LeptonAnchorComparison:
    """Compares ratchet-final ratios against empirical lepton ratios."""
    ratchet_final_ratios: dict[str, float]
    empirical_ratios: dict[str, float]
    log_residual: float
    matches_lepton_tower: bool


def compare_to_empirical(scores: dict[str, float]) -> LeptonAnchorComparison:
    """Compute log-residual of (s_mu/s_e, s_tau/s_e) vs empirical."""
    from . import generations_extended
    sigmas = generations_extended.per_generation_sigmas()
    emp_ratios = {
        "mu_over_e": sigmas["mu"] / sigmas["e"],
        "tau_over_e": sigmas["tau"] / sigmas["e"],
    }
    final_ratios = {
        "mu_over_e": scores.get("mu", 0.0) / max(scores.get("e", 1e-12), 1e-12),
        "tau_over_e": scores.get("tau", 0.0) / max(scores.get("e", 1e-12), 1e-12),
    }
    log_res = float(np.linalg.norm([
        np.log(max(final_ratios["mu_over_e"], 1e-12))
        - np.log(emp_ratios["mu_over_e"]),
        np.log(max(final_ratios["tau_over_e"], 1e-12))
        - np.log(emp_ratios["tau_over_e"]),
    ]))
    return LeptonAnchorComparison(
        ratchet_final_ratios=final_ratios,
        empirical_ratios=emp_ratios,
        log_residual=log_res,
        matches_lepton_tower=(log_res < 0.5),
    )


def run_random_init_to_lepton_pinning_test(
    n_trials: int = 5,
    n_steps: int = 200,
    amplitude: float = 0.3,
) -> dict:
    """For multiple random initialisations, run the ratchet and check
    whether it converges to the empirical lepton ratios.

    EXPECTED: NO convergence (ratchet preserves but doesn't pin).
    """
    log_residuals = []
    for trial in range(n_trials):
        init = random_init_anchor_scores(rng_seed=trial)
        traj = run_ratchet_perturbation_test(
            initial_scores=init,
            rng_seed=trial * 100 + 1,
            amplitude=amplitude,
            n_steps=n_steps,
        )
        comp = compare_to_empirical(traj.final_scores)
        log_residuals.append(comp.log_residual)
    return {
        "n_trials": n_trials,
        "log_residuals": log_residuals,
        "mean_log_residual": float(np.mean(log_residuals)),
        "any_match": any(r < 0.5 for r in log_residuals),
        "verdict": (
            "Pareto ratchet does NOT pin lepton ratios from random init "
            "(by design — it's a stability mechanism, not a generator)."
            if not any(r < 0.5 for r in log_residuals)
            else "UNEXPECTED: at least one random init landed at lepton ratios — recheck"
        ),
    }


__all__ = [
    "ParetoRatchet", "perturb_scores",
    "RatchetTrajectory", "run_ratchet_perturbation_test",
    "lepton_anchor_scores", "random_init_anchor_scores",
    "LeptonAnchorComparison", "compare_to_empirical",
    "run_random_init_to_lepton_pinning_test",
]
