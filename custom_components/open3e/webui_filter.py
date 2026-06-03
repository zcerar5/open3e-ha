"""Curated Web UI discovery filter for the Open3e integration."""

from __future__ import annotations

from collections.abc import Iterable

from .definitions.binary_sensors import BINARY_SENSORS
from .definitions.climate import CLIMATE
from .definitions.fan import FAN
from .definitions.numbers import NUMBERS
from .definitions.select import SELECTS
from .definitions.sensors import DERIVED_SENSORS, SENSORS
from .definitions.switches import SWITCHES
from .definitions.water_heater import WATER_HEATER
from .definitions.webui_discovery import Open3eWebUiDiscoveryEntity

ROOM_CURRENT_VALUE_DIDS = frozenset(range(1886, 1944, 3))
ROOM_CURRENT_VALUE_SUBFIELDS = frozenset({"ActualTemp", "ActualHumidity"})


def _collect_base_feature_ids() -> frozenset[int]:
    feature_ids: set[int] = set()
    collections = (
        BINARY_SENSORS,
        CLIMATE,
        DERIVED_SENSORS,
        FAN,
        NUMBERS,
        SELECTS,
        SENSORS,
        SWITCHES,
        WATER_HEATER,
    )

    for descriptions in collections:
        for description in descriptions:
            for feature in description.poll_data_features or []:
                feature_ids.add(feature.id)

    return frozenset(feature_ids)


BASE_FEATURE_IDS = _collect_base_feature_ids()


def _parse_state_topic(state_topic: str) -> tuple[int | None, str | None]:
    parts = state_topic.split("/")
    if len(parts) < 2:
        return None, None

    did_part = parts[1].split("_", 1)[0]
    try:
        did = int(did_part)
    except ValueError:
        return None, None

    sub_field = parts[2] if len(parts) > 2 else None
    return did, sub_field


def is_curated_webui_entity(entity: Open3eWebUiDiscoveryEntity) -> bool:
    """Return True when an Open3e Web UI entity belongs to the curated HACS set."""
    did, sub_field = _parse_state_topic(entity.state_topic)
    if did is None:
        return False

    if did in ROOM_CURRENT_VALUE_DIDS:
        return sub_field in ROOM_CURRENT_VALUE_SUBFIELDS

    return did in BASE_FEATURE_IDS


def filter_curated_webui_entities(
    entities: Iterable[Open3eWebUiDiscoveryEntity],
) -> list[Open3eWebUiDiscoveryEntity]:
    return [entity for entity in entities if is_curated_webui_entity(entity)]
