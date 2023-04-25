"""Device module for the EstimEnergy application."""
import asyncio

from estimenergy.config import config
from estimenergy.const import DeviceType
from estimenergy.devices.base_device import BaseDevice
from estimenergy.devices.glow_device import GlowDevice
from estimenergy.log import logger

devices: list[BaseDevice] = []


def create_devices():
    """Create the devices for the EstimEnergy application."""

    logger.info("Creating devices...")

    for device_config in config.device_configs:
        if device_config.type == DeviceType.GLOW:
            device = GlowDevice(device_config, config)
            devices.append(device)


def start_devices():
    """Start the devices for the EstimEnergy application."""

    logger.info("Starting devices...")

    for device in devices:
        asyncio.create_task(device.start())
