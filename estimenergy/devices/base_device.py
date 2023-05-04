"""Abstract class for all devices."""
from abc import ABC, abstractmethod
import datetime
from typing import Optional, Type

from estimenergy.const import Metric
from estimenergy.models.config.config import Config
from estimenergy.models.device_config import DeviceConfig
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

    @abstractmethod
    async def start(self):
        """Start the device."""

    @abstractmethod
    async def stop(self):
        """Stop the device."""

    async def write(
        self,
        metric: Metric,
        value: float,
        value_dt: datetime.datetime,
    ):
        """Write a metric to the database."""

        for data_service in self.data_services:
            await data_service.write(metric, value, value_dt)

        await self.update(value_dt)

    async def update(
        self,
        value_dt: datetime.datetime,
    ):
        """Calculate metrics based on other metrics."""

        for data_service in self.data_services:
            await data_service.update(value_dt)

    async def last(
        self,
        metric: Metric,
        value_dt: datetime.datetime,
    ) -> Optional[float]:
        """Get the last value of a metric."""

        sql_service: SqlService = next(
            (
                data_service
                for data_service in self.data_services
                if isinstance(data_service, SqlService)
            ),
        )

        if sql_service:
            return await sql_service.last(metric, value_dt)

        return None
