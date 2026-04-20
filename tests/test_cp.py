"""Test Chandrasekhar–Page eigenvalue limits."""

from math import isclose

import pytest

from dinos import cp


def test_flat_space_limit():
    """|λ_CP| = |k| at aω = aμ = 0."""
    for k in (1, 2, 3, -1):
        assert cp.lambda_CP_flat(k) == abs(k)


def test_leading_correction_sign():
    """λ_CP² = k² − ½ a² (ω² − μ²):  ω > μ ⇒ correction negative."""
    k, a = 1, 0.1
    lam = cp.lambda_CP_leading(k, a=a, omega=1.0, mu=0.5)
    assert lam < 1.0
    assert lam > 0.99  # tiny correction


def test_k_from_j():
    assert cp.k_from_j(0.5, +1) == 1
    assert cp.k_from_j(0.5, -1) == -1
    assert cp.k_from_j(1.5, +1) == 2


def test_k_from_j_rejects_bad_j():
    with pytest.raises(ValueError):
        cp.k_from_j(0.4)
    with pytest.raises(ValueError):
        cp.k_from_j(0.5, parity=0)
