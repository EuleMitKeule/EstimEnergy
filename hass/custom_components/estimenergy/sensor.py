"""Sensor for EstimEnergy integration."""

from __future__ import annotations
import logging
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.typing import DiscoveryInfoType, ConfigType
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.components.sensor import SensorEntity

from .coordinator import EstimEnergyCoordinator

from .const import (
    CONF_NAME,
    CONF_HOST,
    CONF_PORT,
)


_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up the EstimEnergy sensor platform."""

    coordinator = EstimEnergyCoordinator(
        hass,
        name=entry.data[CONF_NAME],
        host=entry.data[CONF_HOST],
        port=entry.data[CONF_PORT],
    )

    async_add_entities(
        [EstimEnergySensor(coordinator)],
        update_before_add=False,
    )


async def async_setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    async_add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None,
) -> None:
    """Set up the sensor platform."""

    coordinator = EstimEnergyCoordinator(
        hass,
        name=config[CONF_NAME],
        host=config[CONF_HOST],
        port=config[CONF_PORT],
    )

    async_add_entities(
        [EstimEnergySensor(coordinator)],
        update_before_add=False,
    )


class EstimEnergySensor(CoordinatorEntity, SensorEntity):
    """EstimEnergy Sensor class."""

    def __init__(self, coordinator) -> None:
        super().__init__(coordinator)
        self._attr_name = f"{coordinator.name} Sensor"
        self._attr_unique_id = f"{coordinator.name}-sensor"

    @property
    def native_value(self) -> int | None:
        """Return the state of the sensor."""
        return self.coordinator.data
