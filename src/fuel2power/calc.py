
"""
Calculation engine: fuel energy/day + heat rate → kWh/day and kW.

Assumptions:
- Heat rate is constant.
- Fuel amount provided is total available per day.
- If operating-hours < 24, the "operating kW" assumes the same daily energy is produced during
  only those operating hours (i.e., higher average output while running).
- In inverse mode, "target operating kW" is the average power while running for the given hours/day.
"""

from __future__ import annotations
from dataclasses import dataclass


@dataclass(frozen=True)
class PowerResult:
    """Results for a single scenario."""
    kwh_per_day: float
    avg_kw_24h: float
    operating_kw: float
    hours_per_day: float


@dataclass(frozen=True)
class FuelEnergyRequirement:
    """Results for an inverse calculation (target power → required fuel energy).

    Attributes:
        target_operating_kw: Target average kW while operating.
        hours_per_day: Operating hours/day used for sizing.
        heat_rate_btu_per_kwh: Heat rate used for sizing.
        required_kwh_per_day: Required electrical energy per day (kWh/day).
        required_btu_per_day: Required fuel energy per day (BTU/day).
    """
    target_operating_kw: float
    hours_per_day: float
    heat_rate_btu_per_kwh: float
    required_kwh_per_day: float
    required_btu_per_day: float


def btu_per_day_to_kwh_per_day(btu_per_day: float, heat_rate_btu_per_kwh: float) -> float:
    if heat_rate_btu_per_kwh <= 0:
        raise ValueError("Heat rate must be > 0.")
    return btu_per_day / heat_rate_btu_per_kwh


def kwh_per_day_to_avg_kw(kwh_per_day: float) -> float:
    return kwh_per_day / 24.0


def kwh_per_day_to_operating_kw(kwh_per_day: float, hours_per_day: float) -> float:
    if hours_per_day <= 0:
        raise ValueError("Hours per day must be > 0.")
    return kwh_per_day / hours_per_day


def compute_power(btu_per_day: float, heat_rate_btu_per_kwh: float, hours_per_day: float) -> PowerResult:
    kwh_day = btu_per_day_to_kwh_per_day(btu_per_day, heat_rate_btu_per_kwh)
    return PowerResult(
        kwh_per_day=kwh_day,
        avg_kw_24h=kwh_per_day_to_avg_kw(kwh_day),
        operating_kw=kwh_per_day_to_operating_kw(kwh_day, hours_per_day),
        hours_per_day=hours_per_day,
    )

def compute_required_fuel_energy(
    target_operating_kw: float,
    hours_per_day: float,
    heat_rate_btu_per_kwh: float,
) -> FuelEnergyRequirement:
    """Inverse calculation: compute required BTU/day to achieve a target operating kW.

    target_operating_kw is interpreted as the average kW while running (during hours_per_day).
    """
    if target_operating_kw < 0:
        raise ValueError("target_operating_kw must be >= 0.")
    if hours_per_day <= 0:
        raise ValueError("hours_per_day must be > 0.")
    if heat_rate_btu_per_kwh <= 0:
        raise ValueError("heat_rate_btu_per_kwh must be > 0.")

    required_kwh_per_day = target_operating_kw * hours_per_day
    required_btu_per_day = required_kwh_per_day * heat_rate_btu_per_kwh

    return FuelEnergyRequirement(
        target_operating_kw=target_operating_kw,
        hours_per_day=hours_per_day,
        heat_rate_btu_per_kwh=heat_rate_btu_per_kwh,
        required_kwh_per_day=required_kwh_per_day,
        required_btu_per_day=required_btu_per_day,
    )
