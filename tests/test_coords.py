"""Tests for BL ↔ cylindrical coordinate transformation and KN metric."""

from math import isclose, pi

import numpy as np
import pytest

from dinos import coords


def test_bl_to_cyl_roundtrip_scalar():
    # Pick an arbitrary non-polar BL point
    a = 1.5
    r, theta = 2.0, 0.9
    rho, z, _ = coords.boyer_lindquist_to_cylindrical(r, theta, a=a)
    r_back, theta_back = coords.cylindrical_to_boyer_lindquist(rho, z, a=a)
    assert isclose(float(r_back), r, rel_tol=1e-12)
    assert isclose(float(theta_back), theta, rel_tol=1e-12)


def test_bl_to_cyl_roundtrip_array():
    a = 0.7
    r = np.linspace(0.1, 5.0, 11)
    theta = np.linspace(0.1, pi - 0.1, 11)
    R, Th = np.meshgrid(r, theta)
    rho, z, _ = coords.boyer_lindquist_to_cylindrical(R, Th, a=a)
    R_back, Th_back = coords.cylindrical_to_boyer_lindquist(rho, z, a=a)
    np.testing.assert_allclose(R_back, R, rtol=1e-10, atol=1e-12)
    np.testing.assert_allclose(Th_back, Th, rtol=1e-10, atol=1e-12)


def test_outer_horizon_sub_extremal():
    # a² + Q² < M² ⇒ horizon exists
    r_plus = coords.outer_horizon(a=0.3, M=1.0, Q=0.0)
    assert r_plus is not None
    assert isclose(r_plus, 1.0 + (1.0 - 0.09) ** 0.5)


def test_outer_horizon_over_rotating_is_naked():
    # DKN electron regime: a > M → no horizon
    assert coords.outer_horizon(a=2.0, M=1.0, Q=0.0) is None
    assert coords.is_over_rotating(a=2.0, M=1.0, Q=0.0)


def test_ergosurface_sign_on_equator():
    # θ = π/2 ⇒ r_E⁺ = M + √(M² − Q²) = 2M for Q=0
    r_e = coords.ergosurface_outer(theta=pi / 2, a=2.0, M=1.0, Q=0.0)
    assert isclose(float(r_e), 2.0)


def test_metric_kerr_frame_dragging_sign():
    # For a > 0 and 0 < θ < π/2, g_tφ should be negative
    m = coords.cylindrical_kerr_metric_components(rho=1.0, z=0.2,
                                                  phi=0.0, a=1.5, M=1.0, Q=0.0)
    assert m.g_tphi < 0.0
    # Σ, Δ, g_φφ positive on this patch
    assert m.Sigma > 0.0
    assert m.g_phiphi > 0.0


def test_metric_zero_spin_reduces_to_schwarzschild():
    # a = 0 ⇒ g_tφ = 0 and g_tt = −(1 − 2M/r)
    m = coords.cylindrical_kerr_metric_components(rho=3.0, z=0.0, phi=0.0,
                                                  a=0.0, M=1.0, Q=0.0)
    assert isclose(m.g_tphi, 0.0, abs_tol=1e-15)
    assert isclose(m.g_tt, -(1.0 - 2.0 / 3.0), rel_tol=1e-12)
