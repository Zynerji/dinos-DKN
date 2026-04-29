"""SU(3) flux-tube on the Z3 Möbius cover (HYPOTHESIS Step 39).

Implements the SU(3) extension of gauge_extension.py:
- Gell-Mann generators
- SU(3) Wilson holonomy as a one-parameter rotation through Lie algebra
- Plaquette / loop trace computation on a 1D Möbius temporal contour
- Effective string tension from -log|Tr(W)| / area

HONEST SCOPE
------------
This module DOES:
  - Construct SU(3) holonomies in the fundamental representation.
  - Compute traces of products of holonomies along a 1D contour, which
    is the natural "Wilson loop" for a single-spatial-direction model.
  - Report quantitative behaviour vs. the input angle and contour length.

This module DOES NOT:
  - Derive QCD string tension from first principles.
  - Provide a 2D area-law in any non-trivial sense — the 1D Möbius
    has no transverse area, so what we call "area" here is really
    "contour length × dummy width = N · 1". The true area-law test
    requires a 2D lattice, not implemented here.
  - Predict heavy-baryon masses from confinement scale.

The Grok conversation that prompted this module claimed "12 new tests
pass cleanly" and "STRONG CONFINEMENT" with specific tunable string
tension. Those numbers were not actually verified — Grok cannot
execute code. What this module gives is the bare numerical machinery
to compute traces of SU(3) holonomy products. Whether that constitutes
"confinement" in any physical sense is left explicit and open.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import pi, sqrt

import numpy as np


# Gell-Mann matrices in the fundamental representation, normalised
# such that Tr(lambda_a lambda_b) = 2 delta_{ab}.
LAMBDA_1 = np.array([[0, 1, 0], [1, 0, 0], [0, 0, 0]], dtype=complex)
LAMBDA_2 = np.array([[0, -1j, 0], [1j, 0, 0], [0, 0, 0]], dtype=complex)
LAMBDA_3 = np.array([[1, 0, 0], [0, -1, 0], [0, 0, 0]], dtype=complex)
LAMBDA_4 = np.array([[0, 0, 1], [0, 0, 0], [1, 0, 0]], dtype=complex)
LAMBDA_5 = np.array([[0, 0, -1j], [0, 0, 0], [1j, 0, 0]], dtype=complex)
LAMBDA_6 = np.array([[0, 0, 0], [0, 0, 1], [0, 1, 0]], dtype=complex)
LAMBDA_7 = np.array([[0, 0, 0], [0, 0, -1j], [0, 1j, 0]], dtype=complex)
LAMBDA_8 = np.array([[1, 0, 0], [0, 1, 0], [0, 0, -2]], dtype=complex) / sqrt(3.0)

GELL_MANN: list[np.ndarray] = [
    LAMBDA_1, LAMBDA_2, LAMBDA_3, LAMBDA_4,
    LAMBDA_5, LAMBDA_6, LAMBDA_7, LAMBDA_8,
]


def su3_generator(angles: np.ndarray) -> np.ndarray:
    """Hermitian generator H = sum_a (theta_a / 2) lambda_a."""
    if len(angles) != 8:
        raise ValueError(f"need 8 SU(3) angles, got {len(angles)}")
    H = np.zeros((3, 3), dtype=complex)
    for a, theta in enumerate(angles):
        H = H + (theta / 2.0) * GELL_MANN[a]
    return H


def su3_wilson_phase(angles: np.ndarray) -> np.ndarray:
    """U = exp(i sum_a (theta_a/2) lambda_a) — proper one-parameter
    SU(3) holonomy via matrix exponential.
    """
    H = su3_generator(angles)
    eigvals, V = np.linalg.eigh(H)
    return V @ np.diag(np.exp(1j * eigvals)) @ V.conj().T


def su3_z3_center_holonomy() -> np.ndarray:
    """Z3 center element of SU(3): exp(2 pi i / 3) * I_3 (in U(3)),
    realised inside SU(3) as exp(i (2 pi / 3) lambda_8 / sqrt(3)).
    Returns the Z3 center element exp(2 pi i / 3) * I, which is exactly
    one of the three center elements of SU(3).
    """
    return np.exp(2j * pi / 3) * np.eye(3, dtype=complex)


def wilson_loop_trace_1d(N: int, U: np.ndarray) -> complex:
    """Trace of U^N divided by 3 (fundamental dimension) — the simplest
    Wilson loop on a 1D Möbius temporal contour of length N steps where
    U is the per-step holonomy.

    Returns Tr(U^N)/3.
    """
    if N < 1:
        raise ValueError("N >= 1 required")
    W = np.linalg.matrix_power(U, N)
    return complex(np.trace(W)) / 3.0


@dataclass(frozen=True)
class FluxTubeReport:
    """Output of the 1D Wilson-loop computation."""
    N: int
    holonomy_angles: np.ndarray
    wilson_trace_real: float
    wilson_trace_abs: float
    log_trace_per_step: float    # -log|Tr|/N — naive "tension" proxy
    is_z3_center: bool
    notes: str


def flux_tube_report(N: int = 192,
                     angles: np.ndarray | None = None,
                     center_element: bool = False) -> FluxTubeReport:
    """Compute the bare 1D Wilson trace and report what it tells us."""
    if center_element:
        # Z3 center: trace is real and equals exp(2 pi i / 3) per copy.
        # For Wilson loop trace we use the literal Z3 center element.
        U = su3_z3_center_holonomy()
        ang = np.zeros(8)
    else:
        if angles is None:
            angles = np.zeros(8)
        ang = np.asarray(angles, dtype=float)
        U = su3_wilson_phase(ang)

    W = wilson_loop_trace_1d(N, U)
    abs_W = float(abs(W))
    safe = max(abs_W, 1e-30)
    tau = -float(np.log(safe)) / N
    is_center = center_element
    notes = (
        "1D Wilson trace Tr(U^N)/3 over N seam-traversals. "
        "For a Z3 center holonomy the modulus is exact (|Tr|/3 = 1 if "
        "N is a multiple of 3, else a 3rd-root-of-unity phase whose "
        "absolute value is still 1 — so this is NOT a confinement "
        "signature in any non-trivial sense). True area-law confinement "
        "needs a 2D plaquette computation that is not present in the "
        "1D Mobius contour."
    )
    return FluxTubeReport(
        N=N,
        holonomy_angles=ang,
        wilson_trace_real=float(W.real),
        wilson_trace_abs=abs_W,
        log_trace_per_step=tau,
        is_z3_center=is_center,
        notes=notes,
    )


def random_su3_holonomy_decay_rate(N_max: int = 64,
                                   seed: int = 0,
                                   theta_scale: float = 0.6) -> dict:
    """For a generic SU(3) holonomy (not center), trace |Tr(U^N)/3|
    typically does NOT decay exponentially — it oscillates inside [0, 1].
    This function checks that, returning the median |trace| across
    N = 1..N_max and showing it does not show exponential decay.
    """
    rng = np.random.default_rng(seed)
    angles = rng.normal(0, theta_scale, 8)
    U = su3_wilson_phase(angles)
    traces = [abs(wilson_loop_trace_1d(N, U)) for N in range(1, N_max + 1)]
    arr = np.array(traces)
    return {
        "median_abs_trace": float(np.median(arr)),
        "max_abs_trace": float(arr.max()),
        "min_abs_trace": float(arr.min()),
        "decay_per_step": float(-np.log(max(arr.mean(), 1e-30)) / N_max),
        "verdict": (
            "Generic SU(3) holonomy on a 1D Mobius contour produces "
            "oscillating traces, not exponential decay. No confinement "
            "signature without a 2D plaquette."
        ),
    }


def su3_mobius_laplacian(N: int, U: np.ndarray) -> np.ndarray:
    """3-color version of su2_mobius_laplacian on N nodes with seam holonomy U.

    Returns a (3N, 3N) Hermitian Laplacian.
    """
    if N < 2:
        raise ValueError("N >= 2 required")
    L = np.zeros((3 * N, 3 * N), dtype=complex)
    I3 = np.eye(3, dtype=complex)
    for j in range(N):
        L[3 * j:3 * j + 3, 3 * j:3 * j + 3] = -2.0 * I3
        j_next = (j + 1) % N
        block_fwd = U if j == N - 1 else I3
        L[3 * j:3 * j + 3, 3 * j_next:3 * j_next + 3] += block_fwd
        j_prev = (j - 1) % N
        block_back = U.conj().T if j == 0 else I3
        L[3 * j:3 * j + 3, 3 * j_prev:3 * j_prev + 3] += block_back
    return -0.5 * (L + L.conj().T)


__all__ = [
    "GELL_MANN", "LAMBDA_1", "LAMBDA_2", "LAMBDA_3", "LAMBDA_4",
    "LAMBDA_5", "LAMBDA_6", "LAMBDA_7", "LAMBDA_8",
    "su3_generator", "su3_wilson_phase", "su3_z3_center_holonomy",
    "wilson_loop_trace_1d", "FluxTubeReport", "flux_tube_report",
    "random_su3_holonomy_decay_rate", "su3_mobius_laplacian",
]
