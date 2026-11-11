"""Constants for open3e."""

DOMAIN = "open3e"

MQTT_TOPIC_KEY = "mqtt_topic"
MQTT_TOPIC_DEFAULT = "open3e"
MQTT_CMD_KEY = "mqtt_cmnd"
MQTT_CMD_DEFAULT = "open3e/cmnd"
MQTT_SYSTEM_TOPIC = "system"
MQTT_SYSTEM_PAYLOAD = '{"mode":"system"}'

VIESSMANN_TEMP_HEATING_MIN = 3
VIESSMANN_TEMP_HEATING_MAX = 37

VIESSMANN_TEMP_DHW_MIN = 10
VIESSMANN_TEMP_DHW_MAX = 60

VIESSMANN_POWER_MAX_WATT_ELECTRICAL_HEATER = 8000
VIESSMANN_POWER_MIN_WATT_ELECTRICAL_HEATER = 0
VIESSMANN_POWER_WATT_ELECTRICAL_HEATER_STEP = 1000

# DID 2626 (maximum power of the electrical heater). The heater only switches whole
# stages (about 2.7 / 5.3 / 8 kW). A limit between 0 and the first stage confuses the
# heat pump (Vitocal 250-A software 2440: compressor off, 4/3-way valve flapping between
# 1 and 255; open3e discussion #205), so such values are refused.
VIESSMANN_HEATER_POWER_UNSAFE_BELOW_WATT = 3000
# Dropdown levels -> watts written to DID 2626.
VIESSMANN_HEATER_POWER_LEVELS = {
    "off": 0,
    "stage_1": 3000,
    "stage_2": 6000,
    "full": 8000,
}
# Seconds to wait for the heat pump to confirm a written value.
WRITE_CONFIRM_TIMEOUT = 10

VIESSMANN_SMART_GRID_TEMP_MIN = 0
VIESSMANN_SMART_GRID_TEMP_MAX = 20

VIESSMANN_HYSTERESIS_MIN = 0
VIESSMANN_HYSTERESIS_MAX = 10

VIESSMANN_UNAVAILABLE_VALUE = -3276.8
VITODENS_UNAVAILABLE_VALUE = 127
