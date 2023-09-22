# pylint: disable=line-too-long
"""Nintendo Switch Parental Controls switch platform."""

import logging
from typing import Any

from homeassistant.components.switch import SwitchEntity, SwitchDeviceClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from pynintendoparental.enum import RestrictionMode

from .coordinator import NintendoUpdateCoordinator

from .const import (
    DOMAIN,
    SW_OVERRIDE_LIMIT_INVALID,
    SW_CONFIGURATION_ENTITIES
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
        for config in SW_CONFIGURATION_ENTITIES:
            entities.append(
                DeviceConfigurationSwitch(coordinator, device.device_id, config)
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
        await self._device.update_max_daily_playtime(0)
        return await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs: Any) -> None:
        if self._old_state == 0:
            _LOGGER.warning(SW_OVERRIDE_LIMIT_INVALID)
            # defaulting to 180 minutes
            await self._device.update_max_daily_playtime(180)
        else:
            await self._device.update_max_daily_playtime(self._old_state)
        return await self.coordinator.async_request_refresh()

class DeviceConfigurationSwitch(NintendoDevice, SwitchEntity):
    """A configuration switch."""
    def __init__(
        self,
        coordinator,
        device_id,
        config_item
    ) -> None:
        """Initialize the sensor class."""
        super().__init__(coordinator, device_id, config_item)
        self._config = SW_CONFIGURATION_ENTITIES.get(config_item)
        self._config_item = config_item
        self._attr_should_poll = True

    @property
    def name(self) -> str:
        return self._config.get("name")

    @property
    def icon(self) -> str:
        return self._config.get("icon")

    @property
    def device_class(self) -> SwitchDeviceClass | None:
        return SwitchDeviceClass.SWITCH

    @property
    def is_on(self) -> bool | None:
        if self._config_item == "restriction_mode":
            return self._device.parental_control_settings["playTimerRegulations"]["restrictionMode"] == "FORCED_TERMINATION"

    async def async_turn_on(self, **kwargs) -> None:
        """Enable forced termination mode."""
        await self._device.set_restriction_mode(RestrictionMode.FORCED_TERMINATION)
        return await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs) -> None:
        """Enable alarm mode."""
        await self._device.set_restriction_mode(RestrictionMode.ALARM)
        return await self.coordinator.async_request_refresh()
