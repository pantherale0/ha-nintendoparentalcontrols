"""Custom integration to integrate nintendo_parental with Home Assistant."""
from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed, ConfigEntryError

from pynintendoparental.exceptions import (
    InvalidSessionTokenException,
    InvalidOAuthConfigurationException,
)

from .const import DOMAIN
from .coordinator import NintendoUpdateCoordinator, Authenticator

PLATFORMS: list[Platform] = [Platform.SENSOR, Platform.SWITCH, Platform.TIME]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up this integration using UI."""
    hass.data.setdefault(DOMAIN, {})
    try:
        nintendo_auth = await Authenticator.complete_login(
            None, entry.data["session_token"], True
        )
    except InvalidSessionTokenException as err:
        raise ConfigEntryAuthFailed(err) from err
    except InvalidOAuthConfigurationException as err:
        raise ConfigEntryError(err) from err

    coord = NintendoUpdateCoordinator(hass, nintendo_auth, entry)
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
