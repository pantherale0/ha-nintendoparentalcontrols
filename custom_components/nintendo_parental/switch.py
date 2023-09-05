"""Nintendo Switch Parental Controls switch platform."""

import logging
from typing import Any

from pynintendoparental.device import Device

from homeassistant.components.switch import SwitchEntity, SwitchDeviceClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .coordinator import NintendoUpdateCoordinator

from .const import (
    DOMAIN
)

from .entity import NintendoDevice

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
        hass: HomeAssistant,
        entry: ConfigEntry,
        async_add_entities: AddEntitiesCallback
) -> None:
    """Set up Nintendo Switch Parental Control switches."""
    coordinator: NintendoUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    entities = []
    for device in coordinator.api.devices:
        entities.append(
            DeviceOverrideSwitch(coordinator, device.device_id)
        )
    async_add_entities(entities, True)

class DeviceOverrideSwitch(NintendoDevice, SwitchEntity):
    """Defines a switch that can enable or disable a device."""

    def __init__(
        self,
        coordinator,
        device_id
    ) -> None:
        """Initialize the sensor class."""
        super().__init__(coordinator, device_id, "override")
        self._old_state = self._device.limit_time

    @property
    def name(self) -> str:
        return "Block Device Access"

    @property
    def is_on(self) -> bool:
        return self._device.limit_time == 0

    @property
    def device_class(self) -> SwitchDeviceClass | None:
        return SwitchDeviceClass.SWITCH

    async def async_turn_on(self, **kwargs: Any) -> None:
        self._old_state = self._device.limit_time
        return await self._device.update_max_daily_playtime(0)

    async def async_turn_off(self, **kwargs: Any) -> None:
        if self._old_state == 0:
            _LOGGER.warning("Attempted to disable device block when screentime limit was already 0, defaulting to 180 minutes.")
            # defaulting to 180 minutes
            await self._device.update_max_daily_playtime(180)
        else:
            await self._device.update_max_daily_playtime(self._old_state)
        await self.coordinator.async_request_refresh()
