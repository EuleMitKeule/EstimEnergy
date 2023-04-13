"""Abstract class for all devices."""
import datetime
import logging
from abc import ABC, abstractmethod
from estimenergy.const import METRICS, DeviceType, Metric
from estimenergy.models.config.device_config import DeviceConfig
from estimenergy.services.data_service import DataService
from estimenergy.common import config
from estimenergy.services.influx_service import InfluxService
from estimenergy.services.sql_service import SqlService


class Device(ABC):
    """Abstract class for all devices."""

    device_config: DeviceConfig
    data_services: list[DataService] = []

    def __init__(self, device_config: DeviceConfig):
        self.device_config = device_config

        sql_service = SqlService(self.device_config)
        self.data_services.append(sql_service)

        if config.influx_config:
            influx_service = InfluxService(self.device_config)
            self.data_services.append(influx_service)

        self.logger = logging.getLogger("estimenergy").getChild(self.device_config.name)

    @property
    @abstractmethod
    def provided_metrics(self) -> list[Metric]:
        """Return a list of metrics provided by this device."""

    @abstractmethod
    async def start(self):
        """Start the device."""

    async def increment(
        self,
        metric: Metric,
        value: float,
        value_dt: datetime.datetime = datetime.datetime.now(),
    ):
        """Increment a metric in the database."""

        if metric not in self.provided_metrics:
            raise ValueError(f"Metric {metric} not provided by this device.")

        for data_service in self.data_services:
            await data_service.increment(metric, value, value_dt)

    async def decrement(
        self,
        metric: Metric,
        value: float,
        value_dt: datetime.datetime = datetime.datetime.now(),
    ):
        """Decrement a metric in the database."""

        if metric not in self.provided_metrics:
            raise ValueError(f"Metric {metric} not provided by this device.")

        for data_service in self.data_services:
            await data_service.decrement(metric, value, value_dt)

    async def write(
        self,
        metric: Metric,
        value: float,
        value_dt: datetime.datetime = datetime.datetime.now(),
    ):
        """Write a metric to the database."""

        if metric not in self.provided_metrics:
            raise ValueError(f"Metric {metric} not provided by this device.")

        for data_service in self.data_services:
            await data_service.write(metric, value, value_dt)

    async def update(
        self,
        value_dt: datetime.datetime = datetime.datetime.now(),
    ):
        """Calculate metrics based on other metrics."""

        for metric in [
            metric for metric in METRICS if not metric in self.provided_metrics
        ]:
            for data_service in self.data_services:
                await data_service.update(metric, value_dt)
