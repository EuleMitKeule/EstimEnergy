
from homeassistant import config_entries
import voluptuous as vol

from .const import (
    DOMAIN,
    CONF_NAME,
    CONF_HOST,
    CONF_PORT,
    DEFAULT_HOST,
    DEFAULT_PORT,
)

class EstimEnergyConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """EstimEnergy config flow."""
    VERSION = 1

    async def async_step_user(self, user_input=None):

        if user_input is not None:
            collector_name = user_input["collector_name"]

            unique_id = f"estimenergy_{collector_name}"
            
            await self.async_set_unique_id(unique_id)
            self._abort_if_unique_id_configured()
            
            return self.async_create_entry(
                title=collector_name.title(),
                data=user_input
            )

        data_schema = vol.Schema(
            {
                vol.Required(
                    CONF_NAME,
                ): str,
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

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema
        )