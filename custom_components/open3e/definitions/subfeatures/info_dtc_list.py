from enum import IntEnum
from typing import Any

from homeassistant.util.json import json_loads


class InfoDtc(IntEnum):
    """Info message IDs of the Open3e "Infos" enum, as listed by InfoDtcList (DID 259)."""
    MIXER_ONE_CIRCUIT_HUMIDITY_PROTECTION_ACTIVATED = 121
    MIXER_TWO_CIRCUIT_HUMIDITY_PROTECTION_ACTIVATED = 122


def get_active_info_dtc_ids(data: Any) -> set[int] | None:
    """Parse the active info message IDs of an InfoDtcList (DID 259) payload.

    Open3e read-json payload:
    {"Count": 1, "ListEntries": [{"Info": {"ID": 121, "Text": "..."}, "DateTime": {...}, "Unknown": "0000"}]}

    Returns None if the payload is not a valid InfoDtcList.
    """
    try:
        active_ids: set[int] = set()
        for entry in json_loads(data)["ListEntries"]:
            info = entry["Info"]
            # O3EEnum payload {"ID": 121, "Text": "..."}; a plain ID is accepted as well
            active_ids.add(int(info["ID"] if isinstance(info, dict) else info))
        return active_ids
    except (TypeError, ValueError, KeyError):
        return None


def is_info_dtc_active(data: Any, info: InfoDtc) -> bool | None:
    """Return True if the info message is active, False if not, None if the payload can not be parsed."""
    active_ids = get_active_info_dtc_ids(data)
    if active_ids is None:
        return None
    return info in active_ids
