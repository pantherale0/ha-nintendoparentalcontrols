"""Adds config flow for Blueprint."""
from __future__ import annotations

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.components import http
from homeassistant.components.http.view import HomeAssistantView
from urllib.parse import quote

from aiohttp import web_response

from .const import DOMAIN, MIDDLEWARE_URL, AUTH_CALLBACK_PATH, AUTH_CALLBACK_NAME

from pynintendoparental import Authenticator

class BlueprintFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for Blueprint."""

    VERSION = 1
    AUTH = None

    async def async_step_user(
        self,
        user_input: dict | None = None,
    ) -> config_entries.FlowResult:
        """Handle a flow initialized by the user."""
        if not user_input:
            # Start an auth flow
            self.AUTH = Authenticator.generate_login()
            return await self.async_step_nintendo_website_auth()
        return await self.async_show_form(step_id="user")

    async def async_step_nintendo_website_auth(self, user_input=None):
        """Begin external auth flow with Nintendo via middleware site."""
        self.hass.http.register_view(MiddlewareCallbackView)
        if (req := http.current_request.get()) is None:
            raise RuntimeError("No current request in context")
        if (hass_url := req.headers.get("HA-Frontend-Base")) is None:
            raise RuntimeError("No header in request")

        forward_url = f"{hass_url}{AUTH_CALLBACK_PATH}?flow_id={self.flow_id}"
        auth_url = MIDDLEWARE_URL.format(
            NAV=quote(self.AUTH.login_url, safe=""),
            RETURN=forward_url
        )
        return self.async_external_step(step_id="obtain_token", url=auth_url)

    async def async_step_obtain_token(self, user_input=None):
        """Obtain token and complete auth after external auth completed."""
        if (req := http.current_request.get()) is None:
            raise RuntimeError("No current request in context")
        if (token := req.query.get("token")) is None:
            raise RuntimeError("No token returned")
        await self.AUTH.complete_login(self.AUTH, token, False)
        return self.async_external_step_done(next_step_id="configure")

    async def async_step_configure(self, user_input=None):
        """Handles the configuration section."""
        schema = {
            vol.Required("session_token", default=self.AUTH._session_token): str,
            vol.Required("update_interval", default=60): int
        }
        return self.async_show_form(step_id="complete", data_schema=vol.Schema(schema))

    async def async_step_complete(self, user_input=None):
        """Completion step"""
        if self.AUTH.account_id is None:
            raise RuntimeError("Init not completed, account_id is null.")
        return self.async_create_entry(
            title=self.AUTH.account_id,
            data={
                "session_token": user_input["session_token"],
                "update_interval": user_input["update_interval"]
            }
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
            text="<script>window.close()</script>Success! This window can be closed"
        )
