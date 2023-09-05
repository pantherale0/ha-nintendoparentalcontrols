"""Custom integration to integrate integration_blueprint with Home Assistant.

For more details about this integration, please refer to
https://github.com/ludeeus/integration_blueprint
"""
from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME, Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import DOMAIN
from .coordinator import NintendoUpdateCoordinator, Authenticator, NintendoParental

PLATFORMS: list[Platform] = [
    Platform.SENSOR,
    Platform.SWITCH
]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up this integration using UI."""
    hass.data.setdefault(DOMAIN, {})
    nintendo_auth = await Authenticator.complete_login(None, entry.data["session_token"], True)
    update_interval = entry.data["update_interval"]
    if entry.options:
        update_interval = entry.options.get("update_interval")
    coord = NintendoUpdateCoordinator(hass, update_interval, nintendo_auth)
    # request first data sync
    await coord.async_request_refresh()
    hass.data[DOMAIN][entry.entry_id] = coord

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(async_reload_entry))

    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Handle removal of an entry."""
    if unloaded := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)
    return unloaded


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload config entry."""
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)
