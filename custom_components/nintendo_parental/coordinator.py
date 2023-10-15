"""DataUpdateCoordinator for nintendo_parental."""
from __future__ import annotations

from datetime import timedelta

import async_timeout

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)

from pynintendoparental import NintendoParental, Authenticator

from .const import DOMAIN, LOGGER


class NintendoUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from the API."""

    config_entry: ConfigEntry

    def __init__(
        self, hass: HomeAssistant, update_interval: int, authenticator: Authenticator
    ) -> None:
        """Initialize."""
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

    async def _async_update_data(self):
        """Request the API to update."""
        try:
            async with async_timeout.timeout(50):
                return await self.api.update()
        except Exception as err:
            LOGGER.error(err)
            raise UpdateFailed(err) from err
