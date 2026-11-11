from typing import Any

from homeassistant.util.json import json_loads

from custom_components.open3e.const import (
    VIESSMANN_HEATER_POWER_LEVELS,
    VIESSMANN_HEATER_POWER_UNSAFE_BELOW_WATT,
)


def heater_power_watts(payload: Any) -> float | None:
    """Parse the DID 2626 payload (watts) published by Open3e."""
    try:
        return float(json_loads(payload))
    except (TypeError, ValueError):
        return None


def heater_level_from_payload(payload: Any) -> str | None:
    """Map the heater power limit to the stage it allows.

    Returns None for limits between 0 and the first stage, which the heat pump
    cannot handle properly (see VIESSMANN_HEATER_POWER_UNSAFE_BELOW_WATT).
    """
    watts = heater_power_watts(payload)
    if watts is None:
        return None
    if watts <= 0:
        return "off"
    if watts >= VIESSMANN_HEATER_POWER_LEVELS["full"]:
        return "full"
    if watts >= VIESSMANN_HEATER_POWER_LEVELS["stage_2"]:
        return "stage_2"
    if watts >= VIESSMANN_HEATER_POWER_UNSAFE_BELOW_WATT:
        return "stage_1"
    return None


def heater_watts_from_level(level: str) -> int:
    """Return the watts to write for a dropdown level."""
    return VIESSMANN_HEATER_POWER_LEVELS[level]
