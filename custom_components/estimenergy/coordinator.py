"""Data coordinator for EstimEnergy."""

import logging
from datetime import timedelta
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from estimenergy_client import EstimEnergyClient


_LOGGER = logging.getLogger(__name__)


class EstimEnergyCoordinator(DataUpdateCoordinator):
    """Data coordinator for EstimEnergy."""

    def __init__(self, hass: HomeAssistant, name: str, host: str, port: int) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name=name,
            update_interval=timedelta(seconds=5),
        )

        self.hass = hass
        self.name = name
        self.host = host
        self.port = port
        self.client = EstimEnergyClient(host, port)
        self.collector_id = None
        self._data = None
        self.collector = None

    async def initialize(self) -> None:
        """Initialize the EstimEnergy API connection."""

        collectors = await self.hass.async_add_executor_job(self.client.get_collectors)

        for collector in collectors:
            if collector["name"] == self.name:
                self.collector_id = collector["id"]
                break

        if not self.collector_id:
            raise CollectorNotFoundError(self.name)

    async def _async_update_data(self):
        """Refresh data from API."""

        if self.collector_id is None:
            return None

        self.collector = await self.hass.async_add_executor_job(
            self.client.get_collector, self.collector_id
        )

        return self.collector


class CollectorNotFoundError(Exception):
    """Custom Exception for a collector not being found."""

    def __init__(self, collector_name: str) -> None:
        super().__init__(f"Collector with name {collector_name} not found!")
