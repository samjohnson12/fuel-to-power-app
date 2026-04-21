
"""
Technology definitions (heat-rate ranges, defaults).

Heat-rate ranges below are seeded from internal reference material:
[Bridge Power - Natural Gas DD Summary.pptx](https://soco365.sharepoint.com/sites/SCSGPDRenewableDevelopment-DERTEAM/_layouts/15/Doc.aspx?sourcedoc=%7B5884A18D-DB29-4A32-9FDB-7121E091D889%7D&file=Bridge%20Power%20-%20Natural%20Gas%20DD%20Summary.pptx&action=edit&mobileredirect=true&EntityRepresentationId=b780b6ce-cafc-4c78-a909-cea3a026588b). [1](https://soco365.sharepoint.com/sites/SCSGPDRenewableDevelopment-DERTEAM/_layouts/15/Doc.aspx?sourcedoc=%7B5884A18D-DB29-4A32-9FDB-7121E091D889%7D&file=Bridge%20Power%20-%20Natural%20Gas%20DD%20Summary.pptx&action=edit&mobileredirect=true&DefaultItemOpen=1)
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Dict


@dataclass(frozen=True)
class TechSpec:
    """Technology specification for converting fuel energy to electricity.

    Attributes:
        name: Display name.
        default_heat_rate_btu_per_kwh: Default heat rate in BTU/kWh.
    """
    name: str
    default_heat_rate_btu_per_kwh: float


TECH_SPECS: Dict[str, TechSpec] = {
    "RICE (Reciprocating Engine)": TechSpec(
        name="RICE (Reciprocating Engine)",
        default_heat_rate_btu_per_kwh=8300.0,
    ),
    "CT / Turbine": TechSpec(
        name="CT / Turbine",
        default_heat_rate_btu_per_kwh=9500.0,
    ),
    "Fuel Cell (e.g., Bloom)": TechSpec(
        name="Fuel Cell (e.g., Bloom)",
        default_heat_rate_btu_per_kwh=7000.0,
    ),
    "Linear Generator": TechSpec(
        name="Linear Generator",
        default_heat_rate_btu_per_kwh=8200.0,
    ),
}
