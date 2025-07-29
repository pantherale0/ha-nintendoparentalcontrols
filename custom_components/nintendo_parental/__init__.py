"""Custom integration to integrate nintendo_parental with Home Assistant."""
from __future__ import annotations

from pynintendoparental.authenticator import Authenticator
from pynintendoparental.exceptions import (
    InvalidOAuthConfigurationException,
    InvalidSessionTokenException,
)

from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryError
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.typing import ConfigType

from .const import CONF_SESSION_TOKEN, DOMAIN
from .coordinator import NintendoParentalConfigEntry, NintendoUpdateCoordinator
from .repairs import raise_invalid_auth
from .services import async_setup_services

PLATFORMS: list[Platform] = [Platform.SENSOR, Platform.SWITCH, Platform.TIME, Platform.NUMBER]

async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the Nintendo Switch Parental Controls integration."""
    async_setup_services(hass)
    return True

async def async_setup_entry(
    hass: HomeAssistant, entry: NintendoParentalConfigEntry
) -> bool:
    """Set up Nintendo Switch Parental Controls from a config entry."""
    try:
        nintendo_auth = await Authenticator.complete_login(
            auth=None,
            response_token=entry.data[CONF_SESSION_TOKEN],
            is_session_token=True,
            client_session=async_get_clientsession(hass),
        )
    except (InvalidSessionTokenException, InvalidOAuthConfigurationException) as err:
        raise_invalid_auth(hass, entry)
        raise ConfigEntryError(
            translation_domain=DOMAIN,
            translation_key="auth_expired",
        ) from err
    entry.runtime_data = coordinator = NintendoUpdateCoordinator(
        hass, nintendo_auth, entry
    )
    await coordinator.async_config_entry_first_refresh()
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(
    hass: HomeAssistant, entry: NintendoParentalConfigEntry
) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
