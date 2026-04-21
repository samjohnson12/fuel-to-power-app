
"""
Unit conversions for fuel quantities → energy/day.

Conversion factors sourced from:
https://www.eia.gov/energyexplained/units-and-calculators/energy-conversion-calculators.php

Design choice:
- Keep all internal energy in BTU/day and MMBtu/day helpers.
- Defaults here are editable "starter" values; you can replace with contract-specific values.

Notes:
- 1 MMBtu = 1,000,000 BTU exactly by definition.
- 1 MCF = 1,000 scf by definition.
"""

from __future__ import annotations
from dataclasses import dataclass


BTU_PER_MMBTU = 1_000_000.0
SCF_PER_MCF = 1000.0


@dataclass(frozen=True)
class FuelDefaults:
    """Default heating values and conversion factors (user-editable in UI)."""
    diesel_btu_per_gal: float = 137_381.0   # typical ballpark; confirm for your fuel spec
    ng_btu_per_scf: float = 1_036.0         # typical ballpark; varies by gas quality
    dth_to_mmbtu: float = 1.0               # dekatherm-to-MMBtu factor (often ~1.0 in practice)


# ---------------------------
# Fuel -> Energy (forward)
# ---------------------------

def diesel_gal_per_day_to_btu_per_day(gal_per_day: float, diesel_btu_per_gal: float) -> float:
    return gal_per_day * diesel_btu_per_gal


def mmbtu_per_day_to_btu_per_day(mmbtu_per_day: float) -> float:
    return mmbtu_per_day * BTU_PER_MMBTU


def dth_per_day_to_mmbtu_per_day(dth_per_day: float, dth_to_mmbtu: float) -> float:
    return dth_per_day * dth_to_mmbtu


def mcf_per_day_to_mmbtu_per_day(mcf_per_day: float, ng_btu_per_scf: float) -> float:
    """Convert MCF/day (1000 scf/day) to MMBtu/day using gas BTU/scf."""
    btu_per_mcf = ng_btu_per_scf * 1000.0
    return (mcf_per_day * btu_per_mcf) / BTU_PER_MMBTU

# ---------------------------
# Energy -> Fuel (inverse)
# ---------------------------

def btu_per_day_to_mmbtu_per_day(btu_per_day: float) -> float:
    return btu_per_day / BTU_PER_MMBTU


def btu_per_day_to_diesel_gal_per_day(btu_per_day: float, diesel_btu_per_gal: float) -> float:
    if diesel_btu_per_gal <= 0:
        raise ValueError("diesel_btu_per_gal must be > 0.")
    return btu_per_day / diesel_btu_per_gal


def btu_per_day_to_dth_per_day(btu_per_day: float, dth_to_mmbtu: float) -> float:
    """Convert BTU/day to dekatherms/day using the Dth->MMBtu factor."""
    if dth_to_mmbtu <= 0:
        raise ValueError("dth_to_mmbtu must be > 0.")
    mmbtu_day = btu_per_day_to_mmbtu_per_day(btu_per_day)
    return mmbtu_day / dth_to_mmbtu


def btu_per_day_to_mcf_per_day(btu_per_day: float, ng_btu_per_scf: float) -> float:
    """Convert BTU/day to MCF/day using gas BTU/scf."""
    if ng_btu_per_scf <= 0:
        raise ValueError("ng_btu_per_scf must be > 0.")
    btu_per_mcf = ng_btu_per_scf * SCF_PER_MCF
    return btu_per_day / btu_per_mcf
