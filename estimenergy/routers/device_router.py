from fastapi import APIRouter

from estimenergy.device import devices
from estimenergy.models.config.device_config import DeviceConfigRead


device_router = APIRouter(prefix="/device", tags=["device"])


@device_router.get(
    "",
    response_model=list[DeviceConfigRead],
)
async def get_devices():
    """Get all devices."""

    device_configs = [device.device_config for device in devices]
    return device_configs
