# pylint: disable=line-too-long
"""Constants for integration_blueprint."""
from logging import Logger, getLogger

LOGGER: Logger = getLogger(__package__)

NAME = "Nintendo Switch Parental Controls"
DOMAIN = "nintendo_parental"
VERSION = "0.0.4"

MIDDLEWARE_URL = (
    "{HASS}/auth/nintendo?return_url={RETURN}&nav_url={NAV}&title={TITLE}&info={INFO}"
)
AUTH_CALLBACK_PATH = "/auth/nintendo/callback"
AUTH_CALLBACK_NAME = "auth:nintendo:callback"
AUTH_MIDDLEWARE_PATH = "/auth/nintendo"
AUTH_MIDDLEWARE_NAME = "auth:nintendo"
AUTH_MIDDLEWARE_CONTENT = "{CWD}/custom_components/nintendo_parental/middleware.html"

SW_OVERRIDE_LIMIT_INVALID = "Attempted to disable device block when screentime limit was already 0, defaulting to 180 minutes."

SW_CONFIGURATION_ENTITIES = {
    "restriction_mode": {
        "icon": "mdi:block-helper",
        "name": "Suspend Software Limit",
        "value": "parental_control_settings",
    },
    "override": {
        "icon": "mdi:block-helper",
        "name": "Block Device Access",
        "value": "limit_time",
    },
}
