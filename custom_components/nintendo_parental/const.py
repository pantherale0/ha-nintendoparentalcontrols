"""Constants for integration_blueprint."""
from logging import Logger, getLogger

LOGGER: Logger = getLogger(__package__)

NAME = "Nintendo Switch Parental Controls"
DOMAIN = "nintendo_parental"
VERSION = "0.0.1"

MIDDLEWARE_URL = "https://static.system32.uk/hass_middleware.html?return_url={RETURN}&nav_url={NAV}"
AUTH_CALLBACK_PATH = "/auth/nintendo/callback"
AUTH_CALLBACK_NAME = "auth:nintendo:callback"
