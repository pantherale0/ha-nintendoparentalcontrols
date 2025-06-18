"""DataUpdateCoordinator for nintendo_parental."""

from __future__ import annotations
import contextlib

from datetime import timedelta

import async_timeout

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)

from pynintendoparental import NintendoParental, Authenticator
from pynintendoparental.exceptions import (
    InvalidSessionTokenException,
    InvalidOAuthConfigurationException,
)

from .const import (
    DOMAIN,
    LOGGER,
    DEFAULT_MAX_PLAYTIME,
    CONF_DEFAULT_MAX_PLAYTIME,
    CONF_UPDATE_INTERVAL,
    CONF_EXPERIMENTAL
)


class NintendoUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from the API."""

    def __init__(
        self,
        hass: HomeAssistant,
        authenticator: Authenticator,
        config_entry: ConfigEntry,
    ) -> None:
        """Initialize."""
        self._config_update_interval = config_entry.data[CONF_UPDATE_INTERVAL]
        if config_entry.options:
            self._config_update_interval = config_entry.options.get(
                CONF_UPDATE_INTERVAL
            )
        super().__init__(
            hass=hass,
            logger=LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=self._config_update_interval),
        )

        self.api: NintendoParental = NintendoParental(
            auth=authenticator,
            timezone=hass.config.time_zone,
            lang=hass.config.language,
        )
        self.config_entry: ConfigEntry = config_entry
        self.default_max_playtime = config_entry.data.get(
            CONF_DEFAULT_MAX_PLAYTIME, DEFAULT_MAX_PLAYTIME
        )
        self.experimental_mode = config_entry.data.get(CONF_EXPERIMENTAL, False)
        if config_entry.options:
            self.default_max_playtime = config_entry.options.get(
                CONF_DEFAULT_MAX_PLAYTIME, DEFAULT_MAX_PLAYTIME
            )
            self.experimental_mode = config_entry.options.get(
                CONF_EXPERIMENTAL, False
            )

    async def _async_update_data(self):
        """Request the API to update."""
        try:
            return await self.api.update()
        except InvalidOAuthConfigurationException as err:
            raise ConfigEntryAuthFailed(err) from err
        except Exception as err:
            raise UpdateFailed(err) from err
