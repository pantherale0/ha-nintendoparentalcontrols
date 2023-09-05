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

    @property
    def native_value(self) -> float:
        """Return the native value of the sensor."""
        return self._device.get_date_summary()[0].get("playingTime")/60

    @property
    def native_unit_of_measurement(self) -> str:
        return "min"

    @property
    def device_class(self) -> SensorDeviceClass | None:
        return SensorDeviceClass.DURATION

    @property
    def extra_state_attributes(self) -> Mapping[str, Any] | None:
        return {"daily": self._device.daily_summaries}

    @property
    def name(self) -> str | None:
        return "Used Screen Time"
