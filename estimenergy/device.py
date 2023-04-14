from estimenergy.const import DeviceType
from estimenergy.devices.base_device import BaseDevice
from estimenergy.config import config
from estimenergy.devices.glow_device import GlowDevice


devices: list[BaseDevice] = []

for device_config in config.device_configs:
    if device_config.type == DeviceType.GLOW:
        device = GlowDevice(device_config, config)
        devices.append(device)
