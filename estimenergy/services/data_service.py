"""Abstract class for all data services."""
from abc import ABC, abstractmethod
import datetime

from estimenergy.const import Metric
from estimenergy.models.config.config import Config
from estimenergy.models.device_config import DeviceConfig


class DataService(ABC):
    """Abstract class for all data services."""

    device_config: DeviceConfig
    config: Config

    def __init__(self, device_config: DeviceConfig, config: Config):
        self.device_config = device_config
        self.config = config

    @abstractmethod
    async def write(
        self,
        metric: Metric,
        value: float,
        value_dt: datetime.datetime,
    ):
        """Write a metric to the database."""

    @abstractmethod
    async def update(
        self,
        value_dt: datetime.datetime,
    ):
        """Update metrics."""
