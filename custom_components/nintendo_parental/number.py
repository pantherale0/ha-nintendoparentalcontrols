"""Number platform."""


import logging

from homeassistant.components.number import NumberEntity, NumberMode
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ServiceValidationError, HomeAssistantError
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from pynintendoparental.exceptions import HttpException

from .coordinator import NintendoUpdateCoordinator

from .const import DOMAIN

from .entity import NintendoDevice

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up Nintendo Switch Parental Control number platform."""
    coordinator: NintendoUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    entities = []
    if coordinator.api.devices is not None:
        for device in list(coordinator.api.devices.values()):
            entities.append(ScreenTimeEntity(
                coordinator=coordinator,
                device_id=device.device_id,
                entity_id="today_max_screentime"))
    async_add_entities(entities, True)


class ScreenTimeEntity(NintendoDevice, NumberEntity):
    """A screen time entity."""

    _attr_should_poll = True
    _attr_mode = NumberMode.SLIDER
    _attr_native_max_value = 360
    _attr_native_step = 1
    _attr_native_unit_of_measurement = "min"

    @property
    def native_min_value(self) -> float | None:
        """Return the min value."""
        return -1

    @property
    def native_value(self) -> float | None:
        """Return the state of the entity."""
        if self._device.limit_time is None:
            return -1
        return float(self._device.limit_time)

    @property
    def name(self) -> str:
        """Return the name of the entity."""
        return f"{self._device.name} Play Time Limit"

    async def async_set_native_value(self, value: float) -> None:
        """Update the state of the entity."""
        if value > 360:
            raise ServiceValidationError(
                "Play Time Limit cannot be more than 6 hours.",
                translation_domain=DOMAIN,
                translation_key="play_time_limit_out_of_range",
            )
        try:
            if value == -1:
                await self._device.update_max_daily_playtime(minutes=None)
            else:
                await self._device.update_max_daily_playtime(minutes=value)
            await self.coordinator.async_request_refresh()
        except HttpException as exc:
            raise HomeAssistantError(
                "Nintendo returned an unexpected response.",
                translation_domain=DOMAIN,
                translation_key="unexpected_response") from exc
