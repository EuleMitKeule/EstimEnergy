"""Abstract class for all data services."""
from abc import ABC, abstractmethod
import datetime
from estimenergy.const import Metric
from estimenergy.models.config.device_config import DeviceConfig


class DataService(ABC):
    """Abstract class for all data services."""

    device_config: DeviceConfig

    def __init__(
        self,
        device_config: DeviceConfig,
    ):
        self.device_config = device_config

    async def last(
        self,
        metric: Metric,
        date: datetime.datetime = datetime.datetime.now(),
    ) -> float:
        """Return the last value for a metric."""

        if metric not in self.supported_metrics:
            return 0

        return await self._last(metric, date)

    async def write(
        self,
        metric: Metric,
        value: float,
        date: datetime.datetime = datetime.datetime.now(),
    ):
        """Write a metric to the database."""

        if metric not in self.supported_metrics:
            return

        await self._write(metric, value, date)

    async def increment(
        self,
        metric: Metric,
        value: float,
        date: datetime.datetime = datetime.datetime.now(),
    ):
        """Increment a metric in the database."""

        if metric not in self.supported_metrics:
            return

        last_value = await self.last(metric, date)

        await self.write(metric, last_value + value, date)

    async def decrement(
        self,
        metric: Metric,
        value: float,
        date: datetime.datetime = datetime.datetime.now(),
    ):
        """Decrement a metric in the database."""

        if metric not in self.supported_metrics:
            return

        last_value = await self.last(metric, date)

        await self.write(metric, last_value - value, date)

    async def update(
        self,
        metric: Metric,
        date: datetime.datetime = datetime.datetime.now(),
    ):
        """Update a metric."""

        if metric.is_predicted:
            await self._predict(metric, date)
            return

        await self._calculate(metric, date)

    @property
    @abstractmethod
    def supported_metrics(self) -> list[Metric]:
        """Return a list of metrics supported by this service."""

    @abstractmethod
    async def _last(
        self,
        metric: Metric,
        date: datetime.datetime = datetime.datetime.now(),
    ) -> float:
        """Get the last value for a metric."""

    @abstractmethod
    async def _write(
        self,
        metric: Metric,
        value: float,
        date: datetime.datetime = datetime.datetime.now(),
    ):
        """Write a metric to the database."""

    @abstractmethod
    async def _calculate(
        self,
        metric: Metric,
        date: datetime.datetime = datetime.datetime.now(),
    ):
        """Calculate a metric."""

    @abstractmethod
    async def _predict(
        self,
        metric: Metric,
        date: datetime.datetime = datetime.datetime.now(),
    ):
        """Predict a metric."""
