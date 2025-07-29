"""Services for Nintendo Parental integration."""

import logging

from homeassistant.core import HomeAssistant, ServiceCall, callback
from homeassistant.exceptions import HomeAssistantError, ServiceValidationError
from homeassistant.helpers import (
    config_validation as cv,
    device_registry as dr,
)

import voluptuous as vol

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

@callback
def async_setup_services(
    hass: HomeAssistant,
):
    """Set up the Nintendo Parental services."""
    hass.services.async_register(
        domain=DOMAIN,
        service="add_bonus_time",
        service_func=async_add_bonus_time,
        schema=vol.Schema({
            vol.Required("integration_id"): cv.string,
            vol.Required("device_id"): cv.string,
            vol.Required("bonus_time"): vol.All(int, vol.Range(min=-1, max=1440)),
        })
    )

def get_config_entry(hass: HomeAssistant, account_id: str):
    """Get the coordinator from the Home Assistant instance."""
    return hass.config_entries.async_get_entry(account_id)

async def async_add_bonus_time(
    call: ServiceCall
) -> None:
    """Add bonus time to a device."""
    data = call.data
    config_entry = get_config_entry(call.hass, data["integration_id"])
    if config_entry is None:
        raise HomeAssistantError(
            f"Config entry for integration_id {data['integration_id']} not found"
        )
    device_id: str = data["device_id"]
    bonus_time: int = data["bonus_time"]
    if not device_id or not bonus_time:
        raise ServiceValidationError(
            "device_id and bonus_time are required fields"
        )

    if bonus_time < -1 or bonus_time > 1440:
        raise ServiceValidationError(
            "bonus_time must be between -1 and 1440 minutes"
        )

    device = dr.async_get(call.hass).async_get(device_id)
    if device is None:
        raise HomeAssistantError(f"Device with ID {device_id} not found")
    device_id = next(iter(device.identifiers))[1].split("_")[-1]

    coordinator = config_entry.runtime_data
    if not coordinator:
        raise HomeAssistantError("Coordinator is not available")

    try:
        await coordinator.api.devices[device_id].add_extra_time(bonus_time)
    except Exception as e:
        _LOGGER.error(f"Failed to add bonus time: {e}")
        raise HomeAssistantError(f"Failed to add bonus time: {e}") from e
