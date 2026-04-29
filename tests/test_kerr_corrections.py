"""Kerr corrections test (HYPOTHESIS.md Step 5).

Verifies what the Möbius framework can and cannot say about the leading
Kerr correction Δλ² = -½a²(ω²-μ²) to the angular eigenvalue.
"""

from math import isclose

import numpy as np
import pytest

from dinos import cp, kerr_corrections, polar_strip


# -----------------------------------------------------------------------------
# CP leading-correction sanity (independent of Möbius)
# -----------------------------------------------------------------------------

def test_cp_leading_shift_matches_closed_form():
    """The closed form Δλ² = -½a²(ω²-μ²) — sanity check on the
    primitive used by everything below."""
    cases = [
        (0.1, 0.5, 0.0,  -0.5 * 0.01 * 0.25),
        (0.5, 1.0, 0.5,  -0.5 * 0.25 * 0.75),
        (1.0, 2.0, 0.0,  -0.5 * 1.0 * 4.0),
    ]
    for a, w, mu, expected in cases:
        assert isclose(kerr_corrections.cp_leading_shift(a, w, mu),
                       expected, rel_tol=1e-12)


def test_on_shell_correction_vanishes_universally():
    """For ω = μ (rest-mass on-shell), Δλ² = 0 for every a — the
    universal feature the Möbius bridge must reproduce."""
    for a in [0.0, 0.1, 0.5, 1.0, 5.0]:
        for m in [0.0, 0.1, 0.5, 1.0]:
            assert kerr_corrections.cp_leading_shift(a, m, m) == 0.0


def test_off_shell_correction_has_correct_sign():
    """ω > μ ⇒ negative shift (timelike modes); ω < μ ⇒ positive."""
    assert kerr_corrections.cp_leading_shift(a=0.5, omega=1.0, mu=0.5) < 0
    assert kerr_corrections.cp_leading_shift(a=0.5, omega=0.5, mu=1.0) > 0


# -----------------------------------------------------------------------------
# Möbius parameter mapping reproduces the form
# -----------------------------------------------------------------------------

def test_mobius_perturbative_shift_equals_cp_leading_under_mapping():
    """Under (a, ω, μ²) ↔ (τ, m_j, β+κ), the Möbius shift IS the CP
    shift — by construction of the mapping."""
    for tau in [0.1, 0.5, 1.0]:
        for n_phi in range(3):
            m_j = n_phi + 0.5
            for bk in [0.1, 0.46, 1.0]:
                shift_mob = kerr_corrections.mobius_perturbative_shift(
                    tau=tau, m_j=m_j, beta_plus_kappa=bk,
                )
                shift_cp = cp.lambda_CP_leading(
                    k=int(m_j + 0.5),  # k integer near m_j+½
                    a=tau, omega=m_j, mu=np.sqrt(bk),
                ) ** 2 - int(m_j + 0.5) ** 2
                assert isclose(shift_mob, shift_cp, rel_tol=1e-9, abs_tol=1e-12)


def test_mobius_shift_vanishes_when_m_j_squared_equals_wall():
    """On-shell analog: when m_j² = β+κ (mode "matches" the wall mass),
    the Möbius perturbative shift vanishes for any τ."""
    for tau in [0.0, 0.1, 1.0, 5.0]:
        for m_j in [0.5, 1.5, 2.5]:
            shift = kerr_corrections.mobius_perturbative_shift(
                tau=tau, m_j=m_j, beta_plus_kappa=m_j ** 2,
            )
            assert shift == 0.0


# -----------------------------------------------------------------------------
# Quadratic-in-tau scaling
# -----------------------------------------------------------------------------

def test_shift_is_quadratic_in_tau():
    """Δλ² ∝ τ² — verify by scaling τ and checking the shift scales
    as τ²."""
    m_j, bk = 0.5, 0.1
    shift_1 = kerr_corrections.mobius_perturbative_shift(
        tau=1.0, m_j=m_j, beta_plus_kappa=bk,
    )
    shift_2 = kerr_corrections.mobius_perturbative_shift(
        tau=2.0, m_j=m_j, beta_plus_kappa=bk,
    )
    shift_5 = kerr_corrections.mobius_perturbative_shift(
        tau=5.0, m_j=m_j, beta_plus_kappa=bk,
    )
    assert isclose(shift_2 / shift_1, 4.0, rel_tol=1e-12)
    assert isclose(shift_5 / shift_1, 25.0, rel_tol=1e-12)


def test_log_log_slope_is_two():
    """log|Δ| vs log τ has slope exactly 2 (off-shell) — the cleanest
    statement of the quadratic dependence."""
    m_j, bk = 0.5, 0.1   # off-shell: m_j² = 0.25 ≠ 0.1
    taus = np.array([0.01, 0.05, 0.1, 0.5, 1.0])
    shifts = np.array([
        abs(kerr_corrections.mobius_perturbative_shift(tau=t, m_j=m_j,
                                                       beta_plus_kappa=bk))
        for t in taus
    ])
    slope, _ = np.polyfit(np.log(taus), np.log(shifts), 1)
    assert isclose(slope, 2.0, abs_tol=1e-9), f"slope = {slope}; expected 2"


# -----------------------------------------------------------------------------
# Full-Dirac eigenvalue (Step 4 + Step 5)
# -----------------------------------------------------------------------------

def test_shifted_full_dirac_eigenvalue_at_on_shell_equals_k_squared():
    """When the wall coupling matches m_j² (on-shell analog), the
    full Step 4 + Step 5 eigenvalue equals the unperturbed |k|²."""
    for n_phi in range(3):
        m_j = n_phi + 0.5
        bk = m_j ** 2  # on-shell: μ² = m_j²
        for n_theta in range(3):
            for tau in [0.0, 0.5, 1.0]:
                full = kerr_corrections.shifted_mobius_eigenvalue_full_dirac(
                    tau=tau, n_theta=n_theta, n_phi=n_phi,
                    beta_plus_kappa=bk,
                )
                expected = polar_strip.dirac_k_squared(n_theta, m_j)
                assert isclose(full, expected, rel_tol=1e-12)


# -----------------------------------------------------------------------------
# Mapping non-canonicity diagnostic
# -----------------------------------------------------------------------------

def test_alternative_mappings_exist():
    """Document that the §3 mapping is not unique — at least two other
    consistent mappings reproduce the functional form ``-½τ²·V``.
    This is a *negative* result: the framework underdetermines V."""
    alts = kerr_corrections.alternative_mappings_giving_same_form()
    assert len(alts) >= 2, "expected multiple plausible mappings"
    # The first one is the proposal of HYPOTHESIS §3; the others are
    # negative-result acknowledgements.
    assert "HYPOTHESIS" in alts[0]["name"]


def test_off_shell_dkn_electron_shift_is_zero_universally():
    """The DKN electron sits at ω = μ = m_e (rest-frame on-shell). The
    leading Kerr correction is therefore zero independent of a — any
    Möbius interpretation is consistent at this point."""
    from dinos.constants import m_e_MeV
    # For DKN: a = a_Compton ≈ 1/(2 m_e), ω = μ = m_e.
    a = 1.0 / (2.0 * m_e_MeV)
    shift = kerr_corrections.cp_leading_shift(a=a, omega=m_e_MeV, mu=m_e_MeV)
    assert shift == 0.0


# -----------------------------------------------------------------------------
# Step 5b — Time-averaging closes the −½ prefactor
# -----------------------------------------------------------------------------

def test_naive_static_shift_is_double_the_floquet():
    """A literal static τ²-coupling gives `−τ²·V` (no ½).  The CP
    formula's −½ is what static treatment is *missing* — exactly a
    factor of 2."""
    tau, m_j, bk = 0.7, 0.5, 0.1
    static = kerr_corrections.mobius_static_shift_naive(tau, m_j, bk)
    floquet = kerr_corrections.floquet_first_order_shift(tau, m_j, bk)
    # static = 2 × floquet  (i.e., the naive one is missing the ½).
    assert isclose(static / floquet, 2.0, rel_tol=1e-12)


def test_time_averaged_shift_recovers_one_half_prefactor_numerically():
    """⟨τ(t)²⟩_t = τ₀²/2 for τ(t) = τ₀ cos(Ωt), so the time-averaged
    shift exactly equals the −½ Floquet prediction.  This is the
    operational closure of the Step 5 prefactor problem."""
    tau_0, m_j, bk = 0.7, 0.5, 0.1
    expected = kerr_corrections.floquet_first_order_shift(tau_0, m_j, bk)
    numerical = kerr_corrections.time_averaged_shift(
        tau_0, omega_drive=1.0, m_j=m_j, beta_plus_kappa=bk,
    )
    assert isclose(numerical, expected, rel_tol=1e-6), (
        f"numerical = {numerical}, expected = {expected}"
    )


def test_time_averaging_factor_is_universal_in_drive_frequency():
    """The −½ prefactor comes from ⟨cos²⟩ = ½, which doesn't depend on
    Ω.  Any drive frequency gives the same time-averaged shift."""
    tau_0, m_j, bk = 0.5, 1.5, 0.2
    expected = kerr_corrections.floquet_first_order_shift(tau_0, m_j, bk)
    for omega in [0.1, 1.0, 10.0, 100.0]:
        numerical = kerr_corrections.time_averaged_shift(
            tau_0, omega_drive=omega, m_j=m_j, beta_plus_kappa=bk,
            n_samples=8192,
        )
        assert isclose(numerical, expected, rel_tol=1e-6), (
            f"omega={omega}: got {numerical}, expected {expected}"
        )


def test_time_averaged_shift_reduces_to_cp_under_mapping():
    """End-to-end: with the §3 mapping (a ↔ τ_0, ω ↔ m_j, μ² ↔ β+κ),
    the time-averaged Möbius shift IS the CP leading shift, with the
    `−½` derived rather than postulated."""
    tau_0, m_j, bk = 0.3, 0.5, 0.2
    time_avg = kerr_corrections.time_averaged_shift(
        tau_0, omega_drive=1.0, m_j=m_j, beta_plus_kappa=bk,
    )
    cp_shift = kerr_corrections.cp_leading_shift(
        a=tau_0, omega=m_j, mu=np.sqrt(bk),
    )
    assert isclose(time_avg, cp_shift, rel_tol=1e-6)


def test_on_shell_time_averaged_shift_is_zero():
    """When m_j² = β+κ (the Möbius on-shell analog), the time-averaged
    shift vanishes for any τ_0 and any Ω — the universal feature
    survives the time-varying generalisation."""
    m_j = 0.5
    bk = m_j ** 2  # on-shell
    for tau_0 in [0.0, 0.3, 1.0, 5.0]:
        for omega in [0.5, 1.0, 10.0]:
            shift = kerr_corrections.time_averaged_shift(
                tau_0, omega_drive=omega, m_j=m_j, beta_plus_kappa=bk,
            )
            assert abs(shift) < 1e-10, f"τ_0={tau_0}, Ω={omega}: shift={shift}"


def test_negative_drive_frequency_rejected():
    with pytest.raises(ValueError):
        kerr_corrections.time_averaged_shift(
            tau_amplitude=1.0, omega_drive=-1.0, m_j=0.5, beta_plus_kappa=0.1,
        )


def test_moving_peak_average_shift_asymptotic_form():
    """Asymptotic L ≫ Δ form: shift = −(4Δ/3L)·τ²·V (moving peak,
    periodic loop — both halves of the peak captured).

    For Δ = 0.01, L = 10: duty = 4·0.01/(3·10) ≈ 1.33e-3."""
    tau, m_j, bk = 0.5, 1.5, 0.2
    naive = kerr_corrections.mobius_static_shift_naive(tau, m_j, bk)
    narrow = kerr_corrections.moving_peak_average_shift(
        tau_amplitude=tau, packet_width=0.01, loop_length=10.0,
        m_j=m_j, beta_plus_kappa=bk,
    )
    expected_ratio = (4.0 / 3.0) * (0.01 / 10.0)
    assert isclose(narrow / naive, expected_ratio, rel_tol=1e-12)
    assert abs(narrow) < abs(naive) / 100.0


# -----------------------------------------------------------------------------
# Step 5c — Moving-peak Floquet (exact)
# -----------------------------------------------------------------------------

def test_sech4_integral_closed_form_matches_numerical():
    """Periodic-loop integral ∫_{−L/2}^{L/2} sech⁴(s/Δ) ds matches
    the closed form 2Δ·[tanh(L/(2Δ)) − ⅓ tanh³(L/(2Δ))]."""
    for L in [1.0, 5.0, 10.0]:
        for delta in [0.1, 1.0, 5.0, 100.0]:
            closed = kerr_corrections.sech4_integral_over_loop(delta, L)
            # Compare against trapezoidal integration on [-L/2, L/2].
            s = np.linspace(-L / 2.0, L / 2.0, 4001)
            f = (1.0 / np.cosh(s / delta)) ** 4
            numerical = float(np.trapezoid(f, s))
            assert isclose(closed, numerical, rel_tol=1e-4), (
                f"L={L}, Δ={delta}: closed={closed}, numerical={numerical}"
            )


def test_moving_peak_duty_cycle_limits():
    """Duty cycle ⟨sech⁴⟩ ∈ (0, 1) and approaches the right limits."""
    L = 10.0
    # Narrow packet (Δ ≪ L): duty cycle → (4Δ)/(3L), i.e. → 0.
    narrow = kerr_corrections.moving_peak_duty_cycle(0.01, L)
    assert 0.0 < narrow < 0.01
    # Wide packet (Δ ≫ L): duty cycle → 1 (uniform overlap).
    wide = kerr_corrections.moving_peak_duty_cycle(1000.0, L)
    assert isclose(wide, 1.0, abs_tol=1e-3)


def test_moving_peak_duty_cycle_asymptotic_form():
    """For L ≫ Δ, duty cycle = (4Δ)/(3L) (full real-line integral
    of sech⁴ is 4/3 — both halves of the peak are captured on a
    periodic loop)."""
    L = 100.0
    delta = 1.0   # L/Δ = 100, deep asymptotic regime
    duty = kerr_corrections.moving_peak_duty_cycle(delta, L)
    asymptotic = (4.0 / 3.0) * (delta / L)
    assert isclose(duty, asymptotic, rel_tol=1e-3)


def test_moving_peak_floquet_shift_matches_static_in_wide_limit():
    """As Δ → ∞, the moving-peak shift saturates the naive static value
    (duty cycle → 1)."""
    tau, m_j, bk = 0.5, 1.5, 0.2
    L = 10.0
    naive = kerr_corrections.mobius_static_shift_naive(tau, m_j, bk)
    wide = kerr_corrections.moving_peak_floquet_shift(
        tau_amplitude=tau, packet_width=1000.0, loop_length=L,
        m_j=m_j, beta_plus_kappa=bk,
    )
    assert isclose(wide, naive, rel_tol=1e-3)


def test_moving_peak_match_to_cp_half_exists_and_is_unique():
    """There exists a packet width Δ such that ⟨sech⁴⟩_periodic = ½
    exactly (matching the CP −½ prefactor in this interpretation).

    With the full periodic integral, the asymptotic estimate is
    Δ/L = 3/8 = 0.375, with finite-size corrections raising it
    slightly."""
    L = 1.0
    delta_match = kerr_corrections.moving_peak_match_to_cp_half(L)
    duty = kerr_corrections.moving_peak_duty_cycle(delta_match, L)
    assert isclose(duty, 0.5, abs_tol=1e-9), (
        f"matched Δ/L = {delta_match/L}, but duty = {duty}"
    )
    # Δ/L should be in the range (0.3, 0.6) — moderate fraction of loop.
    assert 0.3 < delta_match / L < 0.6, (
        f"matched Δ/L = {delta_match/L}; expected in (0.3, 0.6)"
    )


def test_moving_peak_at_match_reproduces_cp_half_prefactor():
    """At the matching Δ, the moving-peak shift exactly equals the CP
    leading shift — establishing one *concrete* (Δ, L, τ_0) point at
    which the moving-peak interpretation pins to the harmonic answer."""
    tau_0, m_j, bk = 0.5, 0.5, 0.1
    L = 1.0
    delta_match = kerr_corrections.moving_peak_match_to_cp_half(L)
    moving = kerr_corrections.moving_peak_floquet_shift(
        tau_amplitude=tau_0, packet_width=delta_match, loop_length=L,
        m_j=m_j, beta_plus_kappa=bk,
    )
    cp = kerr_corrections.cp_leading_shift(
        a=tau_0, omega=m_j, mu=np.sqrt(bk),
    )
    assert isclose(moving, cp, rel_tol=1e-9)


def test_moving_peak_does_not_uniquely_pin_prefactor():
    """The moving-peak prefactor *depends on Δ/L* — so it does NOT, by
    itself, uniquely fix the CP −½.  The harmonic case (Step 5b) gives
    ½ universally; the moving peak only matches at one specific Δ/L.

    Negative result: the moving-peak interpretation is one consistent
    reading, but it doesn't pin the unique answer without additional
    physics fixing Δ/L."""
    L = 1.0
    duties = [
        kerr_corrections.moving_peak_duty_cycle(delta, L)
        for delta in [0.1, 0.5, 1.0, 2.0, 5.0]
    ]
    # All five values should be different — confirming the prefactor is
    # not fixed by the moving-peak interpretation alone.
    sorted_duties = sorted(duties)
    for i in range(len(sorted_duties) - 1):
        assert sorted_duties[i+1] - sorted_duties[i] > 0.01, (
            f"adjacent duties too close: {sorted_duties}"
        )


def test_moving_peak_negative_inputs_rejected():
    with pytest.raises(ValueError):
        kerr_corrections.moving_peak_average_shift(
            tau_amplitude=1.0, packet_width=0.0, loop_length=1.0,
            m_j=0.5, beta_plus_kappa=0.1,
        )
    with pytest.raises(ValueError):
        kerr_corrections.moving_peak_average_shift(
            tau_amplitude=1.0, packet_width=1.0, loop_length=-1.0,
            m_j=0.5, beta_plus_kappa=0.1,
        )
