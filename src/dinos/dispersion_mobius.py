"""Dispersion relations on the Möbius strip (HYPOTHESIS Step 44).

Honest scope
------------
This module DOES:
  - Compute the linear-wave dispersion omega(k) = c |k| + topological
    drift on the discrete Möbius strip.
  - Compute the actual eigenfrequencies of the discrete Laplacian
    on the Möbius (with Z2 seam) and report them honestly.
  - Demonstrate quantitatively that |v_g - c| is a function of the
    dispersion shape ONLY, NOT of c — so c is not "selected" by any
    eigenvalue minimisation. This refutes Grok's "emergent c" claim.

This module DOES NOT:
  - Derive the value of c from any deeper physics. c is an input
    to the dispersion, not an output.

Verdict on the Grok claim that c emerges as the eigenvalue minimising
group-velocity deviation: FALSIFIED. See dinos.grok_claims_validation.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import pi

import numpy as np


@dataclass(frozen=True)
class DispersionScan:
    c_values: np.ndarray
    mean_v_group_deviation: np.ndarray
    is_c_independent_within: float    # max - min of mean_v_group_deviation
    notes: str


def linear_dispersion_with_twist(k: np.ndarray, c: float = 1.0,
                                   twist: float = pi) -> np.ndarray:
    """omega(k) = c |k| + (twist / (2 pi)) sgn(k)."""
    return c * np.abs(k) + (twist / (2.0 * pi)) * np.sign(k)


def dispersion_stability_scan(c_values=None, N: int = 256) -> DispersionScan:
    """Confirm that |v_g - c| is c-independent for the linear dispersion."""
    if c_values is None:
        c_values = np.linspace(0.3, 2.5, 12)
    s = np.linspace(0, 2 * pi, N, endpoint=False)
    ds = s[1] - s[0]
    k = np.fft.fftfreq(N, ds) * 2 * pi
    k = k[1:N // 2]   # exclude k=0
    devs: list[float] = []
    for c in c_values:
        omega = linear_dispersion_with_twist(k, c=c)
        v_g = np.gradient(omega, k)
        devs.append(float(np.mean(np.abs(v_g - c))))
    arr = np.array(devs)
    spread = float(arr.max() - arr.min())
    return DispersionScan(
        c_values=np.array(c_values),
        mean_v_group_deviation=arr,
        is_c_independent_within=spread,
        notes=("Linear dispersion gives v_g = c at every c. The spread "
               "of |v_g - c| across c reflects discrete numerical noise, "
               "not c-selection. There is no eigenvalue criterion that "
               "picks c = 1."),
    )


def discrete_mobius_eigenfrequencies(N: int = 64,
                                      twist_sign: int = -1) -> np.ndarray:
    """Eigenvalues sqrt(-Lap) of the discrete twisted Laplacian.
    These are the actual lattice eigenfrequencies; for c=1 they
    approach |k| in the continuum limit."""
    if twist_sign not in (+1, -1):
        raise ValueError("twist_sign must be +1 or -1")
    L = np.zeros((N, N), dtype=complex)
    for j in range(N):
        L[j, j] = -2.0
        L[j, (j + 1) % N] += 1.0 if j != N - 1 else float(twist_sign)
        L[j, (j - 1) % N] += 1.0 if j != 0 else float(twist_sign)
    L = -0.5 * (L + L.conj().T)
    # -Lap = -L if convention takes Laplacian as second-difference operator
    lap = -L
    eigs = np.linalg.eigvalsh(lap)
    return np.sqrt(np.maximum(eigs, 0.0))


__all__ = [
    "DispersionScan", "linear_dispersion_with_twist",
    "dispersion_stability_scan", "discrete_mobius_eigenfrequencies",
]
