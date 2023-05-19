from typing import List, Union

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.exc import NoResultFound
from sqlmodel import Session, select

from estimenergy.const import (
    RESPONSE_DEVICE_DELETED,
    RESPONSE_DEVICE_EXISTS,
    RESPONSE_DEVICE_FAILED_TO_START,
    RESPONSE_DEVICE_NOT_FOUND,
    RESPONSE_DEVICE_STARTED,
    RESPONSE_DEVICE_STOPPED,
)
from estimenergy.db import get_session
from estimenergy.devices.device_error import DeviceError
from estimenergy.devices.device_registry import device_registry
from estimenergy.models.device_config import (
    DeviceConfig,
    DeviceConfigIn,
    DeviceConfigOut,
)
from estimenergy.models.message import Message

device_router = APIRouter(prefix="/device", tags=["device"])


@device_router.post(
    "",
    response_model=DeviceConfigOut,
    operation_id="create_device",
    responses={
        409: {"model": Message},
        500: {"model": Message},
    },
)
async def create_device(
    device_config_in: DeviceConfigIn, session: Session = Depends(get_session)
):
    """Create a new device."""

    if await device_registry.device_exists(device_config_in.name, session):
        return JSONResponse(
            status_code=409,
            content={"message": RESPONSE_DEVICE_EXISTS},
        )

    try:
        device = await device_registry.create_device(device_config_in, session)
    except DeviceError:
        return JSONResponse(
            status_code=500,
            content={"message": RESPONSE_DEVICE_FAILED_TO_START},
        )

    return device.device_config


@device_router.get(
    "/{device_name}",
    response_model=DeviceConfigOut,
    operation_id="get_device",
    responses={
        404: {"model": Message},
    },
)
async def get_device(device_name: str, session: Session = Depends(get_session)):
    """Get a device."""

    try:
        device_config = await device_registry.get_device_config(device_name, session)
    except NoResultFound:
        return JSONResponse(
            status_code=404,
            content={"message": RESPONSE_DEVICE_NOT_FOUND},
        )

    return device_config


@device_router.get(
    "",
    response_model=list[DeviceConfigOut],
    operation_id="get_devices",
)
async def get_devices(session: Session = Depends(get_session)):
    """Get all devices."""

    device_configs = session.exec(select(DeviceConfig)).all()

    return device_configs


@device_router.put(
    "/{device_name}",
    response_model=DeviceConfigOut,
    operation_id="update_device",
    responses={
        404: {"model": Message},
    },
)
async def update_device(
    device_name: str,
    device_config_in: DeviceConfigIn,
    session: Session = Depends(get_session),
):
    """Update a device."""

    try:
        device_config = await device_registry.update_device(
            device_name, device_config_in, session
        )
    except DeviceError:
        return JSONResponse(
            status_code=500,
            content={"message": RESPONSE_DEVICE_FAILED_TO_START},
        )
    except NoResultFound:
        return JSONResponse(
            status_code=404,
            content={"message": RESPONSE_DEVICE_NOT_FOUND},
        )

    return device_config


@device_router.delete(
    "/{device_name}",
    operation_id="delete_device",
    responses={
        404: {"model": Message},
        200: {"model": Message},
    },
)
async def delete_device(device_name: str, session: Session = Depends(get_session)):
    """Delete a device."""

    try:
        await device_registry.delete_device(device_name, session)
    except NoResultFound:
        return JSONResponse(
            status_code=404,
            content={"message": RESPONSE_DEVICE_NOT_FOUND},
        )

    return JSONResponse(
        status_code=200,
        content={"message": RESPONSE_DEVICE_DELETED},
    )


@device_router.post(
    "/{device_name}/start",
    operation_id="start_device",
    responses={
        200: {"model": Message},
        404: {"model": Message},
        500: {"model": Message},
    },
)
async def start_device(device_name: str, session: Session = Depends(get_session)):
    """Start a device."""

    try:
        await device_registry.start_device(device_name, session)
    except DeviceError:
        return JSONResponse(
            status_code=500,
            content={"message": RESPONSE_DEVICE_FAILED_TO_START},
        )
    except NoResultFound:
        return JSONResponse(
            status_code=404,
            content={"message": RESPONSE_DEVICE_NOT_FOUND},
        )

    return JSONResponse(
        status_code=200,
        content={"message": RESPONSE_DEVICE_STARTED},
    )


@device_router.post(
    "/{device_name}/stop",
    operation_id="stop_device",
    responses={
        200: {"model": Message},
        404: {"model": Message},
    },
)
async def stop_device(device_name: str, session: Session = Depends(get_session)):
    """Stop a device."""

    try:
        await device_registry.stop_device(device_name, session)
    except NoResultFound:
        return JSONResponse(
            status_code=404,
            content={"message": RESPONSE_DEVICE_NOT_FOUND},
        )

    return JSONResponse(
        status_code=200,
        content={"message": RESPONSE_DEVICE_STOPPED},
    )
