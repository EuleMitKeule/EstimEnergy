"""Day router."""
import datetime
from typing import Optional
from fastapi import APIRouter, HTTPException
from sqlmodel import Session, select
from estimenergy.devices.base_device import BaseDevice

from estimenergy.models.day import Day, DayCreate, DayRead
from estimenergy.db import db_engine
from estimenergy.device import devices


day_router = APIRouter(prefix="/day", tags=["day"])


@day_router.get(
    "",
    response_model=list[DayRead],
    responses={
        404: {"description": "Device not found"},
    },
)
async def get_days(device_name: Optional[str] = None):
    """Get all days."""

    if device_name is not None and device_name not in [
        device.device_config.name for device in devices
    ]:
        raise HTTPException(status_code=404, detail="Device not found")

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
        404: {"description": "Day not found"},
    },
)
async def get_day(day_id: int):
    """Get a day."""

    with Session(db_engine) as session:
        day = session.exec(select(Day).where(Day.id == day_id)).first()
        if day is None:
            raise HTTPException(status_code=404, detail="Day not found")
        return day


@day_router.post(
    "",
    response_model=DayRead,
    responses={
        404: {"description": "Device not found"},
    },
)
async def create_day(day: DayCreate):
    """Create a day."""

    device: BaseDevice = next(
        (device for device in devices if device.device_config.name == day.device_name),
        None,
    )

    if device is None:
        raise HTTPException(status_code=404, detail="Device not found")

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
        404: {"description": "Day not found"},
    },
)
async def update_day(day_id: int, day: DayCreate):
    """Update a day."""

    device: BaseDevice = next(
        (device for device in devices if device.device_config.name == day.device_name),
        None,
    )

    if device is None:
        raise HTTPException(status_code=404, detail="Device not found")

    with Session(db_engine) as session:
        db_day = session.exec(select(Day).where(Day.id == day_id)).first()
        if db_day is None:
            raise HTTPException(status_code=404, detail="Day not found")

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
        404: {"description": "Day not found"},
    },
)
async def delete_day(day_id: int):
    """Delete a day."""

    with Session(db_engine) as session:
        day = session.exec(select(Day).where(Day.id == day_id)).first()
        if day is None:
            raise HTTPException(status_code=404, detail="Day not found")

        session.delete(day)
        session.commit()

        return day
