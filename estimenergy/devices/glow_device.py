"""Home Assistant Glow device."""
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
from sqlmodel import Session
from zeroconf import Zeroconf

from estimenergy.const import Metric, MetricPeriod, MetricType
from estimenergy.db import db_engine
from estimenergy.devices import BaseDevice
from estimenergy.devices.device_error import DeviceError
from estimenergy.log import logger
from estimenergy.models.config.config import Config
from estimenergy.models.device_config import DeviceConfig


class EnergySplit:
    energy_start: float
    energy_last: float
    time_start: datetime.datetime
    time_last: datetime.datetime

    def __init__(self, energy_start: float, time_start: datetime.datetime):
        self.energy_start = energy_start
        self.energy_last = energy_start
        self.time_start = time_start
        self.time_last = time_start

    def update(self, energy: float, time: datetime.datetime):
        self.energy_last = energy
        self.time_last = time


class GlowDevice(BaseDevice):
    """Home Assistant Glow device."""

    zeroconf: Zeroconf
    api: APIClient
    reconnect_logic: Optional[ReconnectLogic]
    energy_splits: list[EnergySplit]
    current_split: Optional[EnergySplit]

    def __init__(self, device_config: DeviceConfig, config: Config):
        """Initialize the Glow device."""

        super().__init__(device_config, config)

        self.zeroconf = Zeroconf()
        self.api = APIClient(
            self.device_config.host,
            self.device_config.port,
            self.device_config.password,
            zeroconf_instance=self.zeroconf,
        )
        self.reconnect_logic = None
        self.energy_splits = []
        self.current_split = None

    async def start(self):
        """Start the device."""

        with Session(db_engine) as session:
            self.device_config.is_active = True
            session.add(self.device_config)
            session.commit()
            session.refresh(self.device_config)

        if not await self.can_connect():
            logger.error(f"Unable to login to {self.device_config.name}")
            raise DeviceError(f"Unable to login to {self.device_config.name}")

        event = asyncio.Event()

        async def on_connect():
            logger.info(f"Connected to ESPHome Device {self.device_config.name}")
            event.set()

            with Session(db_engine) as session:
                self.device_config.is_connected = True
                session.add(self.device_config)
                session.commit()
                session.refresh(self.device_config)

            await self.__initialize_data_splits()

            await self.api.subscribe_states(self.__state_changed)

        async def on_connect_error(error: Exception):
            _ = error
            with Session(db_engine) as session:
                self.device_config.is_connected = False
                session.add(self.device_config)
                session.commit()
                session.refresh(self.device_config)

            raise DeviceError(f"Unable to connect to {self.device_config.name}")

        async def on_disconnect():
            with Session(db_engine) as session:
                self.device_config.is_connected = False
                session.add(self.device_config)
                session.commit()
                session.refresh(self.device_config)

        self.reconnect_logic = ReconnectLogic(
            client=self.api,
            on_connect=on_connect,
            on_disconnect=on_disconnect,
            zeroconf_instance=self.zeroconf,
            name=self.device_config.name,
            on_connect_error=on_connect_error,
        )

        await self.reconnect_logic.start()

        await event.wait()

    async def stop(self):
        """Stop the device."""

        logger.info(f"Stopping ESPHome Device {self.device_config.name}")

        with Session(db_engine) as session:
            self.device_config.is_active = False
            session.add(self.device_config)
            session.commit()
            session.refresh(self.device_config)

        await self.api.disconnect(force=True)
        if self.reconnect_logic is not None:
            await self.reconnect_logic.stop()
        self.zeroconf.close()

    async def can_connect(self) -> bool:
        """Check if we can connect to the device."""
        try:
            await self.api.connect(login=True)
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

    async def __initialize_data_splits(self):
        current_timezone = datetime.datetime.now().astimezone().tzinfo
        current_dt = datetime.datetime.now(tz=current_timezone)

        time_start: datetime.datetime = datetime.datetime.now().replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        energy_start: float = 0
        energy_split: EnergySplit = EnergySplit(energy_start, time_start)

        last_energy: float = await self.last(
            Metric(MetricType.ENERGY, MetricPeriod.DAY, False, False), current_dt
        )
        last_accuracy: float = await self.last(
            Metric(MetricType.ACCURACY, MetricPeriod.DAY, False, False), current_dt
        )
        last_time = time_start + datetime.timedelta(
            seconds=last_accuracy * 60 * 60 * 24
        )
        energy_split.update(last_energy, last_time)

        self.energy_splits.append(energy_split)

    def __state_changed(self, state: SensorState):
        loop = asyncio.get_event_loop()

        if state.key == 2274151077:
            loop.create_task(self.__on_power_changed(state.state))
            return

        if state.key == 2690257735:
            loop.create_task(self.__on_total_energy_changed(state.state))

    async def __on_total_energy_changed(self, value: float):
        current_timezone = datetime.datetime.now().astimezone().tzinfo
        current_dt = datetime.datetime.now(tz=current_timezone)

        if self.current_split is None:
            self.current_split = EnergySplit(value, current_dt)
            return

        if value < self.current_split.energy_last:
            self.energy_splits.append(self.current_split)
            self.current_split = EnergySplit(value, current_dt)
            return

        if self.current_split.time_last.date() != current_dt.date():
            self.energy_splits = []
            self.current_split = EnergySplit(value, current_dt)
            return

        self.current_split.update(value, current_dt)

        energy_daily_total: float = (
            sum(
                [
                    energy_data_split.energy_last - energy_data_split.energy_start
                    for energy_data_split in self.energy_splits
                ]
            )
            + self.current_split.energy_last
            - self.current_split.energy_start
        )
        seconds_daily_total: float = (
            sum(
                [
                    (
                        energy_data_split.time_last - energy_data_split.time_start
                    ).total_seconds()
                    for energy_data_split in self.energy_splits
                ]
            )
        ) + (
            self.current_split.time_last - self.current_split.time_start
        ).total_seconds()
        accuracy_daily_total: float = seconds_daily_total / (60 * 60 * 24)

        await self.write(
            Metric(MetricType.ENERGY, MetricPeriod.DAY, False, False),
            energy_daily_total,
            current_dt,
        )
        await self.write(
            Metric(MetricType.ACCURACY, MetricPeriod.DAY, False, False),
            accuracy_daily_total,
            current_dt,
        )

    async def __on_power_changed(self, value: float):
        current_timezone = datetime.datetime.now().astimezone().tzinfo
        value_dt = datetime.datetime.now(tz=current_timezone)

        await self.write(
            Metric(MetricType.POWER, MetricPeriod.TOTAL, False, False), value, value_dt
        )
