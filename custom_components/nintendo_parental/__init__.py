"""Custom integration to integrate nintendo_parental with Home Assistant."""
from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .coordinator import NintendoParentalConfigEntry
from .repairs import raise_integration_deprecated

async def async_setup_entry(
    hass: HomeAssistant, entry: NintendoParentalConfigEntry
) -> bool:
    """Set up Nintendo Switch Parental Controls from a config entry."""
    raise_integration_deprecated(hass, entry)
    return True


async def async_unload_entry(
    hass: HomeAssistant, entry: NintendoParentalConfigEntry
) -> bool:
    """Unload a config entry."""
    return True

async def async_migrate_entry(
    hass: HomeAssistant, entry: NintendoParentalConfigEntry
) -> bool:
    """Migrate old entry."""
    if entry.version == 1:
        new_entry = hass.config_entries.async_entry_for_domain_unique_id("nintendo_parental_controls", entry.unique_id)
        if new_entry is None:
            await hass.config_entries.async_add(
                ConfigEntry(
                    version=1,
                    domain="nintendo_parental_controls",
                    title=entry.title,
                    data=entry.data,
                    options=entry.options,
                    source=entry.source,
                    unique_id=entry.unique_id,
                    discovery_keys=entry.discovery_keys,
                    minor_version=entry.minor_version,
                    subentries_data=entry.subentries,
                )
            )
        hass.config_entries.async_remove(entry.entry_id)
        return True
