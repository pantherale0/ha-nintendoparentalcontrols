"""Custom integration to integrate nintendo_parental with Home Assistant."""
from __future__ import annotations
import contextlib

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed, ConfigEntryError
from homeassistant.helpers import issue_registry as ir

from pynintendoparental.exceptions import (
    InvalidSessionTokenException,
    InvalidOAuthConfigurationException,
)

from .const import DOMAIN, ISSUE_DEPENDANCY_ID, ISSUE_DEPENDANCY_KEY, GH_REPO_URL
from .coordinator import NintendoUpdateCoordinator, Authenticator

PLATFORMS: list[Platform] = [Platform.SENSOR, Platform.SWITCH]


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
        ir.create_issue(
            hass,
            DOMAIN,
            issue_id=ISSUE_DEPENDANCY_ID,
            is_fixable=False,
            severity=ir.IssueSeverity.ERROR,
            translation_key=ISSUE_DEPENDANCY_KEY,
            learn_more_url=GH_REPO_URL,
        )
        raise ConfigEntryError(err) from err

    with contextlib.suppress(TypeError):
        # check if an issue exists for ISSUE_DEPENDANCY_ID
        issue = await ir.async_get(hass).async_get_issue(
            domain=DOMAIN, issue_id=ISSUE_DEPENDANCY_ID
        )
        if issue is not None:
            await ir.async_delete_issue(hass, DOMAIN, ISSUE_DEPENDANCY_ID)

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
