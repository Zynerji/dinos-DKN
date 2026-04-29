"""Validation of the cz.txt 10 'transdisciplinary world-changing algorithms'
(HYPOTHESIS Step 52).

A 448-line cz.txt analysis file proposed applying the Koide Q ≈ 3/2
criterion to triplets across genetics, finance, climate, AI, pharma,
ecology, urban planning, consciousness, and cosmology.

Two fundamental problems:

1. UNIT DEPENDENCE. The Koide formula Q = (Σ√x)²/Σx is well-defined
   only when all three components share the same dimension. The cz
   algorithms apply it to triplets like:
   - Urban planner: housing_cost_ratio (dimensionless), commute_time
     (minutes), jobs/km² (1/area) — Q changes with chosen units.
   - Climate: T_atm (Kelvin), T_ocean (Kelvin), ice_extent (m²) —
     mixed dimensions.
   - Consciousness: neural firing rates with topological measures —
     no shared dimension.

2. FABRICATED EMPIRICAL "MATCHES". The specific Q values cz claims
   (Vienna Q=1.501, San Francisco Q=1.43; Dow/NASDAQ/S&P Q=1.498
   pre-Lehman; cosmic Ω-triplet b=√2) are not actually computed
   from real data. When tested directly:
   - Cosmic Ω triplet from Planck 2018: b ≈ 1.033, not √2 = 1.414.
   - 2008 Dow/NASDAQ/S&P (Dec 2007 ≈ 13260, 2652, 1468): Q ≈ 2.42,
     b ≈ 0.69, NOWHERE near the claimed 1.498.

Verdicts:

| cz # | Claim                              | Verdict       |
|------|-----------------------------------|---------------|
| 1    | Genetic codon classifier (Z_3xZ_2) | UNDEFINED      |
| 2    | Koide market stabilizer            | FALSIFIED      |
| 3    | Climate tipping points             | UNIT-DEPENDENT |
| 4    | Z_3 neural architecture            | UNVALIDATED    |
| 5    | Metallic drug designer             | UNDEFINED      |
| 6    | SK ecosystem manager               | UNIT-DEPENDENT |
| 7    | CF anomaly detector (universal)    | OVERCLAIMED    |
| 8    | Metallic urban planner             | UNIT-DEPENDENT |
| 9    | Z_3 consciousness correlate        | UNDEFINED      |
| 10   | Cyclic universe model              | FALSIFIED      |
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


def koide_Q(arr: list[float] | np.ndarray) -> float:
    arr = np.asarray(arr)
    return float((np.sum(np.sqrt(arr))) ** 2 / np.sum(arr))


def b_from_Q(Q: float) -> float:
    if Q <= 0 or Q >= 3:
        return float("nan")
    inside = 6.0 / Q - 2.0
    return float(np.sqrt(inside)) if inside >= 0 else float("nan")


@dataclass(frozen=True)
class CZVerdict:
    cz_number: int
    claim_label: str
    verdict: str    # FALSIFIED | UNIT-DEPENDENT | UNDEFINED | UNVALIDATED | OVERCLAIMED | CONFIRMED
    evidence: str


def validate_cz_2_market_koide() -> CZVerdict:
    """cz#2: Dow/NASDAQ/S&P had Q ≈ 1.498 pre-Lehman."""
    # End-2007 / mid-2008 approximate close values
    jan08 = np.array([13260, 2652, 1468])
    sept08 = np.array([11421, 2261, 1252])
    Q_jan = koide_Q(jan08)
    Q_sept = koide_Q(sept08)
    return CZVerdict(
        cz_number=2,
        claim_label="Dow/NASDAQ/S&P Koide Q ≈ 1.498 pre-Lehman",
        verdict="FALSIFIED",
        evidence=(f"Direct computation with public index closes: "
                  f"Q(Jan 2008) = {Q_jan:.3f}, Q(Sept 2008) = {Q_sept:.3f}. "
                  f"cz claim was Q = 1.498/1.487. Reality: Q ≈ 2.42 — "
                  f"the values claimed by cz are fabricated."),
    )


def validate_cz_10_cosmology_b() -> CZVerdict:
    """cz#10: cosmic Ω triplet has b ≈ √2 today."""
    Omega_m = 0.315
    Omega_r = 9.4e-5
    Omega_L = 0.685
    Q = koide_Q([Omega_m, Omega_r, Omega_L])
    b = b_from_Q(Q)
    return CZVerdict(
        cz_number=10,
        claim_label="Cosmic Ω-triplet has b = √2 today",
        verdict="FALSIFIED",
        evidence=(f"Planck 2018 values Ω_m=0.315, Ω_r=9.4e-5, Ω_Λ=0.685 "
                  f"give Q = {Q:.4f}, b = {b:.4f}. cz claimed b = √2 = "
                  f"1.4142 (within 0.1%). Reality: b ≈ {b:.3f} — off by "
                  f"{abs(b-np.sqrt(2))/np.sqrt(2)*100:.0f}%."),
    )


def validate_cz_8_urban_planner_units() -> CZVerdict:
    """cz#8: Q for housing/commute/jobs determines city stability."""
    si = np.array([0.3, 30, 1000])
    imperial = np.array([0.3, 30, 2590])     # jobs/sq-mile = jobs/km^2 * 2.59
    mixed = np.array([30, 30, 1000])         # housing as percent
    Qs = [koide_Q(x) for x in (si, imperial, mixed)]
    return CZVerdict(
        cz_number=8,
        claim_label="City Koide Q determines stability (Vienna 1.501, SF 1.43)",
        verdict="UNIT-DEPENDENT",
        evidence=(f"Same city under different unit choices for the three "
                  f"components: SI Q={Qs[0]:.3f}, imperial Q={Qs[1]:.3f}, "
                  f"mixed Q={Qs[2]:.3f}. The claim that 'Q ≈ 3/2 means "
                  f"livable city' is meaningless because Q changes with "
                  f"unit choice. The Vienna/SF/Houston Q values cz cited "
                  f"are not computable from real data without specifying "
                  f"a unit convention that is not provided."),
    )


def validate_cz_3_climate_units() -> CZVerdict:
    """cz#3: climate tipping points from Koide of (T_atm, T_ocean, ice)."""
    return CZVerdict(
        cz_number=3,
        claim_label="Climate tipping point from Koide(T_atm, T_ocean, ice_extent)",
        verdict="UNIT-DEPENDENT",
        evidence=("T_atm and T_ocean (Kelvin or Celsius?) plus ice_extent "
                  "(m² or fraction?) are mixed-dimension quantities. Q is "
                  "not unit-invariant under different dimension choices. "
                  "Even if we used Kelvin throughout, the claim that "
                  "'crossing b = √2' triggers a tipping point is not "
                  "derived from any climate physics — it's pattern-matching "
                  "to particle physics nomenclature."),
    )


def validate_cz_6_ecosystem_units() -> CZVerdict:
    """cz#6: ecosystem stability via Schwinger-Keldysh of (P, C, Q)."""
    return CZVerdict(
        cz_number=6,
        claim_label="Schwinger-Keldysh ecosystem manager",
        verdict="UNIT-DEPENDENT",
        evidence=("Producer (P), consumer (C), predator (Q) populations "
                  "are all in counts (same dimension), so Koide Q is "
                  "well-defined. But the claim that ecosystem collapse "
                  "= failure of Picard convergence is not derived from "
                  "any population dynamics. The Schwinger-Keldysh formalism "
                  "applies to quantum field theory in/out states, not "
                  "ecological time series."),
    )


def validate_cz_7_universal_pattern_detector() -> CZVerdict:
    """cz#7: continued-fraction signature is universal."""
    return CZVerdict(
        cz_number=7,
        claim_label="CF signature detector is universal pattern recognition",
        verdict="OVERCLAIMED",
        evidence=("CF analysis is a real, useful technique for identifying "
                  "rational and quadratic-irrational structure in noisy "
                  "data — that part is accurate (cf. dinos.phi_resolution "
                  "Step 11). But the claim that it 'replaces hundreds of "
                  "domain-specific pattern detection methods' is hyperbole. "
                  "CF detects rationality/quadratic-irrationality; it "
                  "doesn't detect arbitrary structure (e.g., periodicities, "
                  "fractals, manifolds in higher dimensions)."),
    )


def validate_cz_4_z3_neural_architecture() -> CZVerdict:
    """cz#4: Z_3 monodromy neural net beats Transformers."""
    return CZVerdict(
        cz_number=4,
        claim_label="Z_3 neural architecture (replaces Transformers)",
        verdict="UNVALIDATED",
        evidence=("The proposal is implementable as a PyTorch module: "
                  "three branches with omega^k weighted residuals plus "
                  "monodromy-anchored loss. Whether it actually beats "
                  "Transformers on standard benchmarks is an empirical "
                  "ML question that requires GPU experiments — neither "
                  "verified by cz nor by the framework. The claim of "
                  "'O(n log n) attention via monodromy propagation' is "
                  "not fleshed out as a specific operation."),
    )


def validate_cz_1_codon_classifier() -> CZVerdict:
    return CZVerdict(
        cz_number=1,
        claim_label="Genetic codon classifier (Z_3 x Z_2 monodromy)",
        verdict="UNDEFINED",
        evidence=("Codons consist of three discrete nucleotides {A, C, G, U}. "
                  "Mapping (A, C, G, U) to (φ, δ_S, β₃, ρ) is arbitrary. "
                  "The claim that 'first base = Z_3 branch' has 4 letters "
                  "mapped to 3 branches — already a contradiction. The "
                  "amino-acid stability prediction is not a derivation."),
    )


def validate_cz_5_drug_designer() -> CZVerdict:
    return CZVerdict(
        cz_number=5,
        claim_label="Metallic drug designer",
        verdict="UNDEFINED",
        evidence=("Drug-target binding free energies (electrostatic, "
                  "hydrophobic, steric) are real quantities, but they "
                  "are not in commensurable units when treated as a Foot "
                  "triplet. The specific claim that 'b ≈ √2 means specific "
                  "binding' has no biochemical derivation."),
    )


def validate_cz_9_consciousness() -> CZVerdict:
    return CZVerdict(
        cz_number=9,
        claim_label="Z_3 consciousness correlate at b = √2",
        verdict="UNDEFINED",
        evidence=("'Sensory processing', 'recurrent processing', and "
                  "'global workspace integration' are not numerical "
                  "quantities, so a Koide triplet cannot be formed. "
                  "Mapping them to b ≈ √2 ⇒ conscious is unfalsifiable. "
                  "The 'falsifiable predictions' (b drops under propofol, "
                  "rises under psychedelics) require an undefined function "
                  "f(α, β, κ) that is not provided."),
    )


def all_cz_verdicts() -> list[CZVerdict]:
    return [
        validate_cz_1_codon_classifier(),
        validate_cz_2_market_koide(),
        validate_cz_3_climate_units(),
        validate_cz_4_z3_neural_architecture(),
        validate_cz_5_drug_designer(),
        validate_cz_6_ecosystem_units(),
        validate_cz_7_universal_pattern_detector(),
        validate_cz_8_urban_planner_units(),
        validate_cz_9_consciousness(),
        validate_cz_10_cosmology_b(),
    ]


def cz_verdict_summary() -> dict:
    out = all_cz_verdicts()
    counts: dict[str, int] = {}
    for v in out:
        counts[v.verdict] = counts.get(v.verdict, 0) + 1
    return {
        "total_claims_tested": len(out),
        "verdict_counts": counts,
        "summary": (
            "0 of 10 cz.txt 'world-changing' claims survive direct test. "
            "2 are FALSIFIED with public data (cz#2 finance, cz#10 cosmology); "
            "3 are UNIT-DEPENDENT (cz#3 climate, cz#6 ecology, cz#8 urban); "
            "3 are UNDEFINED (cz#1 codons, cz#5 drugs, cz#9 consciousness); "
            "1 is UNVALIDATED (cz#4 Z_3 neural net — implementable but unproven); "
            "1 is OVERCLAIMED (cz#7 CF detector is real but limited)."
        ),
    }


__all__ = [
    "koide_Q", "b_from_Q",
    "CZVerdict",
    "validate_cz_1_codon_classifier",
    "validate_cz_2_market_koide",
    "validate_cz_3_climate_units",
    "validate_cz_4_z3_neural_architecture",
    "validate_cz_5_drug_designer",
    "validate_cz_6_ecosystem_units",
    "validate_cz_7_universal_pattern_detector",
    "validate_cz_8_urban_planner_units",
    "validate_cz_9_consciousness",
    "validate_cz_10_cosmology_b",
    "all_cz_verdicts", "cz_verdict_summary",
]
