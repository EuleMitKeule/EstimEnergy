from fastapi import APIRouter, HTTPException
from sqlmodel import Session

from estimenergy.devices import device_registry
from estimenergy.devices.device_error import DeviceError
from estimenergy.models.device_config import DeviceConfig, DeviceConfigRead
from estimenergy.db import db_engine


device_router = APIRouter(prefix="/device", tags=["device"])


@device_router.post("", response_model=DeviceConfigRead, operation_id="create_device")
async def create_device(device_config: DeviceConfig):
    """Create a new device."""

    device = await device_registry.create_device(device_config)

    try:
        await device.start()
    except DeviceError as device_error:
        raise HTTPException(
            status_code=500, detail="Device failed to start"
        ) from device_error

    return device.device_config


@device_router.get(
    "/{device_name}", response_model=DeviceConfigRead, operation_id="get_device"
)
async def get_device(device_name: str):
    """Get a device."""

    device = await device_registry.get_device(device_name)
    return device.device_config


@device_router.get(
    "", response_model=list[DeviceConfigRead], operation_id="get_devices"
)
async def get_devices():
    """Get all devices."""

    device_configs = [device.device_config for device in device_registry.devices]
    return device_configs


@device_router.put(
    "/{device_name}", response_model=DeviceConfigRead, operation_id="update_device"
)
async def update_device(device_name: str, device_config: DeviceConfig):
    """Update a device."""

    device = await device_registry.get_device(device_name)
    device = await device_registry.update_device(device, device_config)

    return device.device_config


@device_router.delete(
    "/{device_name}", response_model=DeviceConfigRead, operation_id="delete_device"
)
async def delete_device(device_name: str):
    """Delete a device."""

    device = await device_registry.get_device(device_name)
    await device_registry.delete_device(device)

    return device.device_config


@device_router.post(
    "/{device_name}/start", response_model=DeviceConfigRead, operation_id="start_device"
)
async def start_device(device_name: str):
    """Start a device."""

    device = await device_registry.get_device(device_name)

    try:
        await device.start()
    except DeviceError as device_error:
        raise HTTPException(
            status_code=500, detail="Device failed to start"
        ) from device_error

    return device.device_config


@device_router.post(
    "/{device_name}/stop", response_model=DeviceConfigRead, operation_id="stop_device"
)
async def stop_device(device_name: str):
    """Stop a device."""

    device = await device_registry.get_device(device_name)
    await device.stop()

    return device.device_config
