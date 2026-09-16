from enum import StrEnum
from typing import Any

from homeassistant.util.json import json_loads

from .refrigeration_circuit_mode import RefrigerationCircuitOperationMode
from .status_dtc_list import FROST_PROTECTION_IDS, UTILITY_LOCK_IDS

# FourThreeWayValveModes (DID 2735) positions that route the flow to the domestic hot water cylinder.
HOT_WATER_VALVE_IDS = frozenset({
    2,  # Domestic Hot Water
    4,  # Domestic Hot Water and Internal Buffer
})


class HeatPumpActivity(StrEnum):
    """One state for what the heat pump is doing, for timelines and history graphs."""
    OFF = "off"
    STANDBY = "standby"
    HEATING = "heating"
    HOT_WATER = "hot_water"
    COOLING = "cooling"
    DEFROST = "defrost"
    FROST_PROTECTION = "frost_protection"
    ELECTRIC_HEATER = "electric_heater"
    GRID_LOCK = "grid_lock"
    MANUAL = "manual"


def get_enum_id(data: Any) -> int | None:
    """Return the ID of an O3EEnum payload ({"ID": 2, "Text": "..."}) or of a plain integer payload."""
    try:
        if isinstance(data, str) and data.strip().startswith("{"):
            return int(json_loads(data)["ID"])
        return int(data)
    except (TypeError, ValueError, KeyError):
        return None


def is_power_state_on(data: Any) -> bool | None:
    """Return True if a PowerState payload (e.g. AdditionalElectricHeater, DID 2352) reports On."""
    try:
        power_state = json_loads(data)["PowerState"]
        power_id = power_state["ID"] if isinstance(power_state, dict) else power_state
        return int(power_id) == 1
    except (TypeError, ValueError, KeyError):
        return None


def compute_heat_pump_activity(
        mode: RefrigerationCircuitOperationMode | None,
        valve_id: int | None,
        heater_on: bool | None,
        status_ids: set[int] | None,
) -> HeatPumpActivity | None:
    """Combine the refrigeration circuit mode with valve position, electric heater and status messages."""
    if mode is None:
        return None
    status_ids = status_ids or set()

    if mode == RefrigerationCircuitOperationMode.GRID_LOCK or status_ids & UTILITY_LOCK_IDS:
        return HeatPumpActivity.GRID_LOCK
    if mode == RefrigerationCircuitOperationMode.DEFROST:
        return HeatPumpActivity.DEFROST
    if mode == RefrigerationCircuitOperationMode.HEATING:
        return HeatPumpActivity.HOT_WATER if valve_id in HOT_WATER_VALVE_IDS else HeatPumpActivity.HEATING
    if mode == RefrigerationCircuitOperationMode.COOLING:
        return HeatPumpActivity.COOLING
    if mode == RefrigerationCircuitOperationMode.MANUAL:
        return HeatPumpActivity.MANUAL

    # Compressor is off or shut down
    if status_ids & FROST_PROTECTION_IDS:
        return HeatPumpActivity.FROST_PROTECTION
    if heater_on:
        return HeatPumpActivity.ELECTRIC_HEATER
    if mode == RefrigerationCircuitOperationMode.SHUTDOWN:
        return HeatPumpActivity.STANDBY
    return HeatPumpActivity.OFF
