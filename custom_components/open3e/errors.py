from typing import Any

from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.update_coordinator import UpdateFailed

from custom_components.open3e.const import DOMAIN


class Open3eServerTimeoutError(
    HomeAssistantError
):
    """Exception to indicate a timeout error."""

    def __init__(self) -> None:
        """Initialize the error."""
        super().__init__(
            translation_domain=DOMAIN,
            translation_key="timeout"
        )


class Open3eServerUnavailableError(
    HomeAssistantError
):
    """Exception to indicate that the server is unavailable."""

    def __init__(self) -> None:
        """Initialize the error."""
        super().__init__(
            translation_domain=DOMAIN,
            translation_key="unavailable"
        )


class Open3eError(
    HomeAssistantError
):
    """Exception to indicate a MQTT error."""

    def __init__(self, exception: Exception) -> None:
        """Initialize the error."""
        super().__init__(
            exception,
            translation_domain=DOMAIN,
            translation_key="mqtt"
        )


class Open3eHeaterPowerRefusedError(
    HomeAssistantError
):
    """Exception to indicate a heater power limit the heat pump cannot handle."""

    def __init__(self, watts: int, minimum: int) -> None:
        """Initialize the error."""
        super().__init__(
            translation_domain=DOMAIN,
            translation_key="heater_power_unsafe",
            translation_placeholders={"watts": str(watts), "minimum": str(minimum)},
        )


class Open3eWriteNotConfirmedError(
    HomeAssistantError
):
    """Exception to indicate that the heat pump did not confirm a written value."""

    def __init__(self, expected: Any, actual: Any) -> None:
        """Initialize the error."""
        super().__init__(
            translation_domain=DOMAIN,
            translation_key="write_not_confirmed",
            translation_placeholders={"expected": str(expected), "actual": str(actual)},
        )


class Open3eCoordinatorUpdateFailed(
    UpdateFailed
):
    """Exception to indicate an Update error."""
