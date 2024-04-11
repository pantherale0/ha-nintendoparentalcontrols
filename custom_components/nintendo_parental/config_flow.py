# pylint: disable=unused-argument
"""Adds config flow for nintendo_parental."""
from __future__ import annotations
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.const import CONF_API_TOKEN
from homeassistant.config_entries import ConfigFlow, ConfigEntry
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import selector
from pynintendoparental import Authenticator

from .const import (
    DOMAIN,
    DEFAULT_UPDATE_INTERVAL,
    CONF_UPDATE_INTERVAL,
    CONF_APPLICATIONS,
    CONF_SESSION_TOKEN
)

from .coordinator import NintendoUpdateCoordinator


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

    async def async_step_nintendo_website_auth(self, user_input=None):
        """Begin auth flow with Nintendo site."""
        if user_input is not None:
            await self.auth.complete_login(self.auth, user_input[CONF_API_TOKEN], False)
            return await self.async_step_configure()
        return self.async_show_form(
            step_id="nintendo_website_auth",
            description_placeholders={"link": self.auth.login_url},
            data_schema=vol.Schema({vol.Required(CONF_API_TOKEN): str}),
        )

    async def async_step_configure(self, user_input=None):
        """Handle configuration request."""
        if user_input is not None:
            if self.auth.account_id is None:
                raise RuntimeError("Init not completed, account_id is null.")
            return self.async_create_entry(
                title=self.auth.account_id,
                data={
                    CONF_SESSION_TOKEN: user_input[CONF_SESSION_TOKEN],
                    CONF_UPDATE_INTERVAL: user_input[CONF_UPDATE_INTERVAL]
                },
            )
        schema = {
            vol.Required(CONF_SESSION_TOKEN, default=self.auth.get_session_token): str,
            vol.Required(CONF_UPDATE_INTERVAL, default=DEFAULT_UPDATE_INTERVAL): int
        }
        return self.async_show_form(step_id="configure", data_schema=vol.Schema(schema))

    async def async_step_reauth(self, user_input=None) -> FlowResult:
        """Handle reauth."""
        self.auth = Authenticator.generate_login()
        self.reauth_entry = self.hass.config_entries.async_get_entry(
            self.context["entry_id"]
        )
        return self.async_show_form(step_id="reauth_login")

    async def async_step_reauth_login(self, user_input=None):
        """Handle reauth login."""
        return await self.async_step_nintendo_website_auth()

    async def async_step_reauth_obtain_token(self, user_input=None):
        """Obtain token and update configuration."""
        if user_input is not None:
            await self.auth.complete_login(self.auth, user_input[CONF_API_TOKEN], False)
            self.hass.config_entries.async_update_entry(
                self.reauth_entry,
                data={
                    **self.reauth_entry.data,
                    CONF_SESSION_TOKEN: self.auth.get_session_token,
                },
            )
            await self.hass.config_entries.async_reload(self.reauth_entry.entry_id)
            return self.async_abort(reason="reauth_successful")

        return self.async_show_form(
            step_id="nintendo_website_auth",
            description_placeholders={"link": self.auth.login_url},
            data_schema={vol.Required(CONF_API_TOKEN): str},
        )


class OptionsFlowHandler(config_entries.OptionsFlow):
    """Option Flow Handler."""

    _session_token = ""
    _update_interval = DEFAULT_UPDATE_INTERVAL
    _applications = []
    _coordinator: NintendoUpdateCoordinator

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    @property
    def _get_application_name_list(self) -> list[str]:
        """Return all applications as a list of names."""
        apps = []
        for device in self._coordinator.api.devices.values():
            for app in device.applications:
                if app.application_id not in apps:
                    apps.append(app.name)
        return apps

    @property
    def _get_application_name_list_enabled(self) -> list[str]:
        """Return list of applications stored in local _applications."""
        apps = []
        for device in self._coordinator.api.devices.values():
            for app in device.applications:
                if (
                    app.application_id not in apps
                    and app.application_id in self._applications
                ):
                    apps.append(app.name)
        return apps

    def _get_application_id_from_name(self, name: str) -> str:
        """Return the application ID from a given name."""
        for device in self._coordinator.api.devices.values():
            for app in device.applications:
                if app.name == name:
                    return app.application_id
        return None

    async def async_step_config(self, user_input: dict[str, Any] | None = None):
        """Extra options flow."""
        if user_input is not None:
            self._session_token = self.config_entry.data[CONF_SESSION_TOKEN]
            self._update_interval = user_input[CONF_UPDATE_INTERVAL]
            return await self.async_step_init()

        update_interval = self.config_entry.data[CONF_UPDATE_INTERVAL]
        if self.config_entry.options:
            update_interval = self.config_entry.options.get(CONF_UPDATE_INTERVAL)

        return self.async_show_form(
            step_id="config",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_UPDATE_INTERVAL, default=update_interval): int
                }
            ),
        )

    async def async_step_applications(self, user_input: dict[str, Any] | None = None):
        """Application configuration."""
        if user_input is not None:
            self._applications = []
            for app_name in user_input[CONF_APPLICATIONS]:
                self._applications.append(self._get_application_id_from_name(app_name))
            return await self.async_step_init()
        return self.async_show_form(
            step_id=CONF_APPLICATIONS,
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_APPLICATIONS, default=[]
                    ): selector.SelectSelector(
                        config=selector.SelectSelectorConfig(
                            mode=selector.SelectSelectorMode.DROPDOWN,
                            options=self._get_application_name_list,
                            multiple=True,
                        )
                    )
                }
            ),
        )

    async def async_step_done(self, _: dict[str, Any] | None = None):
        """Create or update entry."""
        return self.async_create_entry(
            title=self.config_entry.title,
            data={
                CONF_SESSION_TOKEN: self.config_entry.data[CONF_SESSION_TOKEN],
                CONF_UPDATE_INTERVAL: self._update_interval,
                CONF_APPLICATIONS: self._applications
            },
        )

    async def async_step_init(
        self, _: dict[str, Any] | None = None
    ) -> config_entries.FlowResult:
        """First step."""
        self._coordinator: NintendoUpdateCoordinator = self.hass.data[DOMAIN][
            self.config_entry.entry_id
        ]
        return self.async_show_menu(
            step_id="init", menu_options=[CONF_APPLICATIONS, "config", "done"]
        )
