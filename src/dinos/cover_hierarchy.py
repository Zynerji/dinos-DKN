"""A^n cover hierarchy scaling (HYPOTHESIS Step 45b).

Honest scope
------------
This module DOES:
  - Compute the suppression factor A^n for given Möbius contraction
    A in [0.34, 0.66] and integer winding n.
  - Compute the cover-winding required to suppress an input scale
    (e.g. Planck) to a target scale (e.g. electron mass).
  - Show that any electron-to-Planck ratio is reachable for some
    A and n — this is a PARAMETER MAP, not a derivation of why the
    electron is light.

This module DOES NOT:
  - Derive A from any deeper principle. A is an output of the
    `closure.enforce_mobius_fixed_point` numerical search, but
    its value (~0.34-0.66 in the existing tests) reflects the
    tuned parameters.
  - Solve the hierarchy problem. The hierarchy problem is *why* the
    Higgs mass is light against radiative corrections, not "fit
    the electron-Planck ratio with some A^n."
"""

from __future__ import annotations

from dataclasses import dataclass
from math import log

import numpy as np


# Reference scales (eV)
M_PLANCK_EV: float = 1.22e28
M_ELECTRON_EV: float = 5.110e5


@dataclass(frozen=True)
class HierarchySuppression:
    A: float
    n_cover: int
    suppression_factor: float
    suppressed_value_GeV: float
    initial_scale_GeV: float


def suppression(A: float, n_cover: int,
                 initial_scale_GeV: float = M_PLANCK_EV * 1e-9) -> HierarchySuppression:
    """A^n_cover suppression of an input scale."""
    factor = A ** n_cover
    return HierarchySuppression(
        A=float(A),
        n_cover=int(n_cover),
        suppression_factor=float(factor),
        suppressed_value_GeV=float(initial_scale_GeV * factor),
        initial_scale_GeV=float(initial_scale_GeV),
    )


def n_cover_to_reach_target(A: float,
                             initial_scale_GeV: float = M_PLANCK_EV * 1e-9,
                             target_scale_GeV: float = M_ELECTRON_EV * 1e-9
                             ) -> dict:
    """Number of cover windings n s.t. A^n * initial = target.
    Returns the (in general non-integer) n required."""
    if A <= 0 or A >= 1:
        return {
            "A": A, "n_required_real": float("nan"),
            "feasible": False,
            "note": "A must be in (0, 1) for suppression",
        }
    n = log(target_scale_GeV / initial_scale_GeV) / log(A)
    return {
        "A": A,
        "n_required_real": float(n),
        "n_required_int": int(round(n)),
        "exact_with_int_n": float(initial_scale_GeV * A ** round(n)),
        "feasible": True,
        "note": ("This is a parameter MAP, not a derivation. "
                 "Any electron-to-Planck ratio is reachable for some A."),
    }


__all__ = [
    "M_PLANCK_EV", "M_ELECTRON_EV",
    "HierarchySuppression", "suppression",
    "n_cover_to_reach_target",
]
