"""Config flow for the Nintendo Switch Parental Controls integration."""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


class NintendoConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Nintendo Switch Parental Controls."""

    VERSION = 2

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step."""
        return self.async_abort(reason="integration_deprecated")
