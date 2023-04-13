import asyncio
import datetime
from typing import Optional

from aioesphomeapi import (
    APIClient,
    APIConnectionError,
    InvalidEncryptionKeyAPIError,
    ReconnectLogic,
    RequiresEncryptionAPIError,
    ResolveAPIError,
    SensorState,
)
from zeroconf import Zeroconf
from estimenergy.const import Metric, MetricPeriod, MetricType

from estimenergy.devices import Device
from estimenergy.models.config.device_config import DeviceConfig


class GlowDevice(Device):
    last_kwh: Optional[float]
    last_time: Optional[datetime.datetime]

    def __init__(self, device_config: DeviceConfig):
        super().__init__(device_config)

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

        self.device_info = None
        self.last_kwh = None
        self.last_time = None

    @property
    def provided_metrics(self) -> list[Metric]:
        return [
            Metric(MetricType.ENERGY, MetricPeriod.DAY, False, False),
            Metric(MetricType.ACCURACY, MetricPeriod.DAY, False, False),
            Metric(MetricType.POWER, MetricPeriod.TOTAL, False, False),
        ]

    async def start(self):
        if not await self.__try_login():
            self.logger.error(f"Unable to login to {self.device_config.name}")
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
        self.logger.info(f"Connected to ESPHome Device {self.device_config.name}")

        try:
            await self.api.subscribe_states(self.__state_changed)
        except APIConnectionError:
            await self.api.disconnect()

    async def __on_disconnect(self):
        self.logger.warn(f"Disconnected from ESPHome Device {self.device_config.name}")

    async def __on_connect_error(self, exception: Exception):
        self.logger.error(
            f"Error connecting to ESPHome Device {self.device_config.name}"
        )
        self.logger.error(exception)

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
            self.logger.warn("Detected a reset of the total kWh counter.")
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

    # async def __on_kwh_changed(self, current_kwh: float):
    # date = get_current_datetime()

    # self.logger.info(f"Current KWh: {current_kwh}")

    # energy_data = await EnergyData.filter(
    #     collector=self.collector_config,
    #     year=date.year,
    #     month=date.month,
    #     day=date.day,
    # ).first()
    # previous_energy_data = await self.__get_previous_energy_data(date)

    # if energy_data is None:
    #     if (
    #         previous_energy_data is not None
    #         and current_kwh > previous_energy_data.kwh
    #     ):
    #         previous_energy_data.kwh = current_kwh
    #         previous_energy_data.hour_updated = 23
    #         previous_energy_data.is_completed = True
    #         await previous_energy_data.save()
    #         return

    #     energy_data = EnergyData(
    #         collector=self.collector_config,
    #         year=date.year,
    #         month=date.month,
    #         day=date.day,
    #         kwh=current_kwh,
    #         hour_created=date.hour,
    #         hour_updated=date.hour,
    #         is_completed=False,
    #     )

    #     await energy_data.save()
    #     await self.__update_previous_energy_data(date)
    #     return

    # if energy_data.kwh > current_kwh:
    #     return

    # energy_data.kwh = current_kwh
    # energy_data.hour_updated = date.hour
    # await energy_data.save()
    # await self.metrics.update_metrics()

    # async def __update_previous_energy_data(self, date):
    #     previous_energy_data = await self.__get_previous_energy_data(date)

    #     if previous_energy_data is None:
    #         return

    #     if previous_energy_data.hour_updated < 23:
    #         return

    #     previous_energy_data.is_completed = True
    #     await previous_energy_data.save()

    # async def __get_previous_energy_data(self, date):
    #     date_yesterday = date - datetime.timedelta(days=1)
    #     return await EnergyData.filter(
    #         collector=self.collector_config,
    #         year=date_yesterday.year,
    #         month=date_yesterday.month,
    #         day=date_yesterday.day,
    #     ).first()
