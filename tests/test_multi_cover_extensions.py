"""Multi-cover, electroweak, and anomaly scaffolds (HYPOTHESIS Steps 40-41)."""

import numpy as np

from dinos import multi_cover as mc
from dinos import electroweak_strip as ew
from dinos import anomaly_check as ac


# ---- multi_cover ----

def test_z3_phase_is_third_root():
    omega = mc.z3_phase(1)
    assert abs(omega ** 3 - 1.0) < 1e-12


def test_seam_factor_fermion_z2():
    """Fermionic z2 seam introduces -1, not +1."""
    f = mc.multi_cover_seam_factor(n_fermion=1, n_color=0, n_gen=0)
    assert abs(f + 1.0) < 1e-12  # = -1


def test_multi_cover_laplacian_hermitian():
    p = mc.MultiCoverParams(N=16, n_gen=2)
    L = mc.multi_cover_laplacian(p, n_fermion=1, n_color=1, n_gen=1)
    assert np.allclose(L, L.conj().T, atol=1e-12)


def test_scan_generations_returns_18_sectors():
    """2 z2 x 3 z3 x 3 gen = 18 sectors."""
    p = mc.MultiCoverParams(N=16, n_gen=3)
    out = mc.scan_generations(p)
    assert len(out) == 18


# ---- electroweak_strip ----

def test_electroweak_observables_match_tree_level_SM():
    """At default (observed) inputs, mW/mZ matches tree-level SM."""
    obs = ew.electroweak_observables()
    # mW/mZ = cos(thetaW); tree-level SM
    expected = np.cos(np.arctan(ew.DEFAULT_GP / ew.DEFAULT_G2))
    assert abs(obs.mW_over_mZ - expected) < 1e-10


def test_electroweak_observables_carry_input_caveat():
    obs = ew.electroweak_observables()
    assert "INPUT" in obs.notes or "input" in obs.notes
    assert "open work" in obs.notes


def test_coupling_status_three_couplings_undefined():
    statuses = ew.coupling_derivation_status()
    assert len(statuses) == 3
    for s in statuses:
        assert s.derived_from_geometry is False


# ---- anomaly_check ----

def test_sm_one_generation_cancels_all_anomalies():
    A = ac.standard_model_anomalies()
    assert A.cancels
    assert abs(A.U1Y_cubed) < 1e-12
    assert abs(A.SU2_squared_U1Y) < 1e-12
    assert abs(A.SU3_squared_U1Y) < 1e-12
    assert abs(A.grav_squared_U1Y) < 1e-12


def test_mobius_chiral_toy_is_anomalous():
    """A single LH fermion with Y=1 has anomaly; not cancelled by topology."""
    A = ac.mobius_only_chiral_content_test()
    assert not A.cancels
    assert abs(A.U1Y_cubed - 1.0) < 1e-12  # = (+1)^3 = 1


def test_mobius_vector_like_toy_cancels_trivially():
    """LH and RH with same Y cancels by chirality difference, but
    that's just vector-likeness, not topological protection."""
    A = ac.mobius_only_content_test()
    assert A.cancels  # A_Y3 = (+1)*1 + (-1)*1 = 0
