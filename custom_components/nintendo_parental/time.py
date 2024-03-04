"""Time platform for Home Assistant."""

from datetime import time
import logging

from homeassistant.components.time import TimeEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ServiceValidationError
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .coordinator import NintendoUpdateCoordinator
from .const import DOMAIN, TIME_CONFIGURATION_ENTITIES
from .entity import NintendoDevice

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up Nintendo Switch Parental Control switches."""
    coordinator: NintendoUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    entities = []
    if coordinator.api.devices is not None:
        for device in list(coordinator.api.devices.values()):
            for entity_config in TIME_CONFIGURATION_ENTITIES:
                entities.append(
                    NintendoParentalTimeEntity(
                        coordinator, device.device_id, entity_config
                    )
                )
    async_add_entities(entities, True)


class NintendoParentalTimeEntity(NintendoDevice, TimeEntity):
    """An instance of a time entity."""

    _attr_should_poll = True

    def __init__(
        self, coordinator: NintendoUpdateCoordinator, device_id, entity_id
    ) -> None:
        """Create time entity."""
        self._config = TIME_CONFIGURATION_ENTITIES.get(entity_id)
        super().__init__(coordinator, device_id, entity_id)

    @property
    def name(self) -> str:
        """Return entity name."""
        return self._config["name"].format(DEV_NAME=self._device.name)

    def _value(self) -> time:
        """Conversion class for time."""
        if self._config["value"] == "bedtime":
            return self._device.bedtime_alarm

    @property
    def native_value(self) -> time | None:
        """Return the native value."""
        return self._value()

    async def async_set_value(self, value: time) -> None:
        """Update the value."""
        if self._config["update_method"] == "set_bedtime_alarm":
            if value.hour >= 16 and value.hour <= 23:
                await self._device.set_bedtime_alarm(end_time=value, enabled=True)
            elif value.hour == 0 and value.minute == 0:
                await self._device.set_bedtime_alarm(enabled=False)
            else:
                raise ServiceValidationError(
                    "Bedtime Alarm must be between 16:00 and 23:45. To disable, set to 0:00.",
                    translation_domain=DOMAIN,
                    translation_key="bedtime_alarm_out_of_range",
                    translation_placeholders={"time": value.strftime("%H:%M")},
                )
        await self.coordinator.async_request_refresh()
