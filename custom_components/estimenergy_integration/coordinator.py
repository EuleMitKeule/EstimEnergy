"""Data coordinator for EstimEnergy."""

import logging
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_PORT
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from prometheus_client.parser import text_string_to_metric_families

from estimenergy.client import EstimEnergyClient
from estimenergy.const import METRICS, Metric

_LOGGER = logging.getLogger(__name__)


class EstimEnergyCoordinator(DataUpdateCoordinator):
    """Data coordinator for EstimEnergy."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        super().__init__(
            hass,
            _LOGGER,
            update_interval=timedelta(seconds=5),
            name="estimenergy",
        )

        self.hass = hass
        self.host = entry.data[CONF_HOST]
        self.port = entry.data[CONF_PORT]
        self.client = EstimEnergyClient(self.host, self.port)

    def get_value_for_metric(self, metric: Metric, samples: list):
        """Get the value for a metric."""

        for sample in samples:
            if sample.name == metric.json_key:
                return sample.value
        return None

    async def _async_update_data(self):
        """Refresh data from API."""

        metrics_text = await self.hass.async_add_executor_job(self.client.get_metrics)

        families = list(text_string_to_metric_families(metrics_text))
        metric_keys = [metric.json_key for metric in METRICS]
        samples = []
        for family in families:
            if family.name not in metric_keys:
                continue
            samples.extend(family.samples)

        data = {
            name: {
                metric.json_key: self.get_value_for_metric(metric, samples)
                for metric in METRICS
            }
            for name in set([sample.labels["name"] for sample in samples])
        }

        return data
