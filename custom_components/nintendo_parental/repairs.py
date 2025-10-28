"""Implementations for repairs."""

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers import issue_registry as ir

from .const import DOMAIN

def raise_integration_deprecated(hass: HomeAssistant, config_entry: ConfigEntry) -> None:
    """Create an issue for the integration deprecation."""
    ir.async_create_issue(
        hass=hass,
        domain=DOMAIN,
        issue_id="integration_deprecated",
        is_persistent=False,
        translation_key="integration_deprecated",
        translation_placeholders={
            "account_id": config_entry.title
        },
        is_fixable=True,
        severity=ir.IssueSeverity.ERROR,
    )
