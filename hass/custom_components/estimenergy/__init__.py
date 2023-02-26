"""EstimEnergy integration."""

import logging

from .const import (
    PLATFORM,
    DOMAIN,
    CONF_NAME,
    CONF_HOST,
    CONF_PORT,
)

_LOGGER = logging.getLogger(__name__)

async def async_setup(hass, config) -> bool:
    return True

async def async_setup_entry(hass, entry) -> bool:
    """Set up EstimEnergy from a config entry."""

    name = entry.data[CONF_NAME]
    host = entry.data[CONF_HOST]
    port = entry.data[CONF_PORT]

    hass_data = hass.data.setdefault(DOMAIN, {})

    await hass.config_entries.async_forward_entry_setup(entry, PLATFORM)
    
    return True