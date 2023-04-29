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
from sqlmodel import Session
from zeroconf import Zeroconf

from estimenergy.const import Metric, MetricPeriod, MetricType
from estimenergy.db import db_engine
from estimenergy.devices import BaseDevice
from estimenergy.devices.device_error import DeviceError
from estimenergy.log import logger
from estimenergy.models.config.config import Config
from estimenergy.models.device_config import DeviceConfig


class GlowDevice(BaseDevice):
    """Home Assistant Glow device."""

    zeroconf: Zeroconf
    api: APIClient
    reconnect_logic: Optional[ReconnectLogic] = None
    last_kwh: Optional[float] = None
    last_time: Optional[datetime.datetime] = None

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

    @property
    def provided_metrics(self) -> list[Metric]:
        return [
            Metric(MetricType.ENERGY, MetricPeriod.DAY, False, False),
            Metric(MetricType.ACCURACY, MetricPeriod.DAY, False, False),
            Metric(MetricType.POWER, MetricPeriod.TOTAL, False, False),
        ]

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

            await self.api.subscribe_states(self.__state_changed)

        async def on_connect_error():
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

    def __state_changed(self, state: SensorState):
        loop = asyncio.get_event_loop()

        if state.key == 2274151077:
            loop.create_task(self.__on_power_changed(state.state))
            return

        if state.key == 2690257735:
            loop.create_task(self.__on_total_kwh_changed(state.state))

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

        logger.debug(
            f"Detected {kwh_increase} kWh increase in {time_increase_us} us for device {self.device_config.name}."
        )

        await self.increment(
            Metric(MetricType.ENERGY, MetricPeriod.DAY, False, False),
            kwh_increase,
            time,
        )
        await self.increment(
            Metric(MetricType.ACCURACY, MetricPeriod.DAY, False, False),
            accuracy_increase,
            time,
        )

        await self.update()

        self.last_kwh = value

    async def __on_power_changed(self, value: float):
        await self.write(
            Metric(MetricType.POWER, MetricPeriod.TOTAL, False, False), value
        )
