"""Quantum extension of the Möbius temporal loop (paper §7, roadmap stub).

This module promotes the classical complex field of
:mod:`dinos.temporal_loop` to a density operator ρ(t) evolved by a
completely-positive trace-preserving (CPTP) map with the same prophetic
feedback and Möbius seam conditions.  QuTiP is *not* required — the core
implementation is pure NumPy, so that the dinos-DKN package keeps its
existing dependency footprint.  If QuTiP is installed it can be used
for downstream analysis (partial traces, entanglement entropy), but
nothing in this module imports it.

Physical picture (paper §7)
---------------------------
Replace ψ_f, ψ_b with density matrices ρ_f(t), ρ_b(t) on a D-dimensional
Hilbert space (D = 2 is the natural choice for a Dirac-spinor CTC mode).
The forward / backward evolutions are

    ρ_f(t + dt) = E_f[ ρ_f(t) ] = γ U(dt) ρ_f(t) U(dt)† + (1 − γ) ρ_target
    ρ_b(t − dt) = E_b[ ρ_b(t) ] = γ U(dt)† ρ_b(t) U(dt) + (1 − γ) ρ_target

where ``U(dt) = exp(−i H dt)`` embeds the temporal Möbius twist via
``H = (τ/2) σ_z`` (so U(T=2π/τ) = exp(−iπ σ_z) flips the spin — the
quantum image of the classical Z_2 twist).

Prophetic feedback (Deutsch-self-consistency generalisation):

    ρ_mix = (1 − α) ρ_f + α ρ_b

is the fixed-point equation solved by iteration.  When ρ_f = ρ_b the
feedback is inert — the system has reached a self-consistent CTC state.

Intended downstream uses (roadmap, paper §7.5):

  * Entanglement-entropy diagnostics across the temporal seam.
  * Dirac-field operator coupling via :mod:`dinos.closure`.
  * Symbolic Deutsch-fixed-point verification in :mod:`dinos.verify`.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from math import pi
from typing import Optional

import numpy as np


# -----------------------------------------------------------------------------
# Pauli matrices and utilities
# -----------------------------------------------------------------------------

SIGMA_X = np.array([[0.0, 1.0], [1.0, 0.0]], dtype=complex)
SIGMA_Y = np.array([[0.0, -1j], [1j, 0.0]], dtype=complex)
SIGMA_Z = np.array([[1.0, 0.0], [0.0, -1.0]], dtype=complex)
I2 = np.eye(2, dtype=complex)


def _twist_unitary(dt: float, tau: float = 1.0) -> np.ndarray:
    """U(dt) = exp(−i (τ/2) σ_z dt)  — temporal Möbius twist as a qubit gate.

    At dt = T = 2π/τ this returns exp(−iπ σ_z) = −I (up to phase),
    i.e. the ``Z_2`` antiperiodicity that parallels the Maslov μ_φ = 2
    correction in paper eq. 25.
    """
    phase = 0.5 * tau * dt
    return np.array(
        [[np.exp(-1j * phase), 0.0], [0.0, np.exp(1j * phase)]],
        dtype=complex,
    )


def _purity(rho: np.ndarray) -> float:
    """Tr(ρ²) — 1 for a pure state, 1/D for the maximally mixed state."""
    return float(np.real(np.trace(rho @ rho)))


def von_neumann_entropy(rho: np.ndarray, eps: float = 1e-15) -> float:
    """S(ρ) = −Tr(ρ log ρ).  Uses eigvalsh for Hermitian ρ.

    Numerically-noisy density matrices can have eigenvalues slightly
    outside [0, 1]; we clip to that interval before evaluating the
    log so that the returned entropy is always physically sensible.
    """
    w = np.linalg.eigvalsh(rho)
    w = np.clip(w, eps, 1.0)
    return float(-np.sum(w * np.log(w)))


# -----------------------------------------------------------------------------
# Quantum Möbius temporal loop
# -----------------------------------------------------------------------------

@dataclass
class QuantumMobiusLoop:
    """Quantum analog of :class:`dinos.temporal_loop.MobiusTemporalLoop`.

    Parameters:
        D: Hilbert-space dimension (default 2 = single Dirac-spinor CTC mode).
        T: total proper time around the temporal loop.
        K: number of time steps.
        alpha: prophetic-feedback strength in ρ_mix = (1−α)ρ_f + α ρ_b.
        tau: temporal-twist rate; H = (τ/2) σ_z for D=2.
        damping: γ per step; (1−γ) mixing toward ρ_target enforces the
            Higgs-wall boundary condition.
        rho_target: D×D density matrix that the loop relaxes toward.  If
            ``None``, defaults to a pure state ``|0⟩⟨0|``.
        seed: RNG seed for reproducibility.

    After :meth:`evolve` the trajectories are stored as shape-(K+1, D, D)
    arrays ``rho_f`` and ``rho_b``.
    """
    D: int = 2
    T: float = 2.0 * pi
    K: int = 64
    alpha: float = 0.7
    tau: float = 1.0
    damping: float = 0.99
    rho_target: Optional[np.ndarray] = None
    seed: int = 0

    rho_f: np.ndarray = field(init=False, repr=False)
    rho_b: np.ndarray = field(init=False, repr=False)
    history: list[float] = field(init=False, default_factory=list, repr=False)
    converged: bool = field(init=False, default=False)

    def __post_init__(self) -> None:
        if self.D != 2:
            # Non-qubit Hamiltonians are left as an exercise — τ·σ_z is the
            # minimal realisation of the Möbius twist.
            raise NotImplementedError("only D=2 supported in this stub")
        if not (0.0 < self.damping <= 1.0):
            raise ValueError("damping must be in (0, 1]")

        rng = np.random.default_rng(self.seed)
        if self.rho_target is None:
            self.rho_target = np.array([[1.0, 0.0], [0.0, 0.0]], dtype=complex)
        # Normalise and symmetrise in case a caller handed in something sloppy
        self.rho_target = 0.5 * (self.rho_target + self.rho_target.conj().T)
        tr = np.trace(self.rho_target).real
        if tr <= 0:
            raise ValueError("rho_target must have positive trace")
        self.rho_target /= tr

        # Initialise both trajectories near the target with a small Hermitian
        # perturbation; the self-consistency condition fixes them to agree at
        # t = 0 and t = T.
        pert = 1e-3 * (rng.standard_normal((self.D, self.D))
                       + 1j * rng.standard_normal((self.D, self.D)))
        pert = 0.5 * (pert + pert.conj().T)
        start = self.rho_target + pert
        start = start / np.trace(start).real
        self.rho_f = np.broadcast_to(start, (self.K + 1, self.D, self.D)).copy()
        self.rho_b = self.rho_f.copy()

    # ---- CPTP step --------------------------------------------------------

    def _cptp_forward(self, rho: np.ndarray, dt: float) -> np.ndarray:
        U = _twist_unitary(dt, self.tau)
        evolved = U @ rho @ U.conj().T
        return self.damping * evolved + (1.0 - self.damping) * self.rho_target

    def _cptp_backward(self, rho: np.ndarray, dt: float) -> np.ndarray:
        U = _twist_unitary(dt, self.tau).conj().T
        evolved = U @ rho @ U.conj().T
        return self.damping * evolved + (1.0 - self.damping) * self.rho_target

    # ---- Sweeps -----------------------------------------------------------

    def _forward_sweep(self) -> None:
        dt = self.T / self.K
        for k in range(self.K):
            self.rho_f[k + 1] = self._cptp_forward(self.rho_f[k], dt)

    def _backward_sweep(self) -> None:
        dt = self.T / self.K
        # Anchor the seam at t = T: ρ_b(T) = ρ_f(T)
        self.rho_b[self.K] = self.rho_f[self.K]
        for k in range(self.K, 0, -1):
            self.rho_b[k - 1] = self._cptp_backward(self.rho_b[k], dt)
        # Self-consistency anchor at t = 0
        self.rho_b[0] = self.rho_f[0]

    # ---- Divergence metric ------------------------------------------------

    def trace_distance(self, k: int | None = None) -> float:
        """½ ‖ρ_f − ρ_b‖₁  at time slice k (or averaged over k if None).

        This is the quantum analog of |ψ_f − ψ_b| from the classical
        module; it equals 0 iff ρ_f = ρ_b.
        """
        if k is None:
            return float(np.mean([self.trace_distance(j) for j in range(self.K + 1)]))
        diff = self.rho_f[k] - self.rho_b[k]
        w = np.linalg.eigvalsh(diff)
        return 0.5 * float(np.sum(np.abs(w)))

    # ---- Public API -------------------------------------------------------

    def evolve(self, max_iter: int = 200, epsilon: float = 1e-4) -> dict:
        """Alternate CPTP forward/backward sweeps with Picard symmetrisation.

        Convergence criterion: average trace distance < ε.
        """
        self.history = []
        self.converged = False
        it = 0
        for it in range(1, max_iter + 1):
            self._forward_sweep()
            self._backward_sweep()
            td = self.trace_distance()
            self.history.append(td)
            if td < epsilon:
                self.converged = True
                break
            mean = 0.5 * (self.rho_f + self.rho_b)
            self.rho_f = mean
            self.rho_b = mean.copy()
        return {
            "converged": self.converged,
            "iterations": it,
            "final_trace_distance": self.history[-1] if self.history else float("nan"),
            "history": list(self.history),
            "fixed_point_rho_0": self.rho_f[0].copy(),
            "entropy_at_t0": von_neumann_entropy(self.rho_f[0]),
            "purity_at_t0": _purity(self.rho_f[0]),
        }


__all__ = [
    "QuantumMobiusLoop",
    "SIGMA_X", "SIGMA_Y", "SIGMA_Z", "I2",
    "von_neumann_entropy",
]
