# pylint: disable=line-too-long
"""Nintendo Switch Parental Controls switch platform."""

import logging
from typing import Any

from homeassistant.components.switch import SwitchEntity, SwitchDeviceClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from pynintendoparental.enum import RestrictionMode, AlarmSettingState
from pynintendoparental.application import Application

from .coordinator import NintendoUpdateCoordinator

from .const import DOMAIN, SW_CONFIGURATION_ENTITIES, CONF_APPLICATIONS

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
            for config in SW_CONFIGURATION_ENTITIES:
                entities.append(
                    DeviceConfigurationSwitch(coordinator, device.device_id, config)
                )
            for app_id in entry.options.get(CONF_APPLICATIONS, []):
                try:
                    entities.append(
                        ApplicationWhitelistSwitch(
                            coordinator=coordinator,
                            device_id=device.device_id,
                            app=device.get_application(app_id),
                        )
                    )
                except ValueError:
                    _LOGGER.debug(
                        "Ignoring application %s for device %s as it does not exist.",
                        app_id,
                        device.device_id,
                    )
    async_add_entities(entities, True)


class ApplicationWhitelistSwitch(NintendoDevice, SwitchEntity):
    """A configuration switch."""

    _attr_should_poll = True

    def __init__(self, coordinator, device_id, app: Application) -> None:
        """Initialize the sensor class."""
        super().__init__(coordinator, device_id, app.application_id)
        self._app_id = app.application_id

    @property
    def _application(self) -> Application:
        """Get the application."""
        return self._device.get_application(self._app_id)

    @property
    def name(self) -> str:
        """Return entity name."""
        return f"{self._device.name} {self._application.name} Whitelisted"

    @property
    def entity_picture(self) -> str | None:
        """Return entity picture."""
        return self._application.image_url

    @property
    def device_class(self) -> SwitchDeviceClass | None:
        """Return device class."""
        return SwitchDeviceClass.SWITCH

    @property
    def is_on(self) -> bool | None:
        """Return entity state."""
        return self._device.whitelisted_applications.get(self._app_id, None)

    @property
    def assumed_state(self) -> bool:
        """Return true if unable to access whitelisted application."""
        return self._device.whitelisted_applications.get(self._app_id, None) is None

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Disable whitelisted mode."""
        await self._device.set_whitelisted_application(
            app_id=self._app_id, allowed=False
        )
        return await self.coordinator.async_request_refresh()

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Enable whitelisted mode."""
        await self._device.set_whitelisted_application(
            app_id=self._app_id, allowed=True
        )
        return await self.coordinator.async_request_refresh()


class DeviceConfigurationSwitch(NintendoDevice, SwitchEntity):
    """A configuration switch."""

    def __init__(self, coordinator, device_id, config_item) -> None:
        """Initialize the sensor class."""
        super().__init__(coordinator, device_id, config_item)
        self._config = SW_CONFIGURATION_ENTITIES.get(config_item)
        self._config_item = config_item
        self._attr_should_poll = True
        self._old_state = None
        if self._config_item == "limit_time":
            self._old_state = self._device.limit_time

    @property
    def name(self) -> str:
        """Return entity name."""
        return self._config.get("name").format(DEV_NAME=self._device.name)

    @property
    def entity_registry_enabled_default(self) -> bool:
        """Return default enablement state."""
        return self._config.get("enabled", True)

    @property
    def icon(self) -> str:
        """Return entity icon."""
        return self._config.get("icon")

    @property
    def device_class(self) -> SwitchDeviceClass | None:
        """Return device class."""
        return SwitchDeviceClass.SWITCH

    @property
    def is_on(self) -> bool | None:
        """Return entity state."""
        if self._config_item == "restriction_mode":
            return self._device.forced_termination_mode
        if self._config_item == "override":
            return self._device.limit_time == 0
        if self._config_item == "alarms_enabled":
            return self._device.alarms_enabled

    async def async_turn_on(self, **kwargs) -> None:
        """Enable forced termination mode."""
        if self._config_item == "restriction_mode":
            await self._device.set_restriction_mode(RestrictionMode.FORCED_TERMINATION)
        if self._config_item == "override":
            self._old_state = self._device.limit_time
            await self._device.update_max_daily_playtime(0)
        if self._config_item == "alarms_enabled":
            self._device.alarms_enabled = True
            await self._device.set_alarm_state(AlarmSettingState.TO_VISIBLE)
        return await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs) -> None:
        """Enable alarm mode."""
        if self._config_item == "restriction_mode":
            await self._device.set_restriction_mode(RestrictionMode.ALARM)
        if self._config_item == "override":
            if self._old_state == 0:
                # defaulting to 180 minutes
                await self._device.update_max_daily_playtime(
                    self.coordinator.default_max_playtime
                )
            else:
                await self._device.update_max_daily_playtime(self._old_state)
        if self._config_item == "alarms_enabled":
            await self._device.set_alarm_state(AlarmSettingState.TO_INVISIBLE)
        return await self.coordinator.async_request_refresh()
