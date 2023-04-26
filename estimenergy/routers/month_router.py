from typing import Optional

from fastapi import APIRouter, HTTPException
from sqlmodel import Session, select

from estimenergy.db import db_engine
from estimenergy.devices import device_registry
from estimenergy.models.month import Month

month_router = APIRouter(prefix="/month", tags=["month"])


@month_router.get(
    "",
    response_model=list[Month],
    responses={
        404: {"description": "Device not found"},
    },
    operation_id="get_months",
)
async def get_months(device_name: Optional[str] = None):
    """Get all months."""

    if device_name is not None and not await device_registry.device_exists(device_name):
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
    operation_id="get_month",
)
async def get_month(month_id: int):
    """Get a month."""

    with Session(db_engine) as session:
        month = session.exec(select(Month).where(Month.id == month_id)).first()
        if month is None:
            raise HTTPException(status_code=404, detail="Month not found")
        return month
