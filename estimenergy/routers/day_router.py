"""Day router."""
import datetime
from typing import Optional

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from sqlmodel import Session, select

from estimenergy.const import RESPONSE_DAY_NOT_FOUND, RESPONSE_DEVICE_NOT_FOUND
from estimenergy.db import db_engine
from estimenergy.devices import device_registry
from estimenergy.devices.base_device import BaseDevice
from estimenergy.models.day import Day, DayCreate, DayRead
from estimenergy.models.message import Message

day_router = APIRouter(prefix="/day", tags=["day"])


@day_router.get(
    "",
    response_model=list[DayRead],
    responses={
        404: {"model": Message},
    },
    operation_id="get_days",
)
async def get_days(device_name: Optional[str] = None):
    """Get all days."""

    if device_name is not None and not await device_registry.device_exists(device_name):
        return JSONResponse(
            status_code=404,
            content={"message": RESPONSE_DEVICE_NOT_FOUND},
        )

    with Session(db_engine) as session:
        if device_name is None:
            days = session.exec(select(Day)).all()
        else:
            days = session.exec(select(Day).where(Day.device_name == device_name)).all()
        return days


@day_router.get(
    "/{day_id}",
    response_model=DayRead,
    responses={
        404: {"model": Message},
    },
    operation_id="get_day",
)
async def get_day(day_id: int):
    """Get a day."""

    with Session(db_engine) as session:
        day = session.exec(select(Day).where(Day.id == day_id)).first()

    if day is None:
        return JSONResponse(
            status_code=404,
            content={"message": RESPONSE_DAY_NOT_FOUND},
        )

    return day


@day_router.post(
    "",
    response_model=DayRead,
    responses={
        404: {"model": Message},
    },
    operation_id="create_day",
)
async def create_day(day: DayCreate):
    """Create a day."""

    device: Optional[BaseDevice] = await device_registry.get_device(day.device_name)

    if device is None:
        return JSONResponse(
            status_code=404,
            content={"message": RESPONSE_DEVICE_NOT_FOUND},
        )

    with Session(db_engine) as session:
        db_day = Day.from_orm(day)
        session.add(db_day)
        session.commit()
        session.refresh(db_day)

        date = datetime.datetime(db_day.date.year, db_day.date.month, db_day.date.day)
        await device.update(date)
        session.commit()

        session.refresh(db_day)

        return db_day


@day_router.put(
    "/{day_id}",
    response_model=DayRead,
    responses={
        404: {"model": Message},
    },
    operation_id="update_day",
)
async def update_day(day_id: int, day: DayCreate):
    """Update a day."""

    device: Optional[BaseDevice] = await device_registry.get_device(day.device_name)

    if device is None:
        return JSONResponse(
            status_code=404,
            content={"message": RESPONSE_DEVICE_NOT_FOUND},
        )

    with Session(db_engine) as session:
        db_day = session.exec(select(Day).where(Day.id == day_id)).first()

        if db_day is None:
            return JSONResponse(
                status_code=404,
                content={"message": RESPONSE_DAY_NOT_FOUND},
            )

        db_day.energy = day.energy
        db_day.date = day.date
        db_day.accuracy = day.accuracy

        session.add(db_day)
        session.commit()
        session.refresh(db_day)

        date = datetime.datetime(db_day.date.year, db_day.date.month, db_day.date.day)
        await device.update(date)
        session.commit()

        session.refresh(db_day)

        return db_day


@day_router.delete(
    "/{day_id}",
    response_model=DayRead,
    responses={
        404: {"model": Message},
    },
    operation_id="delete_day",
)
async def delete_day(day_id: int):
    """Delete a day."""

    with Session(db_engine) as session:
        day = session.exec(select(Day).where(Day.id == day_id)).first()

        if day is None:
            return JSONResponse(
                status_code=404,
                content={"message": RESPONSE_DAY_NOT_FOUND},
            )

        session.delete(day)
        session.commit()

        return day
