"""Time platform for Home Assistant."""

from datetime import time, timedelta
import logging

from homeassistant.components.time import TimeEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .coordinator import NintendoUpdateCoordinator
from .const import DOMAIN
from .entity import NintendoDevice

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up Nintendo Switch Parental Control switches."""
    coordinator: NintendoUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    entities = []
    if coordinator.api.devices is not None:
        for device in coordinator.api.devices.values():
            entities.append(
                NintendoParentalTimeEntity(
                    coordinator, device.device_id, "today_max_screentime"
                )
            )
    async_add_entities(entities, True)


class NintendoParentalTimeEntity(NintendoDevice, TimeEntity):
    """An instance of a time entity."""

    _attr_should_poll = True

    @property
    def name(self) -> str:
        """Return entity name."""
        return "Play Time Limit"

    def _value(self) -> time:
        """Conversion class for time."""
        if self._device.limit_time is None:
            return None
        return time(
            int(
                str(timedelta(minutes=self._device.limit_time)).split(":", maxsplit=1)[
                    0
                ]
            ),
            int(
                str(timedelta(minutes=self._device.limit_time)).split(":", maxsplit=2)[
                    1
                ]
            ),
            0,
        )

    @property
    def native_value(self) -> time | None:
        """Return the native value."""
        return self._value()

    async def async_set_value(self, value: time) -> None:
        """Update the value."""
        _LOGGER.debug(
            "Got request to update play time for device %s to %s",
            self._device_id,
            value,
        )
        minutes = value.hour * 60
        minutes += value.minute
        await self._device.update_max_daily_playtime(minutes)
        await self.coordinator.async_request_refresh()
