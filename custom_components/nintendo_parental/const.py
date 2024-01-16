# pylint: disable=line-too-long
"""Constants for nintendo_parental."""
from logging import Logger, getLogger

from homeassistant.components.sensor import SensorDeviceClass

LOGGER: Logger = getLogger(__package__)

NAME = "Nintendo Switch Parental Controls"
DOMAIN = "nintendo_parental"

MIDDLEWARE_URL = (
    "{HASS}/auth/nintendo?return_url={RETURN}&nav_url={NAV}&title={TITLE}&info={INFO}"
)
AUTH_CALLBACK_PATH = "/auth/nintendo/callback"
AUTH_CALLBACK_NAME = "auth:nintendo:callback"
AUTH_MIDDLEWARE_PATH = "/auth/nintendo"
AUTH_MIDDLEWARE_NAME = "auth:nintendo"
AUTH_MIDDLEWARE_CONTENT = "{CWD}/custom_components/nintendo_parental/middleware.html"

CONF_APPLICATIONS = "applications"
CONF_SESSION_TOKEN = "session_token"
CONF_UPDATE_INTERVAL = "update_interval"
CONF_DEFAULT_MAX_PLAYTIME = "default_max_playtime"


SW_CONFIGURATION_ENTITIES = {
    "restriction_mode": {
        "icon": "mdi:block-helper",
        "name": "{DEV_NAME} Suspend Software Limit",
        "value": "parental_control_settings",
    },
    "alarms_enabled": {
        "icon": "mdi:alarm",
        "name": "{DEV_NAME} Alarms Enabled Today",
        "value": "alarms_enabled",
    },
}

SENSOR_CONFIGURATION_ENTITIES = {
    "screentime": {
        "icon": None,
        "name": "{DEV_NAME} Used Screen Time",
        "native_value": "playing_time",
        "device_class": SensorDeviceClass.DURATION,
        "native_unit_of_measurement": "min",
        "state_attributes": "daily_summaries",
    },
    "time_remaining": {
        "icon": None,
        "name": "{DEV_NAME} Time Remaining",
        "native_value": "time_remaining",
        "device_class": SensorDeviceClass.DURATION,
        "native_unit_of_measurement": "min",
    },
}

TIME_CONFIGURATION_ENTITIES = {
    "today_max_screentime": {
        "name": "{DEV_NAME} Play Time Limit",
        "value": "limit_time",
        "update_method": "update_max_daily_playtime",
    },
    "bonus_time": {
        "name": "{DEV_NAME} Bonus Time",
        "value": "bonus_time",
        "update_method": "give_bonus_time",
    },
    "bedtime_alarm": {
        "name": "{DEV_NAME} Bedtime Alarm",
        "value": "bedtime",
        "update_method": "set_bedtime_alarm",
    },
}

ISSUE_DEPENDANCY_ID = "nintendo_parental_dependancy"
ISSUE_DEPENDANCY_KEY = "dependancy_needs_updating"

GH_REPO_URL = "https://github.com/pantherale0/ha-nintendoparentalcontrols"

DEFAULT_MAX_PLAYTIME = 180
DEFAULT_UPDATE_INTERVAL = 60
