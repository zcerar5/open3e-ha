from enum import StrEnum
from typing import Any

from .dtc_list import get_dtc_ids

# Status message IDs of the Open3e "States" enum, as listed by StatusDtcList (DID 257).
# The Viessmann status codes S.<id> carry the same numbers.

# Defrost of the outdoor unit, grouped by phase.
DEFROST_REQUESTED_IDS = frozenset({
    146,  # ControlLoopDefrostStateStartup
    176,  # RefrigerantCycleRequestForDefrost
})
DEFROST_PREPARING_IDS = frozenset({
    127,  # HeatPumpPrepDefrost
    147,  # ControlLoopDefrostStatePrepareDefrostEnergy
    223,  # RefrigerantCycleAppStateDefrostStartup
    232,  # RefrigerantCycleAppStateTransitionHeatingToNaturalDefrost
    392,  # RefrigerantCycleAppStateTransitionHeatingToDefrost
})
DEFROST_DEFROSTING_IDS = frozenset({
    119,  # DefrostingModeOutDoorUnitActive
    128,  # HeatPumpDefrost
    135,  # FourThreeWayValveDefrostPosition
    148,  # ControlLoopDefrostStateDefrosting
    226,  # RefrigerantCycleAppStateDefrostControl
    227,  # RefrigerantCycleAppStateNaturalDefrost
})
DEFROST_FINISHING_IDS = frozenset({
    231,  # RefrigerantCycleAppStateTransitionDefrostToHeating
    233,  # RefrigerantCycleAppStateTransitionNaturalDefrostToHeating
})

# Passive (181-190) and active (393-402) frost protection of circuits, cylinders, buffers and the heat pump.
FROST_PROTECTION_IDS = frozenset(range(181, 191)) | frozenset(range(393, 403))

# Lock by the power supplier (EVU-Sperre), directly or through Smart Grid.
UTILITY_LOCK_IDS = frozenset({
    195,  # SmartGridLock
    196,  # PowerSupplierLock
})

# Instantaneous heating water heater (Heizwasser-Durchlauferhitzer) stages.
ELECTRIC_HEATER_OFF_ID = 130  # ElectricalHeaterOff
ELECTRIC_HEATER_STAGE_IDS = {
    131: 1,  # ElectricalHeaterPhaseOneActive
    132: 2,  # ElectricalHeaterPhaseTwoActive
    133: 3,  # ElectricalHeaterPhaseThreeActive
}


class DefrostPhase(StrEnum):
    NONE = "none"
    REQUESTED = "requested"
    PREPARING = "preparing"
    DEFROSTING = "defrosting"
    FINISHING = "finishing"


class ElectricHeaterStage(StrEnum):
    OFF = "off"
    STAGE_1 = "stage_1"
    STAGE_2 = "stage_2"
    STAGE_3 = "stage_3"


def get_status_dtc_ids(data: Any) -> set[int] | None:
    """Parse the active status message IDs of a StatusDtcList (DID 257) payload."""
    return get_dtc_ids(data, "State")


def get_defrost_phase(data: Any) -> DefrostPhase | None:
    """Return the defrost phase reported by the status messages, None if the payload can not be parsed."""
    ids = get_status_dtc_ids(data)
    if ids is None:
        return None
    if ids & DEFROST_DEFROSTING_IDS:
        return DefrostPhase.DEFROSTING
    if ids & DEFROST_FINISHING_IDS:
        return DefrostPhase.FINISHING
    if ids & DEFROST_PREPARING_IDS:
        return DefrostPhase.PREPARING
    if ids & DEFROST_REQUESTED_IDS:
        return DefrostPhase.REQUESTED
    return DefrostPhase.NONE


def get_electric_heater_stage(data: Any) -> ElectricHeaterStage | None:
    """Return the highest active stage of the electric heater, OFF if no stage is listed."""
    ids = get_status_dtc_ids(data)
    if ids is None:
        return None
    stage = max((ELECTRIC_HEATER_STAGE_IDS[i] for i in ids if i in ELECTRIC_HEATER_STAGE_IDS), default=0)
    return {
        0: ElectricHeaterStage.OFF,
        1: ElectricHeaterStage.STAGE_1,
        2: ElectricHeaterStage.STAGE_2,
        3: ElectricHeaterStage.STAGE_3,
    }[stage]


def is_frost_protection_active(data: Any) -> bool | None:
    """Return True if any frost protection status is active, None if the payload can not be parsed."""
    ids = get_status_dtc_ids(data)
    if ids is None:
        return None
    return bool(ids & FROST_PROTECTION_IDS)


def is_utility_lock_active(data: Any) -> bool | None:
    """Return True if a power supplier lock (EVU-Sperre) status is active, None if the payload can not be parsed."""
    ids = get_status_dtc_ids(data)
    if ids is None:
        return None
    return bool(ids & UTILITY_LOCK_IDS)
