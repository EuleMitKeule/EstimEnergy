"""Abstract class for all devices."""
from abc import ABC, abstractmethod
import datetime

from estimenergy.const import Metric
from estimenergy.models.config.config import Config
from estimenergy.models.device_config import DeviceConfig, DeviceConfigRead
from estimenergy.services.data_service import DataService
from estimenergy.services.influx_service import InfluxService
from estimenergy.services.prometheus_service import PrometheusService
from estimenergy.services.sql_service import SqlService


class BaseDevice(ABC):
    """Abstract class for all devices."""

    config: Config
    device_config: DeviceConfig
    data_services: list[DataService]

    def __init__(self, device_config: DeviceConfig, config: Config):
        self.data_services = []
        self.config = config
        self.device_config = device_config

        sql_service = SqlService(self.device_config, config)
        self.data_services.append(sql_service)

        prometheus_service = PrometheusService(sql_service, self.device_config, config)
        self.data_services.append(prometheus_service)

        if config.influx_config:
            influx_service = InfluxService(self.device_config, config)
            self.data_services.append(influx_service)

    @property
    @abstractmethod
    def provided_metrics(self) -> list[Metric]:
        """Return a list of metrics provided by this device."""

    @abstractmethod
    async def stop(self):
        """Stop the device."""

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

        for data_service in self.data_services:
            await data_service.update(value_dt)
