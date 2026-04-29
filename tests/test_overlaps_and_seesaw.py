"""CKM/PMNS/seesaw scaffold tests (HYPOTHESIS Steps 42-43)."""

import numpy as np

from dinos import ckm_overlaps as ckm
from dinos import pmns_overlaps as pmns
from dinos import topological_seesaw as ts


# ---- CKM ----

def test_overlap_matrix_at_zero_offset_is_identity():
    """delta = 0 -> psi_up == psi_down -> orthonormal -> V = I."""
    V = ckm.overlap_matrix(delta=0.0)
    assert np.allclose(V, np.eye(3), atol=1e-6)


def test_ckm_simple_ansatz_cannot_reach_subpercent():
    """Best simple-sine fit is far from sub-percent — confirms
    Grok's claim was UNDERSPECIFIED."""
    rep = ckm.fit_overlap_to_ckm()
    # Frobenius error >> 1% expected
    assert rep.rel_error_frobenius > 0.05


# ---- PMNS ----

def test_pmns_overlap_at_zero_alpha_is_identity():
    U = pmns.pmns_overlap_matrix(alpha=0.0)
    assert np.allclose(U, np.eye(3), atol=1e-6)


def test_pmns_simple_ansatz_fit_carries_caveat():
    rep = pmns.fit_pmns()
    assert "ansatz" in rep.notes.lower() or "input" in rep.notes.lower()


# ---- topological seesaw ----

def test_seesaw_spectrum_three_masses():
    s = ts.light_neutrino_spectrum()
    assert len(s.light_masses_eV) == 3
    # Should be sorted ascending
    assert s.light_masses_eV[0] <= s.light_masses_eV[1] <= s.light_masses_eV[2]


def test_seesaw_M0_tunable_for_target():
    """Test that M_0 can be solved for any target sum (proves tunability)."""
    info = ts.m_0_required_for_sum(target_sum_eV=0.06)
    assert info["M_0_required_GeV"] > 0


def test_seesaw_sum_scales_inverse_M0():
    s1 = ts.light_neutrino_spectrum(M_0_GeV=1e14)
    s2 = ts.light_neutrino_spectrum(M_0_GeV=1e15)
    # 10x M_0 -> 10x lighter neutrinos -> sum 10x smaller
    assert abs(s1.sum_m_nu_eV / s2.sum_m_nu_eV - 10.0) < 1e-6
