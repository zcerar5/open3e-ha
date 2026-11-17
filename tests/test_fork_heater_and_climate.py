"""Tests for fork-specific behaviour kept through the upstream merge.

- DID 2626 (electrical heater max power) is written raw (Int32 LE watts) and
  goes through the command gate.
- Heater limits between 0 and 3000 W are refused before anything is sent.
- The climate hvac_action is IDLE while domestic hot water is being heated and
  while the circuit pump is off.

Run with ``python -m unittest discover -s tests``.
"""

from __future__ import annotations

import json
import unittest
from unittest.mock import AsyncMock, MagicMock, patch

from homeassistant.components.climate import HVACAction, HVACMode

from custom_components.open3e import api as api_module
from custom_components.open3e.api import Open3eMqttClient
from custom_components.open3e.climate import Open3eClimate
from custom_components.open3e.coordinator import Open3eDataUpdateCoordinator
from custom_components.open3e.definitions.climate import CLIMATE
from custom_components.open3e.errors import Open3eHeaterPowerRefusedError

CMD_TOPIC = "open3e/cmnd"


class HeaterRawWriteTest(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        self.client = Open3eMqttClient(mqtt_topic="open3e", mqtt_cmd=CMD_TOPIC)
        self.hass = MagicMock()

    async def test_raw_payload_goes_through_gate(self) -> None:
        gate = self.client._Open3eMqttClient__command_gate
        with patch.object(api_module.mqtt, "async_publish", new=AsyncMock()) as publish, \
                patch.object(gate, "async_send", wraps=gate.async_send) as gate_send:
            sent = await self.client.async_set_max_power_electrical_heater(
                hass=self.hass, feature_id=2626, max_power=3000, device_id=0x680
            )

        self.assertTrue(sent)
        gate_send.assert_awaited_once()
        publish.assert_awaited_once()
        kwargs = publish.await_args.kwargs
        self.assertEqual(kwargs["topic"], CMD_TOPIC)
        payload = json.loads(kwargs["payload"])
        self.assertEqual(payload["mode"], "write-raw")
        self.assertEqual(payload["addr"], 0x680)
        # 3000 W as Int32 little-endian
        self.assertEqual(payload["data"], [[2626, "b80b0000"]])

    async def test_paused_gate_drops_raw_write(self) -> None:
        self.client.pause_commands()
        with patch.object(api_module.mqtt, "async_publish", new=AsyncMock()) as publish:
            sent = await self.client.async_set_max_power_electrical_heater(
                hass=self.hass, feature_id=2626, max_power=8000, device_id=0x680
            )

        self.assertFalse(sent)
        publish.assert_not_awaited()


class HeaterRefusalTest(unittest.IsolatedAsyncioTestCase):
    def _coordinator(self) -> tuple[Open3eDataUpdateCoordinator, MagicMock]:
        coordinator = object.__new__(Open3eDataUpdateCoordinator)
        client = MagicMock()
        # False = "gate dropped it", so the coordinator skips the read-back loop.
        client.async_set_max_power_electrical_heater = AsyncMock(return_value=False)
        coordinator._Open3eDataUpdateCoordinator__client = client
        coordinator.hass = MagicMock()
        return coordinator, client

    async def test_values_between_zero_and_3000_are_refused(self) -> None:
        for watts in (1, 500, 1500, 2999, 2999.4):
            coordinator, client = self._coordinator()
            with self.subTest(watts=watts), self.assertRaises(Open3eHeaterPowerRefusedError):
                await coordinator.async_set_max_power_electrical_heater(
                    feature_id=2626, max_power=watts, device=MagicMock(id=0x680)
                )
            client.async_set_max_power_electrical_heater.assert_not_awaited()

    async def test_zero_and_stage_values_are_sent(self) -> None:
        for watts in (0, 3000, 6000, 8000):
            coordinator, client = self._coordinator()
            with self.subTest(watts=watts):
                await coordinator.async_set_max_power_electrical_heater(
                    feature_id=2626, max_power=watts, device=MagicMock(id=0x680)
                )
                client.async_set_max_power_electrical_heater.assert_awaited_once()
                self.assertEqual(client.async_set_max_power_electrical_heater.await_args.kwargs["max_power"], watts)


class ClimateHvacActionTest(unittest.IsolatedAsyncioTestCase):
    def setUp(self) -> None:
        self.description = CLIMATE[0]
        entity = object.__new__(Open3eClimate)
        entity.entity_description = self.description
        entity.data = {}
        entity._attr_hvac_mode = HVACMode.AUTO
        entity._attr_hvac_action = HVACAction.IDLE
        for name in ("current_room_temperature", "current_flow_temperature", "current_program",
                     "heating_programs", "cooling_programs", "compressor_power_state",
                     "circuit_pump_active", "domestic_hot_water_status"):
            setattr(entity, f"_Open3eClimate__{name}", None)
        entity.async_write_ha_state = MagicMock()
        self.entity = entity

    async def _feed(self, feature, payload) -> None:
        self.entity.data[feature.id] = json.dumps(payload) if not isinstance(payload, str) else payload
        await self.entity.async_on_data(feature.id)

    async def _heating_with_compressor_on(self) -> None:
        await self._feed(self.description.hvac_mode_feature, {"Mode": {"ID": 1}, "State": {"ID": 2}})
        await self._feed(self.description.compressor_state_feature, {"PowerState": 1})
        await self._feed(self.description.circuit_pump_feature, {"PowerState": 1})
        await self._feed(self.description.domestic_hot_water_status_feature, "0")

    async def test_heating_when_compressor_and_pump_run(self) -> None:
        await self._heating_with_compressor_on()
        self.assertEqual(self.entity._attr_hvac_mode, HVACMode.HEAT)
        self.assertEqual(self.entity._attr_hvac_action, HVACAction.HEATING)

    async def test_idle_during_domestic_hot_water(self) -> None:
        await self._heating_with_compressor_on()
        await self._feed(self.description.domestic_hot_water_status_feature, "1")
        self.assertEqual(self.entity._attr_hvac_action, HVACAction.IDLE)
        await self._feed(self.description.domestic_hot_water_status_feature, '{"ID": 2}')
        self.assertEqual(self.entity._attr_hvac_action, HVACAction.IDLE)

    async def test_idle_when_circuit_pump_off(self) -> None:
        await self._heating_with_compressor_on()
        await self._feed(self.description.circuit_pump_feature, {"PowerState": 0})
        self.assertEqual(self.entity._attr_hvac_action, HVACAction.IDLE)

    async def test_off_when_mode_off(self) -> None:
        await self._heating_with_compressor_on()
        await self._feed(self.description.hvac_mode_feature, {"Mode": {"ID": 0}, "State": {"ID": 2}})
        self.assertEqual(self.entity._attr_hvac_action, HVACAction.OFF)


if __name__ == "__main__":
    unittest.main()
