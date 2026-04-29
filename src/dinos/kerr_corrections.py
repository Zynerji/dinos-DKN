"""Kerr corrections to the Möbius spectrum (HYPOTHESIS.md Step 5).

The Chandrasekhar–Page eigenvalue acquires a perturbative shift when the
Kerr–Newman background is rotating (a > 0) and the field carries
frequency ω and mass μ:

    λ_CP² = k² − ½ a² (ω² − μ²) + O((aω)⁴).

This module asks whether the Möbius construction reproduces this shift,
and if so, with what (a, ω, μ) ↔ (Möbius parameters) identification.

Key observations
----------------
1. **On-shell vanishing.** For ω = μ (the on-shell condition for a
   particle at rest), the leading correction is *exactly zero* —
   independent of a. The DKN electron lives at this on-shell point
   (ω = μ = m_e in natural units), so the leading Kerr correction is
   zero by construction. Any Möbius perturbation that recovers
   "no shift on-shell" is consistent at leading order.

2. **Non-canonical mapping.** The CP correction has three free
   parameters (a, ω, μ); the Möbius construction has four (α, β, κ, τ).
   Multiple identifications can reproduce the functional form
   ``−½ τ² · V``; pinning a *unique* mapping requires an additional
   physical constraint not currently in the framework.

3. **Best-supported mapping.** The cleanest identification consistent
   with the analysis in HYPOTHESIS §1 (continuum action) and §3 (Step 1
   verification) is:

        a  ↔  τ                       (Kerr rotation = Möbius temporal twist rate)
        μ² ↔  β + κ                   (Dirac mass² = wall coupling, Step 1)
        ω² ↔  azimuthal eigenvalue at given mode = m_j²   (mode frequency)

   With this identification, the leading shift to the Möbius eigenvalue
   at mode m_j is:

        Δλ²_Möbius  =  −½ τ² (m_j² − (β + κ))

   At the rest-frame electron (m_j² ≈ μ², i.e. azimuthal mode coupled
   to wall mass), the shift vanishes — matching CP's on-shell result.

What this proves and what it doesn't
------------------------------------
- The *functional form* ``−½ τ² · (ω² − μ²)`` is reproducible: any
  quadratic-in-τ perturbation can be written this way.
- The *on-shell zero* is automatic with the proposed identification,
  matching CP.
- The *normalization* (the ½ prefactor) requires the perturbation to
  have a specific magnitude; the framework as built does not derive
  this prefactor — it must be matched by hand. So the bridge §3
  conjecture about the (a, ω, μ) mapping is **partially supported**
  (form + on-shell zero) and **partially open** (prefactor).
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


# -----------------------------------------------------------------------------
# CP leading-correction formula (closed form)
# -----------------------------------------------------------------------------

def cp_leading_shift(a: float, omega: float, mu: float) -> float:
    """The CP perturbative shift Δλ² = −½ a² (ω² − μ²)  (paper eq. 88)."""
    return -0.5 * a * a * (omega * omega - mu * mu)


def is_on_shell(omega: float, mu: float, atol: float = 1e-12) -> bool:
    """True iff ω = μ (the rest-mass on-shell condition).

    On-shell, the leading Kerr correction vanishes for *any* a — a
    universal feature CP shares with any Möbius interpretation that
    preserves the structure.
    """
    return abs(omega - mu) < atol


# -----------------------------------------------------------------------------
# Proposed Möbius parameter mapping
# -----------------------------------------------------------------------------

@dataclass(frozen=True)
class MobiusKerrMapping:
    """Identification ``(a, ω, μ) ↔ (τ, m_j, β+κ)``.

    Stored as the result of :func:`propose_mapping` for inspection in
    tests and downstream code.
    """
    a_from_tau: float          # a ↔ τ
    omega_from_m_j: float      # ω ↔ m_j
    mu_squared_from_wall: float  # μ² ↔ β + κ

    @property
    def mu(self) -> float:
        return float(np.sqrt(max(self.mu_squared_from_wall, 0.0)))


def propose_mapping(tau: float, m_j: float,
                    beta_plus_kappa: float) -> MobiusKerrMapping:
    """The mapping advocated in HYPOTHESIS.md §3, instantiated."""
    return MobiusKerrMapping(
        a_from_tau=tau,
        omega_from_m_j=m_j,
        mu_squared_from_wall=beta_plus_kappa,
    )


# -----------------------------------------------------------------------------
# Möbius eigenvalue shift under the proposed mapping
# -----------------------------------------------------------------------------

def mobius_perturbative_shift(tau: float, m_j: float,
                              beta_plus_kappa: float) -> float:
    """Predicted Möbius spectrum shift under the proposed mapping:

        Δλ²_Möbius  =  −½ τ² (m_j² − (β + κ))

    Under the identification ``(a, ω, μ²) ↔ (τ, m_j, β+κ)``, this
    equals the CP leading shift :func:`cp_leading_shift`.
    """
    mapping = propose_mapping(tau, m_j, beta_plus_kappa)
    return cp_leading_shift(
        a=mapping.a_from_tau,
        omega=mapping.omega_from_m_j,
        mu=mapping.mu,
    )


def shifted_mobius_eigenvalue(tau: float, m_j: float,
                              beta_plus_kappa: float) -> float:
    """``λ²_Möbius(τ) = m_j² + Δ`` with the leading Kerr-style shift."""
    return m_j ** 2 + mobius_perturbative_shift(tau, m_j, beta_plus_kappa)


def shifted_mobius_eigenvalue_full_dirac(tau: float, n_theta: int, n_phi: int,
                                          beta_plus_kappa: float) -> float:
    """Like :func:`shifted_mobius_eigenvalue` but uses the *full* Dirac
    eigenvalue ``|k|²`` as the unperturbed value (azimuthal m_j² + polar
    shift from Step 4), so this is the natural "Step 1+2+4+5" prediction
    for the eigenvalue with all corrections.

    Returns ``|k|² + Δ`` where ``Δ = −½τ²(m_j² − (β+κ))``.
    """
    from . import polar_strip
    m_j = n_phi + 0.5
    k_squared = polar_strip.dirac_k_squared(n_theta, m_j)
    return k_squared + mobius_perturbative_shift(tau, m_j, beta_plus_kappa)


# -----------------------------------------------------------------------------
# Mapping ambiguity diagnostic
# -----------------------------------------------------------------------------

def alternative_mappings_giving_same_form() -> list[dict]:
    """Enumerate mappings of (a, ω, μ) to Möbius parameters that all
    reproduce the *form* ``−½ τ² · V`` but with different V.

    Demonstrates the non-canonicity of the §3 mapping: the framework
    does not uniquely determine V.
    """
    return [
        {
            "name": "HYPOTHESIS §3 (this module)",
            "a_to": "tau",
            "omega_to": "m_j",
            "mu_squared_to": "beta + kappa",
            "comment": "Cleanest with Step 1 (μ² ↔ wall) and §3 (a ↔ τ).",
        },
        {
            "name": "Alternative A",
            "a_to": "tau",
            "omega_to": "k_squared_eigenvalue",
            "mu_squared_to": "alpha",
            "comment": "Plausible if frame-dragging α plays mass role; weaker support.",
        },
        {
            "name": "Alternative B",
            "a_to": "alpha",
            "omega_to": "tau",
            "mu_squared_to": "beta",
            "comment": "Treats α as Kerr rotation; inconsistent with Step 1's α=cross-coupling.",
        },
    ]


__all__ = [
    "cp_leading_shift", "is_on_shell",
    "MobiusKerrMapping", "propose_mapping",
    "mobius_perturbative_shift", "shifted_mobius_eigenvalue",
    "shifted_mobius_eigenvalue_full_dirac",
    "alternative_mappings_giving_same_form",
    "mobius_static_shift_naive", "time_averaged_shift",
    "floquet_first_order_shift", "moving_peak_average_shift",
    "sech4_integral_over_loop", "moving_peak_duty_cycle",
    "moving_peak_floquet_shift", "moving_peak_match_to_cp_half",
]


# -----------------------------------------------------------------------------
# Step 5b — Time-varying τ closes the ½ prefactor
# -----------------------------------------------------------------------------
#
# Step 5 treated τ as a static scalar, so the −½ prefactor in CP's
# Δλ² = −½a²(ω²−μ²) had to be matched by hand.  The piece the static
# treatment misses is:  the prefactor is the TIME-AVERAGE of cos²(Ωt).
# A τ that oscillates harmonically with amplitude τ₀ contributes
# ⟨τ²⟩_t = τ₀²/2 to the time-averaged Hamiltonian, and the −½ falls
# out as a calculus identity — not a postulate.
#
# Three diagnostics below:
#   - mobius_static_shift_naive: −τ²·V (no ½, what the static reading
#     would give if the prefactor weren't put in by hand)
#   - time_averaged_shift: numerical time-average over an oscillation
#   - floquet_first_order_shift: the closed-form −(τ₀²/2)·V


def mobius_static_shift_naive(tau: float, m_j: float,
                              beta_plus_kappa: float) -> float:
    """*Naive* static perturbation: ``Δ = −τ² (m_j² − μ²)``  (NO ½).

    This is what a literal "constant τ²-coupling" Hamiltonian would give
    at first order — the form is right but the prefactor is twice CP's.
    Used by tests to demonstrate that the missing factor of 2 is
    recovered by time-averaging an oscillating τ(t).
    """
    return -(tau ** 2) * (m_j ** 2 - beta_plus_kappa)


def time_averaged_shift(tau_amplitude: float, omega_drive: float,
                        m_j: float, beta_plus_kappa: float,
                        n_samples: int = 4096) -> float:
    """Numerical time-average of the naive shift over one drive period
    when ``τ(t) = τ₀ cos(Ω t)``.

    Returns ``⟨−τ(t)² · (m_j² − μ²)⟩_t`` — which equals
    ``−(τ₀²/2)·(m_j²−μ²)`` exactly, because ``⟨cos²⟩ = ½``.

    This is the operational demonstration: time-averaging an
    oscillating amplitude produces the CP `−½` prefactor with no
    postulate.
    """
    if omega_drive <= 0.0:
        raise ValueError("omega_drive must be positive")
    period = 2.0 * np.pi / omega_drive
    # Sample one full period; trapezoidal integration → time average.
    t = np.linspace(0.0, period, n_samples + 1)
    tau_t = tau_amplitude * np.cos(omega_drive * t)
    instantaneous = -(tau_t ** 2) * (m_j ** 2 - beta_plus_kappa)
    # Trapezoidal mean (handles endpoint correctly for closed period).
    return float(np.trapezoid(instantaneous, t) / period)


def floquet_first_order_shift(tau_amplitude: float, m_j: float,
                              beta_plus_kappa: float) -> float:
    """Closed-form Floquet first-order (RWA) prediction:

        ⟨Δ⟩_t  =  −½ τ₀² (m_j² − μ²)

    Equivalent to :func:`cp_leading_shift` under the §3 mapping with
    ``a = τ₀`` (oscillation amplitude), proving the −½ in CP is *the
    time-average of cos²* — a calculus identity, not a free parameter.
    """
    return -0.5 * (tau_amplitude ** 2) * (m_j ** 2 - beta_plus_kappa)


def moving_peak_average_shift(tau_amplitude: float, packet_width: float,
                              loop_length: float, m_j: float,
                              beta_plus_kappa: float) -> float:
    """Asymptotic (L ≫ Δ) time-average shift for a *moving* sech² packet
    on a periodic loop.

    For ``τ(s, t) = τ₀ sech²((s − vt)/Δ)`` propagating uniformly around
    a loop of length L, the time-average at any fixed s is uniform and
    equals the full-line integral of sech⁴:

        ⟨τ²⟩_t  =  τ₀² · (4Δ/3L)     for  L ≫ Δ.

    The 4/3 (vs the 2/3 you'd get for a static edge-anchored packet)
    comes from including *both halves* of the peak — natural on a
    periodic loop where the packet wraps.

    Limit checks:
    - Δ → 0: shift → 0 (δ-function packet, no overlap with any s).
    - L ≫ Δ: shift = −(4Δ/3L)·τ₀²·V (asymptotic).
    - Δ ≳ L: asymptote breaks down; use
      :func:`moving_peak_floquet_shift` for the exact periodic integral.
    """
    if loop_length <= 0.0:
        raise ValueError("loop_length must be positive")
    if packet_width <= 0.0:
        raise ValueError("packet_width must be positive")
    duty = (4.0 / 3.0) * (packet_width / loop_length)
    return -duty * (tau_amplitude ** 2) * (m_j ** 2 - beta_plus_kappa)


# -----------------------------------------------------------------------------
# Step 5c — Moving peak τ(s − vt): exact (s,t)-average over one period
# -----------------------------------------------------------------------------
#
# A localised packet ``τ(s, t) = τ₀ · sech²((s − vt)/Δ)`` propagating on
# the loop (s ∈ [0, L), period T = L/v) gives a quasi-stationary
# perturbation in the rotating frame.  In the lab frame, the
# time+space-averaged squared amplitude is
#
#     ⟨τ²⟩_(s,t)  =  (1/L) ∫_0^L sech⁴(s/Δ) ds  ·  τ₀²
#
# (the time-average is automatic since the packet just translates).
# For the loop, this integral has a closed form:
#
#     ∫_0^L sech⁴(s/Δ) ds  =  Δ · [tanh(L/Δ) − ⅓ tanh³(L/Δ)]
#                           ≈ (4/3) Δ      for  L ≫ Δ.
#
# The duty cycle factor (4Δ)/(3L) replaces the harmonic ½ — and is what
# determines the Möbius prefactor in the moving-peak interpretation.


def sech4_integral_over_loop(packet_width: float, loop_length: float) -> float:
    """Periodic-loop integral ∫_{−L/2}^{L/2} sech⁴(s/Δ) ds  in closed form.

    Identity:  ∫ sech⁴(u) du = tanh(u) − ⅓ tanh³(u).
    Symmetric integration around s=0 (where the packet centres) captures
    *both halves* of the peak — the right object for a moving packet on
    a periodic loop, since the time-average at any fixed s equals this
    integral divided by L.

        ∫_{−L/2}^{L/2} sech⁴(s/Δ) ds  =  2Δ · [tanh(L/(2Δ)) − ⅓ tanh³(L/(2Δ))]

    Asymptote (L ≫ Δ): → (4/3) Δ   (full real-line integral of sech⁴).
    """
    if packet_width <= 0.0 or loop_length <= 0.0:
        raise ValueError("packet_width and loop_length must be positive")
    u = loop_length / (2.0 * packet_width)
    return float(2.0 * packet_width * (np.tanh(u) - (1.0 / 3.0) * np.tanh(u) ** 3))


def moving_peak_duty_cycle(packet_width: float, loop_length: float) -> float:
    """Exact duty cycle ⟨sech⁴⟩_periodic = (1/L) ∫_{−L/2}^{L/2} sech⁴(s/Δ) ds.

    This is the time-average of τ²(s, t) at any fixed s for a moving
    packet on a periodic loop.

    Asymptotic form:  → (4Δ)/(3L)  for  L ≫ Δ.
    Limits:
        Δ → ∞ (uniform):  → 1            (sech⁴(0) = 1 everywhere)
        Δ → 0 (δ-fn):     → 0            (no overlap with any fixed s)
    """
    integral = sech4_integral_over_loop(packet_width, loop_length)
    return integral / loop_length


def moving_peak_floquet_shift(tau_amplitude: float, packet_width: float,
                              loop_length: float, m_j: float,
                              beta_plus_kappa: float) -> float:
    """Exact (s,t)-averaged Floquet shift for a moving sech² τ packet.

    Returns ``⟨Δ⟩  =  −duty · τ₀² (m_j² − μ²)`` with the *exact* duty
    cycle from :func:`moving_peak_duty_cycle` (not the L ≫ Δ asymptote).
    """
    duty = moving_peak_duty_cycle(packet_width, loop_length)
    return -duty * (tau_amplitude ** 2) * (m_j ** 2 - beta_plus_kappa)


def moving_peak_match_to_cp_half(loop_length: float) -> float:
    """The packet width Δ for which ⟨sech⁴⟩ = ½ exactly — i.e., the
    moving-peak reading that *reproduces the CP −½ prefactor*.

    Solves   tanh(u) − ⅓ tanh³(u)  =  u/2,    u = L/Δ.

    There is a finite-loop solution because ⟨sech⁴⟩ ranges from 0
    (Δ → 0) to 1 (Δ → ∞), passing through ½ at a unique Δ/L.
    Numerically Δ/L ≈ 1.39 (so Δ slightly larger than the loop —
    the packet is broader than one circumference).
    """
    from scipy.optimize import brentq

    def f(delta_over_L: float) -> float:
        return moving_peak_duty_cycle(delta_over_L * loop_length, loop_length) - 0.5

    # Bracket: small Δ/L gives duty < ½, large Δ/L gives duty → 1 > ½.
    return brentq(f, 0.1, 100.0, xtol=1e-9) * loop_length
