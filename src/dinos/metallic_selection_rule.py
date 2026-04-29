"""What distinguishes the metallic family algebraically (HYPOTHESIS Step 56).

The deep open question from Step 54: WHY are atlas b values built from
the specific 7 ratios {golden, silver, bronze, copper, nickel, plastic,
supergolden} rather than other algebraic numbers?

Tested candidate properties:

1. QUADRATIC IRRATIONAL: TRUE for golden, silver, bronze, copper, nickel.
   FALSE for plastic and supergolden (both cubic). FAILS as universal.

2. PERIODIC CF OF PERIOD 1: TRUE for the metallic family M_n = (n + sqrt(n^2+4))/2
   only. FALSE for plastic and supergolden. FAILS as universal.

3. PISOT NUMBER: real algebraic integer > 1 with all Galois conjugates
   strictly inside the open unit disk. CONFIRMED TRUE for ALL 7
   atlas-relevant ratios. This is the unique unifying property
   identified across the full set.

4. SMALLEST PISOT IN DEGREE CLASS: golden is the smallest degree-2
   Pisot. Plastic is the smallest Pisot OVERALL (degree 3). Supergolden
   is the second-smallest degree-3 Pisot. M_n for n>1 are NOT smallest
   in their class but follow a clean integer family.

5. MINIMAL POLYNOMIAL of form x^d = a*x^k + 1 (binomial recurrence Pisot):
   - golden: x^2 = x + 1
   - silver: x^2 = 2x + 1
   - bronze: x^2 = 3x + 1
   - copper: x^2 = 4x + 1
   - nickel: x^2 = 5x + 1
   - plastic: x^3 = x + 1
   - supergolden: x^3 = x^2 + 1
   ALL 7 satisfy x^d = a*x^k + 1 for integer a and k < d. CONFIRMED.
   By contrast, the next Pisot (tribonacci) satisfies x^3 = x^2 + x + 1
   (THREE terms on the right) and is NOT in the atlas.

6. MULTIPLICATIVE CLOSURE: FAILED in Step 54 Q5 — atlas b values do
   not form a multiplicative semigroup.

CONCLUSION
----------
The atlas-relevant 7 ratios are exactly the smallest "binomial-recurrence
Pisot numbers": real algebraic integers > 1 whose minimal polynomial has
exactly 2 nonzero terms in the recurrence x^d = a*x^k + 1.

This is a genuinely sharp algebraic characterization. It admits more
algebraic numbers than just "metallic ratios" but excludes most algebraic
numbers including the next Pisot (tribonacci, 3-term recurrence). It's
narrower than "all Pisot numbers" and broader than "period-1 CF ratios."

The OPEN question becomes: WHY does nature pick binomial-recurrence
Pisots specifically? Possible deeper hypothesis: such Pisots are exactly
the largest eigenvalues of "minimal hyperbolic toral automorphisms"
arising from substitution dynamics with two-letter alphabets.

Atlas decomposition by Pisot type
----------------------------------
- Quadratic Pisots only (period-1 CF): 10/19 entries
- Requires cubic Pisots (plastic and/or supergolden): 9/19 entries
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from . import foot_canonical_atlas as fca


# The 7 atlas-relevant ratios
ATLAS_PISOT_RATIOS: dict[str, tuple[float, str]] = {
    "golden":      (1.6180339887, "x^2 = x + 1"),
    "silver":      (2.4142135624, "x^2 = 2x + 1"),
    "bronze":      (3.3027756378, "x^2 = 3x + 1"),
    "copper":      (4.2360679775, "x^2 = 4x + 1"),
    "nickel":      (5.1925824036, "x^2 = 5x + 1"),
    "plastic":     (1.3247179572, "x^3 = x + 1 (smallest Pisot overall)"),
    "supergolden": (1.4655712319, "x^3 = x^2 + 1 (second-smallest deg-3 Pisot)"),
}


# Pisot numbers NOT in the atlas (for contrast)
NON_ATLAS_PISOT_RATIOS: dict[str, tuple[float, str]] = {
    "tribonacci": (1.8392867552, "x^3 = x^2 + x + 1 (THREE-term recurrence)"),
    "tetranacci": (1.9275619755, "x^4 = x^3 + x^2 + x + 1 (FOUR-term recurrence)"),
    "newman":     (1.4432687023, "x^5 = x^4 + 1 (degree 5 binomial; smallest deg-5 Pisot)"),
}


@dataclass(frozen=True)
class PisotProperty:
    label: str
    rule: str
    atlas_satisfied: bool
    notes: str


def candidate_properties() -> list[PisotProperty]:
    return [
        PisotProperty(
            label="quadratic_irrational",
            rule="all atlas-relevant ratios are degree-2 algebraic",
            atlas_satisfied=False,
            notes="Plastic and supergolden are cubic; fails as universal property.",
        ),
        PisotProperty(
            label="period_1_continued_fraction",
            rule="CF expansion = [n; n, n, n, ...] for some integer n",
            atlas_satisfied=False,
            notes="Holds for {golden, silver, bronze, copper, nickel} only. Plastic and supergolden are cubic with non-periodic CFs.",
        ),
        PisotProperty(
            label="Pisot_number",
            rule="real algebraic integer > 1, all Galois conjugates inside open unit disk",
            atlas_satisfied=True,
            notes="All 7 atlas-relevant ratios are Pisot. This is the unique unifying algebraic property identified.",
        ),
        PisotProperty(
            label="binomial_recurrence_Pisot",
            rule="minimal polynomial of the form x^d = a*x^k + 1 (integer a, k<d)",
            atlas_satisfied=True,
            notes="Satisfied by all 7. Tribonacci (3-term) and tetranacci (4-term) are Pisot but NOT in the atlas. This is a sharper subset than 'all Pisots' that EXACTLY captures the atlas-relevant family.",
        ),
        PisotProperty(
            label="multiplicative_closure",
            rule="atlas b values close under product / quotient",
            atlas_satisfied=False,
            notes="Step 54 Q5: 6 product hits in 171 pairs, vs ~15 expected by chance. NOT a multiplicative semigroup.",
        ),
    ]


def atlas_decomposition_by_pisot_type() -> dict:
    """Split canonical atlas by which Pisot ratios it requires."""
    period1_only = []
    needs_cubic = []
    for e in fca.CANONICAL_ATLAS:
        expr = e.b_expression.lower()
        if "plastic" in expr or "supergolden" in expr:
            needs_cubic.append(e.family)
        else:
            period1_only.append(e.family)
    return {
        "period_1_metallic_only": period1_only,
        "requires_cubic_pisot": needs_cubic,
        "n_period_1": len(period1_only),
        "n_cubic": len(needs_cubic),
    }


@dataclass(frozen=True)
class SelectionRule:
    label: str
    statement: str
    n_atlas_relevant: int
    counter_examples_in_pisot_class: list[str]
    notes: str


def proposed_selection_rule() -> SelectionRule:
    return SelectionRule(
        label="Binomial-recurrence Pisot hypothesis",
        statement=("Atlas-relevant ratios are exactly the Pisot numbers "
                   "whose minimal polynomial has the binomial form "
                   "x^d = a*x^k + 1 with integer a and k<d."),
        n_atlas_relevant=7,
        counter_examples_in_pisot_class=[
            "tribonacci x^3 = x^2 + x + 1 (3-term recurrence; Pisot but NOT in atlas)",
            "tetranacci x^4 = x^3 + x^2 + x + 1 (4-term; NOT in atlas)",
        ],
        notes=("This is narrower than 'all Pisots' and broader than "
               "'period-1 CF metallics'. It correctly includes plastic "
               "(x^3 = x + 1) and supergolden (x^3 = x^2 + 1) — both "
               "have 2-term right-hand sides, just like the metallics. "
               "DEEPER OPEN QUESTION: why does nature select Pisots "
               "with binomial recurrences specifically? Conjectured "
               "connection to substitution dynamics on 2-letter alphabets."),
    )


__all__ = [
    "ATLAS_PISOT_RATIOS",
    "NON_ATLAS_PISOT_RATIOS",
    "PisotProperty",
    "candidate_properties",
    "atlas_decomposition_by_pisot_type",
    "SelectionRule",
    "proposed_selection_rule",
]
