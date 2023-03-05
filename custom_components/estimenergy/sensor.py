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
from estimenergy.const import (
    JSON_BILLING_MONTH,
    JSON_DATA,
    JSON_DAY_KWH,
    JSON_DAY_COST,
    JSON_DAY_COST_DIFFERENCE,
    JSON_MONTH_KWH_RAW,
    JSON_YEAR_KWH_RAW,
    JSON_MONTH_KWH,
    JSON_MONTH_COST,
    JSON_MONTH_COST_DIFFERENCE,
    JSON_YEAR_KWH,
    SENSOR_TYPE_FRIENDLY_NAME,
    SENSOR_TYPE_JSON,
    SENSOR_TYPE_UNIQUE_ID,
    CONF_NAME,
    CONF_HOST,
    CONF_PORT,
)


_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up the EstimEnergy sensor platform."""

    client = EstimEnergyClient()
    collectors = await hass.async_add_executor_job(client.get_collectors)

    coordinator = EstimEnergyCoordinator(
        hass,
        host=entry.data[CONF_HOST],
        port=entry.data[CONF_PORT],
    )

    await coordinator.initialize()

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
        self._attr_name = f"EstimEnergy {coordinator.name} {metric.friendly_name}"
        self._attr_unique_id = f"estimenergy-{coordinator.name}-{metric.json_key}"

    @property
    def device_class(self) -> SensorDeviceClass | None:
        """Return the class of this entity."""
        if self.json_key in [
            JSON_DAY_KWH,
            JSON_MONTH_KWH_RAW,
            JSON_YEAR_KWH_RAW,
            JSON_MONTH_KWH,
            JSON_YEAR_KWH,
        ]:
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

        billing_month = self.coordinator.data[JSON_BILLING_MONTH]
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
            or JSON_METRICS not in self.coordinator.data
            or self.metric.json_key not in self.coordinator.data[JSON_METRICS]
        ):
            return None

        return self.coordinator.data[JSON_METRICS][self.metric.json_key]

    @property
    def suggested_display_precision(self) -> int | None:
        """Return the suggested number of decimal digits for display."""
        return 2

    @property
    def native_unit_of_measurement(self) -> str | None:
        """Return the unit of measurement of the sensor."""
        if self.json_key in [
            JSON_DAY_KWH,
            JSON_MONTH_KWH_RAW,
            JSON_YEAR_KWH_RAW,
            JSON_MONTH_KWH,
            JSON_YEAR_KWH,
        ]:
            return UnitOfEnergy.KILO_WATT_HOUR

        if self.device_class == SensorDeviceClass.MONETARY:
            currency = self.hass.config.currency
            if currency is None:
                currency = CURRENCY_EURO

            return currency

        return PERCENTAGE
