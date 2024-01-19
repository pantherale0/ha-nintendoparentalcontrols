"""Time platform for Home Assistant."""

from datetime import time, timedelta
import logging

from homeassistant.components.time import TimeEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ServiceValidationError
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .coordinator import NintendoUpdateCoordinator
from .const import DOMAIN, TIME_CONFIGURATION_ENTITIES
from .entity import NintendoDevice

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up Nintendo Switch Parental Control switches."""
    coordinator: NintendoUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    entities = []
    if coordinator.api.devices is not None:
        for device in list(coordinator.api.devices.values()):
            for entity_config in TIME_CONFIGURATION_ENTITIES:
                entities.append(
                    NintendoParentalTimeEntity(
                        coordinator, device.device_id, entity_config
                    )
                )
    async_add_entities(entities, True)


class NintendoParentalTimeEntity(NintendoDevice, TimeEntity):
    """An instance of a time entity."""

    _attr_should_poll = True

    def __init__(
        self, coordinator: NintendoUpdateCoordinator, device_id, entity_id
    ) -> None:
        """Create time entity."""
        self._config = TIME_CONFIGURATION_ENTITIES.get(entity_id)
        super().__init__(coordinator, device_id, entity_id)

    @property
    def name(self) -> str:
        """Return entity name."""
        return self._config["name"].format(DEV_NAME=self._device.name)

    def _value(self) -> time:
        """Conversion class for time."""
        if self._config["value"] == "limit_time":
            if self._device.limit_time is None:
                return None
            return time(
                int(
                    str(timedelta(minutes=self._device.limit_time)).split(
                        ":", maxsplit=1
                    )[0]
                ),
                int(
                    str(timedelta(minutes=self._device.limit_time)).split(
                        ":", maxsplit=2
                    )[1]
                ),
                0,
            )
        elif self._config["value"] == "bonus_time":
            if self._device.bonus_time is None:
                return None
            return time(
                int(
                    str(timedelta(minutes=self._device.bonus_time)).split(
                        ":", maxsplit=1
                    )[0]
                ),
                int(
                    str(timedelta(minutes=self._device.bonus_time)).split(
                        ":", maxsplit=2
                    )[1]
                ),
                0,
            )
        elif self._config["value"] == "bedtime":
            return self._device.bedtime_alarm

    @property
    def native_value(self) -> time | None:
        """Return the native value."""
        return self._value()

    async def async_set_value(self, value: time) -> None:
        """Update the value."""
        if self._config.get("update_method") == "update_max_daily_playtime":
            _LOGGER.debug(
                "Got request to update play time for device %s to %s",
                self._device_id,
                value,
            )
            minutes = value.hour * 60
            minutes += value.minute
            if minutes > 360:
                raise ServiceValidationError(
                    "Play Time Limit cannot be more than 6 hours (6:00). To disable, set to 0:00",
                    translation_domain=DOMAIN,
                    translation_key="play_time_limit_out_of_range",
                )
            await self._device.update_max_daily_playtime(minutes)
        if self._config.get("update_method") == "give_bonus_time":
            _LOGGER.debug(
                "Got request to add bonus time for device %s to %s",
                self._device_id,
                value,
            )
            minutes = value.hour * 60
            minutes += value.minute
            await self._device.give_bonus_time(minutes)
        if self._config["update_method"] == "set_bedtime_alarm":
            if value.hour >= 16 and value.hour <= 23:
                await self._device.set_bedtime_alarm(end_time=value, enabled=True)
            elif value.hour == 0 and value.minute == 0:
                await self._device.set_bedtime_alarm(enabled=False)
            else:
                raise ServiceValidationError(
                    "Bedtime Alarm must be between 16:00 and 23:45. To disable, set to 0:00.",
                    translation_domain=DOMAIN,
                    translation_key="bedtime_alarm_out_of_range",
                    translation_placeholders={"time": value.strftime("%H:%M")},
                )
        await self.coordinator.async_request_refresh()
