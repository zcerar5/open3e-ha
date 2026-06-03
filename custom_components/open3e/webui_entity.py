"""Generic entities backed by Open3e Web UI MQTT discovery."""

from __future__ import annotations

from typing import Any, Callable

from homeassistant.components import mqtt
from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.components.mqtt import ReceiveMessage
from homeassistant.components.number import NumberEntity
from homeassistant.components.select import SelectEntity
from homeassistant.components.sensor import SensorEntity
from homeassistant.components.switch import SwitchEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity import Entity, EntityCategory

from .const import DOMAIN
from .definitions.webui_discovery import Open3eWebUiDiscoveryEntity


def _payload_key(payload: dict[str, Any], *keys: str, default: Any = None) -> Any:
    for key in keys:
        if key in payload:
            return payload[key]
    return default


def _coerce_state(value: str) -> Any:
    state = value.strip()
    if not state:
        return None

    lowered = state.lower()
    if lowered in {"none", "unknown", "unavailable", "nan"}:
        return None

    try:
        if "." not in state and "e" not in lowered:
            return int(state)
        return float(state)
    except ValueError:
        return state


class Open3eWebUiEntity(Entity):
    """Base class for entities discovered from Open3e Web UI MQTT discovery."""

    _subscriptions: list[Callable]

    def __init__(self, discovery: Open3eWebUiDiscoveryEntity) -> None:
        self.discovery = discovery
        self._subscriptions = []

        self._attr_unique_id = f"{DOMAIN}_{discovery.unique_id}"
        self._attr_name = discovery.name
        self._attr_has_entity_name = False
        self._attr_available = True

        if icon := discovery.payload.get("icon"):
            self._attr_icon = icon
        if category := discovery.payload.get("entity_category"):
            try:
                self._attr_entity_category = EntityCategory(category)
            except ValueError:
                pass

        self._attr_device_info = self._device_info(discovery)

    @staticmethod
    def _device_info(discovery: Open3eWebUiDiscoveryEntity) -> DeviceInfo:
        device = discovery.payload.get("device") or {}
        identifiers = discovery.device_identifiers or [discovery.unique_id.rsplit("_", 1)[0]]

        return DeviceInfo(
            identifiers={(DOMAIN, identifier) for identifier in identifiers},
            manufacturer=device.get("manufacturer") or device.get("mf") or "Viessmann",
            model=device.get("model") or device.get("mdl"),
            name=discovery.device_name,
            sw_version=device.get("sw_version") or device.get("sw"),
            hw_version=device.get("hw_version") or device.get("hw"),
        )

    async def async_added_to_hass(self) -> None:
        await super().async_added_to_hass()

        self._subscriptions.append(
            await mqtt.async_subscribe(
                hass=self.hass,
                topic=self.discovery.state_topic,
                msg_callback=self._handle_state_message,
            )
        )

        for availability in self.discovery.payload.get("availability") or []:
            topic = availability.get("topic")
            if not topic:
                continue
            self._subscriptions.append(
                await mqtt.async_subscribe(
                    hass=self.hass,
                    topic=topic,
                    msg_callback=lambda msg, cfg=availability: self._handle_availability_message(msg, cfg),
                )
            )

    async def async_will_remove_from_hass(self) -> None:
        for unsubscribe in self._subscriptions:
            unsubscribe()
        self._subscriptions.clear()

    def _handle_availability_message(self, message: ReceiveMessage, availability: dict[str, Any]) -> None:
        payload_available = availability.get("payload_available", "online")
        self._attr_available = message.payload == payload_available
        self.async_write_ha_state()

    def _handle_state_message(self, message: ReceiveMessage) -> None:
        self._handle_state_payload(message.payload)
        self.async_write_ha_state()

    def _handle_state_payload(self, payload: str) -> None:
        raise NotImplementedError

    async def _publish_command(self, hass: HomeAssistant, payload: Any) -> None:
        if not self.discovery.command_topic:
            return
        await mqtt.async_publish(hass=hass, topic=self.discovery.command_topic, payload=str(payload))


class Open3eWebUiSensor(Open3eWebUiEntity, SensorEntity):
    """Sensor discovered from the Open3e Web UI."""

    def __init__(self, discovery: Open3eWebUiDiscoveryEntity) -> None:
        super().__init__(discovery)
        payload = discovery.payload
        self._attr_device_class = _payload_key(payload, "device_class", "dev_cla")
        self._attr_native_unit_of_measurement = _payload_key(payload, "unit_of_measurement", "unit")
        self._attr_state_class = _payload_key(payload, "state_class", "stat_cla")
        self._attr_suggested_display_precision = _payload_key(payload, "suggested_display_precision", "sug_dsp_prc")

    def _handle_state_payload(self, payload: str) -> None:
        self._attr_native_value = _coerce_state(payload)


class Open3eWebUiBinarySensor(Open3eWebUiEntity, BinarySensorEntity):
    """Binary sensor discovered from the Open3e Web UI."""

    def __init__(self, discovery: Open3eWebUiDiscoveryEntity) -> None:
        super().__init__(discovery)
        self._attr_device_class = _payload_key(discovery.payload, "device_class", "dev_cla")

    def _handle_state_payload(self, payload: str) -> None:
        state = payload.strip().lower()
        self._attr_is_on = state in {"1", "true", "on", "yes", "open", "online"}


class Open3eWebUiNumber(Open3eWebUiEntity, NumberEntity):
    """Number discovered from the Open3e Web UI."""

    def __init__(self, discovery: Open3eWebUiDiscoveryEntity) -> None:
        super().__init__(discovery)
        payload = discovery.payload
        self._attr_device_class = _payload_key(payload, "device_class", "dev_cla")
        self._attr_native_unit_of_measurement = _payload_key(payload, "unit_of_measurement", "unit")
        self._attr_native_min_value = payload.get("min")
        self._attr_native_max_value = payload.get("max")
        self._attr_native_step = payload.get("step")

    @property
    def available(self) -> bool:
        return self.discovery.command_topic is not None and self._attr_available

    def _handle_state_payload(self, payload: str) -> None:
        state = _coerce_state(payload)
        self._attr_native_value = state if isinstance(state, (int, float)) else None

    async def async_set_native_value(self, value: float) -> None:
        await self._publish_command(self.hass, value)


class Open3eWebUiSelect(Open3eWebUiEntity, SelectEntity):
    """Select discovered from the Open3e Web UI."""

    def __init__(self, discovery: Open3eWebUiDiscoveryEntity) -> None:
        super().__init__(discovery)
        self._attr_options = list(discovery.payload.get("options") or [])

    @property
    def available(self) -> bool:
        return self.discovery.command_topic is not None and self._attr_available

    def _handle_state_payload(self, payload: str) -> None:
        state = payload.strip()
        self._attr_current_option = state if state in self.options else None

    async def async_select_option(self, option: str) -> None:
        await self._publish_command(self.hass, option)


class Open3eWebUiSwitch(Open3eWebUiEntity, SwitchEntity):
    """Switch discovered from the Open3e Web UI."""

    def __init__(self, discovery: Open3eWebUiDiscoveryEntity) -> None:
        super().__init__(discovery)
        payload = discovery.payload
        self._payload_on = payload.get("payload_on", "ON")
        self._payload_off = payload.get("payload_off", "OFF")
        self._state_on = payload.get("state_on", self._payload_on)
        self._state_off = payload.get("state_off", self._payload_off)

    @property
    def available(self) -> bool:
        return self.discovery.command_topic is not None and self._attr_available

    def _handle_state_payload(self, payload: str) -> None:
        state = payload.strip()
        if state == self._state_on:
            self._attr_is_on = True
        elif state == self._state_off:
            self._attr_is_on = False
        else:
            self._attr_is_on = state.lower() in {"1", "true", "on", "yes"}

    async def async_turn_on(self, **kwargs: Any) -> None:
        await self._publish_command(self.hass, self._payload_on)

    async def async_turn_off(self, **kwargs: Any) -> None:
        await self._publish_command(self.hass, self._payload_off)
