"""Data coordinator for EstimEnergy."""

import logging
from datetime import timedelta
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

# from estimenergy_client import EstimEnergyClient


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

        # self.client = EstimEnergyClient(host, port)
        self.hass = hass
        self.name = name
        self.host = host
        self.port = port
        self.count = 0

    async def _async_update_data(self):
        """Refresh data from API."""
        self.count += 1
        # self.client.get_data(self.name)
        return self.count