import logging
from typing import Optional

from fastapi import Depends
from sqlalchemy.exc import NoResultFound
from sqlmodel import Session, select

from estimenergy.config import config
from estimenergy.const import DeviceType
from estimenergy.db import db_engine, get_session
from estimenergy.devices.base_device import BaseDevice
from estimenergy.devices.device_error import DeviceError
from estimenergy.devices.glow_device import GlowDevice
from estimenergy.devices.shelly_device import ShellyDevice
from estimenergy.log import logger
from estimenergy.models.device_config import DeviceConfig, DeviceConfigIn
from estimenergy.models.glow_config import GlowConfig
from estimenergy.models.shelly_config import ShellyConfig

_LOGGER = logging.getLogger(__name__)


class DeviceRegistry:
    devices: list[BaseDevice] = []

    async def initialize(self):
        """Initialize the DeviceRegistry class."""

        _LOGGER.info("Initializing device registry...")

        with Session(db_engine, expire_on_commit=False) as session:
            device_configs = session.exec(select(DeviceConfig)).all()

            for device_config in device_configs:
                try:
                    await self.recreate_device(device_config, session)
                except DeviceError as e:
                    _LOGGER.error(e)
                    continue

    async def device_exists(self, device_name, session: Session) -> bool:
        """Check if a device exists."""

        try:
            await self.get_device_config(device_name, session)
            return True
        except NoResultFound:
            return False

    async def get_device_config(
        self, device_name: str, session: Session
    ) -> DeviceConfig:
        """Get a device config by name."""

        device_config = session.exec(
            select(DeviceConfig).where(DeviceConfig.name == device_name)
        ).one()

        return device_config

    async def get_device(self, device_name: str, session: Session) -> BaseDevice:
        """Get a device by name."""

        device_config = await self.get_device_config(device_name, session)
        device = next(
            (
                device
                for device in self.devices
                if device.device_config.id == device_config.id
            ),
            None,
        )

        if device is None:
            raise NoResultFound(f"Device {device_name} not found.")

        return device

    async def create_device_config(
        self, device_config_in: DeviceConfigIn, session: Session
    ) -> DeviceConfig:
        """Create a device config."""

        _LOGGER.info(f"Creating device config {device_config_in.name}...")

        device_config = DeviceConfig.from_orm(device_config_in)

        if device_config_in.device_type == DeviceType.GLOW:
            glow_config = GlowConfig.from_orm(device_config_in.glow_config)
            session.add(glow_config)
            session.commit()
            session.refresh(glow_config)
            device_config.glow_config_id = glow_config.id
            device_config.glow_config = glow_config
        elif device_config_in.device_type == DeviceType.SHELLY:
            shelly_config = ShellyConfig.from_orm(device_config_in.shelly_config)
            session.add(shelly_config)
            session.commit()
            session.refresh(shelly_config)
            device_config.shelly_config_id = shelly_config.id
            device_config.shelly_config = shelly_config
        else:
            raise DeviceError(f"Device type not supported.")

        session.add(device_config)
        session.commit()
        session.refresh(device_config)

        return device_config

    async def recreate_device(self, device_config: DeviceConfig, session) -> BaseDevice:
        """Recreate a device."""

        _LOGGER.info(f"Creating device {device_config.name}...")

        device: BaseDevice

        if device_config.device_type == DeviceType.GLOW:
            device = GlowDevice(device_config, config)
            self.devices.append(device)
        elif device_config.device_type == DeviceType.SHELLY:
            device = ShellyDevice(device_config, config)
            self.devices.append(device)
        else:
            raise DeviceError(f"Device type not supported.")

        if device_config.is_active:
            await self.start_device(device_config.name, session)

        return device

    async def create_device(
        self, device_config_in: DeviceConfigIn, session
    ) -> BaseDevice:
        """Create a device."""

        device_config = await self.create_device_config(device_config_in, session)

        device = await self.recreate_device(device_config, session)

        return device

    async def update_device(
        self, device_name: str, device_config_in: DeviceConfigIn, session: Session
    ) -> DeviceConfig:
        """Update a device."""

        _LOGGER.info(f"Updating device {device_name}...")

        await self.delete_device(device_name, session)

        device = await self.create_device(device_config_in, session)

        return device.device_config

    async def delete_device_config(self, device_name: str, session: Session) -> None:
        """Delete a device config."""

        _LOGGER.info(f"Deleting device config {device_name}...")

        device_config = await self.get_device_config(device_name, session)

        session.delete(device_config)
        session.commit()

    async def delete_device(self, device_name: str, session: Session) -> None:
        """Delete a device for the EstimEnergy application."""

        _LOGGER.info(f"Deleting device {device_name}...")

        device = await self.get_device(device_name, session)

        await self.stop_device(device_name, session)
        await self.delete_device_config(device_name, session)

        self.devices.remove(device)

    async def start_device(self, device_name: str, session: Session) -> None:
        """Start a device."""

        device_config = await self.get_device_config(device_name, session)
        device = await self.get_device(device_name, session)

        if device.is_running:
            _LOGGER.info(f"Ignoring start for running device {device_name}.")
            return

        _LOGGER.info(f"Starting device {device_name}...")

        await device.start()

        device_config.is_active = True
        session.add(device_config)
        session.commit()

    async def stop_device(self, device_name: str, session: Session) -> None:
        """Stop a device."""

        device_config = await self.get_device_config(device_name, session)
        device = await self.get_device(device_name, session)

        if not device.is_running:
            _LOGGER.info(f"Ignoring stop for stopped device {device_name}.")
            return

        _LOGGER.info(f"Stopping device {device_name}...")

        await device.stop()

        device_config.is_active = False
        session.add(device_config)
        session.commit()


device_registry = DeviceRegistry()
