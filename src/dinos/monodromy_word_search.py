"""SL(2,Z) monodromy word search (Algorithm #6 expansion; HYPOTHESIS Step 51d).

Honest scope
------------
This module DOES:
  - Generate all SL(2,Z) words of bounded length L over the standard
    generators S = [[0, -1], [1, 0]] and T = [[1, 1], [0, 1]] (and inverses).
  - Compute |Tr(M)| for each word M.
  - Match each atlas b value to the closest |Tr|/2; report the
    fraction of atlas b's matched within tolerance.

This module DOES NOT:
  - Prove that atlas b values are SL(2,Z) traces. The test in Step 50
    showed lepton b = √2 matches exactly via silver hyperbolic generator;
    here we extend the search to all SL(2,Z) words up to length 8 to
    see if more atlas b's land on hyperbolic-element traces.

Verdict on cj2 #1 conjecture:
  - With INTEGER traces |Tr|/2 ∈ {0, 0.5, 1.0, 1.5, ...}, no atlas b
    other than the integer/half-integer cases can match.
  - For the more permissive interpretation (eigenvalue M of an SL(2,R)
    hyperbolic element gives |Tr|/2 = (M + 1/M)/2), the conjecture
    works for the silver/lepton case (b = √2 = (silver + 1/silver)/2)
    but fails for the smaller atlas b's (vector mesons, B mesons, etc.)
    because (M + 1/M)/2 ≥ 1 for all real M, while atlas b's range
    down to 0.018.
  - VERDICT: PARTIAL.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from . import foot_atlas_discrimination as fad
from . import metallic_invariant_sweep as mis


# Standard SL(2,Z) generators
S = np.array([[0, -1], [1, 0]], dtype=int)
T = np.array([[1, 1], [0, 1]], dtype=int)
T_INV = np.array([[1, -1], [0, 1]], dtype=int)
S_INV = np.array([[0, 1], [-1, 0]], dtype=int)
GENS = [S, T, T_INV, S_INV]


def generate_sl2z_traces(max_length: int = 8) -> set[int]:
    """Generate distinct |Tr(M)| values for words of length ≤ max_length."""
    seen_words: set[tuple[int, int, int, int]] = set()
    traces: set[int] = set()

    def explore(M: np.ndarray, depth: int) -> None:
        if depth > max_length:
            return
        key = tuple(int(x) for x in M.flatten())
        if key in seen_words:
            return
        seen_words.add(key)
        traces.add(int(abs(np.trace(M))))
        for g in GENS:
            explore(M @ g, depth + 1)

    explore(np.eye(2, dtype=int), 0)
    return traces


def hyperbolic_trace_from_eigenvalue(M: float) -> float:
    """For an SL(2,R) hyperbolic element with positive real eigenvalue M,
    the trace is M + 1/M. Returns |Tr|/2 = (M + 1/M)/2."""
    return float((M + 1.0 / M) / 2.0)


@dataclass(frozen=True)
class WordSearchReport:
    max_length: int
    n_distinct_integer_traces: int
    integer_traces: list[int]
    integer_trace_div2: list[float]
    n_atlas_b_within_5pct: int
    n_atlas_total: int
    notes: str


def search_atlas_against_sl2z_traces(max_length: int = 8,
                                      tolerance_pct: float = 5.0
                                      ) -> WordSearchReport:
    traces = generate_sl2z_traces(max_length)
    half_traces = sorted({float(t) / 2.0 for t in traces})
    atlas_bs = [fad.implied_b(masses) for masses in fad.ATLAS_19_MASSES.values()]
    n_within = 0
    for b in atlas_bs:
        if not half_traces:
            continue
        nearest = min(half_traces, key=lambda t: abs(t - b))
        if abs(nearest - b) / b * 100 < tolerance_pct:
            n_within += 1
    return WordSearchReport(
        max_length=max_length,
        n_distinct_integer_traces=len(traces),
        integer_traces=sorted(traces),
        integer_trace_div2=half_traces,
        n_atlas_b_within_5pct=n_within,
        n_atlas_total=len(atlas_bs),
        notes=("Integer-trace test: atlas b values do NOT generally "
               "match |Tr|/2 of SL(2,Z) integer matrices, because integer "
               "traces give half-integer values {0, 0.5, 1.0, ...} but "
               "atlas b's range continuously from 0.018 to 1.41."),
    )


def hyperbolic_match_atlas() -> dict:
    """For each metallic ratio M_n, compute (M+1/M)/2 and match to atlas b."""
    metallic = {
        "golden": mis.GOLDEN, "silver": mis.SILVER, "bronze": mis.BRONZE,
        "copper": mis.COPPER, "nickel": mis.NICKEL,
        "plastic": mis.PLASTIC, "supergolden": mis.SUPERGOLDEN,
    }
    half_traces = {name: hyperbolic_trace_from_eigenvalue(M)
                   for name, M in metallic.items()}
    atlas_bs = {fam: fad.implied_b(masses)
                for fam, masses in fad.ATLAS_19_MASSES.items()}
    matches = {}
    for fam, b in atlas_bs.items():
        nearest_name = min(half_traces.keys(),
                           key=lambda n: abs(half_traces[n] - b))
        rel = abs(half_traces[nearest_name] - b) / b * 100
        matches[fam] = {
            "atlas_b": b,
            "nearest_metallic_hyperbolic": nearest_name,
            "predicted_trace_div2": half_traces[nearest_name],
            "rel_error_pct": rel,
        }
    return {
        "atlas_size": len(atlas_bs),
        "n_matches_within_1pct": sum(1 for v in matches.values()
                                      if v["rel_error_pct"] < 1.0),
        "matches": matches,
        "verdict": ("PARTIAL: silver hyperbolic gives lepton b exactly "
                    "(silver -> sqrt(2) = (1+sqrt(2) + 1/(1+sqrt(2)))/2). "
                    "Other metallic hyperbolic traces are all >= 1, so "
                    "atlas b's below 1 cannot match this construction."),
    }


__all__ = [
    "S", "T", "T_INV", "S_INV", "GENS",
    "generate_sl2z_traces", "hyperbolic_trace_from_eigenvalue",
    "WordSearchReport", "search_atlas_against_sl2z_traces",
    "hyperbolic_match_atlas",
]
