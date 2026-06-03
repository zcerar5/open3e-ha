from dataclasses import dataclass

from homeassistant.components.climate import ClimateEntityDescription

from .devices import Open3eDevices
from .entity_description import Open3eEntityDescription
from .features import Features, Feature
from ..capability.capability import Capability


@dataclass(frozen=True)
class Open3eClimateEntityDescription(
    Open3eEntityDescription, ClimateEntityDescription
):
    """Default climate entity description for open3e."""
    domain: str = "climate"
    hvac_mode_feature: Feature | None = None
    flow_temperature_feature: Feature | None = None
    room_temperature_feature: Feature | None = None
    programs_temperature_feature: Feature | None = None
    compressor_state_feature: Feature | None = None
    circuit_pump_feature: Feature | None = None
    domestic_hot_water_status_feature: Feature | None = None


CLIMATE: tuple[Open3eClimateEntityDescription, ...] = (
    Open3eClimateEntityDescription(
        poll_data_features=[
            Features.Temperature.FlowCircuit1,
            Features.Temperature.Room1,
            Features.State.HvacCircuit1,
            Features.Temperature.ProgramsCircuit1,
            Features.State.HeatPumpCompressor,
            Features.State.Circuit1Pump,
            Features.Misc.DomesticHotWaterStatus
        ],
        hvac_mode_feature=Features.State.HvacCircuit1,
        flow_temperature_feature=Features.Temperature.FlowCircuit1,
        room_temperature_feature=Features.Temperature.Room1,
        programs_temperature_feature=Features.Temperature.ProgramsCircuit1,
        compressor_state_feature=Features.State.HeatPumpCompressor,
        circuit_pump_feature=Features.State.Circuit1Pump,
        domestic_hot_water_status_feature=Features.Misc.DomesticHotWaterStatus,
        key="climate_circuit_1",
        translation_key="climate_circuit_1",
        required_capabilities=[Capability.Circuit1],
        required_device=Open3eDevices.Vitocal
    ),
    Open3eClimateEntityDescription(
        poll_data_features=[
            Features.Temperature.FlowCircuit2,
            Features.Temperature.Room2,
            Features.State.HvacCircuit2,
            Features.Temperature.ProgramsCircuit2,
            Features.State.HeatPumpCompressor,
            Features.State.Circuit2Pump,
            Features.Misc.DomesticHotWaterStatus
        ],
        hvac_mode_feature=Features.State.HvacCircuit2,
        flow_temperature_feature=Features.Temperature.FlowCircuit2,
        room_temperature_feature=Features.Temperature.Room2,
        programs_temperature_feature=Features.Temperature.ProgramsCircuit2,
        compressor_state_feature=Features.State.HeatPumpCompressor,
        circuit_pump_feature=Features.State.Circuit2Pump,
        domestic_hot_water_status_feature=Features.Misc.DomesticHotWaterStatus,
        key="climate_circuit_2",
        translation_key="climate_circuit_2",
        entity_registry_enabled_default=False,
        required_capabilities=[Capability.Circuit2],
        required_device=Open3eDevices.Vitocal
    ),
    Open3eClimateEntityDescription(
        poll_data_features=[
            Features.Temperature.FlowCircuit3,
            Features.Temperature.Room3,
            Features.State.HvacCircuit3,
            Features.Temperature.ProgramsCircuit3,
            Features.State.HeatPumpCompressor,
            Features.State.Circuit3Pump,
            Features.Misc.DomesticHotWaterStatus
        ],
        hvac_mode_feature=Features.State.HvacCircuit3,
        flow_temperature_feature=Features.Temperature.FlowCircuit3,
        room_temperature_feature=Features.Temperature.Room3,
        programs_temperature_feature=Features.Temperature.ProgramsCircuit3,
        compressor_state_feature=Features.State.HeatPumpCompressor,
        circuit_pump_feature=Features.State.Circuit3Pump,
        domestic_hot_water_status_feature=Features.Misc.DomesticHotWaterStatus,
        key="climate_circuit_3",
        translation_key="climate_circuit_3",
        entity_registry_enabled_default=False,
        required_capabilities=[Capability.Circuit3],
        required_device=Open3eDevices.Vitocal
    ),
    Open3eClimateEntityDescription(
        poll_data_features=[
            Features.Temperature.FlowCircuit4,
            Features.Temperature.Room4,
            Features.State.HvacCircuit4,
            Features.Temperature.ProgramsCircuit4,
            Features.State.HeatPumpCompressor,
            Features.State.Circuit4Pump,
            Features.Misc.DomesticHotWaterStatus
        ],
        hvac_mode_feature=Features.State.HvacCircuit4,
        flow_temperature_feature=Features.Temperature.FlowCircuit4,
        room_temperature_feature=Features.Temperature.Room4,
        programs_temperature_feature=Features.Temperature.ProgramsCircuit4,
        compressor_state_feature=Features.State.HeatPumpCompressor,
        circuit_pump_feature=Features.State.Circuit4Pump,
        domestic_hot_water_status_feature=Features.Misc.DomesticHotWaterStatus,
        key="climate_circuit_4",
        translation_key="climate_circuit_4",
        entity_registry_enabled_default=False,
        required_capabilities=[Capability.Circuit4],
        required_device=Open3eDevices.Vitocal
    ),
)
