"""Δῖνος (Dinos) — Dirac–Kerr–Newman electron-as-quantized-Kerr-resonator toolkit.

Reference: Knopp, "The electron as a quantized Kerr resonator with an antipodal
Higgs boundary: a rigorous geometric synthesis of the Dirac–Kerr–Newman soliton"
(2026).
"""

from . import constants, closure, dm, geodesic, cp, casimir, verify

__version__ = "0.1.0"
__all__ = ["constants", "closure", "dm", "geodesic", "cp", "casimir", "verify"]
