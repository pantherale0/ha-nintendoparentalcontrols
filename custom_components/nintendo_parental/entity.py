"""BlueprintEntity class."""
from __future__ import annotations

from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity
import homeassistant.helpers.device_registry as dr

from .const import DOMAIN, NAME, VERSION
from .coordinator import NintendoUpdateCoordinator


class NintendoDevice(CoordinatorEntity):
    """A Nintendo device."""

    def __init__(self,
                 coordinator: NintendoUpdateCoordinator,
                 device_id,
                 entity_id) -> None:
        """Initialize."""
        super().__init__(coordinator)
        self.coordinator: NintendoUpdateCoordinator = coordinator
        self._device_id = device_id
        self._entity_id = entity_id

    @property
    def _device(self):
        """Returns the device"""
        return [x for x in self.coordinator.api.devices if x.device_id == self._device_id][0]

    @property
    def unique_id(self) -> str | None:
        return f"nintendoparental_{self._device_id}_{self._entity_id}"

    @property
    def device_info(self):
        """Return device info."""
        return DeviceInfo(
            identifiers={(DOMAIN, f"nintendoparental_{self._device_id}")},
            manufacturer="Nintendo",
            name=self._device.name,
            entry_type=dr.DeviceEntryType.SERVICE,
            sw_version=self._device.extra["device"]["firmwareVersion"]["displayedVersion"]
        )
