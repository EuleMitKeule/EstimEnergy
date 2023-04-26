import asyncio
from typing import Optional

from sqlmodel import Session, select
from estimenergy.config import config
from estimenergy.const import DeviceType
from estimenergy.devices.glow_device import GlowDevice
from estimenergy.log import logger
from estimenergy.devices.base_device import BaseDevice
from estimenergy.models.device_config import DeviceConfig
from estimenergy.db import db_engine


class DeviceRegistry:
    devices: list[BaseDevice] = []

    async def initialize(self):
        """Initialize the DeviceRegistry class."""

        logger.info("Initializing device registry...")

        with Session(db_engine) as session:
            device_configs = session.exec(select(DeviceConfig)).all()

            for device_config in device_configs:
                device = await self.create_device(device_config)
                await self.start_device(device)

    async def device_exists(self, device_name: str) -> bool:
        """Check if a device exists."""

        return await self.get_device(device_name) is not None

    async def get_device(self, device_name: str) -> Optional[BaseDevice]:
        """Get a device by name."""

        for device in self.devices:
            if device.device_config.name == device_name:
                return device

        return None

    async def create_device(self, device_config: DeviceConfig) -> BaseDevice:
        """Create a device for the EstimEnergy application."""

        logger.info(f"Creating device {device_config.name}...")

        # check if the device_config is already present in the database
        with Session(db_engine) as session:
            device_config_db = session.exec(
                select(DeviceConfig).where(DeviceConfig.name == device_config.name)
            ).first()

            if device_config_db is None:
                session.add(device_config)
                session.commit()
                session.refresh(device_config)

        if device_config.type == DeviceType.GLOW:
            device = GlowDevice(device_config, config)
            self.devices.append(device)

        return device

    async def update_device(
        self, device: BaseDevice, device_config: DeviceConfig
    ) -> BaseDevice:
        """Update a device for the EstimEnergy application."""

        logger.info(f"Updating device {device.device_config.name}...")

        device_config.host = device.device_config.host
        device_config.port = device.device_config.port
        device_config.password = device.device_config.password

        await device.stop()
        await self.delete_device(device)

        device = await device_registry.create_device(device_config)
        await device_registry.start_device(device)

        return device

    async def delete_device(self, device: BaseDevice):
        """Delete a device for the EstimEnergy application."""

        logger.info(f"Deleting device {device.device_config.name}...")

        await device.stop()

        with Session(db_engine) as session:
            session.delete(device.device_config)
            session.commit()

        self.devices.remove(device)

    async def start_device(self, device: BaseDevice):
        """Start a device for the EstimEnergy application."""

        logger.info(f"Starting device {device.device_config.name}...")

        asyncio.create_task(device.start())


device_registry = DeviceRegistry()
