"""Systematic validation of Grok-proposed extensions (HYPOTHESIS Step 39-validation).

A 2300-line Grok conversation proposed ~20 extensions to the DKN
framework, including:

- SU(3) flux-tube confinement on Z3 Mobius (claim: STRONG CONFINEMENT,
  area-law, sigma matches QCD ~0.18 GeV^2)
- Emergent c as eigenvalue (claim: dispersion stability minimum at c=1)
- ElectroweakPolarStrip (claim: sin^2(theta_W) = 0.23174, mW/mZ = 0.8768
  to sub-percent agreement)
- CKM mixing from polar overlaps (claim: theta_12 = 13.02 vs 13.04, 0.15%)
- PMNS mixing from left-handed polar overlaps (claim: theta_12 = 33.82 deg,
  sum m_nu = 0.059 eV)
- Lambda_eff x f_DM Gaussian attractor (claim: peak at f_DM = 0.27)
- Speed of light from string compactification (claim: c = (l_s/l_Pl) * A * exp(phi),
  matches 1 to 2% in 95% of MC realisations)
- Topological seesaw (claim: predicts sum m_nu = 0.059 eV from A^n)
- Z2 x Z3 chiral anomaly index = 0 (claim: cancels geometrically)

This module checks each claim numerically. The verdicts:

| Claim                           | Verdict       |
|---------------------------------|---------------|
| 1D SU(3) area-law               | FALSIFIED     |
| Emergent c as eigenvalue        | FALSIFIED     |
| ElectroweakPolarStrip derivation| TAUTOLOGICAL  |
| CKM from polar overlaps         | UNDERSPECIFIED|
| PMNS from polar overlaps        | UNDERSPECIFIED|
| Lambda - f_DM Gaussian attractor| CURVE-FIT     |
| c from string compactification  | FALSIFIED     |
| Anomaly index = 0               | HARD-CODED    |
| Seesaw sum m_nu = 0.059 eV      | TUNABLE       |

NONE of the headline numerical "matches" Grok claimed are real
derivations. The Grok extensions can be implemented as honest
scaffolds (this module + the gauge_confinement, electroweak_strip,
multi_cover, etc. modules), but the Dinos repo's standard of
honest verdicts requires we mark them as such — not as confirmed
predictions.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import pi

import numpy as np

from . import gauge_confinement as gc


@dataclass(frozen=True)
class Verdict:
    claim_label: str
    grok_claim: str
    verdict: str            # CONFIRMED | FALSIFIED | TAUTOLOGICAL | UNDERSPECIFIED | CURVE-FIT | HARD-CODED | TUNABLE
    evidence: str
    quantitative_test: str  # one-line summary of the test that produced the verdict


def validate_su3_area_law() -> Verdict:
    """The 1D Möbius cannot produce an area-law because there is no
    transverse area. Direct test: |Tr(U^N)|/3 for Z3 center = 1
    (constant), and for generic SU(3) holonomies it oscillates inside
    [0, 1] without monotonic decay. Both falsify the area-law claim.
    """
    Z = gc.su3_z3_center_holonomy()
    abs_trace_at_192 = abs(gc.wilson_loop_trace_1d(192, Z))
    info = gc.random_su3_holonomy_decay_rate(N_max=64, seed=0)
    return Verdict(
        claim_label="SU(3) flux-tube area law on 1D Möbius",
        grok_claim=("STRONG CONFINEMENT (area-law). String tension sigma "
                    "matches QCD ~0.18 GeV^2"),
        verdict="FALSIFIED",
        evidence=(f"Z3 center holonomy gives |Tr(U^N)|/3 = {abs_trace_at_192:.6f} "
                  f"at N=192 (target: exp(-sigma*N) -> 0). Generic SU(3) "
                  f"random holonomy gives median |Tr| = {info['median_abs_trace']:.4f}, "
                  f"max = {info['max_abs_trace']:.4f} — oscillating, not "
                  f"exponentially decaying. Area-law confinement requires "
                  f"a 2D plaquette geometry, which a 1D Möbius does not have."),
        quantitative_test="Z3 center: |Tr(U^192)|/3 == 1.000 exactly",
    )


def validate_emergent_c_eigenvalue() -> Verdict:
    """Grok's claim: dispersion stability MINIMIZED at c = 1.
    Direct test: omega(k) = c|k| + const is LINEAR for any c, so the
    group velocity is exactly c at every c. Stability metric is c-independent.
    """
    N = 256
    s = np.linspace(0, 2 * pi, N, endpoint=False)
    ds = s[1] - s[0]
    k_modes = np.fft.fftfreq(N, ds) * 2 * pi
    k_modes = k_modes[:N // 2]

    def disp(k, c):
        return c * np.abs(k) + 0.5 * np.sign(k)

    devs = []
    for c in [0.5, 0.7, 1.0, 1.3, 1.7, 2.0]:
        omega = disp(k_modes, c)
        v_g = np.gradient(omega, k_modes)[1:-1]
        devs.append(float(np.mean(np.abs(v_g - c))))
    spread = float(np.std(devs))

    return Verdict(
        claim_label="Emergent c as eigenvalue of Mobius dispersion",
        grok_claim=("Stability metric (mean group-velocity deviation from c) "
                    "is minimised exactly at c = 1; deviant c are pruned"),
        verdict="FALSIFIED",
        evidence=(f"Across c in [0.5, 2.0], the stability deviation has "
                  f"range {min(devs):.6f} - {max(devs):.6f}, std {spread:.2e}. "
                  f"It is a function of dispersion shape only, NOT of c. "
                  f"omega = c|k| + const is linear at every c by construction; "
                  f"v_g = c trivially. There is no c-dependent eigenvalue "
                  f"minimum to find."),
        quantitative_test=f"std(stability vs c) = {spread:.2e} (= 0 within numerical noise)",
    )


def validate_electroweak_polar_strip() -> Verdict:
    """Grok's "derived" sin^2(theta_W) and mW/mZ values come from
    hardcoded g2 = 0.652 and g' = 0.357 — these are observed SM
    couplings plugged directly in. The "derivation" is identity:
    given g, g', SM tree-level relations give the W/Z/photon spectrum.
    Nothing is derived from the Möbius geometry.
    """
    g2, gp, v = 0.652, 0.357, 246.22
    mW = 0.5 * g2 * v
    mZ = 0.5 * np.sqrt(g2**2 + gp**2) * v
    sin2 = float(np.sin(np.arctan(gp / g2))**2)

    return Verdict(
        claim_label="ElectroweakPolarStrip derivation of sin^2(theta_W)",
        grok_claim=("sin^2(theta_W) = 0.23174 (observed 0.23120) at 0.23%; "
                    "mW/mZ = 0.8768 (observed 0.8815) at 0.53%, derived from "
                    "the polar Möbius geometry"),
        verdict="TAUTOLOGICAL",
        evidence=(f"Grok's code hardcodes g2 = 0.652 and g' = 0.357 — these "
                  f"are observed SM couplings. The output sin^2 = {sin2:.4f} "
                  f"and mW/mZ = {mW/mZ:.4f} are tree-level SM relations of "
                  f"the input couplings. No prediction from geometry: g2 "
                  f"and g' are not computed from any Möbius eigenvalue. "
                  f"The 'derivation' is back-substitution of measured values."),
        quantitative_test=f"From inputs g2=0.652, g'=0.357 -> sin^2 = {sin2:.5f} (algebra, not derivation)",
    )


def validate_ckm_polar_overlaps() -> Verdict:
    """Grok claims CKM angles to 0.15% accuracy from "overlap integrals
    of generation wavefunctions on the polar strip" but provides no
    explicit wavefunction ansatz.

    Test: try the simplest physically-motivated ansatz
    (psi^up_n(theta) = sin((n+1)theta), psi^down_n(theta) = sin((n+1)(theta - delta)))
    and scan delta. Show that the 0.15% match is not realised by any
    delta in this family — it must come from a bespoke ansatz that
    Grok did not specify.
    """
    from scipy.integrate import quad

    def psi_up(t, n):
        return np.sin((n + 1) * t) * np.sqrt(2 / np.pi)

    def psi_down(t, n, delta):
        return np.sin((n + 1) * (t - delta)) * np.sqrt(2 / np.pi)

    obs_theta12 = 13.04  # degrees, PDG
    best_err = np.inf
    best_delta = 0.0
    for delta in np.linspace(0.05, 0.6, 50):
        V01, _ = quad(lambda t: psi_up(t, 0) * psi_down(t, 1, delta), 0, np.pi)
        V00, _ = quad(lambda t: psi_up(t, 0) * psi_down(t, 0, delta), 0, np.pi)
        if abs(V00) < 1e-9:
            continue
        theta12 = float(np.degrees(np.arctan(abs(V01) / abs(V00))))
        err = abs(theta12 - obs_theta12) / obs_theta12 * 100
        if err < best_err:
            best_err = err
            best_delta = delta

    return Verdict(
        claim_label="CKM mixing matrix from polar overlaps",
        grok_claim=("theta_12 = 13.02 deg (observed 13.04) at 0.15%, "
                    "theta_23 at 0.4%, theta_13 at 1.5%, derived from polar "
                    "wavefunction overlaps"),
        verdict="UNDERSPECIFIED",
        evidence=(f"Grok provides no explicit wavefunction formula. With the "
                  f"simplest physically-motivated sine-mode ansatz, scanning "
                  f"delta in [0.05, 0.6], best theta_12 match achieves {best_err:.1f}% "
                  f"at delta = {best_delta:.3f} — far from the 0.15% claim. "
                  f"Without a specific wavefunction prescription rooted in "
                  f"the Möbius geometry, the claimed sub-percent match is "
                  f"a curve fit to observed values."),
        quantitative_test=f"Best simple-ansatz theta_12 error: {best_err:.1f}% (Grok claim: 0.15%)",
    )


def validate_lambda_attractor_gaussian() -> Verdict:
    """Grok's notebook code: Lambda_eff = 1e-120 * exp(-9*(f_DM - 0.27)^2)
    This is an ansatz with the answer hardcoded as the Gaussian center.
    It is not derived from any pruning dynamics. Replace 0.27 with any
    other target and the same shape produces the same 'attractor'."""
    return Verdict(
        claim_label="Lambda_eff vs f_DM Gaussian attractor at f_DM = 0.27",
        grok_claim=("Lambda_eff dynamically minimised at f_DM = 0.27, "
                    "selecting observed dark fraction + small positive Lambda"),
        verdict="CURVE-FIT",
        evidence=("Grok's equation Lambda_eff = 1e-120 * exp(-9*(f_DM - 0.27)^2) "
                  "is an ansatz; the Gaussian center 0.27 IS the observed value. "
                  "No mechanism in the text actually produces a peak at 0.27 — "
                  "any other target would 'work' equally with the same shape. "
                  "This is a tautology dressed as a derivation."),
        quantitative_test="Replacing 0.27 -> 0.40 in the ansatz gives a peak at 0.40, with no change of physics",
    )


def validate_c_from_string_compactification() -> Verdict:
    """Grok: c = (l_s/l_Pl) * A_Mobius * exp(phi_0). With A ~ 0.48 the
    formula gives c ~ 0.48, not 1. Grok then says "after proper
    normalization to observed Planck/Compton matching" which is undefined.
    """
    rng = np.random.default_rng(42)
    n = 10000
    ratios = rng.normal(1.0, 0.008, n)
    A_mobius = rng.uniform(0.46, 0.50, n)
    warp = np.exp(rng.normal(0, 0.003, n))
    c_4d = ratios * A_mobius * warp
    mean_c = float(c_4d.mean())
    frac_within_2pct = float(np.mean(np.abs(c_4d - 1) < 0.02))
    return Verdict(
        claim_label="c from Möbius-fibered string compactification",
        grok_claim=("Mean c_4D = 0.9998 +- 0.012, 94.7% of MC realisations "
                    "within 2% of 1, derived from string scale ratio + "
                    "Mobius contraction"),
        verdict="FALSIFIED",
        evidence=(f"With Grok's exact priors (R_string/R_compact ~ N(1, 0.008), "
                  f"A_Mobius ~ U(0.46, 0.50), warp ~ N(0, 0.003)) the mean is "
                  f"{mean_c:.4f}, NOT ~1, and {frac_within_2pct:.1%} of "
                  f"realisations sit within 2% of 1. The formula gives "
                  f"c ~ A_Mobius ~ 0.48, not 1. Grok's claimed match is "
                  f"reproduced only by an unspecified 'normalization to "
                  f"observed Planck/Compton matching' that does no work."),
        quantitative_test=f"Reproducing Grok's MC: mean c = {mean_c:.4f}, target ~1: {frac_within_2pct:.1%} within 2%",
    )


def validate_anomaly_cancellation_z2_z3() -> Verdict:
    """Grok's anomaly check: 'return 0' hardcoded. Without specifying
    fermion content (charges under SU(2), SU(3), U(1)) for the Möbius
    framework, the chiral anomaly index is undefined. Real anomaly
    cancellation in the SM is per-generation arithmetic on hypercharges."""
    return Verdict(
        claim_label="Z2 x Z3 chiral anomaly index = 0 by topology",
        grok_claim=("Net chiral anomaly cancels geometrically via Möbius "
                    "Z2 seam + Z3 Wilson lines, no Green-Schwarz needed"),
        verdict="HARD-CODED",
        evidence=("Grok's 'check_anomaly_cancellation' function literally "
                  "contains 'return 0' with no actual chiral fermion content "
                  "specified. The Möbius Z2 seam pairs LH/RH modes, true; "
                  "but anomaly cancellation requires summing Y^3, [SU(2)]^2 Y, "
                  "[SU(3)]^2 Y, [grav]^2 Y over the actual fermion spectrum. "
                  "The framework has not specified that spectrum."),
        quantitative_test="Source code inspection: function returns the hardcoded value 0",
    )


def validate_topological_seesaw_neutrino_sum() -> Verdict:
    """Grok: m_nu^ij ~ (v^2/M_R) * A^(i+j+4) gives sum m_nu = 0.059 eV.
    The seesaw scale M_R is a free parameter; tuning it gives any sum.
    """
    v = 246e9   # eV
    A = 0.48
    M_R_for_target = []
    targets = [0.06, 0.10, 0.20, 0.50]
    for tgt in targets:
        # Approximate: sum_{i=0..2} (v^2/M_R) * A^(2i+4)
        # Solve for M_R from sum
        coeff = sum(A**(2 * i + 4) for i in range(3))
        M_R = v * v * coeff / tgt
        M_R_for_target.append((tgt, M_R))

    return Verdict(
        claim_label="Topological seesaw: sum m_nu = 0.059 eV from A^n",
        grok_claim=("v^2/M_R * A^n produces sum m_nu = 0.059 eV (matches "
                    "Planck + oscillation data) with normal hierarchy"),
        verdict="TUNABLE",
        evidence=(f"M_R is a free parameter. To match a target sum, "
                  f"M_R must be: " +
                  ", ".join(f"sum={t}eV -> M_R={M:.2e}eV"
                            for t, M in M_R_for_target) +
                  ". Grok did not specify M_R from the framework — just "
                  "claimed it is at the right value. The 0.059 match "
                  "is achievable but not predicted."),
        quantitative_test=f"sum m_nu = (v^2/M_R) * sum_i A^(2i+4) — M_R is the free knob",
    )


def all_verdicts() -> list[Verdict]:
    return [
        validate_su3_area_law(),
        validate_emergent_c_eigenvalue(),
        validate_electroweak_polar_strip(),
        validate_ckm_polar_overlaps(),
        validate_lambda_attractor_gaussian(),
        validate_c_from_string_compactification(),
        validate_anomaly_cancellation_z2_z3(),
        validate_topological_seesaw_neutrino_sum(),
    ]


def verdict_summary() -> dict:
    """One-shot summary of all Grok claim verdicts."""
    verdicts = all_verdicts()
    counts: dict[str, int] = {}
    for v in verdicts:
        counts[v.verdict] = counts.get(v.verdict, 0) + 1
    return {
        "total_claims_tested": len(verdicts),
        "verdict_counts": counts,
        "claims_with_grok_overstatement": sum(
            1 for v in verdicts if v.verdict != "CONFIRMED"
        ),
        "summary": (
            "0 of 8 tested Grok claims survive direct numerical test as "
            "stated. None are CONFIRMED. The honest result: Grok's "
            "extensions are implementable as scaffolds but their "
            "headline 'derivations' are tautological, fabricated, "
            "underspecified, or curve-fits."
        ),
    }


__all__ = [
    "Verdict",
    "validate_su3_area_law",
    "validate_emergent_c_eigenvalue",
    "validate_electroweak_polar_strip",
    "validate_ckm_polar_overlaps",
    "validate_lambda_attractor_gaussian",
    "validate_c_from_string_compactification",
    "validate_anomaly_cancellation_z2_z3",
    "validate_topological_seesaw_neutrino_sum",
    "all_verdicts", "verdict_summary",
]
