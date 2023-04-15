from typing import Optional
from fastapi import APIRouter, HTTPException
from sqlmodel import Session, select

from estimenergy.models.month import Month
from estimenergy.db import db_engine
from estimenergy.device import devices


month_router = APIRouter(prefix="/month", tags=["month"])


@month_router.get(
    "",
    response_model=list[Month],
    responses={
        404: {"description": "Device not found"},
    },
)
async def get_months(device_name: Optional[str] = None):
    """Get all months."""

    if device_name is not None and device_name not in [
        device.device_config.name for device in devices
    ]:
        raise HTTPException(status_code=404, detail="Device not found")

    with Session(db_engine) as session:
        if device_name is None:
            months = session.exec(select(Month)).all()
        else:
            months = session.exec(
                select(Month).where(Month.device_name == device_name)
            ).all()
        return months


@month_router.get(
    "/{id}",
    response_model=Month,
    responses={
        404: {"description": "Month not found"},
    },
)
async def get_month(month_id: int):
    """Get a month."""

    with Session(db_engine) as session:
        month = session.exec(select(Month).where(Month.id == month_id)).first()
        if month is None:
            raise HTTPException(status_code=404, detail="Month not found")
        return month
