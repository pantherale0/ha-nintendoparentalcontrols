"""Sensor platform for integration_blueprint."""
from __future__ import annotations
from collections.abc import Mapping
from typing import Any

from homeassistant.components.sensor import SensorEntity
from homeassistant.components.sensor.const import SensorDeviceClass

from .const import DOMAIN
from .coordinator import NintendoUpdateCoordinator
from .entity import NintendoDevice


async def async_setup_entry(hass, entry, async_add_devices):
    """Set up the sensor platform."""
    coordinator: NintendoUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    entities = []
    for device in coordinator.api.devices:
        entities.append(
            NintendoDeviceSensor(coordinator, device.device_id)
        )
    async_add_devices(entities, True)

class NintendoDeviceSensor(NintendoDevice, SensorEntity):
    """nintendo_parental Sensor class."""

    def __init__(
        self,
        coordinator,
        device_id
    ) -> None:
        """Initialize the sensor class."""
        super().__init__(coordinator, device_id, "screentime")
        self._attr_should_poll = True # allow native value to be polled.

    @property
    def native_value(self) -> float:
        """Return the native value of the sensor."""
        return self._device.daily_summaries[0].get("playingTime", 0) / 60

    @property
    def native_unit_of_measurement(self) -> str:
        """Return unit of measurement."""
        return "min"

    @property
    def device_class(self) -> SensorDeviceClass | None:
        """Return device class."""
        return SensorDeviceClass.DURATION

    @property
    def extra_state_attributes(self) -> Mapping[str, Any] | None:
        """Return extra state attributes."""
        # limited to 5 days to prevent HA recorder issues
        return {"daily": self._device.daily_summaries[0:5]}

    @property
    def name(self) -> str | None:
        """Return entity name."""
        return "Used Screen Time"
