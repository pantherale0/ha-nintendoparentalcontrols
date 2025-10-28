"""Nintendo Parental Controls data coordinator."""

from __future__ import annotations

from datetime import timedelta
import logging

from pynintendoparental import NintendoParental
from pynintendoparental.authenticator import Authenticator
from pynintendoparental.exceptions import InvalidOAuthConfigurationException, NoDevicesFoundException

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import issue_registry as ir
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)
UPDATE_INTERVAL = timedelta(seconds=60)


class NintendoUpdateCoordinator(DataUpdateCoordinator[None]):
    """Nintendo data update coordinator."""

    def __init__(
        self,
        hass: HomeAssistant,
        authenticator: Authenticator,
        config_entry: NintendoParentalConfigEntry,
    ) -> None:
        """Initialize update coordinator."""
        super().__init__(
            hass=hass,
            logger=_LOGGER,
            name=DOMAIN,
            update_interval=UPDATE_INTERVAL,
            config_entry=config_entry,
        )

    async def _async_update_data(self) -> None:
        """Update data from Nintendo's API."""
        return

type NintendoParentalConfigEntry = ConfigEntry[NintendoUpdateCoordinator]
