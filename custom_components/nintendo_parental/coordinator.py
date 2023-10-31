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

from .const import DOMAIN, LOGGER


async def async_device_issue_registry(
    coord: NintendoUpdateCoordinator, hass: HomeAssistant
):
    """Use the issue registry to raise issues for specific switch devices."""
    for device in coord.api.devices:
        if device.application_update_failed or device.stats_update_failed:
            ir.create_issue(
                hass,
                DOMAIN,
                issue_id=device.device_id + "configuration_error",
                is_fixable=False,
                is_persistent=False,
                severity=ir.IssueSeverity.WARNING,
                translation_key="configuration_error",
                translation_placeholders={"name": device.name},
            )
        else:
            with contextlib.suppress(TypeError):
                # check if an issue exists for ISSUE_DEPENDANCY_ID
                issue = await ir.async_get(hass).async_get_issue(
                    domain=DOMAIN, issue_id=device.device_id + "configuration_error"
                )
                if issue is not None:
                    await ir.async_delete_issue(
                        hass, DOMAIN, device.device_id + "configuration_error"
                    )


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
            with contextlib.suppress(InvalidSessionTokenException):
                async with async_timeout.timeout(50):
                    await self.api.update()
                    await async_device_issue_registry(self, self.hass)
        except InvalidOAuthConfigurationException as err:
            raise ConfigEntryAuthFailed(err) from err
        except Exception as err:
            raise UpdateFailed(err) from err
