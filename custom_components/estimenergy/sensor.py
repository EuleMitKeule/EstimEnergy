"""Sensor for EstimEnergy integration."""

from __future__ import annotations
import logging
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.typing import DiscoveryInfoType, ConfigType
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.components.sensor import SensorEntity
from homeassistant.const import CURRENCY_EURO
from homeassistant.const import UnitOfEnergy
from .const import (
    SENSOR_DAY_KWH,
    SENSOR_MONTH_KWH_RAW,
    SENSOR_YEAR_KWH_RAW,
    SENSOR_MONTH_KWH,
    SENSOR_YEAR_KWH,
)

from .coordinator import EstimEnergyCoordinator

from .const import CONF_NAME, CONF_HOST, CONF_PORT, SENSOR_TYPES


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

    sensors = [
        EstimEnergySensor(coordinator, sensor_type=sensor_type)
        for sensor_type in SENSOR_TYPES
    ]

    async_add_entities(
        sensors,
        update_before_add=True,
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

    sensors = [
        EstimEnergySensor(coordinator, sensor_type=sensor_type)
        for sensor_type in SENSOR_TYPES
    ]

    async_add_entities(
        sensors,
        update_before_add=True,
    )


class EstimEnergySensor(CoordinatorEntity, SensorEntity):
    """EstimEnergy Sensor class."""

    def __init__(self, coordinator: EstimEnergyCoordinator, sensor_type: str) -> None:
        super().__init__(coordinator)
        self.sensor_type = sensor_type
        self._attr_name = f"EstimEnergy {coordinator.name} {self.sensor_type}"
        self._attr_unique_id = f"estimenergy-{coordinator.name}-{self.sensor_type}"

    @property
    def native_value(self) -> int | None:
        """Return the state of the sensor."""
        if (
            self.coordinator.data is None
            or self.sensor_type not in self.coordinator.data
        ):
            return None

        return self.coordinator.data[self.sensor_type]

    @property
    def native_unit_of_measurement(self) -> str | None:
        """Return the unit of measurement of the sensor."""
        if (
            self.sensor_type == SENSOR_DAY_KWH
            or self.sensor_type == SENSOR_MONTH_KWH_RAW
            or self.sensor_type == SENSOR_YEAR_KWH_RAW
            or self.sensor_type == SENSOR_MONTH_KWH
            or self.sensor_type == SENSOR_YEAR_KWH
        ):
            return UnitOfEnergy.KILO_WATT_HOUR
        else:
            currency = self.hass.config.currency
            if currency is None:
                currency = CURRENCY_EURO

            return currency
