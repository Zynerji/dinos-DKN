"""Quark sector Foot+Koide test (HYPOTHESIS Step 10a).

Tests whether the Foot+Koide derivation (Step 8) extends to quarks.

The lepton Koide ratio Q = (Sum sqrt m)^2 / Sum m  is empirically
3/2, which gives b = sqrt(2) algebraically. If quarks satisfied the
same Koide formula, the same Foot construction would apply with the
same b -- a unified mass formula across leptons and quarks.

Empirically: quarks do NOT satisfy lepton Koide. Each sector
(up-type vs down-type) has its own Q and implied b. This module
documents the negative result quantitatively.

Honest scope statement
----------------------
- This module CAN: compute Q for each quark sector, derive implied b,
  compare to lepton b = sqrt(2).
- This module CANNOT: derive quark masses (per-quark sigma is still
  required; see dinos.quarks).

Negative-result framing
-----------------------
The lepton tower has Q = 3/2 (empirically); the quark sectors do not.
Each quark sector has its OWN b value. This means:

(a) The lepton Koide is NOT a universal feature of all 3-generation
    fermion towers.
(b) Quark Foot+Koide is consistent (each sector has a b), but the
    UNIVERSAL lepton-derived constants (b = sqrt(2)) do not transfer.
(c) A unified quark+lepton mass formula would need additional input
    (running scale corrections, mixing matrix, etc).
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from . import generations_extended


# -----------------------------------------------------------------------------
# Empirical quark masses (PDG 2022, MS-bar at 2 GeV unless noted)
# -----------------------------------------------------------------------------

QUARK_MASSES_MeV: dict[str, float] = {
    "u": 2.16,         # current quark, charge +2/3
    "d": 4.67,         # current quark, charge -1/3
    "s": 93.4,         # current quark, charge -1/3
    "c": 1273.0,       # m_c(m_c) running, charge +2/3
    "b": 4180.0,       # m_b(m_b) running, charge -1/3
    "t": 172700.0,     # pole mass, charge +2/3
}

QUARK_CHARGES: dict[str, float] = {
    "u":  2.0 / 3.0,  "d": -1.0 / 3.0,
    "s": -1.0 / 3.0,  "c":  2.0 / 3.0,
    "b": -1.0 / 3.0,  "t":  2.0 / 3.0,
}


# -----------------------------------------------------------------------------
# Sector Koide computations
# -----------------------------------------------------------------------------

def koide_for_up_sector() -> float:
    """Q for (u, c, t) — up-type quarks."""
    return generations_extended.koide_q([
        QUARK_MASSES_MeV["u"], QUARK_MASSES_MeV["c"], QUARK_MASSES_MeV["t"],
    ])


def koide_for_down_sector() -> float:
    """Q for (d, s, b) — down-type quarks."""
    return generations_extended.koide_q([
        QUARK_MASSES_MeV["d"], QUARK_MASSES_MeV["s"], QUARK_MASSES_MeV["b"],
    ])


def koide_for_pair_sums() -> float:
    """Q for (m_u+m_d, m_c+m_s, m_t+m_b) — generation-paired quarks."""
    return generations_extended.koide_q([
        QUARK_MASSES_MeV["u"] + QUARK_MASSES_MeV["d"],
        QUARK_MASSES_MeV["c"] + QUARK_MASSES_MeV["s"],
        QUARK_MASSES_MeV["t"] + QUARK_MASSES_MeV["b"],
    ])


def koide_for_geometric_means() -> float:
    """Q for sqrt(m_u·m_d), sqrt(m_c·m_s), sqrt(m_t·m_b)."""
    return generations_extended.koide_q([
        float(np.sqrt(QUARK_MASSES_MeV["u"] * QUARK_MASSES_MeV["d"])),
        float(np.sqrt(QUARK_MASSES_MeV["c"] * QUARK_MASSES_MeV["s"])),
        float(np.sqrt(QUARK_MASSES_MeV["t"] * QUARK_MASSES_MeV["b"])),
    ])


def b_from_koide_q(q: float) -> float:
    """Foot b parameter from Koide Q via Q = 3/(1 + b^2/2)."""
    if q <= 0 or q > 3.0:
        raise ValueError(f"Q = {q} outside Foot range (0, 3]")
    return float(np.sqrt(6.0 / q - 2.0))


# -----------------------------------------------------------------------------
# Summary
# -----------------------------------------------------------------------------

@dataclass(frozen=True)
class QuarkKoideReport:
    up_q: float
    down_q: float
    pair_sum_q: float
    geom_mean_q: float
    up_b: float
    down_b: float
    lepton_b: float
    lepton_q: float
    matches_lepton_template: bool
    notes: str


LEPTON_KOIDE_Q: float = 1.5   # canonical 3/2
LEPTON_FOOT_B: float = float(np.sqrt(2.0))


def quark_koide_report() -> QuarkKoideReport:
    """Aggregate the four quark Koide groupings + comparison to lepton."""
    up_q = koide_for_up_sector()
    down_q = koide_for_down_sector()
    pair_q = koide_for_pair_sums()
    geom_q = koide_for_geometric_means()
    up_b = b_from_koide_q(up_q)
    down_b = b_from_koide_q(down_q)

    # Match if both sectors are within 5% of lepton b.
    matches = (
        abs(up_b - LEPTON_FOOT_B) / LEPTON_FOOT_B < 0.05
        and abs(down_b - LEPTON_FOOT_B) / LEPTON_FOOT_B < 0.05
    )

    notes = (
        f"Up-type Q = {up_q:.4f} (b = {up_b:.4f}). "
        f"Down-type Q = {down_q:.4f} (b = {down_b:.4f}). "
        f"Lepton Q = {LEPTON_KOIDE_Q:.4f} (b = sqrt(2) = {LEPTON_FOOT_B:.4f}). "
        f"Quarks DO NOT satisfy lepton Koide -- each sector has its own b. "
        f"Conclusion: lepton b = sqrt(2) is NOT universal across fermion families. "
        f"A unified mass formula across quarks and leptons would need "
        f"additional input (running corrections, mixing matrix, etc)."
    )
    return QuarkKoideReport(
        up_q=up_q,
        down_q=down_q,
        pair_sum_q=pair_q,
        geom_mean_q=geom_q,
        up_b=up_b,
        down_b=down_b,
        lepton_b=LEPTON_FOOT_B,
        lepton_q=LEPTON_KOIDE_Q,
        matches_lepton_template=matches,
        notes=notes,
    )


__all__ = [
    "QUARK_MASSES_MeV", "QUARK_CHARGES",
    "LEPTON_KOIDE_Q", "LEPTON_FOOT_B",
    "koide_for_up_sector", "koide_for_down_sector",
    "koide_for_pair_sums", "koide_for_geometric_means",
    "b_from_koide_q",
    "QuarkKoideReport", "quark_koide_report",
]
