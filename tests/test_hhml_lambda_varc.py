"""HHmL hybrid + Lambda attractor + varying-c tests (HYPOTHESIS Step 46)."""

import numpy as np

from dinos import hhml_dkn_hybrid as hh
from dinos import lambda_attractor as la
from dinos import varying_c_pruning as vcp


# ---- HHmL hybrid ----

def test_branches_generation_shape():
    p = hh.HHmLPruningParams(n_branches=16, n_nodes=64)
    b = hh.generate_branches(p)
    assert b.shape == (16, 64)


def test_pruning_at_low_threshold_keeps_all():
    p = hh.HHmLPruningParams(n_branches=16, n_nodes=64)
    b = hh.generate_branches(p)
    rep = hh.prune(b, threshold=-1.0)   # below any coherence
    assert rep.n_pruned == 0
    assert rep.dark_fraction == 0.0


def test_pruning_at_high_threshold_keeps_few():
    p = hh.HHmLPruningParams(n_branches=16, n_nodes=64)
    b = hh.generate_branches(p)
    rep = hh.prune(b, threshold=1.0)   # above any possible coherence
    assert rep.n_pruned > 0


def test_pruning_entropy_conserved():
    p = hh.HHmLPruningParams(n_branches=16, n_nodes=64)
    b = hh.generate_branches(p)
    rep = hh.prune(b, threshold=0.5)
    assert abs(rep.entropy_conservation_ratio - 1.0) < 1e-12


def test_threshold_for_target_dark_fraction_proves_tunable():
    p = hh.HHmLPruningParams(n_branches=64, n_nodes=128)
    b = hh.generate_branches(p)
    info = hh.threshold_for_target_dark_fraction(b, target=0.27, tol=0.05)
    # Threshold can be found that hits ~0.27 by construction
    assert abs(info["achieved_dark_fraction"] - 0.27) < 0.10


# ---- Lambda attractor ansatz ----

def test_lambda_peak_at_specified_center():
    p = la.LambdaAttractorParams(f_star=0.27)
    s = la.scan_lambda_vs_fDM(p)
    assert abs(s.peak_at - 0.27) < 0.02


def test_lambda_attractor_center_can_be_anything():
    """Replace 0.27 with 0.45; the peak moves to 0.45 — proves the
    'attractor' is just the ansatz center."""
    p = la.replace_attractor_center(0.45)
    s = la.scan_lambda_vs_fDM(p)
    assert abs(s.peak_at - 0.45) < 0.02


# ---- varying-c pruning ----

def test_varying_c_branches_can_be_pruned():
    rep = vcp.evolve_with_variable_c(n_branches=32, n_nodes=128, c_std=0.2)
    assert rep.n_kept + rep.n_pruned == 32
    assert "tautology" in rep.notes.lower()
