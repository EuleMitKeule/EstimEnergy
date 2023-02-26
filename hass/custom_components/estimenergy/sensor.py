"""Sensor for EstimEnergy integration."""
from __future__ import annotations

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, HomeAssistantType

from .const import (
    DOMAIN,
    CONF_NAME,
)


async def async_setup_entry(
    hass: HomeAssistantType, entry: ConfigType, async_add_entities
) -> None:
    """Set up the EstimEnergy sensor platform."""

    hass_data = hass.data[DOMAIN][entry.entry_id]

    async_add_entities(
        [
            EstimEnergySensor(entry.data, hass_data)
        ],
        False,
    )

class EstimEnergySensor(SensorEntity):
    """Representation of a Sensor."""

    def __init__(self, entry_data, hass_data) -> None:
        """Initialize the sensor."""
        self._state = None
        self._name = f"EstimEnergy {entry_data[CONF_NAME]}"
        self._unique_id = f"estimenergy_{entry_data[CONF_NAME]}"

    @property
    def name(self) -> str:
        """Return the name of the sensor."""
        return self._name
    
    @property
    def unique_id(self) -> str:
        """Return the unique id of the sensor."""
        return self._unique_id

    @property
    def platform(self) -> str:
        """Return the platform name."""
        return "EstimEnergy"

    @property
    def state(self) -> str | None:
        """Return the state of the sensor."""
        return self._state

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return self._state is not None

    async def async_update(self) -> None:
        """Get the latest data and updates the states."""
        self._state = "Works!"