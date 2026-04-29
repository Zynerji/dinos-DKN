"""Z2 x Z3 x n_gen multi-cover Möbius scaffold (HYPOTHESIS Step 40).

Honest scope
------------
This module DOES:
  - Define a tensor-product Hilbert space with Z2 (fermionic seam),
    Z3 (color cover, from `mobius_z3_cover`) and an integer winding
    n_gen ∈ {0, 1, 2, ...}
  - Build a discrete Laplacian on the multi-cover (1D azimuthal) with
    explicit Z2 sign-flip and Z3 phase at the seam, parameterised by
    a per-generation winding number.
  - Compute the eigenvalue spectrum and identify the lowest-energy
    state per (n_fermion, n_color, n_gen) triple.

This module DOES NOT:
  - Derive the fermion mass tower (e, μ, τ) from the cover windings.
    The contraction-factor argument A^n that Grok proposed is shown
    to be tunable in `cover_hierarchy.py`; it is not a derivation.
  - Predict CKM/PMNS angles from the multi-cover wavefunctions.
    Overlap integrals are computed in `ckm_overlaps.py`/`pmns_overlaps.py`
    given an *explicit* polar-mode ansatz, but the ansatz is an input
    not an output.
  - Reproduce the SM gauge structure SU(3)×SU(2)×U(1) — the multi-cover
    has Z3 (a discrete subgroup of SU(3)) and Z2 (discrete fermion
    parity), not the full continuous gauge group.

This is a working scaffold for further investigation, not a derivation.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import pi

import numpy as np


@dataclass(frozen=True)
class MultiCoverParams:
    N: int = 64               # azimuthal nodes
    n_gen: int = 3            # number of generation windings
    z2_sign: int = -1         # ±1 (fermionic = -1, bosonic = +1)
    z3_phase_unit: complex = complex(1.0)   # set externally if needed


@dataclass(frozen=True)
class MultiCoverSpectrum:
    n_fermion_label: int      # 0 = bosonic, 1 = fermionic
    n_color_label: int        # 0, 1, 2 (Z3 winding)
    n_gen_label: int          # 0, 1, 2, ...
    lowest_eigenvalue: float
    notes: str


def z3_phase(n_color: int) -> complex:
    """Z3 monodromy phase: omega^n where omega = exp(2 pi i / 3)."""
    omega = np.exp(2j * pi / 3)
    return complex(omega ** (n_color % 3))


def multi_cover_seam_factor(n_fermion: int, n_color: int,
                             n_gen: int) -> complex:
    """Combined seam phase for a (Z2, Z3, gen-winding) sector.

    Z2 sector:    psi -> sign * psi    where sign = (-1)^n_fermion
    Z3 sector:    psi -> omega^n_color * psi
    gen winding:  psi -> exp(2 pi i n_gen / N) accumulates per node
                  (encoded later in the discrete Laplacian, not the seam)
    """
    z2 = (-1) ** (n_fermion % 2)
    z3 = z3_phase(n_color)
    return complex(z2) * z3


def multi_cover_laplacian(params: MultiCoverParams,
                           n_fermion: int, n_color: int,
                           n_gen: int) -> np.ndarray:
    """Discrete 1D Laplacian on N nodes with combined seam factor and
    per-step gen-winding phase.

    The gen-winding manifests as a per-step phase e^(i k_gen) where
    k_gen = 2 pi n_gen / N is the analog of a quantised azimuthal momentum.
    """
    N = params.N
    if N < 4:
        raise ValueError("N >= 4 required")
    seam = multi_cover_seam_factor(n_fermion, n_color, n_gen)
    k_gen = 2.0 * pi * n_gen / N
    step_phase = np.exp(1j * k_gen)

    L = np.zeros((N, N), dtype=complex)
    for j in range(N):
        L[j, j] = -2.0
        j_next = (j + 1) % N
        block_fwd = step_phase * (seam if j == N - 1 else 1.0)
        L[j, j_next] += block_fwd
        j_prev = (j - 1) % N
        block_back = np.conj(step_phase) * (np.conj(seam) if j == 0 else 1.0)
        L[j, j_prev] += block_back
    return -0.5 * (L + L.conj().T)


def multi_cover_spectrum(params: MultiCoverParams,
                          n_fermion: int, n_color: int,
                          n_gen: int) -> MultiCoverSpectrum:
    L = multi_cover_laplacian(params, n_fermion, n_color, n_gen)
    eigs = np.linalg.eigvalsh(L)
    return MultiCoverSpectrum(
        n_fermion_label=n_fermion,
        n_color_label=n_color,
        n_gen_label=n_gen,
        lowest_eigenvalue=float(eigs[0]),
        notes=("Lowest eigenvalue of the discrete Laplacian on the "
               "Z2 x Z3 x gen-winding multi-cover. Not a physical "
               "mass; just the spectral floor for this sector."),
    )


def scan_generations(params: MultiCoverParams) -> list[MultiCoverSpectrum]:
    """Scan all (n_fermion, n_color, n_gen) sectors up to params.n_gen."""
    out: list[MultiCoverSpectrum] = []
    for nf in (0, 1):
        for nc in (0, 1, 2):
            for ng in range(params.n_gen):
                out.append(multi_cover_spectrum(params, nf, nc, ng))
    return out


__all__ = [
    "MultiCoverParams", "MultiCoverSpectrum",
    "z3_phase", "multi_cover_seam_factor",
    "multi_cover_laplacian", "multi_cover_spectrum", "scan_generations",
]
