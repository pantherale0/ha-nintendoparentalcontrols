# pylint: disable=unused-argument
"""Adds config flow for nintendo_parental."""
from __future__ import annotations
from typing import Any

from urllib.parse import quote
import os
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.components import http
from homeassistant.components.http.view import HomeAssistantView
from homeassistant.config_entries import ConfigFlow, ConfigEntry
from homeassistant.data_entry_flow import FlowResult
from pynintendoparental import Authenticator
from aiohttp import web_response

from .const import (
    DOMAIN,
    MIDDLEWARE_URL,
    AUTH_CALLBACK_PATH,
    AUTH_CALLBACK_NAME,
    NAME,
    AUTH_MIDDLEWARE_PATH,
    AUTH_MIDDLEWARE_NAME,
    AUTH_MIDDLEWARE_CONTENT,
    DEFAULT_MAX_PLAYTIME,
    DEFAULT_UPDATE_INTERVAL,
)


class BlueprintFlowHandler(ConfigFlow, domain=DOMAIN):
    """Config flow for nintendo_parental."""

    VERSION = 1
    auth = None
    reauth_entry: ConfigEntry | None = None

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> config_entries.OptionsFlow:
        """Create the options flow."""
        return OptionsFlowHandler(config_entry)

    @property
    def auth_url(self) -> str:
        """Return the full authentication URL."""
        if (req := http.current_request.get()) is None:
            raise RuntimeError("No current request in context")
        if (hass_url := req.headers.get("HA-Frontend-Base")) is None:
            raise RuntimeError("No header in request")

        forward_url = f"{hass_url}{AUTH_CALLBACK_PATH}?flow_id={self.flow_id}"
        auth_url = MIDDLEWARE_URL.format(
            HASS=hass_url,
            NAV=quote(self.auth.login_url, safe=""),
            RETURN=forward_url,
            TITLE=quote("Nintendo OAuth Redirection"),
            INFO=quote(
                f"This request has come from your Home Assistant instance to setup {NAME}"
            ),
        )
        return auth_url

    async def _obtain_token(self):
        """Generate authentication token."""
        if (req := http.current_request.get()) is None:
            raise RuntimeError("No current request in context")
        if (token := req.query.get("token")) is None:
            raise RuntimeError("No token returned")
        await self.auth.complete_login(self.auth, token, False)

    async def async_step_user(
        self,
        user_input: dict | None = None,
    ) -> config_entries.FlowResult:
        """Handle a flow initialized by the user."""
        if not user_input:
            # Start an auth flow
            self.auth = Authenticator.generate_login()
            return await self.async_step_nintendo_website_auth()
        return await self.async_show_form(step_id="user")

    async def async_step_nintendo_website_auth(
        self, user_input=None, reauth_flow=False
    ):
        """Begin external auth flow with Nintendo via middleware site."""
        if http.current_request.get() is not None:
            self.hass.http.register_view(MiddlewareServerView)
            self.hass.http.register_view(MiddlewareCallbackView)
            if reauth_flow:
                return self.async_external_step(
                    step_id="reauth_obtain_token", url=self.auth_url
                )
            return self.async_external_step(step_id="obtain_token", url=self.auth_url)

    async def async_step_obtain_token(self, user_input=None):
        """Obtain token and complete auth after external auth completed."""
        await self._obtain_token()
        return self.async_external_step_done(next_step_id="configure")

    async def async_step_configure(self, user_input=None):
        """Handle configuration request."""
        schema = {
            vol.Required("session_token", default=self.auth.get_session_token): str,
            vol.Required("update_interval", default=DEFAULT_UPDATE_INTERVAL): int,
            vol.Required("default_max_playtime", default=DEFAULT_MAX_PLAYTIME): int,
        }
        return self.async_show_form(step_id="complete", data_schema=vol.Schema(schema))

    async def async_step_complete(self, user_input=None):
        """Completion step."""
        if self.auth.account_id is None:
            raise RuntimeError("Init not completed, account_id is null.")
        return self.async_create_entry(
            title=self.auth.account_id,
            data={
                "session_token": user_input["session_token"],
                "update_interval": user_input["update_interval"],
            },
        )

    async def async_step_reauth(self, user_input=None) -> FlowResult:
        """Handle reauth."""
        self.auth = Authenticator.generate_login()
        self.reauth_entry = self.hass.config_entries.async_get_entry(
            self.context["entry_id"]
        )
        return self.async_show_form(step_id="reauth_login")

    async def async_step_reauth_login(self, user_input=None):
        """Handle reauth login."""
        return await self.async_step_nintendo_website_auth(reauth_flow=True)

    async def async_step_reauth_obtain_token(self, user_input=None):
        """Obtain token and update configuration."""
        if self.reauth_entry:
            await self._obtain_token()
            self.hass.config_entries.async_update_entry(
                self.reauth_entry,
                data={
                    **self.reauth_entry.data,
                    "session_token": self.auth.get_session_token,
                },
            )
            await self.hass.config_entries.async_reload(self.reauth_entry.entry_id)
            return self.async_abort(reason="reauth_successful")


class OptionsFlowHandler(config_entries.OptionsFlow):
    """Option Flow Handler."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.FlowResult:
        """First step."""

        if user_input is not None:
            return self.async_create_entry(
                title=self.config_entry.title,
                data={
                    "session_token": self.config_entry.data["session_token"],
                    "update_interval": user_input["update_interval"],
                    "default_max_playtime": user_input["default_max_playtime"],
                },
            )

        default_max_playtime = self.config_entry.data.get(
            "default_max_playtime", DEFAULT_MAX_PLAYTIME
        )
        update_interval = self.config_entry.data["update_interval"]
        if self.config_entry.options:
            update_interval = self.config_entry.options.get("update_interval")
            default_max_playtime = self.config_entry.options.get(
                "default_max_playtime", DEFAULT_MAX_PLAYTIME
            )

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Required("update_interval", default=update_interval): int,
                    vol.Required(
                        "default_max_playtime", default=default_max_playtime
                    ): int,
                }
            ),
        )


class MiddlewareServerView(HomeAssistantView):
    """Serve the static html content for the middleware controller."""

    url = AUTH_MIDDLEWARE_PATH
    name = AUTH_MIDDLEWARE_NAME
    requires_auth = False

    async def get(self, request):
        """Receive get request to serve content."""

        return web_response.Response(
            headers={"content-type": "text/html"},
            text=open(
                AUTH_MIDDLEWARE_CONTENT.format(CWD=os.getcwd()), encoding="utf-8"
            ).read(),
        )


class MiddlewareCallbackView(HomeAssistantView):
    """Handle callback from external auth."""

    url = AUTH_CALLBACK_PATH
    name = AUTH_CALLBACK_NAME
    requires_auth = False

    async def get(self, request):
        """Receive authorization request."""
        hass = request.app["hass"]
        await hass.config_entries.flow.async_configure(
            flow_id=request.query["flow_id"], user_input=None
        )

        return web_response.Response(
            headers={"content-type": "text/html"},
            text="<script>window.close()</script>Success! This window can be closed",
        )
