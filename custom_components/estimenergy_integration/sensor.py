"""Sensor for EstimEnergy integration."""

from __future__ import annotations
from datetime import datetime
import logging
from homeassistant.components.sensor import SensorDeviceClass, SensorStateClass
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.components.sensor import SensorEntity
from homeassistant.const import CURRENCY_EURO, PERCENTAGE
from homeassistant.const import UnitOfEnergy
from estimenergy.client import EstimEnergyClient
from estimenergy.const import METRICS, Metric, MetricType, MetricPeriod

from .const import CONF_HOST, CONF_PORT
from .coordinator import EstimEnergyCoordinator


_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up the EstimEnergy sensor platform."""

    client = EstimEnergyClient(entry.data[CONF_HOST], entry.data[CONF_PORT])
    collectors = await hass.async_add_executor_job(client.get_collectors)

    coordinator = EstimEnergyCoordinator(
        hass,
        entry,
    )

    for collector in collectors:
        sensors = [
            EstimEnergySensor(coordinator, metric=metric, collector=collector)
            for metric in METRICS
        ]

        async_add_entities(
            sensors,
            update_before_add=True,
        )


class EstimEnergySensor(CoordinatorEntity, SensorEntity):
    """EstimEnergy Sensor class."""

    def __init__(
        self, coordinator: EstimEnergyCoordinator, metric: Metric, collector: dict
    ) -> None:
        super().__init__(coordinator)
        self.metric = metric
        self.collector = collector
        self._attr_name = f"EstimEnergy {collector['name']} {metric.friendly_name}"
        self._attr_unique_id = f"estimenergy-{collector['name']}-{metric.json_key}"

    @property
    def device_class(self) -> SensorDeviceClass | None:
        """Return the class of this entity."""
        if self.metric.metric_type == MetricType.ENERGY:
            return SensorDeviceClass.ENERGY

        if self.metric.metric_type in [MetricType.COST, MetricType.COST_DIFFERENCE]:
            return SensorDeviceClass.MONETARY

        return None

    @property
    def options(self) -> list[str] | None:
        """Return a set of possible options."""
        return None

    @property
    def state_class(self) -> SensorStateClass | str | None:
        """Return the state class of this entity, if any."""
        return SensorStateClass.TOTAL

    @property
    def last_reset(self) -> datetime | None:
        """Return the time when the sensor was last reset, if any."""
        if self.metric.metric_period == MetricPeriod.DAY:
            return datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

        if self.metric.metric_period == MetricPeriod.MONTH:
            return datetime.now().replace(
                day=1, hour=0, minute=0, second=0, microsecond=0
            )

        if self.metric.metric_period == MetricPeriod.TOTAL:
            return None

        billing_month = self.collector["billing_month"]
        now = datetime.now()

        return now.replace(
            year=now.year - (1 if now.month < billing_month else 0),
            month=billing_month,
            day=1,
            hour=0,
            minute=0,
            second=0,
            microsecond=0,
        )

    @property
    def native_value(self) -> int | None:
        """Return the state of the sensor."""
        if (
            self.coordinator.data is None
            or self.collector["name"] not in self.coordinator.data
            or self.metric.json_key not in self.coordinator.data[self.collector["name"]]
        ):
            return None

        return self.coordinator.data[self.collector["name"]][self.metric.json_key]

    @property
    def suggested_display_precision(self) -> int | None:
        """Return the suggested number of decimal digits for display."""
        return 2

    @property
    def native_unit_of_measurement(self) -> str | None:
        """Return the unit of measurement of the sensor."""
        if self.device_class == SensorDeviceClass.ENERGY:
            return UnitOfEnergy.KILO_WATT_HOUR

        if self.device_class == SensorDeviceClass.MONETARY:
            currency = self.hass.config.currency
            if currency is None:
                currency = CURRENCY_EURO

            return currency

        return PERCENTAGE
