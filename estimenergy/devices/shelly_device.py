import asyncio
import logging

import aiohttp
from aioshelly.block_device import COAP, BlockDevice
from aioshelly.common import ConnectionOptions
from aioshelly.exceptions import (
    DeviceConnectionError,
    FirmwareUnsupported,
    InvalidAuthError,
)
from sqlmodel import Session, select

from estimenergy.db import db_engine
from estimenergy.devices.base_device import BaseDevice
from estimenergy.devices.device_error import DeviceError
from estimenergy.models.config.config import Config
from estimenergy.models.device_config import DeviceConfig
from estimenergy.models.shelly_config import ShellyConfig

_LOGGER = logging.getLogger(__name__)


class ShellyDevice(BaseDevice):
    """Shelly device."""

    shelly_config: ShellyConfig
    connection_options: ConnectionOptions

    def __init__(self, device_config: DeviceConfig, config: Config):
        """Initialize the Shelly device."""

        super().__init__(device_config, config)

        with Session(db_engine) as session:
            self.shelly_config = session.exec(
                select(ShellyConfig).where(
                    ShellyConfig.id == device_config.shelly_config_id
                )
            ).one()

        self.connection_options = ConnectionOptions(
            ip_address=self.shelly_config.host,
            username=self.shelly_config.username,
            password=self.shelly_config.password,
        )

    async def start(self) -> None:
        async with aiohttp.ClientSession() as client_session, COAP() as coap_context:
            device = await self.__create_device(client_session, coap_context)

        self.is_running = True

        loop = asyncio.get_event_loop()
        loop.create_task(self.__poll())

    async def stop(self):
        pass

    async def __create_device(
        self, client_session: aiohttp.ClientSession, coap_context: COAP
    ) -> BlockDevice:
        try:
            device: BlockDevice = await BlockDevice.create(
                client_session, coap_context, self.connection_options
            )
        except FirmwareUnsupported as err:
            raise DeviceError(f"Device firmware not supported, error: {repr(err)}")
        except InvalidAuthError as err:
            raise DeviceError(f"Invalid or missing authorization, error: {repr(err)}")
        except DeviceConnectionError as err:
            raise DeviceError(
                f"Error connecting to {self.connection_options.ip_address}, error: {repr(err)}"
            )

        return device

    async def __poll(self):
        while self.is_running:
            async with aiohttp.ClientSession() as client_session, COAP() as coap_context:
                device = await self.__create_device(client_session, coap_context)
                await device.update()

                for block in device.blocks:
                    values = block.current_values()
                    if "energy" in values:
                        value_wattminutes = values["energy"]
                        value_kilowatthours = value_wattminutes / 1000 / 60
                        await self.__on_energy_changed(value_kilowatthours)

                await asyncio.sleep(self.shelly_config.poll_interval)

    async def __on_energy_changed(self, energy: float):
        _LOGGER.info(f"Energy changed: {energy}")
