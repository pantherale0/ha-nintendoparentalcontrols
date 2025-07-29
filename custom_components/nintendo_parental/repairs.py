"""Implementations for repairs."""

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers import issue_registry as ir

from .const import DOMAIN

def raise_no_devices_found(hass: HomeAssistant, config_entry: ConfigEntry) -> None:
    """Create an issue if no devices are found."""
    ir.async_create_issue(
        hass=hass,
        domain=DOMAIN,
        issue_id="no_devices_found",
        is_fixable=False,
        is_persistent=False,
        severity=ir.IssueSeverity.WARNING,
        translation_key="no_devices_found",
        translation_placeholders={
            "account_id": config_entry.title
        }
    )

def raise_invalid_auth(hass: HomeAssistant, config_entry: ConfigEntry) -> None:
    """Create an issue if the auth is invalid."""
    ir.async_create_issue(
        hass=hass,
        domain=DOMAIN,
        issue_id="invalid_auth",
        is_fixable=False,
        is_persistent=False,
        severity=ir.IssueSeverity.ERROR,
        translation_key="invalid_auth",
        translation_placeholders={
            "account_id": config_entry.title
        }
    )
