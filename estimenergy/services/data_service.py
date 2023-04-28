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

    async def last(
        self,
        metric: Metric,
        value_dt: datetime.datetime = datetime.datetime.now(),
    ) -> float:
        """Return the last value for a metric."""

        if metric not in self.supported_metrics:
            return 0

        return await self._last(metric, value_dt)

    async def write(
        self,
        metric: Metric,
        value: float,
        value_dt: datetime.datetime = datetime.datetime.now(),
    ):
        """Write a metric to the database."""

        if metric not in self.supported_metrics:
            return

        await self._write(metric, value, value_dt)

    async def increment(
        self,
        metric: Metric,
        value: float,
        value_dt: datetime.datetime = datetime.datetime.now(),
    ):
        """Increment a metric in the database."""

        if metric not in self.supported_metrics:
            return

        last_value = await self.last(metric, value_dt)

        await self.write(metric, last_value + value, value_dt)

    async def decrement(
        self,
        metric: Metric,
        value: float,
        value_dt: datetime.datetime = datetime.datetime.now(),
    ):
        """Decrement a metric in the database."""

        if metric not in self.supported_metrics:
            return

        last_value = await self.last(metric, value_dt)

        await self.write(metric, last_value - value, value_dt)

    @property
    @abstractmethod
    def supported_metrics(self) -> list[Metric]:
        """Return a list of metrics supported by this service."""

    @abstractmethod
    async def _last(
        self,
        metric: Metric,
        value_dt: datetime.datetime = datetime.datetime.now(),
    ) -> float:
        """Get the last value for a metric."""

    @abstractmethod
    async def _write(
        self,
        metric: Metric,
        value: float,
        value_dt: datetime.datetime = datetime.datetime.now(),
    ):
        """Write a metric to the database."""

    @abstractmethod
    async def update(
        self,
        value_dt: datetime.datetime = datetime.datetime.now(),
    ):
        """Update metrics."""
