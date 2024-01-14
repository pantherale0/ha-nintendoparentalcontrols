"""Sensor platform for nintendo_parental."""
from __future__ import annotations
from collections.abc import Mapping
from typing import Any

from homeassistant.components.sensor import SensorEntity
from homeassistant.components.sensor.const import SensorDeviceClass

from .const import DOMAIN, SENSOR_CONFIGURATION_ENTITIES
from .coordinator import NintendoUpdateCoordinator
from .entity import NintendoDevice


async def async_setup_entry(hass, entry, async_add_devices):
    """Set up the sensor platform."""
    coordinator: NintendoUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    entities = []
    if coordinator.api.devices is not None:
        for device in list(coordinator.api.devices.values()):
            for sensor in SENSOR_CONFIGURATION_ENTITIES:
                entities.append(
                    NintendoDeviceSensor(coordinator, device.device_id, sensor)
                )
    async_add_devices(entities, True)


class NintendoDeviceSensor(NintendoDevice, SensorEntity):
    """nintendo_parental Sensor class."""

    def __init__(self, coordinator, device_id, sensor) -> None:
        """Initialize the sensor class."""
        super().__init__(coordinator, device_id, sensor)
        self._config = SENSOR_CONFIGURATION_ENTITIES.get(sensor)
        self._attr_should_poll = True  # allow native value to be polled.

    @property
    def native_value(self) -> float:
        """Return the native value of the sensor."""
        if self._config.get("native_value") == "playing_time":
            return self._device.daily_summaries[0].get("playingTime", 0) / 60
        if self._config.get("native_value") == "time_remaining":
            if self._device.limit_time == 0:
                return 0
            return self._device.limit_time - (
                self._device.daily_summaries[0].get("playingTime", 0) / 60
            )

    @property
    def native_unit_of_measurement(self) -> str:
        """Return unit of measurement."""
        return self._config.get("native_unit_of_measurement")

    @property
    def device_class(self) -> SensorDeviceClass | None:
        """Return device class."""
        return self._config.get("device_class")

    @property
    def extra_state_attributes(self) -> Mapping[str, Any] | None:
        """Return extra state attributes."""
        # limited to 5 days to prevent HA recorder issues
        if self._config.get("state_attributes") == "daily_summaries":
            return {"daily": self._device.daily_summaries[0:5]}
        return None

    @property
    def icon(self) -> str | None:
        """Return the icon."""
        return self._config.get("icon")

    @property
    def name(self) -> str | None:
        """Return entity name."""
        return self._config.get("name")
