"""Time platform for Home Assistant."""

from datetime import time
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
        for device in coordinator.api.devices:
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
        return "Today Max Screentime"

    @property
    def native_value(self) -> time | None:
        return time(0,0,0)
