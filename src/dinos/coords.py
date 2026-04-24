"""Cylindrical / oblate-spheroidal coordinate transformations for Kerr–Newman.

Boyer–Lindquist (BL) coordinates ``(r, θ, φ)`` map onto oblate-spheroidal
cylindrical coordinates ``(ρ, z, φ)`` via the *oblate* relation

    ρ = √(r² + a²) · sin θ
    z = r · cos θ
    φ = φ                                                          (eqs. 1–2)

The inverse is the standard oblate-spheroidal root (taking the ``+`` branch
so that ``r ≥ 0``):

    r² = ½[ (ρ² + z² − a²) + √((ρ² + z² − a²)² + 4 a² z²) ]
    cos θ = z / r                                                   (eq. 3)

The Kerr–Newman line element in BL coordinates (paper §2)

    ds² = −(Δ − a² sin²θ)/Σ · dt²
          − 2 a sin²θ (r² + a² − Δ)/Σ · dt dφ
          + Σ/Δ · dr² + Σ · dθ²
          + sin²θ · [(r² + a²)² − Δ a² sin²θ]/Σ · dφ²

is expressed here through its raw components.  The cylindrical helpers
evaluate them at an arbitrary ``(ρ, z, φ)`` by round-tripping through BL.

Over-rotating (``a > M``) visualisations emphasise the *naked* ergoregion
that characterises the DKN electron: the outer stationary-limit surface

    r_E⁺(θ) = M + √(M² − Q² − a² cos²θ)

becomes complex for polar angles where ``a² cos²θ > M² − Q²``, which for
``a > M`` includes all but an equatorial band.  The vortex frame-dragging
term ``g_{tφ}`` is therefore the physically meaningful "handle" on the
cylindrical picture, and is returned by :func:`cylindrical_kerr_metric_components`
along with every other metric component.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import pi
from typing import Optional

import numpy as np

from . import constants as C


# -----------------------------------------------------------------------------
# BL ↔ oblate-spheroidal-cylindrical
# -----------------------------------------------------------------------------

def boyer_lindquist_to_cylindrical(r, theta, a: float, M: float = 0.0):
    """Map BL ``(r, θ)`` → cylindrical ``(ρ, z, φ)``.

    The ``M`` argument is accepted for API symmetry with the metric helpers
    but does not enter the coordinate map itself (oblate-spheroidal surfaces
    are a property of ``a`` alone).

    Args:
        r: BL radial coordinate; scalar or array.
        theta: BL polar angle in radians; scalar or array (broadcasts with ``r``).
        a: Kerr spin parameter (length).
        M: unused; present for API consistency.

    Returns:
        tuple ``(ρ, z, φ_placeholder)`` where ``φ_placeholder`` is ``None``
        (φ is invariant under this transformation — callers should supply it
        themselves).  ``ρ`` and ``z`` have the broadcast shape of ``r, θ``.
    """
    r_arr = np.asarray(r, dtype=float)
    t_arr = np.asarray(theta, dtype=float)
    rho = np.sqrt(r_arr * r_arr + a * a) * np.sin(t_arr)
    z = r_arr * np.cos(t_arr)
    return rho, z, None


def cylindrical_to_boyer_lindquist(rho, z, a: float):
    """Inverse map ``(ρ, z) → (r, θ)`` (paper eq. 3, ``+`` branch).

    Returns ``(r, θ)`` with the same broadcast shape as the inputs.  ``r``
    is the non-negative oblate-spheroidal radius and ``θ = arccos(z/r)``
    lies in ``[0, π]``.  On the disk ``z = 0, ρ < a`` we have ``r = 0`` at
    the ring singularity; callers should avoid that locus.
    """
    rho_arr = np.asarray(rho, dtype=float)
    z_arr = np.asarray(z, dtype=float)
    base = rho_arr ** 2 + z_arr ** 2 - a * a
    disc = np.sqrt(base * base + 4.0 * a * a * z_arr ** 2)
    r_squared = 0.5 * (base + disc)
    r = np.sqrt(np.maximum(r_squared, 0.0))
    # θ = arccos(z / r), with r = 0 handled by convention (return π/2)
    with np.errstate(divide="ignore", invalid="ignore"):
        cos_theta = np.where(r > 0.0, z_arr / np.maximum(r, 1e-300), 0.0)
    cos_theta = np.clip(cos_theta, -1.0, 1.0)
    theta = np.arccos(cos_theta)
    return r, theta


# -----------------------------------------------------------------------------
# Kerr–Newman metric components
# -----------------------------------------------------------------------------

@dataclass(frozen=True)
class KerrMetric:
    """Non-zero components of the Kerr–Newman metric at a point.

    Signature convention: ``(−, +, +, +)``.
    Coordinate order for ``(r, θ)`` components: ``(t, r, θ, φ)``.
    """
    g_tt: float
    g_tphi: float
    g_rr: float
    g_thth: float
    g_phiphi: float
    Sigma: float
    Delta: float


def kerr_metric_bl(r: float, theta: float, a: float, M: float, Q: float) -> KerrMetric:
    """BL metric components at ``(r, θ)`` for Kerr–Newman with mass ``M`` and charge ``Q``.

    See module docstring for the line element.  All quantities in geometric
    units (``G = c = 1``).  ``Q²`` enters the horizon function

        Δ = r² − 2 M r + a² + Q²

    and is the only way the EM self-energy appears at the metric level.
    """
    sin_t = np.sin(theta)
    cos_t = np.cos(theta)
    Sigma = r * r + a * a * cos_t * cos_t
    Delta = r * r - 2.0 * M * r + a * a + Q * Q

    g_tt = -(Delta - a * a * sin_t * sin_t) / Sigma
    g_tphi = -a * sin_t * sin_t * ((r * r + a * a) - Delta) / Sigma
    g_rr = Sigma / Delta if Delta != 0.0 else float("inf")
    g_thth = Sigma
    g_phiphi = sin_t * sin_t * ((r * r + a * a) ** 2 - Delta * a * a * sin_t * sin_t) / Sigma
    return KerrMetric(g_tt, g_tphi, g_rr, g_thth, g_phiphi, Sigma, Delta)


def cylindrical_kerr_metric_components(rho: float, z: float, phi: float,
                                       a: float, M: float, Q: float) -> KerrMetric:
    """Kerr–Newman metric components evaluated at cylindrical ``(ρ, z, φ)``.

    The helper inverts ``(ρ, z) → (r, θ)`` and returns the BL-frame
    components at that point.  The frame-dragging term ``g_{tφ}`` (the
    physical signature of the Kerr vortex) is the component that the DKN
    picture interprets as the source of the electron's gyromagnetic
    behaviour, so we expose the full dataclass rather than just a dict.

    Note:
        This returns the metric *components in the BL coordinate basis*,
        evaluated at the cylindrical point.  A full coordinate-transformed
        cylindrical-basis tensor would require an additional Jacobian
        push-forward; that is not needed for the DKN applications (horizon
        location, ergoregion, frame-dragging sign) and is intentionally
        omitted.
    """
    r, theta = cylindrical_to_boyer_lindquist(rho, z, a)
    return kerr_metric_bl(float(r), float(theta), a, M, Q)


# -----------------------------------------------------------------------------
# Surfaces of interest: horizons and ergoregion
# -----------------------------------------------------------------------------

def outer_horizon(a: float, M: float, Q: float) -> Optional[float]:
    """Outer event horizon r₊ = M + √(M² − a² − Q²), or ``None`` if naked.

    For the DKN over-rotating regime (``a > M``) the discriminant is
    negative and no horizon exists — the solution is a *naked* Kerr–Newman
    soliton.  Callers rely on the ``None`` return to branch into the
    over-rotating code path.
    """
    disc = M * M - a * a - Q * Q
    if disc < 0.0:
        return None
    return M + np.sqrt(disc)


def ergosurface_outer(theta, a: float, M: float, Q: float):
    """Outer stationary-limit surface r_E⁺(θ) = M + √(M² − Q² − a² cos²θ).

    Returns ``NaN`` at polar angles where the radicand is negative (this is
    the generic case for ``a > M`` outside a narrow equatorial band — the
    ergoregion becomes toroidal in the over-rotating limit).
    """
    theta_arr = np.asarray(theta, dtype=float)
    disc = M * M - Q * Q - a * a * np.cos(theta_arr) ** 2
    with np.errstate(invalid="ignore"):
        return np.where(disc >= 0.0, M + np.sqrt(np.maximum(disc, 0.0)), np.nan)


def is_over_rotating(a: float, M: float, Q: float = 0.0) -> bool:
    """True iff the Kerr–Newman solution has no horizon (a² + Q² > M²).

    The DKN electron is always over-rotating (a ≫ M_geom for the electron),
    and many downstream choices depend on this branch.
    """
    return a * a + Q * Q > M * M


# -----------------------------------------------------------------------------
# Optional matplotlib visualisation
# -----------------------------------------------------------------------------

def plot_vortex_cross_section(a: float, M: float, Q: float = 0.0,
                              extent: float = 3.0, n: int = 400,
                              ax=None, show_ergoregion: bool = True,
                              show_ring_singularity: bool = True):
    """Plot a (ρ, z) meridional slice of the Kerr–Newman frame-dragging field.

    Colour shows ``|g_{tφ}|`` on a logarithmic scale; the ring singularity
    ``(ρ = a, z = 0)`` and the outer ergosurface (where finite) are overlaid.
    matplotlib is an optional dependency (see ``pyproject.toml`` ``[notebooks]``
    extras) — this function imports it lazily and raises if absent.

    Returns the matplotlib ``Axes`` for further customisation.
    """
    try:
        import matplotlib.pyplot as plt
    except ImportError as exc:
        raise ImportError(
            "plot_vortex_cross_section requires matplotlib. Install via "
            "`pip install -e .[notebooks]`."
        ) from exc

    rho = np.linspace(1e-6, extent * max(a, M, 1.0), n)
    z = np.linspace(-extent * max(a, M, 1.0), extent * max(a, M, 1.0), n)
    RHO, Z = np.meshgrid(rho, z)

    g_tphi = np.zeros_like(RHO)
    for i in range(n):
        for j in range(n):
            m = cylindrical_kerr_metric_components(RHO[i, j], Z[i, j], 0.0,
                                                   a=a, M=M, Q=Q)
            g_tphi[i, j] = m.g_tphi

    if ax is None:
        _, ax = plt.subplots(figsize=(6, 6))
    field = np.log10(np.abs(g_tphi) + 1e-30)
    im = ax.pcolormesh(RHO, Z, field, shading="auto", cmap="magma")
    ax.set_xlabel(r"$\rho$")
    ax.set_ylabel(r"$z$")
    ax.set_aspect("equal")
    ax.set_title(
        f"Kerr–Newman vortex (a={a:.3g}, M={M:.3g}, Q={Q:.3g}) — "
        f"{'over-rotating' if is_over_rotating(a, M, Q) else 'sub-extremal'}"
    )

    if show_ring_singularity:
        ax.plot([a], [0.0], marker="o", markersize=6, color="cyan",
                label="ring singularity")

    if show_ergoregion:
        thetas = np.linspace(0.0, pi, 500)
        r_e = ergosurface_outer(thetas, a=a, M=M, Q=Q)
        mask = np.isfinite(r_e)
        rho_e = np.sqrt(r_e[mask] ** 2 + a * a) * np.sin(thetas[mask])
        z_e = r_e[mask] * np.cos(thetas[mask])
        if rho_e.size:
            ax.plot(rho_e, z_e, color="white", lw=1.2, label="outer ergosurface")
            ax.plot(-rho_e, z_e, color="white", lw=1.2)

    ax.legend(loc="upper right", fontsize=8)
    plt.colorbar(im, ax=ax, label=r"$\log_{10}|g_{t\phi}|$")
    return ax


__all__ = [
    "KerrMetric",
    "boyer_lindquist_to_cylindrical",
    "cylindrical_to_boyer_lindquist",
    "kerr_metric_bl",
    "cylindrical_kerr_metric_components",
    "outer_horizon",
    "ergosurface_outer",
    "is_over_rotating",
    "plot_vortex_cross_section",
]
