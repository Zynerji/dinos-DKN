"""Step 12 extension tests: neutrinos, CKM, hierarchy, gauge, gravity."""

from math import isclose

import numpy as np

from dinos import (
    neutrinos_brannen,
    ckm_foot_test,
    hierarchy_scale,
    gauge_extension,
    quantum_gravity_loop,
)


# ============================================================================
# 12a: Neutrinos
# ============================================================================

def test_neutrino_foot_solver_converges():
    """Foot ansatz with b = sqrt(2) and Δm² constraints converges."""
    a, phi, masses = neutrinos_brannen.solve_foot_for_neutrinos()
    assert a > 0
    assert all(m > 0 for m in masses)


def test_neutrino_predicted_sum_within_planck_bound():
    """Predicted Σm_ν ~ 0.06 eV, within Planck 0.12 eV bound."""
    report = neutrinos_brannen.neutrino_prediction_report()
    assert report.sum_within_planck
    assert 0.04 < report.sum_m_eV < 0.10


def test_neutrino_masses_satisfy_delta_m_squared():
    """Predicted neutrino masses reproduce empirical Δm² to high precision."""
    a, phi, masses = neutrinos_brannen.solve_foot_for_neutrinos()
    dm21 = masses[1] ** 2 - masses[0] ** 2
    dm31 = masses[2] ** 2 - masses[0] ** 2
    assert isclose(dm21, neutrinos_brannen.DELTA_M21_SQ_eV2, rel_tol=1e-6)
    assert isclose(dm31, neutrinos_brannen.DELTA_M31_SQ_ABS_eV2, rel_tol=1e-6)


def test_neutrino_branch_has_one_negative_factor():
    """Neutrinos sit in the *one-sign-flip* branch (charged leptons: 0 flips)."""
    report = neutrinos_brannen.neutrino_prediction_report()
    assert report.n_negative_foot_factors == 1


# ============================================================================
# 12b: CKM
# ============================================================================

def test_cabibbo_lepton_phi_gap_is_positive():
    """θ_C ≈ 13.04° > φ_lepton = 12.74° (gap ~ 0.30°)."""
    report = ckm_foot_test.cabibbo_lepton_gap_report()
    assert report.gap_deg > 0
    assert isclose(report.gap_deg, 0.30, abs_tol=0.05)


def test_foot_extension_to_ckm_does_not_work():
    """Honest negative: sin(2/9) ≠ Wolfenstein λ within 0.005."""
    report = ckm_foot_test.cabibbo_lepton_gap_report()
    assert not report.foot_extension_works


# ============================================================================
# 12c: Hierarchy
# ============================================================================

def test_v_SM_to_v_bag_ratio_is_about_5_orders():
    """v_SM (246 GeV) / v_bag (0.43 MeV) ~ 10^5.8."""
    report = hierarchy_scale.hierarchy_report()
    assert 5.0 < report.log10_v_SM_v_bag < 6.5


def test_framework_explicitly_does_not_address_hierarchy():
    """Honest non-derivation."""
    report = hierarchy_scale.hierarchy_report()
    assert not report.framework_addresses_hierarchy


# ============================================================================
# 12d: Gauge
# ============================================================================

def test_su2_wilson_phase_is_unitary():
    """U·U† = I for the SU(2) Wilson phase."""
    U = gauge_extension.su2_wilson_phase(angle=2.094, axis="z")
    UUdag = U @ U.conj().T
    np.testing.assert_allclose(UUdag, np.eye(2), atol=1e-12)


def test_su2_mobius_laplacian_is_2N_dimensional():
    """SU(2) cover doubles the Hilbert-space size per node."""
    N = 8
    U = gauge_extension.su2_wilson_phase(angle=2 * np.pi / 3)
    L = gauge_extension.su2_mobius_laplacian(N, U)
    assert L.shape == (2 * N, 2 * N)


def test_su2_eigenvalues_are_real():
    """Hermitised SU(2) Laplacian has real eigenvalues."""
    eigs = gauge_extension.su2_eigenvalues(N=16, holonomy_angle=2 * np.pi / 3)
    # eigvalsh already returns real; just check no NaN/inf
    assert np.all(np.isfinite(eigs))


def test_su2_does_not_match_SM_gauge():
    """Honest non-derivation: SU(2) scaffold doesn't reproduce SM gauge."""
    report = gauge_extension.su2_gauge_report()
    assert not report.matches_SM_gauge_structure


# ============================================================================
# 12e: Quantum gravity
# ============================================================================

def test_one_loop_qg_correction_is_negligible():
    """Graviton-loop correction to m_e is (m_e/M_Pl)² ~ 10⁻⁴⁴."""
    report = quantum_gravity_loop.estimate_one_loop_correction()
    assert report.is_safely_neglected
    assert report.one_loop_correction_order < 1e-40


def test_classical_and_one_loop_both_negligible():
    """Both classical (Step 6c) and one-loop QG corrections are below
    mass-closure precision."""
    report = quantum_gravity_loop.estimate_one_loop_correction()
    assert report.classical_delta_g_over_g < 1e-30
    assert report.one_loop_correction_order < 1e-40
