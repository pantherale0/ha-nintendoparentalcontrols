"""nintendo_parental entity class."""
from __future__ import annotations

from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity
import homeassistant.helpers.device_registry as dr

from .const import DOMAIN
from .coordinator import NintendoUpdateCoordinator


class NintendoDevice(CoordinatorEntity[NintendoUpdateCoordinator]):
    """A Nintendo device."""

    def __init__(
        self, coordinator: NintendoUpdateCoordinator, device_id, entity_id
    ) -> None:
        """Initialize."""
        super().__init__(coordinator)
        self._device_id = device_id
        self._entity_id = entity_id

    @property
    def _device(self):
        """Return the device."""
        return self.coordinator.api.devices[self._device_id]

    @property
    def unique_id(self) -> str | None:
        """Return unique ID."""
        return f"nintendoparental_{self._device_id}_{self._entity_id}"

    @property
    def device_info(self):
        """Return device info."""
        return DeviceInfo(
            identifiers={(DOMAIN, f"nintendoparental_{self._device_id}")},
            manufacturer="Nintendo",
            name=self._device.name,
            entry_type=dr.DeviceEntryType.SERVICE,
            sw_version=self._device.extra["firmwareVersion"][
                "displayedVersion"
            ],
        )
