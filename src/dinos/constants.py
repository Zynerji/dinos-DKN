"""Physical constants and DKN-paper numerical values.

All values drawn from the reference paper unless noted. Natural units (ℏ=c=1)
are assumed in closure/Casimir formulas; SI conversions supplied.
"""

from math import pi

# -----------------------------------------------------------------------------
# Fundamental constants (CODATA 2018 / PDG 2022)
# -----------------------------------------------------------------------------
c_SI = 2.99792458e8            # m/s  (exact)
hbar_SI = 1.054571817e-34      # J·s
eV = 1.602176634e-19           # J     (exact)
hbar_c_eV_m = 1.97326980e-7    # eV·m
hbar_c_MeV_fm = 197.326980     # MeV·fm

# -----------------------------------------------------------------------------
# Electron parameters (paper §5.1 / PDG)
# -----------------------------------------------------------------------------
m_e_MeV = 0.51099895           # electron rest energy, MeV
m_e_kg = 9.1093837015e-31      # electron mass, kg
alpha_EM = 7.2973525693e-3     # fine-structure constant α = e²/(ℏc)
Q_electron_natural = 1.0       # in units where e² = α·ℏc ⇒ Q = e

# Reduced Compton wavelength λ_C = ℏ/(m_e c); Compton radius a = ℏ/(2 m_e c)
lambda_C_m = hbar_SI / (m_e_kg * c_SI)     # ≈ 3.8616e-13 m
a_Compton_m = lambda_C_m / 2.0             # ≈ 1.9308e-13 m
lambda_C_MeV_inv = 1.0 / m_e_MeV           # natural units: λ_C = 1/m_e
a_Compton_MeV_inv = 1.0 / (2.0 * m_e_MeV)  # natural units: a = 1/(2 m_e)

# -----------------------------------------------------------------------------
# DKN structural constants (paper §9-§16)
# -----------------------------------------------------------------------------

# MIT-bag / Boyer Casimir constant for a massless Dirac field confined to a
# spherical cavity (Milton 1978; paper eq. 43).
C_bag_Dirac = 0.17695

# Boyer's conducting-sphere photon Casimir (paper eq. 79 discussion).
C_Meissner_photon = 0.0462

# Bulk Higgs scalar (single real, Dirichlet) Casimir (paper eq. 79).
C_Higgs_bulk = 0.0113

# Derrick virial gap that must be closed (paper §12.2, Theorem 12.4).
DELTA_C = 0.153  # = 1/3 - (C_Dirac + α/2)

# Required residual scalar-sector Casimir (paper eq. 79):
#   C_Phi^req = ΔC - C_Meissner - C_Higgs_bulk
C_Phi_req = DELTA_C - C_Meissner_photon - C_Higgs_bulk  # ≈ 0.0955

# Joint-closure single-point prediction (paper eq. 81 / Remark 16.14)
m_star_MeV = 0.156                   # hidden scalar mass (central value)
m_star_MeV_err = 0.025                # 1σ uncertainty
lambda_H_DKN = 0.129                 # DKN scalar self-coupling
lambda_H_DKN_err = 0.060             # 1σ uncertainty
m_star_times_a_dimless = 0.153       # dimensionless m*·a
m_star_times_a_err = 0.025

# Bag VEV and Yukawa (paper §14.2, eq. 66; §16.6)
v_bag_MeV = 0.43                     # Higgs VEV inside bag
y_e_DKN = m_e_MeV / v_bag_MeV        # ≈ 1.19 (paper: "≈ 1.2")

# SM Higgs parameters for cross-reference
v_SM_GeV = 246.0
lambda_H_SM = 0.129                  # m_H²/(2 v_SM²) for m_H ≃ 125 GeV

# Fractional decomposition of m_e c² (paper Corollary 14.3, Table)
FRACTION_HIGGS_WALL = 0.63880        # 1 - 2C - α
FRACTION_DIRAC_CASIMIR = 0.35390     # 2C
FRACTION_EM_SELF = 0.00730           # α

# Electron charge radius prediction (paper eq. 47)
r_e_squared_m2 = 3.7e-26             # ⟨r_e²⟩ = (3/5) a² in m²

# -----------------------------------------------------------------------------
# Unit-conversion helpers
# -----------------------------------------------------------------------------

def natural_to_SI_length(L_eV_inv: float) -> float:
    """Convert inverse-eV length to meters."""
    return L_eV_inv * hbar_c_eV_m

def SI_to_natural_length(L_m: float) -> float:
    """Convert meters to inverse-eV length."""
    return L_m / hbar_c_eV_m

__all__ = [
    "pi", "c_SI", "hbar_SI", "eV", "hbar_c_eV_m", "hbar_c_MeV_fm",
    "m_e_MeV", "m_e_kg", "alpha_EM", "Q_electron_natural",
    "lambda_C_m", "a_Compton_m", "lambda_C_MeV_inv", "a_Compton_MeV_inv",
    "C_bag_Dirac", "C_Meissner_photon", "C_Higgs_bulk",
    "DELTA_C", "C_Phi_req",
    "m_star_MeV", "m_star_MeV_err", "lambda_H_DKN", "lambda_H_DKN_err",
    "m_star_times_a_dimless", "m_star_times_a_err",
    "v_bag_MeV", "y_e_DKN", "v_SM_GeV", "lambda_H_SM",
    "FRACTION_HIGGS_WALL", "FRACTION_DIRAC_CASIMIR", "FRACTION_EM_SELF",
    "r_e_squared_m2",
    "natural_to_SI_length", "SI_to_natural_length",
]
