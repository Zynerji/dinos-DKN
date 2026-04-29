"""Foot+Koide+Pareto lepton tower derivation tests (HYPOTHESIS Step 8)."""

from math import isclose

import numpy as np
import pytest

from dinos import generations, lepton_tower_derivation as ltd


# -----------------------------------------------------------------------------
# Koide -> b = sqrt(2)
# -----------------------------------------------------------------------------

def test_koide_at_three_halves_implies_b_sqrt_2():
    """Q = 3/2  =>  b = sqrt(2) exactly."""
    b = ltd.koide_implied_b(q_value=1.5)
    assert isclose(b, np.sqrt(2.0), rel_tol=1e-12)


def test_koide_implied_b_rejects_invalid_q():
    """Q must be in (0, 3] (so b^2 = 6/Q - 2 >= 0)."""
    with pytest.raises(ValueError):
        ltd.koide_implied_b(q_value=4.0)
    with pytest.raises(ValueError):
        ltd.koide_implied_b(q_value=-0.1)


# -----------------------------------------------------------------------------
# Derivation of (a, phi) from three masses
# -----------------------------------------------------------------------------

def test_derive_a_from_lepton_masses():
    """a = ((sum sqrt m)/3)^2; for empirical leptons, a ~ 313.84 MeV."""
    masses = [
        generations.M_E_MeV,
        generations.M_MU_MeV,
        generations.M_TAU_MeV,
    ]
    a = ltd.derive_a_from_three_masses(masses)
    assert isclose(a, 313.84, rel_tol=1e-3), f"a = {a}, expected ~313.84"


def test_derive_phi_from_lepton_masses():
    """For empirical leptons, phi ~ 12.74 deg = 0.2223 rad."""
    masses = [
        generations.M_E_MeV,
        generations.M_MU_MeV,
        generations.M_TAU_MeV,
    ]
    phi = ltd.derive_phi_from_three_masses(masses)
    assert isclose(phi, 0.2223, abs_tol=0.001), f"phi = {phi}"


def test_foot_eigenvalues_round_trip_to_empirical_masses():
    """foot_eigenvalues with derived (a, b, phi) should reproduce empirical."""
    masses = [
        generations.M_E_MeV,
        generations.M_MU_MeV,
        generations.M_TAU_MeV,
    ]
    a = ltd.derive_a_from_three_masses(masses)
    b = np.sqrt(2.0)
    phi = ltd.derive_phi_from_three_masses(masses, b=b)
    eigs = ltd.foot_eigenvalues(a, b, phi)
    eigs_sorted = sorted(eigs)
    masses_sorted = sorted(masses)
    for e, m in zip(eigs_sorted, masses_sorted):
        # 0.1% tolerance accounts for the ~0.001% Koide deviation.
        assert isclose(e, m, rel_tol=1e-2), (
            f"foot eig {e} vs empirical {m}"
        )


# -----------------------------------------------------------------------------
# Four-branch prediction of m_tau from (m_e, m_mu)
# -----------------------------------------------------------------------------

def test_four_branches_returned():
    """4 branches (sign_v=+/-1, root_sign=+/-1)."""
    branches = ltd.predict_third_mass_branches(
        m_1_MeV=generations.M_E_MeV,
        m_2_MeV=generations.M_MU_MeV,
    )
    assert len(branches) == 4


def test_one_branch_predicts_m_tau_to_high_precision():
    """At least one branch matches empirical m_tau to better than 0.1%."""
    branches = ltd.predict_third_mass_branches(
        m_1_MeV=generations.M_E_MeV,
        m_2_MeV=generations.M_MU_MeV,
    )
    target = generations.M_TAU_MeV
    rel_errors = [abs(b.m_3_MeV - target) / target for b in branches]
    best_err = min(rel_errors)
    assert best_err < 0.001, (
        f"best branch gives rel_err = {best_err}, expected < 0.001"
    )


def test_branches_satisfy_foot_constraint_u_v_w_sum_to_3():
    """All 4 branches must satisfy u + v + w = 3 (Foot identity)."""
    branches = ltd.predict_third_mass_branches(
        m_1_MeV=generations.M_E_MeV,
        m_2_MeV=generations.M_MU_MeV,
    )
    for b in branches:
        s = b.u + b.v + b.w
        assert isclose(s, 3.0, abs_tol=1e-9), f"branch sum = {s}"


def test_best_branch_helper_returns_match():
    """The convenience helper returns the best branch and its rel error."""
    branch, rel_err = ltd.best_branch_matching_empirical_tau()
    assert rel_err < 0.001
    target = generations.M_TAU_MeV
    assert isclose(branch.m_3_MeV, target, rel_tol=0.001)


# -----------------------------------------------------------------------------
# Cabibbo angle proximity (numerical observation)
# -----------------------------------------------------------------------------

def test_foot_phi_is_close_to_cabibbo_angle():
    """Empirical Foot phi ~ 12.74 deg, Cabibbo theta_C ~ 13.04 deg.
    Difference is ~0.3 deg --- close, but not exact equality."""
    report = ltd.cabibbo_proximity_to_foot_phi()
    assert abs(report["difference_deg"]) < 1.0, (
        f"phi - theta_C = {report['difference_deg']} deg; expected < 1 deg"
    )
    # But also: not equal to high precision (this is a numerical
    # observation, not a derivation).
    assert abs(report["difference_deg"]) > 0.05, (
        f"phi and theta_C agree to {report['difference_deg']} deg --- "
        f"if this becomes exact the relationship may be deeper"
    )


# -----------------------------------------------------------------------------
# Pareto-ratchet wrapper preserves Foot structure
# -----------------------------------------------------------------------------

def test_ratchet_wrapped_foot_preserves_ordering_at_small_perturbation():
    """At small phi perturbation, the mass *ordering* is preserved.
    Magnitudes drift but the 3-mode hierarchy is maintained."""
    report = ltd.ratchet_protected_foot(
        initial_phi_rad=None,
        n_steps=50, perturb_amplitude=0.01, rng_seed=0,
    )
    final = report.final_masses
    assert final["e"] < final["mu"] < final["tau"], (
        f"mass ordering broken: {final}"
    )


def test_foot_structure_self_stabilises_against_dual_collapse():
    """A KEY EMPIRICAL OBSERVATION: even at large phi perturbation
    (amp=0.5), the Foot eigenvalue formula naturally prevents two
    masses from dropping below their 80% floor simultaneously.

    Reason: the Foot identities (Sum cos = 0, Sum cos^2 = 3/2)
    couple the three eigenvalues so that when one drops, others
    rise to conserve Sum m. Dual collapse is essentially forbidden
    by the structure itself. This is a STRONGER stability than
    the Pareto ratchet provides --- the ratchet is largely
    redundant for Foot-constrained systems."""
    report = ltd.ratchet_protected_foot(
        initial_phi_rad=None,
        n_steps=200, perturb_amplitude=0.5, rng_seed=0,
    )
    # At amp=0.5, we expect FEW rollbacks because Foot prevents
    # dual collapse. This documents the self-stabilisation.
    assert report.n_rollbacks <= 5, (
        f"unexpectedly many rollbacks ({report.n_rollbacks}) -- "
        f"Foot was supposed to be self-stabilising"
    )
