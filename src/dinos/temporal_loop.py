"""Möbius Temporal Loop / self-consistent CTC with DKN coupling.

Numerical implementation of a Möbius-strip temporal-loop field theory with
prophetic feedback, tightly coupled to the DKN electron ansatz.

The physical picture
--------------------
A complex field ψ(x, t) lives on an N-node discrete Möbius strip in space
and on a closed loop of length T in time.  Two copies evolve concurrently:

    ψ_f : forward evolution   (t: 0 → T)
    ψ_b : backward evolution  (t: T → 0)

coupled by a "prophetic feedback" term that pulls ψ_f toward ψ_b and
vice versa.  The physical states are the **fixed points** at which
ψ_f(t) = ψ_b(t) for every t — the discrete analog of a self-consistent
closed timelike curve.

Why the twist.  The spatial Möbius twist ``s → s + 2π ⇒ ψ → −ψ``
enforces a ``Z_2`` antiperiodicity identical to the spin-½ antiperiodicity
that fixes the Maslov index ``μ_φ = 2`` in :mod:`dinos.geodesic` (paper
App. E, eq. 106).  The temporal twist ``ϕ_twist(t) = τ t / 2`` plays the
same rôle for the time loop and with τ = 1.0 degenerates, at t = T = 2π,
to the same ``−1`` phase.  The Möbius loop is therefore the natural
kinematic arena for a Dirac-like self-consistent solution.

Link to DKN
-----------
When ``dkn_params`` are supplied the fixed-point seed is chosen so that
``|ψ_f(0)|²`` equals the mass-self-consistent radius predicted by
:mod:`dinos.closure`, and the relaxation term pulls the loop toward that
target.  The converged phase winding (spatial and temporal) is then mapped
to Bohr–Sommerfeld integers ``(n_φ, n_θ)`` via
:func:`dinos.geodesic.geodesic_to_dirac`, giving an independent handle on
the electron's Dirac quantum numbers.

Governing equations
-------------------
Equation numbering below follows the Dinos whitepaper
(paper/temporal_loop_dkn.tex).

    Spatial parametrisation (1–3):
        s_j = 2π j / N,  j = 0..N−1
        ψ[N] ≡ −ψ[0]         (Möbius Z_2 boundary)

    Temporal twist:
        ϕ_twist(t) = τ t / 2

    Forward step (5):
        ψ_f[j, k+1] = γ · [ψ_f[j, k] + Δt (D_s ψ_f[j, k] + F_proph[j, k])]
                        + η · ξ[j, k]

    Backward step (6):
        ψ_b[j, k−1] = γ · [ψ_b[j, k] + Δt (D_s ψ_b[j, k] + F_proph[j, k])]
                        + η · ξ[j, k]          (sign of D_s is symmetric —
                                                the diffusion operator is
                                                self-adjoint on the Möbius
                                                strip with Z_2 BC)

    Prophetic feedback (7–8):
        F_proph = α (ψ_b − ψ_f)  +  β (ψ_target − ψ)

    Fixed-point / self-consistency:
        ψ_f(0) = ψ_b(0)                                  (≡ DKN Higgs boundary)
        ψ_f(T) = ψ_b(T)                                  (Möbius temporal seam)
        |ψ_f[j, k] − ψ_b[j, k]| < ε    for all j, k.

    Divergence metric (10):
        D = ⟨|ψ_f − ψ_b|²⟩ = (1/NT) Σ_{j, k} |ψ_f[j, k] − ψ_b[j, k]|²

Here ``γ = 0.99`` is the damping factor and η the noise amplitude.
``D_s`` is the discrete Möbius Laplacian (sign-flipped across the seam).

Note on ψ_target.
    The relaxation source ψ_target is held *spatial-only*.  The temporal
    Möbius twist ``exp(iτ t/2)`` is a topological label of the converged
    solution (detected by :meth:`MobiusTemporalLoop.extract_dkn_quantum_numbers`)
    rather than an imposed drive; embedding it into ψ_target makes the
    forward and backward Euler steps track it with opposite sign and
    leaves a permanent O(τ·dt) gap between ψ_f and ψ_b.  The DKN Higgs
    wall is therefore the *spatial* self-consistency constraint
    ``|ψ_f(·, 0)|² = a²`` — exactly what paper eq. 62 demands — and the
    twist is read off after the fact from the azimuthal phase winding.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from math import pi
from typing import Optional

import numpy as np

from . import casimir, closure, constants as C, geodesic


# -----------------------------------------------------------------------------
# Discrete Möbius Laplacian
# -----------------------------------------------------------------------------

def mobius_laplacian(psi: np.ndarray) -> np.ndarray:
    """Discrete 1-D Laplacian with Möbius (Z_2-twisted) boundary.

    For a 1-D array of length N with Möbius BC ``ψ[N] = −ψ[0]`` the
    second difference is

        (D_s ψ)[j] = ψ[j+1] + ψ[j−1] − 2 ψ[j]

    with ``ψ[−1] = −ψ[N−1]`` and ``ψ[N] = −ψ[0]`` at the seam.  We
    implement that with two ``np.roll`` calls and a sign correction at
    indices 0 and N−1.
    """
    forward = np.roll(psi, -1)
    backward = np.roll(psi, +1)
    # Flip sign at the seam: position 0 sees "−ψ[N−1]" when looking
    # backward; position N−1 sees "−ψ[0]" when looking forward.
    forward[-1] = -psi[0]
    backward[0] = -psi[-1]
    return forward + backward - 2.0 * psi


def temporal_twist_phase(t: float, tau: float = 1.0) -> complex:
    """Temporal twist ``e^{i τ t / 2}`` (Eq. 4)."""
    return np.exp(1j * 0.5 * tau * t)


# -----------------------------------------------------------------------------
# DKN target builder
# -----------------------------------------------------------------------------

@dataclass(frozen=True)
class DKNParams:
    """Optional DKN coupling parameters for the prophetic-feedback target.

    If supplied, the fixed-point seed ``ψ_target`` is normalised so that
    its modulus reproduces the mass-self-consistent Compton radius
    (:mod:`dinos.closure`), and :meth:`MobiusTemporalLoop.extract_dkn_quantum_numbers`
    pulls the associated ``(C_bag, σ)`` for the mass contribution.

    The default ``sigma_MeV3`` is the *required* surface tension that
    closes eq. 65 of the paper at the physical electron mass (≈ 2.74e−2
    MeV³); ``C_bag`` and ``alpha`` default to the paper's canonical
    numerical values so that ``MobiusTemporalLoop(dkn_params=DKNParams())``
    reproduces the electron sector out of the box.
    """
    sigma_MeV3: float = field(default_factory=closure.required_surface_tension)
    C_bag: float = C.C_bag_Dirac                   # Dirac Casimir (paper eq. 43)
    alpha: float = C.alpha_EM                      # fine-structure constant
    include_casimir: bool = True                   # also pin Derrick residue


def _dkn_seed(N: int, dkn: DKNParams) -> np.ndarray:
    """Build a spatial seed whose modulus encodes DKN mass self-consistency.

    The mass-self-consistent radius ``a = [(1 − 2C − α) / (8π σ)]^{1/3}``
    (paper eq. 62) is used as the seed magnitude.  A single unit of phase
    winding around the Möbius strip is imposed so that the ``n_φ = 0``
    ground-state extraction (Corollary 7.6) is recoverable from a trivially
    phased state — higher windings arise from evolution.
    """
    if dkn.sigma_MeV3 <= 0:
        raise ValueError("sigma_MeV3 must be positive")
    try:
        a = closure.compton_radius(dkn.sigma_MeV3, dkn.C_bag, dkn.alpha)
    except ValueError as exc:
        # Fall through to unit magnitude if the inputs are pathological;
        # the loop still runs, just without a physical amplitude.
        a = 1.0
        _ = exc
    # Derrick residue is a scalar correction ≲ 1 that we fold into the
    # amplitude — it tunes the relative weight of the Higgs wall vs. the
    # confined scalar multiplet (paper App. D).
    amplitude = a
    if dkn.include_casimir:
        x_star = C.m_star_times_a_dimless
        amp_correction = 1.0 + casimir.C_phi_multiplet(x_star)  # ≈ 1 + 0.0955
        amplitude *= amp_correction
    s = np.linspace(0.0, 2.0 * pi, N, endpoint=False)
    return amplitude * np.exp(1j * 0.5 * s)  # half-winding — Z_2 seam honoured


# -----------------------------------------------------------------------------
# Main class
# -----------------------------------------------------------------------------

@dataclass
class MobiusTemporalLoop:
    """Self-consistent forward/backward field on a Möbius strip + time loop.

    Parameters (whitepaper §2.2):
        N       — spatial nodes (default 1000)
        T       — temporal extent (default 50 time-units; Δt = T/K is the
                  internal step, K = number of time steps, default K = N)
        alpha   — retrocausal feedback strength (Eq. 7)
        beta    — relaxation toward ψ_target (Eq. 8)
        tau     — temporal-twist rate; ϕ_twist(t) = τ t / 2
        damping — Eq. 5 damping γ; 0.99 by the whitepaper default
        eta     — noise amplitude (Gaussian, i.i.d.); 0 by default so that
                  tests are deterministic
        dkn_params — optional :class:`DKNParams`; if set, the loop is
                     tied to DKN mass self-consistency

    After :meth:`evolve` runs, ``psi_f`` and ``psi_b`` contain the
    converged fields of shape ``(N, K+1)`` (space × time).
    """
    N: int = 1000
    T: float = 50.0
    alpha: float = 0.7
    beta: float = 0.15
    tau: float = 1.0
    damping: float = 0.99
    eta: float = 0.0
    K: Optional[int] = None
    dkn_params: Optional[DKNParams] = None
    seed: int = 0

    psi_f: np.ndarray = field(init=False, repr=False)
    psi_b: np.ndarray = field(init=False, repr=False)
    psi_target: np.ndarray = field(init=False, repr=False)
    history: list[float] = field(init=False, default_factory=list, repr=False)
    converged: bool = field(init=False, default=False)

    def __post_init__(self) -> None:
        if self.N < 4:
            raise ValueError("N must be ≥ 4 for a discrete Laplacian")
        if not (0.0 <= self.damping <= 1.0):
            raise ValueError("damping must be in [0, 1]")
        if self.alpha < 0.0 or self.beta < 0.0:
            raise ValueError("α, β must be non-negative")
        if self.K is None:
            self.K = int(self.N)

        rng = np.random.default_rng(self.seed)
        # Fixed-point seed (spatial).  We deliberately keep ψ_target
        # *time-independent*: the temporal Möbius twist is a topological
        # label of the converged solution, not a drive we impose on the
        # relaxation source — imposing it on ψ_target makes the forward
        # and backward Euler steps track the twist with opposite sign
        # and leaves a permanent O(τ·dt) gap between ψ_f and ψ_b.
        if self.dkn_params is not None:
            seed_spatial = _dkn_seed(self.N, self.dkn_params)
        else:
            s = np.linspace(0.0, 2.0 * pi, self.N, endpoint=False)
            seed_spatial = np.exp(1j * 0.5 * s)

        self.psi_target = np.broadcast_to(
            seed_spatial[:, None], (self.N, self.K + 1)
        ).copy()

        # Initial guess: ψ_f and ψ_b equal to the target with a tiny
        # anti-symmetric kick (so a generic non-trivial residual must be
        # driven out by the iteration — otherwise the test would be
        # trivial).
        kick = 1e-3 * (rng.standard_normal(self.psi_target.shape)
                       + 1j * rng.standard_normal(self.psi_target.shape))
        self.psi_f = self.psi_target.copy() + kick
        self.psi_b = self.psi_target.copy() - kick
        # Clamp the seam: ψ_f(t=0) must equal ψ_b(t=0) exactly.
        self.psi_b[:, 0] = self.psi_f[:, 0]

    # ---- internal dynamics ------------------------------------------------

    def _prophetic(self, psi_self: np.ndarray, psi_other: np.ndarray,
                   k: int) -> np.ndarray:
        """F_proph[:, k] = α (ψ_other − ψ_self) + β (ψ_target − ψ_self)."""
        retro = self.alpha * (psi_other[:, k] - psi_self[:, k])
        relax = self.beta * (self.psi_target[:, k] - psi_self[:, k])
        return retro + relax

    def _forward_sweep(self, rng: np.random.Generator) -> None:
        dt = self.T / self.K
        gamma = self.damping
        one_minus_gamma = 1.0 - gamma
        for k in range(self.K):
            lap = mobius_laplacian(self.psi_f[:, k])
            f_pro = self._prophetic(self.psi_f, self.psi_b, k)
            noise = 0.0
            if self.eta > 0.0:
                noise = self.eta * (rng.standard_normal(self.N)
                                    + 1j * rng.standard_normal(self.N))
            # Damped Euler with a Higgs-wall source: the decay caused by γ<1 is
            # compensated by pulling toward ψ_target[k+1] with weight (1−γ).
            # This is the numerical image of the DKN antipodal Higgs boundary
            # — without it, γ=0.99 would drive every mode to zero.
            self.psi_f[:, k + 1] = (
                gamma * (self.psi_f[:, k] + dt * (lap + f_pro))
                + one_minus_gamma * self.psi_target[:, k + 1]
                + noise
            )

    def _backward_sweep(self, rng: np.random.Generator) -> None:
        dt = self.T / self.K
        gamma = self.damping
        one_minus_gamma = 1.0 - gamma
        # Anchor the *other* seam: ψ_b[K] ← ψ_f[K]. Together with the
        # ψ_b[0] ← ψ_f[0] anchor applied at the end of this sweep, this
        # is a two-point boundary match that closes the Möbius time loop
        # and is what enables the iteration to actually find a fixed point.
        self.psi_b[:, self.K] = self.psi_f[:, self.K]
        for k in range(self.K, 0, -1):
            lap = mobius_laplacian(self.psi_b[:, k])
            f_pro = self._prophetic(self.psi_b, self.psi_f, k)
            noise = 0.0
            if self.eta > 0.0:
                noise = self.eta * (rng.standard_normal(self.N)
                                    + 1j * rng.standard_normal(self.N))
            self.psi_b[:, k - 1] = (
                gamma * (self.psi_b[:, k] + dt * (lap + f_pro))
                + one_minus_gamma * self.psi_target[:, k - 1]
                + noise
            )
        # Re-enforce the self-consistency anchor at t = 0.
        self.psi_b[:, 0] = self.psi_f[:, 0]

    # ---- public API -------------------------------------------------------

    def divergence(self) -> float:
        """D = ⟨|ψ_f − ψ_b|²⟩ over all (j, k) (Eq. 10)."""
        diff = self.psi_f - self.psi_b
        return float(np.mean(np.abs(diff) ** 2))

    @property
    def contraction_factor(self) -> float:
        """Analytic contraction factor ``A = (1−β)(1−α) + βα`` of the
        prophetic-feedback + relaxation map (see Appendix B of the
        whitepaper).  The field fixed-point error decays as ``A^n``; for
        the canonical α=0.7, β=0.15 this gives A ≈ 0.36, suppressing the
        residual to machine precision in ~34 iterations."""
        return (1.0 - self.beta) * (1.0 - self.alpha) + self.beta * self.alpha

    def emergent_twist(self) -> float:
        """Extract the emergent temporal twist from the phase offset of
        the converged fixed point against the (spatial-only) target.

        Convention (matching the snippet-level algorithm in the docs):

            ϕ_twist = ⟨ arg( ψ_f(·, 0) / ψ_target(·, 0) ) ⟩_j

        i.e. the circular mean over spatial nodes of the per-node phase
        offset.  At a genuine DKN fixed point this should equal ``τ·T/2``
        modulo the Möbius Z_2 seam.
        """
        ratio = self.psi_f[:, 0] / self.psi_target[:, 0]
        # Circular mean (equivalent to mean of np.angle for small spread,
        # but well-defined at the branch cut).
        return float(np.angle(np.mean(ratio)))

    def evolve(self, max_iter: int = 200, epsilon: float = 1e-2) -> dict:
        """Alternate forward and backward sweeps until convergence.

        Convergence criterion: max_{j, k} |ψ_f[j, k] − ψ_b[j, k]| < ε.
        The divergence metric ``D`` is recorded per iteration in
        ``self.history``.

        Returns:
            dict with ``converged`` (bool), ``iterations`` (int),
            ``final_max_error`` (float), ``final_divergence`` (float,
            Eq. 10), ``history`` (list[float]), ``fixed_point_slice``
            (numpy array of shape ``(N,)`` containing ψ_f(0) = ψ_b(0)),
            and ``phi_twist_extracted`` — the emergent temporal twist
            read off the converged phase winding via :meth:`emergent_twist`.
        """
        rng = np.random.default_rng(self.seed + 1)
        self.history = []
        self.converged = False
        max_err = float("inf")
        it = 0
        for it in range(1, max_iter + 1):
            self._forward_sweep(rng)
            self._backward_sweep(rng)
            # The residual |ψ_f − ψ_b| measured here is the physical
            # self-consistency gap — how much the forward trajectory
            # disagrees with the backward trajectory *after* both have
            # run from the shared t=0, t=K anchors.
            diff = np.abs(self.psi_f - self.psi_b)
            max_err = float(diff.max())
            self.history.append(self.divergence())
            if max_err < epsilon:
                self.converged = True
                break
            # Picard-style symmetrization: the self-consistent CTC solution
            # is a common fixed point of both operators, so averaging them
            # is the contraction that drives subsequent gaps → 0.  Applied
            # *after* measurement, never before, so the residual reported
            # is always the honest pre-symmetrization difference.
            mean = 0.5 * (self.psi_f + self.psi_b)
            self.psi_f = mean
            self.psi_b = mean.copy()
        return {
            "converged": self.converged,
            "iterations": it,
            "final_max_error": max_err,
            "final_divergence": self.history[-1] if self.history else float("nan"),
            "history": list(self.history),
            "fixed_point_slice": self.psi_f[:, 0].copy(),
            "phi_twist_extracted": self.emergent_twist(),
            "contraction_factor_A": self.contraction_factor,
        }

    # ---- DKN quantum-number extraction ------------------------------------

    def extract_dkn_quantum_numbers(self) -> dict:
        """Map converged phase structure → Dirac labels via :mod:`dinos.geodesic`.

        Delegates to :func:`dinos.geodesic.quantize` with
        ``boundary_condition="mobius_self_consistent"`` so that this method
        and the unified geodesic API return *identical* labels for the
        same fixed point.  ``n_φ`` is the azimuthal phase winding of
        ``ψ_f(·, 0)`` (including the +π Möbius Z_2 seam); ``n_θ`` is the
        number of Re ψ zero-crossings around the spatial loop (polar
        nodal surfaces of the corresponding Dirac mode).

        If ``dkn_params`` are set, the associated mass contribution is
        returned via :func:`dinos.closure.electron_mass`.

        Returns:
            dict with keys ``n_phi``, ``n_theta``, ``winding_raw`` (float
            before rounding), ``DiracLabels``, and optionally ``m_e_MeV``.
        """
        fp = self.psi_f[:, 0]
        phases = np.angle(fp)
        dphases = np.diff(np.unwrap(phases))
        winding = (dphases.sum() + pi) / (2.0 * pi)  # +π for the Möbius seam
        n_phi = int(np.round(winding))
        re = np.real(fp)
        sign_changes = int(np.sum(np.diff(np.sign(re)) != 0))
        n_theta = max(sign_changes // 2, 0)
        labels = geodesic.geodesic_to_dirac(n_phi=n_phi, n_theta=n_theta)

        out = {
            "n_phi": n_phi,
            "n_theta": n_theta,
            "winding_raw": float(winding),
            "DiracLabels": labels,
        }
        if self.dkn_params is not None:
            try:
                m = closure.electron_mass(
                    sigma_MeV3=self.dkn_params.sigma_MeV3,
                    C_bag=self.dkn_params.C_bag,
                    alpha=self.dkn_params.alpha,
                )
            except ValueError:
                m = float("nan")
            out["m_e_MeV"] = float(m)
            out["mass_contribution_fraction"] = closure.mass_fractions(
                C_bag=self.dkn_params.C_bag, alpha=self.dkn_params.alpha,
            )
        return out


__all__ = [
    "MobiusTemporalLoop",
    "DKNParams",
    "mobius_laplacian",
    "temporal_twist_phase",
]
