"""Nintendo Parental Controls data coordinator."""

from __future__ import annotations

from datetime import timedelta
import logging

from pynintendoparental import NintendoParental
from pynintendoparental.authenticator import Authenticator
from pynintendoparental.exceptions import InvalidOAuthConfigurationException, NoDevicesFoundException

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryError
from homeassistant.helpers import issue_registry as ir
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import DOMAIN
from .repairs import raise_no_devices_found, raise_invalid_auth

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
        self.api = NintendoParental(
            authenticator, hass.config.time_zone, hass.config.language
        )

    async def _async_update_data(self) -> None:
        """Update data from Nintendo's API."""
        try:
            issue_registry = ir.async_get(self.hass)
            issue_ids_to_track = ["no_devices_found", "invalid_auth"]
            await self.api.update()
            for issue_id in issue_ids_to_track:
                issue = issue_registry.async_get_issue(domain=DOMAIN, issue_id=issue_id)
                if issue:
                    ir.async_delete_issue(self.hass, DOMAIN, issue.issue_id)
        except NoDevicesFoundException:
            raise_no_devices_found(self.hass, self.config_entry)
        except InvalidOAuthConfigurationException:
            raise_invalid_auth(self.hass, self.config_entry)

type NintendoParentalConfigEntry = ConfigEntry[NintendoUpdateCoordinator]
