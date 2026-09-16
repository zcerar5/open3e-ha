from enum import IntEnum
from typing import Any

from .dtc_list import get_dtc_ids


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
    return get_dtc_ids(data, "Info")


def is_info_dtc_active(data: Any, info: InfoDtc) -> bool | None:
    """Return True if the info message is active, False if not, None if the payload can not be parsed."""
    active_ids = get_active_info_dtc_ids(data)
    if active_ids is None:
        return None
    return info in active_ids
