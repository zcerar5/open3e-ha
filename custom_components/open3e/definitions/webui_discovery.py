"""Types for entities published by the Open3e Web UI add-on."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class Open3eWebUiDiscoveryEntity:
    """MQTT discovery payload published by the Open3e Web UI."""

    component: str
    unique_id: str
    name: str
    state_topic: str
    payload: dict[str, Any]

    @property
    def command_topic(self) -> str | None:
        return self.payload.get("command_topic") or self.payload.get("cmd_t")

    @property
    def object_id(self) -> str:
        return self.payload.get("object_id") or self.payload.get("obj_id") or self.unique_id

    @property
    def device_identifiers(self) -> list[str]:
        device = self.payload.get("device") or {}
        identifiers = device.get("identifiers") or device.get("ids") or []
        if isinstance(identifiers, str):
            return [identifiers]
        return list(identifiers)

    @property
    def device_name(self) -> str:
        device = self.payload.get("device") or {}
        return device.get("name") or device.get("name_by_user") or "Open3e"

    @staticmethod
    def from_discovery_payload(component: str, object_id: str, payload: dict[str, Any]):
        state_topic = payload.get("state_topic") or payload.get("stat_t")
        if not state_topic:
            return None

        unique_id = payload.get("unique_id") or payload.get("uniq_id") or object_id
        name = payload.get("name") or payload.get("name_by_user") or object_id.replace("_", " ")

        return Open3eWebUiDiscoveryEntity(
            component=component,
            unique_id=unique_id,
            name=name,
            state_topic=state_topic,
            payload=payload,
        )
