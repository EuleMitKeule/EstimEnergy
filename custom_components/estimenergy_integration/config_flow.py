from homeassistant import config_entries
import voluptuous as vol

from homeassistant.data_entry_flow import FlowResult

from estimenergy.const import DEFAULT_HOST, DEFAULT_PORT

from .const import (
    DOMAIN,
    CONF_HOST,
    CONF_PORT,
)


class EstimEnergyConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """EstimEnergy config flow."""

    VERSION = 1

    async def async_step_user(self, user_input=None) -> FlowResult:
        if user_input is not None:
            unique_id = f"estimenergy_{user_input[CONF_HOST]}:{user_input[CONF_PORT]}"

            await self.async_set_unique_id(unique_id)
            self._abort_if_unique_id_configured()

            return self.async_create_entry(title=unique_id, data=user_input)

        data_schema = vol.Schema(
            {
                vol.Required(
                    CONF_HOST,
                    default=DEFAULT_HOST,
                ): str,
                vol.Required(
                    CONF_PORT,
                    default=DEFAULT_PORT,
                ): int,
            },
        )

        return self.async_show_form(step_id="user", data_schema=data_schema)
