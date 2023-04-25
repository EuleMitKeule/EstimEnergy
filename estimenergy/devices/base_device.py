"""Abstract class for all devices."""
from abc import ABC, abstractmethod
import datetime
import logging

from estimenergy.const import Metric
from estimenergy.models.config.config import Config
from estimenergy.models.config.device_config import DeviceConfig
from estimenergy.services.data_service import DataService
from estimenergy.services.influx_service import InfluxService
from estimenergy.services.sql_service import SqlService


class BaseDevice(ABC):
    """Abstract class for all devices."""

    config: Config
    device_config: DeviceConfig
    data_services: list[DataService] = []

    def __init__(self, device_config: DeviceConfig, config: Config):
        self.config = config
        self.device_config = device_config

        sql_service = SqlService(self.device_config, config)
        self.data_services.append(sql_service)

        if config.influx_config:
            influx_service = InfluxService(self.device_config, config)
            self.data_services.append(influx_service)

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
        date: datetime.datetime = datetime.datetime.now(),
    ):
        """Increment a metric in the database."""

        if metric not in self.provided_metrics:
            raise ValueError(f"Metric {metric} not provided by this device.")

        for data_service in self.data_services:
            await data_service.increment(metric, value, date)

    async def decrement(
        self,
        metric: Metric,
        value: float,
        date: datetime.datetime = datetime.datetime.now(),
    ):
        """Decrement a metric in the database."""

        if metric not in self.provided_metrics:
            raise ValueError(f"Metric {metric} not provided by this device.")

        for data_service in self.data_services:
            await data_service.decrement(metric, value, date)

    async def write(
        self,
        metric: Metric,
        value: float,
        date: datetime.datetime = datetime.datetime.now(),
    ):
        """Write a metric to the database."""

        if metric not in self.provided_metrics:
            raise ValueError(f"Metric {metric} not provided by this device.")

        for data_service in self.data_services:
            await data_service.write(metric, value, date)

    async def update(
        self,
        date: datetime.datetime = datetime.datetime.now(),
    ):
        """Calculate metrics based on other metrics."""

        for data_service in self.data_services:
            await data_service.update(date)
