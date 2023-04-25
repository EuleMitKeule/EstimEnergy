"""Home Assistant Glow device."""
import asyncio
import datetime
from typing import Optional

from aioesphomeapi import (
    APIClient,
    APIConnectionError,
    DeviceInfo,
    InvalidEncryptionKeyAPIError,
    ReconnectLogic,
    RequiresEncryptionAPIError,
    ResolveAPIError,
    SensorState,
)
from zeroconf import Zeroconf

from estimenergy.const import Metric, MetricPeriod, MetricType
from estimenergy.devices import BaseDevice
from estimenergy.log import logger
from estimenergy.models.config.config import Config
from estimenergy.models.config.device_config import DeviceConfig


class GlowDevice(BaseDevice):
    """Home Assistant Glow device."""

    zeroconf: Zeroconf
    api: APIClient
    reconnect_logic: ReconnectLogic
    device_info: Optional[DeviceInfo] = None
    last_kwh: Optional[float] = None
    last_time: Optional[datetime.datetime] = None

    def __init__(self, device_config: DeviceConfig, config: Config):
        super().__init__(device_config, config)

        self.zeroconf = Zeroconf()
        self.api = APIClient(
            self.device_config.host,
            self.device_config.port,
            self.device_config.password,
            zeroconf_instance=self.zeroconf,
        )
        self.reconnect_logic = ReconnectLogic(
            client=self.api,
            on_connect=self.__on_connect,
            on_disconnect=self.__on_disconnect,
            zeroconf_instance=self.zeroconf,
            name=self.device_config.name,
            on_connect_error=self.__on_connect_error,
        )

    @property
    def provided_metrics(self) -> list[Metric]:
        return [
            Metric(MetricType.ENERGY, MetricPeriod.DAY, False, False),
            Metric(MetricType.ACCURACY, MetricPeriod.DAY, False, False),
            Metric(MetricType.POWER, MetricPeriod.TOTAL, False, False),
        ]

    async def start(self):
        if not await self.__try_login():
            logger.error(f"Unable to login to {self.device_config.name}")
            return
        await self.reconnect_logic.start()

    async def __try_login(self):
        try:
            await self.api.connect(login=True)
            self.device_info = await self.api.device_info()
            return True
        except (
            ResolveAPIError,
            APIConnectionError,
            InvalidEncryptionKeyAPIError,
            RequiresEncryptionAPIError,
        ):
            return False
        finally:
            await self.api.disconnect(force=True)

    async def __on_connect(self):
        logger.info(f"Connected to ESPHome Device {self.device_config.name}")

        try:
            await self.api.subscribe_states(self.__state_changed)
        except APIConnectionError:
            await self.api.disconnect()

    async def __on_disconnect(self):
        logger.warn(f"Disconnected from ESPHome Device {self.device_config.name}")

    async def __on_connect_error(self, exception: Exception):
        logger.error(f"Error connecting to ESPHome Device {self.device_config.name}")
        logger.error(exception)

    def __state_changed(self, state: SensorState):
        loop = asyncio.get_event_loop()

        if state.key == 2274151077:
            loop.create_task(self.__on_power_changed(state.state))
            return

        if state.key == 2690257735:
            loop.create_task(self.__on_total_kwh_changed(state.state))
            return

    async def __on_total_kwh_changed(self, value: float):
        if self.last_kwh is None or self.last_time is None:
            self.last_kwh = value
            self.last_time = datetime.datetime.now()
            return

        if value < self.last_kwh:
            self.last_kwh = value
            logger.warning("Detected a reset of the total kWh counter.")
            return

        time = datetime.datetime.now()

        kwh_increase = value - self.last_kwh
        time_increase_us = (time - self.last_time).microseconds
        us_per_day = 1000 * 1000 * 60 * 60 * 24
        accuracy_increase = time_increase_us / us_per_day

        await self.increment(
            Metric(MetricType.ENERGY, MetricPeriod.DAY, False, False), kwh_increase
        )
        await self.increment(
            Metric(MetricType.ACCURACY, MetricPeriod.DAY, False, False),
            accuracy_increase,
        )

        await self.update()

        self.last_kwh = value

    async def __on_power_changed(self, value: float):
        await self.write(
            Metric(MetricType.POWER, MetricPeriod.TOTAL, False, False), value
        )
