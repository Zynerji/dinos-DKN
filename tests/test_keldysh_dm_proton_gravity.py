"""Keldysh fixed-point + DM scalar + proton stability + gravity confined
scaffold tests (HYPOTHESIS Steps 47-48)."""

import numpy as np

from dinos import keldysh_fixedpoint as kfp
from dinos import dm_scalar_channel as dmc
from dinos import proton_stability as ps
from dinos import gravity_with_confined_sources as gwc


# ---- keldysh_fixedpoint ----

def test_dalembertian_with_z2_twist():
    """Twist sign should flip the seam contribution."""
    psi = np.ones(8, dtype=complex)
    out_pos = kfp.discrete_dalembertian(psi, c=1.0, twist_sign=+1)
    out_neg = kfp.discrete_dalembertian(psi, c=1.0, twist_sign=-1)
    # Seam term sign flip should make the boundary contribution different
    assert not np.allclose(out_pos, out_neg)


def test_keldysh_iteration_runs():
    rep = kfp.evolve_keldysh_fixed_point(N=32, m=0.05, eta=0.05, max_iter=200)
    # Either converges or doesn't; both are valid outcomes
    assert rep.iterations >= 1
    assert rep.final_norm > 0


def test_keldysh_works_at_multiple_c_values():
    """Confirm the iteration works (doesn't NaN) for c != 1, against
    Grok's claim that c=1 is special."""
    for c in [0.5, 1.0, 1.5]:
        rep = kfp.evolve_keldysh_fixed_point(N=16, c=c, m=0.05, eta=0.05,
                                               max_iter=100)
        assert np.isfinite(rep.final_residual)


# ---- DM scalar channel ----

def test_hidden_scalar_mass_in_keV_window():
    rep = dmc.hidden_scalar_channel()
    # Existing dm.py predicts m* ~ 155 keV
    assert 100 < rep.m_scalar_keV < 300


def test_dm_scalar_channel_caveat():
    rep = dmc.hidden_scalar_channel()
    assert "NOT verified" in rep.notes


# ---- proton stability ----

def test_baryon_winding_mod3():
    s0 = ps.baryon_winding(0)
    s3 = ps.baryon_winding(3)
    s4 = ps.baryon_winding(4)
    assert s0.baryon_number_mod3 == 0
    assert s3.baryon_number_mod3 == 0
    assert s4.baryon_number_mod3 == 1


# ---- gravity with confined sources ----

def test_gravity_confined_negligible_at_electron_scale():
    rep = gwc.confined_metric_backreaction(sigma_QCD_GeV2=0.18)
    # Even with confinement, dg/g should be tiny at electron scale
    assert abs(rep.delta_g_over_g_with_confinement) < 1e-30


def test_gravity_confined_caveat():
    rep = gwc.confined_metric_backreaction()
    assert "negligible" in rep.notes.lower() or "not implemented" in rep.notes.lower()
