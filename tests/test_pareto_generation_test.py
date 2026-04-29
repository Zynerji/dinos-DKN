"""Pareto-ratchet generation experiment tests."""

import numpy as np
import pytest

from dinos import pareto_generation_test as pgt


# -----------------------------------------------------------------------------
# ParetoRatchet basics (direct port from Aletheia, tested for parity)
# -----------------------------------------------------------------------------

def test_ratchet_initialises_with_anchor():
    r = pgt.ParetoRatchet(anchor={"a": 1.0, "b": 2.0, "c": 3.0})
    assert r.best_scores == {"a": 1.0, "b": 2.0, "c": 3.0}
    assert r.best_product == 6.0


def test_ratchet_rejects_empty_anchor():
    with pytest.raises(ValueError):
        pgt.ParetoRatchet(anchor={})


def test_ratchet_rejects_invalid_floor():
    with pytest.raises(ValueError):
        pgt.ParetoRatchet(anchor={"a": 1.0}, floor=1.5)


def test_below_floor_axes_detection():
    """Floor at 0.8: scores < 0.8·anchor are below floor."""
    r = pgt.ParetoRatchet(anchor={"a": 1.0, "b": 2.0}, floor=0.80)
    below = r.below_floor_axes({"a": 0.5, "b": 1.9})  # a is below, b is above
    assert below == ["a"]


def test_should_rollback_on_two_axis_collapse():
    """Rollback iff ≥ 2 axes below floor."""
    r = pgt.ParetoRatchet(anchor={"a": 1.0, "b": 1.0, "c": 1.0}, floor=0.80)
    assert not r.should_rollback({"a": 0.5, "b": 0.9, "c": 0.9})  # 1 axis low
    assert r.should_rollback({"a": 0.5, "b": 0.5, "c": 0.9})  # 2 axes low


def test_is_new_best_requires_product_improvement_and_no_floor_violation():
    r = pgt.ParetoRatchet(anchor={"a": 1.0, "b": 1.0}, floor=0.80)
    # Product increases AND no axis below floor → new best.
    assert r.is_new_best({"a": 1.2, "b": 1.1})
    # Product increases but axis below floor → NOT new best.
    assert not r.is_new_best({"a": 0.5, "b": 100.0})


# -----------------------------------------------------------------------------
# Experiment C: Ratchet maintains separation under perturbation
# -----------------------------------------------------------------------------

def test_ratchet_prevents_dual_axis_collapse_but_allows_single_axis_drift():
    """The Pareto ratchet's rollback rule fires only when ≥ 2 axes are
    below floor.  Single-axis collapse is *allowed* — this is by design
    (Phase B oscillation tolerance per the Aletheia docstring).

    Honest verdict: ratchet keeps the *top* score intact but does NOT
    enforce absolute pairwise separation."""
    init = {"e": 1.0, "mu": 100.0, "tau": 10000.0}
    initial_max = max(init.values())
    traj = pgt.run_ratchet_perturbation_test(
        initial_scores=init, rng_seed=42, amplitude=0.3, n_steps=200,
    )
    # Top score should remain within an order of magnitude of initial top.
    final_max = max(traj.final_scores.values())
    assert 0.1 * initial_max < final_max < 10.0 * initial_max, (
        f"top score collapsed: initial={initial_max}, final={final_max}"
    )
    # Some rollbacks should have happened.
    assert traj.n_rollbacks > 0, (
        "no rollbacks at amp=0.3 — ratchet not triggering"
    )


def test_ratchet_rollbacks_increase_with_perturbation_amplitude():
    """Larger perturbations should trigger more rollbacks."""
    init = {"e": 1.0, "mu": 10.0, "tau": 100.0}
    traj_low = pgt.run_ratchet_perturbation_test(
        initial_scores=init, rng_seed=0, amplitude=0.1, n_steps=200,
    )
    traj_high = pgt.run_ratchet_perturbation_test(
        initial_scores=init, rng_seed=0, amplitude=2.0, n_steps=200,
    )
    assert traj_high.n_rollbacks > traj_low.n_rollbacks, (
        f"low={traj_low.n_rollbacks}, high={traj_high.n_rollbacks}"
    )


# -----------------------------------------------------------------------------
# Experiment D: Ratchet does NOT pin lepton ratios from random init
# -----------------------------------------------------------------------------

def test_random_init_does_not_converge_to_lepton_ratios():
    """The ratchet preserves but does not pin: random initialisations
    do not converge to (m_μ/m_e, m_τ/m_e) ≈ (207, 3477) under random
    perturbation."""
    result = pgt.run_random_init_to_lepton_pinning_test(
        n_trials=5, n_steps=200, amplitude=0.3,
    )
    assert not result["any_match"], (
        f"unexpected match — log residuals: {result['log_residuals']}"
    )
    # Mean log-residual should be substantial (> 1).
    assert result["mean_log_residual"] > 1.0, (
        f"residuals suspiciously small: {result['log_residuals']}"
    )


def test_lepton_anchor_at_empirical_satisfies_floor():
    """If we anchor at the empirical lepton σ values, no axis is below
    the floor (trivially, since anchor equals scores)."""
    anchor = pgt.lepton_anchor_scores()
    r = pgt.ParetoRatchet(anchor=anchor, floor=0.80)
    assert len(r.below_floor_axes(anchor)) == 0


def test_compare_to_empirical_at_anchor_gives_zero_residual():
    """Comparing the empirical anchor against itself gives log_residual ≈ 0."""
    anchor = pgt.lepton_anchor_scores()
    comp = pgt.compare_to_empirical(anchor)
    assert comp.log_residual < 1e-9
    assert comp.matches_lepton_tower
