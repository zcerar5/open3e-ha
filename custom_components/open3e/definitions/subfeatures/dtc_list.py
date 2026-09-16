from typing import Any

from homeassistant.util.json import json_loads

# Home Assistant rejects states longer than this (MAX_LENGTH_STATE_STATE).
MAX_STATE_LENGTH = 255


def get_dtc_entries(data: Any, entry_key: str) -> list[dict] | None:
    """Return the entries of an Open3e DTC list payload (DIDs 257-266).

    Open3e read-json payload, e.g. StatusDtcList (DID 257):
    {"Count": 1, "ListEntries": [{"State": {"ID": 128, "Text": "HeatPumpDefrost"}, "DateTime": {...}, "Unknown": "0000"}]}

    entry_key is the enum field name of the list: "State", "Info", "Service", "Warning" or "Error".
    Returns None if the payload is not a valid DTC list.
    """
    try:
        entries = json_loads(data)["ListEntries"]
        if not isinstance(entries, list):
            return None
        for entry in entries:
            entry[entry_key]
        return entries
    except (TypeError, ValueError, KeyError):
        return None


def get_dtc_ids(data: Any, entry_key: str) -> set[int] | None:
    """Return the message IDs of a DTC list payload, or None if it can not be parsed."""
    entries = get_dtc_entries(data, entry_key)
    if entries is None:
        return None

    try:
        ids: set[int] = set()
        for entry in entries:
            value = entry[entry_key]
            # O3EEnum payload {"ID": 128, "Text": "..."}; a plain ID is accepted as well
            ids.add(int(value["ID"] if isinstance(value, dict) else value))
        return ids
    except (TypeError, ValueError, KeyError):
        return None


def get_dtc_texts(data: Any, entry_key: str) -> list[str] | None:
    """Return the message texts of a DTC list payload in order of appearance, without duplicates."""
    entries = get_dtc_entries(data, entry_key)
    if entries is None:
        return None

    texts: list[str] = []
    for entry in entries:
        value = entry[entry_key]
        if isinstance(value, dict):
            text = value.get("Text") or f"#{value.get('ID')}"
        else:
            text = str(value)
        if text not in texts:
            texts.append(text)
    return texts


def get_dtc_list_state(data: Any, entry_key: str) -> str | None:
    """Return the message texts joined for a sensor state, "-" for an empty list, None if unparsable."""
    texts = get_dtc_texts(data, entry_key)
    if texts is None:
        return None

    state = ", ".join(texts) or "-"
    if len(state) > MAX_STATE_LENGTH:
        state = state[:MAX_STATE_LENGTH - 1] + "…"
    return state
