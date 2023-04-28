from typing import Optional

from sqlmodel import Session, select

from estimenergy.config import config
from estimenergy.const import DeviceType
from estimenergy.db import db_engine
from estimenergy.devices.base_device import BaseDevice
from estimenergy.devices.device_error import DeviceError
from estimenergy.devices.glow_device import GlowDevice
from estimenergy.log import logger
from estimenergy.models.device_config import DeviceConfig


class DeviceRegistry:
    devices: list[BaseDevice] = []

    async def initialize(self):
        """Initialize the DeviceRegistry class."""

        logger.info("Initializing device registry...")

        with Session(db_engine) as session:
            device_configs = session.exec(select(DeviceConfig)).all()

        for device_config in device_configs:
            device = await self.create_device(device_config)

            if device_config.is_active:
                try:
                    await device.start()
                except DeviceError:
                    continue

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

        with Session(db_engine) as session:
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

        if device.device_config.is_active:
            await device.stop()

        with Session(db_engine) as session:
            db_device_config: DeviceConfig = session.exec(
                select(DeviceConfig).where(
                    DeviceConfig.name == device.device_config.name
                )
            ).one()

            db_device_config.name = device_config.name
            db_device_config.type = device_config.type
            db_device_config.host = device_config.host
            db_device_config.port = device_config.port
            db_device_config.password = device_config.password
            db_device_config.cost_per_kwh = device_config.cost_per_kwh
            db_device_config.base_cost_per_month = device_config.base_cost_per_month
            db_device_config.payment_per_month = device_config.payment_per_month
            db_device_config.billing_month = device_config.billing_month
            db_device_config.min_accuracy = device_config.min_accuracy

            session.add(db_device_config)
            session.commit()
            session.refresh(db_device_config)

        self.devices.remove(device)

        if device_config.type == DeviceType.GLOW:
            device = GlowDevice(db_device_config, config)
            self.devices.append(device)

        await device.start()

        return device

    async def delete_device(self, device: BaseDevice):
        """Delete a device for the EstimEnergy application."""

        logger.info(f"Deleting device {device.device_config.name}...")

        if device.device_config.is_active:
            await device.stop()

        with Session(db_engine) as session:
            session.delete(device.device_config)
            session.commit()

        self.devices.remove(device)


device_registry = DeviceRegistry()
