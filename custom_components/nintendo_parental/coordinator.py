"""DataUpdateCoordinator for nintendo_parental."""
from __future__ import annotations
import contextlib

from datetime import timedelta

import async_timeout

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers import issue_registry as ir
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)

from pynintendoparental import NintendoParental, Authenticator
from pynintendoparental.exceptions import (
    InvalidSessionTokenException,
    InvalidOAuthConfigurationException,
)

from .const import DOMAIN, LOGGER, DEFAULT_MAX_PLAYTIME


class NintendoUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from the API."""

    def __init__(
        self,
        hass: HomeAssistant,
        authenticator: Authenticator,
        config_entry: ConfigEntry,
    ) -> None:
        """Initialize."""
        update_interval = config_entry.data["update_interval"]
        if config_entry.options:
            update_interval = config_entry.options.get("update_interval")
        super().__init__(
            hass=hass,
            logger=LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=update_interval),
        )

        self.api: NintendoParental = NintendoParental(
            auth=authenticator,
            timezone=hass.config.time_zone,
            lang=hass.config.language,
        )
        self.config_entry: ConfigEntry = config_entry
        self.default_max_playtime = config_entry.data.get(
            "default_max_playtime", DEFAULT_MAX_PLAYTIME
        )
        if config_entry.options:
            self.default_max_playtime = config_entry.options.get(
                "default_max_playtime", DEFAULT_MAX_PLAYTIME
            )

    async def _async_update_data(self):
        """Request the API to update."""
        try:
            with contextlib.suppress(InvalidSessionTokenException):
                async with async_timeout.timeout(50):
                    return await self.api.update()
        except InvalidOAuthConfigurationException as err:
            raise ConfigEntryAuthFailed(err) from err
        except Exception as err:
            raise UpdateFailed(err) from err
