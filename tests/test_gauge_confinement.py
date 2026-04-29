"""SU(3) flux-tube tests (HYPOTHESIS Step 39)."""

import numpy as np

from dinos import gauge_confinement as gc


def test_eight_gell_mann_generators():
    assert len(gc.GELL_MANN) == 8


def test_gell_mann_orthogonality():
    """Tr(lambda_a lambda_b) = 2 delta_{ab}."""
    for a in range(8):
        for b in range(8):
            tr = np.trace(gc.GELL_MANN[a] @ gc.GELL_MANN[b])
            expected = 2.0 if a == b else 0.0
            assert abs(tr.real - expected) < 1e-12
            assert abs(tr.imag) < 1e-12


def test_su3_holonomy_is_unitary():
    rng = np.random.default_rng(0)
    angles = rng.normal(0, 0.5, 8)
    U = gc.su3_wilson_phase(angles)
    assert np.allclose(U @ U.conj().T, np.eye(3), atol=1e-10)


def test_su3_holonomy_has_unit_determinant():
    rng = np.random.default_rng(1)
    angles = rng.normal(0, 0.4, 8)
    U = gc.su3_wilson_phase(angles)
    assert abs(np.linalg.det(U) - 1.0) < 1e-10


def test_z3_center_element():
    Z = gc.su3_z3_center_holonomy()
    assert abs(np.linalg.det(Z) - 1.0) < 1e-12  # det = exp(2pi i) = 1
    # Z^3 = I
    assert np.allclose(np.linalg.matrix_power(Z, 3), np.eye(3), atol=1e-10)


def test_wilson_trace_z3_center():
    """Tr(Z^N)/3 = exp(2 pi i N / 3); modulus 1, NOT exponential decay."""
    Z = gc.su3_z3_center_holonomy()
    for N in [3, 6, 9, 12]:
        W = gc.wilson_loop_trace_1d(N, Z)
        assert abs(abs(W) - 1.0) < 1e-10


def test_generic_holonomy_traces_do_not_decay_exponentially():
    """Honest negative result: 1D Wilson trace is not a confinement
    signature; |Tr| oscillates inside [0, 1] without monotonic decay."""
    info = gc.random_su3_holonomy_decay_rate(N_max=64, seed=0)
    assert info["max_abs_trace"] > 0.05
    # The key honest claim: NOT exponentially driven to zero.
    assert "oscillating" in info["verdict"].lower()


def test_flux_tube_report_carries_caveat():
    rep = gc.flux_tube_report(N=128, center_element=True)
    assert rep.is_z3_center
    assert "NOT a confinement" in rep.notes
    assert rep.wilson_trace_abs > 0.5  # center element has |trace|=1


def test_su3_mobius_laplacian_is_hermitian():
    Z = gc.su3_z3_center_holonomy()
    L = gc.su3_mobius_laplacian(16, Z)
    assert np.allclose(L, L.conj().T, atol=1e-12)


def test_su3_mobius_laplacian_eigenvalues_real():
    Z = gc.su3_z3_center_holonomy()
    L = gc.su3_mobius_laplacian(8, Z)
    eigs = np.linalg.eigvalsh(L)
    assert np.all(np.isreal(eigs))
