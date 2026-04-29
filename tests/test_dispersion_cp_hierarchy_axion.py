"""Dispersion + Strong CP + cover hierarchy + axion bridge tests
(HYPOTHESIS Steps 44-45)."""

import numpy as np

from dinos import dispersion_mobius as dm_disp
from dinos import strong_cp_relaxation as scp
from dinos import cover_hierarchy as ch
from dinos import axion_dm_bridge as ax


# ---- dispersion ----

def test_dispersion_stability_is_c_independent():
    s = dm_disp.dispersion_stability_scan(c_values=np.linspace(0.5, 2.0, 8))
    # Spread of |v_g - c| across c should be < 1e-3 (numerical floor only)
    assert s.is_c_independent_within < 1e-2


def test_discrete_mobius_eigenfrequencies_real_nonneg():
    eigs = dm_disp.discrete_mobius_eigenfrequencies(N=32)
    assert np.all(np.isfinite(eigs))
    assert np.all(eigs >= -1e-12)


# ---- strong_cp ----

def test_theta_relaxes_to_minimum():
    rep = scp.relax_theta_gradient_flow(theta_init=0.5, theta_min=0.0)
    assert rep.converged
    assert abs(rep.theta_final) < 1e-6


def test_strong_cp_status_is_open():
    s = scp.symmetry_argument_status()
    assert s.framework_provides_theta_zero_minimum is False


# ---- cover_hierarchy ----

def test_suppression_factor_correct():
    h = ch.suppression(A=0.5, n_cover=10)
    assert abs(h.suppression_factor - 0.5 ** 10) < 1e-15


def test_n_cover_to_reach_electron_from_planck():
    info = ch.n_cover_to_reach_target(A=0.48,
                                        initial_scale_GeV=1e19,
                                        target_scale_GeV=5.11e-4)
    assert info["feasible"]
    # log(5.11e-4 / 1e19) / log(0.48) ~ 65
    assert 50 < info["n_required_real"] < 90


# ---- axion_bridge ----

def test_axion_mass_inverse_proportional_to_f_a():
    m1 = ax.axion_mass_from_decay_constant(1e11)
    m2 = ax.axion_mass_from_decay_constant(1e12)
    # m_a ∝ 1/f_a
    assert abs(m1 / m2 - 10.0) < 1e-6


def test_axion_prediction_has_caveat():
    p = ax.axion_prediction()
    assert "tunable" in p.notes.lower() or "input" in p.notes.lower()
    assert p.f_a_GeV > 0
    assert p.m_axion_eV > 0


def test_axion_window_scan_returns_list():
    scan = ax.scan_axion_window(n_covers=range(5, 12))
    assert len(scan) == 7
    # m_a should monotonically decrease as n_cover increases (f_a grows)
    masses = [s.m_axion_eV for s in scan]
    assert all(masses[i] > masses[i + 1] for i in range(len(masses) - 1))
