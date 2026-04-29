"""SU(2) Wilson-line scaffold on the Möbius cover (HYPOTHESIS Step 12d).

The standard DKN Möbius is a U(1) construction (psi -> -psi after one
loop, encoded as a Z_2 phase). Step 9b extended to Z_3 monodromy
(psi -> omega·psi). Both are Abelian.

To address the SM gauge structure SU(3)xSU(2)xU(1), we'd need
non-Abelian Wilson lines. This module builds the SU(2) version as a
scaffold and computes its eigenvalue spectrum, comparing to weak gauge
boson masses.

Honest scope statement
----------------------
- This module CAN: construct an SU(2) Wilson-line operator on the
  Möbius cover, compute its eigenvalue spectrum.
- This module CANNOT: derive the SM gauge group SU(3)xSU(2)xU(1) or
  predict gauge boson masses (W, Z, gluons). The framework's natural
  fiber is U(1) or its Z_n discrete subgroups.
- VERDICT: SU(2) Wilson line is a consistent extension but does NOT
  reproduce SM gauge structure. The cover gives a 2D Hilbert space
  per node (color/isospin), but the eigenvalues do not match weak
  gauge boson scales.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import pi

import numpy as np


# Pauli matrices (SU(2) generators, as Hermitian)
SIGMA_X = np.array([[0, 1], [1, 0]], dtype=complex)
SIGMA_Y = np.array([[0, -1j], [1j, 0]], dtype=complex)
SIGMA_Z = np.array([[1, 0], [0, -1]], dtype=complex)


def su2_wilson_phase(angle: float, axis: str = "z") -> np.ndarray:
    """SU(2) holonomy operator U = exp(i theta/2 sigma_axis).

    Going around the Möbius once picks up this U as the monodromy.
    """
    if axis == "x":
        sigma = SIGMA_X
    elif axis == "y":
        sigma = SIGMA_Y
    elif axis == "z":
        sigma = SIGMA_Z
    else:
        raise ValueError(f"axis must be x/y/z, got {axis}")
    return np.cos(angle / 2.0) * np.eye(2) + 1j * np.sin(angle / 2.0) * sigma


def su2_mobius_laplacian(N: int, U: np.ndarray) -> np.ndarray:
    """Discrete 1D Laplacian on N nodes with SU(2) monodromy U at the seam.

    Acts on a 2N-dimensional state (2 internal isospin components per node).
    Returns the 2N × 2N Laplacian matrix.
    """
    if N < 2:
        raise ValueError("N >= 2 required")
    L = np.zeros((2 * N, 2 * N), dtype=complex)
    for j in range(N):
        # Diagonal: -2 * I
        L[2 * j:2 * j + 2, 2 * j:2 * j + 2] = -2.0 * np.eye(2)
        # Forward neighbour
        j_next = (j + 1) % N
        if j == N - 1:
            # Seam: pick up U
            block = U
        else:
            block = np.eye(2)
        L[2 * j:2 * j + 2, 2 * j_next:2 * j_next + 2] += block
        # Backward neighbour
        j_prev = (j - 1) % N
        if j == 0:
            block = U.conj().T
        else:
            block = np.eye(2)
        L[2 * j:2 * j + 2, 2 * j_prev:2 * j_prev + 2] += block
    return L


def su2_eigenvalues(N: int, holonomy_angle: float = 2 * pi / 3,
                     axis: str = "z") -> np.ndarray:
    """Compute eigenvalues of the SU(2) Möbius Laplacian."""
    U = su2_wilson_phase(holonomy_angle, axis=axis)
    L = su2_mobius_laplacian(N, U)
    L_neg = -0.5 * (L + L.conj().T)   # ensure Hermitian
    eigs = np.linalg.eigvalsh(L_neg)
    return np.sort(eigs.real)


@dataclass(frozen=True)
class SU2GaugeScaffoldReport:
    N: int
    holonomy_angle_rad: float
    n_distinct_low_eigs: int
    lowest_eigenvalues: np.ndarray
    matches_SM_gauge_structure: bool
    notes: str


def su2_gauge_report(N: int = 64) -> SU2GaugeScaffoldReport:
    """Compute the SU(2) Wilson-line spectrum and document the scaffold."""
    eigs = su2_eigenvalues(N, holonomy_angle=2 * pi / 3, axis="z")
    # Take 5 lowest
    lowest = eigs[:5]
    # Count distinct eigenvalues (tolerance)
    distinct: list[float] = []
    last = -np.inf
    for e in lowest:
        if e - last > 1e-9:
            distinct.append(float(e))
            last = e
    notes = (
        f"SU(2) Mobius Laplacian on N={N} nodes with holonomy 2pi/3 "
        f"around z-axis. Lowest 5 eigenvalues: {[f'{e:.4f}' for e in lowest]}. "
        f"Number of distinct levels: {len(distinct)}. "
        f"VERDICT: this is a consistent SU(2) scaffold but does NOT "
        f"naturally produce the SM gauge structure SU(3)xSU(2)xU(1) "
        f"or predict W/Z masses. Each node carries an isospin doublet, "
        f"but the eigenvalue spectrum has no obvious mapping to gauge "
        f"boson masses. Full SM derivation requires additional structure."
    )
    return SU2GaugeScaffoldReport(
        N=N,
        holonomy_angle_rad=2 * pi / 3,
        n_distinct_low_eigs=len(distinct),
        lowest_eigenvalues=lowest,
        matches_SM_gauge_structure=False,
        notes=notes,
    )


__all__ = [
    "SIGMA_X", "SIGMA_Y", "SIGMA_Z",
    "su2_wilson_phase", "su2_mobius_laplacian", "su2_eigenvalues",
    "SU2GaugeScaffoldReport", "su2_gauge_report",
]
